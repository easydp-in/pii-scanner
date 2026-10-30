"""Pass 2 Edge AI NER inference module using GLiNER for deep unstructured PII detection."""

from __future__ import annotations

import contextlib
import importlib.util
import logging
import os
import platform
import shutil
import subprocess
import warnings
from typing import Any

logger = logging.getLogger("pii_scanner.ai")

MODEL_ID = "urchade/gliner_small-v2.1"
DEFAULT_NER_LABELS = ["person name", "address", "medical condition"]

# System resource thresholds for safe Local AI execution
MIN_AVAILABLE_RAM_GB = 2.0
MIN_FREE_DISK_GB = 1.5


def check_system_resources() -> dict[str, Any]:
    """Pre-flight system check: RAM + disk before loading the AI model.

    Returns a dict with:
        total_ram_gb, available_ram_gb, free_disk_gb,
        ram_ok (bool), disk_ok (bool), warnings (list[str])
    """
    result: dict[str, Any] = {
        "total_ram_gb": None,
        "available_ram_gb": None,
        "free_disk_gb": None,
        "ram_ok": True,
        "disk_ok": True,
        "warnings": [],
    }

    # --- Disk space check ---
    cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
    if not os.path.isdir(cache_dir):
        cache_dir = os.path.expanduser("~")

    try:
        usage = shutil.disk_usage(cache_dir)
        free_gb = usage.free / (1024**3)
        result["free_disk_gb"] = round(free_gb, 1)
        if free_gb < MIN_FREE_DISK_GB:
            result["disk_ok"] = False
            result["warnings"].append(
                f"Low disk space: {free_gb:.1f} GB free. "
                f"Local AI needs ~{MIN_FREE_DISK_GB:.0f} GB for the model download."
            )
    except OSError:
        pass

    # --- RAM check (cross-platform, stdlib only) ---
    system = platform.system()
    try:
        if system == "Darwin":
            _check_ram_macos(result)
        elif system == "Linux":
            _check_ram_linux(result)
        elif system == "Windows":
            _check_ram_windows(result)
    except Exception:
        logger.debug("System resource check: unable to read RAM info on %s", system)

    # Evaluate RAM
    avail = result["available_ram_gb"]
    if avail is not None and avail < MIN_AVAILABLE_RAM_GB:
        result["ram_ok"] = False
        result["warnings"].append(
            f"Low memory: {avail:.1f} GB available. "
            f"Local AI needs ~{MIN_AVAILABLE_RAM_GB:.0f} GB free RAM to load the model safely."
        )

    return result


def _check_ram_macos(result: dict[str, Any]) -> None:
    """Read total and available RAM on macOS via sysctl + vm_stat."""
    total_bytes = int(subprocess.check_output(["sysctl", "-n", "hw.memsize"]).strip())
    result["total_ram_gb"] = round(total_bytes / (1024**3), 1)

    vm_out = subprocess.check_output(["vm_stat"]).decode("utf-8", errors="replace")
    page_size = 16384  # Apple Silicon default
    for line in vm_out.splitlines():
        if "page size" in line.lower():
            digits = "".join(c for c in line if c.isdigit())
            if digits:
                page_size = int(digits)
            break

    free_pages = 0
    for line in vm_out.splitlines():
        if "Pages free" in line or "Pages inactive" in line or "Pages speculative" in line:
            parts = line.split(":")
            if len(parts) == 2:
                digits = parts[1].strip().rstrip(".")
                if digits.isdigit():
                    free_pages += int(digits)

    result["available_ram_gb"] = round((free_pages * page_size) / (1024**3), 1)


def _check_ram_linux(result: dict[str, Any]) -> None:
    """Read total and available RAM on Linux via /proc/meminfo."""
    with open("/proc/meminfo") as f:
        for line in f:
            if line.startswith("MemTotal:"):
                result["total_ram_gb"] = round(int(line.split()[1]) / (1024**2), 1)
            elif line.startswith("MemAvailable:"):
                result["available_ram_gb"] = round(int(line.split()[1]) / (1024**2), 1)


def _check_ram_windows(result: dict[str, Any]) -> None:
    """Read total and available RAM on Windows via kernel32."""
    import ctypes

    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    stat = MEMORYSTATUSEX()
    stat.dwLength = ctypes.sizeof(stat)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))  # type: ignore[attr-defined]
    result["total_ram_gb"] = round(stat.ullTotalPhys / (1024**3), 1)
    result["available_ram_gb"] = round(stat.ullAvailPhys / (1024**3), 1)


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
