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
import os

from .tools import Configs, GitHubAPIv4

LOCAL = os.environ.get('LOCAL', False) == 'True'
file_path = {0: 'bot/configs/config.yaml', 1: 'bot/configs/languages.yaml'}

# 对本地环境开启热加载
if LOCAL:
    CFG = Configs(file_path, hot=True)
    GITHUB = GitHubAPIv4(os.environ['TOKEN_GITHUB'], proxy=CFG[0]['PROXY_URL'])
else:
    CFG = Configs(file_path, hot=False)
    GITHUB = GitHubAPIv4(os.environ['TOKEN_GITHUB'])

if __name__ == '__main__':
    pass
