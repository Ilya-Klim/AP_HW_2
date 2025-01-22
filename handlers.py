from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from states import *
from utils import *

router = Router()
users = {}

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.reply(
        "Добро пожаловать! Здесь вы можете узнать дневные нормы воды и калорий, а также отслеживать тренировки и питание\n"
        "Введите /help для уточнения списка команд\n"
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.reply(
        "Список команд:\n"
        "/start - Запуск бота\n"
        "/set_profile - Заполнить профиль пользователя\n"
        "/log_water <количество, мл> - Добавить количество выпитой воды\n"
        "/log_food <название продукта> - Добавить съеденный продукт и его калорийность\n"
        "/log_workout <тип тренировки> <время, мин> - Добавить запись о проведенной тренировки\n"
        "/check_progress - Посмотреть прогресс\n"
        "/help - Помощь\n"
    )

@router.message(Command("set_profile"))
async def cmd_set_profile(message: Message, state: FSMContext):
    await message.reply("Введите ваш вес (в кг):\n")
    await state.set_state(ProfileForm.weight)

@router.message(ProfileForm.weight)
async def cmd_set_profile_weight(message: Message, state: FSMContext):
    await state.update_data(weight=float(message.text))
    await message.reply("Введите ваш рост (в см):\n")
    await state.set_state(ProfileForm.height)

@router.message(ProfileForm.height)
async def cmd_set_profile_age(message: Message, state: FSMContext):
    await state.update_data(height=float(message.text))
    await message.reply("Введите ваш возраст:\n")
    await state.set_state(ProfileForm.age)

@router.message(ProfileForm.age)
async def profile_activity(message: Message, state: FSMContext):
    await state.update_data(age=float(message.text))
    await message.reply("Сколько минут активности у вас в день?\n")
    await state.set_state(ProfileForm.activity)

@router.message(ProfileForm.activity)
async def profile_activity(message: Message, state: FSMContext):
    await state.update_data(activity=float(message.text))
    await message.reply("В каком городе вы находитесь?\n")
    await state.set_state(ProfileForm.city)

@router.message(ProfileForm.city)
async def profile_city(message: Message, state: FSMContext):
    city = message.text
    data = await state.get_data()
    user_id = message.from_user.id
    weight = data.get('weight')
    height = data.get('height')
    age = data.get('age')
    activity = data.get('activity')
    temp = await get_temp(city)
    if temp > 25:
        water_temp = 750
    else:
        water_temp = 0
    user = {
            "weight": weight,
            "height": height,
            "age": age,
            "activity": activity,
            "city": city,
            "water_goal": 30 * weight + water_temp + 500 * activity / 30,
            "calorie_goal": 10 * weight + 6.25 * height - 5 * age + 200 + activity * 4.5,  # последняя добавка от активности
            "logged_water": 0,
            "logged_calories": 0,
            "burned_calories": 0
        }
    users[user_id] = user
    await message.reply(
        f"Ваш профиль заполнен!\n"
        f"Ваш вес: {weight} кг\nВаш рост: {height} см\nВаш возраст: {age} лет\n"
        f"Ваша активность: {activity} минут\nВаш город: {city}")
    await state.clear()

@router.message(Command("log_water"))
async def cmd_log_water(message: Message):
    user_id = message.from_user.id
    args = message.text.split()
    if len(args) != 2:
        await message.reply(
            "Некорректный ввод! Укажите количество воды в мл как в примере:\n"
            "/log_water 500"
        )
        return

    if not args[1].isdigit():
        await message.reply(
            "Некорректный ввод! Количество воды должно быть числом в мл как в примере:\n"
            "/log_water 500"
        )
        return

    water_amount = int(args[1])
    if user_id not in users:
        await message.reply("Сначала создайте свой профиль с помощью команды /set_profile.")
        return

    user = users[user_id]
    user["logged_water"] = user.get("logged_water", 0) + water_amount
    estimated_water = max(0, user["water_goal"] - user["logged_water"])

    await message.reply(
        f"Записан прием воды.\n"
        f"На сегодня выпито {user["logged_water"] } мл воды.\n"
        f"Осталось выпить {estimated_water} мл воды до выполнения нормы {user["water_goal"]}."
    )

@router.message(Command("log_food"))
async def cmd_log_food(message: Message, state: FSMContext):
    user_id = message.from_user.id
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            "Некорректный ввод! Укажите название продукта как в примере:\n"
            "/log_food банан"
        )
        return

    food_name = args[1]
    if food_name.isdigit():
        await message.reply(
            "Некорректный ввод! Укажите название продукта как в примере:\n"
            "/log_food банан"
        )
        return

    food_info = await get_food_info(food_name)
    if food_info is not None:
        food_name = food_info["name"]
        calories = food_info["calories"]
        await message.reply(
            f"{food_name} — {calories} ккал на 100 г. Сколько грамм вы съели?"
        )
        await state.update_data(
            food_name=food_name,
            calories=calories
        )
    else:
        await message.reply("Некорректный ввод! Проверьте название продукта.")
        return

    await state.set_state(FoodForm.food_amount)

@router.message(FoodForm.food_amount)
async def food_calories(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = await state.get_data()
    calories = user_data.get('calories')
    try:
        amount = float(message.text)
        total_calories = (calories * amount) / 100
        users[user_id]["logged_calories"] += total_calories
        await message.reply(f"Записано: {total_calories:.1f} ккал.")
    except ValueError:
        await message.reply("Пожалуйста, корректное количество граммов.")

    await state.clear()

@router.message(Command("log_workout"))
async def cmd_log_workout(message: Message):
    user_id = message.from_user.id
    args = message.text.split()
    if len(args) != 3:
        await message.reply(
            "Некорректный ввод! Укажите тип и время активности согласно формату примера:\n"
            "/log_workout бег 60"
        )
        return

    activity_name = args[1]
    activity_time = args[2]
    if not activity_time.isdigit():
        await message.reply(
            "Некорректный ввод времени активности! Укажите как в примере в мин:\n"
            "/log_workout бег 60"
        )
        return
    else:
        activity_time = float(activity_time)

    if activity_name.isdigit():
        await message.reply(
            "Некорректный ввод названия активности! Пример:\n"
            "/log_workout бег 30"
        )
        return

    burned_calories = activity_time / 30 * 250 # взял среднее количество ккал на 30 мин любой активности
    users[user_id]["burned_calories"] += burned_calories
    water_activ = int(500 * activity_time / 30)
    users[user_id]["water_goal"] += water_activ
    await message.reply(
        f"{activity_name} {activity_time} мин — {burned_calories:.1f} ккал.\n"
        f"Дополнительно выпейте {water_activ} мл воды."
    )

@router.message(Command("check_progress"))
async def check_progress(message: Message):
    user_id = message.from_user.id
    if not user_id:
        await message.answer("Сначала настройте профиль с помощью команды /set_profile.")
        return

    await message.reply(
        "Прогресс:\n"
        f"Вода:\n"
        f"- Выпито: {users[user_id]['logged_water']} мл из {users[user_id]['water_goal']} мл\n"
        f"- Осталось: {users[user_id]['water_goal'] - users[user_id]['logged_water']} мл\n"
        "\n"
        "Калории:\n"
        f"- Потреблено: {users[user_id]['logged_calories']} ккал из {users[user_id]['calorie_goal']} ккал\n"
        f"- Сожжено: {users[user_id]['burned_calories']} ккал"
        f"- Баланс: {users[user_id]['logged_calories'] - users[user_id]['burned_calories']} ккал\n"
    )
