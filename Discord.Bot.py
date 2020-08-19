"""
Hey, this is my simple Discord Bot I created for my Server.

It's not coded in the best way, but it seems to work fine. I use the discord.py API to allow me to access my Discord Bot
via Python.
"""

from discord.ext import commands
import discord
from json import dump
from emoji import emojize

# Here I set up the bot and create a bunch of constants that need tidying up in the future. It works for the moment,
# But it's very messy and I hate it as of now.
# TODO Get rid of all these constants via alternate coding methods
client = commands.Bot(command_prefix='.')
MEMBERS_FILENAME = "users.json"
TOKEN_FILENAME = "token.txt"
OWNER_ID = 104265011714592768  # ID for my Discord, zak#6030

# I decided to go for a dictionary for each role and their respective emoji to go with the role. At the moment this is
# hard-coded as a constant, but in the future I plan on changing this. I might, for example, store this data in a JSON
# file, which can be edited and saved manually via discord commands.
ROLE_YEARS_AND_EMOJIS = {"Fresher": u"\U0001F4D8", "Second Year": u"\U0001F4D5", "Placement": u"\U0001F4BC",
                         "Final Year": u"\U0001F4D7", "Postgraduate": u"\U0001F4D9"}

ROLE_COURSES_AND_EMOJIS = {"Business Information Technology": u"\U0001F535", "Computing": u"\U0001F7E2",
                           "Data Science & Analytics": u"\U0001F7E4",
                           "Information Technology Management": u"\U0001F7E0", "Computer Networks": u"\U0001F534",
                           "Cyber Security Management": u"\U0001F7E3", "Forensic Computing & Security": u"\U0001F7E6",
                           "Software Engineering": u"\U0001F7E8"}


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

    channel = client.get_channel(740607231787008102)  # TODO Change these IDs so they are not hardcoded

    # Here I store a msg as a variable and add specific reactions to both messages. Makes it easier for users to add
    # their own reaction.
    msg = await channel.fetch_message(740607492257742888)
    for emoji in ROLE_YEARS_AND_EMOJIS.values():
        await msg.add_reaction(emoji)

    msg = await channel.fetch_message(740607524419665960)
    for emoji in ROLE_COURSES_AND_EMOJIS.values():
        await msg.add_reaction(emoji)


@client.event
async def on_guild_join(guild):
    """This is an unfinished side thing. Need to get around to finishing this.
    At the moment, all it does is, once the bot joins a discord server it will create a json file storing all user's
    info such as their name, id and rep. It also records the servers name, id and members.

    To finish, I want to add reaction-role stuff here. Such as the message ID and what reactions give what roles.
    This way it can change variably rather than being hard-coded."""

    data = {"server_name": guild.name,
            "server_id": guild.id,
            "roles_max": 0,
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

    if message_id == 740607492257742888:
        for role, emoji in ROLE_YEARS_AND_EMOJIS.items():
            if payload.emoji.name == emoji:
                role_to_give = discord.utils.get(guild.roles, name=role)

    elif message_id == 740607524419665960:
        for role, emoji in ROLE_COURSES_AND_EMOJIS.items():
            if payload.emoji.name == emoji:
                role_to_give = discord.utils.get(guild.roles, name=role)

    if role_to_give:
        member = discord.utils.find(lambda m: m.id == payload.user_id, guild.members)
        if member:
            await member.add_roles(role_to_give)


@client.event
async def on_member_update(before, after):
    """Function is run when a member is updated, e.g a new role is given.
    This is quite complicated, and can definitely be improved, but for now it works (lol). It took me longer than it
    should have to figure how to do this.

    Basically it only allows users to have one role out of a set list of roles x2. e.g The user can have the roles
    First Year and Computing together. But NOT First Year and Second Year roles together."""

    new_role = list(set(after.roles) - set(before.roles))  # Gives us the difference between the before and after roles
    year_count = 0
    course_count = 0

    if len(new_role) == 0:
        return

    for role in after.roles:
        if role.name in ROLE_YEARS_AND_EMOJIS.keys():
            year_count += 1
        elif role.name in ROLE_COURSES_AND_EMOJIS.keys():
            course_count += 1

    if year_count > 1:
        for role in after.roles:
            if role.name in ROLE_YEARS_AND_EMOJIS.keys() and role.name != new_role[0].name:
                await after.remove_roles(role)
    elif course_count > 1:
        for role in after.roles:
            if role.name in ROLE_COURSES_AND_EMOJIS.keys() and role.name != new_role[0].name:
                await after.remove_roles(role)


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
        `.add_reaction_role {message ID} {role name} {emoji name}`
        For example:
        `.add_reaction_role [656201333698854932] [YouTuber] [red_square]`""")


# TODO Finish this command. Need to add a check for the emoji_name parameter using
# https://pypi.org/project/emoji/
@client.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def add_reaction_roles(ctx, msg_id=None, role_name=None, emoji_name=None):
    if not msg_id or not role_name or not emoji_name:
        await ctx.channel.send("Error, please provide 3 arguments. See help via add_reaction_role_help")
        return

    for role in ctx.guild.roles:
        if role.name == role_name:
            await ctx.channel.send("Error, could not find the Role! Make sure spelling and capitalisation are "
                                   "correct!")
            return

    await ctx.channel.send("{} {} {}".format(msg_id, role_name, emoji_name))  # This is a temporary return...

if __name__ == "__main__":
    client.run(read_token())


# making a change i cannot see