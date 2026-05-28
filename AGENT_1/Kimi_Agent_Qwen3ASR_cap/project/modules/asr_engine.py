"""
ASR Engine Module — Powered by Qwen3-ASR-1.7B
==============================================
Provides Chinese speech recognition with streaming support for a
real-time speech translation Web App.

Usage::

    from modules.asr_engine import ASREngine

    engine = ASREngine(model_path="/models/Qwen3-ASR-1.7B")
    text = engine.transcribe(audio_array, sample_rate=16000)

Environment Constraints
-----------------------
- Python 3.12
- torch == 2.6.0+cu124
- transformers == 5.9.0
- CUDA 12.4
- Model: Qwen3-ASR-1.7B (loaded from local path via ``qwen-asr``)
- No flash_attention_2
"""

from __future__ import annotations

import io
import logging
import wave
from typing import Any, Optional, Union

import numpy as np
import soundfile as sf
import torch
import librosa

logger: logging.Logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Type alias for convenience
# ---------------------------------------------------------------------------
AudioInput = Union[np.ndarray, bytes, bytearray]


class ModelLoadError(RuntimeError):
    """Raised when the ASR model fails to load."""


class TranscriptionError(RuntimeError):
    """Raised when transcription fails fatally (caller may choose to catch)."""


class ASREngine:
    """Speech-recognition engine backed by Qwen3-ASR-1.7B.

    The engine supports:

    * Loading the model from a **local** path (no remote downloads).
    * Accepting audio as ``numpy.ndarray``, ``bytes`` (WAV), or ``bytearray``.
    * Automatic resampling to 16 kHz via ``librosa``.
    * Optional *context* text for improved long-form transcription coherence.
    * Graceful error handling — every public method is fully exception-safe.

    Attributes:
        model_path: Local filesystem path to the Qwen3-ASR-1.7B checkpoint.
        device: CUDA device string, e.g. ``"cuda:0"``.
        dtype: PyTorch dtype used for model weights (default ``torch.bfloat16``).
        max_new_tokens: Maximum number of new tokens generated per utterance.
        model: The underlying ``Qwen3ASRModel`` instance (``None`` until loaded).
    """

    # ------------------------------------------------------------------ #
    # Construction / Model Loading
    # ------------------------------------------------------------------ #

    def __init__(
        self,
        model_path: str,
        *,
        device: str = "cuda:0",
        dtype: torch.dtype = torch.bfloat16,
        max_new_tokens: int = 256,
    ) -> None:
        """Initialise the ASR engine and load the model eagerly.

        Args:
            model_path: Absolute or relative local path to the model directory
                (e.g. ``/models/Qwen3-ASR-1.7B``).
            device: CUDA device identifier. Pass ``"cpu"`` for CPU-only
                inference (not recommended for production).
            dtype: Floating-point dtype for model weights.
                ``torch.bfloat16`` offers the best speed/quality trade-off on
                Ampere-or-newer GPUs; fall back to ``torch.float16`` or
                ``torch.float32`` on older hardware if needed.
            max_new_tokens: Hard cap on generated tokens per transcription
                call. Increase for very long utterances.

        Raises:
            ModelLoadError: If ``qwen-asr`` is unavailable or the checkpoint
                cannot be loaded.
        """
        self.model_path: str = model_path
        self.device: str = device
        self.dtype: torch.dtype = dtype
        self.max_new_tokens: int = max_new_tokens
        self.model: Optional[Any] = None

        self._load_model()

    def _load_model(self) -> None:
        """Load the Qwen3-ASR-1.7B model from :attr:`model_path`.

        Raises:
            ModelLoadError: On any import or loading failure.
        """
        try:
            from qwen_asr import Qwen3ASRModel
        except ImportError as exc:
            logger.error(
                "Cannot import 'qwen_asr'. Please install the qwen-asr package: "
                "pip install qwen-asr"
            )
            raise ModelLoadError(
                "Missing dependency: qwen-asr is not installed."
            ) from exc

        logger.info(
            "Loading ASR model from '%s' (device=%s, dtype=%s, max_new_tokens=%d)",
            self.model_path,
            self.device,
            self.dtype,
            self.max_new_tokens,
        )

        try:
            self.model = Qwen3ASRModel.from_pretrained(
                self.model_path,
                dtype=self.dtype,
                device_map=self.device,
                max_inference_batch_size=32,
                max_new_tokens=self.max_new_tokens,
            )
        except Exception as exc:
            logger.error(
                "Failed to load Qwen3ASRModel from '%s': %s",
                self.model_path,
                exc,
                exc_info=True,
            )
            raise ModelLoadError(
                f"Failed to load ASR model from {self.model_path}: {exc}"
            ) from exc

        logger.info("ASR model loaded successfully.")

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def transcribe(
        self,
        audio: AudioInput,
        sample_rate: int = 16000,
        *,
        context: str = "",
        language: str = "Chinese",
        return_language: bool = False,
    ) -> Union[str, tuple[str, str]]:
        """Transcribe audio into text.

        Parameters
        ----------
        audio:
            One of the following:

            * ``numpy.ndarray`` — 1-D array of float32 samples in ``[-1.0, 1.0]``.
            * ``bytes`` / ``bytearray`` — Raw WAV data (including RIFF header).

        sample_rate:
            Sampling rate of *audio* when it is an ndarray. Ignored for WAV
            bytes (the WAV header rate is used instead). Must be positive.
        context:
            Optional preceding text that provides linguistic context. Useful
            for maintaining consistency across consecutive chunks in a
            streaming pipeline.
        language:
            Language code passed to the model (default ``"Chinese"``).
        return_language:
            If ``True``, return a ``(text, detected_language)`` tuple instead
            of plain text.

        Returns
        -------
        str
            Recognised text (empty string on non-fatal failure).
        tuple[str, str]
            *(text, detected_language)* when *return_language* is ``True``.

        Raises
        ------
        TranscriptionError:
            Only raised for truly unexpected internal errors; normal failure
            modes (empty audio, model error) return an empty string so that
            caller applications stay robust.
        ValueError:
            If input validation fails (e.g. invalid *sample_rate*).
        """
        # ---- Validate & normalise input ----------------------------------
        if sample_rate <= 0:
            raise ValueError(f"sample_rate must be positive, got {sample_rate}")

        try:
            waveform: np.ndarray = self._normalize_input(audio, sample_rate)
        except Exception as exc:
            logger.error("Audio input normalisation failed: %s", exc, exc_info=True)
            return ("", "") if return_language else ""

        if waveform.size == 0:
            logger.debug("Empty audio buffer received; returning empty transcript.")
            return ("", "") if return_language else ""

        # ---- Resample to 16 kHz (model requirement) ----------------------
        try:
            waveform_16k = self._resample(waveform, 16000, 16000)
        except Exception as exc:
            logger.error("Resampling failed: %s", exc, exc_info=True)
            return ("", "") if return_language else ""

        # ---- Run inference -----------------------------------------------
        try:
            results = self.model.transcribe(
                audio=(waveform_16k, 16000),
                language=language,
                context=context if context else None,
            )
        except Exception as exc:
            logger.error("Model transcription failed: %s", exc, exc_info=True)
            return ("", "") if return_language else ""

        # ---- Extract text from results -----------------------------------
        if not results or len(results) == 0:
            logger.debug("Model returned empty results.")
            return ("", "") if return_language else ""

        first_result = results[0]
        text: str = getattr(first_result, "text", "").strip()
        detected_language: str = getattr(first_result, "language", language)

        logger.debug(
            "ASR result: text='%s...' (language=%s)",
            text[:80],
            detected_language,
        )

        if return_language:
            return text, detected_language
        return text

    def health_check(self) -> bool:
        """Return ``True`` if the model is loaded and ready.

        This is intended for Kubernetes / Docker health-check endpoints.
        """
        return self.model is not None

    def warmup(self, duration_sec: float = 1.0) -> None:
        """Run a dummy transcription to warm up CUDA kernels.

        This prevents the first real request from incurring a GPU cache
        initialisation penalty.

        Args:
            duration_sec: Length of the dummy audio in seconds.
        """
        if not self.health_check():
            logger.warning("Model not loaded; skipping warmup.")
            return

        num_samples = int(16000 * duration_sec)
        dummy_audio = np.zeros(num_samples, dtype=np.float32)
        logger.info("Running warmup transcription (%.1f s silence)...", duration_sec)
        _ = self.transcribe(dummy_audio, sample_rate=16000)
        logger.info("Warmup complete.")

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _normalize_input(
        self, audio: AudioInput, sample_rate: int
    ) -> np.ndarray:
        """Convert any supported input format to a float32 1-D numpy array.

        Args:
            audio: ndarray, bytes, or bytearray.
            sample_rate: Fallback sample rate for ndarray input.

        Returns:
            1-D float32 numpy array. If the input was WAV bytes, resampling
            to 16 kHz is performed automatically.

        Raises:
            TypeError: If *audio* has an unsupported type.
        """
        if isinstance(audio, (bytes, bytearray)):
            return self._wav_bytes_to_numpy(bytes(audio))

        if isinstance(audio, np.ndarray):
            arr = np.asarray(audio, dtype=np.float32)
            if arr.ndim == 0:
                return np.array([], dtype=np.float32)
            # Flatten multi-channel to mono
            if arr.ndim > 1:
                arr = np.mean(arr, axis=tuple(range(1, arr.ndim)), dtype=np.float32)
            # Resample if needed
            if sample_rate != 16000:
                arr = self._resample(arr, sample_rate, 16000)
            return arr

        raise TypeError(
            f"Unsupported audio type: {type(audio).__name__}. "
            "Expected np.ndarray, bytes, or bytearray."
        )

    @staticmethod
    def _resample(
        audio: np.ndarray,
        orig_sr: int,
        target_sr: int = 16000,
    ) -> np.ndarray:
        """Resample *audio* to *target_sr* using librosa.

        Args:
            audio: Input waveform as a 1-D float32 array.
            orig_sr: Original sampling rate (Hz).
            target_sr: Desired sampling rate (Hz).

        Returns:
            Resampled waveform as float32. If *orig_sr* already equals
            *target_sr*, a view (or copy) is returned unchanged.
        """
        if orig_sr == target_sr:
            return audio.astype(np.float32, copy=False)

        if audio.size == 0:
            return audio.astype(np.float32, copy=False)

        return librosa.resample(
            audio.astype(np.float32),
            orig_sr=orig_sr,
            target_sr=target_sr,
        )

    @staticmethod
    def _wav_bytes_to_numpy(audio_bytes: bytes) -> np.ndarray:
        """Decode WAV bytes (RIFF header + PCM data) to a float32 array.

        Args:
            audio_bytes: Complete WAV file contents as bytes.

        Returns:
            1-D float32 numpy array at 16 kHz (resampled if necessary).

        Raises:
            ValueError: If *audio_bytes* cannot be parsed as a WAV file.
        """
        try:
            with io.BytesIO(audio_bytes) as f:
                wav, sr = sf.read(f, dtype="float32", always_2d=False)
        except Exception as exc:
            raise ValueError(f"Invalid WAV data: {exc}") from exc

        wav = np.asarray(wav, dtype=np.float32)

        # Handle multi-channel
        if wav.ndim > 1:
            wav = np.mean(wav, axis=tuple(range(1, wav.ndim)), dtype=np.float32)

        # Resample to 16 kHz if needed
        if sr != 16000:
            wav = ASREngine._resample(wav, sr, 16000)

        return wav

    # ------------------------------------------------------------------ #
    # Resource management
    # ------------------------------------------------------------------ #

    def release(self) -> None:
        """Release GPU memory held by the model.

        Safe to call multiple times — subsequent calls are no-ops.
        """
        if self.model is not None:
            try:
                del self.model
            except Exception as exc:
                logger.warning("Exception while releasing model: %s", exc)
            finally:
                self.model = None
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                logger.info("ASR model released and GPU cache cleared.")

    def __del__(self) -> None:
        """Attempt graceful cleanup on garbage collection."""
        try:
            self.release()
        except Exception:
            pass

    def __repr__(self) -> str:
        status = "loaded" if self.health_check() else "not loaded"
        return (
            f"{self.__class__.__name__}("
            f"model_path={self.model_path!r}, "
            f"device={self.device!r}, "
            f"dtype={self.dtype}, "
            f"status={status})"
        )

    def __enter__(self) -> ASREngine:
        """Support ``with`` statement."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Ensure model release on context-manager exit."""
        self.release()
