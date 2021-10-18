#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Filename    :  bot.py
@Datatime    :  2021/09/23 20:10:01
@Author      :  Kiyan Yang
@Contact     :  KiyanYang@outlook.com
@Version     :  v1.2
@Description :  自定义 bot 相关工具: 获取配置, 发送文本, 发送超长文本
"""
import os

from telegram import Bot, Message
from telegram.error import BadRequest
from telegram.utils.request import Request

from .config import CFG, LOCAL
from .tools import MessageError, MessageText


class MyBot(Bot):
    def __init__(self, token: str) -> None:
        if LOCAL:
            super().__init__(token, request=Request(proxy_url=CFG[0]['PROXY_URL']))
        else:
            super().__init__(token)

    def send_too_long_message(
        self,
        chat_id: str | int,
        text: list[str],
        joiner: str = '\n',
        parse_mode: str = None,
    ) -> Message:
        """
        过长消息转多条消息发送

        Parameters
        ----------
        Bot: `CallbackContext`
            传入参数
        chat_id: `str | int`
            对话id
        text: `list[str]`
            要转换的文本, 以`list`形式传入
        joiner: `str` = '\\n'
            参数`text`在转换时各元素之间的连接符
        parse_mode: `str | None` = None
            仅支持 MarkdownV2, 且`text`中任何元素均为单一实体, 即形如 ``str``, *str*, _str_,\n
            支持的修饰符有 [ * | _ | __ | ~ | `` | *_ | *__ | *~ | _~ | __~ | `````` ]

        Returns
        -------
        `Message`
            Message(TelegramObject)

        """
        # 构建分割后的字符串列表
        text = MessageText().too_long_split(text, parse_mode=parse_mode, joiner=joiner)
        text = MessageText().short2long(text)
        reply_to_message_id = None
        for line in text:
            try:
                if reply_to_message_id:
                    bsr = self.send_message(
                        chat_id,
                        line,
                        parse_mode=parse_mode,
                        reply_to_message_id=reply_to_message_id,
                    )
                else:
                    bsr = self.send_message(chat_id, line, parse_mode=parse_mode)
                reply_to_message_id = bsr['message_id']
            except BadRequest:
                raise MessageError(line, '发生于 MyBot.send_too_long_message')
        return bsr


BOT = MyBot(os.environ['DEVELOPER_TOKEN'])
if __name__ == '__main__':
    pass
