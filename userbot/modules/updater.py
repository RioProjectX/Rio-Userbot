"""
This module updates the userbot based on upstream revision
"""

import asyncio
import sys
from os import environ, execle, remove

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError

from userbot import CMD_HANDLER as cmd
from userbot import CMD_HELP, HEROKU_API_KEY, HEROKU_APP_NAME, UPSTREAM_REPO_URL, bot
from userbot.events import man_cmd


async def gen_chlog(repo, diff):
    d_form = "%d/%m/%y"
    return "".join(
        f"• [{c.committed_datetime.strftime(d_form)}]: {c.summary} <{c.author}>\n"
        for c in repo.iter_commits(diff)
    )


async def print_changelogs(event, ac_br, changelog):
    changelog_str = (
        f"**✥ Tersedia Pembaruan Untuk [{ac_br}] :\n\n✥ Pembaruan:**\n`{changelog}`"
    )
    if len(changelog_str) > 4096:
        await event.edit("**Changelog terlalu besar, dikirim sebagai file.**")
        with open("output.txt", "w+") as file:
            file.write(changelog_str)
        await event.client.send_file(event.chat_id, "output.txt")
        remove("output.txt")
    else:
        await event.client.send_message(event.chat_id, changelog_str)
    return True


async def deploy(event, repo, ups_rem, ac_br, txt):
    if HEROKU_API_KEY is not None:
        import heroku3

        heroku = heroku3.from_key(HEROKU_API_KEY)
        heroku_app = None
        heroku_applications = heroku.apps()
        if HEROKU_APP_NAME is None:
            await event.edit(
                "**[HEROKU]: Harap Tambahkan Variabel** `HEROKU_APP_NAME` "
                " **untuk deploy perubahan terbaru dari Userbot.**"
            )
            repo.__del__()
            return
        for app in heroku_applications:
            if app.name == HEROKU_APP_NAME:
                heroku_app = app
                break
        if heroku_app is None:
            await event.edit(
                f"{txt}\n"
                "**Kredensial Heroku tidak valid untuk deploy Man-Userbot dyno.**"
            )
            return repo.__del__()
        try:
            from userbot.modules.sql_helper.globals import addgvar, delgvar

            delgvar("restartstatus")
            addgvar("restartstatus", f"{event.chat_id}\n{event.id}")
        except AttributeError:
            pass
        ups_rem.fetch(ac_br)
        repo.git.reset("--hard", "FETCH_HEAD")
        heroku_git_url = heroku_app.git_url.replace(
            "https://", "https://api:" + HEROKU_API_KEY + "@"
        )
        if "heroku" in repo.remotes:
            remote = repo.remote("heroku")
            remote.set_url(heroku_git_url)
        else:
            remote = repo.create_remote("heroku", heroku_git_url)
        try:
            remote.push(refspec="HEAD:refs/heads/master", force=True)
        except Exception as error:
            await event.edit(f"{txt}\n**Terjadi Kesalahan Di Log:**\n`{error}`")
            return repo.__del__()
        build = heroku_app.builds(order_by="created_at", sort="desc")[0]
        if build.status == "failed":
            await event.edit("**Build Gagal!** Dibatalkan karena ada beberapa error.`")
            await asyncio.sleep(5)
            return await event.delete()
        await event.edit(
            "`Man-Userbot Berhasil Di Deploy! Userbot bisa di gunakan kembali.`"
        )

    else:
        await event.edit("**[HEROKU]: Harap Tambahkan Variabel** `HEROKU_API_KEY`")
        await asyncio.sleep(10)
        await event.delete()
    return


async def update(event, repo, ups_rem, ac_br):
    try:
        ups_rem.pull(ac_br)
    except GitCommandError:
        repo.git.reset("--hard", "FETCH_HEAD")
    await event.edit("`Man-Userbot Berhasil Diupdate! Userbot bisa di Gunakan Lagi.`")

    try:
        from userbot.modules.sql_helper.globals import addgvar, delgvar

        delgvar("restartstatus")
        addgvar("restartstatus", f"{event.chat_id}\n{event.id}")
    except AttributeError:
        pass

    # Spin a new instance of bot
    args = [sys.executable, "-m", "userbot"]
    execle(sys.executable, *args, environ)


@bot.on(man_cmd(outgoing=True, pattern=r"update( now| deploy|$)"))
async def upstream(event):
    "For .update command, check if the bot is up to date, update if specified"
    await event.edit("`Mengecek Pembaruan, Tunggu Sebentar...`")
    conf = event.pattern_match.group(1).strip()
    off_repo = UPSTREAM_REPO_URL
    force_update = False
    try:
        txt = "**Pembaruan Tidak Dapat Di Lanjutkan Karna "
        txt += "Terjadi Beberapa ERROR**\n\n**LOGTRACE:**\n"
        repo = Repo()
    except NoSuchPathError as error:
        await event.edit(f"{txt}\n**Directory** `{error}` **Tidak Dapat Di Temukan.**")
        return repo.__del__()
    except GitCommandError as error:
        await event.edit(f"{txt}\n**Kegagalan awal!** `{error}`")
        return repo.__del__()
    except InvalidGitRepositoryError as error:
        if conf is None:
            return await event.edit(
                f"**Sayangnya, Directory {error} Tampaknya Bukan Dari Repo."
                "\nTapi Kita Bisa Memperbarui Paksa Userbot Menggunakan** `.update deploy`"
            )
        repo = Repo.init()
        origin = repo.create_remote("upstream", off_repo)
        origin.fetch()
        force_update = True
        repo.create_head("master", origin.refs.master)
        repo.heads.master.set_tracking_branch(origin.refs.master)
        repo.heads.master.checkout(True)

    ac_br = repo.active_branch.name
    try:
        repo.create_remote("upstream", off_repo)
    except BaseException:
        pass

    ups_rem = repo.remote("upstream")
    ups_rem.fetch(ac_br)

    changelog = await gen_chlog(repo, f"HEAD..upstream/{ac_br}")
    if conf == "deploy":
        await event.edit("`[HEROKU]: Update Deploy Man-Userbot Sedang Dalam Proses...`")
        await deploy(event, repo, ups_rem, ac_br, txt)
        return

    if changelog == "" and not force_update:
        await event.edit("**✥ Man-Userbot Sudah Versi Terbaru**")
        await asyncio.sleep(15)
        await event.delete()
        return repo.__del__()

    if conf == "" and not force_update:
        await print_changelogs(event, ac_br, changelog)
        await event.delete()
        return await event.respond(
            "**Ketik** `.update deploy` **untuk Mengupdate Userbot.**"
        )

    if force_update:
        await event.edit(
            "**Sinkronisasi Paksa Ke Kode Userbot Terbaru, Harap Tunggu...**"
        )

    if conf == "now":
        for commit in changelog.splitlines():
            if (
                commit.startswith("- [NQ]")
                and HEROKU_APP_NAME is not None
                and HEROKU_API_KEY is not None
            ):
                return await event.edit(
                    "**Quick update telah dinonaktifkan untuk pembaruan ini; "
                    "Gunakan** `.update deploy` **sebagai gantinya.**"
                )
        await event.edit("**Perfoming a quick update, please wait...**")
        await update(event, repo, ups_rem, ac_br)

    return


CMD_HELP.update(
    {
        "update": f"**Plugin : **`update`\
        \n\n  •  **Syntax :** `{cmd}update`\
        \n  •  **Function : **Untuk Melihat Pembaruan Terbaru Man-Userbot.\
        \n\n  •  **Syntax :** `{cmd}update deploy`\
        \n  •  **Function : **Untuk MengUpdate Fitur Terbaru Dari Man-Userbot.\
    "
    }
)
