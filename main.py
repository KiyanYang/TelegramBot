#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Filename    :  main.py
@Datatime    :  2021/09/23 20:07:17
@Author      :  Kiyan Yang
@Contact     :  KiyanYang@outlook.com
@Version     :  v1.5
@Description :  telegram bot 主文件
"""
import logging
import os
from time import time

from telegram.ext import Updater

from bot import (
    CFG,
    LOCAL,
    BOT,
    CommHandlerBingimage,
    CommHandlerCancal,
    CommHandlerHello,
    CommHandlerHelp,
    CommHandlerStart,
    ConvHandlerFund,
    ConvHandlerSettings,
    ErrorHandler,
    MessHandlerEcho,
    MessHandlerUnknown,
    TestHandler,
)


def main():
    time_start = time()
    if LOCAL:
        bot_token = os.environ.get('TOKEN_BOT_TEST', os.environ['TOKEN_BOT'])
        updater = Updater(token=bot_token, request_kwargs=CFG[0]['REQUEST_KWARGS'])
        dispatcher = updater.dispatcher
        dispatcher.add_handler(TestHandler())
    else:
        bot_token = CFG[0]['TOKEN_BOT']
        updater = Updater(token=bot_token)
        dispatcher = updater.dispatcher

    # ConversationHandler 一般放在CommandHandler之前
    dispatcher.add_handler(ConvHandlerFund())
    dispatcher.add_handler(ConvHandlerSettings())

    # CommandHandler
    dispatcher.add_handler(CommHandlerStart())
    dispatcher.add_handler(CommHandlerHello())
    dispatcher.add_handler(CommHandlerBingimage())
    dispatcher.add_handler(CommHandlerCancal())
    dispatcher.add_handler(CommHandlerHelp())

    # MessageHandler, 一般在其他Handler之后
    dispatcher.add_handler(MessHandlerUnknown())  # 用于接收未知指令，必须放置在命令之后
    dispatcher.add_handler(MessHandlerEcho())  # 用于接收文字消息并复读，必须放置在命令之后

    # error_handler 记录错误日志并向开发者发送 Telegram 消息
    dispatcher.add_error_handler(ErrorHandler())

    if LOCAL:
        # polling 模式
        # updater.start_polling()

        # webhook 模式
        # 使用前打开 ngrok 所在目录并输入 `./ngrok http 5000` 获取 ngrok_https
        ngrok_https = 'https://aed5-2001-250-4000-821b-21c8-bf-4997-e03a.ngrok.io/'
        updater.start_webhook(listen='127.0.0.1',
                              port=5000,
                              url_path='TelegramBot',
                              webhook_url=ngrok_https + 'TelegramBot')

    else:
        updater.start_webhook(
            listen="0.0.0.0",
            port=int(os.environ.get('PORT', '5000')),
            url_path='TelegramBot',
            webhook_url="https://tg-bot-lscr.herokuapp.com/" + 'TelegramBot',
        )
    time_end = time()  # 结束计时
    text_time_cost = f'time cost {time_end-time_start:.3f} s'
    if LOCAL:
        logging.info(text_time_cost)
    else:
        BOT.send_message(os.environ['DEVELOPER_CHAT_ID'], text_time_cost)

    updater.idle()


if __name__ == '__main__':
    main()
