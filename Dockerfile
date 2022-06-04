FROM python:3.10.4-bullseye

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg

RUN git clone https://github.com/Rapptz/discord.py && \
    cd discord.py && \
    python3 -m pip install -U .[voice]

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "main.py"]