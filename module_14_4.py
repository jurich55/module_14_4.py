from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

from crud_functions import*
#     Создание бота и диспетчера
api = "****"
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

#     Создание клавиатуры  kb_re
kb_re = ReplyKeyboardMarkup(resize_keyboard=True)
button = KeyboardButton(text='Информация')
button1 = KeyboardButton(text='Рассчитать')
button2 = KeyboardButton(text='Купить')
kb_re.row(button, button1)
kb_re.add(button2)

#     Создание клавиатуры  kb_in
kb_in = InlineKeyboardMarkup(resize_keyboard=True)
button = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
kb_in.row(button, button2)

#     Создание клавиатуры  catalog_kb
catalog_kb = InlineKeyboardMarkup(row_width=4)
catalog_kb.add(
    InlineKeyboardButton('Продукт 1', callback_data='product_buying'),
    InlineKeyboardButton('Продукт 2', callback_data='product_buying'),
    InlineKeyboardButton('Продукт 3', callback_data='product_buying'),
    InlineKeyboardButton('Продукт 4', callback_data='product_buying')
)

#    Обработчик    кнопок   Inline клавиатуры  catalog_kb
@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer('Спасибо. Вы успешно приобрели продукт!')
    await call.answer()
    await call.message.answer("Для продолжения  работы  введите команду /start .")

                 # Обработчик    кнопки   Купить
@dp.message_handler(text='Купить')
async def get_buying_list(message):
    for i in range(1, 5):
        await message.answer(f'Название: Продукт {i}|'
                             f' Описание: Комплект добавок {i}| Цена: {i*100}')
        with open(f'files1/{i}.png', 'rb') as png:
            await message.answer_photo(png)
    await message.answer('Выберите продукт для покупки:', reply_markup=catalog_kb)                  #  вызов  клавиатуры catalog_kb


# Определение класса состояний для профиля пользователя
class UserProfile(StatesGroup):
    age = State()  # Состояние для ввода возраста
    growth = State()  # Состояние для ввода роста
    weight = State()  # Состояние для ввода веса
    gender = State()  # Состояние для выбора пола


#           обработчики состояний :
@dp.message_handler(commands=['start'])     # команда  для запуска бота
async def set_start(message):
    await message.answer('Здравствуйте! Нажмите кнопку  "Информация" ',
                         reply_markup=kb_re)           # вызов   клавиатуры  kb_re


# Обработчик    кнопки   Информация
@dp.message_handler(text='Информация')
async def inform(massage):
    await massage.answer('Привет!  Я бот, и я рассчитаю для Вас необходимое '
                         'суточное  количество калорий.  Нажмите кнопку  "Рассчитать"')


# Обработчик    кнопки   Рассчитать  и  вызов  клавиатуры  kb_in
@dp.message_handler(text='Рассчитать')
async def main_menu(massage):
    await massage.answer('Выберите опцию :',
                reply_markup=kb_in)                  # вызов   клавиатуры  kb_in


# Обработчик    кнопки   calories
@dp.callback_query_handler(text='calories')
async def calculation(call):
    await call.message.answer('Введите свой возраст:')
    await call.answer()
    await UserProfile.age.set()                     # Переход к  состоянию   age


# Обработчик   состояния  age
@dp.message_handler(state=UserProfile.age)
async def set_age(message, state):
    age = int(message.text)
    await state.update_data(age=age)       # Обновление и сохранение данных
    await UserProfile.growth.set()                    # Переход к  состоянию   growth
    await message.answer("Какой у вас рост?")         # 2 Запрос (рост)


# Обработчик   состояния  growth
@dp.message_handler(state=UserProfile.growth)
async def set_growth(message, state):
    growth = int(message.text)
    await state.update_data(growth=growth)  # Обновление и сохранение данных
    await UserProfile.weight.set()                       # Переход к  состоянию  weight
    await message.answer("Какой у вас вес ?")         # 3 Запрос (вес)


# Обработчик   состояния  weight
@dp.message_handler(state=UserProfile.weight)
async def set_weight(message, state):
    weight = int(message.text)
    await state.update_data(weight=weight)  # Обновление и сохранение данных
    await UserProfile.gender.set()                     # Переход к состоянию  gender
    await message.answer("Укажите ваш пол (1 = мужчина или  2 = женщина)")


# Обработчик   состояния  gender
@dp.message_handler(state=UserProfile.gender)
async def process_gender(message, state):
    gender = message.text.lower()                # сохранение пола по адресу gender
    await state.update_data(gender=gender)  # Обновление и сохранение данных.

    # Получение всех данных
    data = await state.get_data()
    age = data['age']
    growth = data['growth']
    weight = data['weight']
    gender = data['gender']

    # Расчёт BMR на основе выбора пола
    if gender == "1":
        bmr = 10 * weight + 6.25 * growth - 5 * age + 5
    elif gender == "2":
        bmr = 10 * weight + 6.25 * growth - 5 * age - 161
    else:                           # Исключение ошибки записи
        await message.answer("Некорректный ввод пола."
                             " Пожалуйста, укажите ' 1 ' или ' 2 '.")
        return

    #    Ответ пользователю
    await message.answer(f"Ваши данные:"
                         f" возраст - {data['age']} лет, "
                         f" рост - {data['growth']} см, "
                         f" вес - {data['weight']} кГ")
    await message.answer(f"Ваш уровень метаболизма (BMR) составляет:"
                         f" {bmr:.2f} калорий в день.")

    # Обработчик   кнопки   formulas
    @dp.callback_query_handler(text='formulas')
    async def get_formulas(call):
        if gender == "1":
            await call.message.answer('10 x вес (кг) + 6,25 x рост (см)'
                                      ' – 5 x возраст (г) + 5')
        elif gender == "2":
            await call.message.answer('10 x вес (кг) + 6,25 x рост (см)'
                                      ' – 5 x возраст (г) – 161')
        await call.answer()

    await state.finish()


# "Перехват"  произвольного  сообщения
@dp.message_handler()
async def all_message(message):
    if message.text != '/start':
        await message.answer("Для начала работы  введите команду /start .")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)  # Эта строка запускает бота
                                                # и начинает получать обновления из Telegram

#               добавление различных файлов в код
# messages.answer_photo
# messages.answer_video
# messages.answer_file
