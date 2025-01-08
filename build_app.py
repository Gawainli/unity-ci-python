"""提供unity自动出包功能"""

import os
import sys
from pathlib import Path
from logger import logger
import build_tool
import build_env_tool
import post_build


def _build_app_and_run_unity_command():

    BUILD_TARGET = os.environ["BUILD_TARGET"]
    PROJ_DIR = Path(os.environ["PROJ_DIR"])
    UNITY_EXECUTABLE = os.environ.get(
        "UNITY_EXECUTABLE",
        'xvfb-run --auto-servernum --server-args="-screen 0 640x480x24" unity-editor',
    )
    BUILD_NAME = os.environ["BUILD_NAME"]

    logger.info(f"Building for {BUILD_TARGET}")

    BUILD_PATH = Path(os.environ["BUILD_OUTPUT"]) / "build" / BUILD_TARGET
    BUILD_PATH.mkdir(parents=True, exist_ok=True)
    BUILD_TIME = os.environ["BUILD_TIME"]

    build_name = f"{BUILD_NAME}_{BUILD_TIME}"
    os.environ["APK_PATH"] = BUILD_PATH/f"{build_name}.apk"

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
        "-customBuildName",
        build_name,
        "-customBuildPath",
        str(BUILD_PATH),
        "-executeMethod",
        "BuildCommand.PerformBuild",
        # '-logFile', str(BUILD_LOG_PATH.absolute())
        # '-logFile -'
    ]

    cmd_str = " ".join(unity_cmd)
    logger.info(f"Running Unity with command: {cmd_str}")
    build_tool.run_unity_command(cmd_str)
    # 列出构建路径中的文件
    logger.info("Contents of build path:")
    if BUILD_PATH.exists():
        for item in BUILD_PATH.iterdir():
            logger.info(item)
    else:
        logger.warning(f"Build path {BUILD_PATH} does not exist.")

    # 检查构建文件夹是否为空
    if not any(BUILD_PATH.iterdir()):
        logger.error("Build folder is empty, failing job.")
        sys.exit(1)


def build_app():
    """读取配置文件，构建Unity应用

    Args:
        file_path (string): 配置文件路径
    """
    # 确保所有使用的环境变量都已定义
    required_env_vars = [
        "BUILD_TARGET",
        "PROJ_DIR",
        "BUILD_OUTPUT",
        "UNITY_EXECUTABLE",
        "BUILD_NAME",
        "BUILD_TIME",
    ]
    if build_env_tool.check_environ(required_env_vars) is not True:
        sys.exit(1)
    _build_app_and_run_unity_command()


def _main():
    logger.info(build_tool.HEADER)
    build_tool.setup_build_time()
    logger.add(
        f"logs/app/build-app-{os.environ['BUILD_TIME']}.log",
        backtrace=True,
        diagnose=True,
        enqueue=True,
    )
    build_env_tool.load_config_from_args()
    build_app()
    post_build.post_build_app()


if __name__ == "__main__":
    _main()
