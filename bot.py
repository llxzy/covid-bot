import csv
import datetime
from dateutil.parser import parse
import discord
import yaml
import urllib.request
from discord.ext import commands

bot = commands.Bot(command_prefix='!')

LAST_ARCHIVED = datetime.date(2020, 7, 4)
DATA_URL = "https://mapa.covid.chat/export/csv"

#TODO
# config file
# date formatting
# arguments for command
# help function

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
            # if datetime.datetime(2020, 7, 3) == parse(i["Datum"], dayfirst=True):

@bot.command(name='info')
async def info(ctx, year, month, day):
    #TODO set defaults for y m d
    if datetime.date.today() != LAST_ARCHIVED:
        get_csv()
    data_dict = parse_csv()
    date_string = f"{year}-{month}-{day}"
    for entry in data_dict:
        if parse(date_string) == parse(entry["Datum"], dayfirst=True):
            today = entry["Datum"]
            m_embed = discord.Embed(title=f"Data for {date_string}")
            #TODO move to separate func
            m_embed.add_field(name="Total cases", value=entry["Pocet potvrdenych"])
            m_embed.add_field(name="New cases", value=entry["Dennych prirastkov"])
            m_embed.add_field(name="Daily tested", value=entry["Dennych testov"])
            #await ctx.send(f"The value for today is {today}")
            await ctx.send(embed=m_embed)
            return
    ctx.send("Data for selected day not found.")



def main():
    # todo Setup connection string on first startup, else bot.run(connection_string)
    bot.run('CONNECTION STRING')

if __name__ == "__main__":
    main()