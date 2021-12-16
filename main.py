import os
from keep_alive import keep_alive
import discord
import time
from discord.ext import commands
from botutil import buildEmb, seperate_number
import botdb
import requests
import asyncio
from datetime import datetime
from discord_components import *
botdb.setupdb()
# ----------
STANDARDPREFIX = "c!"
global PREFIX
PREFIX = "c!"
VERSION = "1.3.2"
COLOR = 0xF94242
# ----------

async def get_prefix(bot, message):
    global PREFIX
    global custom_prefix
    guild = message.guild
    #Only allow custom prefixs in guild
    if guild:
        custom_prefixcheck = botdb.selectwhere("server_settings", "prefix", f"guild_id={guild.id}")
        if custom_prefixcheck == []:
            botdb.insert("server_settings","guild_id, prefix", f"{guild.id}, '{STANDARDPREFIX}'")
        custom_prefix = botdb.selectwhere("server_settings", "prefix", f"guild_id={guild.id}")
        PREFIX = str(custom_prefix[0]).replace("(", "").replace(")", "").replace("'", "").replace(",", "")
        return custom_prefix[0]
    else:
        PREFIX = STANDARDPREFIX
        return PREFIX

bot = commands.Bot(command_prefix=get_prefix)
DiscordComponents(bot)
bot.remove_command("help")
@bot.event
async def on_ready():
    print("-----------")
    print(f"{bot.user.name} is online!")
    print("-----------")

    while True:
        count = 0
        for guild in bot.guilds:
            count += guild.member_count
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing,
                                                               name="❤️| auf " + str(len(bot.guilds)) + " Servern!"))
        await asyncio.sleep(10)
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing,
                                                               name="❤️| mit " + str(count) + " Usern!"))
        await asyncio.sleep(10)
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing,
                                                               name="❤️| Echtzeit Corona Daten"))
        await asyncio.sleep(10)
        if str(datetime.now().time())[:5] == "13:00":
            print("updated 1")
            for guild in bot.guilds:
                response = requests.get("https://api.corona-zahlen.org/germany")
                response = response.json()
                for channel in guild.channels:
                    if "Inzidenz・" in channel.name:
                        await channel.edit(name=f"Inzidenz・{str(round(response['weekIncidence'], 3)).replace('.', ',')}")
                    if "Fälle pro Woche・" in channel.name:
                        await channel.edit(name=f"Fälle pro Woche・{seperate_number(int(response['casesPerWeek']))}")
                    if "Hospitalisierung・" in channel.name:
                        await channel.edit(name=f"Hospitalisierung・{str(round((response['hospitalization']['incidence7Days']), 3)).replace('.', ',')}")
            print("updated 2")


@bot.command(name="help", help="Zeigt eine Hilfe Ansicht an",
                  description=f"Dieser Command erklärt dir alle Commands! \n**Benutzung:** `PREFIXVARhelp <Command>`")
async def help_cmd(ctx, *args):
    if not args:
        helptext = "────────────────────\n"
        for command in bot.commands:
            helptext += f"**{PREFIX}{command}** | {command.help}\n"
        helptext += "────────────────────\n \u200b"
        await ctx.send(embed=buildEmb("Help", helptext))
    elif len(args) == 1:

        for command in bot.commands:
            if command.name == args[0]:
                await ctx.send(embed=buildEmb(f"Erklärung | {PREFIX}{command.name}",
                                              "" + str(command.description).replace("PREFIXVAR", PREFIX) + "\n \u200b \n_In '<>' stehende Argumente sind optional_ \n _In '[]' stehende Argumente sind für die Benutzung nötig_"))
                return

        errmsg = await ctx.send(
            embed=buildEmb(f":no_entry_sign: 〢 Fehler", "Konnte keinen Command mit diesem Namen finden"))
        time.sleep(5)
        await errmsg.delete()

    else:
        errmsg = await ctx.send(
            embed=buildEmb(":no_entry_sign: 〢 Fehler", f"Benutze `{PREFIX}help <Command>` oder `{PREFIX}help`"))
        time.sleep(5)
        await errmsg.delete()

@bot.command(name="setupstats", help="Erstellt Channel mit aktuellen Corona Daten!",
                  description=f"Dieser Command erstellt Channel um dir wie bei einem Server Stats Bot die aktuellen Corona Zahlen von Deutschland anzuzeigen!\n**Benutzung:**\n`PREFIXVARsetupstats`")
@commands.guild_only()
@commands.has_permissions(administrator=True)
async def stats_cmd(ctx):
    try:

        await ctx.send(embed=buildEmb("Setup | Starte Setup", "Das Setup wurde gestartet"))
        response = requests.get("https://api.corona-zahlen.org/germany")
        response = response.json()
        category = await ctx.guild.create_category("📊  ・ CoronaStats", overwrites=None, reason=None)
        await category.set_permissions(ctx.guild.default_role, connect=False, view_channel=True)


        await ctx.guild.create_voice_channel(f"Inzidenz・{str(round(response['weekIncidence'], 3)).replace('.', ',')}", overwrites=None, category=category, reason=None)
        await ctx.guild.create_voice_channel(f"Fälle pro Woche・{seperate_number(int(response['casesPerWeek']))}",
                                             overwrites=None, category=category, reason=None)
        await ctx.guild.create_voice_channel(f"Hospitalisierung・{str(round((response['hospitalization']['incidence7Days']), 3)).replace('.', ',')}",
                                             overwrites=None, category=category, reason=None)
        await ctx.send(embed=buildEmb("Setup | Fertiggestellt", "Das Setup wurde erfolgreich fertiggestellt"))

    except Exception:
        await ctx.send(embed=buildEmb("Setup | Fehler", f"Bitte überprüfe die Berechtigungen des Bots!"))




@bot.command(name="stats", aliases=["coronastats", "corona", "citystats", "zahlen"], help="Zeigt eine Liste an aktuellen Zahlen an",
                  description=f"Dieser Command zeigt dir die aktuellen Corona Zahlen von Deutschland oder einer Stadt!\n**Benutzung:**\n`PREFIXVARstats <Stadtname>` \n oder \n`{PREFIX}stats`")
async def stats_cmd(ctx, *args):
    try:
        if not args:
            response = requests.get("https://api.corona-zahlen.org/germany")
            response = response.json()
            e = discord.Embed(title="Coronazahlen | Deutschland", colour=COLOR, timestamp=datetime.utcnow(), description="Alle wichtigen aktuellen Zahlen mit Daten des RKIs! \n _Letzes Update: " +
                              str(datetime.strptime(response["meta"]["lastUpdate"],"%Y-%m-%dT%H:%M:%S.%fZ")) + "_")
            e.set_footer(text="CoronaStats Bot ",
                         icon_url="https://cdn.discordapp.com/avatars/917807713948418048/c4d836e14dccf875c9ccdc1023574fee.png?size=32")

            e.add_field(name='Insgesamte Infizierte', value=" " + seperate_number(int(response["cases"])), inline=True)
            e.add_field(name='Insgesamte Tode', value=" " + seperate_number(int(response["deaths"])), inline=True)
            e.add_field(name='Insgesamte Geheilte', value=" " + seperate_number(int(response["recovered"])), inline=True)
            e.add_field(name='7 Tage Inzidenz', value=" " + str(round(response["weekIncidence"], 3)).replace('.', ','), inline=True)
            e.add_field(name='Fälle pro Woche', value=" " + seperate_number(int(response["casesPerWeek"])), inline=True)
            e.add_field(name='Hospitalisierungsrate', value=" " + str(round((response["hospitalization"]["incidence7Days"]), 3)).replace('.', ','), inline=True)
            await ctx.send(embed=e)
        elif args[0]:
                response = requests.get("https://api.corona-zahlen.org/districts")
                response = response.json()
                args = list(args)
                cityname = ' '.join(map(str,args))
                v = False
                l = False
                for namecode in response["data"].keys():
                    if response["data"][namecode]["name"] == args[0]:
                        v = True
                        response1 = response["data"][namecode]

                if v == False:
                    errmsg = await ctx.send(
                            embed=buildEmb(":no_entry_sign: 〢 Fehler", f"Die Stadt `{cityname}` wurde leider nicht gefunden!"))
                    time.sleep(5)
                    await errmsg.delete()
                else:
                    e = discord.Embed(title=f"Coronazahlen | " + cityname, colour=COLOR, timestamp=datetime.utcnow(), description="Alle wichtigen aktuellen Zahlen mit Daten des RKIs! \n _Letzes Update: " +
                                          str(datetime.strptime(response["meta"]["lastUpdate"],"%Y-%m-%dT%H:%M:%S.%fZ")) + "_")
                    e.set_footer(text="CoronaStats Bot ",
                                     icon_url="https://cdn.discordapp.com/avatars/917807713948418048/c4d836e14dccf875c9ccdc1023574fee.png?size=32")

                    e.add_field(name='Insgesamte Infizierte', value=" " + seperate_number(int(response1["cases"])), inline=True)
                    e.add_field(name='Insgesamte Tode', value=" " + seperate_number(int(response1["deaths"])), inline=True)
                    e.add_field(name='Insgesamte Geheilte', value=" " + seperate_number(int(response1["recovered"])), inline=True)
                    e.add_field(name='7 Tage Inzidenz', value=" " + str(round(response1["weekIncidence"], 3)).replace('.', ','), inline=True)
                    e.add_field(name='Fälle pro Woche', value=" " + seperate_number(int(response1["casesPerWeek"])), inline=True)
                    await ctx.send(embed=e)
        else:
            response = requests.get("https://api.corona-zahlen.org/germany")
            response = response.json()
            e = discord.Embed(title="Coronazahlen | Deutschland", colour=COLOR, timestamp=datetime.utcnow(), description="Alle wichtigen aktuellen Zahlen mit Daten des RKIs! \n _Letzes Update: " +
                              str(datetime.strptime(response["meta"]["lastUpdate"],"%Y-%m-%dT%H:%M:%S.%fZ")) + "_")
            e.set_footer(text="CoronaStats Bot ",
                         icon_url="https://cdn.discordapp.com/avatars/917807713948418048/c4d836e14dccf875c9ccdc1023574fee.png?size=32")

            e.add_field(name='Insgesamte Infizierte', value=" " + seperate_number(int(response["cases"])), inline=True)
            e.add_field(name='Insgesamte Tode', value=" " + seperate_number(int(response["deaths"])), inline=True)
            e.add_field(name='Insgesamte Geheilte', value=" " + seperate_number(int(response["recovered"])), inline=True)
            e.add_field(name='7 Tage Inzidenz', value=" " + str(round(response["weekIncidence"], 3)).replace('.', ','), inline=True)
            e.add_field(name='Fälle pro Woche', value=" " + seperate_number(int(response["casesPerWeek"])), inline=True)
            e.add_field(name='Hospitalisierungsrate', value=" " + str(round((response["hospitalization"]["incidence7Days"]), 3)).replace('.', ','), inline=True)
            await ctx.send(embed=e)
    except Exception:
        pass


@bot.command(name="map", help="Zeigt eine Deutschland Karte mit nach Inzidenz gefärbten Gebieten an",
                  description=f"Dieser Command zeigt dir eine Karte von Deutschland an, die dir mit verschiedenen Farben die aktuellen Inzidenz-Zahlen in den Regionen angibt\n**Benutzung:** `PREFIXVARmap`")
async def map_cmd(ctx):
    map_e = discord.Embed(title="Corona Map | Deutschland", colour=COLOR, description="Hier siehst du eine Karte mit nach Inzidenz gefärbten Gebieten", timestamp=datetime.utcnow())
    map_e.set_footer(text="CoronaStats Bot ",
                 icon_url="https://cdn.discordapp.com/avatars/917807713948418048/c4d836e14dccf875c9ccdc1023574fee.png?size=32")
    map_e.set_image(url="https://api.corona-zahlen.org/map/districts-legend")
    await ctx.send(embed=map_e)


@bot.command(name="info", help="Zeigt wichtige Informationen über den Bot an",
                  description=f"Dieser Command zeigt dir Informationen und Quellen von unserem Bot an!\n**Benutzung:** `PREFIXVARinfo`")
async def info_cmd(ctx):
    await ctx.send(embed=buildEmb("Informationen | Bot", "────────────────────\n \u200b \n Der Bot wurde von `ᴢᴇɴ#0001` entwickelt."
                                                   "\nDas System arbeitet mit der **RestAPI des RKIs (Robert Koch Institut) mit Echtzeitdaten**\n"
                                                   "Der Bot soll zur **Aufklärung und Informationsquelle** für die Corona-Pandemie dienen\n"
                                                   "Falls Probleme, Bugs oder anderer Gesprächsbedarf besteht, **melde dich bitte per DM!**\n"
                                                   "_Die Daten sind nur auf Deutschland zugewiesen. Wir übernehmen keine Haftung für fehlerhafte Informationen oder Ausfälle der RestAPI_\n \u200b \n────────────────────\n"))

@bot.command(name="setprefix", help="Setzt den Server Prefix ",
                  description=f"Mit diesem Command setzt du einen eigenen Prefix für den Bot auf deinem Server!\n**Benutzung:** `PREFIXVARsetprefix [Prefix]`")
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def setprefix_cmd(ctx, *args):
    global PREFIX

    if args:
        if len(args[0]) <= 7:
            botdb.updatewhere("server_settings", f"prefix='{args[0]}'", f"guild_id={ctx.guild.id}")
            PREFIX = args[0]
            await ctx.send(embed=buildEmb("Prefix | Erfolgreich", f"Der Server Prefix wurde zu `{args[0]} geändert!`"))
        else:
            errmsg = await ctx.send(
                embed=buildEmb(":no_entry_sign: 〢 Fehler", f"Der Prefix darf nicht länger als 7 Zeichen sein!"))
            time.sleep(5)
            await errmsg.delete()
    else:
        errmsg = await ctx.send(
            embed=buildEmb(":no_entry_sign: 〢 Fehler", f"Benutzung: `{PREFIX}setprefix [Prefix]`"))
        time.sleep(5)
        await errmsg.delete()

@bot.command(name="invite", help="Lade diesen Bot auf deinen Server ein!",
                  description=f"Dieser Command gibt dir den Invite Link, um unseren Bot einzuladen!\n**Benutzung:** `PREFIXVARinvite`")
async def invite_cmd(ctx):
    await ctx.send(embed=buildEmb("Invite | Bot", "────────────────────\n \u200b "
                                                  "\n Du kannst mich [hier](https://discord.com/api/oauth2/authorize?client_id=917807713948418048&permissions=412317248592&scope=bot) "
                                                  "einladen!\n \u200b \n────────────────────\n"))

@bot.command(name="vote", help="Vote für unseren Bot!",
                  description=f"Dieser Command gibt dir den Vote Link für unseren Bot!\n**Benutzung:** `PREFIXVARvote`")
async def vote_cmd(ctx):
    await ctx.send(embed=buildEmb("Vote | Bot", "────────────────────\n \u200b "
                                                  "\n Du kannst [hier](https://top.gg/bot/917807713948418048/vote) für unseren Bot voten!"
                                                  "\n \u200b \n────────────────────\n"))

def getpercentage(part, whole):
  return 100 * float(part)/float(whole)


@bot.command(name="impfung", aliases=["impfungen", "vaccination"], help="Zeigt dir Informationen zu den Impfungen an",
                  description=f"Dieser Command zeigt dir alle wichtigen Informationen rund um die aktuelle Impf-Lage an!\n**Benutzung:** `PREFIXVARimpfung <states>`")
async def impfung_cmd(ctx, *args):
    if not args:
        response = requests.get("https://api.corona-zahlen.org/vaccinations")
        response = response.json()
        e = discord.Embed(title="Impfungen | Deutschland", colour=COLOR, timestamp=datetime.utcnow(),
                          description="Alle wichtigen aktuellen Zahlen zu den Impfungen mit Daten des RKIs! \n _Letzes Update: " +
                                      str(datetime.strptime(response["meta"]["lastUpdate"], "%Y-%m-%dT%H:%M:%S.%fZ")) + "_")
        e.set_footer(text="CoronaStats Bot ",
                     icon_url="https://cdn.discordapp.com/avatars/917807713948418048/c4d836e14dccf875c9ccdc1023574fee.png?size=32")

        e.add_field(name='Ingesamte Impfungen', value=" " + seperate_number(int(response["data"]["administeredVaccinations"])), inline=True)
        e.add_field(name='Impfungquote', value=" " + str(round(response["data"]["quote"], 3)*100).replace('.', ',') + "%", inline=True)
        e.add_field(name='1 / 2 Impfungen', value=" " + seperate_number(int(response["data"]["vaccinated"])), inline=True)
        e.add_field(name='2 / 2 Impfungen', value=" " + seperate_number(int(response["data"]["secondVaccination"]["vaccinated"])), inline=True)
        e.add_field(name='Geboostet', value=" " + seperate_number(int(response["data"]["boosterVaccination"]["vaccinated"])), inline=True)
        e.add_field(name='Gestern Geimpft', value=" " + seperate_number(int(response["data"]["latestDailyVaccinations"]["vaccinated"])), inline=True)
        e.add_field(name='Impfstoffe',value="Biontech: **" + str(round(getpercentage(int(response["data"]["vaccination"]["biontech"]), int(response["data"]["vaccinated"])),2)).replace('.', ',') +
                                            "%**\nModerna: **" + str(round(getpercentage(int(response["data"]["vaccination"]["moderna"]), int(response["data"]["vaccinated"])),2)).replace('.', ',') +
                                            "%**\nAstraZeneca: **" + str(round(getpercentage(int(response["data"]["vaccination"]["astraZeneca"]), int(response["data"]["vaccinated"])),2)).replace('.', ',') +
                                            "%**\nJanssen: **" + str(round(getpercentage(int(response["data"]["vaccination"]["janssen"]), int(response["data"]["vaccinated"])),2)).replace('.', ',') + "%**",inline=True)
        await ctx.send(embed=e)

    elif len(args) == 1:
        if args[0] == "states":
            response = requests.get("https://api.corona-zahlen.org/vaccinations")
            response = response.json()
            t = []
            for namecode in response["data"]["states"].keys():
                t.append(SelectOption(label=str(response["data"]["states"][namecode]["name"]),
                                      value=str(response["data"]["states"][namecode]["name"])))

            await ctx.send(embed=buildEmb("Impfungen | Bundesländer",
                                          "Wähle unten ein Bundesland aus, um aktuelle Impfungens-Daten über dieses zu erhalten!"),
                           components=[
                               Select(
                                   placeholder="Wähle ein Bundesland",
                                   options=t
                               )
                           ])

            res = await bot.wait_for("select_option")
            if res.channel == ctx.message.channel:
                    response1 = []
                    cityname = str({res.values[0]}).replace("'", "").replace("{", "").replace("}", "")
                    v = False
                    for namecode in response["data"]["states"].keys():
                        if response["data"]["states"][namecode]["name"] == cityname:
                            v = True
                            response1 = response["data"]["states"][namecode]

                    e = discord.Embed(title=f"Impfungen | {response1['name']}", colour=COLOR, timestamp=datetime.utcnow(),
                                      description="Alle wichtigen aktuellen Zahlen zu den Impfungen mit Daten des RKIs! \n _Letzes Update: " +
                                                  str(datetime.strptime(response["meta"]["lastUpdate"], "%Y-%m-%dT%H:%M:%S.%fZ")) + "_")
                    e.set_footer(text="CoronaStats Bot ",
                                 icon_url="https://cdn.discordapp.com/avatars/917807713948418048/c4d836e14dccf875c9ccdc1023574fee.png?size=32")

                    e.add_field(name='Ingesamte Impfungen', value=" " + seperate_number(int(response1["administeredVaccinations"])), inline=True)
                    e.add_field(name='Impfungquote', value=" " + str(round(response1["quote"], 3)*100).replace('.', ',') + "%", inline=True)
                    e.add_field(name='1 / 2 Impfungen', value=" " + seperate_number(int(response1["vaccinated"])), inline=True)
                    e.add_field(name='2 / 2 Impfungen', value=" " + seperate_number(int(response1["secondVaccination"]["vaccinated"])), inline=True)
                    e.add_field(name='Geboostet', value=" " + seperate_number(int(response1["boosterVaccination"]["vaccinated"])), inline=True)
                    e.add_field(name='Impfstoffe',value="Biontech: **" + str(round(getpercentage(int(response1["vaccination"]["biontech"]), int(response1["vaccinated"])),2)).replace('.', ',') +
                                                        "%**\nModerna: **" + str(round(getpercentage(int(response1["vaccination"]["moderna"]), int(response1["vaccinated"])),2)).replace('.', ',') +
                                                        "%**\nAstraZeneca: **" + str(round(getpercentage(int(response1["vaccination"]["astraZeneca"]), int(response1["vaccinated"])),2)).replace('.', ',') +
                                                        "%**\nJanssen: **" + str(round(getpercentage(int(response1["vaccination"]["janssen"]), int(response1["vaccinated"])),2)).replace('.', ',') + "%**",inline=False)
                    await res.send(embed=e)






@bot.command(name="states" , aliases=["bundesland", "bundesländer"], help="Zeigt dir Corona Informationen zu den Bundesländern an",
                  description=f"Dieser Command zeigt dir alle wichtigen Informationen über die Bundesländer von Deutschland an! \n**Benutzung:** `PREFIXVARstates`")
async def states_cmd(ctx):
    response = requests.get("https://api.corona-zahlen.org/states")
    response = response.json()
    t = []
    for namecode in response["data"].keys():
        t.append(SelectOption(label=str(response["data"][namecode]["name"]), value=str(response["data"][namecode]["name"])))


    await ctx.send(embed=buildEmb("Corona | Bundesländer", "Wähle unten ein Bundesland aus, um aktuelle Corona Daten über dieses zu erhalten!"), components=[
        Select(
            placeholder="Wähle ein Bundesland",
            options = t
        )
    ])

    res = await bot.wait_for("select_option")
    if res.channel == ctx.message.channel:
            response1 = []
            cityname = str({res.values[0]}).replace("'", "").replace("{", "").replace("}", "")
            v = False
            for namecode in response["data"].keys():
                if response["data"][namecode]["name"] == cityname:
                    v = True
                    response1 = response["data"][namecode]
            e = discord.Embed(title=f"Coronazahlen | " + cityname, colour=COLOR, timestamp=datetime.utcnow(),
                              description="Alle wichtigen aktuellen Zahlen mit Daten des RKIs! \n _Letzes Update: " +
                                          str(datetime.strptime(response["meta"]["lastUpdate"],
                                                                "%Y-%m-%dT%H:%M:%S.%fZ")) + "_")
            e.set_footer(text="CoronaStats Bot ",
                         icon_url="https://cdn.discordapp.com/avatars/917807713948418048/c4d836e14dccf875c9ccdc1023574fee.png?size=32")

            e.add_field(name='Insgesamte Infizierte', value=" " + seperate_number(int(response1["cases"])), inline=True)
            e.add_field(name='Insgesamte Tode', value=" " + seperate_number(int(response1["deaths"])), inline=True)
            e.add_field(name='Insgesamte Geheilte', value=" " + seperate_number(int(response1["recovered"])),
                        inline=True)
            e.add_field(name='7 Tage Inzidenz', value=" " + str(round(response1["weekIncidence"], 3)).replace('.', ','),
                        inline=True)
            e.add_field(name='Fälle pro Woche', value=" " + seperate_number(int(response1["casesPerWeek"])),
                        inline=True)
            await res.send(embed=e)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        errmsg = await ctx.send(
            embed=buildEmb(":no_entry_sign: 〢 Fehler", "Du hast **keine Rechte** diesen Command auszuführen!\n _ _ "))
        time.sleep(5)
        await errmsg.delete()





keep_alive()
bot.run(os.environ['token'])
