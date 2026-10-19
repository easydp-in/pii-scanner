"""Pass 2 Edge AI NER inference module using GLiNER for deep unstructured PII detection."""

from __future__ import annotations

import contextlib
import importlib.util
import logging
import os
import warnings
from typing import Any

logger = logging.getLogger("pii_scanner.ai")

MODEL_ID = "urchade/gliner_small-v2.1"
DEFAULT_NER_LABELS = ["person name", "address", "medical condition"]


class LocalEdgeNER:
    """Zero-shot lightweight local edge NER running 100% on CPU in-process."""

    def __init__(
        self,
        model_name: str = MODEL_ID,
        threshold: float = 0.50,
        labels: list[str] | None = None,
    ) -> None:
        self.model_name = model_name
        self.threshold = threshold
        self.labels = labels or DEFAULT_NER_LABELS
        self._model: Any = None

    @classmethod
    def is_available(cls) -> bool:
        """Check whether gliner and its runtime dependencies are installed."""
        return importlib.util.find_spec("gliner") is not None

    def load_model(self) -> None:
        """Load or download the local edge GLiNER model checkpoint with suppressed background noise."""
        if self._model is not None:
            return

        if not self.is_available():
            raise ImportError(
                "GLiNER is not installed. Run 'pip install \"easydp-pii-scanner[ai]\"' to enable Pass 2 AI detection."
            )

        os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        os.environ["HF_HUB_VERBOSITY"] = "error"
        os.environ["TRANSFORMERS_VERBOSITY"] = "error"
        os.environ["TQDM_DISABLE"] = "1"

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            logging.getLogger("transformers").setLevel(logging.ERROR)
            logging.getLogger("gliner").setLevel(logging.ERROR)
            logging.getLogger("huggingface_hub").setLevel(logging.ERROR)

            from gliner import GLiNER

            logger.info("Loading Pass 2 Local Edge AI NER model (%s)...", self.model_name)
            with open(os.devnull, "w") as devnull:
                with contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(devnull):
                    self._model = GLiNER.from_pretrained(self.model_name)
            logger.info("Pass 2 Local Edge AI NER model loaded successfully.")

    def predict_entities(self, text: str) -> list[dict[str, Any]]:
        """Run in-process CPU zero-shot NER extraction on natural language text.

        Returns a list of dicts:
            [{"text": entity_text, "label": entity_label, "score": float}, ...]
        """
        if self._model is None:
            return []

        text_stripped = text.strip()
        if len(text_stripped) < 6:
            return []

        try:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore")
                with open(os.devnull, "w") as devnull:
                    with contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(devnull):
                        results: list[dict[str, Any]] = self._model.predict_entities(
                            text_stripped, self.labels, threshold=self.threshold
                        )
                return results or []
        except Exception as e:
            logger.debug("LocalEdgeNER prediction failed on text slice: %s", e)
            return []
