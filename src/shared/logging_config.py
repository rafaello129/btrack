from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configure_logging(log_dir: Path | None = None) -> None:
    target_dir = log_dir or Path.cwd() / "logs"
    target_dir.mkdir(parents=True, exist_ok=True)
    log_file = target_dir / "btrack.log"

    root = logging.getLogger()
    if root.handlers:
        return

    root.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    rotating = RotatingFileHandler(
        filename=log_file,
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    rotating.setFormatter(formatter)

    stream = logging.StreamHandler()
    stream.setFormatter(formatter)

    root.addHandler(rotating)
    root.addHandler(stream)
