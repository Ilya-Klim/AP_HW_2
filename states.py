from aiogram.fsm.state import State, StatesGroup

class ProfileForm(StatesGroup):
    weight = State()
    height = State()
    age = State()
    activity = State()
    city = State()

class FoodForm(StatesGroup):
    food_name = State()
    calories = State()
    food_amount = State()