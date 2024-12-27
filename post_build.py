from logger import logger
from pathlib import Path
import build_yoo_bundles
import cpy_tool

DST_PATH_ROOT = "E:/cwcx/bundles/250"

def post_build_bundles(bundles_root_path: str, pkg_name: str, version: str):
    """_summary_

    Args:
        file_path (str): _description_
        version (str): _description_
    """
    cpy_src_path = Path(bundles_root_path + "/bundles" +
                        "/Android" + f"/{pkg_name}" + "/" + version)
    if cpy_src_path.exists():
        dst_path = Path(DST_PATH_ROOT + "/android")
        dst_path.mkdir(parents=True, exist_ok=True)
        cpy_tool.copy_directory_tree_with_info(cpy_src_path, dst_path)
    else:
        logger.warning(f"Path {cpy_src_path} does not exist.")

    cpy_src_path = Path(bundles_root_path + "/bundles" +
                        "/iOS" + f"/{pkg_name}" + "/" + version)
    if cpy_src_path.exists():
        dst_path = Path(DST_PATH_ROOT + "/ios")
        dst_path.mkdir(parents=True, exist_ok=True)
        cpy_tool.copy_directory_tree_with_info(cpy_src_path, dst_path)
    else:
        logger.warning(f"Path {cpy_src_path} does not exist.")

def _test():
    post_build_bundles("E:/cwcx", "ResPackage", "1.0.0-24-12-20-191209")

if __name__ == "__main__":
    _test()
