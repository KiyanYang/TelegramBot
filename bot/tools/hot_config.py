#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Filename    :  config.py
@Datatime    :  2021/10/11 00:15:03
@Author      :  Kiyan Yang
@Contact     :  KiyanYang@outlook.com
@Version     :  v1.0
@Description :  配置文件热加载
"""
import logging
from typing import Hashable

import yaml

from .other import FileWatchDog


class LoadConfig:
    def __init__(self) -> None:
        pass

    @staticmethod
    def yaml(path: str) -> dict:
        with open(path, 'r', encoding='utf8') as f:
            config_load = yaml.safe_load(f.read())
        return config_load


class _BaseConfig:
    __values = {}
    __counts = {}

    def __init__(self, name: str, key: Hashable, path: str, hot: bool = True) -> None:
        if name not in self.__values.keys():  # 当前变量的名称不在名称库
            _BaseConfig.__values[name] = {}  # 初始化
            _BaseConfig.__counts[name] = {}  # 初始化
        if key not in self.__counts[name].keys():
            _BaseConfig.__counts[name][key] = 0
        self.name = name  # 记录当前变量的名称
        self.key = key  # 记录当前变量的 key
        self.path = path  # 记录当前变量的 path
        self.__get_config()  # 读取配置
        # 如果需要热加载, 则启动文件监测
        if hot:
            FileWatchDog(self.path, {'modified': self.__get_config})

    def __get_config(self) -> None:
        config_load = LoadConfig.yaml(self.path)  # 读取配置文件, 可更改格式
        _BaseConfig.__values[self.name][self.key] = config_load
        if self.__counts[self.name][self.key] > 0:
            count = self.__counts[self.name][self.key]
            logging.info(f'{self.path} 重新加载完毕：第{count}次重新加载。')
        else:
            print(f'{self.path} 首次加载完毕。')
        _BaseConfig.__counts[self.name][self.key] += 1

    @classmethod  # 使用类方法可以直接外部访问
    def get(cls, name: str) -> dict:
        return cls.__values[name]


class Configs:
    def __init__(self, key_path: dict[Hashable, str], hot: bool = False) -> None:
        __id = str(id(self))
        for key, path in key_path.items():
            _BaseConfig(__id, key, path, hot)
        self.__item = _BaseConfig.get(__id)

    def __getitem__(self, key):
        return self.__item[key]


if __name__ == '__main__':
    pass
