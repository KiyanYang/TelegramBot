#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Filename    :  other.py
@Datatime    :  2021/11/09 19:27:10
@Author      :  Kiyan Yang
@Contact     :  KiyanYang@outlook.com
@Version     :  v1.1
@Description :  其他工具: 监控文件，日志
"""
import logging
import os
import threading
import time
from datetime import datetime, timedelta, timezone


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)


# 后续从此方式得到的 logger 都采用上述基本配置
def get_logger(name: str | None = None):
    return logging.getLogger(name)


class FileWatchDog:
    def __init__(self, path: str, handler_func: dict) -> None:
        self.path = path
        self.modified_time = os.stat(path).st_mtime  # 文件修改时间
        self.handler_func = handler_func  # 用户传入的函数
        handlers = {'modified': self.__modified}
        for handler in handler_func.keys():
            t = threading.Thread(target=handlers[handler], name=handler, daemon=True)
            t.start()

    def __modified(self):
        while True:
            time.sleep(0.5)
            mtime = os.stat(self.path).st_mtime
            if self.modified_time < mtime:
                self.modified_time = mtime
                self.handler_func['modified']()


# 返回当前时间
def datetime_now(hours=8, f=None):
    tz = timezone(timedelta(hours=hours))
    dtn = datetime.now(tz)
    match f:
        case 'd':
            return dtn.strftime('%Y-%m-%d')  # year-month-day 字符串
        case 'S':
            return dtn.strftime('%H:%M:%S')  # hour-minute-second 字符串
        case 'dS':
            return dtn.strftime('%Y-%m-%d %H:%M:%S')  # 格式化输出，保留到秒，不显示时区
        case 'dSf':
            return dtn.strftime('%Y-%m-%d %H:%M:%S.%f')  # 格式化输出，保留到微秒，不显示时区
        case _:
            return dtn  # datetime.datetime 实例
