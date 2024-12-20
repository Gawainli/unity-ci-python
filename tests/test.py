import subprocess
from logger import logger

# 执行外部命令
cmd = ['ping', 'www.baidu.com']
process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                     text=True, universal_newlines=True)

for line in iter(process.stdout.readline, ''):
    logger.info(line.strip())
process.stdout.close()

# 等待命令执行完成
process.wait()
