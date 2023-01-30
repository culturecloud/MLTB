from signal import signal, SIGINT
from os import path as ospath, remove as osremove, execl as osexecl
from subprocess import run as srun, check_output
from psutil import disk_usage, cpu_percent, swap_memory, cpu_count, virtual_memory, net_io_counters, boot_time
from time import time
from sys import executable
from telegram.ext import CommandHandler

from bot import bot, dispatcher, updater, botStartTime, IGNORE_PENDING_REQUESTS, LOGGER, Interval, \
                DATABASE_URL, app, main_loop, QbInterval, INCOMPLETE_TASK_NOTIFIER, config_dict
from .helper.ext_utils.fs_utils import start_cleanup, clean_all, exit_clean_up
from .helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time
from .helper.ext_utils.db_handler import DbManger
from .helper.telegram_helper.bot_commands import BotCommands
from .helper.telegram_helper.message_utils import sendMessage, editMessage, sendLogFile
from .helper.telegram_helper.filters import CustomFilters
from .helper.telegram_helper.button_build import ButtonMaker
from .modules import authorize, list, cancel_mirror, mirror_status, mirror_leech, clone, ytdlp, \
                     shell, eval, delete, count, users_settings, search, rss, bt_select, bot_settings


def stats(update, context):
    if ospath.exists('.git'):
        last_commit = check_output(["git log -1 --date=short --pretty=format:'%cd <b>From</b> %cr'"], shell=True).decode()
    else:
        last_commit = 'No UPSTREAM_REPO'
    total, used, free, disk = disk_usage('/')
    swap = swap_memory()
    memory = virtual_memory()
    stats = f'<b>Commit Date:</b> {last_commit}\n\n'\
            f'<b>Bot Uptime:</b> {get_readable_time(time() - botStartTime)}\n'\
            f'<b>OS Uptime:</b> {get_readable_time(time() - boot_time())}\n\n'\
            f'<b>Total Disk Space:</b> {get_readable_file_size(total)}\n'\
            f'<b>Used:</b> {get_readable_file_size(used)} | <b>Free:</b> {get_readable_file_size(free)}\n\n'\
            f'<b>Upload:</b> {get_readable_file_size(net_io_counters().bytes_sent)}\n'\
            f'<b>Download:</b> {get_readable_file_size(net_io_counters().bytes_recv)}\n\n'\
            f'<b>CPU:</b> {cpu_percent(interval=0.5)}%\n'\
            f'<b>RAM:</b> {memory.percent}%\n'\
            f'<b>DISK:</b> {disk}%\n\n'\
            f'<b>Physical Cores:</b> {cpu_count(logical=False)}\n'\
            f'<b>Total Cores:</b> {cpu_count(logical=True)}\n\n'\
            f'<b>SWAP:</b> {get_readable_file_size(swap.total)} | <b>Used:</b> {swap.percent}%\n'\
            f'<b>Memory Total:</b> {get_readable_file_size(memory.total)}\n'\
            f'<b>Memory Free:</b> {get_readable_file_size(memory.available)}\n'\
            f'<b>Memory Used:</b> {get_readable_file_size(memory.used)}\n'
    sendMessage(stats, context.bot, update.message)

def start(update, context):
    buttons = ButtonMaker()
    buttons.buildbutton("Repo", "https://www.github.com/anasty17/mirror-leech-telegram-bot")
    buttons.buildbutton("Owner", "https://www.github.com/anasty17")
    reply_markup = buttons.build_menu(2)
    if CustomFilters.authorized_user(update) or CustomFilters.authorized_chat(update):
        start_string = f'''
This bot can mirror all your links to Google Drive or to telegram!
Type /{BotCommands.HelpCommand} to get a list of available commands
'''
        sendMessage(start_string, context.bot, update.message, reply_markup)
    else:
        sendMessage('Not an Authorized user, deploy your own mirror-leech bot', context.bot, update.message, reply_markup)

def restart(update, context):
    restart_message = sendMessage("Restarting...", context.bot, update.message)
    if Interval:
        Interval[0].cancel()
        Interval.clear()
    if QbInterval:
        QbInterval[0].cancel()
        QbInterval.clear()
    clean_all()
    srun(["pkill", "-9", "-f", "gunicorn|aria2c|qbittorrent-nox|ffmpeg"])
    srun(["python3", "update.py"])
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_message.chat.id}\n{restart_message.message_id}\n")
    osexecl(executable, executable, "-m", "bot")

def ping(update, context):
    start_time = int(round(time() * 1000))
    reply = sendMessage("Starting Ping", context.bot, update.message)
    end_time = int(round(time() * 1000))
    editMessage(f'{end_time - start_time} ms', reply)

def log(update, context):
    sendLogFile(context.bot, update.message)

help_string = f'''
NOTE: Try each command without any argument to see more detalis.
/{BotCommands.MirrorCommand[0]} or /{BotCommands.MirrorCommand[1]}: Start mirroring to Google Drive.
/{BotCommands.ZipMirrorCommand[0]} or /{BotCommands.ZipMirrorCommand[1]}: Start mirroring and upload the file/folder compressed with zip extension.
/{BotCommands.UnzipMirrorCommand[0]} or /{BotCommands.UnzipMirrorCommand[1]}: Start mirroring and upload the file/folder extracted from any archive extension.
/{BotCommands.QbMirrorCommand[0]} or /{BotCommands.QbMirrorCommand[1]}: Start Mirroring to Google Drive using qBittorrent.
/{BotCommands.QbZipMirrorCommand[0]} or /{BotCommands.QbZipMirrorCommand[1]}: Start mirroring using qBittorrent and upload the file/folder compressed with zip extension.
/{BotCommands.QbUnzipMirrorCommand[0]} or /{BotCommands.QbUnzipMirrorCommand[1]}: Start mirroring using qBittorrent and upload the file/folder extracted from any archive extension.
/{BotCommands.YtdlCommand[0]} or /{BotCommands.YtdlCommand[1]}: Mirror yt-dlp supported link.
/{BotCommands.YtdlZipCommand[0]} or /{BotCommands.YtdlZipCommand[1]}: Mirror yt-dlp supported link as zip.
/{BotCommands.LeechCommand[0]} or /{BotCommands.LeechCommand[1]}: Start leeching to Telegram.
/{BotCommands.ZipLeechCommand[0]} or /{BotCommands.ZipLeechCommand[1]}: Start leeching and upload the file/folder compressed with zip extension.
/{BotCommands.UnzipLeechCommand[0]} or /{BotCommands.UnzipLeechCommand[1]}: Start leeching and upload the file/folder extracted from any archive extension.
/{BotCommands.QbLeechCommand[0]} or /{BotCommands.QbLeechCommand[1]}: Start leeching using qBittorrent.
/{BotCommands.QbZipLeechCommand[0]} or /{BotCommands.QbZipLeechCommand[1]}: Start leeching using qBittorrent and upload the file/folder compressed with zip extension.
/{BotCommands.QbUnzipLeechCommand[0]} or /{BotCommands.QbUnzipLeechCommand[1]}: Start leeching using qBittorrent and upload the file/folder extracted from any archive extension.
/{BotCommands.YtdlLeechCommand[0]} or /{BotCommands.YtdlLeechCommand[1]}: Leech yt-dlp supported link.
/{BotCommands.YtdlZipLeechCommand[0]} or /{BotCommands.YtdlZipLeechCommand[1]}: Leech yt-dlp supported link as zip.
/{BotCommands.CloneCommand} [drive_url]: Copy file/folder to Google Drive.
/{BotCommands.CountCommand} [drive_url]: Count file/folder of Google Drive.
/{BotCommands.DeleteCommand} [drive_url]: Delete file/folder from Google Drive (Only Owner & Sudo).
/{BotCommands.UserSetCommand} [query]: Users settings.
/{BotCommands.BotSetCommand} [query]: Bot settings.
/{BotCommands.BtSelectCommand}: Select files from torrents by gid or reply.
/{BotCommands.CancelMirror}: Cancel task by gid or reply.
/{BotCommands.CancelAllCommand} [query]: Cancel all [status] tasks.
/{BotCommands.ListCommand} [query]: Search in Google Drive(s).
/{BotCommands.SearchCommand} [query]: Search for torrents with API.
/{BotCommands.StatusCommand}: Shows a status of all the downloads.
/{BotCommands.StatsCommand}: Show stats of the machine where the bot is hosted in.
/{BotCommands.PingCommand}: Check how long it takes to Ping the Bot (Only Owner & Sudo).
/{BotCommands.AuthorizeCommand}: Authorize a chat or a user to use the bot (Only Owner & Sudo).
/{BotCommands.UnAuthorizeCommand}: Unauthorize a chat or a user to use the bot (Only Owner & Sudo).
/{BotCommands.UsersCommand}: show users settings (Only Owner & Sudo).
/{BotCommands.AddSudoCommand}: Add sudo user (Only Owner).
/{BotCommands.RmSudoCommand}: Remove sudo users (Only Owner).
/{BotCommands.RestartCommand}: Restart and update the bot (Only Owner & Sudo).
/{BotCommands.LogCommand}: Get a log file of the bot. Handy for getting crash reports (Only Owner & Sudo).
/{BotCommands.ShellCommand}: Run shell commands (Only Owner).
/{BotCommands.EvalCommand}: Run Python Code Line | Lines (Only Owner).
/{BotCommands.ExecCommand}: Run Commands In Exec (Only Owner).
/{BotCommands.ClearLocalsCommand}: Clear {BotCommands.EvalCommand} or {BotCommands.ExecCommand} locals (Only Owner).
/{BotCommands.RssListCommand[0]} or /{BotCommands.RssListCommand[1]}: List all subscribed rss feed info (Only Owner & Sudo).
/{BotCommands.RssGetCommand[0]} or /{BotCommands.RssGetCommand[1]}: Force fetch last N links (Only Owner & Sudo).
/{BotCommands.RssSubCommand[0]} or /{BotCommands.RssSubCommand[1]}: Subscribe new rss feed (Only Owner & Sudo).
/{BotCommands.RssUnSubCommand[0]} or /{BotCommands.RssUnSubCommand[1]}: Unubscribe rss feed by title (Only Owner & Sudo).
/{BotCommands.RssSettingsCommand[0]} or /{BotCommands.RssSettingsCommand[1]} [query]: Rss Settings (Only Owner & Sudo).
'''

def bot_help(update, context):
    sendMessage(help_string, context.bot, update.message)

if config_dict['SET_BOT_COMMANDS']:
    botcmds = [
        (f'{BotCommands.MirrorCommand[0]}', 'Mirror'),
        (f'{BotCommands.ZipMirrorCommand[0]}','Mirror and upload as zip'),
        (f'{BotCommands.UnzipMirrorCommand[0]}','Mirror and extract files'),
        (f'{BotCommands.QbMirrorCommand[0]}','Mirror torrent using qBittorrent'),
        (f'{BotCommands.QbZipMirrorCommand[0]}','Mirror torrent and upload as zip using qb'),
        (f'{BotCommands.QbUnzipMirrorCommand[0]}','Mirror torrent and extract files using qb'),
        (f'{BotCommands.YtdlCommand[0]}','Mirror yt-dlp supported link'),
        (f'{BotCommands.YtdlZipCommand[0]}','Mirror yt-dlp supported link as zip'),
        (f'{BotCommands.CloneCommand}','Copy file/folder to Drive'),
        (f'{BotCommands.LeechCommand[0]}','Leech'),
        (f'{BotCommands.ZipLeechCommand[0]}','Leech and upload as zip'),
        (f'{BotCommands.UnzipLeechCommand[0]}','Leech and extract files'),
        (f'{BotCommands.QbLeechCommand[0]}','Leech torrent using qBittorrent'),
        (f'{BotCommands.QbZipLeechCommand[0]}','Leech torrent and upload as zip using qb'),
        (f'{BotCommands.QbUnzipLeechCommand[0]}','Leech torrent and extract using qb'),
        (f'{BotCommands.YtdlLeechCommand[0]}','Leech yt-dlp supported link'),
        (f'{BotCommands.YtdlZipLeechCommand[0]}','Leech yt-dlp supported link as zip'),
        (f'{BotCommands.CountCommand}','Count file/folder of Drive'),
        (f'{BotCommands.DeleteCommand}','Delete file/folder from Drive'),
        (f'{BotCommands.CancelMirror}','Cancel a task'),
        (f'{BotCommands.CancelAllCommand}','Cancel all downloading tasks'),
        (f'{BotCommands.ListCommand}','Search in Drive'),
        (f'{BotCommands.SearchCommand}','Search in Torrent'),
        (f'{BotCommands.UserSetCommand}','Users settings'),
        (f'{BotCommands.BotSetCommand}','BOT settings'),
        (f'{BotCommands.StatusCommand}','Get mirror status message'),
        (f'{BotCommands.PingCommand}','Ping the bot'),
        (f'{BotCommands.RestartCommand}','Restart the bot'),
        (f'{BotCommands.LogCommand}','Get the bot Log'),
        (f'{BotCommands.HelpCommand}','Get detailed help')
    ]

def main():
    if config_dict['SET_BOT_COMMANDS']:
        bot.set_my_commands(botcmds)
    start_cleanup()
    if INCOMPLETE_TASK_NOTIFIER and DATABASE_URL:
        if notifier_dict := DbManger().get_incomplete_tasks():
            for cid, data in notifier_dict.items():
                if ospath.isfile(".restartmsg"):
                    with open(".restartmsg") as f:
                        chat_id, msg_id = map(int, f)
                    msg = 'Restarted Successfully!'
                else:
                    msg = 'Bot Restarted!'
                for tag, links in data.items():
                    msg += f"\n\n{tag}: "
                    for index, link in enumerate(links, start=1):
                        msg += f" <a href='{link}'>{index}</a> |"
                        if len(msg.encode()) > 4000:
                            if 'Restarted Successfully!' in msg and cid == chat_id:
                                try:
                                    bot.editMessageText(msg, chat_id, msg_id)
                                except:
                                    pass
                                osremove(".restartmsg")
                            else:
                                try:
                                    bot.sendMessage(cid, msg)
                                except Exception as e:
                                    LOGGER.error(e)
                            msg = ''
                if 'Restarted Successfully!' in msg and cid == chat_id:
                    try:
                        bot.editMessageText(msg, chat_id, msg_id)
                    except:
                        pass
                    osremove(".restartmsg")
                else:
                    try:
                        bot.sendMessage(cid, msg)
                    except Exception as e:
                        LOGGER.error(e)

    if ospath.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        try:
            bot.edit_message_text("Restarted Successfully!", chat_id, msg_id)
        except:
            pass
        osremove(".restartmsg")

    start_handler = CommandHandler(BotCommands.StartCommand, start)
    log_handler = CommandHandler(BotCommands.LogCommand, log,
                                        filters=CustomFilters.owner_filter | CustomFilters.sudo_user)
    restart_handler = CommandHandler(BotCommands.RestartCommand, restart,
                                        filters=CustomFilters.owner_filter | CustomFilters.sudo_user)
    ping_handler = CommandHandler(BotCommands.PingCommand, ping,
                               filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
    help_handler = CommandHandler(BotCommands.HelpCommand, bot_help,
                               filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
    stats_handler = CommandHandler(BotCommands.StatsCommand, stats,
                               filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(ping_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(stats_handler)
    dispatcher.add_handler(log_handler)

    updater.start_polling(drop_pending_updates=IGNORE_PENDING_REQUESTS)
    LOGGER.info("Bot Started!")
    signal(SIGINT, exit_clean_up)

app.start()
main()

main_loop.run_forever()
