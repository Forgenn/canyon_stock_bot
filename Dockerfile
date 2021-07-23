FROM python:3.7
WORKDIR /canyon_bot
ADD https://raw.githubusercontent.com/Forgenn/canyon_stock_bot/master/canyon_stock_bot.py .
ADD .env .
RUN pip3 install beautifulsoup4 python-telegram-bot python-dotenv requests
CMD ["python", "./canyon_stock_bot.py"]
