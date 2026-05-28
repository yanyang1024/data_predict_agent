"""
翻译引擎模块 -- 基于内网 LLM API
提供中文到英文的翻译，支持增量修正和智能分段。

核心设计:
    - 调用内网 OpenAI 兼容 API 进行翻译
    - 维护翻译历史，利用前文上下文保持翻译连贯性
    - 使用 LLM 判断句子完整性并智能分段
    - 自动回退策略确保在 API 异常时仍能工作
"""

import json
import logging
import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict

from openai import OpenAI

logger = logging.getLogger(__name__)


@dataclass
class Segment:
    """字幕段落，存储中文原文和英文翻译。

    Attributes:
        id: 全局唯一段落标识，按创建顺序递增
        chinese: 中文原文文本
        english: 英文翻译文本
        is_final: 是否为已稳定段落（True 表示语义完整，不会再被修改）
    """
    id: int
    chinese: str
    english: str
    is_final: bool = False


class TranslateEngine:
    """翻译引擎，使用内网 OpenAI 兼容 LLM API。

    主要功能:
        1. 接收 ASR 识别出的中文文本，检测完整句子并翻译
        2. 维护未稳定（pending）段落的增量更新
        3. 利用前文已稳定段落的翻译上下文保持连贯性
        4. API 异常时自动回退到简单策略

    使用示例:
        engine = TranslateEngine("http://llm.internal:8000/v1", "key", "qwen2.5-7b")
        changes = engine.add_asr_result("今天天气很好。我们出去")
        # changes 包含新增/更新的段落信息
    """

    def __init__(
        self,
        api_base: str,
        api_key: str,
        model_name: str,
        max_history: int = 10,
    ):
        """初始化翻译引擎。

        Args:
            api_base: OpenAI 兼容 API 的基础 URL
            api_key: API 密钥
            model_name: 使用的模型名称
            max_history: 保留的最大历史段落数，超出则裁剪
        """
        self.client = OpenAI(base_url=api_base, api_key=api_key)
        self.model_name = model_name
        self.max_history = max_history
        self.segments: List[Segment] = []
        self.pending_segment: Optional[Segment] = None  # 未稳定的当前段
        self.next_id = 0  # 自增段落 ID 计数器

    # ------------------------------------------------------------------
    # 内部工具方法
    # ------------------------------------------------------------------

    def _call_llm(self, prompt: str, temperature: float = 0.3, max_tokens: int = 512) -> str:
        """调用 LLM API，带异常处理和重试回退。

        Args:
            prompt: 发送给模型的提示文本
            temperature: 采样温度，越低越确定
            max_tokens: 最大生成 token 数

        Returns:
            模型生成的文本字符串，失败时返回空字符串
        """
        try:
            resp = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = resp.choices[0].message.content
            return content.strip() if content else ""
        except Exception as e:
            logger.error(f"LLM API 调用失败: {e}")
            return ""

    def _extract_json(self, text: str) -> Optional[dict]:
        """从 LLM 返回文本中提取 JSON 对象。

        支持多种格式:
            - 纯 JSON 文本
            - ```json ... ``` 代码块
            - ``` ... ``` 代码块

        Args:
            text: LLM 返回的原始文本

        Returns:
            解析后的 dict，失败时返回 None
        """
        if not text:
            return None

        json_str = text

        # 尝试提取代码块中的 JSON
        if "```json" in text:
            json_str = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            json_str = text.split("```")[1].split("```")[0].strip()

        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            logger.warning(f"JSON 解析失败，原始文本: {text[:200]}")
            return None

    # ------------------------------------------------------------------
    # 智能分段
    # ------------------------------------------------------------------

    def _detect_segments(self, text: str) -> tuple:
        """使用 LLM 检测文本中的完整句子和未完成片段。

        通过 LLM 判断文本中哪些部分构成了语义完整的句子，
        哪些部分尚未结束。以标点符号为主要依据，同时考虑语义完整性。

        Args:
            text: 待分析的中文文本

        Returns:
            (completed_sentences: List[str], remaining: str)
            completed_sentences 是完整句子列表
            remaining 是最后一个完整句子之后的未完成片段
        """
        if not text or not text.strip():
            return [], ""

        # 如果文本很短（少于 10 个字），大概率未完成，直接返回
        if len(text.strip()) < 10:
            # 但如果有结束标点，仍然可能完整
            if not any(text.strip().endswith(p) for p in (".", "!", "?", "。", "！", "？")):
                return [], text.strip()

        prompt = f"""Analyze the following Chinese text and split it into complete sentences.
Incomplete or unfinished sentences should be placed in "remaining".

Requirements:
1. Sentences ending with punctuation (。！？.!?) are complete sentences
2. Sentences that are semantically complete are also considered complete
3. Return STRICTLY in JSON format with NO other text

{{"completed": ["complete sentence 1", "complete sentence 2"], "remaining": "incomplete fragment"}}

Text: {text}"""

        result = self._call_llm(prompt, temperature=0.1, max_tokens=256)
        data = self._extract_json(result)

        if data is not None:
            completed = data.get("completed", [])
            remaining = data.get("remaining", "")

            if isinstance(completed, list) and isinstance(remaining, str):
                # 过滤空字符串
                completed = [s.strip() for s in completed if s and s.strip()]
                remaining = remaining.strip()
                return completed, remaining

        # 回退到简单策略
        logger.info("LLM 分段失败，使用回退策略")
        return self._fallback_segment(text)

    def _fallback_segment(self, text: str) -> tuple:
        """简单的回退分段策略（基于正则表达式）。

        当 LLM 分段失败时使用，按中文/英文结束标点符号分割文本。

        Args:
            text: 待分割的中文文本

        Returns:
            (completed_sentences: List[str], remaining: str)
        """
        # 匹配以标点符号结尾的完整句子（中英文标点都支持）
        pattern = r"([^。！？.!?]*[。！？.!?]+)"
        matches = re.findall(pattern, text)

        if matches:
            completed = [s.strip() for s in matches if s.strip()]
            # 计算最后一个匹配之后的剩余文本
            last_end = 0
            for m in re.finditer(pattern, text):
                last_end = m.end()
            remaining = text[last_end:].strip()
            return completed, remaining

        # 没有任何标点，全部作为 remaining
        return [], text.strip()

    # ------------------------------------------------------------------
    # 翻译
    # ------------------------------------------------------------------

    def _get_context(self) -> tuple:
        """获取前文翻译上下文。

        取最近 3 个已稳定段落的中文和英文文本作为上下文，
        帮助 LLM 保持翻译的连贯性（如指代一致性）。

        Returns:
            (context_chinese: str, context_english: str)
        """
        final_segs = [s for s in self.segments if s.is_final][-3:]
        context_ch = " ".join([s.chinese for s in final_segs]) if final_segs else ""
        context_eng = " ".join([s.english for s in final_segs]) if final_segs else ""
        return context_ch, context_eng

    def _translate_sentences(self, sentences: List[str]) -> List[str]:
        """批量翻译句子列表，利用前文上下文保持连贯性。

        将多个句子一次性翻译，比逐句翻译更高效，且能保持段落间连贯。

        Args:
            sentences: 中文句子列表

        Returns:
            对应的英文翻译列表，与输入一一对应
        """
        if not sentences:
            return []

        context_ch, context_eng = self._get_context()
        sentences_json = json.dumps(sentences, ensure_ascii=False)

        prompt = f"""Translate the following Chinese sentences into fluent English.
Maintain contextual coherence and semantic accuracy.

Previous Chinese context: {context_ch}
Previous English context: {context_eng}

Sentences to translate (JSON format): {sentences_json}

Requirements:
1. Translation must be natural and fluent, conforming to English expression habits
2. Maintain consistent references (pronouns, names) with the previous context
3. Return STRICTLY in JSON format: {{"translations": ["English 1", "English 2"]}}
4. The number of translations MUST match the number of input sentences"""

        result = self._call_llm(prompt, temperature=0.3, max_tokens=512)
        data = self._extract_json(result)

        if data is not None:
            translations = data.get("translations", [])
            if isinstance(translations, list):
                # 确保数量一致：少了填充，多了截断
                while len(translations) < len(sentences):
                    idx = len(translations)
                    # 尝试逐句翻译作为补充
                    fallback = self._call_llm(
                        f"Translate to English: {sentences[idx]}",
                        temperature=0.3,
                        max_tokens=128,
                    )
                    translations.append(fallback if fallback else sentences[idx])
                return translations[: len(sentences)]

        # 回退到逐句翻译
        logger.info("批量翻译失败，使用逐句回退")
        return self._fallback_translate(sentences)

    def _fallback_translate(self, sentences: List[str]) -> List[str]:
        """逐句翻译的回退方案。

        当批量翻译失败时，逐句调用 API，每句独立翻译。
        效果可能不如批量翻译连贯，但稳定性更高。

        Args:
            sentences: 中文句子列表

        Returns:
            对应的英文翻译列表
        """
        results = []
        for s in sentences:
            prompt = f"Translate the following Chinese into English: {s}"
            result = self._call_llm(prompt, temperature=0.3, max_tokens=128)
            results.append(result if result else s)
        return results

    # ------------------------------------------------------------------
    # 对外接口
    # ------------------------------------------------------------------

    def add_asr_result(self, chinese_text: str) -> List[Dict]:
        """处理新的 ASR 识别结果。

        这是翻译引擎的核心入口方法。每次 ASR 识别出新文本时调用，
        引擎会:
        1. 将新文本与未稳定（pending）段落合并
        2. 使用 LLM 检测其中的完整句子
        3. 翻译完整句子并标记为 final
        4. 将未完成的片段作为新的 pending 段落

        Args:
            chinese_text: ASR 识别出的中文文本

        Returns:
            变更列表，每个元素是一个 dict:
                - id: 段落 ID
                - chinese: 中文文本
                - english: 英文翻译
                - is_final: 是否已稳定
                - is_new: 是否是新段落（而非更新已有段落）
        """
        if not chinese_text or not chinese_text.strip():
            return []

        changes = []

        # 1. 累积新文本：与 pending 段落合并
        if self.pending_segment:
            combined = self.pending_segment.chinese + chinese_text
        else:
            combined = chinese_text

        # 2. 检测完整句子和未完成片段
        completed, remaining = self._detect_segments(combined)

        # 3. 处理已完成的句子
        if completed:
            translations = self._translate_sentences(completed)

            for cn, en in zip(completed, translations):
                # 检查是否已有 pending 段落可以复用
                if (
                    self.pending_segment
                    and not self.pending_segment.is_final
                    and self.pending_segment.chinese.strip() == cn.strip()
                ):
                    # pending 段落实质上已稳定，升级为 final
                    existing = self.pending_segment
                    existing.chinese = cn
                    existing.english = en
                    existing.is_final = True
                    changes.append(
                        {
                            "id": existing.id,
                            "chinese": cn,
                            "english": en,
                            "is_final": True,
                            "is_new": False,
                        }
                    )
                    self.segments.append(existing)
                    self.pending_segment = None
                else:
                    # 创建新段落
                    seg = Segment(
                        id=self.next_id, chinese=cn, english=en, is_final=True
                    )
                    self.next_id += 1
                    self.segments.append(seg)
                    changes.append(
                        {
                            "id": seg.id,
                            "chinese": cn,
                            "english": en,
                            "is_final": True,
                            "is_new": True,
                        }
                    )
                    self.pending_segment = None

        # 4. 处理未完成片段（临时字幕 / pending）
        if remaining and remaining.strip():
            if self.pending_segment:
                # 更新现有 pending
                old_id = self.pending_segment.id
                prompt = f"Translate the following Chinese into English: {remaining}"
                en_remaining = (
                    self._call_llm(prompt, temperature=0.3, max_tokens=128) or remaining
                )

                self.pending_segment.chinese = remaining
                self.pending_segment.english = en_remaining
                self.pending_segment.is_final = False

                changes.append(
                    {
                        "id": old_id,
                        "chinese": remaining,
                        "english": en_remaining,
                        "is_final": False,
                        "is_new": False,
                    }
                )
            else:
                # 创建新的 pending segment
                prompt = f"Translate the following Chinese into English: {remaining}"
                en_remaining = (
                    self._call_llm(prompt, temperature=0.3, max_tokens=128) or remaining
                )

                seg = Segment(
                    id=self.next_id,
                    chinese=remaining,
                    english=en_remaining,
                    is_final=False,
                )
                self.next_id += 1
                self.pending_segment = seg
                changes.append(
                    {
                        "id": seg.id,
                        "chinese": remaining,
                        "english": en_remaining,
                        "is_final": False,
                        "is_new": True,
                    }
                )

        # 5. 裁剪历史，防止内存无限增长
        self._trim_history()

        return changes

    def _trim_history(self) -> None:
        """裁剪历史段落，只保留最近 max_history 个已稳定段落。

        pending 段落不会被裁剪，因为它代表当前正在进行的字幕。
        """
        if len(self.segments) > self.max_history:
            self.segments = self.segments[-self.max_history :]

    def get_all_segments(self) -> List[Dict]:
        """获取所有段落（包括已稳定和未稳定）。

        Returns:
            包含所有段落的字典列表
        """
        all_segs = [
            {
                "id": s.id,
                "chinese": s.chinese,
                "english": s.english,
                "is_final": s.is_final,
            }
            for s in self.segments
        ]
        if self.pending_segment:
            all_segs.append(
                {
                    "id": self.pending_segment.id,
                    "chinese": self.pending_segment.chinese,
                    "english": self.pending_segment.english,
                    "is_final": False,
                }
            )
        return all_segs

    def finalize_all(self) -> List[Dict]:
        """强制将所有 pending 文本标记为最终（录音结束时调用）。

        当用户停止录音时调用，确保最后一段未完成的文本也能被翻译并显示。

        Returns:
            变更列表（如果有 pending 段落被结算）
        """
        changes = []
        if self.pending_segment and self.pending_segment.chinese.strip():
            cn = self.pending_segment.chinese.strip()
            translations = self._translate_sentences([cn])
            en = translations[0] if translations else cn

            self.pending_segment.chinese = cn
            self.pending_segment.english = en
            self.pending_segment.is_final = True
            self.segments.append(self.pending_segment)

            changes.append(
                {
                    "id": self.pending_segment.id,
                    "chinese": cn,
                    "english": en,
                    "is_final": True,
                    "is_new": False,
                }
            )
            self.pending_segment = None

        return changes

    def reset(self) -> None:
        """重置所有状态（开始新录音时调用）。"""
        self.segments = []
        self.pending_segment = None
        self.next_id = 0
