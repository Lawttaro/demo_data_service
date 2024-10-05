from dagster import Definitions, load_assets_from_modules, FilesystemIOManager
from . import assets

all_assets = load_assets_from_modules([assets])

defs = Definitions(
    assets=all_assets,
    resources={
        "fs_io_manager": FilesystemIOManager()
    }
)
