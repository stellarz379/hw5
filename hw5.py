import sqlite3
import requests
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types, executor
from config import token  

bot = Bot(token=token)
dp = Dispatcher(bot)

def init_db():
    conn = sqlite3.connect('news.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_news_to_db(title, url):
    conn = sqlite3.connect('news.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO news (title, url) VALUES (?, ?)', (title, url))
    conn.commit()
    conn.close()

async def start(message: types.Message):
    await message.answer("Привет! Я бот новостей. Чтобы получить новости, введите команду /news.")

async def news(message: types.Message):
    for page in range(1, 11):
        url = f'https://24.kg/page_{page}'
        try:
            response = requests.get(url=url)
            response.raise_for_status()  
            soup = BeautifulSoup(response.text, 'html.parser')
            all_news = soup.find_all('div', class_='one')
            for news_item in all_news:
                news_title_div = news_item.find('div', class_='title')
                news_link = news_item.find('a')
                if news_title_div and news_link:
                    news_title = news_title_div.text.strip()
                    news_url = news_link['href']
                    add_news_to_db(news_title, news_url)
                    news_text = f"*{news_title}*\n[Читать далее]({news_url})"
                    while len(news_text) > 0:
                        await message.answer(news_text[:4096], parse_mode="Markdown")
                        news_text = news_text[4096:]
        except Exception as e:
            await message.answer(f"Произошла ошибка при получении новостей: {e}")

@dp.message_handler(commands=['start'])
async def handle_start(message: types.Message):
    await start(message)

@dp.message_handler(commands=['news'])
async def handle_news(message: types.Message):
    await news(message)

if __name__ == '__main__':
    init_db()  
    executor.start_polling(dp)
