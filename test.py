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
    cpy_tool.move_all_files_and_dirs(
        "E:/cwcx/250/ch_auto/android", "E:/cwcx/250/ch_auto/test_copy")
    cpy_tool.move_all_files_and_dirs(
        "E:/cwcx/250/ch_auto/ios", "E:/cwcx/250/ch_auto/test_copy")


if __name__ == "__main__":
    test_copy_files()
