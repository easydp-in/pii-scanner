"""Centralized logging configuration for EasyDP PII Scanner.

Redirects noisy third-party libraries (openpyxl, pypdf, urllib3) and
runtime warnings to a dedicated file logger (e.g. reports/scanner.log)
while maintaining a pristine, readable console interface.
"""

from __future__ import annotations

import logging
import warnings
from pathlib import Path


def _close_and_clear_handlers(logger: logging.Logger) -> None:
    """Close and remove all handlers from a logger cleanly without leaving open file descriptors."""
    for handler in list(logger.handlers):
        try:
            handler.close()
        except Exception:
            pass
        logger.removeHandler(handler)


def setup_scanner_logging(log_path: str | Path | None = None) -> Path:
    """Initialize dedicated file logging and silence third-party library console noise.

    Args:
        log_path: Optional path to the log file. Defaults to ./reports/scanner.log.

    Returns:
        Resolved absolute Path to the active log file.
    """
    if log_path is None:
        target_path = Path("reports") / "scanner.log"
    else:
        target_path = Path(log_path)

    target_path = target_path.resolve()
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # Dedicated File Handler
    file_handler = logging.FileHandler(str(target_path), mode="w", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)-7s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    _close_and_clear_handlers(root_logger)
    root_logger.addHandler(file_handler)

    # Route Python runtime warnings (e.g., openpyxl UserWarning) into logging
    logging.captureWarnings(True)
    warnings_logger = logging.getLogger("py.warnings")
    _close_and_clear_handlers(warnings_logger)
    warnings_logger.addHandler(file_handler)
    warnings_logger.propagate = False
    warnings.filterwarnings("always")

    # Direct noisy third-party library loggers strictly to file handler without terminal propagation
    noisy_modules = [
        "pypdf",
        "openpyxl",
        "urllib3",
        "charset_normalizer",
        "pdfminer",
    ]
    for mod_name in noisy_modules:
        lib_logger = logging.getLogger(mod_name)
        _close_and_clear_handlers(lib_logger)
        lib_logger.addHandler(file_handler)
        lib_logger.propagate = False
        lib_logger.setLevel(logging.DEBUG)

    # Application logger
    app_logger = logging.getLogger("pii_scanner")
    _close_and_clear_handlers(app_logger)
    app_logger.addHandler(file_handler)
    app_logger.propagate = False
    app_logger.setLevel(logging.DEBUG)
    app_logger.info("EasyDP PII Scanner logging initialized. Log file: %s", target_path)

    return target_path
