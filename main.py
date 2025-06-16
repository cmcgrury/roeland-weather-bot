import os
from dotenv import load_dotenv
import requests
import json
import discord
from discord import Intents
from discord.ext import tasks
from datetime import datetime


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
    check_weather_alerts.start()
    await client.change_presence(activity=discord.Game(name="type !help for commands"))

@client.event
async def on_message(message):
    if message.author == client.user: # returns nothing if the message author is the bot
        return
    
    allowedChannelId = {1381749910247964761, 1381417910244741241}
    if message.channel.id not in allowedChannelId:
        return

    if message.content.startswith("!weather"):
        location = message.content[len("!weather"):].strip() # slices off "!weather" from the start of the message, leaving just the location (e.g., "Beatrice, NE"). The colon means "start at index 8 and go to the end"
        
        url = f"https://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={location}"
        urlSun = f"https://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={location}"

        try:
            response = requests.get(url)
            responseSun = requests.get(urlSun)
            data = response.json()
            dataSun = responseSun.json()
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
            sunrise = dataSun["forecast"]["forecastday"][0]["astro"]["sunrise"]
            sunset = dataSun["forecast"]["forecastday"][0]["astro"]["sunset"]


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
            return
        
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
            f"🌅 Sunrise: {sunrise} (location time)\n"
            f"🌇 Sunset: {sunset} (location time)\n"
            f"⏲️ Last updated: {lastUpdated} (location time)"

                                   ) # sends the current weather in a message
        try:
            await message.delete() # delete command
        except discord.Forbidden:
            print("Bot doesn't hav epermission to delete messages.")
        # print(f"Getting weather for {location}")

    if message.content.startswith("!alert"):
        locationAlert = message.content[len("!alert"):].strip()
        urlAlerts = f"https://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={locationAlert}&alerts=yes"

        try:
            response = requests.get(urlAlerts)
            dataAlerts = response.json()
        except requests.exceptions.RequestException:
            await message.channel.send("Couldn't connect to the weather service. Try again later.")
            return
        except ValueError:
            await message.channel.send("The response wasn't valid JSON")
            return
        
        alerts = dataAlerts.get("alerts", {}).get("alert", [])

        if not alerts:
           await message.channel.send(f"No active weather alerts for **{locationAlert}**")

        for alert in alerts:
            event = alert.get("event", "")
            if "beach hazard" in event.lower():
                continue

            headline = alert.get("headline", "No Headline")
            severity = alert.get("severity", "Unknown")
            urgency = alert.get("urgency", "Unknown")
            areas = alert.get("areas", "")
            certainty = alert.get("certainty", "")
            event = alert.get("event", "")
            start = alert.get("effective", "")
            end = alert.get("expires", "")
            desc = alert.get("desc", "")
            instruction = alert.get("instruction", "")

            alertMessage = (
                f"**{headline}** ({severity})\n"
                f"**Urgency:** {urgency}\n"
                f"**Certainty:** {certainty}\n"
                f"\n"
                f"\n"
                f"{desc}\n"
                f"**Instructions:** {instruction}"
            )

            await message.channel.send(alertMessage)

        try:
            await message.delete() # delete command
        except discord.Forbidden:
            print("Bot doesn't hav epermission to delete messages.")

    
    if message.content.startswith("!help"):
        await message.channel.send("Type `!weather cityname` or `!weather cityname, state abreviation` for current weather. Type `!alert cityname` or `!alert cityname, state abreviation` for current weather alerts.")

seenAlerts = set()

locationAlertTags = {
    "Beatrice, NE": [320361266407276546],
    "Lincoln, NE": [456265293099040768],
    "Los Angeles, CA": [190277036600721408],
    "Omaha, NE": [330029870673559553]
}

@tasks.loop(minutes=1)
async def check_weather_alerts():
    allowedChannelIds = [1381417910244741241, 1381749910247964761]
    allowedChannels = [client.get_channel(ch_id) for ch_id in allowedChannelIds]
    locations = ["Beatrice, NE", "Omaha, NE", "Lincoln, NE", "Los Angeles, CA", "Kearney, NE"]

    for location in locations:
        userIds = locationAlertTags.get(location, [])
        tag = " ".join(f"<@{uid}>" for uid in userIds)
        url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={location}&alerts=yes"

        response = requests.get(url)
        data = response.json()

        alerts = data.get("alerts", {}).get("alert", [])
        if alerts:
            print("Alerts found")
        else:
            print("No alerts found")

        for alert in alerts:
            event = alert.get("event", "")
            if "beach hazard" in event.lower:
                continue
            
            f"{tag}\n"
            headline = alert.get("headline", "No Headline")
            severity = alert.get("severity", "Unknown")
            urgency = alert.get("urgency", "Unknown")
            areas = alert.get("areas", "")
            certainty = alert.get("certainty", "")
            event = alert.get("event", "")
            start = alert.get("effective", "")
            end = alert.get("expires", "")
            desc = alert.get("desc", "")
            instruction = alert.get("instruction", "")
                
            alertMessage = (
                f"**{headline}** ({severity})\n"
                f"**Urgency:** {urgency}\n"
                f"**Certainty:** {certainty}\n"
                f"\n"
                f"\n"
                f"{desc}\n"
                f"**Instructions:** {instruction}\n"
                f"{tag}"
            )

            if headline not in seenAlerts:
                seenAlerts.add(headline)

                for channel in allowedChannels:
                    if channel:
                        await channel.send(alertMessage)





client.run(BOT_TOKEN) # connect to discord's servers, log in using bot token, start asynchronous event loop that listens for on_ready, on_message, on_member_join, keeps the bot running. uses the on_ready() function I made.