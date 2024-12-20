"""用于yooasset导出bundles"""
import os
import sys
import configparser
import argparse
from datetime import datetime
from pathlib import Path
from logger import logger
import build_app


def build_bundles(file_path):
    """读取bundles配置文件，构建bundles

    Args:
        file_path (string): bundles配置文件路径
    """
    logger.info(f"Read bundles config:{file_path}")
    cfg = configparser.ConfigParser()
    cfg.read(file_path)
    for section in cfg.sections():
        logger.info(f"Build Package:{section}")
        os.environ['PACKAGE_NAME'] = section
        _set_pkg_env(cfg[section])
        _build_package()


def _set_pkg_env(section):
    for key, value in section.items():
        os.environ[key.upper()] = value
        logger.info(f"Build Env:{key.upper()} = {value}")


def _build_package():
    for target in os.environ['BUILD_TARGET'].split(','):
        logger.info(f"Build Target:{target}")
        os.environ['BUILD_TARGET'] = target
        _build_bundles_and_run_unity_command()


def _build_bundles_and_run_unity_command():
    required_env_vars = ['UNITY_EXECUTABLE', 'PROJ_DIR', 'BUILD_OUTPUT_ROOT',
                         'BUILD_TARGET', 'BUILD_IN_FILE_COPY', 'BUILD_PKG_VER',
                         'FILE_NAME_STYLE', 'COMPRESSION', 'ENCRYPTION',
                         'BUILD_MODE', 'PACKAGE_NAME']
    if not build_app.check_environ(required_env_vars):
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

    current_date = datetime.now().strftime('%y-%m-%d-%H%M%S')
    logfile = f'logs/build_{BUILD_TARGET}_{PACKAGE_NAME}_{current_date}.log'
    BUILD_LOG_PATH = BUILD_PATH / logfile

    PACKAGE_VER = os.environ['BUILD_PKG_VER']
    PACKAGE_VER = PACKAGE_VER + "-" + current_date

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
        '-pkgVersion', PACKAGE_VER,
        '-executeMethod', 'BuildCommand.PerformBuildYooBundles',
        '-logFile', str(BUILD_LOG_PATH.absolute())
    ]

    logger.info(f"Running Unity with command: {' '.join(unity_cmd)}")
    build_app.run_unity_command(unity_cmd)


def _main():
    print(build_app.HEADER)
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
