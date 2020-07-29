import json
from pathlib import Path

from appcfg import get_config

config = get_config(__name__)

SCHEMA_DIR = Path(__file__).parents[1] / Path(config["schema_dir"])


def load_schema_file(path: Path):
    with path.with_suffix(".json").open() as f:
        return json.load(f)


resources = {
    name: load_schema_file(SCHEMA_DIR / path)
    for name, path in [
        ("descriptors/functions", "descriptors/functions/any"),
        ("descriptors/services", "descriptors/service/service"),
        ("records/functions", "records/functions/any"),
        ("records/services", "records/service"),
    ]
}
