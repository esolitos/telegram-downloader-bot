from typing import Union
from dotenv import load_dotenv
from os import getenv, path
from telethon.sessions import StringSession


if not load_dotenv():
    raise Exception("No .env file found")

TELEGRAM_DAEMON_SESSION_PATH = getenv("TELEGRAM_DAEMON_SESSION_PATH")
sessionName = getenv("TELEGRAM_DAEMON_SESSION_NAME", "telegramArchive")
stringSessionFilename = "{0}.session".format(sessionName)


def _getStringSessionIfExists():
    sessionPath = path.join(TELEGRAM_DAEMON_SESSION_PATH,
                            stringSessionFilename)
    if path.isfile(sessionPath):
        with open(sessionPath, 'r') as file:
            session = file.read()
            print("Session loaded from {0}".format(sessionPath))
            return session
    return None


def getSession():
    if TELEGRAM_DAEMON_SESSION_PATH == None:
        return sessionName

    return StringSession(_getStringSessionIfExists())


def saveSession(session):
    if TELEGRAM_DAEMON_SESSION_PATH != None:
        sessionPath = path.join(TELEGRAM_DAEMON_SESSION_PATH,
                                stringSessionFilename)
        with open(sessionPath, 'w') as file:
            file.write(StringSession.save(session))
        print("Session saved in {0}".format(sessionPath))


def saveProgress(progress):
    if TELEGRAM_DAEMON_SESSION_PATH != None:
        progressPath = path.join(TELEGRAM_DAEMON_SESSION_PATH,
                                 "progress.txt")
        with open(progressPath, 'w') as file:
            file.write(str(progress))
            file.close()
        print("Progress saved in {0}".format(progressPath))


def getProgress() -> Union[str, None]:
    if TELEGRAM_DAEMON_SESSION_PATH != None:
        progressPath = path.join(TELEGRAM_DAEMON_SESSION_PATH,
                                 "progress.txt")
        if path.isfile(progressPath):
            with open(progressPath, 'r') as file:
                progress = file.read()
                print("Progress loaded from {0}".format(progressPath))
                file.close()
                return progress
    return None
