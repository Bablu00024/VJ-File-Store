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
            share_link = f"{WEBSITE_URL}?POCKETAUDIO=BATCH-{file_id}"
        else:
            share_link = f"https://t.me/{username}?start=BATCH-{file_id}"

        if user["base_site"] and user["shortener_api"] != None:
            short_link = await get_short_link(user, share_link)
            reply_texts.append(
                f"<b>⭕ Batch {batch_number} created!\nContains `{og_msg}` files.\n🖇️ Short link: {short_link}</b>"
            )
            summary_rows.append(short_link)
        else:
            reply_texts.append(
                f"<b>⭕ Batch {batch_number} created!\nContains `{og_msg}` files.\n🔗 Original link: {share_link}</b>"
            )
            summary_rows.append(share_link)

        batch_number += 1

    final_output = "\n\n".join(reply_texts)
    if summary_rows:
        summary_table = "\n".join(summary_rows)
        final_output += f"\n\n<b>📋 Summary Table</b>\n<pre>{summary_table}</pre>"

    await message.reply(final_output)
