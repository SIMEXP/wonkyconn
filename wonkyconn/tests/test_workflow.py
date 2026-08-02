import argparse
from pathlib import Path

import pandas as pd
import pytest

from wonkyconn.workflow import load_data_frame


def test_load_data_frame_requires_site_column(tmp_path: Path) -> None:
    """Enabling site correction requires a 'site' column in the phenotypes file."""
    phenotypes_path = tmp_path / "participants.tsv"
    pd.DataFrame(
        dict(
            participant_id=["sub-1", "sub-2"],
            age=[30.0, 40.0],
            gender=["m", "f"],
        )
    ).to_csv(phenotypes_path, sep="\t", index=False)

    args = argparse.Namespace(phenotypes=phenotypes_path, site_correction=True)
    with pytest.raises(ValueError, match="site"):
        load_data_frame(args)
