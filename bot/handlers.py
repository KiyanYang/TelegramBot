#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Filename    :  handlers.py
@Datatime    :  2021/09/23 18:42:37
@Author      :  Kiyan Yang
@Contact     :  KiyanYang@outlook.com
@Version     :  v1.1
@Description :  telegram bot 所需要的 handler 模块
"""
import json
import logging
import os
import traceback

import requests
from telegram import (
    BotCommandScopeChat,
    BotCommandScopeDefault,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
)

from .config import CFG, GITHUB
from .my_bot import BOT
from .tools import (
    EscapeMarkDowmV2,
    Fund,
    GetUrlError,
    MessageError,
    MessageText,
    datetime_now,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def get_lang(primary_key: str, subkey: str, language_code: str | None = None):
    if (language_code is None) or (language_code not in CFG[1].keys()):
        language_code = 'zh'
    return CFG[1][language_code][primary_key][subkey]


# 均使用 classmethod 或 staticmethod, 以防止调用出错
# CommandHandler ==============================================================
class CommHandlerBingimage:
    """命令/bing_image => 必应日图"""

    def __new__(cls) -> CommandHandler:
        comm_handler = CommandHandler('bing_image', cls.bing_image)
        return comm_handler

    @staticmethod
    def _get_bingimage() -> tuple[str, str, str]:
        base_url = 'https://cn.bing.com/HPImageArchive.aspx?format=js&n=1&mkt=zh-CN'
        r_json = requests.get(base_url).json()
        url_image = r_json['images'][0]
        image_url = f"https://www.bing.com{url_image['urlbase']}_1920x1080.jpg"
        image_url_uhd = f"https://www.bing.com{url_image['urlbase']}_UHD.jpg"
        image_copyright = url_image['copyright']
        return image_url, image_url_uhd, image_copyright

    @classmethod
    def bing_image(cls, update: Update, context: CallbackContext) -> None:
        """获取必应今日高清壁纸，并包含UHD图链接"""
        chat_id = update.effective_chat.id
        context.bot.send_chat_action(chat_id, 'upload_photo')
        image_url, image_url_uhd, image_copyright = cls._get_bingimage()
        text_view_uhd_image = get_lang('bing_image', 'bing_image')
        text = f'''\
            {image_copyright}
            \[{text_view_uhd_image}\]\({image_url_uhd}\)
            '''
        text = MessageText.dedent(text)
        text = EscapeMarkDowmV2.sub_auto(text)
        context.bot.send_photo(
            chat_id,
            image_url,
            caption=text,
            parse_mode='MarkdownV2',
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END


# CommandHandler ==============================================================
class CommHandlerCancal:
    """命令/cancel => 取消"""

    def __new__(cls) -> CommandHandler:
        comm_handler = CommandHandler('cancel', cls.cancel)
        return comm_handler

    @staticmethod
    def cancel(update: Update, context: CallbackContext) -> None:
        """取消操作, 重置状态"""
        chat_id = update.effective_chat.id
        text = get_lang('cancel', 'cancel')
        context.bot.send_message(chat_id, text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END


# CommandHandler ==============================================================
class CommHandlerHello:
    """命令/hello => 问好"""

    def __new__(cls) -> CommandHandler:
        comm_handler = CommandHandler('hello', cls.hello)
        return comm_handler

    @staticmethod
    def hello(update: Update, context: CallbackContext) -> None:
        chat_id = update.effective_chat.id
        first_name = update.effective_user.first_name
        text_hello = get_lang('hello', 'hello')
        text = f'{text_hello}{first_name}'
        context.bot.send_message(chat_id, text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END


# CommandHandler ==============================================================
class CommHandlerHelp:
    """命令/help => 帮助"""

    def __new__(cls) -> CommandHandler:
        comm_handler = CommandHandler('help', cls.help)
        return comm_handler

    @staticmethod
    def help(update: Update, context: CallbackContext) -> None:
        chat_id = update.effective_chat.id
        if chat_id == os.environ['DEVELOPER_CHAT_ID']:
            text = get_lang('help', 'help_1')
        else:
            text = get_lang('help', 'help_1')
        text = EscapeMarkDowmV2.sub_auto(text)
        context.bot.send_message(
            chat_id, text, parse_mode='MarkdownV2', reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END


# CommandHandler ==============================================================
class CommHandlerStart:
    """命令/start => 开始"""

    def __new__(cls) -> CommandHandler:
        comm_handler = CommandHandler('start', cls.start)
        return comm_handler

    @staticmethod
    def start(update: Update, context: CallbackContext) -> None:
        chat_id = update.effective_chat.id
        text = get_lang('start', 'start')
        context.bot.send_message(chat_id, text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END


# ConversationHandler =========================================================
class ConvHandlerFund:
    """命令/fund => 基金相关，启动对话"""

    def __new__(cls) -> ConversationHandler:
        cls.CHOOSING, cls.FUNDINFO = range(2)
        cls.fund_url = CFG[0]['jsdelivr']['fund']
        __states = {
            cls.CHOOSING: [
                MessageHandler(Filters.regex('^(基金信息)$'), cls.show_fund_code),
                MessageHandler(Filters.regex('^(今日操作)$'), cls.send_today_action),
                MessageHandler(Filters.regex('^(估计收益)$'), cls.send_all_fund_income),
                MessageHandler(Filters.regex('^(/fund)$'), ConvHandlerFund.fund),
                MessageHandler(Filters.regex('^(/settings)$'), ConvHandlerSettings.settings),
            ],
            cls.FUNDINFO: [
                MessageHandler(Filters.regex(r'^\d{6}$'), cls.send_fund_info),
                MessageHandler(Filters.regex('^(/fund)$'), ConvHandlerFund.fund),
                MessageHandler(Filters.regex('^(/settings)$'), ConvHandlerSettings.settings),
            ],
        }
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('fund', cls.fund)],
            states=__states,
            fallbacks=[CommandHandler('cancel', cls.cancel)],
        )
        return conv_handler

    @classmethod
    def fund(cls, update: Update, context: CallbackContext):
        try:
            cls.fund_data = GITHUB.get_raw(cls.fund_url, 'json')
        except:
            raise GetUrlError(cls.github_url, 'Fund/fund【fund 命令】')
        chat_id = update.effective_chat.id
        text = get_lang('fund', 'fund')
        myfund_reply_keyboard = [['基金信息', '今日操作', '估计收益']]
        markup = ReplyKeyboardMarkup(
            myfund_reply_keyboard, resize_keyboard=True, one_time_keyboard=True
        )
        context.bot.send_message(chat_id, text, reply_markup=markup)
        return cls.CHOOSING

    # fund选择 基金信息_1
    @classmethod
    def show_fund_code(cls, update: Update, context: CallbackContext):
        chat_id = update.effective_chat.id
        text = get_lang('fund', 'show_fund_code')
        wang_ge = cls.fund_data['WangGe']  # 获取网格基金
        fundcode = [x[0] for x in wang_ge]
        fundcode = [fundcode[x : x + 3] for x in range(0, len(fundcode), 3)]
        markup = ReplyKeyboardMarkup(fundcode, resize_keyboard=True)
        context.bot.send_message(chat_id, text, reply_markup=markup)
        return cls.FUNDINFO

    # fund选择 基金信息_2, 根据输入的基金代码获取相关信息
    @classmethod
    def send_fund_info(cls, update: Update, context: CallbackContext):
        chat_id = update.effective_chat.id
        context.bot.send_chat_action(chat_id, 'typing')  # 发送动作
        # 创建基金数据，并转置
        fund_info_list = [Fund.FUNDINFO_HEADER]
        fund_info_list.append(Fund.get_fund_info(update.effective_message.text))
        fund_info_list_zip = list(zip(*fund_info_list))
        # 将转置后的2维list中一维用'：'连接，然后在用'\n'连接
        flz = ['：'.join([str(i) for i in x]) for x in fund_info_list_zip]
        text = '\n'.join(flz)
        # 发送信息
        context.bot.send_message(chat_id, text)
        return cls.FUNDINFO

    # myfund选择“今日操作”
    @classmethod
    def send_today_action(cls, update: Update, context: CallbackContext):
        chat_id = update.effective_chat.id
        context.bot.send_chat_action(chat_id, 'typing')  # 发送动作
        wang_ge = cls.fund_data['WangGe']  # 获取网格基金
        # 创建“今日操作”数据
        fund_dict = {}
        for fe in wang_ge:
            fund_dict.update(Fund.get_fund_info(fe[0], type='dict'))
        code_jz_fene_w_jzgs_gzzf = [x[:] + fund_dict[x[0]][1:3] for x in wang_ge]
        fw = Fund.get_fund_working(code_jz_fene_w_jzgs_gzzf)  # 得到今日操作
        # 基金代码左对齐<10, 今日操作左对齐<9, 估值涨幅右对齐>7
        text_fw_1 = [f'{x[0]:<10}{x[1]:<9}{x[2]:>7}' for x in fw]
        text_fw_2 = '\n'.join(text_fw_1)
        text = f'\`{text_fw_2}\`'
        text = EscapeMarkDowmV2.sub_auto(text)
        # 发送信息，并移除回复键盘
        context.bot.send_message(
            chat_id, text, parse_mode='MarkdownV2', reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    # myfund选择“估计收益”
    @classmethod
    def send_all_fund_income(cls, update: Update, context: CallbackContext):
        chat_id = update.effective_chat.id
        context.bot.send_chat_action(chat_id, 'typing')  # 发送动作
        all_fund = cls.fund_data['AllFund']  # 获取全部基金份额
        code_income_name = []
        all_fund_income = 0
        today = datetime_now(f='d')
        res = requests.get(CFG[0]['API_holiday'] + today).json()
        for code in all_fund:
            fund_info = Fund.get_fund_info(code)
            name = f'{fund_info[1][:9]}'
            if fund_info[5] == today:
                jz, jz_last = float(fund_info[4]), float(fund_info[8])
                income = all_fund[code] * (jz - jz_last)
                code += '^'  # 表示实际收益
            elif res['type']['type'] == 0:
                jz, jz_last = float(fund_info[2]), float(fund_info[4])
                income = all_fund[code] * (jz - jz_last)
                code += '*'  # 表示估算收益
            else:
                income = 0  # 非交易日返回
                code += '-'  # -
            code_income_name.append([code, f'{income:.2f}', name])
            all_fund_income += income
        code_income_name.append(['Income', f'{all_fund_income:.2f}', ''])
        # 基金代码左对齐<10, 今日收益右对齐>7, 基金名称
        code_income_name = [f'{x[0]:<7}{x[1]:>7}  {x[2]}' for x in code_income_name]
        text_code_income_name = '\n'.join(code_income_name)
        text = EscapeMarkDowmV2.sub_auto(f'\`{text_code_income_name}\`')
        # 发送信息，并移除回复键盘
        context.bot.send_message(
            chat_id, text, parse_mode='MarkdownV2', reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    @staticmethod
    def cancel(update: Update, context: CallbackContext):
        chat_id = update.effective_chat.id
        text = get_lang('fund', 'cancel')
        context.bot.send_message(chat_id, text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END


# ConversationHandler =========================================================
class ConvHandlerSettings:
    """命令/settings => 设置"""

    def __new__(cls) -> ConversationHandler:
        cls.SETTINGS_COMMANDS = 0
        cls.DEVELOPER_CHAT_ID = os.environ['DEVELOPER_CHAT_ID']
        __states = {
            cls.SETTINGS_COMMANDS: [
                MessageHandler(Filters.regex('^(设置命令)$'), cls.set_my_commands),
                MessageHandler(Filters.regex('^(删除命令)$'), cls.del_my_commands),
                MessageHandler(Filters.regex('^(/fund)$'), ConvHandlerFund.fund),
                MessageHandler(Filters.regex('^(/settings)$'), ConvHandlerSettings.settings),
            ]
        }
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('settings', cls.settings)],
            states=__states,
            fallbacks=[CommandHandler('cancel', cls.cancel)],
        )
        return conv_handler

    @classmethod
    def settings(cls, update: Update, context: CallbackContext):
        chat_id = update.effective_chat.id
        settings_reply_keyboard = [['设置命令', '删除命令']]
        markup = ReplyKeyboardMarkup(
            settings_reply_keyboard, resize_keyboard=True, one_time_keyboard=True
        )
        text = get_lang('settings', 'settings')
        context.bot.send_message(chat_id, text, reply_markup=markup)
        return cls.SETTINGS_COMMANDS

    @classmethod
    def set_my_commands(cls, update: Update, context: CallbackContext):
        scope_1 = BotCommandScopeChat(cls.DEVELOPER_CHAT_ID)
        scope_2 = BotCommandScopeDefault()
        context.bot.set_my_commands(CFG[0]['MY_COMMANDS_1'], scope=scope_1)
        context.bot.set_my_commands(CFG[0]['MY_COMMANDS_2'], scope=scope_2)
        chat_id = update.effective_chat.id
        text = get_lang('settings', 'set_my_commands')
        context.bot.send_message(chat_id, text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    @classmethod
    def del_my_commands(cls, update: Update, context: CallbackContext):
        scope_1 = BotCommandScopeChat(cls.DEVELOPER_CHAT_ID)
        scope_2 = BotCommandScopeDefault()
        context.bot.delete_my_commands(scope=scope_1)
        context.bot.delete_my_commands(scope=scope_2)
        chat_id = update.effective_chat.id
        text = get_lang('settings', 'del_my_commands')
        context.bot.send_message(chat_id, text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    @staticmethod
    def cancel(update: Update, context: CallbackContext):
        chat_id = update.effective_chat.id
        text = get_lang('settings', 'cancel')
        context.bot.send_message(chat_id, text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END


# MessageHandler ==============================================================
class MessHandlerEcho:
    """消息 => 复读普通消息"""

    def __new__(cls) -> MessageHandler:
        __filters = Filters.text & ~Filters.command & Filters.chat_type.private
        mess_handler = MessageHandler(__filters, cls.echo)
        return mess_handler

    @staticmethod
    def echo(update: Update, _) -> None:
        chat_id = update.effective_chat.id
        # 复读，message.copy的方法是返回MessageId，行为类似于forwardMessage
        update.message.copy(chat_id)


# MessageHandler ==============================================================
class MessHandlerUnknown:
    """消息 => 未知指令"""

    def __new__(cls) -> MessageHandler:
        __filters = Filters.command & Filters.chat_type.private
        mess_handler = MessageHandler(__filters, cls.unknown)
        return mess_handler

    @staticmethod
    def unknown(update: Update, context: CallbackContext) -> None:
        chat_id = update.effective_chat.id
        text = get_lang('unknown', 'unknown')
        context.bot.send_message(chat_id, text)


# ErrorHandler ================================================================
class ErrorHandler:
    """记录错误日志并向开发者发送 Telegram 消息"""

    def __new__(cls):
        error_handler = cls.error_handler
        return error_handler

    @classmethod
    def error_handler(cls, update: object, context: CallbackContext) -> None:
        """记录错误日志并向开发者发送 Telegram 消息"""
        logger.error(msg="Exception while handling an update:", exc_info=context.error)

        tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
        tb_string = ''.join(tb_list)

        update_str = update.to_dict() if isinstance(update, Update) else str(update)
        text_error = get_lang('error', 'error')
        text = (
            f'{text_error}',
            f'\`update = {json.dumps(update_str, indent=2, ensure_ascii=False)}\`',
            f'\`context.chat_data = {str(context.chat_data)}\`',
            f'\`context.user_data = {str(context.user_data)}\`',
            f'\`{tb_string}\`',
        )
        text = EscapeMarkDowmV2.sub_auto(text)

        # 最后, 发送消息，采用多次发送
        BOT.send_too_long_message(
            os.environ['DEVELOPER_CHAT_ID'], text, joiner='\n\n', parse_mode='MarkdownV2'
        )


# TestHandler =================================================================
class TestHandler:
    def __new__(cls):
        # __filters = Filters.chat(os.environ['DEVELOPER_CHAT_ID'])
        # comm_handler = CommandHandler('test', cls.test, filters=__filters)
        test_handler = CommandHandler('test', cls.test)
        return test_handler

    @classmethod
    def test(cls, update: Update, context: CallbackContext):
        # chat_id = update.effective_chat.id

        # with open('test.txt', encoding='utf-8') as f:
        #     lines = f.readlines()
        #     line = f.read()

        # tool_bot.long2multiple_message(context.bot, chat_id, [line], joiner='\n\n')
        # context.bot.send_message(chat_id, text, parse_mode='MarkdownV2')
        cls.test_error1()

    @classmethod
    def test_error1(cls):
        try:
            cls.test_error2()
        except:
            try:
                try:
                    try:
                        try:
                            raise ValueError('xxxasd')
                        except:
                            raise ValueError('xxx123')
                    except:
                        raise ValueError('xxxqwe')
                except:
                    raise ValueError('xxx456')
            except:
                raise MessageError('xxxpoi', '/bot.py/TestHandler')
        finally:
            cls.test_error2()

    @classmethod
    def test_error2(cls):
        try:
            try:
                try:
                    try:
                        raise ValueError('asd')
                    except:
                        raise ValueError('123')
                except:
                    raise ValueError('qwe')
            except:
                raise ValueError('456')
        except:
            raise ValueError('poi')
