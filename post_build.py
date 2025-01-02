from logger import logger
from pathlib import Path
from datetime import datetime
import os
import cpy_tool

DST_PATH_ROOT = "/Volumes/cwcx/ch_auto"


def bak_old_bundles():
    """_summary_"""
    logger.info("Bak old bundles.")
    bak_time = datetime.now().strftime('%y-%m-%d-%H%M%S')

    dst_path = Path(f"{DST_PATH_ROOT}/bak/{bak_time}")
    dst_path.mkdir(parents=True, exist_ok=True)

    src_path = Path(f"{DST_PATH_ROOT}/auto_bundles")
    if src_path.exists():
        cpy_tool.move_directory_tree_with_info(src_path, f"{dst_path}")
    else:
        logger.warning(f"Path {src_path} does not exist.")


def move_bundles_to_pack(build_target: str, bundles_root_path: str, pkg_name: str, version: str):
    logger.info(f"Move build bundles to pack: {build_target}, {bundles_root_path}, {pkg_name}, {version}")
    cpy_src_path = Path(
        f"{bundles_root_path}/{build_target}/{pkg_name}/{version}")
    if cpy_src_path.exists():
        dst_path = Path(
            f"{bundles_root_path}/pack/{version}/{build_target.lower()}/bundles")
        dst_path.mkdir(parents=True, exist_ok=True)
        cpy_tool.move_all_files_and_dirs(cpy_src_path, dst_path)
    else:
        logger.warning(f"Error. Path {cpy_src_path} does not exist.")


def post_build_bundles():
    archive_path = pack_bundles()
    file_name = Path(archive_path).name
    dst_archive_path = Path(f"{DST_PATH_ROOT}/pack")
    logger.info(f"Copy archive from {archive_path} to {dst_archive_path}")
    cpy_tool.copy_with_info(archive_path, dst_archive_path)
    bak_old_bundles()
    logger.info(f"Unzip archive {dst_archive_path}/{file_name} to {DST_PATH_ROOT}/auto_bundles")
    cpy_tool.unzip_file(Path(f"{dst_archive_path}/{file_name}"), f"{DST_PATH_ROOT}/auto_bundles")

def post_build_bundles_without_pack():
    bak_old_bundles()
    version = f"{os.environ['BUILD_PKG_VER']}-{os.environ['BUILD_TIME']}"
    bundle_path = Path(f"{os.environ['BUILD_OUTPUT_ROOT']}/pack/{version}")
    dst_path = Path(f"{DST_PATH_ROOT}/auto_bundles")
    if not dst_path.exists():
        dst_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Copy directory with progress from {bundle_path} to {dst_path}")
    cpy_tool.copy_directory_with_progress(bundle_path, dst_path)

def pack_bundles() -> str:
    logger.info("Pack bundles.")
    version = f"{os.environ['BUILD_PKG_VER']}-{os.environ['BUILD_TIME']}"
    bundle_path = Path(f"{os.environ['BUILD_OUTPUT_ROOT']}/pack/{version}")
    return cpy_tool.pack_directory_to_specific_location(bundle_path, bundle_path.parent, f"{version}")


if __name__ == "__main__":
    logger.info("Post build bundles start.")
    src = Path(r"E:\cwcx\bundles\pack\1.0.0-24-12-27-221505.zip") 
    logger.info(f"src is file: {src.is_file()}")
    dst = Path(r"X:\ch_auto\pack\1.0.0-24-12-27-221505.zip")
    if not dst.parent.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"dst is dir: {dst.is_dir()}")
    cpy_tool.copy_with_info(src, dst)
    unzip_dst = Path(r"X:\ch_auto\auto_bundles")
    if not unzip_dst.exists():
        unzip_dst.mkdir(parents=True, exist_ok=True)
    cpy_tool.unzip_file(dst, unzip_dst)
    logger.info("Post build bundles end.")
