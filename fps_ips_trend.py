import math
import re
import matplotlib.pyplot as plt
plt.switch_backend("agg")
from logger_self import logger

def trend(file_name):
    fps_li = []
    ips_li = []
    logger.info("file_name: {}".format(file_name) )
    try:
        lines = 0
        with open(file_name, "r", encoding="utf-8") as fp1:
            # 2021-09-03 16:32:09.920 [Info] FPS:109.45, IPS:214

            for line in fp1:
                res = re.findall("FPS:(\d{3,}).*IPS:(\d{3,})", line)
                if res:
                    fps, ips = res[0]
                    fps_li.append(int(fps))
                    ips_li.append(int(ips))
                    lines += 1
                if lines >= 30000:  # 48次大概再18000行
                    break
        # 一共60个X坐标 每个坐标的分钟数 （每分钟输出59次 除以59 是总分钟数）
        x_num= 30
        one_minites = int( lines /59 / x_num) # 24小时大概每个点 24分钟

        max_ps = max(max(fps_li), max(ips_li))
        # y轴取整方便画图
        max_ps = math.ceil((max_ps / 500) + 1) * 500
        # X轴
        length = len(fps_li)
        x = [i for i in range(length)]

        plt.figure(figsize=(x_num, 10), dpi=100)

        plt.plot(x, fps_li, color='c', linestyle='-', label="FPS")
        plt.plot(x, ips_li, color='m', linestyle='-.', label="IPS")
        # 刻度显示
        x_ticks_label = ["{}m".format(i * one_minites) for i in range(x_num+1)]
        min_num= min(len(x[::one_minites * 59]), len(x_ticks_label))
        plt.xticks(x[::one_minites * 59][0:min_num], x_ticks_label[::1][0:min_num])

        #  添加图例
        plt.legend(loc="best")
        # 添加刻度
        y_ticks = range(max_ps)
        plt.yticks(y_ticks[::500])

        #  添加网格显示
        plt.grid(True, linestyle='--', alpha=0.5)
        # X,Y 轴的描述信息
        plt.ylabel("Frame rate")
        plt.xlabel("time(minutes)")
        # title
        plt.title("The trend of FPS and IPS over time", fontsize=20)
        png = file_name + ".png"
        plt.savefig(png)
    except Exception as e:
        logger.info(e)

if __name__ == '__main__':
    file_name = "DemoStatistic_4816.log"
    trend(file_name)

    # file_name = "DemoStatic_second.txt"
    # trend(file_name)