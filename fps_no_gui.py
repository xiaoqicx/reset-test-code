import csv
import os
import re
import time
import glob
import argparse

from read_last_n_lines import get_last_n_lines


class GetData(object):
    def __init__(self, f_path):
        self.file_path = f_path
        # self.channel_num = ch_num
        self.per_file = []
        # 每个流上次的fps数据
        self.old_per_list = []
        # 记录重复的次数 按index记录，连续两次不同就清0，连续相同每次+1
        self.same_time_num = 0

    def read_per_last(self):
        try:
            # glob.glob 全局正则文件查找， 返回文件路径名的list
            self.per_file = glob.glob(os.path.join(self.file_path, "DemoStatistic*.log"))
            is_e = len(self.per_file) == 0
            # 重复5次寻找这个文件， 没找到就报异常。
            loops = 5
            while is_e:
                print("Find file for {} time".format(6-loops))
                time.sleep(6)
                self.per_file = glob.glob(os.path.join(self.file_path, "DemoStatistic*.log"))
                is_e = len(self.per_file) == 0
                loops -= 1
                if loops == 0:
                    return None
            # 假设8个流+1行统计 共9行 读取17行 有且只有一个完整行
            reader_list = get_last_n_lines(self.per_file[-1], 10)
        except Exception as ex:
            print(str(ex))

        return reader_list

    def get_cur_per(self):
        last_per_list = self.read_per_last()
        # 去除没有FPS和IPS的行
        last_per_list = [l for l in last_per_list if "IPS" in l and "FPS" in l]
        if last_per_list == self.old_per_list:
            self.same_time_num += 1
            if self.same_time_num >= 4:
                print("streams have output the same FPS for 4 times, maybe hang!!!")
                return 0, 0
        else:
            self.same_time_num = 0
        self.old_per_list = last_per_list
        line = last_per_list[-1]
        res = re.findall("FPS:(\d+).*IPS:(\d+)", line)
        if res:
            FPS, IPS = res[0]
            print("stream fps: {}; total infer ifs: {}" .format(FPS, IPS))
            return FPS, IPS
        else:
            print("streams  error")
            return 0, 0



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", "-p", default="/home/hddl/kmb_nvr_build/streaming_mode/host_install_dir/kmb_ia_sample", help='The path of the csv file; Default - "."')
    args = parser.parse_args()
    # file_path = args.path
    file_path = r"C:\kmb_setup\letcode\yilin"
    get_data = GetData(file_path)

    print(get_data.get_cur_per())
    print(get_data.get_cur_per())
    print(get_data.get_cur_per())
    print(get_data.get_cur_per())
    print(get_data.get_cur_per())




