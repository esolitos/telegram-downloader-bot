FROM python:3.10-alpine

COPY ./*.py .
COPY ./requirements.txt .

RUN mkdir /downloads /session \
        && pip install -r requirements.txt

# Set some sane defaults
ENV TELEGRAM_DAEMON_SESSION_PATH "/session/"
ENV TELEGRAM_DOWNLOAD_DIR "/downloads/"

CMD ["python3", "telethon-download.py"]
