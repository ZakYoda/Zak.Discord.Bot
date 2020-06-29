from discord.ext import commands
import discord
from json import dump, load
import time


client = commands.Bot(command_prefix='.')
MEMBERS_FILENAME = "users.json"
TOKEN_FILENAME = "token.txt"
OWNER_ID = 104265011714592768  # ID for my Discord, zak#6030


def read_token():
    with open(TOKEN_FILENAME, "r") as f:
        token = f.read()

    return token


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_guild_join(guild):
    data = {"server_name": guild.name,
            "server_id": guild.id,
            "members": []}

    for guild_member in guild.members:
        data["members"].append({"name": str(guild_member),
                                "id": guild_member.id,
                                "rep": 0})

    with open("{}.json".format(guild.id), "w+", encoding="utf-8") as f:
        dump(data, f, ensure_ascii=False, indent=4)


@client.event
async def on_message(message):

    if message.author == client.user:  # Bot ignores its own messages
        return

    if 'open the pod bay doors' in message.content:
        msg = "I\'m sorry, {0.author.mention} I\'m afraid I can\'t do that.".format(message)
        await message.channel.send(msg)

    # Add this line so we can still process bot.command() stuff (otherwise it overwrites)
    await client.process_commands(message)


@client.command(name="rep")
@commands.cooldown(1, 60*60, commands.BucketType.user)
async def add_rep(ctx, user: discord.User):
    rep = 0

    if user.id == ctx.author.id:
        await ctx.send("You cannot give yourself rep!")
        await add_rep.reset_cooldown(ctx)
        return

    with open("{}.json".format(ctx.guild.id), encoding="utf-8") as f:
        data = load(f)

    for i in range(len(data["members"])):
        if user.id == data["members"][i]["id"]:  # User Match
            data["members"][i]["rep"] += 1  # Add the rep and store it
            rep = data["members"][i]["rep"]
            break  # Now we may break the loop for efficiency purposes

    # Now write our changes back to the file
    with open("{}.json".format(ctx.guild.id), "w", encoding="utf-8") as f:
        dump(data, f, ensure_ascii=False, indent=4)

    await ctx.send("Given rep to: {}! This user now has **{}** reputation.".format(user.mention, rep))


@add_rep.error
async def add_rep_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        retryTime = time.strftime(r"%H:%M:%S", time.gmtime(error.retry_after))
        msg = 'This command is only available once a day, please try again in **{}**'.format(retryTime)
        await ctx.send(msg)
    else:
        raise error


if __name__ == "__main__":
    client.run(read_token())
