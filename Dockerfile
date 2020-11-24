FROM python:3.9.0-slim
COPY . /app
WORKDIR app
RUN useradd memfrogbot && chown memfrogbot:memfrogbot /app
RUN pip3 install -r requirements.txt
USER memfrogbot
ENTRYPOINT ["python3", "bot.py"]