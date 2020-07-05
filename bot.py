import csv
import datetime
from dateutil.parser import parse
import discord
import os
import yaml
import urllib.request
from discord.ext import commands

bot = commands.Bot(command_prefix='!')
bot.remove_command('help')

LAST_ARCHIVED = datetime.date(2020, 7, 4)
DATA_URL = "https://mapa.covid.chat/export/csv"

#TODO
# date formatting
# arguments for command

def get_csv() -> bool:
    """
    Checks whether there is a newer version of covid data .csv file on korona.gov.sk,
    if it finds one then it downloads and updates data.
    ALTERNATIVE: do a script that runs and select time that updates the data and dl's the .csv file.
    """
    try:
        urllib.request.urlretrieve(DATA_URL, "data.csv")
        LAST_ARCHIVED = datetime.date.today()
        return True
    except:
        return False


def parse_csv() -> list:
    dt = []
    with open("./data.csv", "r") as csv_file:
        csv_data = csv.DictReader(csv_file, delimiter=';')
        for row in csv_data:
            dt.append(row)
    return dt


def format_data(date_str: str, row: dict) -> discord.Embed:
    embed = discord.Embed(title=f"Data for {date_str}")
    embed.add_field(name="Confirmed", value=row["Pocet potvrdenych"])
    embed.add_field(name="Active", value=row["Pocet aktivnych"])
    embed.add_field(name="Cured", value=row["Pocet vyliecenych"])
    embed.add_field(name="New tested", value=row["Dennych testov"])
    embed.add_field(name="New cases", value=row["Dennych prirastkov"])
    embed.add_field(name="Total deaths", value=row["Pocet umrti"])
    return embed

"""
----------------------------------------------------------------
"""

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="!help for a list of commands"))


@bot.command(name='help')
async def help_msg(ctx) -> None:
    m_embed = discord.Embed()
    m_embed.add_field(name="Commands", value="help, source, info (WIP)")
    await ctx.send(embed=m_embed)


@bot.command(name='source')
async def source_msg(ctx) -> None:
    m_embed = discord.Embed()
    m_embed.add_field(name="Source code available at:", value="https://github.com/llxzy/covid-bot")
    await ctx.send(embed=m_embed)


@bot.command(name='info')
async def info(ctx, year: str, month: str, day: str):
    if datetime.date.today() != LAST_ARCHIVED:
        get_csv()
    data_dict = parse_csv()
    for entry in data_dict:
        if parse(f"{year}-{month}-{day}") == parse(entry["Datum"], dayfirst=True):
            formatted_date_string = datetime.date(int(year), int(month), int(day)).strftime("%d/%m/%Y")
            await ctx.send(embed=format_data(formatted_date_string, entry))
    await ctx.send(embed=discord.Embed(title="Data for selected day not found"))


@info.error
async def info_error(ctx, error):
    await ctx.send("```Usage: !info <year> <month> <day>```")


def main():
    if not os.path.isfile("config.yaml"):
        print("No configuration file found.")
        print("Please enter your connection string into the file and rerun the program.")
        data = {"connection_string" : ""}
        with open("config.yaml", "w") as new_file:
            yaml.dump(data, new_file)
    else:
        with open("config.yaml", "r") as config_file:
            config = yaml.safe_load(config_file)
        bot.run(config["connection_string"])

if __name__ == "__main__":
    main()