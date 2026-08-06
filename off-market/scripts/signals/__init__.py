"""Signal results.

Each signal module exports a `score(parcel, *, extra=None)` function that returns
a SignalResult. matched=False means the signal did not fire (weight should be 0).
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class SignalResult:
    matched: bool
    weight: float
    reason: str  # "" when not matched
