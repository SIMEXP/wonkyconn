from pathlib import Path

import pandas as pd
import pytest

from wonkyconn.config import WonkyconnConfig
from wonkyconn.workflow import load_data_frame


@pytest.mark.parametrize("column", ["participant_id", "age", "gender", "site"])
def test_load_data_frame_missing_column(tmp_path: Path, column: str) -> None:
    """Enabling site correction requires a 'site' column in the phenotypes file."""

    phenotypes = dict(
        participant_id=["sub-1", "sub-2"],
        age=[30.0, 40.0],
        gender=["m", "f"],
        site=["site-a", "site-b"],
    )
    del phenotypes[column]

    phenotypes_path = tmp_path / "participants.tsv"
    pd.DataFrame(phenotypes).to_csv(phenotypes_path, sep="\t", index=False)

    config = WonkyconnConfig(phenotypes=phenotypes_path, site_correction=True)
    with pytest.raises(ValueError, match=column):
        load_data_frame(config)
