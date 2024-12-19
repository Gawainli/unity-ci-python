"""提供unity自动出包功能"""
import os
import subprocess
import sys
from pathlib import Path
import configparser
import argparse
from datetime import datetime
from logger import logger


def _resolve_path(value):
    """解析路径，如果路径不存在则返回原始值。"""
    try:
        return str(Path(value).resolve())
    except FileNotFoundError:
        logger.warning(f"Path {value} does not exist, using original value.")
        return str(Path(value))


def _read_app_cfg_and_set_env(file_path):
    logger.info(f"Read build cofnig:{file_path}")
    cfg = configparser.ConfigParser()
    cfg.read(file_path)

    for section in cfg.sections():
        for key, value in cfg.items(section):
            env_key = key.upper()
            v = value
            if value is not None and value.strip() != '':
                # 处理Proj路径
                if env_key == 'PROJ_DIR':
                    v = _resolve_path(value)
                os.environ[env_key] = str(v)
                logger.info("Build set env %s:%s", env_key, v)


def check_environ(env_vars):
    """检查需要用到环境变量有没有被正确设置

    Args:
        env_vars (string[]): 环境变量名数组 

    Returns:
        bool: 都正确设置返回true否则返回false
    """
    for var in env_vars:
        if var not in os.environ:
            logger.error(f"Error: Environment variable {var} is not set.")
            return False
    return True


def _build_app_and_run_unity_command():
    # 确保所有使用的环境变量都已定义
    required_env_vars = ['BUILD_TARGET', 'PROJ_DIR',
                         'UNITY_EXECUTABLE', 'BUILD_NAME']
    if check_environ(required_env_vars) is not True:
        sys.exit(1)

    BUILD_TARGET = os.environ['BUILD_TARGET']
    PROJ_DIR = Path(os.environ['PROJ_DIR'])
    UNITY_EXECUTABLE = os.environ.get(
        'UNITY_EXECUTABLE', 'xvfb-run --auto-servernum --server-args="-screen 0 640x480x24" unity-editor')
    BUILD_NAME = os.environ['BUILD_NAME']

    logger.info(f"Building for {BUILD_TARGET}")

    BUILD_PATH = PROJ_DIR / 'Builds' / BUILD_TARGET
    BUILD_PATH.mkdir(parents=True, exist_ok=True)

    current_date = datetime.now().strftime('%m-%d-%H-%M')
    logfile = f'logs/build_log_{current_date}.log'
    BUILD_LOG_PATH = BUILD_PATH / logfile

    build_name = f'{BUILD_NAME}_{current_date}'

    # 构建 Unity 命令
    unity_cmd = [
        *UNITY_EXECUTABLE.split(),  # 解析可能包含空格的命令
        '-projectPath', str(PROJ_DIR),
        '-quit',
        '-batchmode',
        '-nographics',
        '-buildTarget', BUILD_TARGET,
        '-customBuildTarget', BUILD_TARGET,
        '-customBuildName', build_name,
        '-customBuildPath', str(BUILD_PATH.absolute()),
        '-executeMethod', 'BuildCommand.PerformBuild',
        '-logFile', str(BUILD_LOG_PATH.absolute())
    ]

    logger.info(f"Running Unity with command: {' '.join(unity_cmd)}")
    run_unity_command(unity_cmd)
    # 列出构建路径中的文件
    logger.info("\nContents of build path:")
    if BUILD_PATH.exists():
        for item in BUILD_PATH.iterdir():
            logger.info(item)
    else:
        logger.warning(f"Build path {BUILD_PATH} does not exist.")

    # 检查构建文件夹是否为空
    if not any(BUILD_PATH.iterdir()):
        logger.error("Build folder is empty, failing job.")
        sys.exit(1)


def run_unity_command(cmd):
    """运行unity命令行
    Args:
        cmd (string[]): 命令行数组
    """
    try:
        # 执行 Unity 构建命令
        result = subprocess.run(
            cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        UNITY_EXIT_CODE = result.returncode

        # 处理不同的退出码
        if UNITY_EXIT_CODE == 0:
            logger.info("Run succeeded, no failures occurred")
        elif UNITY_EXIT_CODE == 2:
            logger.error("Run succeeded, some tests failed")
        elif UNITY_EXIT_CODE == 3:
            logger.error("Run failure (other failure)")
        else:
            logger.error(f"Unexpected exit code {UNITY_EXIT_CODE}")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)


HEADER = r"""
                            )                             
   (    (  (        (    ( /(     (             (   (     
   )\   )\))(   '   )\   )\())  ( )\    (   (   )\  )\ )  
 (((_) ((_)()\ )  (((_) ((_)\   )((_)  ))\  )\ ((_)(()/(  
 )\___ _(())\_)() )\___ __((_) ((_)_  /((_)((_) _   ((_)) 
((/ __|\ \((_)/ /((/ __|\ \/ /  | _ )(_))(  (_)| |  _| |  
 | (__  \ \/\/ /  | (__  >  <   | _ \| || | | || |/ _` |  
  \___|  \_/\_/    \___|/_/\_\  |___/ \_,_| |_||_|\__,_| 
"""


def build_app():
    """从命令行读取出包配置文件路径，启动unity命令行出包"""
    print(HEADER)
    parser = argparse.ArgumentParser(description="Unity build tool")
    parser.add_argument('cfg_path', type=str, help='build config ini file')
    args = parser.parse_args()
    if not os.path.isfile(args.cfg_path):
        logger.info(f"Error: The file {args.cfg_path} does not exist.")
        return

    _read_app_cfg_and_set_env(args.cfg_path)
    _build_app_and_run_unity_command()


if __name__ == "__main__":
    build_app()
