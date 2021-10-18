#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Filename    :  exception.py
@Datatime    :  2021/09/27 14:00:41
@Author      :  Kiyan Yang
@Contact     :  KiyanYang@outlook.com
@Version     :  v1.0
@Description :  自定义错误异常
"""


class MessageError(Exception):
    '''当发送消息出错时, 抛出此异常'''

    # 自定义异常类型的初始化
    def __init__(self, value, location):
        self.value = value
        self.location = location

    # 返回异常类对象的说明信息
    def __str__(self):
        return (f"{repr(self.value)} 为错误消息\n错误位于 '{self.location}'")


class GetUrlError(Exception):
    '''当从链接获取数据出错时, 抛出此异常'''

    # 自定义异常类型的初始化
    def __init__(self, value, location):
        self.value = value
        self.location = location

    # 返回异常类对象的说明信息
    def __str__(self):
        return (f"从 {repr(self.value)} 获取数据出错\n错误位于 '{self.location}'")


if __name__ == '__main__':
    pass
