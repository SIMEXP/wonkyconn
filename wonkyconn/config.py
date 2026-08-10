from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, TypeAlias


def _coerce_path(value: str | Path | None) -> Path | None:
    """Expand and resolve *value* to an absolute ``Path``, or return ``None``."""
    if value is None:
        return None
    return Path(value).expanduser().resolve()


Metric: TypeAlias = Literal["motion", "analytic-insights", "gradients", "prediction"]

light_mode_metrics: set[Metric] = {"motion", "analytic-insights"}
all_metrics: set[Metric] = {"motion", "analytic-insights", "gradients", "prediction"}


@dataclass
class WonkyconnConfig:
    """Shared configuration for CLI and GUI."""

    bids_dir: Path | None = None
    output_dir: Path | None = None
    analysis_level: str = "group"
    phenotypes: Path | None = None
    atlas: list[tuple[str, Path]] = field(default_factory=list)
    log_level: str | None = None
    debug: bool = False
    metrics: set[Metric] | None = None
    theme: str | None = None  # GUI-only
    suppress_warnings: bool = False
    site_correction: bool = False

    @property
    def light_mode(self) -> bool:
        return self.metrics == light_mode_metrics

    @classmethod
    def from_cli_args(cls, args: argparse.Namespace | None) -> "WonkyconnConfig":
        """Create a config from argparse args (may be partial when GUI is requested)."""
        if args is None:
            return cls()

        atlas_entries: list[tuple[str, Path]] = list()
        for label, atlas_path in args.atlas or []:
            atlas_entries.append((label, Path(atlas_path).expanduser().resolve()))

        metrics: set[Metric] = light_mode_metrics if args.light_mode else set(args.metrics)

        return cls(
            bids_dir=_coerce_path(args.bids_dir),
            output_dir=_coerce_path(args.output_dir),
            analysis_level=args.analysis_level,
            phenotypes=_coerce_path(args.phenotypes),
            atlas=atlas_entries,
            log_level=args.log_level,
            debug=bool(args.debug),
            metrics=metrics,
            suppress_warnings=bool(args.suppress_warnings),
            site_correction=bool(args.site_correction),
        )
