# TelegramBot

基于 python-telegram-bot 的 telegram bot

[![](https://img.shields.io/badge/Bot%20API-5.3-blue?logo=telegram)](https://core.telegram.org/bots/api-changelog)

# 环境

`python 3.10`

# heroku

文档待补充

# 配置

## 环境变量

需要设置以下 6 个环境变量，下面为 ps1 文件示例

```
$Env:TOKEN_BOT = "TG_BOT_TOKEN_1"  # Telegram 机器人的 TOKEN
$Env:TOKEN_TEST = "TG_BOT_TOKEN_2" # Telegram 测试使用的机器人的 TOKEN, 可选
$Env:TOKEN_GITHUB = "Personal access token"  # 适用于 Github API v4 的 TOKEN
$Env:DEVELOPER_TOKEN = "TG_BOT_TOKEN_3" # 向开发者发生错误日志的机器人的 TOKEN
$Env:DEVELOPER_CHAT_ID = "DEVELOPER_CHAT_ID"  # 开发者的 ID
$Env:LOCAL = 'True' # 是否使用本地环境，用于测试以及代理等相关内容，'True' 为开启，其他情况下均为关闭
```

## 配置

位于 `bot/configs` 下，包含配置文件和语言文件。

1. 配置文件
   主要配置参数以及其他可能变更的参数（如文件链接），此外你也可以将环境变量中的 6 个变量写入此处（当然你要修改文件中这 6 个变量的读取路径）
2. 语言文件
   多种语言，主要用于 `bot/handlers.py` ，暂时在处理消息时并未根据语言代码选择相应的数据，但是框架已经写好，文件内 `get_lang()` 函数，只需调用此函数的时传入语言代码就可得到相应的语言文本。
   问题在于语言代码，虽然 telegram 说明了 `language_code` 使用 IETF language tag，但是并不明确，以我为例， telegram 传递的 `User` 字段显示我的 `language_code` 为 `zh-Hans` 而不是 `zh`，因此目前的语言文件是不能被正确处理的。我的想法是以 `https://translations.telegram.org/`为标准得到语言代码，比如简体中文的网站为 `https://translations.telegram.org/zh-hans/`。
