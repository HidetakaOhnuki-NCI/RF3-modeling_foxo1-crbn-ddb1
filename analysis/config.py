"""Load and enforce the public RF3 inference protocol."""

from __future__ import annotations

import json
import numbers
from collections.abc import Mapping
from pathlib import Path
from typing import Any


PROTOCOL_FIELDS = ("num_steps", "n_recycles", "diffusion_batch_size")


def _integer_value(value: object, *, field: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be an integer, not a Boolean")
    if isinstance(value, numbers.Integral):
        return int(value)
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    raise ValueError(f"{field} must be an integer")


def load_protocol(path: Path) -> dict[str, Any]:
    """Read a protocol JSON file and validate its required inference fields."""
    try:
        protocol = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read protocol JSON: {path}") from exc
    if not isinstance(protocol, dict) or not isinstance(protocol.get("inference"), dict):
        raise ValueError("Protocol must contain an inference object")
    inference = protocol["inference"]
    for field in PROTOCOL_FIELDS:
        if field not in inference:
            raise ValueError(f"Protocol is missing inference.{field}")
        inference[field] = _integer_value(inference[field], field=field)
    return protocol


def validate_protocol_record(record: Mapping[str, object], protocol: Mapping[str, Any]) -> None:
    """Reject a model record whose RF3 inference settings differ from protocol."""
    inference = protocol.get("inference")
    if not isinstance(inference, Mapping):
        raise ValueError("Protocol must contain an inference mapping")
    for field in PROTOCOL_FIELDS:
        if field not in record:
            raise ValueError(f"Model record is missing {field}")
        if field not in inference:
            raise ValueError(f"Protocol is missing inference.{field}")
        actual = _integer_value(record[field], field=field)
        expected = _integer_value(inference[field], field=f"inference.{field}")
        if actual != expected:
            raise ValueError(f"{field}={actual} does not match required value {expected}")
