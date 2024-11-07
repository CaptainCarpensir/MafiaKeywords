FROM python:3.9-slim

WORKDIR /usr/src/app

ADD src .

EXPOSE 8080

RUN python3 -m pip install -U discord.py
RUN python3 -m pip install -U python-dotenv
RUN pip install rapidfuzz

CMD ["python", "bot.py"]