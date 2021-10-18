#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Filename    :  fund.py
@Datatime    :  2021/09/23 20:11:40
@Author      :  Kiyan Yang
@Contact     :  KiyanYang@outlook.com
@Version     :  v1.0
@Description :  基金相关工具
"""
import requests

import json


class Fund:
    # 基金信息表头
    FUNDINFO_HEADER = [
        '基金代码', '基金名称', '盘中估值', '估值涨幅', '最新净值', '净值日期', '累计净值', '日增长率', '上期净值', '净值时间'
    ]

    # 获取基金信息
    @staticmethod
    def get_fund_info(fundcode: str, type_dict: bool = False):
        url = 'https://fund.eastmoney.com/Data/FundCompare_Interface.aspx?bzdm='
        url_json = requests.get(url + str(fundcode))
        url_text = url_json.text[17:-3]
        url_list = url_text.split(',')
        fund_info = url_list[0:2] + url_list[4:12]
        fund_info[3] += '%'
        fund_info[7] += '%'
        if type_dict:
            fund_info_dict = {fund_info[0]: fund_info[1:]}
            return fund_info_dict  # 返回dict类型的基金信息{code: ...}
        else:
            return fund_info  # 返回list类型的基金信息

    # 今日操作，以2维list返回[[基金代码,今日操作,估值涨幅],]
    @staticmethod
    def get_fund_working(fundcode_jz_fene_w_jzgs_gzzf):
        # 今日操作前处理，返回需要比较的位置
        def get_fe_jz_higher(fe, jz=1.0, jzgs=1.0, w=1):
            # fe:份额; jz:净值; jzgs:净值估算; w:权重; wglist:网格表
            # a:份额的末位，范围0~7
            fe = fe + [0.00]
            a = fe.index(0.00)
            # b:净值的末位，范围0~8
            rate = jzgs / jz
            wglist = [0.04, 0.00, -0.04, -0.08, -0.12, -0.16, -0.20, -0.24]
            wglist = [1 + w * x for x in wglist]
            wglist.append(rate)
            wglist.sort(reverse=True)
            b = wglist.index(rate)
            return a, b

        working = []
        # 金额 1.00,0.96,0.92,0.88,0.84,0.80,0.76
        je = [100, 110, 120, 260, 140, 150, 320]
        for x in fundcode_jz_fene_w_jzgs_gzzf:
            code, jz, fe, w, jzgs, gzzf = x[0], x[1], x[2:-3], x[-3], float(x[-2]), x[-1]
            # a = 0..7, b = 0..8 , 以1.04..0.04..0.72共9个格子计算
            a, b = get_fe_jz_higher(fe, jz, jzgs, w)
            if a > b:
                value = sum(fe[b:a])  # 应卖份额之和
                working.append([code, 'S ' + str(value), gzzf])
            elif a < b - 1:
                value = sum(je[a:b - 1])  # 应买金额之和
                working.append([code, 'B ' + str(value), gzzf])
            else:
                working.append([code, 'N', gzzf])
        return working  # [[代码, 操作, 涨跌幅]]

    # ['基金代码', '基金名称', '净值日期', '单位净值', '净值估算', '估值涨幅', '估值日期']
    # ['001618', '天弘ETF', '2021-10-13', '1.4784', '1.4777', '-0.05%', '2021-10-14 15:00']
    @staticmethod
    def get_fund_info_(code: str):
        url = f'http://fundgz.1234567.com.cn/js/{code}.js'
        result = requests.get(url)
        fund_info_dict = json.loads(result.text[8:-2])
        fund_info_keys = ['fundcode', 'name', 'jzrq', 'dwjz', 'gsz', 'gszzl', 'gztime']
        fund_info = []
        for i in fund_info_keys:
            fund_info.append(fund_info_dict[i])
        fund_info[5] += '%'
        return fund_info


if __name__ == '__main__':
    pass
