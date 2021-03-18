import discord
from discord.ext import commands
from dotenv import load_dotenv
from random import randint
import os
from datetime import datetime
from utils import database

description = "Ein Bot der eine virtuelle Bank simuliert."
bot = commands.Bot(command_prefix=".", description=description)

load_dotenv()
#DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
botOwner = ["215080717560971264", "405843581534994433"]

udb = database.UserDB("user.db")
cdb = database.ClaimDB("claim.db")
fdb = database.FlipDB("flip.db")


@bot.event
async def on_ready():
  guild_count = 0
  
  print("Logged in as")
  print(bot.user.name)
  print(bot.user.id)
  print("------")
  
  for guild in bot.guilds:
    print("{0} : {1}".format(guild.id, guild.name))
    guild_count = guild_count + 1
  
  await bot.change_presence(activity=discord.Game(name="on " + str(guild_count) + " servers | .help"))
  
  print("Bot is in " + str(guild_count) + " guilds")

    
@bot.command(description="Testet den Ping des Bots", help="Testet den Ping des Bots")
async def ping(ctx):
  await ctx.send("Pong! Bot latency: {0}".format(bot.latency))


@bot.command(description="Registriere dein Konto", help="Registriere dein Konto")
async def signup(ctx):
  userBalance = udb.get(str(ctx.author.id))
  now = datetime.now()
  datenow = now.strftime("%d-%m-%Y")
  if userBalance == None:
    udb.set(str(ctx.author.id), 20)
    cdb.set(str(ctx.author.id), "none")
    fdb.set(str(ctx.author.id), [0, datenow])
    await ctx.send("Dein Konto bei **ehrebank** wurde eröffnet. Als Willkommensgeschenk bekommst du `20 EHRE`!")
  else:
    await ctx.send("Du hast schon ein Konto eröffnet.")


@bot.command(description="Zeige deinen Kontostand an", help="Zeige deinen Kontostand an")
async def balance(ctx):
  try:
    mentionedID = str(ctx.message.mentions[0].id)
    mentionedBalance = udb.get(mentionedID)
    if mentionedBalance == None:
      await ctx.send("Der Benutzer hat noch kein Konto und muss es erst mit `.signup` erstellen.")
    else:
      await ctx.send(f"Der Kontostand von {ctx.message.mentions[0]} bei der **ehrebank** ist: `{mentionedBalance} EHRE`")
  except:
    mentionedID = str(ctx.author.id)
    mentionedBalance = udb.get(mentionedID)
    if mentionedBalance == None:
      await ctx.send("Der Benutzer hat noch kein Konto und muss es erst mit `.signup` erstellen.")
    else:
      await ctx.send(f"Dein Kontostand bei der **ehrebank** ist: `{mentionedBalance} EHRE`")


@bot.command(description="Sende EHRE", help="Sende EHRE")
async def send(ctx, amount: int):
  senderBalance = udb.get(str(ctx.author.id))
  if senderBalance == None:
    await ctx.send("Bitte eröffne zuerst ein Konto mit `.signup`!")
  else:
    if senderBalance < amount:
      await ctx.send("Dein Kontostand kann diesen Betrag nicht decken. Wähle einen kleineren Betrag.")
    else:
      receiverID = str(ctx.message.mentions[0].id)
      receiverBalance = udb.get(receiverID)
      if receiverBalance == None:
        await ctx.send("Der Empfänger hat noch kein Konto und muss es erst mit `.signup` erstellen.")
      else:
        if amount < 0:
          await ctx.send("Nice try! Es können keine Minusbeträge gesendet werden.")
        else:
          newReceiverBalance = receiverBalance + amount
          newSenderBalance = senderBalance - amount
          senderID = str(ctx.author.id)
          udb.set(receiverID, newReceiverBalance)
          udb.set(senderID, newSenderBalance)
          await ctx.send(f"Transaktion fertig! `{amount} EHRE` wurde(n) zu `{ctx.message.mentions[0]}` gesendet.")
          await ctx.message.mentions[0].send(f"`{amount} EHRE` wurde(n) dir von `{ctx.author}` gesendet.")


@bot.command(description="Gebe EHRE", help="Gebe EHRE (kann nur der Bot Besitzer)")
async def give(ctx, amount: int):
  if str(ctx.author.id) in botOwner:
    senderBalance = udb.get(str(ctx.author.id))
    if senderBalance == None:
      await ctx.send("Bitte eröffne zuerst ein Konto mit `>signup`!")
    else:
      receiverID = str(ctx.message.mentions[0].id)
      receiverBalance = udb.get(receiverID)
      if receiverBalance == None:
        await ctx.send("Der Empfänger hat noch kein Konto und muss es erst mit `.signup` erstellen.")
      else:
        if amount < 0:
          await ctx.send("Nice try! Es können keine Minusbeträge gesendet werden.")
        else:
          newReceiverBalance = receiverBalance + amount
          senderID = str(ctx.author.id)
          udb.set(receiverID, newReceiverBalance)
          await ctx.send(f"Transaktion fertig! `{amount} EHRE` wurde(n) zu `{ctx.message.mentions[0]}` gegeben.")
          await ctx.message.mentions[0].send(f"`{amount} EHRE` wurde(n) dir gegeben.")
  else:
    await ctx.send("Du must der Bot Besitzer sein um diese Aktion ausführen zu können.")


@bot.command(description="Claime täglich EHRE", help="Claime täglich EHRE")
async def claim(ctx):      
  userBalance = udb.get(str(ctx.author.id))
  lastClaim = cdb.get(str(ctx.author.id))
  if userBalance == None:
    await ctx.send("Bitte eröffne zuerst ein Konto mit `.signup`!")
  else:
    if lastClaim == False:
      cdb.set(str(ctx.author.id), "None")
      
    now = datetime.now()
    datenow = now.strftime("%d-%m-%Y")

    if lastClaim != datenow:
      newUserBalance = userBalance + 5
      udb.set(str(ctx.author.id), newUserBalance)
      cdb.set(str(ctx.author.id), datenow)
      await ctx.send("Du hast `5 EHRE` geclaimt!")
    elif lastClaim == "none":
      newUserBalance = userBalance + 5
      udb.set(str(ctx.author.id), newUserBalance)
      cdb.set(str(ctx.author.id), datenow)
      await ctx.send("Du hast `5 EHRE` geclaimt!")
    else:
      await ctx.send("Du kannst erst morgen wieder `EHRE` claimen, alla!")


@bot.command(description="Zeige die aktuelle Shopseite", help="Zeige die aktuelle Shopseite")
async def shop(ctx):
  await ctx.send("**EHRE SHOP** \n`50 EHRE` Ritter \n`100 EHRE` Adel \n`500 EHRE` König \n`1000 EHRE` Gottheit \n \n Schreibe `.buy [Name des Items]` um etwas zu kaufen")


@bot.command(description="Kaufe ein Item aus dem Shop", help="Kaufe ein Item aus dem Shop")
async def buy(ctx, item: str):
  member = ctx.author
  memberRoles = str(member.roles)
  roleItem1 = discord.utils.get(ctx.guild.roles, name="Ritter")
  roleItem2 = discord.utils.get(ctx.guild.roles, name="Adel")
  roleItem3 = discord.utils.get(ctx.guild.roles, name="König")
  roleItem4 = discord.utils.get(ctx.guild.roles, name="Gottheit")
  
  if item == "Ritter":
    if memberRoles.find("Ritter") >= 0:
      await ctx.send("Wait a second! Die Rolle hast du schon! Schande!")
    else:
      price = 50
      balance = udb.get(str(ctx.author.id))
      if balance == None:
        await ctx.send("Bitte eröffne zuerst ein Konto mit `.signup`!")
      else:
        if balance < price:
          await ctx.send("Dein Kontostand kann diesen Betrag nicht decken.")
        else:
          newBalance = balance - price
          memberID = str(ctx.author.id)
          udb.set(memberID, newBalance)
          await member.add_roles(roleItem1, reason=None, atomic=True)
          await ctx.send("Du hast `Ritter` für `50 EHRE` gekauft! EHRE!")
  elif item == "Adel":
    if memberRoles.find("Adel") >= 0:
      await ctx.send("Wait a second! Die Rolle hast du schon! Schande!")
    else:
      price = 100
      balance = udb.get(str(ctx.author.id))
      if balance == None:
        await ctx.send("Bitte eröffne zuerst ein Konto mit `.signup`!")
      else:
        if balance < price:
          await ctx.send("Dein Kontostand kann diesen Betrag nicht decken.")
        else:
          newBalance = balance - price
          memberID = str(ctx.author.id)
          udb.set(memberID, newBalance)
          await member.add_roles(roleItem2, reason=None, atomic=True)
          await ctx.send("Du hast `Adel` für `100 EHRE` gekauft! SEHR EHRENVOLL!")
  elif item == "König":
    if memberRoles.find("König") >= 0:
      await ctx.send("Wait a second! Die Rolle hast du schon! Schande!")
    else:
      price = 500
      balance = udb.get(str(ctx.author.id))
      if balance == None:
        await ctx.send("Bitte eröffne zuerst ein Konto mit `.signup`!")
      else:
        if balance < price:
          await ctx.send("Dein Kontostand kann diesen Betrag nicht decken.")
        else:
          newBalance = balance - price
          memberID = str(ctx.author.id)
          udb.set(memberID, newBalance)
          await member.add_roles(roleItem3, reason=None, atomic=True)
          await ctx.send("Du hast `König` für `500 EHRE` gekauft! EIN WAHRHAFTER EHRENBARON!")
  elif item == "Gottheit":
    if memberRoles.find("Gottheit") >= 0:
      await ctx.send("Wait a second! Die Rolle hast du schon! Schande!")
    else:
      price = 1000
      balance = udb.get(str(ctx.author.id))
      if balance == None:
        await ctx.send("Bitte eröffne zuerst ein Konto mit `.signup`!")
      else:
        if balance < price:
          await ctx.send("Dein Kontostand kann diesen Betrag nicht decken.")
        else:
          newBalance = balance - price
          memberID = str(ctx.author.id)
          udb.set(memberID, newBalance)
          await member.add_roles(roleItem4, reason=None, atomic=True)
          await ctx.send("Du hast `Gottheit` für `1000 EHRE` gekauft! GÖTTLICHE EHRE!")
  else:
    await ctx.send("Sorry, aber dieses Item gibt es nicht.")


@bot.command(description="Wirf eine Münze", help="Wirf eine Münze")
async def coinflip(ctx, side: str, amount: int):
  balance = udb.get(str(ctx.author.id))
  flips = fdb.get(str(ctx.author.id))
  now = datetime.now()
  datenow = now.strftime("%d-%m-%Y")

  if flips == False:
    fdb.set(str(ctx.author.id), [0, datenow])

  if flips[0] >= 5 and flips[1] == datenow:
    await ctx.send("Du hast dein tägliches Flip-Limit erreicht!")
  else:
    if flips[1] != datenow:
      fdb.set(str(ctx.author.id), [0,datenow])

    if balance == None:
      await ctx.send("Bitte eröffne zuerst ein Konto mit `.signup`!")
    else:
      if balance < amount:
        await ctx.send("Dein Kontostand kann diesen Betrag nicht decken.")
      elif side != "heads" and side != "tails":
        await ctx.send("`{0}` ist keine gültige Seite. Probiere `heads` oder `tails`.".format(side))
      else:
        newFlips = []
        newFlips.append(fdb.get(str(ctx.author.id))[0] + 1)
        newFlips.append(datenow)
        fdb.set(str(ctx.author.id), newFlips)
        randSide = randint(1,2)
        sidePercentage = randint(1,50)
        if sidePercentage == 1:
          randSide = "side"
        elif randSide == 1:
          randSide = "heads"
        elif randSide == 2:
          randSide = "tails"
        if side == randSide:
          await ctx.send("Du hast `{0}` geworfen! Du gewinnst `{1} EHRE`!".format(randSide, amount))
          udb.set(str(ctx.author.id),balance+amount)
        else:
          await ctx.send("Du hast `{0}` geworfen! Du verlierst `{1} EHRE`!".format(randSide, amount))
          udb.set(str(ctx.author.id), balance-amount)


@bot.command(description="Limits zurücksetzen", help="Limits zurücksetzen (kann nur der Bot Besitzer)")
async def reset(ctx, type: str):
  if str(ctx.author.id) in botOwner:
    receiverID = str(ctx.message.mentions[0].id)
    now = datetime.now()
    datenow = now.strftime("%d-%m-%Y")

    if type == "claim":
      cdb.set(str(receiverID), "none")
      await ctx.send("`{0}` limit wurde für {1} zurückgesetzt.".format(type, ctx.message.mentions[0]))
    elif type == "coinflip":
      fdb.set(str(receiverID), [0,datenow])
      await ctx.send("`{0}` limit wurde für {1} zurückgesetzt.".format(type, ctx.message.mentions[0]))
    else:
      await ctx.send("`{0}` existiert nicht.".format(type))
  else:
    await ctx.send("Du must der Bot Besitzer sein um diese Aktion ausführen zu können.")
        
bot.run(DISCORD_TOKEN)