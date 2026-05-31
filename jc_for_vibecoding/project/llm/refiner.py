import logging
import threading
import openai

logger = logging.getLogger(__name__)


class LLMRefiner:
    """LLM-based translation refiner with conversation context.

    Calls an OpenAI-compatible API (streaming) to refine raw SeamlessM4T
    translations using a sliding window of conversation history.
    Supports retroactive correction of previous segments.
    """

    def __init__(self, config):
        self.client = openai.OpenAI(
            api_key=config.LLM_API_KEY,
            base_url=config.LLM_API_BASE,
        )
        self.model = config.LLM_MODEL
        self.timeout = config.LLM_TIMEOUT_S
        self.context_window = config.LLM_CONTEXT_WINDOW
        self.early_threshold = getattr(config, 'LLM_EARLY_THRESHOLD', 0.3)
        self.mature_threshold = getattr(config, 'LLM_MATURE_THRESHOLD', 0.7)
        self._history = []
        self._lock = threading.Lock()

    def refine(self, segment_id, raw_en_text, timestamp,
               on_token=None, on_corrections=None, on_done=None):
        context_lines = []
        with self._lock:
            for seg in self._history:
                context_lines.append(f"[{seg['timestamp']}] {seg['en_text']}")

        # Context maturity & correction bias
        history_len = len(self._history)
        maturity = history_len / max(history_len, self.context_window)
        bias_instruction = self._build_bias_instruction(maturity)

        system_prompt = (
            "You are a real-time Chinese-to-English meeting translator. "
            "Your task is to refine raw machine translations using conversation context.\n\n"
            "Rules:\n"
            "- Output ONLY the refined English translation as plain text, one line per segment\n"
            "- If context clarifies a term (e.g. 'revenue' vs 'profit'), use the correct term\n"
            "- Keep the same information but make it natural and fluent\n"
            "- If a previous segment's translation needs correction based on new context, "
            "add a new line after your translation starting with CORRECT: followed by "
            "that segment_id and the corrected text\n"
            "- Do NOT add explanations, notes, or prefixes\n"
            f"\n{bias_instruction}"
        )

        ctx = "\n".join(context_lines) if context_lines else "(start of conversation)"
        user_prompt = (
            f"Conversation history:\n{ctx}\n\n"
            f"New segment [{timestamp}]: {raw_en_text}\n\n"
            f"Refined translation:"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        with self._lock:
            self._history.append({
                'segment_id': segment_id,
                'en_text': raw_en_text,
                'timestamp': timestamp,
            })
            if len(self._history) > self.context_window:
                self._history = self._history[-self.context_window:]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                timeout=self.timeout,
            )

            partial_line = ""
            corrections = []

            for chunk in response:
                if chunk.choices[0].finish_reason is not None:
                    break
                delta = chunk.choices[0].delta.content or ""
                for char in delta:
                    partial_line += char
                    if char == '\n':
                        self._process_line(partial_line, on_token, corrections)
                        partial_line = ""

            if partial_line.strip():
                self._process_line(partial_line, on_token, corrections)

            if on_corrections and corrections:
                on_corrections(segment_id, corrections)
                with self._lock:
                    for corr in corrections:
                        for seg in self._history:
                            if seg['segment_id'] == corr['segment_id']:
                                seg['en_text'] = corr['corrected_text']
                                break

        except Exception as e:
            logger.error(f"LLM refinement failed: {e}")
            if on_token:
                on_token(segment_id, raw_en_text)

        finally:
            if on_done:
                on_done(segment_id)

    def _build_bias_instruction(self, maturity):
        maturity = min(maturity, 1.0)
        if maturity < self.early_threshold:
            return (
                "Context priority: early conversation stage.\n"
                "Earlier translations had very limited context and may need "
                "significant revision. Review ALL previous segments and correct "
                "them wherever the growing conversation context now clarifies "
                "meaning, terminology, or references."
            )
        if maturity > self.mature_threshold:
            return (
                "Context priority: established conversation.\n"
                "Earlier translations already benefited from substantial context. "
                "Focus refinement on the new segment. Only correct previous "
                "segments if the new utterance directly contradicts or "
                "clarifies them."
            )
        return (
            "Context priority: building context.\n"
            "Review previous segments critically. Earlier entries may still "
            "benefit from correction as context accumulates. Balance corrections "
            "across old and new segments."
        )

    def _process_line(self, line, on_token, corrections):
        line = line.strip()
        if not line:
            return
        if line.startswith("CORRECT:"):
            rest = line[len("CORRECT:"):].strip()
            colon_idx = rest.find(':')
            if colon_idx > 0:
                corr_id = rest[:colon_idx].strip()
                corr_text = rest[colon_idx + 1:].strip()
                if corr_id and corr_text:
                    corrections.append({
                        'segment_id': corr_id,
                        'corrected_text': corr_text,
                    })
        elif on_token:
            on_token(segment_id=None, token=line + '\n')
