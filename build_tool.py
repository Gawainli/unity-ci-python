import os
import subprocess
import time
import sys
from logger import logger

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

def setup_build_time():
    """
    Sets up the build time environment variable.

    This function sets the '_build_time' environment variable to the current time
    formatted as 'yy-mm-dd-HHMMSS'.
    """
    os.environ['BUILD_TIME'] = time.strftime('%y-%m-%d-%H%M%S')


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


def run_unity_command(cmd):
    """运行unity命令行
    Args:
        cmd (string[]): 命令行数组
    """
    start_time = time.time()
    try:
        # 执行 Unity 构建命令
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=True,
            encoding='utf-8',
            universal_newlines=True  # 确保输出为文本格式
        )

        # 实时读取并打印标准输出和标准错误
        for line in iter(process.stdout.readline, ''):
            logger.info(line.strip())

        process.stdout.close()
        process.wait()

        # 计算运行时间
        elapsed_time = time.time() - start_time
        logger.info(f"Command completed in {elapsed_time:.2f} seconds")

        UNITY_EXIT_CODE = process.returncode

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
