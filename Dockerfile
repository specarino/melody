FROM python:3.10.4-bullseye

WORKDIR /app

RUN git clone https://github.com/Rapptz/discord.py
RUN cd discord.py
RUN python3 -m pip install -U .[voice]

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

RUN apt-get update && apt-get install -y ffmpeg

CMD ["python3", "main.py"]