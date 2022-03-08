import os


def get_last_n_lines(logfile, n):
    '''
    :param logfile: 文件的路径名
    :param n: 读取的行数
    :return: n行文件字符串的list
    '''
    n=int(n)
    # 设置一次读取的大小
    blk_size_max = 1024
    n_lines = []
    with open(logfile, 'rb') as fp:
        # 偏移到文件尾，前提是二进制打开
        fp.seek(0, os.SEEK_END)
        # 当前的指针位置
        cur_pos = fp.tell()
        # 当前指针大于0 & 读取的行数小于n 的时候，继续读取文件
        while cur_pos > 0 and len(n_lines) < n:
            blk_size = min(blk_size_max, cur_pos)
            # os.SEEK_SET=0 指文件头位置(如果文件不够， 偏移到文件头)
            fp.seek(cur_pos - blk_size, os.SEEK_SET)
            blk_data = fp.read(blk_size)
            # len(blk_data) 必须等于 blk_size，否则代表文件读取出了问题
            assert len(blk_data) == blk_size
            lines = blk_data.split(b'\n')

            # 因为是按固定size 读取，第一行不一定完整，要剔除第一行
            if len(lines) > 1 and len(lines[0]) > 0:
                n_lines[0:0] = lines[1:]
                cur_pos -= (blk_size - len(lines[0]))
            else:
                # <==> n_lines = lines + n_lines
                n_lines[0:0] = lines
                cur_pos -= blk_size

            fp.seek(cur_pos, os.SEEK_SET)

    # 删除没有意义的空行
    n_lines = [line for line in n_lines if line]
    # if len(n_lines) > 0 and len(n_lines[-1]) == 0:
    #     del n_lines[-1]

    # 按行解码为字符
    n_lines = [ss.decode() for ss in n_lines]
    return n_lines[-n:]



if __name__ == '__main__':
    lines = get_last_n_lines(r"C:\work\test_scripts\Validation_fps.txt", 25)
    for line in lines:
        print(line)


