"""Stage 1 orchestrator: fetch + filter + score + write outputs.

Composes the county adapter + listings subtractor + propensity scorer into
a single pipeline. The CLI surface at the bottom (`__main__`) wires this
into the `python off-market/scripts/discover.py <county>` invocation
documented in SKILL.md.

Adding a new county
-------------------

1. Implement an adapter class with ``.load(criteria, *, as_of=None) -> list[Parcel]``
   under ``scripts/county_adapters/<county>.py``.
2. Register it in ``_ADAPTER_REGISTRY`` below.

That's it — output writers and scoring are county-agnostic.

Outputs
-------

Three files under ``<output_dir>/runs/<YYYY-MM-DD>-<county>/``:

  - ``candidates.csv``  — every scored parcel (incl. tier=dropped) for audit.
  - ``candidates.md``   — top 20 candidates as human-readable Markdown.
  - ``health.md``       — per-source fetch status + tier counts.

The audit-everything CSV is intentional: it lets the user see which parcels
the rubric dropped and why, in case the scoring needs tuning.
"""

from __future__ import annotations

import csv
import logging
import urllib.parse
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from scripts.cache import Cache
from scripts.county_adapters.allegheny_pa import AlleghenyPAAdapter
from scripts.criteria import Criteria
from scripts.listings.redfin import fetch_listings
from scripts.listings.subtract import subtract_listed
from scripts.models import Parcel
from scripts.propensity import PropensityScore, score as propensity_score

logger = logging.getLogger(__name__)


# Registry of known counties → adapter classes. Adding a new county is a
# one-line change here plus the adapter file under ``scripts/county_adapters/``.
_ADAPTER_REGISTRY: dict[str, type] = {
    "allegheny_pa": AlleghenyPAAdapter,
}


# CSV column order — kept stable so downstream scripts (outreach, audits)
# can rely on the schema. ``reasons`` is semicolon-separated rather than
# comma-separated so it survives a vanilla CSV reader without quoting.
_CSV_COLUMNS = (
    "parcel_id",
    "address",
    "owner_name",
    "owner_mailing",
    "assessed_value",
    "last_sale_date",
    "last_sale_price",
    "lot_sqft",
    "year_built",
    "tax_owed_usd",
    "sheriff_sale_date",
    "is_absentee",
    "propensity_total",
    "tier",
    "reasons",
    "street_view_url",
)


@dataclass
class DiscoverResult:
    """Summary returned from ``discover()`` for the CLI banner."""

    county: str
    as_of: date
    parcels_total: int
    parcels_after_listings_filter: int
    candidates_scored: int  # every parcel that got a propensity score
    candidates_kept: int    # tier != "dropped"
    output_files: list[Path]
    health: dict[str, Any] = field(default_factory=dict)
    tier_counts: dict[str, int] = field(default_factory=dict)


# ---------- helpers ----------


def _street_view_url(address: str) -> str:
    """Return a Google Maps URL that searches the parcel's address.

    WPRDC parcels don't carry lat/long; the search URL is a fair substitute —
    one click lands on Street View when there's a match.
    """
    return f"https://www.google.com/maps?q={urllib.parse.quote_plus(address)}"


def _format_date(d: date | None) -> str:
    return d.isoformat() if d else ""


def _format_float(x: float | None) -> str:
    return f"{x:.2f}" if x is not None else ""


def _format_int(x: int | None) -> str:
    return str(x) if x is not None else ""


def _row_for(parcel: Parcel, score: PropensityScore) -> dict[str, str]:
    return {
        "parcel_id": parcel.parcel_id,
        "address": parcel.address,
        "owner_name": parcel.owner_name,
        "owner_mailing": parcel.owner_mailing,
        "assessed_value": _format_float(parcel.assessed_value),
        "last_sale_date": _format_date(parcel.last_sale_date),
        "last_sale_price": _format_float(parcel.last_sale_price),
        "lot_sqft": _format_float(parcel.lot_sqft),
        "year_built": _format_int(parcel.year_built),
        "tax_owed_usd": _format_float(parcel.tax_owed_usd),
        "sheriff_sale_date": _format_date(parcel.sheriff_sale_date),
        "is_absentee": "true" if parcel.is_absentee() else "false",
        "propensity_total": f"{score.total:.0f}",
        "tier": score.tier,
        "reasons": ";".join(score.reasons),
        "street_view_url": _street_view_url(parcel.address),
    }


# ---------- writers ----------


def _write_candidates_csv(
    path: Path, scored: list[tuple[Parcel, PropensityScore]]
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(_CSV_COLUMNS))
        writer.writeheader()
        for parcel, score in scored:
            writer.writerow(_row_for(parcel, score))


def _write_candidates_md(
    path: Path, candidates: list[tuple[Parcel, PropensityScore]], top_n: int = 20
) -> None:
    lines = ["# Top off-market candidates", ""]
    if not candidates:
        lines.append("_No candidates scored above the drop threshold (≥15)._")
        lines.append("")
        path.write_text("\n".join(lines))
        return
    for i, (parcel, score) in enumerate(candidates[:top_n], start=1):
        lines.append(f"## #{i} — Score {score.total:.0f} ({score.tier})")
        lines.append(parcel.address)
        mailing = parcel.owner_mailing or "(unknown)"
        lines.append(f"Owner: {parcel.owner_name} (mailing: {mailing})")
        if score.reasons:
            lines.append(f"Signals: {', '.join(score.reasons)}")
        else:
            lines.append("Signals: (none)")
        lines.append(f"Street view: {_street_view_url(parcel.address)}")
        lines.append("")
    path.write_text("\n".join(lines))


def _write_health_md(
    path: Path,
    *,
    county: str,
    as_of: date,
    health: dict[str, Any],
    tier_counts: dict[str, int],
    candidates_kept: int,
) -> None:
    lines = [
        f"# Run health — {county} — {as_of.isoformat()}",
        "",
        f"- Parcels fetched: {health.get('parcels_total', 0):,}",
        f"- Active listings subtracted: {health.get('listings_subtracted', 0)}",
        f"- Parcels scored: {health.get('candidates_scored', 0):,}",
        f"- Candidates (score ≥ 15): {candidates_kept:,}",
        f"  - Act this week (≥70): {tier_counts.get('act_this_week', 0)}",
        f"  - High priority (40-69): {tier_counts.get('high_priority', 0)}",
        f"  - Worth a letter (15-39): {tier_counts.get('worth_a_letter', 0)}",
        "",
        "## Sources",
        "",
    ]
    for source_label, status in health.get("sources", []):
        lines.append(f"- {source_label}: {status}")
    if not health.get("sources"):
        lines.append("- (no source health captured)")
    lines.append("")
    path.write_text("\n".join(lines))


# ---------- orchestrator ----------


def discover(
    county: str,
    criteria: Criteria,
    *,
    output_dir: Path,
    use_cache: bool = True,
    as_of: date | None = None,
) -> DiscoverResult:
    """Run Stage 1: load parcels → subtract listings → score → write outputs.

    Args:
        county: registry key for a known adapter (e.g. ``"allegheny_pa"``).
        criteria: user buying constraints; protected-class fields rejected at
            criteria-load time.
        output_dir: parent directory for the timestamped run directory. The
            actual outputs land at ``<output_dir>/runs/<as_of>-<county>/``.
        use_cache: when True, the adapter is given a ``Cache`` rooted at
            ``~/.cache/off-market/`` so repeat runs don't re-hit upstream
            sources. Tests pass False to bypass.
        as_of: optional "as of" date for scoring (used by sheriff-sale signal
            to decide what's a future auction). Defaults to ``date.today()``.

    Returns:
        ``DiscoverResult`` with counts + paths for the CLI banner.

    Raises:
        KeyError: if ``county`` is not registered in ``_ADAPTER_REGISTRY``.
    """
    if as_of is None:
        as_of = date.today()

    if county not in _ADAPTER_REGISTRY:
        raise KeyError(
            f"unknown county {county!r}; known: {sorted(_ADAPTER_REGISTRY)}"
        )

    # 1. Adapter ----------------------------------------------------------
    cache = (
        Cache(root=Path.home() / ".cache" / "off-market") if use_cache else None
    )
    adapter_cls = _ADAPTER_REGISTRY[county]
    adapter = adapter_cls(cache=cache)
    parcels = adapter.load(criteria, as_of=as_of)
    health: dict[str, Any] = {
        "parcels_total": len(parcels),
        "sources": [
            (
                f"{county} adapter",
                f"OK (parcels: {len(parcels)}, cache: {'on' if cache else 'off'})",
            ),
        ],
    }

    # 2. Listings subtraction --------------------------------------------
    if criteria.zips:
        listings: set[str] = set()
        per_zip: list[tuple[str, int]] = []
        for zip_code in criteria.zips:
            try:
                fetched = fetch_listings(zip_code)
            except Exception as exc:  # pragma: no cover — fetcher catches its own
                logger.warning("listings fetch failed for %s: %s", zip_code, exc)
                fetched = []
            per_zip.append((zip_code, len(fetched)))
            listings |= set(fetched)
        parcels_after = subtract_listed(parcels, listings)
        subtracted = len(parcels) - len(parcels_after)
        health["listings_subtracted"] = subtracted
        zips_summary = ", ".join(f"{z}:{n}" for z, n in per_zip)
        health["sources"].append(
            (
                "Redfin listings",
                f"OK (zips: {zips_summary}, subtracted: {subtracted})",
            )
        )
    else:
        parcels_after = parcels
        health["listings_subtracted"] = 0
        health["sources"].append(
            ("Redfin listings", "skipped (no zips in criteria)")
        )

    health["parcels_after_listings_filter"] = len(parcels_after)

    # 3. Score every remaining parcel ------------------------------------
    scored: list[tuple[Parcel, PropensityScore]] = [
        (p, propensity_score(p, as_of=as_of)) for p in parcels_after
    ]
    scored.sort(key=lambda ps: ps[1].total, reverse=True)
    candidates = [(p, s) for p, s in scored if s.tier != "dropped"]
    health["candidates_scored"] = len(scored)

    tier_counts: dict[str, int] = {}
    for _, s in candidates:
        tier_counts[s.tier] = tier_counts.get(s.tier, 0) + 1

    # 4. Write outputs ---------------------------------------------------
    run_dir = output_dir / "runs" / f"{as_of.isoformat()}-{county}"
    run_dir.mkdir(parents=True, exist_ok=True)
    csv_path = run_dir / "candidates.csv"
    md_path = run_dir / "candidates.md"
    health_path = run_dir / "health.md"

    _write_candidates_csv(csv_path, scored)
    _write_candidates_md(md_path, candidates)
    _write_health_md(
        health_path,
        county=county,
        as_of=as_of,
        health=health,
        tier_counts=tier_counts,
        candidates_kept=len(candidates),
    )

    return DiscoverResult(
        county=county,
        as_of=as_of,
        parcels_total=len(parcels),
        parcels_after_listings_filter=len(parcels_after),
        candidates_scored=len(scored),
        candidates_kept=len(candidates),
        output_files=[csv_path, md_path, health_path],
        health=health,
        tier_counts=tier_counts,
    )
