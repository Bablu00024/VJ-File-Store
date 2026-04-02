# Don't Remove Credit @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import re
from pyrogram import filters, Client, enums
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, UsernameInvalid, UsernameNotModified
from config import ADMINS, LOG_CHANNEL, PUBLIC_FILE_STORE, WEBSITE_URL, WEBSITE_URL_MODE
from plugins.users_api import get_user, get_short_link
import os
import json
import base64

async def allowed(_, __, message):
    if PUBLIC_FILE_STORE:
        return True
    if message.from_user and message.from_user.id in ADMINS:
        return True
    return False

@Client.on_message((filters.document | filters.video | filters.audio) & filters.private & filters.create(allowed))
async def incoming_gen_link(bot, message):
    username = (await bot.get_me()).username
    file_type = message.media
    post = await message.copy(LOG_CHANNEL)
    file_id = str(post.id)
    string = 'file_' + file_id
    outstr = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")
    user_id = message.from_user.id
    user = await get_user(user_id)
    if WEBSITE_URL_MODE == True:
        share_link = f"{WEBSITE_URL}?POCKETAUDIO={outstr}"
    else:
        share_link = f"https://t.me/{username}?start={outstr}"
    if user["base_site"] and user["shortener_api"] != None:
        short_link = await get_short_link(user, share_link)
        await message.reply(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\n🖇️ sʜᴏʀᴛ ʟɪɴᴋ :- {short_link}</b>")
    else:
        await message.reply(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\n🔗 ᴏʀɪɢɪɴᴀʟ ʟɪɴᴋ :- {share_link}</b>")

@Client.on_message(filters.command(['link']) & filters.create(allowed))
async def gen_link_s(bot, message):
    username = (await bot.get_me()).username
    replied = message.reply_to_message
    if not replied:
        return await message.reply('Reply to a message to get a shareable link.')
    post = await replied.copy(LOG_CHANNEL)
    file_id = str(post.id)
    string = f"file_{file_id}"
    outstr = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")
    user_id = message.from_user.id
    user = await get_user(user_id)
    if WEBSITE_URL_MODE == True:
        share_link = f"{WEBSITE_URL}?POCKETAUDIO={outstr}"
    else:
        share_link = f"https://t.me/{username}?start={outstr}"
    if user["base_site"] and user["shortener_api"] != None:
        short_link = await get_short_link(user, share_link)
        await message.reply(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\n🖇️ sʜᴏʀᴛ ʟɪɴᴋ :- {short_link}</b>")
    else:
        await message.reply(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\n🔗 ᴏʀɪɢɪɴᴀʟ ʟɪɴᴋ :- {share_link}</b>")

# -------------------------
# UPDATED MULTI-RANGE /batch HANDLER
# -------------------------
@Client.on_message(filters.command(['batch']) & filters.create(allowed))
async def gen_link_batch(bot, message):
    username = (await bot.get_me()).username
    links = message.text.strip().split()

    if len(links) < 3 or (len(links) - 1) % 2 != 0:
        return await message.reply(
            "Use correct format.\n"
            "Example:\n"
            "/batch <first_link> <last_link> [<first_link> <last_link> ...]"
        )

    regex = re.compile("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
    reply_texts = []
    summary_rows = []
    batch_number = 1

    for i in range(1, len(links), 2):
        first, last = links[i], links[i+1]

        match = regex.match(first)
        if not match:
            reply_texts.append(f"❌ Batch {batch_number}: Invalid first link")
            batch_number += 1
            continue
        f_chat_id = match.group(4)
        f_msg_id = int(match.group(5))
        if f_chat_id.isnumeric():
            f_chat_id = int("-100" + f_chat_id)

        match = regex.match(last)
        if not match:
            reply_texts.append(f"❌ Batch {batch_number}: Invalid last link")
            batch_number += 1
            continue
        l_chat_id = match.group(4)
        l_msg_id = int(match.group(5))
        if l_chat_id.isnumeric():
            l_chat_id = int("-100" + l_chat_id)

        if f_chat_id != l_chat_id:
            reply_texts.append(f"❌ Batch {batch_number}: Chat IDs not matched.")
            batch_number += 1
            continue

        try:
            chat_id = (await bot.get_chat(f_chat_id)).id
        except ChannelInvalid:
            reply_texts.append(f"❌ Batch {batch_number}: Private channel/group. Make me admin.")
            batch_number += 1
            continue
        except (UsernameInvalid, UsernameNotModified):
            reply_texts.append(f"❌ Batch {batch_number}: Invalid link specified.")
            batch_number += 1
            continue
        except Exception as e:
            reply_texts.append(f"❌ Batch {batch_number}: Error: {e}")
            batch_number += 1
            continue

        outlist = []
        og_msg = 0
        async for msg in bot.iter_messages(f_chat_id, l_msg_id, f_msg_id):
            if msg.empty or msg.service:
                continue
            file = {"channel_id": f_chat_id, "msg_id": msg.id}
            og_msg += 1
            outlist.append(file)

        if not outlist:
            reply_texts.append(f"❌ Batch {batch_number}: No files found.")
            batch_number += 1
            continue

        with open(f"batchmode_{message.from_user.id}.json", "w+") as out:
            json.dump(outlist, out)
        post = await bot.send_document(
            LOG_CHANNEL,
            f"batchmode_{message.from_user.id}.json",
            file_name="Batch.json",
            caption="⚠️ Batch Generated For Filestore."
        )
        os.remove(f"batchmode_{message.from_user.id}.json")

        string = str(post.id)
        file_id = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")
        user_id = message.from_user.id
        user = await get_user(user_id)

        if WEBSITE_URL_MODE == True:
            share_link = f"{WEBSITE_URL}?POCKETAUDIO-{file_id}"
        else:
            share_link = f"https://t.me/{username}?start=BATCH-{file_id}"

        if user["base_site"] and user["shortener_api"] != None:
            short_link = await get_short_link(user, share_link)
            reply_texts.append(
                f"<b>⭕ Batch {batch_number} created!\nContains `{og_msg}` files.\n🖇️ Short link: {short_link}</b>"
            )
            summary_rows.append(f"Batch {batch_number} | {og_msg} files | {short_link}")
        else:
            reply_texts.append(
                f"<b>⭕ Batch {batch_number} created!\nContains `{og_msg}` files.\n🔗 Original link: {share_link}</b>"
            )
            summary_rows.append(f"Batch {batch_number} | {og_msg} files | {share_link}")

        batch_number += 1

    final_output = "\n\n".join(reply_texts)
    if summary_rows:
        summary_table = "\n".join(summary_rows)
        final_output += f"\n\n<b>📋 Summary Table</b>\n<pre>{summary_table}</pre>"

    await message.reply(final_output)

# -------------------------
# NEW /start HANDLER FOR BATCH LINKS
# -------------------------
Here’s the **fully integrated `genlink.py` file** with everything wired together — your `/link`, updated `/batch`, and the new `/start` handler that makes the `=BATCH` links actually deliver files:

```python
# Don't Remove Credit @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import re
from pyrogram import filters, Client, enums
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, UsernameInvalid, UsernameNotModified
from config import ADMINS, LOG_CHANNEL, PUBLIC_FILE_STORE, WEBSITE_URL, WEBSITE_URL_MODE
from plugins.users_api import get_user, get_short_link
import os
import json
import base64

async def allowed(_, __, message):
    if PUBLIC_FILE_STORE:
        return True
    if message.from_user and message.from_user.id in ADMINS:
        return True
    return False

# -------------------------
# SINGLE FILE LINK HANDLER
# -------------------------
@Client.on_message((filters.document | filters.video | filters.audio) & filters.private & filters.create(allowed))
async def incoming_gen_link(bot, message):
    username = (await bot.get_me()).username
    post = await message.copy(LOG_CHANNEL)
    file_id = str(post.id)
    string = 'file_' + file_id
    outstr = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")
    user_id = message.from_user.id
    user = await get_user(user_id)
    if WEBSITE_URL_MODE:
        share_link = f"{WEBSITE_URL}?POCKETAUDIO={outstr}"
    else:
        share_link = f"https://t.me/{username}?start={outstr}"
    if user["base_site"] and user["shortener_api"] != None:
        short_link = await get_short_link(user, share_link)
        await message.reply(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\n🖇️ sʜᴏʀᴛ ʟɪɴᴋ :- {short_link}</b>")
    else:
        await message.reply(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\n🔗 ᴏʀɪɢɪɴᴀʟ ʟɪɴᴋ :- {share_link}</b>")

@Client.on_message(filters.command(['link']) & filters.create(allowed))
async def gen_link_s(bot, message):
    username = (await bot.get_me()).username
    replied = message.reply_to_message
    if not replied:
        return await message.reply('Reply to a message to get a shareable link.')
    post = await replied.copy(LOG_CHANNEL)
    file_id = str(post.id)
    string = f"file_{file_id}"
    outstr = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")
    user_id = message.from_user.id
    user = await get_user(user_id)
    if WEBSITE_URL_MODE:
        share_link = f"{WEBSITE_URL}?POCKETAUDIO={outstr}"
    else:
        share_link = f"https://t.me/{username}?start={outstr}"
    if user["base_site"] and user["shortener_api"] != None:
        short_link = await get_short_link(user, share_link)
        await message.reply(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\n🖇️ sʜᴏʀᴛ ʟɪɴᴋ :- {short_link}</b>")
    else:
        await message.reply(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\n🔗 ᴏʀɪɢɪɴᴀʟ ʟɪɴᴋ :- {share_link}</b>")

# -------------------------
# MULTI-RANGE /batch HANDLER
# -------------------------
@Client.on_message(filters.command(['batch']) & filters.create(allowed))
async def gen_link_batch(bot, message):
    username = (await bot.get_me()).username
    links = message.text.strip().split()

    if len(links) < 3 or (len(links) - 1) % 2 != 0:
        return await message.reply(
            "Use correct format.\n"
            "Example:\n"
            "/batch <first_link> <last_link> [<first_link> <last_link> ...]"
        )

    regex = re.compile("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
    reply_texts = []
    summary_rows = []
    batch_number = 1

    for i in range(1, len(links), 2):
        first, last = links[i], links[i+1]

        match = regex.match(first)
        if not match:
            reply_texts.append(f"❌ Batch {batch_number}: Invalid first link")
            batch_number += 1
            continue
        f_chat_id = match.group(4)
        f_msg_id = int(match.group(5))
        if f_chat_id.isnumeric():
            f_chat_id = int("-100" + f_chat_id)

        match = regex.match(last)
        if not match:
            reply_texts.append(f"❌ Batch {batch_number}: Invalid last link")
            batch_number += 1
            continue
        l_chat_id = match.group(4)
        l_msg_id = int(match.group(5))
        if l_chat_id.isnumeric():
            l_chat_id = int("-100" + l_chat_id)

        if f_chat_id != l_chat_id:
            reply_texts.append(f"❌ Batch {batch_number}: Chat IDs not matched.")
            batch_number += 1
            continue

        try:
            chat_id = (await bot.get_chat(f_chat_id)).id
        except ChannelInvalid:
            reply_texts.append(f"❌ Batch {batch_number}: Private channel/group. Make me admin.")
            batch_number += 1
            continue
        except (UsernameInvalid, UsernameNotModified):
            reply_texts.append(f"❌ Batch {batch_number}: Invalid link specified.")
            batch_number += 1
            continue
        except Exception as e:
            reply_texts.append(f"❌ Batch {batch_number}: Error: {e}")
            batch_number += 1
            continue

        outlist = []
        og_msg = 0
        async for msg in bot.iter_messages(f_chat_id, l_msg_id, f_msg_id):
            if msg.empty or msg.service:
                continue
            file = {"channel_id": f_chat_id, "msg_id": msg.id}
            og_msg += 1
            outlist.append(file)

        if not outlist:
            reply_texts.append(f"❌ Batch {batch_number}: No files found.")
            batch_number += 1
            continue

        with open(f"batchmode_{message.from_user.id}.json", "w+") as out:
            json.dump(outlist, out)
        post = await bot.send_document(
            LOG_CHANNEL,
            f"batchmode_{message.from_user.id}.json",
            file_name="Batch.json",
            caption="⚠️ Batch Generated For Filestore."
        )
        os.remove(f"batchmode_{message.from_user.id}.json")

        string = str(post.id)
        file_id = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")
        user_id = message.from_user.id
        user = await get_user(user_id)

        if WEBSITE_URL_MODE:
            share_link = f"{WEBSITE_URL}?POCKETAUDIO-{file_id}"
        else:
            share_link = f"https://t.me/{username}?start=BATCH-{file_id}"

        if user["base_site"] and user["shortener_api"] != None:
            short_link = await get_short_link(user, share_link)
            reply_texts.append(
                f"<b>⭕ Batch {batch_number} created!\nContains `{og_msg}` files.\n🖇️ Short link: {short_link}</b>"
            )
            summary_rows.append(f"Batch {batch_number} | {og_msg} files | {short_link}")
        else:
            reply_texts.append(
                f"<b>⭕ Batch {batch_number} created!\nContains `{og_msg}` files.\n🔗 Original link: {share_link}</b>"
            )
            summary_rows.append(f"Batch {batch_number} | {og_msg} files | {share_link}")

        batch_number += 1

    final_output = "\n\n".join(reply_texts)
    if summary_rows:
        summary_table = "\n".join(summary_rows)
        final_output += f"\n\n<b>📋 Summary Table</b>\n<pre>{summary_table}</pre>"

    await message.reply(final_output)

# -------------------------
# NEW /start HANDLER FOR BATCH LINKS
# -------------------------
@Client.on_message(filters.command("start"))
async def start_handler(bot, message):
    args = message.text.split()
    if len(args) > 1 and "BATCH" in args[1]:
        batch_id
