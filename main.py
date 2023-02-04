from aiogram import Bot, Dispatcher, executor, types
import time
import logging
import asyncio
import requests
from datetime import date
STOCK = ["TSLA", "AAPL", "NVDA"]
COMPANY_NAME = {"TSLA": "Tesla",
                "AAPL": "Apple",
                "NVDA": "Nvidia"}
stock_api_key = "QINTCOBUUO6WFHQN"
news_api_key = "9680383ccf424798bdb54fe87b0091a5"
stock_base = "https://www.alphavantage.co/query?"
news_base = "/v2/top-headlines"


news_base = "https://newsapi.org/v2/top-headlines?"
news_api_key = "9680383ccf424798bdb54fe87b0091a5"
news_params = {
    "apiKey": news_api_key,
    "q": "Tesla Inc",
    "sources": "business-insider"
}

stock_params = {
    "function": "TIME_SERIES_INTRADAY",
    "symbol": STOCK,
    "apikey": stock_api_key,
    "interval": '60min'
}
TOKEN = BOT_TOKEN

bot = Bot(TOKEN)
dp = Dispatcher(bot=bot)

@dp.message_handler(commands="start")
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    logging.info(f'{user_id} {user_full_name} {time.asctime()}')
    await message.reply(f"Привет {user_full_name}")
    while True:
        await asyncio.sleep(10)
        today = str(date.today()).split('-')
        yesterday = f"{today[0]}-{today[1]}-{str(int(today[2]) - 1)} 20:00:00"
        pre_yesterday = f"{today[0]}-{today[1]}-{str(int(today[2]) - 2)} 20:00:00"
        for id in STOCK:
            stock_params["symbol"] = id
            response = requests.get(stock_base, params=stock_params)
            stock_data = response.json()
            if yesterday not in stock_data["Time Series (60min)"] and pre_yesterday not in stock_data["Time Series (60min)"]:
                print('weekends today')
                break
            else:
                price_yesterday = float(stock_data["Time Series (60min)"][yesterday]['4. close'])
                price_pre_yesterday = float(stock_data["Time Series (60min)"][pre_yesterday]['4. close'])
                price_change = (price_yesterday - price_pre_yesterday) / price_pre_yesterday
                if abs(price_change) >= 0.05:
                    news_params["q"] = COMPANY_NAME[id]
                    response = requests.get(news_base, params=news_params)
                    news_data = response.json()['articles']
                    if len(news_data) > 0:
                        news = news_data[0]
                        if price_change < 0:
                            emoji = "🔻"
                        else:
                            emoji = "🔺"
                        msg = f"{id}: {emoji}{price_change * 100}%\n" \
                                  f"Headline: {news['title']}\n" \
                                  f"Brief: {news['description']}\n" \
                                  f"{news['url']}"
                        await bot.send_message(user_id, msg)
if __name__ == "__main__":
    executor.start_polling(dp)