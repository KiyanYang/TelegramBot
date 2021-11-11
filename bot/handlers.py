#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Filename    :  handlers.py
@Datatime    :  2021/11/07 20:02:57
@Author      :  Kiyan Yang
@Contact     :  KiyanYang@outlook.com
@Version     :  v1.2
@Description :  telegram bot 所需要的 handler 模块
"""
from functools import wraps
from typing import Any

import requests
from telegram import (
    BotCommandScopeChat,
    BotCommandScopeDefault,
    ChatAction,
    InlineKeyboardButton,
    Message,
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

from .config import CFG, DEVELOPER_CHAT_ID, GITHUB
from .tools import Fund, MarkdownV2, get_logger

logger = get_logger(__name__)


# 辅助函数 =====================================================================
def build_keyboard(
    buttons: list[InlineKeyboardButton] | list[ReplyKeyboardMarkup],
    n_cols: int,
    header_buttons: InlineKeyboardButton
    | list[InlineKeyboardButton]
    | ReplyKeyboardMarkup
    | list[ReplyKeyboardMarkup] = None,
    footer_buttons: InlineKeyboardButton
    | list[InlineKeyboardButton]
    | ReplyKeyboardMarkup
    | list[ReplyKeyboardMarkup] = None,
) -> list[list[InlineKeyboardButton]] | list[list[ReplyKeyboardMarkup]]:
    keyboard = [buttons[x:x + n_cols] for x in range(0, len(buttons), n_cols)]
    if header_buttons:
        keyboard.insert(0, header_buttons if isinstance(header_buttons, list) else [header_buttons])
    if footer_buttons:
        keyboard.append(footer_buttons if isinstance(footer_buttons, list) else [footer_buttons])
    return keyboard


def get_text(topkey: str, subkey: str, update: Update = None, language_code: str = None):
    if update is not None:
        code = update.effective_user.language_code
    if language_code is not None:
        code = language_code
    # code = 'en'  # 测试语言使用
    if (code is None) or (code not in ('zh-hans', 'en')):
        code = 'zh-hans'
    return CFG[1][topkey][subkey][code]


def stop(*args, **kwargs) -> int:
    return END


# 装饰器 =======================================================================
def send_action(action) -> Any:
    """Sends `action` while processing func command."""
    def decorator(func: callable):
        @wraps(func)
        def send_action_(self, update: Update, context: CallbackContext, *args, **kwargs) -> Any:
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(self, update, context, *args, **kwargs)

        return send_action_

    return decorator


def cancel(topkey: str, subkey: str, language_code: str = None) -> Any:
    '''执行取消命令，发送消息，移除键盘'''
    def decorator(func: callable):
        @wraps(func)
        def cancel_(self, update: Update, context: CallbackContext, *args, **kwargs):
            res = func(self, update, context, *args, **kwargs)
            chat_id = update.effective_message.chat_id
            language_code = update.effective_user.language_code
            text = get_text(topkey, subkey, language_code=language_code)
            context.bot.send_message(chat_id, text, reply_markup=ReplyKeyboardRemove())
            return res

        return cancel_

    return decorator


def stop_other_conversation(func: callable) -> Any:
    """停止其他对话"""
    @wraps(func)
    def stop_(self, update: Update, context: CallbackContext, *args, **kwargs):
        stop_keys = STOP_KEYS.copy()
        del stop_keys[func.__name__]
        for stop_key in stop_keys.values():
            message = Message(
                message_id=0,
                date=update.message.date,
                chat=update.message.chat,
                from_user=update.message.from_user,
                text=stop_key,
            )
            context.dispatcher.process_update(Update(update.update_id, message=message))
        return func(self, update, context, *args, **kwargs)

    return stop_


# 快捷别名/全局变量 =============================================================
send_action_typing = send_action(ChatAction.TYPING)
send_action_upload_photo = send_action(ChatAction.UPLOAD_PHOTO)
END = ConversationHandler.END
STOP_KEYS = {'fund': '_stop_fund_', 'settings': '_stop_settings_'}
STOP_HANDLERS = {k: MessageHandler(Filters.regex(f'^{v}$'), stop) for k, v in STOP_KEYS.items()}


# CommandHandler ==============================================================
class CommHandlerBingimage:
    """命令`/bing_image` => 必应日图"""
    def __init__(self) -> None:
        self.handler = CommandHandler('bing_image', self.bing_image)

    def get_bingimage(self) -> tuple[str, str, str]:
        base_url = 'https://cn.bing.com/HPImageArchive.aspx?format=js&n=1&mkt=zh-CN'
        r_json = requests.get(base_url).json()
        url_image = r_json['images'][0]
        image_url = f"https://www.bing.com{url_image['urlbase']}_1920x1080.jpg"
        image_url_uhd = f"https://www.bing.com{url_image['urlbase']}_UHD.jpg"
        image_copyright = url_image['copyright']
        return image_url, image_url_uhd, image_copyright

    @send_action_upload_photo
    def bing_image(self, update: Update, context: CallbackContext) -> None:
        """获取必应今日高清壁纸，包含高清图链接、超高清图链接、版权信息"""
        chat_id = update.effective_message.chat_id
        image_url, image_url_uhd, image_copyright = self.get_bingimage()
        text_view_uhd_image = get_text('bing_image', 'bing_image', update=update)
        text = (f'{image_copyright}', f'\[{text_view_uhd_image}\]\({image_url_uhd}\)')
        text = MarkdownV2.sub_auto('\n'.join(text))
        context.bot.send_photo(chat_id, image_url, caption=text, parse_mode='MarkdownV2')


# CommandHandler ==============================================================
class CommHandlerCancel:
    """命令`/cancel` => 取消"""
    def __init__(self) -> None:
        self.handler = CommandHandler('cancel', self.cancel)

    @cancel('cancel', 'cancel')
    def cancel(self, update: Update, context: CallbackContext) -> None:
        """取消操作, 重置状态"""
        pass


# CommandHandler ==============================================================
class CommHandlerEcho:
    """命令`/echo` => 复读消息"""
    def __init__(self) -> None:
        self.handler = CommandHandler('echo', self.echo)

    def echo(self, update: Update, context: CallbackContext) -> None:
        chat_id = update.effective_message.chat_id
        message = update.message
        if 'reply_to_message' in message.to_dict().keys():
            try:
                message_id = message.reply_to_message.message_id
                context.bot.copy_message(chat_id, chat_id, message_id)
            except Exception as e:
                ...
        else:
            text = get_text('echo', 'echo', update=update)
            text = MarkdownV2.sub_auto(text)
            context.bot.send_message(chat_id, text, parse_mode='MarkdownV2')


# CommandHandler ==============================================================
class CommHandlerHello:
    """命令`/hello` => 问好"""
    def __init__(self) -> None:
        self.handler = CommandHandler('hello', self.hello)

    def hello(self, update: Update, context: CallbackContext) -> None:
        chat_id = update.effective_message.chat_id
        first_name = update.effective_user.first_name
        text_hello = get_text('hello', 'hello', update=update)
        text = f'{text_hello}{first_name}'
        context.bot.send_message(chat_id, text)


# CommandHandler ==============================================================
class CommHandlerHelp:
    """命令`/help` => 帮助"""
    def __init__(self) -> None:
        self.handler = CommandHandler('help', self.help)

    def help(self, update: Update, context: CallbackContext) -> None:
        chat_id = update.effective_message.chat_id
        if chat_id == DEVELOPER_CHAT_ID:
            text = get_text('help', 'help_1', update=update)
        else:
            text = get_text('help', 'help_1', update=update)
        text = MarkdownV2.sub_auto(text)
        context.bot.send_message(chat_id, text, parse_mode='MarkdownV2')


# CommandHandler ==============================================================
class CommHandlerHhsh:
    """命令`/hhsh` => 好好说话"""
    def __init__(self) -> None:
        self.handler = CommandHandler('hhsh', self.hhsh)

    def get_nbnhhsh(self, text: list[str] = None) -> list[dict[str:list[str]]]:
        payload = {'text': ','.join(text)}
        res = requests.post(CFG[0]['API']['nbnhhsh'], json=payload).json()
        # 反序再反序可以使重复的数据按首次出现的位置排序
        rule = {x: i for i, x in enumerate(text[::-1])}
        res_sorted = sorted(res, key=lambda x: rule[x['name']], reverse=True)
        return res_sorted

    @send_action_typing
    def hhsh(self, update: Update, context: CallbackContext) -> None:
        def trans(nbnhhsh: dict) -> str:
            if 'trans' in nbnhhsh.keys():
                trans = nbnhhsh['trans']
                trans.insert(0, '')
                trans_text = '\n    '.join(trans)
            else:
                trans_text = '\n    ' + text_hhsh_2
            return f'\*{nbnhhsh["name"]}：\*{trans_text}\n'

        chat_id = update.effective_message.chat_id
        args_hhsh = context.args
        text_hhsh_1 = get_text('hhsh', 'hhsh_1', update=update)
        text_hhsh_2 = get_text('hhsh', 'hhsh_2', update=update)
        if args_hhsh == [] or args_hhsh is None:
            text = text_hhsh_1
        else:
            nbnhhsh = self.get_nbnhhsh(args_hhsh)
            text = [trans(x) for x in nbnhhsh]
            text = '\n'.join(text)
        text = MarkdownV2.sub_auto(text)
        context.bot.send_message(chat_id, text, parse_mode='MarkdownV2')


# CommandHandler ==============================================================
class CommHandlerStart:
    """命令`/start` => 开始"""
    def __init__(self) -> None:
        self.handler = CommandHandler('start', self.start)

    def start(self, update: Update, context: CallbackContext) -> None:
        chat_id = update.effective_message.chat_id
        text = get_text('start', 'start', update=update)
        context.bot.send_message(chat_id, text)


# ConversationHandler =========================================================
class ConvHandlerFund:
    """命令`/fund` => 基金相关，启动对话"""
    def __init__(self) -> None:
        self.CHOOSING, self.FUNDINFO = range(2)
        self.fund_url = CFG[0]['GitHub']['fund']
        _states = {
            self.CHOOSING: [
                MessageHandler(Filters.regex('^基金信息$'), self.show_fund_code),
                MessageHandler(Filters.regex('^今日操作$'), self.send_today_action),
                MessageHandler(Filters.regex('^估计收益$'), self.send_all_fund_income),
            ],
            self.FUNDINFO: [
                MessageHandler(Filters.regex(r'^\d{6}$'), self.send_fund_info),
            ],
        }
        self.handler = ConversationHandler(
            entry_points=[CommandHandler('fund', self.fund)],
            states=_states,
            fallbacks=[CommandHandler('cancel', self.cancel), STOP_HANDLERS['fund']],
            allow_reentry=True,
        )

    @stop_other_conversation
    def fund(self, update: Update, context: CallbackContext):
        ...
        return self.CHOOSING

    # fund选择 基金信息_1
    def show_fund_code(self, update: Update, context: CallbackContext):
        ...
        return self.FUNDINFO

    # fund选择 基金信息_2, 根据输入的基金代码获取相关信息
    @send_action_typing
    def send_fund_info(self, update: Update, context: CallbackContext):
        ...
        return self.FUNDINFO

    # myfund选择“今日操作”
    @send_action_typing
    def send_today_action(self, update: Update, context: CallbackContext):
        ...
        return END

    # myfund选择“估计收益”
    @send_action_typing
    def send_all_fund_income(self, update: Update, context: CallbackContext) -> int:
        ...
        return END

    @cancel('fund', 'cancel')
    def cancel(self, update: Update, context: CallbackContext) -> int:
        return END


# ConversationHandler =========================================================
class ConvHandlerSettings:
    """命令`/settings` => 设置，启动对话"""
    def __init__(self) -> None:
        self.SETTINGS = range(1)
        _states = {
            self.SETTINGS: [
                MessageHandler(Filters.regex('^设置命令$'), self.set_my_commands),
                MessageHandler(Filters.regex('^删除命令$'), self.del_my_commands),
            ]
        }
        self.handler = ConversationHandler(
            entry_points=[CommandHandler('settings', self.settings)],
            states=_states,
            fallbacks=[CommandHandler('cancel', self.cancel), STOP_HANDLERS['settings']],
            allow_reentry=True,
        )

    @stop_other_conversation
    def settings(self, update: Update, context: CallbackContext) -> int:
        chat_id = update.effective_message.chat_id
        markup = ReplyKeyboardMarkup(
            [['设置命令', '删除命令']],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        text = get_text('settings', 'settings', update=update)
        context.bot.send_message(chat_id, text, reply_markup=markup)
        return self.SETTINGS

    def set_my_commands(self, update: Update, context: CallbackContext) -> int:
        scope_1 = BotCommandScopeChat(DEVELOPER_CHAT_ID)
        scope_2 = BotCommandScopeDefault()
        context.bot.set_my_commands(CFG[0]['MY_COMMANDS_1'], scope=scope_1)
        context.bot.set_my_commands(CFG[0]['MY_COMMANDS_2'], scope=scope_2)
        chat_id = update.effective_message.chat_id
        text = get_text('settings', 'set_my_commands', update=update)
        context.bot.send_message(chat_id, text, reply_markup=ReplyKeyboardRemove())
        return END

    def del_my_commands(self, update: Update, context: CallbackContext) -> int:
        scope_1 = BotCommandScopeChat(DEVELOPER_CHAT_ID)
        scope_2 = BotCommandScopeDefault()
        context.bot.delete_my_commands(scope=scope_1)
        context.bot.delete_my_commands(scope=scope_2)
        chat_id = update.effective_message.chat_id
        text = get_text('settings', 'del_my_commands', update=update)
        context.bot.send_message(chat_id, text, reply_markup=ReplyKeyboardRemove())
        return END

    @cancel('settings', 'cancel')
    def cancel(self, update: Update, context: CallbackContext) -> int:
        return END


# MessageHandler ==============================================================
class MessHandlerUnknown:
    """消息 => 未知指令"""
    def __init__(self) -> None:
        commands = [x[0] for x in CFG[0]['MY_COMMANDS_1']]
        commands_filter = Filters.regex(f'^({"|".join(commands)})')
        filters = ~commands_filter & Filters.command & Filters.chat_type.private
        self.handler = MessageHandler(filters, self.unknown)

    def unknown(self, update: Update, context: CallbackContext) -> None:
        chat_id = update.effective_message.chat_id
        text = get_text('unknown', 'unknown', update=update)
        context.bot.send_message(chat_id, text)


# TestHandler =================================================================
class TestHandler:
    def __init__(self) -> None:
        self.handler = CommandHandler('test', self.test)

    def test(self, update: Update, context: CallbackContext):
        self.test_0()

    def test_0(self, update: Update, context: CallbackContext):
        ...
        pass


# handlers
comm_handler_bingimage = CommHandlerBingimage().handler
comm_handler_cancel = CommHandlerCancel().handler
comm_handler_echo = CommHandlerEcho().handler
comm_handler_hello = CommHandlerHello().handler
comm_handler_help = CommHandlerHelp().handler
comm_handler_hhsh = CommHandlerHhsh().handler
comm_handler_start = CommHandlerStart().handler
conv_handler_fund = ConvHandlerFund().handler
conv_handler_settings = ConvHandlerSettings().handler
mess_handler_unknown = MessHandlerUnknown().handler
test_handler = TestHandler().handler
