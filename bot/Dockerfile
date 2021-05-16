FROM python:3.9.0
COPY . /app
WORKDIR app
RUN useradd memfrogbot && chown memfrogbot:memfrogbot /app
RUN pip3 install -r requirements.txt
USER memfrogbot
ENV PYTHONPATH "${PYTHONPATH}:/app"
ENTRYPOINT ["python3", "bot.py"]