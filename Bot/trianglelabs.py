# python3 "[PATH TO bot.py]" "[TOKEN]" "[ACTIVITY TYPE]" "[BOT STATUS]" "[BOT PERSONALITY]" "[DATABASE LOC]" "[OPT STREAM LINK]"
import langdetect, langcodes, translators, os, json

with open("config.json") as config_raw:
    config_tokens = json.load(config_raw)
    config_raw.close()

langdetect.DetectorFactory.seed = 0
import threading, random, asyncio
import re, json, time
import os, hashlib, requests
from urllib.parse import urlparse
import requests_async as arequests
from discord.ext import commands
import sys, subprocess, openai, discord, os

a, b = [sys.argv, {}]
b["token"], b["activity"], b["status"], b["personality"], b["DATABASE"], b[
    "stream_link"] = [
        a[1], a[2], a[3], a[4], a[5], None if len(a) < 7 else a[7]
    ]
config = b
del b, a
config["__num"] = None if len(sys.argv) < 6 else sys.argv[6]
import threading
import nest_asyncio


langdetect.DetectorFactory.seed = 0
import threading, random, asyncio
import re, json, time
import os, hashlib, requests
from urllib.parse import urlparse
import requests_async as arequests
from discord.ext import commands
import sys, subprocess, openai, discord, os

a, b = [sys.argv, {}]
b["token"], b["activity"], b["status"], b["personality"], b["DATABASE"], b[
    "stream_link"] = [
        a[1], a[2], a[3], a[4], a[5], None if len(a) < 7 else a[7]
    ]
config = b
del b, a
config["__num"] = None if len(sys.argv) < 6 else sys.argv[6]
import threading
import nest_asyncio


class Limits:
    limit = 33

    def is_limited(message):
        user_dir = config["DATABASE"] + "/user_info/limits/" + str(
            message.author.id)
        if not os.path.exists(user_dir):
            with open(user_dir, "w") as file:
                file.write("1")
                file.close()
            return False
        else:
            with open(user_dir, "r") as file:
                messages = float(file.read().replace("\n", ""))
                file.close()
            if messages >= Limits.limit:
                return True
            else:
                with open(user_dir, "w") as file:
                    file.write(str(messages + 1))
                    file.close()
                return False


version = "0.1.7"
nest_asyncio.apply()


class URL:

    async def get_file_name(url):
        a = urlparse(url)
        return os.path.basename(a.path)


class RunThread(threading.Thread):

    def __init__(self, coro):
        self.coro = coro
        self.result = None
        super().__init__()

    def run(self):
        self.result = asyncio.run(self.coro)


class Language:

    def translate(message):
        return translators.translate_text(message)


def run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        thread = RunThread(coro)
        thread.start()
        thread.join()
        return thread.result
    else:
        return asyncio.run(coro)


openai.api_key = config_tokens["openai_apikey"]


def find_in_file(file, text, message=None):
    if message != None:
        id = message
        if text == id:
            return True
        found = 0
        with open(file) as toread:
            if toread.read().find(str(text)) != -1: found = 1
            toread.close()
        if found: return True
        else: return False
    else:
        found = 0
        with open(file) as toread:
            if toread.read().find(str(text)) != -1: found = 1
            toread.close()
        if found: return True
        else: return False


class vars:
    # Store the `Popen` Objects from the `subprocess` module so they can be terminated
    clients = {}


async def Launch_Client(id,
                        token,
                        activity,
                        status,
                        personality,
                        stream_link=None):
    if stream_link != None:
        vars.clients[str(id)] = subprocess.Popen([
            "python3", "bot.py", token, activity, status, personality,
            stream_link
        ])
    else:
        vars.clients[str(id)] = subprocess.Popen(
            ["python3", "bot.py", token, activity, status, personality])


async def End_Client(id):
    vars.clients[str(id)].kill()


class Discord:

    def is_safe_message(input: str):
        try:
            r = openai.Moderation.create(
                input=input
            )
            r = (r["results"]["categories"]) if "results" in r else (
                r["response"]["categories"])
            r = True if r["sexual"] == True else (
                True if r["hate"] == True else
                (True if r["sexual/minors"] == True else False))
        except Exception as Error:
            print(Error)
            return False  # Return false if API Not working so bots can still respond to messages
        return r

    users_devs = ["746446670228619414", "294961139693912065"]

    def is_command(message):
        valid_commands = [
            "help", "ping", "wack", "sync", "eval", "exec", "activate", "regen", "deactivate"
        ]
        text = message.content
        if text[:len("<@" + str(vars.Client.user.id) +
                     ">")] == "<@" + str(vars.Client.user.id) + ">":
            stripped = text[len("<@" + str(vars.Client.user.id) + ">"):]
            touched_letter = 0
            end_text = ""
            for i in [char for char in stripped]:
                if i != " " or touched_letter == 1:
                    end_text = end_text + i
                else:
                    touched_letter = 1
            command = ""
            if " " in end_text:
                command = end_text.split(" ")[0].lower()
            else:
                command = end_text.lower()
            if command in valid_commands:
                return True
            else:
                return False
        else:
            return False

    async def parse_presence(Client, activitytype, status, stream_link=None):
        if activitytype == "listening":
            await Client.change_presence(activity=discord.Activity(
                type=discord.ActivityType.listening, name=status))
        elif activitytype == "watching":
            await Client.change_presence(activity=discord.Activity(
                type=discord.ActivityType.watching, name=status))
        elif activitytype == "playing":
            await Client.change_presence(activity=discord.Activity(
                type=discord.ActivityType.playing, name=status))
        elif activitytype == "streaming":
            await Client.change_presence(
                activity=discord.Activity(type=discord.ActivityType.streaming,
                                          name=status,
                                          url=stream_link))
        print("[Trianglelabs] > Bot Activity set to type %s with name %s" %
              (activitytype, status))

    def create_client(prefix=commands.when_mentioned_or(">>>>>")):
        mentions = discord.AllowedMentions.none
        Client = commands.AutoShardedBot(
            command_prefix=prefix,
            help_command=None,
            intents=discord.Intents.all(),
            AllowedMentions=mentions,
        )
        vars.Client = Client
        return Client

    def is_dm_channel(message):
        if message.channel.type is discord.ChannelType.private:
            return True
        else:
            return False

    def sent_by_bot(message):
        return message.author.bot

    def log_login(Client):
        print("[Trianglelabs] > Logged in as %s (%s)" %
              (Client.user.name, Client.user.ID))

    async def parse_message(message):
        # This Function Strips Discord Pings from messages
        # Prevents bot from mass pinging
        subs = {"You:": "", "Friend:": "", vars.Client.user.name + ":": ""}
        new_message = message
        for i in subs:
            new_message = new_message.replace(i, subs[i])
        banned_words = [
            "shit", "fuck", "nigger", "retard", "dumbass", "motherfucker",
            "brotherfucker", "arsehole", "asshole", "bastard", "bollocks",
            "spastic", "wanker", "nigga" # my bad if u had to read this ;-;
        ]
        for i in banned_words:
            compiled = re.compile(re.escape(i), re.IGNORECASE)
            new_message = compiled.sub("#" * len(i), new_message)
        if new_message.count("```") == 1:
            new_message = new_message.replace("```", "")
        return new_message

    async def reply(ctx, message, log=0, embed=None):
        msg = await Discord.parse_message(message)
        if Discord.is_dm_channel(ctx):
            try:
                sent = await ctx.send(msg, embed=embed)
            except:
                sent = await ctx.channel.send(msg, embed=embed)
        else:
            sent = await ctx.reply(msg.strip(),
                                   mention_author=False,
                                   embed=embed)
        if log:
            os.system(f"echo %s >> %s" % (
                sent.id,
                f"{config['DATABASE']}/clients/{vars.Client.user.id}/users/{ctx.author.id}"
            ))


class AI:
    Chat_Endings = {"okay": "👍", "ok": "👍"}

    class Response:

        async def wrap_content(message, ctx, user_activity="", mode=0):
            __ashfadsf = os.path.exists(
                f"{config['DATABASE']}/clients/{vars.Client.user.id}/message_context/{ctx.channel.id}"
            )
            bot_nickname = vars.Client.user.name
            user_nickname = message.author.display_name
            roleplay_store = config["DATABASE"] + "/user_info/roleplay/" + str(
                ctx.author.id)
            story_mode_enabled = os.path.exists(
                f"rm {config['DATABASE']}/clients/{vars.Client.user.id}/story_mode/{ctx.channel.id}"
            )
            file = f"{config['DATABASE']}/clients/{vars.Client.user.id}/users/{message.author.id}"
            if not os.path.exists(file):
                os.system("touch %s" % file)
            bot_nickname = vars.Client.user.name
            user_nickname = message.author.display_name
            if not Discord.is_dm_channel(message):
                bot_nickname = message.guild.get_member(
                    vars.Client.user.id).display_name
            if os.path.exists(roleplay_store):
                bot_data = f"{user_activity}\nSystem: DO NOT USE MARKDOWN ON NORMAL MESSAGES. ONLY MARKDOWN IF YOU ARE GENERATING CODE. If you are asked to put a tilde in your message, ONLY PUT ONE AT THE END.\nYou are roleplaying with your friend, {message.author.name}{'' if user_nickname == message.author.name else (', but you call them ' + user_nickname)}. You are to put any actions inside italics. Your are roleplaying as {vars.Client.user.name}{('') if message.channel.type is discord.ChannelType.private else ((', but people call you %s' % bot_nickname) if bot_nickname != vars.Client.user.name else (''))}.\nYou are having the conversation over Discord.\nYou are to put any code inside codeblocks, but do not put your own text into codeblocks.\nYou are also to speak English, even if your friend starts speaking other languages. Your backstory: {config['personality']}.\n\n\nYour conversation so far:"
            else:
                bot_data = f"{user_activity}\nSystem: DO NOT USE MARKDOWN ON NORMAL MESSAGES. ONLY MARKDOWN IF YOU ARE GENERATING CODE. If you are asked to put a tilde in your message, ONLY PUT ONE AT THE END.\nYou are having a conversation with your friend, {message.author.name}{'' if user_nickname == message.author.name else (', but you call them ' + user_nickname)}. Your name is {vars.Client.user.name}{('') if message.channel.type is discord.ChannelType.private else ((', but people call you %s' % bot_nickname) if bot_nickname != vars.Client.user.name else (''))}.\nYou are having the conversation over Discord.\nYou are to put any code inside codeblocks, but do not put your own text into codeblocks.\nYou are also to speak English, even if your friend starts speaking other languages. Your backstory: {config['personality']}.\n\n\nYour conversation so far:"
            chatter = message.author.id
            print("PINS")
            pined = await ctx.channel.pins()
            messages = [msg async for msg in ctx.channel.history(limit=10)] + [msg for msg in pined]
            print(messages)
            prompt = ""
            for i in messages:
                if __ashfadsf or find_in_file(file, i.id, message.id) or i in pined:
                    if story_mode_enabled:
                        if i.author.id == vars.Client.user.id:
                            prompt = (f"\nYou ({message.created_at}): %s" %
                                      i.content.replace("\n", " ")) + prompt
                        elif i.author.id == chatter:
                            if i.attachments:
                                links = ""
                                for attatchment in i.attachments:
                                    __e = await AI.Image_Recognition.URL(
                                        attatchment.url)
                                    links = ", ".join(__e) + " " + links
                                __a = await URL.get_file_name(attatchment.url)
                                text = await AI.OCR.URL(attatchment.url)
                                prompt = (
                                    f"\n{ctx.author.name}: %s" %
                                    i.content.replace("\n", " ")
                                ) + "\nSystem: Your Friend Sends you a Image Containing: " + links + " named " + __a + " with " + text + prompt
                            else:
                                prompt = (
                                    f"\{ctx.author.name}: %s" %
                                    i.content.replace("\n", " ")) + prompt
                    else:
                        if i.author.id == vars.Client.user.id:
                            prompt = (f"\nYou: %s" %
                                      i.content.replace("\n", " ")) + prompt
                        elif i.author.id == chatter:
                            if i.attachments:
                                links = ""
                                for attatchment in i.attachments:
                                    __e = await AI.Image_Recognition.URL(
                                        attatchment.url)
                                    links = ", ".join(__e) + " " + links
                                __a = await URL.get_file_name(attatchment.url)
                                text = await AI.OCR.URL(attatchment.url)
                                prompt = (
                                    f"\n{ctx.author.name} ({message.created_at}): %s"
                                    % i.content.replace("\n", " ")
                                ) + "\nSystem: Your Friend Sends you a Image Containing: " + links + " named " + __a + " with " + text + prompt
                            else:
                                prompt = (
                                    f"\n{ctx.author.name}: %s" %
                                    i.content.replace("\n", " ")) + prompt
            prompt = bot_data + prompt
            return (prompt + "\nYou: ").replace("{user}",
                                                ctx.author.name).replace(
                                                    "```", "")

        async def wrap_content_gpt(message, ctx, mode=0, user_activity=""):
            bot_nickname = vars.Client.user.name
            user_nickname = message.author.display_name
            roleplay_store = config["DATABASE"] + "/user_info/roleplay/" + str(
                ctx.author.id)
            if os.path.exists(roleplay_store):
                bot_data = f"{user_activity}\nSystem: DO NOT USE MARKDOWN ON NORMAL MESSAGES. ONLY MARKDOWN IF YOU ARE GENERATING CODE. If you are asked to put a tilde in your message, ONLY PUT ONE AT THE END.\nYou are roleplaying with your friend, {message.author.name}{'' if user_nickname == message.author.name else (', but you call them ' + user_nickname)}. You are to put any actions inside italics. Your are roleplaying as {vars.Client.user.name}{('') if message.channel.type is discord.ChannelType.private else ((', but people call you %s' % bot_nickname) if bot_nickname != vars.Client.user.name else (''))}.\nYou are having the conversation over Discord.\nYou are to put any code inside codeblocks, but do not put your own text into codeblocks.\nYou are also to speak English, even if your friend starts speaking other languages. Your backstory: {config['personality']}.\n\n\nYour conversation so far:"
            else:
                bot_data = f"{user_activity}\nSystem: DO NOT USE MARKDOWN ON NORMAL MESSAGES. ONLY MARKDOWN IF YOU ARE GENERATING CODE. If you are asked to put a tilde in your message, ONLY PUT ONE AT THE END.\nYou are having a conversation with your friend, {message.author.name}{'' if user_nickname == message.author.name else (', but you call them ' + user_nickname)}. Your name is {vars.Client.user.name}{('') if message.channel.type is discord.ChannelType.private else ((', but people call you %s' % bot_nickname) if bot_nickname != vars.Client.user.name else (''))}.\nYou are having the conversation over Discord.\nYou are to put any code inside codeblocks, but do not put your own text into codeblocks.\nYou are also to speak English, even if your friend starts speaking other languages. Your backstory: {config['personality']}.\n\n\nYour conversation so far:"
            if mode == 0:
                story_mode_enabled = os.path.exists(
                    f"rm {config['DATABASE']}/clients/{vars.Client.user.id}/story_mode/{ctx.channel.id}"
                )
                file = f"{config['DATABASE']}/clients/{vars.Client.user.id}/users/{message.author.id}"
                if not os.path.exists(file):
                    os.system("touch %s" % file)
                bot_nickname = vars.Client.user.name
                user_nickname = message.author.display_name
                if not Discord.is_dm_channel(message):
                    bot_nickname = message.guild.get_member(
                        vars.Client.user.id).display_name
                chatter = message.author.id
                print("PINS")
                pined = await ctx.channel.pins()
                messages = [msg async for msg in ctx.channel.history(limit=10)] + [msg for msg in pined]
                print(messages)
                prompt = []
                for i in messages:
                    if find_in_file(file, i.id, message.id) or i in pined:
                        if i.author.id == vars.Client.user.id:
                            prompt.append({
                                "role": "assistant",
                                "content": i.content
                            })
                        elif i.author.id == chatter:
                            if i.attachments:
                                links = ""
                                for attatchment in i.attachments:
                                    __e = await AI.Image_Recognition.URL(
                                        attatchment.url)
                                    links = ", ".join(__e) + " " + links
                                __a = await URL.get_file_name(attatchment.url)
                                text = await AI.OCR.URL(attatchment.url)
                                prompt.append({
                                    "role":
                                    "system",
                                    "content":
                                    "Your Friend sends you a attachment containing: "
                                    + links + "named " + __a + " with" + text
                                })
                                prompt.append({
                                    "role":
                                    "user",
                                    "content":
                                    i.content.replace("\n", " ")
                                })
                            else:
                                prompt.append({
                                    "role":
                                    "user",
                                    "content":
                                    i.content.replace("\n", " ") + " "
                                })
                new = []
                for i in prompt:
                    new.append({
                        "role":
                        i["role"],
                        "content":
                        i["content"].replace("{user}",
                                             ctx.author.name).replace(
                                                 "```", "")
                    })
                new.append({"role": "system", "content": bot_data})
                new.reverse()
                return new
            elif mode == 1:
                story_mode_enabled = os.path.exists(
                    f"rm {config['DATABASE']}/clients/{vars.Client.user.id}/story_mode/{ctx.channel.id}"
                )
                file = f"{config['DATABASE']}/clients/{vars.Client.user.id}/users/{message.author.id}"
                os.system(f"echo {message.id} >> {file}")
                if Discord.is_dm_channel(message):
                    file = f"{config['DATABASE']}/clients/{vars.Client.user.id}/users/{message.author.id}"
                bot_nickname = vars.Client.user.name
                user_nickname = message.author.display_name
                if not Discord.is_dm_channel(message):
                    bot_nickname = message.guild.get_member(
                        vars.Client.user.id).display_name
                chatter = message.author.id
                print("PINS")
                pined = await ctx.channel.pins()
                messages = [msg async for msg in ctx.channel.history(limit=10)] + [msg for msg in pined]
                prompt = []
                for i in messages:
                    file = f"{config['DATABASE']}/clients/{vars.Client.user.id}/users/{message.author.id}"
                    if find_in_file(file, i.id, message.id) or i in pined:
                        if i.author.id == vars.Client.user.id:
                            prompt.append({
                                "role": "assistant",
                                "content": i.content
                            })
                        elif i.author.id == chatter:
                            if i.attachments:
                                links = ""
                                for attatchment in i.attachments:
                                    links += attatchment.url
                                prompt.append({
                                    "role":
                                    "system",
                                    "content":
                                    "Your Friend Sent you attachments: " +
                                    links
                                })
                                prompt.append({
                                    "role":
                                    "user",
                                    "content":
                                    i.content.replace("\n", " ")
                                })
                            else:
                                prompt.append({
                                    "role":
                                    "user",
                                    "content":
                                    i.content.replace("\n", " ") + " "
                                })
                new = []
                for i in prompt:
                    new.append({
                        "role":
                        i["role"],
                        "content":
                        i["content"].replace("{user}",
                                             ctx.author.name).replace(
                                                 "```", "")
                    })
                new.append({"role": "system", "content": bot_data})
                new.reverse()
                return new

        async def prompt(prompt, retry=1, ctx=None):
            try:
                try:
                    prompt = await asyncio.to_thread(
                        translators.translate_text, query_text=prompt)
                except:
                    ...
                engine = 1
                if ctx != None:
                    if os.path.exists(
                            f"{config['DATABASE']}/clients/{vars.Client.user.id}/engine/{ctx.channel.id}"
                    ):
                        with open(
                                f"{config['DATABASE']}/clients/{vars.Client.user.id}/engine/{ctx.channel.id}"
                        ) as conf:
                            engine = int(conf.read().replace("\n", ""))
                            conf.close()

                try:
                    if engine == 1:
                        response = await asyncio.wait_for(
                            openai.Completion.acreate(model="text-davinci-003",
                                                      prompt=prompt,
                                                      temperature=0.35,
                                                      max_tokens=100,
                                                      top_p=1.0,
                                                      frequency_penalty=0.5,
                                                      presence_penalty=0.0,
                                                      stop=None),
                            timeout=15)
                        if response.choices[0].text.strip(
                        )[:1] == '"' and response.choices[0].text.strip(
                        )[-1] == '"':
                            return response.choices[0].text.strip()[:-1][1:]
                        else:
                            return response.choices[0].text.strip()
                    elif engine == 2:
                        response = await asyncio.wait_for(
                            openai.Completion.acreate(model="text-davinci-002",
                                                      prompt=prompt,
                                                      temperature=0.35,
                                                      max_tokens=100,
                                                      top_p=1.0,
                                                      frequency_penalty=0.5,
                                                      presence_penalty=0.0,
                                                      stop=None),
                            timeout=15)
                        if response.choices[0].text.strip(
                        )[:1] == '"' and response.choices[0].text.strip(
                        )[-1] == '"':
                            return response.choices[0].text.strip()[:-1][1:]
                        else:
                            return response.choices[0].text.strip()
                    elif engine == 99999:
                        response = await asyncio.wait_for(
                            openai.Completion.acreate(model="text-curie-001",
                                                      prompt=prompt,
                                                      temperature=0.35,
                                                      max_tokens=100,
                                                      top_p=1.0,
                                                      frequency_penalty=0.5,
                                                      presence_penalty=0.0,
                                                      stop=None),
                            timeout=15)
                        if response.choices[0].text.strip(
                        )[:1] == '"' and response.choices[0].text.strip(
                        )[-1] == '"':
                            return response.choices[0].text.strip()[:-1][1:]
                        else:
                            return response.choices[0].text.strip()
                    elif engine in [3, 4]:
                        response = await asyncio.wait_for(
                            openai.ChatCompletion.acreate(
                                model="gpt-3.5-turbo",
                                messages=prompt,
                                temperature=0.35,
                                max_tokens=100,
                                top_p=1.0,
                                frequency_penalty=0.5,
                                presence_penalty=0.0,
                                stop=None),
                            timeout=15)
                        return response['choices'][0]['message']['content']
                    elif engine == 4:
                        response = await asyncio.wait_for(
                            openai.ChatCompletion.acreate(
                                model="gpt-4",
                                messages=prompt,
                                temperature=0.35,
                                max_tokens=100,
                                top_p=1.0,
                                frequency_penalty=0.5,
                                presence_penalty=0.0,
                                stop=None),
                            timeout=15)
                        return response['choices'][0]['message']['content']
                except openai.error.RateLimitError:
                    if len(vars.tokens) == 1:
                        return "Unfortunately, we are out of funding for the month :(\nPlease support us at https://www.patreon.com/trianglelabs :hearts:"
                    else:
                        vars.tokens.pop(0)
                        openai.api_key = vars.tokens[0]
                        return "Unfortunately, we are out of funding for the month :(\nPlease support us at https://www.patreon.com/trianglelabs :hearts:"
                except (openai.error.APIConnectionError, asyncio.TimeoutError):
                    try:
                        await response.aclose()
                    except:
                        ...
                    if retry:
                        res = await AI.Response.prompt(prompt, 0, ctx)
                        return res
                    else:
                        return "Unfortunately, we are out of funding for the month :(\nPlease support us at https://www.patreon.com/trianglelabs :hearts:"
            except:
                return "Unfortunately, we are out of funding for the month :(\nPlease support us at https://www.patreon.com/trianglelabs :hearts:"

    class Image_Recognition:
        # TODO
        async def URL(url):
            async with arequests.Session() as session:
                session.auth = config_tokens["imagga_auth"]
                r = await session.get(
                    f"http://api.imagga.com/v2/tags?image_url={url}")
                try:
                    results = json.loads(r.text)["result"]["tags"]
                    in_img = []
                    for i in results:
                        if i["confidence"] > 80:
                            in_img.append(i["tag"]["en"])
                        else:
                            break
                    return in_img
                except:
                    return ["a file"]

    class OCR:

        async def URL(url):
            image_database = config["DATABASE"] + "/images/"
            async with arequests.Session() as session:
                if ".png" in url or ".bmp" in url or ".jpg" in url or ".apng" in url or ".jpeg" in url or ".gif" in url or ".webp" in url:
                    response = requests.get(url)
                    if response.status_code == 200:
                        image_hash = hashlib.sha1(response.content).hexdigest()
                        if os.path.exists(image_database + image_hash):
                            with open(image_database + image_hash) as f:
                                data = f.read().split("\n")
                                f.close()
                            return " the text " + ' '.join(data)
                        loop = asyncio.get_event_loop()
                        data = loop.run_until_complete(
                            Image_Tools.compress(response.content))
                        r = requests.post(
                            'https://api.api-ninjas.com/v1/imagetotext',
                            files={'image': data},
                            headers={
                                'X-Api-Key':
                                config_tokens["api-ninjas_apikey"]
                            })
                        res = r.json()
                        text = []
                        for i in res:
                            text.append(i["text"])
                        text2 = ' '.join(text)
                        text_n = '\n'.join(text)
                        text = text2

                        with open(image_database + image_hash, "w") as f:
                            f.write(text_n)
                            f.close()
                        del response, data
                        return " the text " + text
                    else:
                        del response
                        return " no text."
                else:
                    return " no text."

    class Upscale:

        def url(url):
            r = requests.post(
                "https://api.deepai.org/api/torch-srgan",
                data={
                    'image': url,
                },
                headers={'api-key': config_tokens["deepai_apikey"]})
            return r.json()["output_url"]

    class Art:

        def prompt(prompt):
            data = json.dumps({
                "key": config_tokens["stablediffusion_apikey"],
                "prompt": prompt,
                "negative_prompt":
                "((out of frame)), ((extra fingers)), mutated hands, ((poorly drawn hands)), ((poorly drawn face)), (((mutation))), (((deformed))), (((tiling))), ((naked)), ((tile)), ((fleshpile)), ((ugly)), (((abstract))), blurry, ((bad anatomy)), ((bad proportions)), ((extra limbs)), cloned face, (((skinny))), glitchy, ((extra breasts)), ((double torso)), ((extra arms)), ((extra hands)), ((mangled fingers)), ((missing breasts)), (missing lips), ((ugly face)), ((fat)), ((extra legs))",
                "width": "512",
                "height": "512",
                "samples": "1",
                "num_inference_steps": "20",
                "guidance_scale": 7.5,
                "safety_checker": "yes",
            })
            r = requests.post("https://stablediffusionapi.com/api/v3/text2img",
                              data=data,
                              headers={"Content-Type": "application/json"})
            data = json.loads(r.text)
            print(data)
            if not "status" in data:
                raise "API Server Errors"
            if data["status"] == "processing":
                return [data["fetch_result"], data["eta"]]
            else:
                return data["output"][0]

        def resume_fetch(link):
            stop = 0
            tries = 0
            while not stop and not (tries == 10):
                data = json.dumps({
                    "key":
                    config_tokens["stablediffusion_apikey"],
                })
                r = requests.post(link,
                                  data=data,
                                  headers={"Content-Type": "application/json"})
                data = json.loads(r.text)
                print(data)
                if not data["status"] == "processing":
                    return data["output"][0]
                time.sleep(10)
                tries += 1


import os
import sys
from PIL import Image
from io import BytesIO


class Image_Tools:

    async def compress(raw_data):
        stream = BytesIO(raw_data)
        file = os.getcwd() + "/tmp.raw" + str(random.randint(0, 100000))
        picture = Image.open(stream)
        conv = picture.convert('RGB')
        conv.save(file, "JPEG", optimize=True, quality=10)
        picture.close()
        del conv
        with open(file, "rb") as image:
            raw_data = image.read()
            image.close()
        os.remove(file)
        return raw_data


class Moderation:

    def Not_Banned_User(id):
        if not os.path.exists(f"{config['DATABASE']}/user_info/bans/{id}"):
            return True
        else:
            return False


async def asyncify(func, *args):
    coro = asyncio.to_thread(func, *args)
    task = asyncio.create_task(coro)
    result = await task
    return result
