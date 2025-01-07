"""用于yooasset导出bundles"""

import os
import sys
from pathlib import Path
from logger import logger
import build_tool
import post_build
import build_env_tool


def build_bundles():
    package_names = os.environ["PACKAGE_NAMES"].split(",")
    for package_name in package_names:
        _build_one_package(package_name)


def _build_one_package(package_name: str):
    build_env_tool.set_package_env(package_name)
    required_env_vars = [
        "UNITY_EXECUTABLE",
        "PROJ_DIR",
        "BUILD_TARGET",
        "BUILD_IN_FILE_COPY",
        "FILE_NAME_STYLE",
        "COMPRESSION",
        "ENCRYPTION",
        "BUILD_MODE",
        "VERSION_BUILD_VAR",
        "PACKAGE_NAME",
    ]
    if not build_env_tool.check_environ(required_env_vars):
        logger.error("check env failed.")
        sys.exit(1)
    _build_bundles_and_run_unity_command()


def _build_bundles_and_run_unity_command():
    logger.info("Build bundles and run unity command.")

    BUILD_TARGET = os.environ["BUILD_TARGET"]
    PROJ_DIR = Path(os.environ["PROJ_DIR"])
    OUTPUT_DIR = Path(os.environ["BUILD_OUTPUT"])
    UNITY_EXECUTABLE = os.environ.get(
        "UNITY_EXECUTABLE",
        'xvfb-run --auto-servernum --server-args="-screen 0 640x480x24" unity-editor',
    )
    PACKAGE_NAME = os.environ["PACKAGE_NAME"]
    COPY_OPTION = os.environ["BUILD_IN_FILE_COPY"]
    BUILD_MODE = os.environ["BUILD_MODE"]

    BUILD_PATH = OUTPUT_DIR / "bundles"
    BUILD_PATH.mkdir(parents=True, exist_ok=True)

    # logfile = f'logs/build_{BUILD_TARGET}_{PACKAGE_NAME}_{_build_time}.log'
    # BUILD_LOG_PATH = BUILD_PATH / logfile
    PACKAGE_VER = os.environ["VERSION_BUILD_VAR"]
    BUILD_TIME = os.environ["BUILD_TIME"]

    pkg_version = f"{PACKAGE_VER}-{BUILD_TIME}"
    os.environ["BUNDLE_VERSION"] = pkg_version

    # 构建 Unity 命令
    unity_cmd = [
        *UNITY_EXECUTABLE.split(),  # 解析可能包含空格的命令
        "-projectPath",
        str(PROJ_DIR),
        "-quit",
        "-batchmode",
        "-nographics",
        "-buildTarget",
        BUILD_TARGET,
        "-customBuildTarget",
        BUILD_TARGET,
        "-customBuildPath",
        str(BUILD_PATH),
        "-pkgName",
        PACKAGE_NAME,
        "-copyOption",
        COPY_OPTION,
        "-buildMode",
        BUILD_MODE,
        "-pkgVersion",
        pkg_version,
        "-executeMethod",
        "BuildCommand.PerformBuildYooBundles",
        # # '-logFile', str(BUILD_LOG_PATH.absolute())
    ]

    cmd = " ".join(unity_cmd)
    build_tool.run_unity_command(cmd)
    # post_build.move_bundles_to_pack(BUILD_TARGET, OUTPUT_DIR, PACKAGE_NAME, pkg_version)


def _main():
    logger.info(build_tool.HEADER)
    build_tool.setup_build_time()
    logger.add(
        f"logs/bundles/build-bundles-{os.environ['BUILD_TIME']}.log",
        backtrace=True,
        diagnose=True,
        enqueue=True,
    )
    build_env_tool.load_config_from_args()
    build_bundles()
    post_build.post_build_bundles()


if __name__ == "__main__":
    _main()
