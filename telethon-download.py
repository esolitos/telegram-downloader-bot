import asyncio
import logging
import os

from telethon import TelegramClient, errors, types, sync
from telethonSession import getSession, saveSession, saveProgress, getProgress
from typing import Union

loop = asyncio.get_event_loop()


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def dl_progr(current, total):
    global pbar
    global prev_curr

    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    while total >= 1024 and unit_index < len(units) - 1:
        current /= 1024
        total /= 1024
        unit_index += 1
    print(
        f'Downloaded {current:.2f} {units[unit_index]} out of {total:.2f} {units[unit_index]}', end='\r')


def get_file_name(message: types.Message) -> Union[str, None]:
    filename = None
    if isinstance(message.media, types.MessageMediaDocument):
        for attr in message.media.document.attributes:
            if isinstance(attr, types.DocumentAttributeFilename):
                filename = attr.file_name
                break

    return filename


def get_dl_dir(message: types.Message, base_dir: str) -> str:
    msg_date = message.date.strftime('%Y%m%d')
    dldir = os.path.join(base_dir, msg_date)
    os.makedirs(dldir, mode=0o777, exist_ok=True)
    return dldir


async def download_media(client, msg: types.Message, directory: str) -> Union[str, None]:
    dldir = get_dl_dir(msg, directory)
    filename = get_file_name(msg)

    if filename and os.path.exists(os.path.join(dldir, filename)):
        logger.info(f'Already downloaded: "{filename}"')
        return None

    logger.info(f'Downloading "{filename or "N/A"}"')

    # downloaded = await fast_download(client, msg, download_folder=dldir)
    downloaded = await msg.download_media(file=dldir, progress_callback=dl_progr)
    # client.iter_download

    logger.info(f'Finished download of "{downloaded}"')

    return downloaded


async def main():
    global session_path

    from dotenv import load_dotenv
    if not load_dotenv():
        logger.info('No .env file found')

    # Your API ID and hash
    app_id = os.getenv("TELEGRAM_APP_ID")
    app_hash = os.getenv("TELEGRAM_APP_HASH")
    invite_link = os.getenv("TELEGRAM_CHANNEL_INVITE_LINK")
    download_dir = os.getenv("TELEGRAM_DOWNLOAD_DIR")
    limit = int(os.getenv("DOWNLOAD_LIMIT", 10))

    session_path = os.getenv("TELEGRAM_DAEMON_SESSION_PATH", "./")

    if not app_id or not app_hash or not invite_link or not download_dir:
        logger.fatal('Missing environment variables')
        return

    # Creating the client and connecting
    async with TelegramClient(getSession(session_path), api_id=app_id, api_hash=app_hash, receive_updates=False) as client:
        saveSession(client.session, session_path)
        await client.start()

        private_info = await client.get_input_entity(invite_link)
        logger.debug(private_info.stringify())

        channel = await client.get_entity(private_info.channel_id)
        logger.debug(channel.stringify())

        try:
            async with client.takeout() as takeout:
                newer_than_id = int(getProgress(session_path) or 0)
                async for message in takeout.iter_messages(
                    channel,
                    wait_time=0,
                    limit=limit,
                    reverse=True,  # from old to new
                    # filter=types.InputMessagesFilterDocument,
                    offset_id=newer_than_id
                ):
                    logger.debug(message.stringify())
                    if message.media:
                        await download_media(takeout, message, directory=download_dir)

                    # Save the last message id to continue from there if the script is restarted
                    saveProgress(message.id, session_path)

        except errors.TakeoutInitDelayError as e:
            print('Must wait', e.seconds, 'before takeout')
            return
        finally:
            await client.disconnect()


if __name__ == '__main__':
    # asyncio.run(main())
    loop.run_until_complete(main())
