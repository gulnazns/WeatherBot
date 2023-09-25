import telebot
import requests
from telebot import types

from constants import API_KEY
from constants import YOUR_TELEGRAM_TOKEN

# Initialize the bot using Telegram bot token
bot = telebot.TeleBot(YOUR_TELEGRAM_TOKEN)
# Create a dictionary to store user data (cities)
user_data = {}


# Handler for the /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to the latest weather update")
    msg = bot.send_message(message.chat.id, "Please enter the name of your city to get the weather:")
    bot.register_next_step_handler(msg, process_city)


# Handler for processing the entered city name
def process_city(message):
    try:
        chat_id = message.chat.id
        city = message.text
        user_data[chat_id] = {'city': city}  # Save the city in user data
        show_weather_options(chat_id)   # Show the user options with buttons
    except Exception as e:
        bot.reply_to(message, 'Oops! Something went wrong.')


# Sending options with buttons
def show_weather_options(chat_id):
    markup = types.InlineKeyboardMarkup()
    temperature_button = types.InlineKeyboardButton("Temperature", callback_data="temperature")
    description_button = types.InlineKeyboardButton("Description", callback_data="description")
    feels_like_button = types.InlineKeyboardButton("Feels Like", callback_data="feels_like")
    humidity_button = types.InlineKeyboardButton("Humidity", callback_data="humidity")
    wind_speed_button = types.InlineKeyboardButton("Wind Speed", callback_data="wind_speed")

    markup.add(temperature_button, description_button)
    markup.add(feels_like_button, humidity_button, wind_speed_button)

    bot.send_message(chat_id, "Select an option:", reply_markup=markup)


# Handler for button click with function
@bot.callback_query_handler(func=lambda call: call.data in ["temperature", "description", "feels_like", "humidity", "wind_speed"])
def handle_option(call):
    try:
        chat_id = call.message.chat.id
        option = call.data
        city = user_data.get(chat_id, {}).get('city')
        if city:
            weather_data = get_weather_data(city, option)
            bot.send_message(chat_id, weather_data)
        else:
            bot.send_message(chat_id, "Please enter the name of your city first.")
    except Exception as e:
        bot.send_message(chat_id, 'Oops! Something went wrong.')


# Fetch weather data from the OpenWeatherMap API
def get_weather_data(city, option):
    api_key = API_KEY
    url = 'https://api.openweathermap.org/data/2.5/weather'
    params = {'q': city, 'appid': api_key, 'units': 'metric', 'lang': 'en', 'exclude': 'minutely,hourly,daily'}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        temperature = f'Temperature: {data["main"]["temp"]}°C'
        description = f'Description: {data["weather"][0]["description"]}'
        feels_like = f'Feels like: {data["main"]["feels_like"]}°C'
        humidity = f'Humidity: {data["main"]["humidity"]}%'
        wind_speed = f'Wind speed: {data["wind"]["speed"]} m/s'

        if option == "temperature":
            weather_data = temperature
        elif option == "description":
            weather_data = description
        elif option == "feels_like":
            weather_data = feels_like
        elif option == "humidity":
            weather_data = humidity
        elif option == "wind_speed":
            weather_data = wind_speed
    else:
        message = 'Sorry, I could not fetch the weather data for that location.'
        weather_data = message

    return weather_data


if __name__ == '__main__':
    bot.polling()
