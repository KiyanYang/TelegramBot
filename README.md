# TelegramBot

基于 python-telegram-bot 的 telegram bot

[![](https://img.shields.io/badge/Bot%20API-5.4-blue?logo=telegram)](https://core.telegram.org/bots/api-changelog)

# 环境

`python 3.10`

# 功能

待补充

# 目录

```
├─bot
│  ├─configs
│  │  ├─config.yaml
│  │  └─languages.yaml
│  ├─tools
│  │  ├─config.py
│  │  ├─fund.py
│  │  ├─github.py
│  │  ├─other.py
│  │  ├─text.py
│  │  └─__init__.py
│  ├─bot.py
│  ├─config.py
│  ├─handlers.py
│  └─__init__.py
├─main.py
├─README.md
└─requirements.txt
```

# heroku

如果部署到 heroku，除了需要上面目录中的文件外，还需要 `Procfile` 和 `runtime.txt` 两个文件

# 配置

## 环境变量

需要设置以下 6 个环境变量，下面为 ps1(powershell) 文件示例

```
$Env:TOKEN_BOT = "TG_BOT_TOKEN_1"  # Telegram 机器人的 TOKEN
$Env:TOKEN_TEST = "TG_BOT_TOKEN_2" # Telegram 测试使用的机器人的 TOKEN
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
   多种语言，主要用于 `bot/handlers.py` ，根据语言代码选择相应的数据，`get_text()` 函数，调用此函数得到相应的语言文本。`language_code` 使用 IETF language tag，目前初始设置 2 种语言 `zh-hans` 和 `en`（只翻译了个别语句，仅供测试）。
