"""Allegheny County, PA — adapter wiring four WPRDC fetchers into Parcels.

Composes ``wprdc.parcels`` + ``wprdc.sales`` + ``wprdc.delinquency`` +
``allegheny_sheriff`` into enriched ``Parcel`` objects, then filters by
the user-supplied ``Criteria``.

Join keys
---------

- Sales and delinquency join on ``Parcel.parcel_id`` (both feeds publish
  ``PARID``/``pin``).
- Sheriff sales have **no PARID** — the WPRDC dataset publishes Street/City/
  State/ZIPCode only. We join by extracting the street portion of
  ``Parcel.address`` (dropping the ``, CITY, STATE ZIP`` tail) and running
  it through ``allegheny_sheriff.normalize_address`` so both sides collapse
  to the same canonical form (lowercase, abbreviations expanded).

Caching
-------

If a ``Cache`` is supplied, each fetcher is wrapped in
``cache.get_or_fetch(county, source, fetcher, ttl_days)`` with these TTLs
(per ``references/adding-county-adapter.md``):

  - parcels:      30 days
  - sales:         7 days  (recency matters for tenure scoring)
  - delinquency:   7 days
  - sheriff:       7 days

If ``cache`` is ``None``, fetchers are called directly with no persistence.

Filtering
---------

``Criteria`` fields are applied as monotonic hard filters — a parcel is
dropped if it FAILS any specified constraint. ``None`` criteria fields
are skipped. Ordering is not the adapter's job; the propensity scorer
ranks downstream.
"""

from __future__ import annotations

import dataclasses
import logging
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Callable

from scripts.cache import Cache
from scripts.county_adapters.allegheny_sheriff import (
    fetch_sheriff_sales,
    normalize_address,
)
from scripts.county_adapters.wprdc.delinquency import fetch_delinquency
from scripts.county_adapters.wprdc.parcels import fetch_parcels
from scripts.county_adapters.wprdc.sales import Sale, fetch_sales
from scripts.criteria import Criteria
from scripts.models import Parcel

logger = logging.getLogger(__name__)


# Address-tail stripping + abbreviation expansion are shared with the listings
# subtractor — see ``scripts.listings.address_norm.normalize``. The shared
# normalizer handles trailing ", CITY, STATE ZIP" itself, so no separate
# `_street_only` helper is needed at this layer.


@dataclass
class AlleghenyPAAdapter:
    """Allegheny County, PA — adapter composing WPRDC + sheriff sales."""

    cache: Cache | None = None
    # Per-fetcher row caps. Live fetchers stream paginated; these bound the
    # working set during one-shot loads. ``parcels_limit`` was raised from
    # 1_000 to 10_000 alongside the server-side zip push-down — a single
    # zip's worth of parcels comfortably fits but the prior cap was tight
    # enough to truncate even 2-3 mid-density zips on an unfiltered run.
    parcels_limit: int = 10_000
    sales_limit: int = 10_000
    delinquency_limit: int = 10_000
    sheriff_limit: int = 1_000

    COUNTY_NAME: str = field(default="allegheny_pa", init=False)

    # ---------- fetch (cache-wrapped or direct) ----------

    # The on-disk cache stores JSON, but fetchers return dataclasses + `date`
    # objects. We wrap each fetcher with an encode step (object → JSON-safe
    # dict/list) and a decode step (JSON-safe → object) on read.

    @staticmethod
    def _encode_parcels(parcels: list[Parcel]) -> list[dict]:
        return [dataclasses.asdict(p) for p in parcels]

    @staticmethod
    def _decode_parcels(payload: Any) -> list[Parcel]:
        out: list[Parcel] = []
        for d in payload:
            d = dict(d)
            for k in ("last_sale_date", "sheriff_sale_date"):
                if d.get(k):
                    d[k] = date.fromisoformat(d[k])
            out.append(Parcel(**d))
        return out

    @staticmethod
    def _encode_sales(sales: dict[str, Sale]) -> dict[str, dict]:
        return {
            pid: {
                "parcel_id": s.parcel_id,
                "sale_date": s.sale_date.isoformat(),
                "sale_price": s.sale_price,
            }
            for pid, s in sales.items()
        }

    @staticmethod
    def _decode_sales(payload: Any) -> dict[str, Sale]:
        return {
            pid: Sale(
                parcel_id=d["parcel_id"],
                sale_date=date.fromisoformat(d["sale_date"]),
                sale_price=float(d["sale_price"]),
            )
            for pid, d in payload.items()
        }

    @staticmethod
    def _encode_sheriff(sheriff: dict[str, date]) -> dict[str, str]:
        return {k: v.isoformat() for k, v in sheriff.items()}

    @staticmethod
    def _decode_sheriff(payload: Any) -> dict[str, date]:
        return {k: date.fromisoformat(v) for k, v in payload.items()}

    def _maybe_cached(
        self,
        source: str,
        fetcher: Callable[[], Any],
        ttl_days: int,
        encode: Callable[[Any], Any] | None = None,
        decode: Callable[[Any], Any] | None = None,
    ):
        if self.cache is None:
            return fetcher()
        wrapped = (lambda: encode(fetcher())) if encode else fetcher
        cached = self.cache.get_or_fetch(
            county=self.COUNTY_NAME, source=source, fetcher=wrapped, ttl_days=ttl_days
        )
        return decode(cached) if decode else cached

    def _load_parcels(self, zips: list[str] | None = None) -> list[Parcel]:
        # Cache key includes zip scope so a single-zip run doesn't poison the
        # cache for a later wider-scope run (and vice versa).
        source = "parcels" if not zips else f"parcels__zips={','.join(sorted(zips))}"
        return self._maybe_cached(
            source,
            lambda: fetch_parcels(limit=self.parcels_limit, zips=zips),
            ttl_days=30,
            encode=self._encode_parcels,
            decode=self._decode_parcels,
        )

    def _load_sales(self, zips: list[str] | None = None) -> dict[str, Sale]:
        source = "sales" if not zips else f"sales__zips={','.join(sorted(zips))}"
        return self._maybe_cached(
            source,
            lambda: fetch_sales(limit=self.sales_limit, zips=zips),
            ttl_days=7,
            encode=self._encode_sales,
            decode=self._decode_sales,
        )

    def _load_delinquency(self) -> dict[str, float]:
        # Already JSON-safe (dict[str, float]).
        return self._maybe_cached(
            "delinquency",
            lambda: fetch_delinquency(limit=self.delinquency_limit),
            ttl_days=7,
        )

    def _load_sheriff(self) -> dict[str, date]:
        return self._maybe_cached(
            "sheriff",
            lambda: fetch_sheriff_sales(limit=self.sheriff_limit),
            ttl_days=7,
            encode=self._encode_sheriff,
            decode=self._decode_sheriff,
        )

    # ---------- enrich ----------

    @staticmethod
    def _enrich(
        parcel: Parcel,
        sales: dict[str, Sale],
        delinquency: dict[str, float],
        sheriff: dict[str, date],
    ) -> Parcel:
        """Mutate-and-return: populate optional fields from the three side-feeds."""
        sale = sales.get(parcel.parcel_id)
        if sale is not None:
            parcel.last_sale_date = sale.sale_date
            parcel.last_sale_price = sale.sale_price

        tax_owed = delinquency.get(parcel.parcel_id)
        if tax_owed is not None:
            parcel.tax_owed_usd = tax_owed

        # Sheriff side joins on the shared normalized address (which already
        # strips ", CITY, STATE ZIP" tails and expands abbreviations).
        sheriff_key = normalize_address(parcel.address)
        sale_date = sheriff.get(sheriff_key)
        if sale_date is not None:
            parcel.sheriff_sale_date = sale_date

        return parcel

    # ---------- filter ----------

    @staticmethod
    def _matches(parcel: Parcel, c: Criteria) -> bool:
        """Return True iff `parcel` satisfies every non-None criterion in `c`."""
        if c.beds_min is not None and (parcel.beds is None or parcel.beds < c.beds_min):
            return False
        if c.baths_min is not None and (
            parcel.baths is None or parcel.baths < c.baths_min
        ):
            return False
        if c.lot_sqft_min is not None and (
            parcel.lot_sqft is None or parcel.lot_sqft < c.lot_sqft_min
        ):
            return False
        if c.lot_sqft_max is not None and (
            parcel.lot_sqft is not None and parcel.lot_sqft > c.lot_sqft_max
        ):
            return False
        if c.year_built_min is not None and (
            parcel.year_built is None or parcel.year_built < c.year_built_min
        ):
            return False
        if c.year_built_max is not None and (
            parcel.year_built is not None and parcel.year_built > c.year_built_max
        ):
            return False
        if c.price_min is not None and (
            parcel.assessed_value is None or parcel.assessed_value < c.price_min
        ):
            return False
        if c.price_max is not None and (
            parcel.assessed_value is not None and parcel.assessed_value > c.price_max
        ):
            return False
        # NOTE: ``c.zips`` is intentionally NOT re-checked here — when criteria
        # specify zips, ``load()`` pushes the filter down to CKAN's
        # ``datastore_search`` via the ``filters`` query param so parcels arrive
        # pre-filtered by ``PROPERTYZIP``. Re-applying a Python-side regex on
        # the composed address would only fire false negatives on rows whose
        # PROPERTYZIP was set but address composition dropped the zip token.
        return True

    # ---------- load (orchestrator) ----------

    def load(self, criteria: Criteria, *, as_of: date | None = None) -> list[Parcel]:
        """Fetch all sources, enrich, filter, return ranked ``Parcel`` list.

        ``as_of`` is reserved for future point-in-time queries (e.g. "what
        would the off-market list have looked like on date X"). Unused
        today — the underlying datasets don't carry historical snapshots.

        When ``criteria.zips`` is non-empty, parcels + sales are fetched
        with a server-side ``PROPERTYZIP`` filter (push-down). Without this,
        a single-zip criteria typically returned 0 parcels because the
        ``limit``-sized fetch was a random slice across 580K county rows.
        Delinquency + sheriff feeds have no zip column, so they're still
        post-joined by ``parcel_id`` / normalized address.
        """
        zips = list(criteria.zips) if criteria.zips else None
        parcels = self._load_parcels(zips=zips)
        sales = self._load_sales(zips=zips)
        delinquency = self._load_delinquency()
        sheriff = self._load_sheriff()

        enriched = [self._enrich(p, sales, delinquency, sheriff) for p in parcels]
        return [p for p in enriched if self._matches(p, criteria)]
