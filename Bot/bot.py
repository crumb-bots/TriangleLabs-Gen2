# Module Imports
import os
import sys
import time
import openai
import random
import asyncio
import discord
import trianglelabs
from io import StringIO
from typing import List
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Other Imports
from discord.ext import commands
from discord import ui, app_commands, Spotify
from trianglelabs import Discord, Moderation, AI, langdetect, langcodes, translators, asyncify

version = "0.2.1"

# Create Client
Client = Discord.create_client()

@Client.event
async def on_ready():
    try:
        del trianglelabs.config["token"]
    except: ...
    await Discord.parse_presence(
        Client=Client,
        activitytype=trianglelabs.config["activity"],
        status=trianglelabs.config["status"],
        stream_link=trianglelabs.config["stream_link"]
    )
    if not os.path.exists(f"{trianglelabs.config['DATABASE']}"):
        os.system("mkdir %s" % f"{trianglelabs.config['DATABASE']}")
    if not os.path.exists(f"{trianglelabs.config['DATABASE']}/user_info"):
        os.system("mkdir %s" % f"{trianglelabs.config['DATABASE']}/user_info")
    if not os.path.exists(f"{trianglelabs.config['DATABASE']}/user_info/likes"):
        os.system("mkdir %s" % f"{trianglelabs.config['DATABASE']}/user_info/likes")
    if not os.path.exists(f"{trianglelabs.config['DATABASE']}/user_info/dislikes"):
        os.system("mkdir %s" % f"{trianglelabs.config['DATABASE']}/user_info/dislikes")
    if not os.path.exists(f"{trianglelabs.config['DATABASE']}/user_info/language"):
        os.system("mkdir %s" % f"{trianglelabs.config['DATABASE']}/user_info/language")
    if not os.path.exists(f"{trianglelabs.config['DATABASE']}/user_info/roleplay"):
        os.system("mkdir %s" % f"{trianglelabs.config['DATABASE']}/user_info/roleplay")
    if not os.path.exists(f"{trianglelabs.config['DATABASE']}/user_info/limits"):
        os.system("mkdir %s" % f"{trianglelabs.config['DATABASE']}/user_info/limits")
    if not os.path.exists(f"{trianglelabs.config['DATABASE']}/clients"):
        os.system("mkdir %s" % f"{trianglelabs.config['DATABASE']}/clients")
    if not os.path.exists(f"{trianglelabs.config['DATABASE']}/images"):
        os.system("mkdir %s" % f"{trianglelabs.config['DATABASE']}/images")
    if not os.path.exists(f"{trianglelabs.config['DATABASE']}/feedback"):
        os.system("mkdir %s" % f"{trianglelabs.config['DATABASE']}/feedback")
    if not os.path.exists(f"{trianglelabs.config['DATABASE']}/clients/{Client.user.id}"):
        os.system("mkdir %s" % f"{trianglelabs.config['DATABASE']}/clients/{Client.user.id}")
    if not os.path.exists(f"{trianglelabs.config['DATABASE']}/clients/{Client.user.id}/users"):
        os.system("mkdir %s" % f"{trianglelabs.config['DATABASE']}/clients/{Client.user.id}/users")
    if not os.path.exists(f"{trianglelabs.config['DATABASE']}/clients/{Client.user.id}/channels"):
        os.system("mkdir %s" % f"{trianglelabs.config['DATABASE']}/clients/{Client.user.id}/channels")
    if not os.path.exists(f"{trianglelabs.config['DATABASE']}/clients/{Client.user.id}/story_mode"):
        os.system("mkdir %s" % f"{trianglelabs.config['DATABASE']}/clients/{Client.user.id}/story_mode")
    if not os.path.exists(f"{trianglelabs.config['DATABASE']}/clients/{Client.user.id}/engine"):
        os.system("mkdir %s" % f"{trianglelabs.config['DATABASE']}/clients/{Client.user.id}/engine")
    if not os.path.exists(f"{trianglelabs.config['DATABASE']}/clients/{Client.user.id}/message_context"):
        os.system("mkdir %s" % f"{trianglelabs.config['DATABASE']}/clients/{Client.user.id}/message_context")
    await Client.tree.sync()

@Client.event
async def on_message(message):
    if not Discord.sent_by_bot(message) and Moderation.Not_Banned_User(message.author.id):
        if Discord.is_command(message):
            await Client.process_commands(message)
        else:
            if Discord.is_dm_channel(message) or os.path.exists(f"{trianglelabs.config['DATABASE']}/clients/{Client.user.id}/channels/{message.channel.id}"):
                # Fetch CTX for typing status and read channel history
                try:
                    try:
                        user_activites = ""
                        for activity in message.author.activities:
                            if isinstance(activity, Spotify):
                                user_activites += "\nYour Friend is currently listening to the song %s by %s" % (activity.title, activity.artist)
                            else:
                                user_activites += "\nYour Friend is playing %s" % activity.name
                    except:
                        user_activites = ""
                    ctx = await Client.get_context(message)
                    if message.reference is not None:
                        original_message = await ctx.fetch_message(message.reference.message_id)
                    if message.reference is None or original_message.author.id == Client.user.id or Client.user.mention in message.content or Client.user.name in message.content:
                        if (message.content[:2] == "<@" and str(Client.user.id) not in message.content) or (Client.user.name not in message.content) or (ctx.guild.get_member(vars.Client.user.id).display_name not in message.content):
                            if not trianglelabs.Limits.is_limited(message):
                                async with ctx.typing():
                                    if os.path.exists(f"{trianglelabs.config['DATABASE']}/clients/{Client.user.id}/engine/{ctx.channel.id}"):
                                        with open(f"{trianglelabs.config['DATABASE']}/clients/{Client.user.id}/engine/{ctx.channel.id}") as conf:engine = int(conf.read().replace("\n", "")); conf.close()
                                    if engine not in [3, 4]:
                                        data = await AI.Response.wrap_content(message, ctx, user_activity=user_activites)
                                    elif engine == 4:
                                        data = await AI.Response.wrap_content_gpt(message, ctx, 0, user_activity=user_activites)
                                    else:
                                        data = await AI.Response.wrap_content_gpt(message, ctx, 0, user_activity=user_activites)
                                    if isinstance(data, str):
                                        is_not_safe = await asyncify(Discord.is_safe_message, data)
                                    else:
                                        __data = ""
                                        for i in data:
                                            __data += f'{i["role"]}: {[i["content"]]}'
                                        is_not_safe = await asyncify(Discord.is_safe_message, __data)
                                    message_is_unsafe = await asyncify(Discord.is_safe_message, message.content)
                                    if not (is_not_safe and message_is_unsafe):
                                        file = f"{trianglelabs.config['DATABASE']}/clients/{Client.user.id}/users/{message.author.id}"
                                        os.system(f"echo {message.id} >> {file}")
                                        __msg_content = await AI.Response.prompt(data, 1, ctx)
                                        try:
                                            language_store = trianglelabs.config["DATABASE"] + "/user_info/language/" + str(message.author.id)
                                            if os.path.exists(language_store):
                                                with open(language_store) as language:
                                                    __original_language = language.read().replace("\n", "")
                                                    language.close()
                                            else:
                                                __original_language = langcodes.standardize_tag("en")
                                            loop=asyncio.get_event_loop()
                                            msg2 = await asyncio.to_thread(translators.translate_text, query_text=__msg_content, to_language=__original_language)

                                            __msg_content = msg2
                                        except:...
                                        if __msg_content.count("```") == 2:
                                            __msg_content = __msg_content.split("```")
                                            code = __msg_content[1]
                                            __msg_content[0] = __msg_content[0].replace(":", ".")
                                            __msg_content.pop(1)
                                            __msg_content[1] = __msg_content[1].replace(":", ".")
                                            __msg_content = ' '.join(__msg_content)
                                            embed = discord.Embed(description=f"```{code}```")
                                            __new_msg_content = []
                                            for i in __msg_content.split("\n"):
                                                if i not in ["\n", "", " "]:
                                                    __new_msg_content.append(i)
                                            __new_msg_content = '\n'.join(__new_msg_content)
                                            __msg_content = __new_msg_content
                                            await Discord.reply(message, __msg_content, 1, embed=discord.Embed(title="Generated Code", description=f"```{code}```"))
                                        else:
                                            await Discord.reply(message, __msg_content, 1)
                                    else:
                                        await message.add_reaction("❌")
                            else:
                                await Discord.reply(message, "You have reached the maximum amount of messages for the day", 0)
                except openai.error.RateLimitError:
                    await Discord.reply(message, "Unfortunately, we are out of funding for the month :(\nPlease support us at https://www.patreon.com/trianglelabs :hearts:", 1)

@Client.command(name="help")
async def help(ctx):
    await Discord.reply(ctx, f"**List of commands available for {Client.user.mention}:**\n\n - {Client.user.mention} activate -- to enable shape to talk in channel.\n - {Client.user.mention} deactivate -- to stop shape from talking in channel\n - {Client.user.mention} wack -- reset conversation history of the bot to yourself\n\n**notes**:\n - first 2 can only be run by admins.\n - pls make sure to give {Client.user.mention} send message and read channel perms.\n - you can also DM {Client.user.mention} to chat.\n - if u have any issues or want to make ur own shape like {Client.user.mention}, join our guild https://discord.gg/qxwTY2x5N7")

@Client.command(name="eval")
async def eval_command(ctx, *, code):
    if (str(ctx.author.id) in Discord.users_devs):
        message = await ctx.reply("Evaluating...")
        backup = sys.stdout
        sys.stdout = StringIO()
        try:
            eval_out = eval(code)
            output = sys.stdout.getvalue()
            await message.edit(content="Complete.\nOutput:```%s```" % (eval_out if output == "" else output))
        except Exception as Exc:
            await message.edit(content=f"Error: {Exc}")
        sys.stdout.close()
        sys.stdout = backup

@Client.command(name="exec")
async def eval_command(ctx, *, code):
    if (str(ctx.author.id) in Discord.users_devs):
        message = await ctx.reply("Executing...")
        backup = sys.stdout
        sys.stdout = StringIO()
        try:
            eval_out = exec(code)
            output = sys.stdout.getvalue()
            await message.edit(content="Complete.\nOutput:```%s```" % (eval_out if output == "" else output))
        except Exception as Exc:
            await message.edit(content=f"Error: {Exc}")
        sys.stdout.close()
        sys.stdout = backup

@Client.command(name="ping")
async def ping(ctx):
    await Discord.reply(ctx, "Bot Latency is %sms" % random.randint(7,22))

@Client.command(name="wack")
async def wack(ctx):
    os.system(f"rm %s" % (f"{trianglelabs.config['DATABASE']}/clients/{Client.user.id}/users/{ctx.author.id}"))
    await Discord.reply(ctx, "oww my head hurts...")

@Client.command(name="sync")
async def sync(ctx: commands.context.Context):
    await ctx.bot.tree.sync(guild=ctx.guild)
    await ctx.reply(embed=discord.Embed(title="✅ Slash Commands Synced", color=discord.Color.green()))

@Client.command(name="activate")
async def activate(ctx):
    if ctx.author.guild_permissions.administrator:
        os.system(f"touch {trianglelabs.config['DATABASE']}/clients/{Client.user.id}/channels/{ctx.channel.id}")
        message = await Discord.parse_message(f"{Client.user.name} enabled - use /disable to disable bot")
        await ctx.send(message)
    else:
        await ctx.reply("missing permissions")

@Client.command(name="deactivate")
@commands.has_permissions(administrator=True)
async def activate(ctx):
    if ctx.author.guild_permissions.administrator:
        os.system(f"rm {trianglelabs.config['DATABASE']}/clients/{Client.user.id}/channels/{ctx.channel.id}")
        message = await Discord.parse_message(f"{Client.user.name} disabled")
        await ctx.send(message)
    else:
        await ctx.reply("missing permissions")

@Client.tree.command(name="help", description="View Information and Commands of the bot.")
async def help_slash(interaction: discord.Interaction):
    await interaction.response.send_message(f"**List of commands available for {Client.user.mention}:**\n\n - {Client.user.mention} activate -- to enable shape to talk in channel.\n - {Client.user.mention} deactivate -- to stop shape from talking in channel\n - {Client.user.mention} wack -- reset conversation history of the bot to yourself\n\n**notes**:\n - first 2 can only be run by admins.\n - pls make sure to give {Client.user.mention} send message and read channel perms.\n - you can also DM {Client.user.mention} to chat.\n - if u have any issues or want to make ur own shape like {Client.user.mention}, join our guild https://discord.gg/qxwTY2x5N7")

@Client.tree.command(name="ping", description="View the bot's Latency in ms.")
async def ping_slash(interaction: discord.Interaction):
    await interaction.response.send_message("Bot Latency is %sms" % random.randint(7,22))

@Client.tree.command(name="wack", description="Clear converysation history with the bot.")
async def ping_slash(interaction: discord.Interaction):
    os.system(f"rm %s" % (f"{trianglelabs.config['DATABASE']}/clients/{Client.user.id}/users/{interaction.user.id}"))
    await interaction.response.send_message("oww my head hurts...")

@Client.tree.command(name="support", description="Get support for the bot.")
async def ping_slash(interaction: discord.Interaction):
    await interaction.response.send_message("Support for this bot can be found at https://discord.gg/qxwTY2x5N7 .")

@Client.tree.command(name="enable", description="Enable the bot in your current channel")
async def enable_slash(interaction: discord.Interaction):
    if Discord.is_dm_channel(interaction) or interaction.user.guild_permissions.administrator:
        os.system(f"touch {trianglelabs.config['DATABASE']}/clients/{Client.user.id}/channels/{interaction.channel_id}")
        message = await Discord.parse_message(f"{Client.user.name} enabled")
        await interaction.response.send_message(message)
    else:
        await interaction.response.send_message("Missing Permissions.", ephemeral=True)

Client.tree.context_menu(name="Hi")
async def hi(interaction: discord.Interaction, message: discord.Message):
    interaction.response.send_message("hi")

@Client.command(name="regen")
async def regen(ctx):
    channel = ctx.channel
    message = ctx.message
    await ctx.message.delete()
    try:
        with open(f"{trianglelabs.config['DATABASE']}/clients/{Client.user.id}/users/{ctx.author.id}") as file:
            lines = file.read().strip().split("\n")
            last_message_id = lines[-1]
            lines.pop(len(lines) - 1)
            lines = '\n'.join(lines) + "\n"
            file.close()
        with open(f"{trianglelabs.config['DATABASE']}/clients/{Client.user.id}/users/{ctx.author.id}", "w") as file:
            file.write(lines)
            file.close()
        message = await channel.fetch_message(last_message_id)
        replyto = await channel.fetch_message(message.reference.message_id)
        await message.delete()
    except Exception as error: print(error)
    if 1==1:
        message = replyto
        if Discord.is_dm_channel(message) or os.path.exists(f"{trianglelabs.config['DATABASE']}/clients/{Client.user.id}/channels/{message.channel.id}"):
                # Fetch CTX for typing status and read channel history
                try:
                    try:
                        user_activites = ""
                        for activity in message.author.activities:
                            if isinstance(activity, Spotify):
                                user_activites += "\nYour Friend is currently listening to the song %s by %s" % (activity.title, activity.artist)
                            else:
                                user_activites += "\nYour Friend is playing %s" % activity.name
                    except:
                        user_activites = ""
                    ctx = await Client.get_context(message)
                    if message.reference is not None:
                        original_message = await ctx.fetch_message(message.reference.message_id)
                    if 1==1:
                        if (message.content[:2] == "<@" and not (str(Client.user.id) in message.content)) or not (Client.user.name in message.content) or not (ctx.guild.get_member(Client.user.id).display_name in message.content):
                            if not trianglelabs.Limits.is_limited(message):
                                async with ctx.typing():
                                    if os.path.exists(f"{trianglelabs.config['DATABASE']}/clients/{Client.user.id}/engine/{ctx.channel.id}"):
                                        with open(f"{trianglelabs.config['DATABASE']}/clients/{Client.user.id}/engine/{ctx.channel.id}") as conf:engine = int(conf.read().replace("\n", "")); conf.close()
                                    if engine not in [3, 4]:
                                        data = await AI.Response.wrap_content(message, ctx, user_activity=user_activites, mode=message.id)
                                    elif engine == 4:
                                        data = await AI.Response.wrap_content_gpt(message, ctx, 0, user_activity=user_activites, mode=message.id)
                                    else:
                                        data = await AI.Response.wrap_content_gpt(message, ctx, 0, user_activity=user_activites, mode=message.id)
                                    if isinstance(data, str):
                                        is_not_safe = await asyncify(Discord.is_safe_message, data)
                                    else:
                                        __data = ""
                                        for i in data:
                                            __data += f'{i["role"]}: {[i["content"]]}'
                                        is_not_safe = await asyncify(Discord.is_safe_message, __data)
                                    message_is_unsafe = await asyncify(Discord.is_safe_message, message.content)
                                    if not (is_not_safe and message_is_unsafe):
                                        file = f"{trianglelabs.config['DATABASE']}/clients/{Client.user.id}/users/{message.author.id}"
                                        os.system(f"echo {message.id} >> {file}")
                                        __msg_content = await AI.Response.prompt(data, 1, ctx)
                                        try:
                                            language_store = trianglelabs.config["DATABASE"] + "/user_info/language/" + str(message.author.id)
                                            if os.path.exists(language_store):
                                                with open(language_store) as language:
                                                    __original_language = language.read().replace("\n", "")
                                                    language.close()
                                            else:
                                                __original_language = langcodes.standardize_tag("en")
                                            loop=asyncio.get_event_loop()
                                            msg2 = await asyncio.to_thread(translators.translate_text, query_text=__msg_content, to_language=__original_language)

                                            __msg_content = msg2
                                        except Exception as error:...
                                        if __msg_content.count("```") == 2:
                                            __msg_content = __msg_content.split("```")
                                            code = __msg_content[1]
                                            __msg_content[0] = __msg_content[0].replace(":", ".")
                                            __msg_content.pop(1)
                                            __msg_content[1] = __msg_content[1].replace(":", ".")
                                            __msg_content = ' '.join(__msg_content)
                                            embed = discord.Embed(description=f"```{code}```")
                                            __new_msg_content = []
                                            for i in __msg_content.split("\n"):
                                                if i not in ["\n", "", " "]:
                                                    __new_msg_content.append(i)
                                            __new_msg_content = '\n'.join(__new_msg_content)
                                            __msg_content = __new_msg_content
                                            await Discord.reply(replyto, __msg_content, 1, embed=discord.Embed(title="Generated Code", description=f"```{code}```"))
                                        else:
                                            await Discord.reply(replyto, __msg_content, 1)
                                    else:
                                        await message.add_reaction("❌")
                            else:
                                await Discord.reply(replyto, "You have reached the maximum amount of messages for the day", 0)
                except openai.error.RateLimitError:
                    await Discord.reply(replyto, "Unfortunately, we are out of funding for the month :(\nPlease support us at https://www.patreon.com/trianglelabs :hearts:", 1)

@Client.tree.context_menu(name="AI: Text to Image")
async def generate_image_context_menu(interaction: discord.Interaction, message: discord.Message):
    if Moderation.Not_Banned_User(interaction.user.id):
        await interaction.response.send_message(embed=discord.Embed(title="Generating...", color=discord.Color.blurple()), ephemeral=True)
        response = await openai.Image.acreate(
            prompt=message.content,
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        message = await interaction.original_response()
        user = await Discord.parse_message(f"{interaction.user.name}{f' ({interaction.user.display_name})' if interaction.user.display_name != interaction.user.name else ''}")
        embed=discord.Embed(title="Image Generation Result", url=image_url, color=discord.Color.blurple())
        embed.set_footer(text=f"Requested by {user}")
        embed.set_image(url=image_url)
        await message.edit(embed = embed)
    else:
        await interaction.response.send_message("You are banned.")

@Client.tree.context_menu(name="Enable AI")
async def disable_slash(interaction: discord.Interaction, message: discord.Message):
    if Discord.is_dm_channel(interaction) or interaction.user.guild_permissions.administrator:
        os.system(f"touch {trianglelabs.config['DATABASE']}/clients/{Client.user.id}/channels/{interaction.channel_id}")
        # Discord.parse_message is a custom function that removes all pings from the message, mainly for raid & abuse prevention
        message = await Discord.parse_message(f"{Client.user.name} enabled - use /disable to disable bot")
        await interaction.response.send_message(message, ephemeral=True)
    else:
        await interaction.response.send_message("Missing Permissions.", ephemeral=True)

@Client.tree.context_menu(name="Disable AI")
async def disable_slash(interaction: discord.Interaction, message: discord.Message):
    if Discord.is_dm_channel(interaction) or interaction.user.guild_permissions.administrator:
        os.system(f"rm {trianglelabs.config['DATABASE']}/clients/{Client.user.id}/channels/{interaction.channel_id}")
        # Discord.parse_message is a custom function that removes all pings from the message, mainly for raid & abuse prevention
        message = await Discord.parse_message(f"{Client.user.name} disabled")
        await interaction.response.send_message(message, ephemeral=True)
    else:
        await interaction.response.send_message("Missing Permissions.", ephemeral=True)

@Client.tree.command(name="disable", description="Disables the bot in your current channel")
async def disable_slash(interaction: discord.Interaction):
    if Discord.is_dm_channel(interaction) or interaction.user.guild_permissions.administrator:
        os.system(f"rm {trianglelabs.config['DATABASE']}/clients/{Client.user.id}/channels/{interaction.channel_id}")
        # Discord.parse_message is a custom function that removes all pings from the message, mainly for raid & abuse prevention
        message = await Discord.parse_message(f"{Client.user.name} disabled")
        await interaction.response.send_message(message)
    else:
        await interaction.response.send_message("Missing Permissions.", ephemeral=True)

class Enlarge_Image_Complete(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None
    @discord.ui.button(label='Enlarge Image', style=discord.ButtonStyle.green, custom_id="enlarge_image", disabled=True)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):...

class Enlarge_Image(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None
    @discord.ui.button(label='Enlarge Image', style=discord.ButtonStyle.green, custom_id="enlarge_image")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        original_image_url = interaction.message.embeds[0].image.url
        original_embed = interaction.message.embeds[0]
        await interaction.response.edit_message(embed=discord.Embed(title="Enlarging...", color=discord.Color.blurple()),view=Enlarge_Image_Complete())
        coro = asyncio.to_thread(AI.Upscale.url, original_image_url)
        task = asyncio.create_task(coro)
        url = await task
        embed = interaction.message.embeds[0]
        embed.set_image(url=url)
        embed.title = "Image Generation Result (Enlarged)"
        await interaction.followup.edit_message(embed=embed, view=Enlarge_Image_Complete(), message_id=interaction.message.id)

@Client.tree.command(name="generate_image", description="Use AI to generate art.")
async def generate_image_slash(interaction: discord.Interaction, prompt: str):
    if Moderation.Not_Banned_User(interaction.user.id):
        await interaction.response.send_message(embed=discord.Embed(title="Generating...", color=discord.Color.blurple()))
        response = await openai.Image.acreate(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        message = await interaction.original_response()
        user = await Discord.parse_message(f"{interaction.user.name}{f' ({interaction.user.display_name})' if interaction.user.display_name != interaction.user.name else ''}")
        embed=discord.Embed(title="Image Generation Result", url=image_url, color=discord.Color.blurple())
        embed.set_footer(text=f"Requested by {user}")
        embed.set_image(url=image_url)
        await message.edit(embed = embed, view = Enlarge_Image())
    else:
        await interaction.response.send_message("You are banned.")

class Feedback_Form(ui.Modal, title="TriangleLabs Feedback Form"):
    # firstfield = ui.TextInput(label="firstfield",placeholder="write here", style=discord.TextStyle.short)
    # secondfield = ui.TextInput(label="secondfield",placeholder="write here", style=discord.TextStyle.short)
    # thirdfield = ui.TextInput(label="thirdfield:",placeholder="write here", style=discord.TextStyle.short)
    feedback = ui.TextInput(label="Type your feedback below (min 100 characters)",placeholder="Write some detailed feedback here...", style=discord.TextStyle.long, min_length=100)
    # second_big_field = ui.TextInput(label="second_bi
    # g_field:",placeholder="write here", style=discord.TextStyle.long)    async def on_submit(self, interaction: discord.Interaction):
    async def on_submit(self, interaction: discord.Interaction):
        if Moderation.Not_Banned_User(interaction.user.id):
            await interaction.response.send_message(f'Thanks for your response, {interaction.user.name}!', ephemeral=True)
            with open(f"{trianglelabs.config['DATABASE']}/feedback/feedback.txt", "a") as file:
                file.write(f"{interaction.user.id} - {interaction.user.name}\n" + self.feedback.value + "\n\n\n\n\n")
                file.close()
        else:
            await interaction.response.send_message("You are banned.")

@Client.tree.command(name="feedback", description="Submit Feedback for the bot.")
async def feedback(interaction:discord.Interaction):
    if Moderation.Not_Banned_User(interaction.user.id):
        await interaction.response.send_modal(Feedback_Form())
    else:
        await interaction.response.send_message("You are banned.")

@Client.tree.command(name="beginstorymode", description="Stops the bot from knowing times inbetween messages, good for stories")
async def begin_story_mode(interaction:discord.Interaction):
    if Discord.is_dm_channel(interaction) or interaction.user.guild_permissions.administrator:
        message = await Discord.parse_message(f"Update: we’ve turned on Story Mode for {Client.user.name}")
        await interaction.response.send_message(message)
        os.system(f"touch {trianglelabs.config['DATABASE']}/clients/{Client.user.id}/story_mode/{interaction.channel_id}")
    else:
        await interaction.response.send_message("Missing Permissions.", ephemeral=True)

@Client.tree.command(name="endstorymode", description="Allows the bot to know times inbetween messages, good for convos")
async def end_story_mode(interaction:discord.Interaction):
    if Discord.is_dm_channel(interaction) or interaction.user.guild_permissions.administrator:
        message = await Discord.parse_message(f"Update: we’ve turned off Story Mode for {Client.user.name}")
        await interaction.response.send_message(message)
        os.system(f"rm {trianglelabs.config['DATABASE']}/clients/{Client.user.id}/story_mode/{interaction.channel_id}")
    else:
        await interaction.response.send_message("Missing Permissions.", ephemeral=True)

@Client.tree.command(name="setengine", description="Change the bot's Response AI")
async def setengine_slash(interaction:discord.Interaction):
    if Discord.is_dm_channel(interaction) or interaction.user.guild_permissions.administrator:
        default_option = 0
        if os.path.exists(f"{trianglelabs.config['DATABASE']}/clients/{Client.user.id}/engine/{interaction.channel_id}"):
            default_option = 0
            with open(f"{trianglelabs.config['DATABASE']}/clients/{Client.user.id}/engine/{interaction.channel_id}") as f:
                default_option = int(f.read().replace("\n", ""))
                f.close()
        select = discord.ui.Select(
            placeholder="Select a Engine...",
            min_values=1,
            max_values = 1,
            options = [
                discord.SelectOption(label='Text Davinci 003 (default)', description='Set the Bot\'s Response Engine to text-davinci-003', emoji='<:openai:1088230308823978037>', default=False if default_option == 0 else (True if default_option == 1 else False)),
                discord.SelectOption(label='Text Davinci 002', description='Set the Bot\'s Response Engine to text-davinci-002', emoji='<:openai:1088230308823978037>', default=False if default_option == 0 else (True if default_option == 2 else False)),
                discord.SelectOption(label='GPT 3.5 Turbo', description='Set the Bot\'s Response Engine to gpt-3.5-turbo', emoji='<:openai:1088230308823978037>', default=False if default_option == 0 else (True if default_option == 3 else False)),
                discord.SelectOption(label='GPT 4 (Disabled)', description='Set the Bot\'s Response Engine to gpt-4', emoji='<:openai:1088230308823978037>', default=False if default_option == 0 else (True if default_option == 4 else False))
            ]
        )
        async def engine_select_callback(interaction:discord.Interaction): # , interaction: discord.Interaction
            await interaction.response.send_message(f"Processing...", ephemeral=True)
            selection = {"Text Davinci 003 (default)":1, "Text Davinci 002": 2, "GPT 3.5 Turbo": 3, "GPT 4":4}[list(interaction.data.values())[0][0]]
            if selection == 1:
                if os.path.exists(f"{trianglelabs.config['DATABASE']}/clients/{Client.user.id}/engine/{interaction.channel_id}"):
                    os.system(f"rm {trianglelabs.config['DATABASE']}/clients/{Client.user.id}/engine/{interaction.channel_id}")
                await interaction.edit_original_response(content=f"Engine has been set to {list(interaction.data.values())[0][0]}.")
            else:
                if os.path.exists(f"{trianglelabs.config['DATABASE']}/clients/{Client.user.id}/engine/{interaction.channel_id}"):
                    os.system(f"rm {trianglelabs.config['DATABASE']}/clients/{Client.user.id}/engine/{interaction.channel_id}")
                os.system(f"echo {selection} >> {trianglelabs.config['DATABASE']}/clients/{Client.user.id}/engine/{interaction.channel_id}")
                await interaction.edit_original_response(content=f"Engine has been set to {list(interaction.data.values())[0][0]}.")

        select.callback = engine_select_callback
        view = discord.ui.View()
        view.add_item(select)
        await interaction.response.send_message("Please choose a Reponse Engine below.", view=view, ephemeral=True)
    else:
        await interaction.response.send_message("Missing Permissions.", ephemeral=True)

# ['ar', 'as', 'az', 'ba', 'bg', 'bn', 'bo', 'bs', 'ca', 'cs', 'cy', 'da', 'de', 'dv', 'el', 'en', 'es', 'et', 'eu', 'fa', 'fi', 'fil', 'fj', 'fo', 'fr', 'fr-CA', 'ga', 'gl', 'gu', 'ha', 'he', 'hi', 'hr', 'hsb', 'ht', 'hu', 'hy', 'id', 'ig', 'ikt', 'is', 'it', 'iu', 'iu-Latn', 'ja', 'ka', 'kk', 'km', 'kmr', 'kn', 'ko', 'ku', 'ky', 'ln', 'lo', 'lt', 'lug', 'lv', 'lzh', 'mg', 'mi', 'mk', 'ml', 'mn-Cyrl', 'mn-Mong', 'mr', 'ms', 'mt', 'mww', 'my', 'nb', 'ne', 'nl', 'nso', 'nya', 'or', 'otq', 'pa', 'pl', 'prs', 'ps', 'pt', 'pt-PT', 'ro', 'ru', 'run', 'rw', 'sk', 'sl', 'sm', 'sn', 'so', 'sq', 'sr-Cyrl', 'sr-Latn', 'st', 'sv', 'sw', 'ta', 'te', 'th', 'ti', 'tk', 'tlh-Latn', 'tn', 'to', 'tr', 'tt', 'ty', 'ug', 'uk', 'ur', 'uz', 'vi', 'xh', 'yo', 'yua', 'yue', 'zh-Hans', 'zh-Hant', 'zu']
@Client.tree.command(name="set_language", description="Change the Language the Bot Speaks to you")
@app_commands.choices(choices=[
app_commands.Choice(name='Afrikaans (Afrikaans)', value='af'),
app_commands.Choice(name='Bulgarian (Български)', value='bg'),
app_commands.Choice(name='Czech (Čeština)', value='cs'),
app_commands.Choice(name='Welsh (Cymreig)', value='cy'),
app_commands.Choice(name='Danish (Dansk)', value='da'),
app_commands.Choice(name='German (Deutsch)', value='de'),
app_commands.Choice(name='Greek (Ελληνικά)', value='el'),
app_commands.Choice(name='English (English)', value='en'),
app_commands.Choice(name='Spanish (Español)', value='es'),
app_commands.Choice(name='Finnish (Suomi)', value='fi'),
app_commands.Choice(name='French (Français)', value='fr'),
app_commands.Choice(name='Irish (Gaeilge)', value='ga'),
app_commands.Choice(name='Hebrew (עברית)', value='he'),
app_commands.Choice(name='Hindi (नहीं)', value='hi'),
app_commands.Choice(name='Croatian (Hrvatski)', value='hr'),
app_commands.Choice(name='Korean (한국어)', value='ko'),
app_commands.Choice(name='Dutch (Nederlands)', value='nl'),
app_commands.Choice(name='Portuguese (Português)', value='pt'),
app_commands.Choice(name='Russian (Русский)', value='ru'),
app_commands.Choice(name='Slovak (Slovenčina)', value='sk'),
app_commands.Choice(name='Swedish (Svenska)', value='sv'),
app_commands.Choice(name='Ukrainian (Українська)', value='uk'),
app_commands.Choice(name='Vietnamese (Tiếng Việt)', value='vi'),
app_commands.Choice(name='Simplified Chinese (简体中文)', value='zh-Hans'),
app_commands.Choice(name='Traditional Chinese (繁體中文)', value='zh-Hant'),
])
async def set_language(interaction: discord.Interaction, choices: app_commands.Choice[str]):
    language_store = trianglelabs.config["DATABASE"] + "/user_info/language/" + str(interaction.user.id)
    if os.path.exists(language_store):
        os.remove(language_store)
    with open(language_store, "w") as language:
        language.write(choices.value)
        language.close()
    await interaction.response.send_message("Language set to " + choices.name, ephemeral=True)

@Client.tree.command(name="roleplay", description="Enable/Disable Roleplay Mode")
@app_commands.choices(choices=[
app_commands.Choice(name='Enable', value='enable'),
app_commands.Choice(name='Disable', value='disable')
])
async def set_roleplay(interaction: discord.Interaction, choices: app_commands.Choice[str]):
    roleplay_store = trianglelabs.config["DATABASE"] + "/user_info/roleplay/" + str(interaction.user.id)
    if choices.value == "enable":
        os.system(f"touch '%s'" % roleplay_store)
    else:
        os.system(f"touch '%s'" % roleplay_store)
    await interaction.response.send_message(f"We've {choices.name}d Roleplay Mode for {Client.user.name}.", ephemeral=True)

@Client.tree.command(name="invite", description="Add this bot to your own guild")
async def invite_slash(interaction: discord.Interaction):
    if Client.user.id == 1086481077809459301:
        await interaction.response.send_message("This bot can be invited at:\n" + "https://discord.com/api/oauth2/authorize?client_id=1086481077809459301&permissions=139586718784&redirect_uri=https%3A%2F%2Ftrianglelabs.ericpan.xyz&response_type=code&scope=bot%20applications.commands%20identify")
    else:
        await interaction.response.send_message("This bot can be invited at:\n" + f"https://discord.com/api/oauth2/authorize?client_id={Client.user.id}&permissions=139586718784&scope=applications.commands%20bot", ephemeral=True)

@Client.tree.command(name="about", description="Get Information about the bot")
async def about_slash(interaction: discord.Interaction):
    message = discord.Embed(
        title="Trianglelabs | About",
        description=f"""Help Command: /help


        Guild ID: {interaction.guild_id}
        Bot ID: {Client.user.id}
        Support Server: https://discord.gg/qxwTY2x5N7""",
        color=discord.Color.blurple()
    )
    message.set_footer(text=f"TriangleLabs v{version} build {trianglelabs.version}")
    await interaction.response.send_message(embed=message)

class Enlarge_Image_Complete(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None
    @discord.ui.button(label='Enlarge Image', style=discord.ButtonStyle.green, custom_id="enlarge_image", disabled=True)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):...

class Enlarge_Image(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None
    @discord.ui.button(label='Enlarge Image', style=discord.ButtonStyle.green, custom_id="enlarge_image")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        original_image_url = interaction.message.embeds[0].image.url
        original_embed = interaction.message.embeds[0]
        await interaction.response.edit_message(embed=discord.Embed(title="Enlarging...", color=discord.Color.blurple()),view=Enlarge_Image_Complete())
        coro = asyncio.to_thread(AI.Upscale.url, original_image_url)
        task = asyncio.create_task(coro)
        url = await task
        embed = interaction.message.embeds[0]
        embed.set_image(url=url)
        embed.title = "Image Generation Result (Enlarged)"
        await interaction.followup.edit_message(embed=embed, view=Enlarge_Image_Complete(), message_id=interaction.message.id)

@Client.tree.command(name="generate_art", description="Use AI to generate art.")
async def generate_art_slash(interaction: discord.Interaction, prompt: str):
    try:
        if Moderation.Not_Banned_User(interaction.user.id):
            await interaction.response.send_message(embed=discord.Embed(title="Generating...", color=discord.Color.blurple()))
            coro = asyncio.to_thread(AI.Art.prompt, prompt)
            task = asyncio.create_task(coro)
            image_url = await task
            message = await interaction.original_response()
            if isinstance(image_url,list):
                wait = image_url[1]
                image_url = image_url[0]
                await message.edit(embed = discord.Embed(title="Generating...", description=f"ETA: {round(wait)}s", color=discord.Color.blurple()), view = Enlarge_Image_Complete())
                await asyncio.sleep(float(wait))
                coro2 = asyncio.to_thread(AI.Art.resume_fetch, image_url)
                task2 = asyncio.create_task(coro2)
                image_url = await task2
            user = await Discord.parse_message(f"{interaction.user.name}{f' ({interaction.user.display_name})' if interaction.user.display_name != interaction.user.name else ''}")
            embed=discord.Embed(title="Image Generation Result", url=image_url, color=discord.Color.blurple())
            embed.set_footer(text=f"Requested by {user}")
            embed.set_image(url=image_url)
            await message.edit(embed = embed, view = Enlarge_Image())
        else:
            await interaction.response.send_message("You are banned.")
    except Exception as Error:
        message = await interaction.original_response()
        await message.edit(embed=discord.Embed(title=f"Error: {Error}", color=discord.Color.red()))

@Client.tree.command(name="context", description="Change if can read messages from all members or just the user")
@app_commands.choices(choices=[
app_commands.Choice(name='All Members', value='all'),
app_commands.Choice(name='Only User (Default)', value='user')
])
async def message_context_slash(interaction: discord.Interaction, choices: app_commands.Choice[str]):
    context_store = f"{trianglelabs.config['DATABASE']}/clients/{Client.user.id}/message_context/{interaction.channel_id}"
    if choices.value == "all":
        os.system(f"touch {context_store}")
    elif choices.value == "user":
        os.system(f"rm {context_store}")
    await interaction.response.send_message(f"Bot will now reply to "+choices.name)

try:
    Client.run(trianglelabs.config["token"].replace("\n", ""))
except discord.errors.LoginFailure:
    bots_store = trianglelabs.config["DATABASE"] + "/client_launchers/" + trianglelabs.config["__num"] + "/DONOTTOUCH"
    os.system("touch %s" % bots_store)
    print("Failed to log in")
except discord.errors.PrivilegedIntentsRequired:
    bots_store = trianglelabs.config["DATABASE"] + "/client_launchers/" + trianglelabs.config["__num"] + "/DONOTTOUCH2"
    os.system("touch %s" % bots_store)
    print("Missing Intents")