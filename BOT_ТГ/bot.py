import aiohttp  # Для асинхронных запросов
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
import logging
import re
import asyncio
from bs4 import BeautifulSoup
import g4f  # Для взаимодействия с OpenAI API
from colorama import Fore, Style  # Для цветного вывода
from functools import lru_cache

# Токен Telegram-бота
API_TOKEN = '8042576890:AAEdk_lK-PP84m2cP5Ylhy9UYXlneZLswcc'

# Настроим логирование
logging.basicConfig(level=logging.DEBUG)

# Инициализируем бота и диспетчер
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Создаем клавиатуру с четырьмя кнопками в два ряда
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🔍 Анализировать сайт"),
            KeyboardButton(text="❓ Помощь AI")
        ],
        [
            KeyboardButton(text="📞 Контакты"),
            KeyboardButton(text="👥 Люди")
        ],
        [
            KeyboardButton(text="🧑‍💼 Владислав Борисович Каламбет")  # Новая кнопка
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

# Структура для хранения состояния пользователя
user_states = {}


# Функция для проверки валидности URL с использованием регулярных выражений
def is_valid_url(url: str) -> bool:
    # Регулярное выражение для проверки URL
    regex = re.compile(
        r'^(?:http|https)://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+$')
    return re.match(regex, url) is not None


# Функция для обработки команды /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_states[message.from_user.id] = None
    await message.answer("Привет! Что вы хотите сделать?", reply_markup=keyboard)


# "Анализировать сайт"
@dp.message(lambda message: "анализировать" in message.text.lower())
async def handle_analyze_site(message: Message):
    user_states[message.from_user.id] = 'analyze'
    await message.answer("Отправьте мне ссылку на сайт, который вы хотите проанализировать.")


# "Помощь AI" (для взаимодействия с GPT-4)
@dp.message(lambda message: "помощь ai" in message.text.lower())
async def handle_help_ai(message: Message):
    user_states[message.from_user.id] = 'help_ai'
    await message.answer("Задайте свой вопрос, и я постараюсь на него ответить.")


# "Контакты"
@dp.message(lambda message: "контакты" in message.text.lower())
async def handle_contacts(message: Message):
    user_states[message.from_user.id] = 'contacts'
    await message.answer("Отправьте мне ссылку на сайт, чтобы я нашел контактные данные.")


# "Люди"
@dp.message(lambda message: "люди" in message.text.lower())
async def handle_people(message: Message):
    user_states[message.from_user.id] = 'people'
    await message.answer("Отправьте мне ссылку на сайт, чтобы я нашел людей на нем.")


# Обработчик URL (для анализа сайта и поиска контактов)
@dp.message(lambda message: re.match(r'http[s]?://[^\s]+', message.text))
async def handle_url(message: Message):
    url = message.text.strip()

    # Проверка на валидность URL
    if not is_valid_url(url):
        await message.answer("Введенная ссылка некорректна. Пожалуйста, отправьте правильный URL.")
        return

    logging.info(f"Получена ссылка: {url}")

    state = user_states.get(message.from_user.id)

    if state == 'analyze':
        result = await analyze_website(url)
        if isinstance(result, dict):
            response = (f"Заголовок: {result['title']}\n\n"
                        f"Изображений: {result['images']}\n"
                        f"Ссылок: {result['links']}\n"
                        f"Слов в тексте: {result['words']}")

        else:
            response = result
        await message.answer(response)
        user_states[message.from_user.id] = None

    elif state == 'contacts':
        result = await find_contacts(url)
        try:
            g4f_response = await process_gpt4_data(result, "user",
                                                   "Вот данные о контактах: {0}. Оставь только номера начинающиеся на +, и почты с @.")
            await message.answer(g4f_response)
        except Exception as e:
            logging.error(f"Ошибка при работе с g4f: {str(e)}")
            await message.answer("Произошла ошибка при обработке данных. Попробуйте снова.")
        user_states[message.from_user.id] = None

    elif state == 'people':
        result = await find_people(url)
        try:
            g4f_response = await process_gpt4_data(result, "user",
                                                   "Вот данные о людях с сайта: {0}. Оставь только корректные ФИО и, если есть, дату рождения.")
            await message.answer(g4f_response)
        except Exception as e:
            logging.error(f"Ошибка при работе с g4f: {str(e)}")
            await message.answer("Произошла ошибка при обработке данных. Попробуйте снова.")
        user_states[message.from_user.id] = None

    else:
        await message.answer("Пожалуйста, отправьте ссылку на сайт для анализа или поиска контактов.")


# Функция для обработки вопросов с помощью GPT-4
@dp.message(lambda message: user_states.get(message.from_user.id) == 'help_ai')
async def handle_ai_question(message: Message):
    user_states[message.from_user.id] = None  # Сбрасываем состояние после получения ответа

    try:
        # Получаем ответ от GPT-4
        g4f_response = await process_gpt4_data(message.text, "user", "Ответь на вопрос: {0}")
        await message.answer(g4f_response)

    except Exception as e:
        logging.error(f"Ошибка при работе с GPT-4: {str(e)}")
        await message.answer("Произошла ошибка при обработке данных через GPT-4. Попробуйте снова.")

    # Возвращаем пользователя в главное меню
    await message.answer("Задайте другой вопрос или выберите одну из опций в главном меню.", reply_markup=keyboard)


# Функция для обработки запросов к GPT-4
async def process_gpt4_data(result: str, role: str, content_template: str):
    try:
        g4f_response = g4f.ChatCompletion.create(
            model=g4f.models.gpt_4,
            messages=[{"role": role, "content": content_template.format(result)}]
        )
        return str(g4f_response)
    except Exception as e:
        logging.error(f"Ошибка при работе с GPT-4: {str(e)}")
        return "Произошла ошибка при обработке данных через GPT-4. Попробуйте снова."


# Функция для анализа сайта (с использованием aiohttp для асинхронных запросов)
@lru_cache(maxsize=100)  # Кэшируем результаты анализа сайтов
async def analyze_website(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    text = await response.text()
                    soup = BeautifulSoup(text, 'html.parser')

                    # Анализируем заголовок страницы
                    title = soup.find('title').text.strip() if soup.find('title') else "Не найдено"

                    # Анализируем количество изображений на странице
                    images = soup.find_all('img')
                    image_count = len(images)

                    # Анализируем количество ссылок на странице
                    links = soup.find_all('a')
                    link_count = len(links)

                    # Анализируем количество слов в тексте страницы
                    text_content = soup.get_text().strip()
                    word_count = len(text_content.split())

                    return {
                        "title": title,
                        "images": image_count,
                        "links": link_count,
                        "words": word_count
                    }
                else:
                    return f"{Fore.RED}Ошибка: Код статуса {response.status}{Style.RESET_ALL}"
    except Exception as e:
        return f"{Fore.RED}Ошибка: {str(e)}{Style.RESET_ALL}"


# Функция для поиска контактов (почты и телефонов)
async def find_contacts(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    text = await response.text()

                    # Ищем только телефонные номера, начинающиеся с '+'
                    phones = set(re.findall(r'\+[\d\-\s()]{7,20}', text))

                    # Ищем email-адреса
                    emails = set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text))

                    # Формируем сообщение с контактными данными
                    response_message = ""

                    # Выводим email-адреса
                    if emails:
                        response_message += "Электронные адреса:\n"
                        for i, email in enumerate(emails, 1):
                            response_message += f"{i}. {email}\n"

                    # Выводим номера телефонов
                    if phones:
                        response_message += "\nТелефоны:\n"
                        for i, phone in enumerate(phones, 1):
                            response_message += f"{i}. {phone}\n"

                    # Если нет контактных данных
                    if not emails and not phones:
                        response_message = "Контактные данные не найдены."

                    return response_message
                else:
                    return f"{Fore.RED}Ошибка: Код статуса {response.status}{Style.RESET_ALL}"
    except Exception as e:
        return f"{Fore.RED}Ошибка: {str(e)}{Style.RESET_ALL}"


# Функция для поиска людей на сайте с улучшенным регулярным выражением
people_regex = r'([А-ЯЁ][a-zа-яё]+ [А-ЯЁ][a-zа-яё]+)(?:.*?(\d{1,2}[-/.]\d{1,2}[-/.]\d{4}))?'


async def find_people(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    text = await response.text()

                    # Пример регулярных выражений для поиска ФИО и даты рождения
                    people = set(re.findall(people_regex, text))

                    if people:
                        response_message = "Люди на сайте:\n\n"
                        for i, person in enumerate(people, 1):
                            full_name = person[0]
                            birth_date = person[1] if person[1] else "Не указана"
                            response_message += f"{i}. {full_name} - {birth_date}\n"

                        return response_message.strip()

                    else:
                        return "Люди не найдены на сайте."

                else:
                    return f"{Fore.RED}Ошибка: Код статуса {response.status}{Style.RESET_ALL}"
    except Exception as e:
        return f"{Fore.RED}Ошибка: {str(e)}{Style.RESET_ALL}"


# Обработчик для кнопки "Владислав Борисович Каламбет"
@dp.message(lambda message: "владислав борисович каламбет" in message.text.lower())
async def handle_vladislav(message: Message):
    # Текст, который будет отправляться при нажатии на кнопку
    text = """
📜 **Экспертная деятельность**:

🔹 Заведующий лабораторией кибернетики и робототехники в РКСИ
🔹 Преподаватель в учебном центре «Гэндальф»
🔹 Эксперт WorldSkills по направлениям «Машинное обучение и большие данные», «Веб-дизайн и разработка» (Эксперт открытого чемпионата, Эксперт демонстрационного экзамена)
🔹 Эксперт Abilympics по направлению «Веб-дизайн и разработка»

📚 **Преподаваемые дисциплины**:

🔹 Машинное обучение и большие данные
🔹 Основы кибернетики и основы робототехники
🔹 Веб-дизайн и разработка
🔹 Технология разработки и защиты баз данных
🔹 Облачные технологии
🔹 Основы программирования и БД

💻 **Основные языки программирования**:

🔸 С, Python, PHP, SQL, HTML, CSS
"""
    await message.answer(text)


# Запуск бота
if __name__ == '__main__':
    asyncio.run(dp.start_polling(bot))
