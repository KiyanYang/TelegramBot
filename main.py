#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Filename    :  main.py
@Datatime    :  2021/09/23 20:07:17
@Author      :  Kiyan Yang
@Contact     :  KiyanYang@outlook.com
@Version     :  v1.51
@Description :  telegram bot 主文件
"""
import os

from telegram.ext import Updater

from bot import (
    CFG,
    LOCAL,
    comm_handler_bingimage,
    comm_handler_cancel,
    comm_handler_echo,
    comm_handler_hello,
    comm_handler_help,
    comm_handler_hhsh,
    comm_handler_start,
    conv_handler_fund,
    conv_handler_settings,
    error_handler,
    get_logger,
    mess_handler_unknown,
    test_handler,
)

logger = get_logger(__name__)

"""
需要设置以下 6 个环境变量，下面为 ps1 文件示例

$Env:TOKEN_BOT = "TG_BOT_TOKEN_1"  # Telegram 机器人的 TOKEN
$Env:TOKEN_TEST = "TG_BOT_TOKEN_2" # Telegram 测试使用的机器人的 TOKEN
$Env:TOKEN_GITHUB = "Personal access token"  # 适用于 Github API v4 的 TOKEN
$Env:DEVELOPER_TOKEN = "TG_BOT_TOKEN_3" # 向开发者发生错误日志的机器人的 TOKEN
$Env:DEVELOPER_CHAT_ID = "DEVELOPER_CHAT_ID"  # 开发者的 ID
$Env:LOCAL = 'True' # 是否使用本地环境，用于测试以及代理等相关内容，'True' 为开启，其他情况下均为关闭
"""

def main():
    if LOCAL:
        bot_token = os.environ['TOKEN_BOT_TEST']
        updater = Updater(token=bot_token, request_kwargs=CFG[0]['REQUEST_KWARGS'])
        dispatcher = updater.dispatcher
        dispatcher.add_handler(test_handler, group=10)
    else:
        bot_token = os.environ['TOKEN_BOT']
        updater = Updater(token=bot_token)
        dispatcher = updater.dispatcher

    # ConversationHandler 一般放在CommandHandler之前
    dispatcher.add_handler(conv_handler_fund, group=1)
    dispatcher.add_handler(conv_handler_settings, group=1)

    # CommandHandler
    dispatcher.add_handler(comm_handler_bingimage, group=1)
    dispatcher.add_handler(comm_handler_cancel, group=1)
    dispatcher.add_handler(comm_handler_echo, group=1)
    dispatcher.add_handler(comm_handler_hello, group=1)
    dispatcher.add_handler(comm_handler_help, group=1)
    dispatcher.add_handler(comm_handler_hhsh, group=1)
    dispatcher.add_handler(comm_handler_start, group=1)

    # MessageHandler, 一般在其他Handler之后
    dispatcher.add_handler(mess_handler_unknown, group=1)

    # error_handler 记录错误日志并向开发者发送 Telegram 消息
    dispatcher.add_error_handler(error_handler)

    if LOCAL:
        # 使用前打开 ngrok 所在目录并输入 `./ngrok http 5000` 获取 ngrok_https 注意要以 `/` 结尾
        ngrok_https = 'https://627b-2001-250-4000-821b-bd2f-8ff7-8c74-f0c5.ngrok.io/'
        updater.start_webhook(
            listen='127.0.0.1',
            port=5000,
            url_path='TelegramBot',
            webhook_url=ngrok_https + 'TelegramBot',
        )

    else:
        updater.start_webhook(
            listen="0.0.0.0",
            port=int(os.environ.get('PORT', '5000')),
            url_path='TelegramBot',
            webhook_url="https://tg-bot-lscr.herokuapp.com/" + 'TelegramBot',
        )

    updater.idle()


if __name__ == '__main__':
    main()
