from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class ImageURL(BaseModel):
    url: str
    detail: Optional[str] = None


class ContentPartText(BaseModel):
    type: Literal["text"]
    text: str


class ContentPartImage(BaseModel):
    type: Literal["image_url"]
    image_url: ImageURL


ContentPart = Union[ContentPartText, ContentPartImage, Dict[str, Any]]


class FunctionToolDefinition(BaseModel):
    name: str
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class ToolDefinition(BaseModel):
    type: Literal["function"]
    function: FunctionToolDefinition


class ToolCallFunction(BaseModel):
    name: str
    arguments: str


class ToolCall(BaseModel):
    id: str
    type: Literal["function"]
    function: ToolCallFunction


class ChatMessage(BaseModel):
    role: Literal["system", "developer", "user", "assistant", "tool"]
    content: Optional[Union[str, List[ContentPart], List[Dict[str, Any]]]] = None
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    refusal: Optional[str] = None
    audio: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(extra="allow")


class StreamOptions(BaseModel):
    include_usage: Optional[bool] = None
    include_obfuscation: Optional[bool] = None


class ChatCompletionRequest(BaseModel):
    model: str = "backend-compatible-model"
    messages: List[ChatMessage]
    stream: bool = False
    tools: Optional[List[ToolDefinition]] = None
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None
    user: Optional[str] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    max_tokens: Optional[int] = None
    n: Optional[int] = 1
    stop: Optional[Union[str, List[str]]] = None
    stream_options: Optional[StreamOptions] = None
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(extra="allow")


class BackendFile(BaseModel):
    Name: str
    Path: str
    Size: Optional[int] = None
    Url: str


class QueryExtendsInfo(BaseModel):
    Files: List[BackendFile] = Field(default_factory=list)


class BackendRequest(BaseModel):
    Query: str
    AppConversationID: str
    QueryExtends: Optional[QueryExtendsInfo] = None


class OpenAIChoiceMessage(BaseModel):
    role: Literal["assistant"] = "assistant"
    content: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    function_call: Optional[Dict[str, Any]] = None


class OpenAIChoice(BaseModel):
    index: int = 0
    message: OpenAIChoiceMessage
    logprobs: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = "stop"


class UsageInfo(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class OpenAIChatCompletionResponse(BaseModel):
    id: str
    object: Literal["chat.completion"] = "chat.completion"
    created: int
    model: str
    choices: List[OpenAIChoice]
    usage: UsageInfo
    system_fingerprint: Optional[str] = None


class OpenAIChunkChoiceDelta(BaseModel):
    role: Optional[Literal["assistant"]] = None
    content: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None


class OpenAIChunkChoice(BaseModel):
    index: int = 0
    delta: OpenAIChunkChoiceDelta
    finish_reason: Optional[str] = None
    logprobs: Optional[Dict[str, Any]] = None


class OpenAIChatCompletionChunk(BaseModel):
    id: str
    object: Literal["chat.completion.chunk"] = "chat.completion.chunk"
    created: int
    model: str
    choices: List[OpenAIChunkChoice]
    usage: Optional[UsageInfo] = None
    system_fingerprint: Optional[str] = None
