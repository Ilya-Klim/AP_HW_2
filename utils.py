import aiohttp
from config import WEATHER_TOKEN
import matplotlib.pyplot as plt
import os

async def get_response_async(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def get_temp(city: str) -> float:
    city_info_url = \
        f'https://api.openweathermap.org/geo/1.0/direct?q={city}&appid={WEATHER_TOKEN}'
    city_info = await get_response_async(city_info_url)
    lat, lon = city_info[0]['lat'], city_info[0]['lon']
    weather_url = \
        f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={WEATHER_TOKEN}'
    weather = await get_response_async(weather_url)
    curr_temp = weather['main']['temp']
    return curr_temp

async def get_food_info(product_name: str):
    url = f"https://world.openfoodfacts.org/cgi/search.pl?action=process&search_terms={product_name}&json=true"
    product_info = await get_response_async(url)
    products = product_info.get('products', [])
    if products:  # Проверяем, есть ли найденные продукты
        first_product = products[0]
        return {
            'name': first_product.get('product_name', 'Неизвестно'),
            'calories': first_product.get('nutriments', {}).get('energy-kcal_100g', 0)
        }
    return None


def generate_progress_graphs(user_id, user_data):
    folder = "graphs"
    os.makedirs(folder, exist_ok=True)

    water_goal = user_data["water_goal"]
    logged_water = user_data["logged_water"]

    calorie_goal = user_data["calorie_goal"]
    logged_calories = user_data["logged_calories"]
    burned_calories = user_data["burned_calories"]
    net_calories = logged_calories - burned_calories

    fig, ax = plt.subplots(1, 2, figsize=(10, 5))

    ax[0].bar(["Выпито", "Норма"], [logged_water, water_goal], color=["blue", "lightblue"])
    ax[0].set_title("Прогресс по воде")
    ax[0].set_ylabel("мл")
    ax[0].set_ylim(0, max(water_goal, logged_water) + 500)

    ax[1].bar(
        ["Потреблено", "Сожжено", "Баланс", "Норма"],
        [logged_calories, burned_calories, net_calories, calorie_goal],
        color=["green", "red", "orange", "lightgreen"]
    )
    ax[1].set_title("Прогресс по калориям")
    ax[1].set_ylabel("ккал")
    ax[1].set_ylim(0, max(calorie_goal, logged_calories, net_calories) + 500)

    file_path = os.path.join(folder, f"user_{user_id}_progress.png")
    plt.tight_layout()
    plt.savefig(file_path)
    plt.close()

    return file_path