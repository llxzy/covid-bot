import csv
import datetime
from dateutil.parser import parse
import discord
import os
import yaml
import urllib.request
from discord.ext import commands


"""----------CONSTANTS AND GLOBAL VARIABLES----------"""

bot = commands.Bot(command_prefix='!')
bot.remove_command('help')

LAST_ARCHIVED = datetime.date(1970, 1, 1)
DATA_URL = "https://mapa.covid.chat/export/csv"
CONFIG_FILE = "./config.yaml"
CSV_FILE = "./data.csv"



"""----------CSV RETRIEVAL AND DATA PARSING----------"""


def get_csv() -> None:
    urllib.request.urlretrieve(DATA_URL, CSV_FILE)
    LAST_ARCHIVED = datetime.date.today()


def parse_csv() -> list:
    data_list = []
    with open(CSV_FILE, "r") as csv_file:
        csv_data = csv.DictReader(csv_file, delimiter=';')
        data_list = list(csv_data)
    return data_list


def format_data(date_str: str, row: dict) -> discord.Embed:
    embed = discord.Embed(title=f"Data for {date_str}")
    embed.add_field(name="Confirmed", value=row["Pocet potvrdenych"])
    embed.add_field(name="Active", value=row["Pocet aktivnych"])
    embed.add_field(name="Cured", value=row["Pocet vyliecenych"])
    embed.add_field(name="New tested", value=row["Dennych testov"])
    embed.add_field(name="New cases", value=row["Dennych prirastkov"])
    embed.add_field(name="Total deaths", value=row["Pocet umrti"])
    return embed




"""----------BOT EVENTS AND COMMANDS----------"""
            

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="!help for a list of commands"))
    print("Battlecruiser operational (Connected and running)")


@bot.command(name='help')
async def help_msg(ctx) -> None:
    m_embed = discord.Embed()
    m_embed.add_field(name="Commands", 
                      value="help, source, info (WIP)")
    await ctx.send(embed=m_embed)


@bot.command(name='source')
async def source_msg(ctx) -> None:
    m_embed = discord.Embed()
    m_embed.add_field(name="Source code available at:",
                      value="https://github.com/llxzy/covid-bot")
    await ctx.send(embed=m_embed)


@bot.command(name='info')
async def info(ctx, 
               day:str, 
               month:str, 
               year: str = 2020
               ) -> None:
    if datetime.date.today() != LAST_ARCHIVED:
        get_csv()
    data_dict = parse_csv()
    for entry in data_dict:
        if parse(f"{year}-{month}-{day}") == parse(entry["Datum"], dayfirst=True):
            formatted_date_string = datetime.date(int(year), int(month), int(day)).strftime("%d/%m/%Y")
            await ctx.send(embed=format_data(formatted_date_string, entry))
            return
    await ctx.send(embed=discord.Embed(title="Data for selected day not found"))


@info.error
async def info_error(ctx, error) -> None:
    await ctx.send("```Usage: !info <day> <month> [year (2020 by default)]```")


@bot.command(name='ping')
async def ping(ctx) -> None:
    await ctx.send("```Pong!```")



"""----------MAIN----------"""

def main():
    if not os.path.isfile(CONFIG_FILE):
        print("No configuration file found.")
        print("Please enter your connection string into the file and rerun the program.")
        data = { "connection_string" : "" }
        with open(CONFIG_FILE, "w") as new_file:
            yaml.dump(data, new_file)
    else:
        with open(CONFIG_FILE, "r") as config_file:
            config = yaml.safe_load(config_file)
        bot.run(config["connection_string"])


if __name__ == "__main__":
    main()