from logger import logger
from pathlib import Path
from datetime import datetime
import os
import cpy_tool


def _bak_old_bundles():
    """_summary_"""
    logger.info("Bak old bundles.")
    bak_time = datetime.now().strftime("%y-%m-%d-%H%M%S")

    bak_path = Path(os.environ["BUNDLE_COPY_TO"]).parent / "bak" / f"bak_{bak_time}"
    bak_path.mkdir(parents=True, exist_ok=True)

    src_path = Path(os.environ["BUNDLE_COPY_TO"])
    if src_path.exists():
        cpy_tool.move_directory_tree_with_info(
            src_path / "cdn/android", bak_path / "android"
        )
        cpy_tool.move_directory_tree_with_info(src_path / "cdn/ios", bak_path / "ios")
    else:
        logger.warning(f"Path {src_path} does not exist.")


def post_build_bundles():
    _bak_old_bundles()
    package_names = os.environ["PACKAGE_NAMES"].split(",")
    version = os.environ["BUNDLE_VERSION"]
    build_target = os.environ["BUILD_TARGET"]
    _move_bundles(package_names, version, build_target)


def _move_bundles(package_names: str, bundle_version: str, build_target: str) -> None:
    for package_name in package_names:
        from_path = (
            Path(os.environ["BUILD_OUTPUT"])
            / "bundles"
            / build_target
            / package_name
            / bundle_version
        )
        to_path = (
            Path(os.environ["BUNDLE_COPY_TO"])
            / "cdn"
            / build_target.lower()
            / "bundles"
        )
        logger.info(f"move from {from_path} to {to_path}")
        cpy_tool.copy_director_with_info(from_path, to_path, True)


if __name__ == "__main__":
    import build_env_tool

    build_env_tool.set_ci_env("cfg/ci_env.ini")
    _bak_old_bundles()
    # _move_bundles(["DefaultPackage", "RawPackage"], "1.0.0-25-01-06-224641", "Android")
