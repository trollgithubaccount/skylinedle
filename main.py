from logging import NullHandler
import discord 
from discord.ext import commands
import settings
import traceback
import utils
from geopy.distance import great_circle 
import requests
import json

import settings


skylinedleCity = ""
coords = (0, 0)

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
        
        data = json.loads(response.text)[0]
        lat = data["lat"]
        long = data["lon"]

        guessCoords = (lat, long)
        
        if (great_circle(guessCoords, coords).km < 10):
          await interaction.response.send_message(f"You guessed the correct city! The city was {skylinedleCity}.")
          
          skylinedleCity = ""
        
        else:
          await interaction.response.send_message(f"Your guess is ~{round(int(great_circle(guessCoords, coords).km), -3)} km away from the city.")
        
      else:
        print("Error:", response.status_code, response.text)
        await interaction.response.send_message("Invalid city.")
  
def run():
  
  intents = discord.Intents.all()
  
  bot = commands.Bot(command_prefix="!", intents=intents)
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
    skylinedleCity = "Houston"

    api_url = f'https://geocode.maps.co/search?city={skylinedleCity}&api_key={settings.api_key}'
    response = requests.get(api_url)

    data = json.loads(response.text)[0]

    global coords
    coords = (data["lat"], data["lon"])
    
    await interaction.response.send_message("Skylinedle started. Use /guess to guess the city.")
   
  bot.run(settings.token)

if __name__ == "__main__":
  run()