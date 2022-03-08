import os
import threading
import time
import subprocess
from fps_ips_trend import trend
from fps_no_gui import GetData
from logger_self import logger

# 配置项
vpu_path = "/opt/intel/vpu_accelerator_samples"
config_json = "s240_avc_group.json"
demo = "demo-reset"

scriptdir = os.path.dirname(os.path.abspath(__file__))
time_stamp = time.strftime('%Y-%m-%d.%H_%M_%S')
log_path = "{}/log/{}".format(scriptdir, time_stamp)
demo_log_path =  "{}/demo_logs".format(log_path)

# 命令
cmd_start = "sudo modprobe i2c-i801; sudo modprobe mxlk; sudo modprobe xlink; sudo modprobe intel_tsens_host; " \
            "sudo modprobe hddl_device_server; sleep 10; sudo systemctl enable pms-daemon"
dmesg = "dmesg -wH > {}/dmesg.log &".format(log_path)
journalctl = "journalctl -fu pms-daemon > {}/pms_daemon_robin_reset.log &".format(log_path)
restart_pms= "sudo systemctl restart pms-daemon;"


hddl_service = "rm -rf {0}/bypass/demoUI/*.log; cd {0}/hddlunite; source env_host.sh; ./bin/hddl_scheduler_service" \
               " | tee {1}/hddl_device_service.log".format(vpu_path, log_path)

set_mode = " cd {0}/hddlunite; source env_host.sh; ./bin/SetHDDLMode -m b >> {1}/hddl_device_service.log;" \
           "sleep 10; ./add_group.sh".format(vpu_path, log_path)
fullpipe = "cd {}/bypass/demoUI; ulimit -n 65535; source ./prepare_demo_no_gui.sh; ./{} -c ./{}".\
           format(vpu_path, demo, config_json)
reset = "bash ./reset_device.sh {}".format(log_path)
cpu_info = "bash ./trace_cpu.sh {}".format(log_path)


def mkdir_folder():
    # 创建本次日志目录，以时间戳命名
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    if not os.path.exists(demo_log_path):
        os.makedirs(demo_log_path)

def run(cmd):
    return os.system(cmd)


def pipe_run(cmd):
    return subprocess.Popen(cmd, shell=True, executable="/bin/bash")


def e2e_test():

    mkdir_folder()
    logger.info(cmd_start)
    logger.info(dmesg)
    logger.info(journalctl)
    logger.info(restart_pms)
    run(cmd_start)
    time.sleep(5)
    run(dmesg)
    time.sleep(5)
    run(journalctl)
    time.sleep(5)
    run(restart_pms)

    thread_hddl_service = threading.Thread(target=pipe_run, args=(hddl_service,))
    thread_set_mode = threading.Thread(target=pipe_run, args=(set_mode,))
    thread_fullpipe = threading.Thread(target=pipe_run, args=(fullpipe,))
    thread_cpu_info = threading.Thread(target=pipe_run, args=(cpu_info,))

    loops = 0
    streams_started = False

    logger.info(hddl_service)
    logger.info("thread_hddl_service start")
    thread_hddl_service.start()
    time.sleep(20)

    logger.info(set_mode)
    logger.info("set mode cmd start")
    thread_set_mode.start()
    time.sleep(65)

    logger.info(fullpipe)
    logger.info("fullpipe start")
    thread_fullpipe.start()
    time.sleep(90)

    while True:
        state, reslut = subprocess.getstatusoutput("ls {}/bypass/demoUI/Demo_*.log | wc -l".format(vpu_path))
        try:
            if int(reslut) >= 24:
                streams_started = True
                logger.info("fullpipe start success")
                break
        except Exception as ex:
            logger.info(str(ex))
        loops += 1
        time.sleep(6)
        if loops >= 10:
            logger.info("wait streams be ready exceeded times!!!")
            break
        logger.info("wait streams be ready loop {} times!!!".format(loops))

    fps_counter = GetData("{}/bypass/demoUI".format(vpu_path))

    if streams_started:
        try:
            FPS, IPS = fps_counter.get_cur_per()
            if int(FPS) >= 6600:
                logger.info("FPS is: {}, IPS is: {}".format(FPS, IPS))
                logger.info("PFS 已经运行正常\n")
            else:
                # 如果FPS不达标就重启
                logger.info("reboot and test again\n")
                run("sudo reboot")
        except Exception as ex:
            # 没有获取到 FPS
            logger.info(str(ex))
            logger.info("Failed to get FPS!")
    logger.info("cpu info start:{}".format(cpu_info))
    thread_cpu_info.start()
    time.sleep(5)
    logger.info("reset test start:{}".format(reset))
    run(reset)
    time.sleep(60)
    logger.info("reset test end")
    # # 画图 + 收集日志
    collect_log()
    logger.info("sleep 10s and then reboot...!!!")
    run("mv {}/log/run_tests_log.txt {}".format(scriptdir, log_path))
    time.sleep(10)
    run("sudo reboot")

def collect_log():
    save_demo_log="cp {}/bypass/demoUI/Demo_*.log  {}".format(vpu_path, demo_log_path)
    file_name = "{}/DemoStatistic.log".format(log_path)
    save_demoStatistic_log = "cp {}/bypass/demoUI/DemoStatistic_*.log  {}".format(vpu_path, file_name)

    logger.info(save_demo_log)
    logger.info(save_demoStatistic_log)
    run(save_demo_log)
    run(save_demoStatistic_log)
    time.sleep(5)
    # 画图
    logger.info("画趋势图")
    trend(file_name)



if __name__ == '__main__':
    e2e_test()