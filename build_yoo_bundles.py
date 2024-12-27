"""用于yooasset导出bundles"""
import os
import sys
import configparser
import argparse
from datetime import datetime
from pathlib import Path
from logger import logger
import build_tool
import post_build


def build_bundles(file_path):
    """读取bundles配置文件，构建bundles

    Args:
        file_path (string): bundles配置文件路径
    """
    build_tool.setup_build_time()
    logger.info(f"Read bundles config:{file_path}")
    logger.add("logs/bundles/build_bundles_{time}.log",
               backtrace=True, diagnose=True, enqueue=True)
    cfg = configparser.ConfigParser()
    cfg.read(file_path)
    for section in cfg.sections():
        logger.info(f"Build Package:{section}")
        os.environ['PACKAGE_NAME'] = section
        _set_pkg_env(cfg[section])
        _build_package()
    post_build.post_build_bundles_without_pack()


def _set_pkg_env(section):
    for key, value in section.items():
        v = value.replace("\\", "/")
        os.environ[key.upper()] = v
        logger.info(f"Build Env:{key.upper()} = {v}")


def _build_package():
    for target in os.environ['BUILD_TARGET'].split(','):
        logger.info(f"Build Target:{target}")
        os.environ['BUILD_TARGET'] = target
        _build_bundles_and_run_unity_command()


def _build_bundles_and_run_unity_command():
    logger.info(f"Build bundles and run unity command.")
    required_env_vars = ['UNITY_EXECUTABLE', 'PROJ_DIR', 'BUILD_OUTPUT_ROOT',
                         'BUILD_TARGET', 'BUILD_IN_FILE_COPY', 'BUILD_PKG_VER',
                         'FILE_NAME_STYLE', 'COMPRESSION', 'ENCRYPTION',
                         'BUILD_MODE', 'PACKAGE_NAME']
    if not build_tool.check_environ(required_env_vars):
        logger.error("check env failed.")
        sys.exit(1)

    BUILD_TARGET = os.environ['BUILD_TARGET']
    PROJ_DIR = Path(os.environ['PROJ_DIR'])
    OUTPUT_DIR = Path(os.environ['BUILD_OUTPUT_ROOT'])
    UNITY_EXECUTABLE = os.environ.get(
        'UNITY_EXECUTABLE', 'xvfb-run --auto-servernum --server-args="-screen 0 640x480x24" unity-editor')
    PACKAGE_NAME = os.environ['PACKAGE_NAME']
    COPY_OPTION = os.environ['BUILD_IN_FILE_COPY']
    BUILD_MODE = os.environ['BUILD_MODE']

    BUILD_PATH = OUTPUT_DIR
    BUILD_PATH.mkdir(parents=True, exist_ok=True)

    # logfile = f'logs/build_{BUILD_TARGET}_{PACKAGE_NAME}_{_build_time}.log'
    # BUILD_LOG_PATH = BUILD_PATH / logfile
    PACKAGE_VER = os.environ['BUILD_PKG_VER']
    BUILD_TIME = os.environ['BUILD_TIME']

    pkg_version = f"{PACKAGE_VER}-{BUILD_TIME}"

    # 构建 Unity 命令
    unity_cmd = [
        *UNITY_EXECUTABLE.split(),  # 解析可能包含空格的命令
        '-projectPath', str(PROJ_DIR),
        '-quit',
        '-batchmode',
        '-nographics',
        '-buildTarget', BUILD_TARGET,
        '-customBuildTarget', BUILD_TARGET,
        '-customBuildPath', str(BUILD_PATH.absolute()),
        '-pkgName', PACKAGE_NAME,
        '-copyOption', COPY_OPTION,
        '-buildMode', BUILD_MODE,
        '-pkgVersion', pkg_version,
        '-executeMethod', 'BuildCommand.PerformBuildYooBundles',
        # '-logFile', str(BUILD_LOG_PATH.absolute())
    ]

    logger.info(f"Running Unity with command: {' '.join(unity_cmd)}")
    build_tool.run_unity_command(unity_cmd)
    post_build.move_bundles_to_pack(
        BUILD_TARGET, OUTPUT_DIR, PACKAGE_NAME, pkg_version)


def _main():
    logger.info(build_tool.HEADER)
    parser = argparse.ArgumentParser(description="Unity build tool")
    parser.add_argument('cfg_path', type=str, help='build config ini file')
    args = parser.parse_args()
    file_path = Path(args.cfg_path)
    if not file_path.is_file():
        logger.error(f"Error: The file {args.cfg_path} does not exist.")
        return
    build_bundles(file_path)


if __name__ == "__main__":
    _main()
