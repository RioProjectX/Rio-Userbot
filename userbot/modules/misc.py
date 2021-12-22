# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#
# You can find misc modules, which dont fit in anything xD
#
# Recode by @mrismanaziz
# FROM Man-Userbot <https://github.com/mrismanaziz/Man-Userbot>
# t.me/SharingUserbot & t.me/Lunatic0de
#
""" Userbot module for other small commands. """

import io
import os
import re
import sys
import urllib
from os import environ, execle
from time import sleep

import requests
from bs4 import BeautifulSoup
from heroku3 import from_key
from PIL import Image

from userbot import BOT_VER, BOTLOG, BOTLOG_CHATID
from userbot import CMD_HANDLER as cmd
from userbot import CMD_HELP, HEROKU_API_KEY, HEROKU_APP_NAME, UPSTREAM_REPO_BRANCH, bot
from userbot.events import man_cmd
from userbot.utils import time_formatter

# ================= CONSTANT =================
HEROKU_APP = from_key(HEROKU_API_KEY).apps()[HEROKU_APP_NAME]
# ============================================

opener = urllib.request.build_opener()
useragent = "Mozilla/5.0 (Linux; Android 9; SM-G960F Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/78.0.3904.70 Mobile Safari/537.36"
opener.addheaders = [("User-agent", useragent)]


@bot.on(man_cmd(outgoing=True, pattern=r"sleep ([0-9]+)$"))
async def sleepybot(time):
    """For .sleep command, let the userbot snooze for a few second."""
    counter = int(time.pattern_match.group(1))
    await time.edit("`Saya mengantuk dan tertidur...`")
    if BOTLOG:
        str_counter = time_formatter(counter)
        await time.client.send_message(
            BOTLOG_CHATID,
            f"Anda menyuruh bot untuk tidur {str_counter}.",
        )
    sleep(counter)
    await time.edit("**Oke, saya sudah bangun sekarang.**")


@bot.on(man_cmd(outgoing=True, pattern=r"shutdown$"))
async def killdabot(event):
    if event.fwd_from:
        return
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            "**#SHUTDOWN** \n"
            "**Rio-Userbot** telah di matikan!\nJika ingin menghidupkan kembali silahkan buka heroku",
        )
    await event.edit("`Man-Userbot Berhasil di matikan!`")
    if HEROKU_APP is not None:
        HEROKU_APP.process_formation()["worker"].scale(0)
    else:
        sys.exit(0)


@bot.on(man_cmd(outgoing=True, pattern=r"restart$"))
async def killdabot(event):
    await event.edit("**Rio-Userbot Berhasil di Restart**")
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID, "#RESTART \n" "**Rio-Userbot Berhasil Di Restart**"
        )
    # Spin a new instance of bot
    args = [sys.executable, "-m", "userbot"]
    execle(sys.executable, *args, environ)


@bot.on(man_cmd(outgoing=True, pattern=r"readme$"))
async def reedme(e):
    await e.edit(
        @bot.on(man_cmd(outgoing=True, pattern=r"readme$"))
async def reedme(e):
    await e.edit(
        "**Berikut sesuatu untuk kamu baca:**\n"
        "\n✣ [Userbot Repo](https://github.com/rioprojectx/Rio-Userbot/blob/Rio-Userbot/README.md)"
        "\n✣ [Video Tutorial](https://youtu.be/tTDaPKsGC1I)"
        "\n✣ [List Variabel Heroku untuk Rio-Userbot](https://telegra.ph/List-Variabel-Heroku-untuk-Man-Userbot-09-22)"
        "\n✣ [Setup Guide - Basic](https://mrismanaziz.medium.com/cara-memasang-userbot-telegram-repo-man-userbot-deploy-di-heroku-c56d1f8b5537)"
        "\n✣ [Setup Guide - LastFM Module](https://telegra.ph/How-to-set-up-LastFM-module-for-Paperplane-userbot-11-02)"
    )


@bot.on(man_cmd(outgoing=True, pattern=r"repeat (.*)"))
async def repeat(rep):
    cnt, txt = rep.pattern_match.group(1).split(" ", 1)
    replyCount = int(cnt)
    toBeRepeated = txt

    replyText = toBeRepeated + "\n"

    for _ in range(replyCount - 1):
        replyText += toBeRepeated + "\n"

    await rep.edit(replyText)


@bot.on(man_cmd(outgoing=True, pattern=r"repo$"))
async def repo_is_here(wannasee):
    """For .repo command, just returns the repo URL."""
    await wannasee.edit(
        f"**Hai**, Saya Menggunakan 🔥 **Rio-Userbot** 🔥\n\n"
        f"      Special Thanks For Rio\n\n"
        f"✣ **Userbot Version :** `{BOT_VER}@{UPSTREAM_REPO_BRANCH}`\n"
        f"✣ **Group Support :** [Group](t.me/riogroupsupport)\n"
        f"✣ **Channel Man :** [Projects](t.me/Lunatic0de)\n"
        f"✣ **Owner Repo :** [Rio](t.me/fckualot)\n"
        f"✣ **Repo :** [Rio-Userbot](https://github.com/RioProjectX/Rio-Userbot)\n"
    )


@bot.on(man_cmd(outgoing=True, pattern=r"string$"))
async def repo_is_here(wannasee):
    """For .repo command, just returns the repo URL."""
    await wannasee.edit(
        "✥ **GET STRING SESSION TELEGRAM :** [KLIK DISINI](https://replit.com/@RioProjectX/stringen-2#main.py)\n"
    )


@bot.on(man_cmd(outgoing=True, pattern=r"raw$"))
async def raw(event):
    the_real_message = None
    reply_to_id = None
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        the_real_message = previous_message.stringify()
        reply_to_id = event.reply_to_msg_id
    else:
        the_real_message = event.stringify()
        reply_to_id = event.message.id
    with io.BytesIO(str.encode(the_real_message)) as out_file:
        out_file.name = "raw_message_data.txt"
        await event.edit("`Check the userbot log for the decoded message data !!`")
        await event.client.send_file(
            BOTLOG_CHATID,
            out_file,
            force_document=True,
            allow_cache=False,
            reply_to=reply_to_id,
            caption="**Inilah data pesan yang didecodekan !!**",
        )


@bot.on(man_cmd(outgoing=True, pattern=r"reverse(?: |$)(\d*)"))
async def okgoogle(img):
    """For .reverse command, Google search images and stickers."""
    if os.path.isfile("okgoogle.png"):
        os.remove("okgoogle.png")

    message = await img.get_reply_message()
    if message and message.media:
        photo = io.BytesIO()
        await bot.download_media(message, photo)
    else:
        await img.edit("**Harap Balas ke Gambar**")
        return

    if photo:
        await img.edit("`Processing...`")
        try:
            image = Image.open(photo)
        except OSError:
            await img.edit("**Gambar tidak di dukung**")
            return
        name = "okgoogle.png"
        image.save(name, "PNG")
        image.close()
        # https://stackoverflow.com/questions/23270175/google-reverse-image-search-using-post-request#28792943
        searchUrl = "https://www.google.com/searchbyimage/upload"
        multipart = {"encoded_image": (name, open(name, "rb")), "image_content": ""}
        response = requests.post(searchUrl, files=multipart, allow_redirects=False)
        fetchUrl = response.headers["Location"]

        if response != 400:
            await img.edit(
                "`Image successfully uploaded to Google. Maybe.`"
                "\n`Parsing source now. Maybe.`"
            )
        else:
            await img.edit("**Google told me to fuck off.**")
            return

        os.remove(name)
        match = await ParseSauce(fetchUrl + "&preferences?hl=en&fg=1#languages")
        guess = match["best_guess"]
        imgspage = match["similar_images"]

        if guess and imgspage:
            await img.edit(f"[{guess}]({fetchUrl})\n\n`Looking for images...`")
        else:
            await img.edit("**Tidak dapat menemukan apa pun.**")
            return

        lim = img.pattern_match.group(1) or 3
        images = await scam(match, lim)
        yeet = []
        for i in images:
            k = requests.get(i)
            yeet.append(k.content)
        try:
            await img.client.send_file(
                entity=await img.client.get_input_entity(img.chat_id),
                file=yeet,
                reply_to=img,
            )
        except TypeError:
            pass
        await img.edit(
            f"[{guess}]({fetchUrl})\n\n[Visually similar images]({imgspage})"
        )


async def ParseSauce(googleurl):
    """Parse/Scrape the HTML code for the info we want."""

    source = opener.open(googleurl).read()
    soup = BeautifulSoup(source, "html.parser")

    results = {"similar_images": "", "best_guess": ""}

    try:
        for similar_image in soup.findAll("input", {"class": "gLFyf"}):
            url = "https://www.google.com/search?tbm=isch&q=" + urllib.parse.quote_plus(
                similar_image.get("value")
            )
            results["similar_images"] = url
    except BaseException:
        pass

    for best_guess in soup.findAll("div", attrs={"class": "r5a77d"}):
        results["best_guess"] = best_guess.get_text()

    return results


async def scam(results, lim):

    single = opener.open(results["similar_images"]).read()
    decoded = single.decode("utf-8")

    imglinks = []
    counter = 0

    pattern = r"^,\[\"(.*[.png|.jpg|.jpeg])\",[0-9]+,[0-9]+\]$"
    oboi = re.findall(pattern, decoded, re.I | re.M)

    for imglink in oboi:
        counter += 1
        if counter < int(lim):
            imglinks.append(imglink)
        else:
            break

    return imglinks


@bot.on(man_cmd(outgoing=True, pattern=r"send (.*)"))
async def send(event):
    await event.edit("**Berhasil Mengirim pesan ini**")

    if not event.is_reply:
        return await event.edit("**Mohon Balas ke pesan yang ingin dikirim!**")

    chat = event.pattern_match.group(1)
    try:
        chat = int(chat)
    except ValueError:
        pass

    try:
        chat = await event.client.get_entity(chat)
    except (TypeError, ValueError):
        return await event.edit("**Link yang diberikan tidak valid!**")

    message = await event.get_reply_message()

    await event.client.send_message(entity=chat, message=message)
    await event.edit(f"**Berhasil Mengirim pesan ini ke** `{chat.title}`")


CMD_HELP.update(
    {
        "send": f"**Plugin : **`send`\
        \n\n  •  **Syntax :** `{cmd}send` <username/id>\
        \n  •  **Function : **Meneruskan pesan balasan ke obrolan tertentu tanpa tag Forwarded from. Bisa mengirim ke Group Chat atau ke Personal Message\
    "
    }
)

CMD_HELP.update(
    {
        "random": f"**Plugin : **`random`\
        \n\n  •  **Syntax :** `{cmd}random`\
        \n  •  **Function : **Dapatkan item acak dari daftar item. \
    "
    }
)

CMD_HELP.update(
    {
        "sleep": f"**Plugin : **`sleep`\
        \n\n  •  **Syntax :** `{cmd}sleep`\
        \n  •  **Function : **Biarkan Man-Userbot tidur selama beberapa detik \
    "
    }
)


CMD_HELP.update(
    {
        "repo": f"**Plugin : **`Repository Man-Userbot`\
        \n\n  •  **Syntax :** `{cmd}repo`\
        \n  •  **Function : **Menampilan link Repository Man-Userbot\
        \n\n  •  **Syntax :** `{cmd}string`\
        \n  •  **Function : **Menampilan link String Man-Userbot\
    "
    }
)


CMD_HELP.update(
    {
        "readme": f"**Plugin : **`Panduan Menggunakan userbot`\
        \n\n  •  **Syntax :** `{cmd}readme`\
        \n  •  **Function : **Menyediakan tautan untuk mengatur userbot dan modulnya\
    "
    }
)


CMD_HELP.update(
    {
        "restart": f"**Plugin : **`Restart Man-Userbot`\
        \n\n  •  **Syntax :** `{cmd}restart`\
        \n  •  **Function : **Untuk Merestart userbot.\
    "
    }
)


CMD_HELP.update(
    {
        "shutdown": f"**Plugin : **`shutdown`\
        \n\n  •  **Syntax :** `{cmd}shutdown`\
        \n  •  **Function : **Mematikan Userbot.\
    "
    }
)


CMD_HELP.update(
    {
        "raw": f"**Plugin : **`raw`\
        \n\n  •  **Syntax :** `{cmd}raw`\
        \n  •  **Function : **Dapatkan data berformat seperti JSON terperinci tentang pesan yang dibalas.\
    "
    }
)


CMD_HELP.update(
    {
        "repeat": f"**Plugin : **`repeat`\
        \n\n  •  **Syntax :** `{cmd}repeat`\
        \n  •  **Function : **Mengulangi teks untuk beberapa kali. Jangan bingung ini dengan spam tho.\
    "
    }
)
