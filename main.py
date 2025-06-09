import os
from dotenv import load_dotenv
import requests
import json
import discord
from discord import Intents


load_dotenv() # Gets the data from my .env file where the api keys are stored
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
BOT_TOKEN = os.getenv("DISCORD_TOKEN")

# print(WEATHER_API_KEY)
# print(BOT_TOKEN)

# city = "Beatrice"
# url = f"https://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}" # build the url using f print with the api key and example city

# response = requests.get(url) # gets data
# data = response.json() # converts data into readable JSON

# print(data["location"]["region"]) # Syntax to print only the state
# print(json.dumps(data, indent=2))
# print(data["location"]["name"])
# print(data["current"]["temp_f"])
# print(data["current"]["condition"]["text"])


intents = discord.Intents.default() # creates intents object
intents.message_content = True # allows the bot to read messages sent by users
client = discord.Client(intents=intents) # needs the intents passed into the client

@client.event
async def on_ready(): # Must be async because discord bots need to run this way because they are constantly doing things like listening for messages, responding to events, etc. Async lets the program start a task, wait for it to finish, and do something elsew while it's waiting.
    print(f"Logged in as Roeland Weather Bot")

@client.event
async def on_message(message):
    if message.author == client.user: # returns nothing if the message author is the bot
        return
    
    if message.content.startswith("!weather"):
        location = message.content[len("!weather"):].strip() # slices off "!weather" from the start of the message, leaving just the location (e.g., "Beatrice, NE"). The colon means "start at index 8 and go to the end"
        
        url = f"https://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={location}"

        try:
            response = requests.get(url)
            data = response.json()
        except requests.exceptions.RequestException:
            await message.channel.send("Couldn't connect to the weather service. Try again later.")
            return
        except ValueError:
            await message.channel.send("The response wasn't valid JSON.")
            return

        # await message.channel.send(data["location"]["name"], data["current"]["temp_f"], data["current"]["condition"]["text"]) ### This doesn't work because .send() can't accept more than a single argument.

        condition_emojis = { # dictionary to house all the emojis
            "sunny": "☀️",
            "clear": "🌙",
            "cloud": "☁️",
            "overcast": "🌥️",
            "mist": "💧",
            "fog": "🌫️",
            "rain": "🌧️",
            "drizzle": "🌦️",
            "snow": "❄️",
            "sleet": "🌨️",
            "ice": "🧊",
            "freezing": "🧊",
            "blizzard": "🌨️❄️",
            "thunder": "⛈️⚡",
            "showers": "🌦️",
        }

        uv_levels = { # dictionary to house uv levels
            (0, 2): "🟢 Low",
            (3, 5): "🟡 Moderate",
            (6, 7): "🟠 High",
            (8, 10): "🔴 Very High",
            (11, float('inf')): "🟣 Extreme"
        }


        try:
            city = data["location"]["name"]
            temp = data["current"]["temp_f"]
            condition = data["current"]["condition"]["text"]
            conditionForEmoji = data["current"]["condition"]["text"].lower() # ensure the condition is lowercase for the emoji code
            windSpeed = data["current"]["wind_mph"]
            windDirection = data["current"]["wind_dir"]
            feelsLike = data["current"]["feelslike_f"]
            lastUpdated = data["current"]["last_updated"]
            windChill = data["current"]["windchill_f"]
            gust = data["current"]["gust_mph"]
            humidity = data["current"]["humidity"]
            uv = data["current"]["uv"]
            precip = data["current"]["precip_in"]


            emoji = "❔"
            uvLevel = "Unknown"

            for (minval, maxval), label in uv_levels.items():
                if minval <= uv <= maxval:
                    uvLevel = label
                    break

            for keyword, symbol in condition_emojis.items(): # .items() gets both the keyword and the symbol in one iteration
                if keyword in conditionForEmoji:
                    emoji = symbol
                    break

        except KeyError:
            await message.channel.send("Couldn't find weather for that location. Make sure it's valid, like `Beatrice, NE` or `Lincoln`")

        await message.channel.send(
            f"# Weather in {city}\n"
            f"{emoji} Condition: {condition}\n"
            f"🌡️ Temperature: {temp}°F\n"
            f"🌡️ Feels like: {feelsLike}°F\n"
            f"🧣 Wind chill: {windChill}°F\n"
            f"💧 Precipitation (last hour): {precip} inches\n"
            f"💦🏜️ Humidity: {humidity}%\n"
            f"💨 Wind: {windSpeed} mph from {windDirection}\n"
            f"💨💨 Gusts: {gust} mph\n"
            f"☀️ UV Level: {uvLevel}, {uv}\n"
            f"⏲️ Last updated: {lastUpdated} (local time)"

                                   ) # sends the current weather in a message
        try:
            await message.delete() # delete command
        except discord.Forbidden:
            print("Bot doesn't hav epermission to delete messages.")
        # print(f"Getting weather for {location}")

client.run(BOT_TOKEN) # connect to discord's servers, log in using bot token, start asynchronous event loop that listens for on_ready, on_message, on_member_join, keeps the bot running. uses the on_ready() function I made.