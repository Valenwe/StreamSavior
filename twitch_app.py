# ░▀█▀░█▄█░█▀█░█▀█░█▀▄░▀█▀░█▀▀
# ░░█░░█░█░█▀▀░█░█░█▀▄░░█░░▀▀█
# ░▀▀▀░▀░▀░▀░░░▀▀▀░▀░▀░░▀░░▀▀▀
# Text generated from https://textkool.com/en/ascii-art-generator?hl=default&vl=default&font=Pagga

import json
import datetime
import logging
import os
import threading
import argparse
import sys
import requests
from twitchio import Message, Channel
from twitchio.ext import commands, routines

# ░█▀▄░█▀█░█▀▀░▀█▀░█▀▀░█▀▀
# ░█▀▄░█▀█░▀▀█░░█░░█░░░▀▀█
# ░▀▀░░▀░▀░▀▀▀░▀▀▀░▀▀▀░▀▀▀

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", dest="port",help="defines the Flask server port", type=int)
parser.add_argument("-v", "--verbose", dest="verbose",help="adds verbosity", action="store_true")
parser.add_argument("-vv", "--mega-verbose", dest="vverbose", help="adds maximum verbosity", action="store_true")
args = parser.parse_args().__dict__

if args["verbose"]:
    logging.basicConfig(level=logging.INFO)
elif args["vverbose"]:
    logging.basicConfig(level=logging.DEBUG)

# Get JSON files
try:
    with open("config.json", "r") as file:
        config = json.loads(file.read())
    with open("creds.json", "r") as file:
        creds = json.loads(file.read())
except:
    logging.error("Could not read config / creds file")
    exit()

# First time launching the program
if len(creds["irc_token"]) == 0:
    r = requests.get("https://id.twitch.tv/oauth2/authorize",
                     params={"response_type": "code",
                             "client_id": creds["bot_client_id"],
                             "redirect_uri": "https://twitchapps.com/tmi/",
                             "scope": "chat:edit+chat:read",
                             })
    print(f"You must follow this url to get an IRC token: {r.url}")
    exit()

# ░█▀▄░█▀█░█░█░▀█▀░▀█▀░█▀█░█▀▀░█▀▀
# ░█▀▄░█░█░█░█░░█░░░█░░█░█░█▀▀░▀▀█
# ░▀░▀░▀▀▀░▀▀▀░░▀░░▀▀▀░▀░▀░▀▀▀░▀▀▀

@routines.routine(minutes=int(config["regular_message_frequency"]))
async def message(channel: Channel, str: str):
    try:
        # If the last messages are the same message we want to send
        for i in range(1, 4):
            if len(bot.messages) >= i and bot.messages[-i]["content"] == str:
                return

        await channel.send(str)
    except Exception as e:
        logging.debug(e)

@routines.routine(seconds=int(config["passive_earn_frequency"]))
async def passive_earn():
    try:
        users = set()
        for msg in bot.messages:
            if msg["author"] != None:
                users.add(msg["author"])

        user: TwitchViewer
        for user in users:
            viewerlist.get(user).add_money(config["passive_earn"])
    except Exception as e:
        logging.debug(e)

# Will store all routines
bot_routines = [message, passive_earn]

def launch_flask():
    """ launch Flask server with the same argv than the main python script
    """
    args = sys.argv
    del args[0]
    os.system(f"python web_app.py {' '.join(args)}")


# ░█▀▀░█░░░█▀█░█▀▀░█▀▀░█▀▀░█▀▀
# ░█░░░█░░░█▀█░▀▀█░▀▀█░█▀▀░▀▀█
# ░▀▀▀░▀▀▀░▀░▀░▀▀▀░▀▀▀░▀▀▀░▀▀▀

class TwitchViewer():
    date_format = "%d-%m-%Y %H:%M:%S"

    def __init__(self, name: str, displayname: str = None, money: str = "0", last_earn: str = None):
        self.name = name
        if displayname == None:
            self.displayname = name
        else:
            self.displayname = displayname
        self.money = int(money)
        self.last_earn = last_earn

    def add_money(self, amount: str) -> int | None:
        amount = int(amount)
        self.money += amount
        return amount

    def remove_money(self, amount: str) -> int | None:
        amount = int(amount)
        if amount >= self.money:
            return None

        self.money -= amount
        return amount

    def can_earn(self, duration: str, target_date=datetime.datetime.now()):
        """
        duration is the number of minutes to check
        """
        # First time
        if self.last_earn == None:
            return True

        duration = datetime.timedelta(minutes=int(duration))
        end_duration_date: datetime.datetime = (datetime.datetime.strptime(
            self.last_earn, TwitchViewer.date_format) + duration)
        return target_date.timestamp() >= end_duration_date.timestamp()

    def reset_last(self):
        self.last_earn = datetime.datetime.now().strftime(TwitchViewer.date_format)

    def set_displayname(self, displayname: str):
        self.displayname = displayname

    def __eq__(self, other):
        if type(self).__name__ != type(other).__name__:
            return False
        else:
            return self.name == other.name

    def __repr__(self) -> str:
        return f"\n{self.name} ==> Money: {self.money} - Last earn: {self.last_earn}"

    def to_json(self) -> dict:
        return {"name": self.name, "displayname": self.displayname, "money": self.money, "last_earn": self.last_earn}


class TwitchViewerList():
    def __init__(self):
        self.viewers = []

    def add(self, user, displayname: str = None):
        if isinstance(user, str):
            user = TwitchViewer(user)

        if displayname != None:
            user.set_displayname(displayname)

        if user not in self.viewers and isinstance(user, TwitchViewer):
            self.viewers.append(user)
            logging.info(f"Added new user {user.displayname}")

    def remove(self, user):
        if isinstance(user, str):
            user = TwitchViewer(user)

        if user in self.viewers and isinstance(user, TwitchViewer):
            self.viewers.remove(user)
            logging.info(f"Removed user {user.displayname}")

    def get(self, username: str) -> TwitchViewer | None:
        try:
            index = self.viewers.index(TwitchViewer(username))
            return self.viewers[index]
        except ValueError:
            return None

    def import_from_json(self, filename: str):
        if not os.path.isfile(filename):
            logging.error(f"Could not open file {filename}")
            return

        with open(filename, "r") as file:
            try:
                content = json.loads(file.read())
                for viewer in content:
                    self.add(TwitchViewer(
                        viewer["name"], viewer["displayname"], viewer["money"], viewer["last_earn"]))
            except:
                logging.exception(
                    f"Could not import content from file {filename}")

    def export_to_json(self, filename: str):
        with open(filename, "w") as file:
            file.write(json.dumps([elem.to_json() for elem in self.viewers]))
            print("Successfully saved the viewers")


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=creds["irc_token"],
            client_id=creds["bot_client_id"],
            client_secret=creds["bot_secret"],
            nick=config["bot_name"],
            prefix=config["prefix"],
            initial_channels=[config["channel"]]
        )
        self.messages = []

    async def check_price(self, ctx: commands.Context, price: str) -> bool:
        """ Check the price for a given command, apply the money, and send the request
        Args:
            ctx (Command context)
            price (str): the price

        Returns:
            Yes if we found and applied a command effect, false otherwise
        """
        user = viewerlist.get(ctx.message.author.name)
        if not user:
            return False

        if user.remove_money(price) == None:
            await ctx.send(f"{user.displayname}, you do not have enough 𒌐 !")
            return False

        command = ctx.message.content.split()[0][len(config["prefix"]):].lower()
        args: list[str] = ctx.message.content.split()
        del args[0]

        data = {"source": "tchat", "user": user.displayname}

        if command == "gif":
            data["data"] = args[0]
        elif command in config["audio_commands"].keys():
            elem = config["audio_commands"][command]
            data["data"] = elem["gif"]
            data["audio"] = elem["audio"]

        logging.debug(data)
        response = requests.post('http://localhost:5000/api', data=data)
        if response.text == "success":
            await ctx.send(f"{user.displayname}, your reaction has been sent for {price}𒌐 !")
            return True
        elif response.text == "error":
            # give back the money if wrong link
            user.add_money(price)
            await ctx.send("Invalid link!")
            return False

    async def event_ready(self):
        """ Notify us when everything is ready!
        """
        print(f'Bot logged in as {self.nick}')
        logging.info(f'Bot user id is {self.user_id}')

        # Start routines
        for routine in bot_routines:
            if routine == message:
                new_routine = routine.start(self.get_channel(config["channel"]), config["regular_message"])
            else:
                new_routine = passive_earn.start()

            bot_routines[bot_routines.index(routine)] = new_routine

    async def event_message(self, message: Message) -> None:
        """ Register any message, and handle commands if there is an author
        """
        try:
            author = message.author.name
        except:
            author = None

        self.messages.append({"author": author, "content": message.content})
        try:
            # try to add the user if possible
            viewerlist.add(author, message.author.display_name)
            return await super().event_message(message)
        except Exception as e:
            logging.debug(e)

    @commands.command(name='commands')
    async def command_list(self, ctx: commands.Context):
        """ Give the list of all possible commands
        """
        p = config["prefix"]
        text = f"List of commands: {p}bank / {p}earn / {p}gif <url>"
        for command in config["audio_commands"]:
            text += f" / {p}{command}"
        await ctx.send(text)

    @commands.command(name='earn')
    async def earn_command(self, ctx: commands.Context):
        """ Manual earn command to get money
        """
        user = viewerlist.get(ctx.message.author.name)
        if not user:
            return

        if user.can_earn(config["earn_frequency"]):
            amount = user.add_money(config["earn_amount"])
            if amount != None:
                await ctx.send(f"Yipii! You earned {amount}𒌐 !")
                user.reset_last()
        else:
            await ctx.send(f"You earned your money too recently... You have to wait at least {config['earn_frequency']} minute{'s' if int(config['earn_frequency']) > 1 else ''}.")

    @commands.command(name='bank', aliases=["money"])
    async def bank_command(self, ctx: commands.Context):
        """ Display the current user money amount
        """
        user = viewerlist.get(ctx.message.author.name)
        if not user:
            return
        await ctx.send(f"{user.displayname}, you currently own {user.money}𒌐.")

    @commands.command(name='gif')
    async def display_gif(self, ctx: commands.Context):
        """ Sends a gif to the stream
        """
        await self.check_price(ctx, config["gif_price"])

    @commands.command(name='audio_command', aliases=config["audio_commands"].keys())
    async def anya(self, ctx: commands.Context):
        """ Custom audio commands, displaying a gif & sound registered in the config file
        """
        command = ctx.message.content.split()[0][len(config["prefix"]):].lower()
        await self.check_price(ctx, config["audio_commands"][command]["price"])


# ░█▄█░█▀█░▀█▀░█▀█
# ░█░█░█▀█░░█░░█░█
# ░▀░▀░▀░▀░▀▀▀░▀░▀

if __name__ == '__main__':
    print("Process - began")
    flask_server = threading.Thread(target=launch_flask)
    flask_server.start()

    viewerlist = TwitchViewerList()
    viewerlist.import_from_json("viewers.json")
    bot = Bot()

    try:
        bot.run()
    except KeyboardInterrupt:
        pass

    # Save & stop all processes
    viewerlist.export_to_json("viewers.json")

    flask_server.join()

    for routine in bot_routines:
        routine.cancel()

    print("Process - ended")
