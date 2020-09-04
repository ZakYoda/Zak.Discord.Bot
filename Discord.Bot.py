"""
Hey, this is my simple Discord Bot I created for my Server.

It's not coded in the best way, but it seems to work fine. I use the discord.py API to allow me to access my Discord Bot
via Python.
"""

from discord.ext import commands
import discord
from json import dump, load
import emojis


client = commands.Bot(command_prefix='.')
MEMBERS_FILENAME = "users.json"
TOKEN_FILENAME = "token.txt"
OWNER_ID = 104265011714592768  # ID for my Discord, zak#6030


def read_token():
    """Simple function to read the token for my Discord bot that I store in a txt file.
    This is done so when I upload my code to Github, users cannot view my token for my bot.
    """
    with open(TOKEN_FILENAME, "r") as f:
        token = f.read()

    return token


@client.event
async def on_ready():
    """This function is run when the bot is first run and logged in.
    At the moment it's coded quite badly, as I've hardcoded the channelIDs and messageIDs. For the moment, it's fine.
    But definitely needs changing.
    """
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_guild_join(guild):
    """This is an unfinished side thing. Need to get around to finishing this.
    At the moment, all it does is, once the bot joins a discord server it will create a json file storing all user's
    info such as their name, id and rep. It also records the servers name, id and members.

    To finish, I want to add reaction-role stuff here. Such as the message ID and what reactions give what roles.
    This way it can change variably rather than being hard-coded."""

    data = {"server_name": guild.name,
            "server_id": guild.id,
            "reaction_roles": []}

    with open("{}.json".format(guild.id), "w+", encoding="utf-8") as f:
        dump(data, f, ensure_ascii=False, indent=4)


@client.event
async def on_raw_reaction_add(payload):
    """This function is run when someone adds a reaction to a message.
    Here, I check if the reaction is to a certain message. If it is, I check what emoji it is. If it's the correct
    reaction, it will give them the respective role."""

    if payload.user_id == client.user.id:
        return

    message_id = payload.message_id
    role_to_give = None
    guild_id = payload.guild_id
    guild = discord.utils.find(lambda g: g.id == guild_id, client.guilds)

    json_data = get_json_data("{}.json".format(guild_id))

    for role_dict in json_data["reaction_roles"]:
        if role_dict["msgID"] == str(message_id) and role_dict["role_emoji"] == payload.emoji.name and \
                json_data["server_id"] == guild_id:
            role_to_give = discord.utils.get(guild.roles, name=role_dict["role_name"])

    if role_to_give:
        member = discord.utils.find(lambda m: m.id == payload.user_id, guild.members)
        if member:
            await member.add_roles(role_to_give)


@client.event
async def on_message(message):

    if message.author == client.user:  # bot ignores its own commands
        return

    # Add this line so we can still process bot.command() stuff (otherwise it overwrites)
    await client.process_commands(message)


@client.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def add_reaction_role_help(ctx):
    await ctx.channel.send("""To add reaction roles, the format is:
        `.add_reaction_role {message ID} {role name} {emoji}`
        For example:
        `.add_reaction_role 656201333698854932 "Old Man" :red_square:`
Note that this must be done in the same channel as the message. (commands may be deleted after)""")


@client.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def add_reaction_role(ctx, msg_id=None, role_name=None, emoji_name=None):
    if not msg_id or not role_name or not emoji_name:
        await ctx.channel.send("Error, please provide 3 arguments. See help via add_reaction_role_help")
        return

    try:
        _ = await ctx.channel.fetch_message(msg_id)
    except discord.NotFound:
        await ctx.channel.send("Error, please check the message ID and try again!")
    except Exception as e:
        await ctx.channel.send("Error, uh oh: {}".format(str(e)))
        return

    found_role = False
    for role in ctx.guild.roles:
        if role.name == role_name:
            found_role = True

    if not found_role:
        await ctx.channel.send("Error, could not find the Role! Make sure spelling and capitalisation are "
                               "correct!")
        return

    if emojis.count(emoji_name) < 1:
        await ctx.channel.send("Error, please enter an emoji! e.g :red_square:")
        return
    elif emojis.count(emoji_name) > 1:
        await ctx.channel.send("Error, please enter **one** emoji!")
        return

    json_data = get_json_data("{}.json".format(ctx.guild.id))

    exists = False

    for i in range(len(json_data["reaction_roles"])):
        try:
            _ = json_data["reaction_roles"][i][role_name]
        except KeyError:
            continue
        exists = True

    if exists:
        await ctx.channel.send("Error, role already exists with reaction! Please remove it first.")
        return

    json_data["reaction_roles"].append({"msgID": msg_id, "role_name": role_name, "role_emoji": emoji_name})
    with open("{}.json".format(ctx.guild.id), "w", encoding="utf-8") as f:
        dump(json_data, f, ensure_ascii=False, indent=4)

    await ctx.channel.send("Done!")


@client.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def remove_reaction_role_help(ctx):
    await ctx.channel.send("""To remove all reaction-roles from a message, the format is:
        `.remove_reactions {message ID}`
        For example:
        `.remove_reactions 751177943174217738`""")


# TODO Create remove_reaction_role() function/command.
@client.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def remove_reactions(ctx, msg_id=None):
    pass

# TODO Bug Testing / Debugging necessary.


def get_json_data(json_path):
    """Simple function to return our data in a json form"""
    with open(json_path, encoding="utf-8") as json_string:
        return load(json_string)


if __name__ == "__main__":
    client.run(read_token())
