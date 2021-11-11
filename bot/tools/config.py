#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Filename    :  config.py
@Datatime    :  2021/10/11 00:15:03
@Author      :  Kiyan Yang
@Contact     :  KiyanYang@outlook.com
@Version     :  v1.1
@Description :  配置文件热加载
"""
from io import StringIO
from pathlib import Path
from typing import Any, Callable, Hashable

from ruamel.yaml import YAML

from .other import FileWatchDog, get_logger

logger = get_logger(__name__)


class ConfigManager:
    def __init__(self) -> None:
        self.__yaml = YAML()
        self.__yaml.default_flow_style = False
        self.__yaml.preserve_quotes = True
        self.__yaml.indent(mapping=2, sequence=4, offset=2)
        self.__yaml.default_style

    @property
    def yaml(self) -> YAML:
        return self.__yaml

    def __yaml_loads(self, mode: Callable, path: str = None, text: str = None) -> Any:
        if path is not None:
            return mode(stream=Path(path))
        elif text is not None:
            return mode(stream=text)
        else:
            raise TypeError("需要 'path' 或 'text' 参数")

    def yaml_load(self, path: str = None, text: str = None) -> Any:
        return self.__yaml_loads(self.__yaml.load, path, text)

    def yaml_load_all(self, path: str = None, text: str = None) -> Any:
        return self.__yaml_loads(self.__yaml.load_all, path, text)

    def __yaml_dumps(self, mode: Callable, data: Any, path: str = None) -> Any:
        if path is None:
            stream = StringIO()
            mode(data, stream=stream)
            return stream.getvalue()
        else:
            with Path(path).open('w', encoding='UTF-8') as f:
                return mode(data, stream=f)

    def yaml_dump(self, data: Any, path: str = None) -> Any:
        return self.__yaml_dumps(self.__yaml.dump, data, path)

    def yaml_dump_all(self, data: Any, path: str = None) -> Any:
        return self.__yaml_dumps(self.__yaml.dump_all, data, path)


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
        config_load = ConfigManager().yaml_load(path=self.path)  # 读取配置文件, 可更改格式
        _BaseConfig.__values[self.name][self.key] = config_load
        if self.__counts[self.name][self.key] > 0:
            count = self.__counts[self.name][self.key]
            logger.info(f'{self.path} 重新加载完毕：第{count}次重新加载')
        else:
            logger.info(f'{self.path} 首次加载完毕')
        _BaseConfig.__counts[self.name][self.key] += 1

    # TODO @property 使用此装饰器进行访问更改
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
