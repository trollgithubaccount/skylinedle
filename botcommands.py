import discord 
from discord.ext import commands
import requests
import json
import random
from geopy.distance import great_circle 

import settings

list_of_cities = []
num_of_cities = 799

def searchSkyline():
  return 1

def getCoords(city):
  
  api_url = f'https://geocode.maps.co/search?city={city}&api_key={settings.api_key}'
  response = requests.get(api_url)
  return response

def loadCities():

  r = open("worldcities.txt")
  for i in range(num_of_cities):
    
    cityName = r.readline()
    cityName.replace("\n", "")
    
    global list_of_cities
    list_of_cities.append(cityName)

def generateCity():
  return random.choice(list_of_cities)
  
class guessCity(discord.ui.Modal, title="Guess"):
  guess = discord.ui.TextInput(
    style=discord.TextStyle.short,
    label="City",
    required=True,
    placeholder="Enter your guess here",
    max_length=30
  )

  async def on_submit(self, interaction: discord.Interaction):
    global skylinedleCity

    if skylinedleCity == "":
      await interaction.response.send_message("No active skylinedle game. Please start a new one.")

    else: 
      city = self.guess.value

      api_url = f'https://geocode.maps.co/search?city={city}&api_key={settings.api_key}'
      response = requests.get(api_url)

      if response.status_code == requests.codes.ok:
        print(response.text)
        data = json.loads(response.text)[0]
        
        lat = data["lat"]
        long = data["lon"]

        guessCoords = (lat, long)

        if (great_circle(guessCoords, coords).km < 10):
          await interaction.response.send_message(f"You guessed the correct city! The city was {skylinedleCity}.")

          skylinedleCity = ""

        else:
          await interaction.response.send_message(f"Your guess is ~{round(int(great_circle(guessCoords, coords).km), -1)} km away from the city.")

      else:
        print("Error:", response.status_code, response.text)
        await interaction.response.send_message("Invalid city.")



def run():
  intents = discord.Intents.all()
  
  bot = commands.Bot(command_prefix="!", intents=intents)

  loadCities()
  
  @bot.event 
  
  async def on_ready():
    bot.tree.copy_global_to(guild=settings.GUILDS_ID)
    await bot.tree.sync(guild=settings.GUILDS_ID)
    print("no")
  
  @bot.tree.command()
  async def guess(interaction: discord.Interaction):
    guess_modal = guessCity()
    await interaction.response.send_modal(guess_modal)
  
  @bot.tree.command()
  async def start(interaction: discord.Interaction):
  
    global skylinedleCity
    skylinedleCity = generateCity()

    searchSkyline()
    
    response = getCoords(skylinedleCity)
  
    data = json.loads(response.text)[0]
  
    global coords
    coords = (data["lat"], data["lon"])
  
    await interaction.response.send_message("Skylinedle started. Use /guess to guess the city.")
  
  bot.run(settings.token)