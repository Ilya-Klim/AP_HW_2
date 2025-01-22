import aiohttp
from config import WEATHER_TOKEN

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