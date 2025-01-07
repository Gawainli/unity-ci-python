import subprocess
from logger import logger
import cpy_tool

def test_subprocess():
    # 执行外部命令
    cmd = ['ping', 'www.baidu.com']
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               text=True, universal_newlines=True)

    for line in iter(process.stdout.readline, ''):
        logger.info(line.strip())
    process.stdout.close()

    # 等待命令执行完成
    process.wait()


def test_copy_files():
    cpy_tool.copy_director_with_info(r'E:\cwcx\bundles\Android\DefaultPackage\1.0.0-24-12-30-155419', r'E:\cwcx\bundles\test_copy')


if __name__ == "__main__":
    test_copy_files()
