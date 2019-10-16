# SCP-079-PM - Everyone can have their own Telegram private chat bot
# Copyright (C) 2019 SCP-079 <https://scp-079.org>
#
# This file is part of SCP-079-PM.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import pickle
from configparser import RawConfigParser
from os import mkdir
from os.path import exists
from shutil import rmtree
from threading import Lock
from typing import List, Dict, Set, Tuple, Union

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING,
    filename='log',
    filemode='w'
)
logger = logging.getLogger(__name__)

# Read data from config.ini

# [basic]
bot_token: str = ""
prefix: List[str] = []
prefix_str: str = "/!"

# [channels]
critical_channel_id: int = 0
debug_channel_id: int = 0
exchange_channel_id: int = 0
hide_channel_id: int = 0
test_group_id: int = 0

# [custom]
backup: Union[str, bool] = ""
date_reset: str = ""
flood_ban: int = 0
flood_limit: int = 0
flood_time: int = 0
host_id: int = 0
host_name: str = ""
project_link: str = ""
project_name: str = ""
zh_cn: Union[str, bool] = ""

# [encrypt]
password: str = ""

try:
    config = RawConfigParser()
    config.read("config.ini")
    # [basic]
    bot_token = config["basic"].get("bot_token", bot_token)
    prefix = list(config["basic"].get("prefix", prefix_str))
    # [channels]
    critical_channel_id = int(config["channels"].get("critical_channel_id", critical_channel_id))
    debug_channel_id = int(config["channels"].get("debug_channel_id", debug_channel_id))
    exchange_channel_id = int(config["channels"].get("exchange_channel_id", exchange_channel_id))
    hide_channel_id = int(config["channels"].get("hide_channel_id", hide_channel_id))
    test_group_id = int(config["channels"].get("test_group_id", test_group_id))
    # [custom]
    backup = config["custom"].get("backup", backup)
    backup = eval(backup)
    date_reset = config["custom"].get("date_reset", date_reset)
    flood_ban = int(config["custom"].get("flood_ban", flood_ban))
    flood_limit = int(config["custom"].get("flood_limit", flood_limit))
    flood_time = int(config["custom"].get("flood_time", flood_time))
    host_id = int(config["custom"].get("host_id", host_id))
    host_name = config["custom"].get("host_name", host_name)
    project_link = config["custom"].get("project_link", project_link)
    project_name = config["custom"].get("project_name", project_name)
    zh_cn = config["custom"].get("zh_cn", zh_cn)
    zh_cn = eval(zh_cn)
    # [encrypt]
    password = config["encrypt"].get("password", password)
except Exception as e:
    logger.warning(f"Read data from config.ini error: {e}")

# Check
if (bot_token in {"", "[DATA EXPUNGED]"}
        or prefix == []
        or backup not in {False, True}
        or date_reset in {"", "[DATA EXPUNGED]"}
        or flood_ban == 0
        or flood_limit == 0
        or flood_time == 0
        or host_id == 0
        or host_name in {"", "[DATA EXPUNGED]"}
        or zh_cn not in {False, True}):
    logger.critical("No proper settings")
    raise SystemExit("No proper settings")

# Languages
lang: Dict[str, str] = {
    # Admin
    "admin": (zh_cn and "管理员") or "Admin",
    "admin_group": (zh_cn and "群管理") or "Group Admin",
    "admin_project": (zh_cn and "项目管理员") or "Project Admin",
    # Basic
    "action": (zh_cn and "执行操作") or "Action",
    "clear": (zh_cn and "清空数据") or "Clear Data",
    "colon": (zh_cn and "：") or ": ",
    "description": (zh_cn and "说明") or "Description",
    "disabled": (zh_cn and "禁用") or "Disabled",
    "enabled": (zh_cn and "启用") or "Enabled",
    "error": (zh_cn and "错误") or "Error",
    "reason": (zh_cn and "原因") or "Reason",
    "reset": (zh_cn and "重置数据") or "Reset Data",
    "rollback": (zh_cn and "数据回滚") or "Rollback",
    "status_error": (zh_cn and "出现错误") or "Error Occurred",
    "status_failed": (zh_cn and "未执行") or "Failed",
    "status_succeed": (zh_cn and "成功执行") or "Succeed",
    "type": (zh_cn and "类别") or "Type",
    "version": (zh_cn and "版本") or "Version",
    # Command
    "command_lack": (zh_cn and "命令参数缺失") or "Lack of Parameter",
    "command_para": (zh_cn and "命令参数有误") or "Incorrect Command Parameter",
    "command_type": (zh_cn and "命令类别有误") or "Incorrect Command Type",
    "command_usage": (zh_cn and "用法有误") or "Incorrect Usage",
    # Data
    "blacklist_ids": (zh_cn and "黑名单") or "Blacklist",
    "flood_ids": (zh_cn and "刷屏名单") or "Flood ID",
    "message_ids": (zh_cn and "消息 ID") or "Message ID",
    # Emergency
    "issue": (zh_cn and "发现状况") or "Issue",
    "exchange_invalid": (zh_cn and "数据交换频道失效") or "Exchange Channel Invalid",
    "auto_fix": (zh_cn and "自动处理") or "Auto Fix",
    "protocol_1": (zh_cn and "启动 1 号协议") or "Initiate Protocol 1",
    "transfer_channel": (zh_cn and "频道转移") or "Transfer Channel",
    "emergency_channel": (zh_cn and "应急频道") or "Emergency Channel",
    # Group
    "reason_none": (zh_cn and "无数据") or "No Data",
    # Record
    "project": (zh_cn and "项目编号") or "Project",
    "project_origin": (zh_cn and "原始项目") or "Original Project",
    "status": (zh_cn and "状态") or "Status",
    "user_id": (zh_cn and "用户 ID") or "User ID",
    "level": (zh_cn and "操作等级") or "Level",
    "rule": (zh_cn and "规则") or "Rule",
    "message_type": (zh_cn and "消息类别") or "Message Type",
    "message_game": (zh_cn and "游戏标识") or "Game Short Name",
    "message_lang": (zh_cn and "消息语言") or "Message Language",
    "message_len": (zh_cn and "消息长度") or "Message Length",
    "message_freq": (zh_cn and "消息频率") or "Message Frequency",
    "user_score": (zh_cn and "用户得分") or "User Score",
    "user_bio": (zh_cn and "用户简介") or "User Bio",
    "user_name": (zh_cn and "用户昵称") or "User Name",
    "from_name": (zh_cn and "来源名称") or "Forward Name",
    "more": (zh_cn and "附加信息") or "Extra Info",
    # Special
    "action_block": (zh_cn and "拉黑用户") or "Block User",
    "action_direct": (zh_cn and "直接对话") or "Direct Chat",
    "action_forgive": (zh_cn and "解除限制") or "Forgive the User",
    "action_leave": (zh_cn and "退出对话") or "Leave Direct Chat",
    "action_limit": (zh_cn and "自动限制用户") or "Limit the User Automatically",
    "action_mention": (zh_cn and "查询用户") or "Mention User",
    "action_now": (zh_cn and "查看直接对话") or "Show Direct Chat",
    "action_recall": (zh_cn and "撤回消息") or "Recall Messages",
    "action_status_set": (zh_cn and "设定状态") or "Set the Status",
    "action_status_show": (zh_cn and "查看当前状态") or "Show the Status",
    "action_unblock": (zh_cn and "解禁用户") or "Unblock User",
    "chat_id": (zh_cn and "对话 ID") or "Chat ID",
    "description_choose_clear": (zh_cn and "请选择要清空的数据") or "Please Choose the Data to Clear",
    "description_choose_recall": (zh_cn and "请选择要撤回全部消息的类别") or "Please Choose the Messages to Recall",
    "description_direct": ((zh_cn and ("如需将消息转发给某人，"
                                       "请以 /direct 命令回复某条包含该用户 ID 的汇报消息，并转发消息给机器人\n"
                                       "注意：此时将开启与该用户的直接对话，您发送给机器人的任何消息都将发送给对方，"
                                       "而无需回复带该用户 ID 的汇报消息\n"
                                       "如欲退出与该用户的直接对话，请发送：/leave 指令\n")
                            or ("To forward a message to someone, "
                                "reply with a report message containing the user ID with the /direct command "
                                "and forward the message to the robot\n"
                                "Note: A direct conversation with the user will be initiated "
                                "and any messages you send to the bot will be sent to the user "
                                "without having to reply to the report message with that user ID\n"
                                "To quit a direct conversation with this user, please send: /leave command\n"))),
    "description_flood": ((zh_cn and ("您发送的消息过于频繁，请 {} 分钟后重试\n"
                                      "期间机器人将对您的消息不做任何转发和应答\n"))
                          or ("You sent messages too frequently. Please try again in {} minutes\n"
                              "During this time the bot will not forward and respond to your messages\n")),
    "description_forgive": ((zh_cn and "您已被手动解除等待的时间限制\n"
                                       "您现在可以正常发送消息\n")
                            or ("You have been manually lifted the waiting flood time restriction\n"
                                "You can now send messages\n")),
    "description_reply": ((zh_cn and "如需回复某人，请回复某条包含该用户 ID 的汇报消息")
                          or "To reply to someone, please reply to a report message containing the user's ID"),
    "mention_id": (zh_cn and "查询 ID") or "Mention ID",
    "message_all": (zh_cn and "全部对话消息") or "All Messages",
    "message_host": (zh_cn and "由您发送的消息") or "All Messages Sent by You",
    "reason_blacklist": (zh_cn and "该用户在黑名单中") or "The User is in the Blacklist",
    "reason_blocked": (zh_cn and "该用户已在黑名单中") or "The User is Already Blocked",
    "reason_no_direct": (zh_cn and "当前无直接对话") or "No Direct Chat",
    "reason_not_blocked": (zh_cn and "该用户不在黑名单中") or "The User is Not Blocked",
    "reason_not_limited": (zh_cn and "该用户未被限制") or "The User is Not Limited",
    "reason_recall": (zh_cn and "没有可撤回的消息") or "No Messages to Recall",
    "reason_stopped": (zh_cn and "对方已停用机器人") or "The User Stopped the Bot",
    "recall": (zh_cn and "撤回") or "Recall",
    "start_guest": ((zh_cn and ("欢迎使用\n"
                                "如您需要私聊 {}，您可以直接在此发送消息并等待回复\n"
                                "若您也想拥有自己的私聊机器人，请参照 {} 建立\n"))
                    or ("Welcome\n"
                        "If you need a private chat with {}, "
                        "you can send a message directly here and wait for a reply\n"
                        "If you want to have your own private chat bot, please refer to {}\n")),
    "start_host": ((zh_cn and ("您的传送信使已准备就绪\n"
                               "请勿停用机器人，否则无法收到他人的消息\n"
                               "关注 {} 可及时获取更新信息\n"))
                   or ("Your delivery messenger is ready\n"
                       "Don't disable the bot, otherwise you won't be able to receive messages from others\n"
                       "Follow {} for updates\n")),
    "status_delivered": (zh_cn and "已发送") or "Delivered",
    "status_edited": (zh_cn and "已编辑") or "Edited",
    "status_resent": (zh_cn and "已重新发送并撤回旧消息") or "Resent and Deleted the Old Message",
    "this_page": (zh_cn and "此页面") or "This Page",
    "to_id": (zh_cn and "发送至 ID") or "Delivered to ID",
    "user_status": (zh_cn and "对方状态") or "The User's Status"
}

# Init

all_commands: List[str] = [
    "block",
    "clear",
    "direct",
    "forgive",
    "leave",
    "mention",
    "now",
    "ping",
    "recall",
    "start",
    "status",
    "unblock",
    "version"
]

flood_ids: Dict[str, Union[Dict[int, List[float]], Set[int]]] = {
    "users": set(),
    "counts": {}
}
# flood_ids = {
#     "users": {12345678},
#     "counts": {
#           12345678: [1512345678.1234567]
#      }
# }

locks: Dict[str, Lock] = {
    "message": Lock()
}

media_group_ids: Set[int] = set()
# media_group_ids = {12556677123456789}

sender: str = "PM"

should_hide: bool = False

version: str = "0.4.6"

direct_chat: int = 0

# Load data from pickle

# Init dir
try:
    rmtree("tmp")
except Exception as e:
    logger.info(f"Remove tmp error: {e}")

for path in ["data", "tmp"]:
    if not exists(path):
        mkdir(path)

# Init ids variables

blacklist_ids: Set[int] = set()
# blacklist_ids = {12345678}

message_ids: Dict[int, Dict[str, Set[int]]] = {}
# message_ids = {
#     12345678: {
#         "guest": {123},
#         "host": {456}
#     }
# }

reply_ids: Dict[str, Dict[int, Tuple[int, int]]] = {
    "g2h": {},
    "h2g": {}
}
# reply_ids = {
#     "g2h": {
#         123: (124, 12345678)
#     },
#     "h2g": {
#         124: (123, 12345678)
#     }
# }

# Init data variables

status: str = ""

# Load data
file_list: List[str] = ["blacklist_ids", "message_ids", "reply_ids", "status"]
for file in file_list:
    try:
        try:
            if exists(f"data/{file}") or exists(f"data/.{file}"):
                with open(f"data/{file}", 'rb') as f:
                    locals()[f"{file}"] = pickle.load(f)
            else:
                with open(f"data/{file}", 'wb') as f:
                    pickle.dump(eval(f"{file}"), f)
        except Exception as e:
            logger.error(f"Load data {file} error: {e}", exc_info=True)
            with open(f"data/.{file}", 'rb') as f:
                locals()[f"{file}"] = pickle.load(f)
    except Exception as e:
        logger.critical(f"Load data {file} backup error: {e}", exc_info=True)
        raise SystemExit("[DATA CORRUPTION]")

# Start program
copyright_text = (f"SCP-079-{sender} v{version}, Copyright (C) 2019 SCP-079 <https://scp-079.org>\n"
                  "Licensed under the terms of the GNU General Public License v3 or later (GPLv3+)\n")
print(copyright_text)
