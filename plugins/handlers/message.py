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

from pyrogram import Client, Filters

from .. import glovar
from ..functions.etc import bold, thread
from ..functions.deliver import deliver_guest_message, deliver_host_message, get_guest, send_message
from ..functions.filters import host_chat, limited_user
from ..functions.ids import add_id, count_id

# Enable logging
logger = logging.getLogger(__name__)


@Client.on_message(Filters.private & Filters.incoming & host_chat
                   & ~Filters.command(glovar.all_commands, glovar.prefix))
def deliver_to_guest(client, message):
    try:
        hid = message.chat.id
        mid = message.message_id
        cid = get_guest(message)
        if cid:
            thread(deliver_host_message, (client, message, cid))
        elif glovar.direct_chat:
            thread(deliver_host_message, (client, message, glovar.direct_chat))
        else:
            if glovar.direct_chat:
                text = "如需回复某人，请回复某条包含该用户 ID 的汇报消息"
            else:
                text = "如需在当前直接对话中另外回复某人，请回复某条包含该用户 ID 的汇报消息"

            thread(send_message, (client, hid, text, mid))
    except Exception as e:
        logger.warning(f"Deliver to guest error: {e}", exc_info=True)


@Client.on_message(Filters.private & Filters.incoming & ~host_chat & ~limited_user
                   & ~Filters.command(glovar.all_commands, glovar.prefix), group=0)
def deliver_to_host(client, message):
    try:
        thread(deliver_guest_message, (client, message))
    except Exception as e:
        logger.warning(f"Deliver to host error: {e}", exc_info=True)


@Client.on_message(Filters.private & Filters.incoming & ~host_chat & ~limited_user
                   & ~Filters.command(glovar.all_commands, glovar.prefix), group=1)
def count(client, message):
    try:
        # Count user's messages in 5 seconds
        cid = message.from_user.id
        counts = count_id(cid)
        if counts == 20:
            add_id(cid, 0, "flood")
            text = (f"您发送的消息过于频繁，请 {bold('15')} 分钟后重试\n"
                    f"期间机器人将对您的消息不做任何转发和应答")
            thread(send_message, (client, cid, text))
    except Exception as e:
        logger.warning(f"Count error: {e}", exc_info=True)