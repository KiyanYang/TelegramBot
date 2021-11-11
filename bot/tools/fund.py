#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Filename    :  fund.py
@Datatime    :  2021/09/23 20:11:40
@Author      :  Kiyan Yang
@Contact     :  KiyanYang@outlook.com
@Version     :  v1.1
@Description :  基金相关工具
"""
import json

import requests


class Fund:
    # 基金信息表头
    FUNDINFO_HEADER = [
        '基金代码', '基金名称', '盘中估值', '估值涨幅', '最新净值', '净值日期', '累计净值', '日增长率', '上期净值', '净值时间'
    ]

    @staticmethod
    def get_fund_info_1(code: str, type_dict: bool = False):
        """获取基金信息 1

        ['基金代码', '基金名称', '盘中估值', '估值涨幅', '最新净值', '净值日期', '累计净值', '日增长率', '上期净值', '净值时间']

        Parameters
        ----------
        code : str
            基金代码
        type_dict : bool, optional
            是否以 dict 类型返回, by default False

        Returns
        -------
        list | dict
            基金信息
        """
        url = 'https://fund.eastmoney.com/Data/FundCompare_Interface.aspx?bzdm='
        url_json = requests.get(url + str(code))
        url_text = url_json.text[17:-3]
        url_list = url_text.split(',')
        fund_info = url_list[0:2] + url_list[4:12]
        fund_info[3] += '%'
        fund_info[7] += '%'
        if type_dict:
            fund_info_dict = {fund_info[0]: fund_info[1:]}
            return fund_info_dict  # 返回dict类型的基金信息 {code: ...}
        else:
            return fund_info  # 返回list类型的基金信息 [code, ...]

    @staticmethod
    def get_fund_info_2(code: str):
        """获取基金信息 2

        ['基金代码', '基金名称', '净值日期', '单位净值', '净值估算', '估值涨幅', '估值日期']
        ['001618', '天弘...', '2021-10-13', '1.4784', '1.4777', '-0.05%', '2021-10-14 15:00']

        Parameters
        ----------
        code : str
            基金代码

        Returns
        -------
        list
            基金信息
        """
        url = f'http://fundgz.1234567.com.cn/js/{code}.js'
        result = requests.get(url)
        fund_info_dict = json.loads(result.text[8:-2])
        fund_info_keys = ['fundcode', 'name', 'jzrq', 'dwjz', 'gsz', 'gszzl', 'gztime']
        fund_info = []
        for i in fund_info_keys:
            fund_info.append(fund_info_dict[i])
        fund_info[5] += '%'
        return fund_info

    # 今日操作，以2维list返回[[基金代码,今日操作,估值涨幅],]
    @classmethod
    def get_fund_working(cls, code_jz_fe_w):
        ...

    # 估计收益，以2维list返回[[基金代码+标志,收益,基金名称],...,['Income', 总计收益, '']]
    @classmethod
    def get_fund_income(cls, code_fe: dict):
        ...


if __name__ == '__main__':
    pass
