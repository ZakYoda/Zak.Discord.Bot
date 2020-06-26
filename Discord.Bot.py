from discord.ext import commands


client = commands.Bot(command_prefix='.')
MEMBERS_FILENAME = "members.json"
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
async def on_message(message):

    if message.author == client.user: # Bot ignores its own messages
        return

    if 'open the pod bay doors' in message.content:
        msg = "I\'m sorry, {0.author.mention} I\'m afraid I can\'t do that.".format(message)
        await message.channel.send(msg)

    # Add this line so we can still process bot.command() stuff (otherwise it overwrites)
    await client.process_commands(message)


@client.command(name="daily")
# @commands.cooldown(1, 60*60*24, commands.BucketType.user)
async def on_daily_reward(ctx):
    # TODO
    pass


if __name__ == "__main__":
    client.run(read_token())
