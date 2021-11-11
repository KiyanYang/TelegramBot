#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Filename    :  text.py
@Datatime    :  2021/09/23 20:06:30
@Author      :  Kiyan Yang
@Contact     :  KiyanYang@outlook.com
@Version     :  v1.4.1
@Description :  文本相关工具: MarkdownV2 转义, 判断是否为空消息, 判断字符串列表中元素是否过长,
                短字符串列表转长字符串列表
"""
import re
from typing import Literal


class MarkdownV2:
    @staticmethod
    def sub(text: str, key: Literal[1, 2, 3] = 3) -> str:
        """MarkdownV2 特殊字符转义

        Parameters
        ----------
        text : `str`
            使用 Markdown V2 规则的字符串
        key : `Literal[1, 2, 3]`, `optional`
            转义方法, by default 3

        Returns
        -------
        str
            转义后的字符串
        """
        def dash_repl(matchobj):
            return '\\' + matchobj.group(0)

        pattern = {
            1: r'[\\]',  # 在pre和code实体内部,`自行转义
            2: r'[\)\\]',  # 内联链接定义的内部(...)部分
            3: r'([\_\*\[\]\(\)\~\`\>\#\+\-\=\|\{\}\.\!])',
        }  # 其他地方
        return re.sub(pattern[key], dash_repl, text)

    @classmethod
    def sub_auto(cls, text: str | list[str] | tuple[str]) -> (str | list[str]):
        """Markdown V2 反规则字符串的自动替换\n
        【 * _ [ ] ( ) ~ ` 】在依规则使用时, 需要使用转义符, 而普通使用时, 不需要转义符\n
        即使用时与 Markdown V2 规则相反

        Parameters
        ----------
        text : `str | list[str] | tuple[str]`
            使用 Markdown V2 反规则的字符串, 或由此类字符串组成的列表或元组

        Returns
        -------
        Union[str,list[str]]
            符合 Markdown V2 规则的字符串或由其组成的列表
        """
        def repl_2(matchobj):
            return '\\' + matchobj.group(0)

        def repl_1(matchobj):
            data_pre = {
                r'\*': 'To0g0o1',
                r'\_': 'To0g0o2',
                r'\[': 'To0g0o3',
                r'\]': 'To0g0o4',
                r'\(': 'To0g0o5',
                r'\)': 'To0g0o6',
                r'\~': 'To0g0o7',
                r'\`': 'To0g0o8',
            }
            return data_pre[matchobj.group(0)]

        def repl_3(matchobj):
            data_post = {
                'To0g0o1': '*',
                'To0g0o2': '_',
                'To0g0o3': '[',
                'To0g0o4': ']',
                'To0g0o5': '(',
                'To0g0o6': ')',
                'To0g0o7': '~',
                'To0g0o8': '`',
            }
            return data_post[matchobj.group(0)]

        escape_1 = r'\*|\_|\[|\]|\(|\)|\~|\`'.split('|')
        escape_2 = r'\_*[]()~`>#+-=|{}.!'
        escape_3 = r'To0g0o1|To0g0o2|To0g0o3|To0g0o4|To0g0o5|To0g0o6|To0g0o7|To0g0o8'.split('|')
        repl = {repl_1: escape_1, repl_2: escape_2, repl_3: escape_3}
        if isinstance(text, str):
            for i in repl:
                text = re.sub('|'.join(map(re.escape, repl[i])), i, text)
            return text
        elif isinstance(text, (list, tuple)):
            return [cls.sub_auto(x) for x in text]


class MessageText:
    @staticmethod
    def is_message_empty(text: str) -> bool:
        """
        判断是否为空消息(即不含任何可见字符的消息)

        Parameters
        ----------
        text: `str`
            消息文本

        Returns
        -------
        `bool`
            如果为空消息返回`True`, 否则返回`False`

        """
        # ASCII 编码中 0~32 和 127 是不可见（无法显示）, 33 是空格
        empty_repl = list(range(33)) + [127]
        for i in empty_repl:
            text = text.replace(chr(i), '')
        if text == '':
            return True
        else:
            return False

    @staticmethod
    def is_too_long(text: list[str], limit: int = 4000):
        """
        判断 text: `list[str]` 中各个元素是否有过长字符串(大于`limit`)

        Parameters
        ----------
        text: `list[str]`
            由字符串组成的列表

        Returns
        -------
        `Bool, [int]`
            存在过长字符串时, 返回 `True, [int]` 其中`[int]`中的元素为过长字符串的位置;
            否则返回 `False`

        """
        too_long_index = []
        for index, value in enumerate(text):
            if len(value) > limit:
                too_long_index.append(index)
        if len(too_long_index):
            return True, too_long_index
        else:
            return False

    @staticmethod
    def short2long_message(text: list[str], limit: int = 4000):
        """
        文本元素由短字符串合成小于等于`limit`的长字符串

        Parameters
        ----------
        text: `list[str]`
            短字符串作为元素的文本

        Returns
        -------
        `list[str]`
            长字符串作为元素的文本

        """
        count = 0  # 字符数
        lines = ''  # 长字符串
        new_text = []  # 新文本
        for line in text:
            count += len(line)  # 不超过 limit 时, count 正常计数
            if count > limit:
                new_text.append(lines)
                count = len(line)  # 发送之后再重新记录此次循环时的字符数
                lines = ''  # 重置长字符串
            if count <= limit:
                lines += line
        # 完成 for 循环之后一般总有一条字符串
        new_text.append(lines)
        return new_text

    @classmethod
    def split_too_long_message(cls, text: list[str], parse_mode=None, joiner=''):
        """
        将 text: `list[str]` 元素中的过长字符串按行分割为多个字符串, 并构成新 text
        注: 由于对过长字符串按行分割, 如果其无法按行分割, 那么新 text 的元素可能依然有过长字符串

        Parameters
        ----------
        text: `list[str]`
            由字符串组成的列表

        Returns
        -------
        `list[str]`
            如果 text 含有过长字符串, 则返回分割并组合后的新 text, 否则直接返回原 text

        """
        def split_markdownv2(line: str):
            """MarkdownV2 实体分割"""
            mdv2 = (
                ('*', '_', '~', '`'),
                ('__', '*_', '*~', '_~'),
                ('*__', '__~', '```'),
            )
            for i in reversed(range(3)):
                if line[:i + 1] in mdv2[i]:
                    j_len = i + 1  # 修饰符长度
                    j = line[:j_len]  # 修饰符
                    break

            line = line[j_len:-j_len]
            lines = line.splitlines(keepends=True)
            new_lines = cls.short2long_message(lines)
            new_lines = [j + i + j for i in new_lines]
            return new_lines

        itl_r = cls.is_too_long(text)
        if itl_r:  # text 含有过长字符串
            too_long_index = itl_r[1]  # 过长字符串所在位置
            new_text = []
            # 构建新 text, 如果是过长字符串则按行分割后加入, 否则直接加入
            for index, value in enumerate(text):
                if index in too_long_index:
                    # 判断是否为实体, 如果是, 则对每个分割后的字符串均加上实体
                    if parse_mode == 'MarkdownV2':
                        new_lines = split_markdownv2(value)
                    else:
                        lines = value.splitlines(keepends=True)
                        new_lines = cls.short2long_message(lines)
                    new_lines[-1] += joiner  # 在最后的元素加上 joiner
                    new_text.extend(new_lines)
                else:
                    new_text.append(value + joiner)
            return new_text
        else:  # text 不含过长字符串
            text = [i + joiner for i in text]
            return text


if __name__ == '__main__':
    pass
