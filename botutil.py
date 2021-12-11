import discord
import datetime

#----------
PREFIX = "c!"
VERSION = "1.1.2"
COLOR = 0xF94242
#----------



def buildEmb(title, text):
    e = discord.Embed(title=title, colour=COLOR, description=text, timestamp=datetime.datetime.utcnow())
    e.set_footer(text="CoronaStats Bot ",
                 icon_url="https://cdn.discordapp.com/avatars/917807713948418048/c4d836e14dccf875c9ccdc1023574fee.png?size=32")
    return e

def seperate_number(nr):
    seperated_nr = ""
    for enu, part_nr in enumerate(str(nr)[::-1]):
        if (enu + 1) % 3 == 0 and enu != len(str(nr)) - 1:
            seperated_nr += part_nr + "."
        else:
            seperated_nr += part_nr
    return seperated_nr[::-1]