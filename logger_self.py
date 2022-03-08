import logging  # 引入logging模块
import os.path
import time

# 创建一个logger
logger = logging.getLogger()
# Log等级总开关
logger.setLevel(logging.INFO)

# 创建一个handler，用于写入日志文件
# sj = time.strftime('%Y%m%d %H:%M:%S', time.localtime(time.time()))
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log")
if not os.path.exists(log_path):
    os.makedirs(log_path)
logfile = os.path.join(log_path, 'run_tests_log.txt')

fh = logging.FileHandler(logfile, mode='a')
# 第三步，定义handler的输出格式
formatter = logging.Formatter("[%(asctime)s][%(filename)s][line:%(lineno)d]-%(levelname)s: %(message)s")
fh.setFormatter(formatter)
# 第四步，将logger添加到handler里面
logger.addHandler(fh)

# 日志打印到控制台
console = logging.StreamHandler() # 输出到控制台的handler
formatter_console = logging.Formatter("[%(filename)s][line:%(lineno)d]: %(message)s")
console.setFormatter(formatter_console)
console.setLevel('INFO')
logger.addHandler(console)
