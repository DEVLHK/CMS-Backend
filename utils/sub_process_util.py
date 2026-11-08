#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2024/9/16 19:34
# @Author : Ken.Lin
# @Email : kenlin@hisunglobal.com
# @File : sub_process_util.py
# @Project : hbs_flink
import subprocess
import time

from util.loging_util import logger


def execute_command(command, stop_by=None,is_shell=True, is_wait=True):
    process = subprocess.Popen(command, shell=is_shell, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    command_output = ""
    if is_wait:
        while True:
            output = process.stdout.readline().decode()
            if process.poll() is not None and output == '':
                break
            if output:
                command_output += output.strip() + "\n"
            if stop_by is not None and output.find(stop_by) != -1:
                break
        command_output = command_output.strip()
        return_code = process.returncode
    else:
        return_code, command_output=0,""
    return return_code, command_output

def kill_consumer_pid(table_name):
    # commands = " ps -ef | grep " + "'python3.*ibsver_server.py " + port + "'" + " |grep -v grep |grep -v /bin/sh"
    commands = f"ps -ef | grep 'python -u.*kafka_consumer.py {table_name}' |grep -v grep |grep -v /bin/sh"
    return_code, command_output = execute_command(commands)
    thread_info = str(command_output).split()
    if len(thread_info) > 1:
        pid = thread_info[1]
        commands = "kill -9 " + pid
        logger.info(commands)
        return_code, command_output = execute_command(commands)
        logger.info(command_output)
        return return_code,command_output
    else:
        return 0,""

def kill_source_and_sink_pid(table_name):
    # commands = " ps -ef | grep " + "'python3.*ibsver_server.py " + port + "'" + " |grep -v grep |grep -v /bin/sh"
    commands = f"ps -ef | grep 'python -u.*flink_source_and_sink.py {table_name}' |grep -v grep |grep -v /bin/sh"
    return_code, command_output = execute_command(commands)
    thread_info = str(command_output).split()
    if len(thread_info) > 1:
        pid = thread_info[1]
        commands = "kill -9 " + pid
        logger.info(commands)
        return_code, command_output = execute_command(commands)
        logger.info(command_output)
        return return_code,command_output
    else:
        return 0,""

def async_execute_func(params):
    process = subprocess.Popen(
        params,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(10)

if __name__ == '__main__':
    exit(0)
