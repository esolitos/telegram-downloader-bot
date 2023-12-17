from typing import Union
from os import getenv, path
from telethon.sessions import StringSession


def _getStringSessionIfExists(sessionPath: str):
    if path.isfile(sessionPath):
        with open(sessionPath, 'r') as file:
            session = file.read()
            print("Session loaded from {0}".format(sessionPath))
            return session
    return None


def getSession(basePath: str):
    sessionPath = path.join(basePath, 'telegramArchive.session')
    return StringSession(_getStringSessionIfExists(sessionPath))


def saveSession(session, basePath: str):
    sessionPath = path.join(basePath, 'telegramArchive.session')
    with open(sessionPath, 'w') as file:
        file.write(StringSession.save(session))
    print("Session saved in {0}".format(sessionPath))


def saveProgress(progress, basePath: str):
    progressPath = path.join(basePath, "progress.txt")
    with open(progressPath, 'w') as file:
        file.write(str(progress))
        file.close()
    print("Progress saved in {0}".format(progressPath))


def getProgress(basePath: str) -> Union[str, None]:
    progressPath = path.join(basePath, "progress.txt")
    if path.isfile(progressPath):
        with open(progressPath, 'r') as file:
            progress = file.read()
            print("Progress loaded from {0}".format(progressPath))
            file.close()
            return progress
