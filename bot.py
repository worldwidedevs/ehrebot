import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from random import randint
import json
from datetime import datetime

description = "Ein Bot der eine virtuelle Bank simuliert."
bot = commands.Bot(command_prefix='.', description=description)

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Database setup
class UserDB(object):
    def __init__(self , location):
        self.location = os.path.expanduser(location)
        self.load(self.location)

    def load(self , location):
       if os.path.exists(location):
           self._load()
       else:
            self.db = {}
       return True

    def _load(self):
        self.db = json.load(open(self.location , "r"))

    def dumpdb(self):
        try:
            json.dump(self.db , open(self.location, "w+"))
            return True
        except:
            return False

    def set(self , key , value):
        try:
            self.db[str(key)] = value
            self.dumpdb()
        except Exception as e:
            print("[X] Error Saving Values to Database : " + str(e))
            return False

    def get(self , key):
        try:
            return self.db[key]
        except KeyError:
            print("No Value Can Be Found for " + str(key))
            return False

    def delete(self , key):
        if not key in self.db:
            return False
        del self.db[key]
        self.dumpdb()
        return True
    
    def resetdb(self):
        self.db={}
        self.dumpdb()
        return True
	
udb = UserDB("user.db")

class ClaimDB(object):
    def __init__(self , location):
        self.location = os.path.expanduser(location)
        self.load(self.location)

    def load(self , location):
       if os.path.exists(location):
           self._load()
       else:
            self.db = {}
       return True

    def _load(self):
        self.db = json.load(open(self.location , "r"))

    def dumpdb(self):
        try:
            json.dump(self.db , open(self.location, "w+"))
            return True
        except:
            return False

    def set(self , key , value):
        try:
            self.db[str(key)] = value
            self.dumpdb()
        except Exception as e:
            print("[X] Error Saving Values to Database : " + str(e))
            return False

    def get(self , key):
        try:
            return self.db[key]
        except KeyError:
            print("No Value Can Be Found for " + str(key))
            return False

    def delete(self , key):
        if not key in self.db:
            return False
        del self.db[key]
        self.dumpdb()
        return True
    
    def resetdb(self):
        self.db={}
        self.dumpdb()
        return True
	
cdb = ClaimDB("claim.db")

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
  if userBalance == False:
    udb.set(str(ctx.author.id), 20)
    cdb.set(str(ctx.author.id), "none")
    await ctx.send("Dein Konto bei **ehrebank** wurde eröffnet. Als Willkommensgeschenk bekommst du `20 EHRE`!")
  else:
    await ctx.send("Du hast schon ein Konto eröffnet.")
    
@bot.command(description="Zeige deinen Kontostand an", help="Zeige deinen Kontostand an")
async def balance(ctx):
  try:
    mentionedID = str(ctx.message.mentions[0].id)
    mentionedBalance = udb.get(mentionedID)
  except:
    await ctx.send("Du musst einen Benutzer erwähnen.")
  if mentionedBalance == False:
    await ctx.send("Der Benutzer hat noch kein Konto und muss es erst mit `.signup` erstellen.")
  else:
    await ctx.send(f"Der Kontostand von {ctx.message.mentions[0]} bei der **ehrebank** ist: `{mentionedBalance} EHRE`")
    
@bot.command(description="Sende EHRE", help="Sende EHRE")
async def send(ctx, amount: int):
  senderBalance = udb.get(str(ctx.author.id))
  if senderBalance == False:
    await ctx.send("Bitte eröffne zuerst ein Konto mit `.signup`!")
  else:
    if senderBalance < amount:
      await ctx.send("Dein Kontostand kann diesen Betrag nicht decken. Wähle einen kleineren Betrag.")
    else:
      receiverID = str(ctx.message.mentions[0].id)
      receiverBalance = udb.get(receiverID)
      if receiverBalance == False:
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
  if str(ctx.author.id) == "215080717560971264":
    senderBalance = udb.get(str(ctx.author.id))
    if senderBalance == False:
      await ctx.send("Bitte eröffne zuerst ein Konto mit `>signup`!")
    else:
      receiverID = str(ctx.message.mentions[0].id)
      receiverBalance = udb.get(receiverID)
      if receiverBalance == False:
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
  if userBalance == False:
    await ctx.send("Bitte eröffne zuerst ein Konto mit `.signup`!")
  else:
    if lastClaim == False:
      cdb.set(str(ctx.author.id), "none")
      
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
      if balance == False:
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
      if balance == False:
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
      if balance == False:
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
      if balance == False:
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
        
bot.run(DISCORD_TOKEN)
