import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
from keep_alive import keep_alive
import asyncio
import json
import random
import time
from datetime import datetime, timedelta

load_dotenv('.env')

client = commands.Bot(command_prefix='+', case_insensitive=True)
client.remove_command('help')
AFK = {}

RANDOM_STUFF = [
    "death is inevitable",
    "Sometimes I think of what exists outside of my "
    "little bubble. This existence of compliance and "
    "order is excruciatingly painful.",
    'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
    'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
    'yo wireless gas?? wireless gas doe? wireless gas?!?!?!?!',
    'MONKEY MODE OOO A AA OOO OA AAA AOO OA OOO AA OO OA AAA',
    "Can I go back to the ages when I didn't have to think?",
    ":fire::b::ok_hand:"
    "<:laughcry:820391753156263938>:ok_hand::b::fire:",
    "you are like a cactus with no needles. i know where you sleep.",
    "betrayals happen when people sleep",
    "the balloon can fly. but the time "
    "the balloon flies does not matter",
    "you cannot sleep in a world without pillows",
    "Die hamster sien dalk net deur die lens van sy eie oë.",
    "I never leave the bed when the sun is looking into my soul"
]

HAPPY = ['happy', 'celebrate', 'congrats', 'congratulations', 'nice']

POG = [
    '<:spedpog:816749395264405568>', '<:npog:816749361614159914>',
    '<:quagpog:819646454649323591>', '<:pog:819262750802575371>',
    '<:ppog:819262750751457341>', '<:pogu:819262751020023828>',
    '<:fishpog:819262750952783912>', '<a:pog:818437856779436102>',
    '<:cpog:819988583393001533>', '<a:kannapog:825964713585147904>']

EMOTES = {
    'wob': '<a:wob:818437838588608573>',
    'conga': '<a:conga:818437963616092183>' * 5,
    'blobnuts': '<a:blobNUTS:800173958082592809>',
    'pcwob': '<a:ablobwobwork:800508733591388230>',
    'blobroll': '<a:ablobwobroll:800508734014881812>',
    'thisisfine': '<a:thisisfine:799085979553890334>',
    'wobble': '<a:wobble:819661113515180102>',
    'catdance': '<a:catdance:821203420064382986>',
    'thonk': '<:thonk:822681360215965746>',
    'sadge': '<:sadge:810649990808469514>',
    'pensivecheese': '<:pensivecheese:823324747516608522>',
    'menacing': '<a:menacing:823417218431844372>' * 5,
    'kirbo': '<a:kirbo:832056783065186315>', 'kirb': '<:kirb:833042433385168947>',
    'death': '<:death:833042433809580062>', 'kirbgun': '<:kirbgun:833043498537320508>'
}


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    reminder.start()
    await client.change_presence(activity=discord.Game(' reality surf '
                                                       '| +help'))


@tasks.loop(seconds=1)
async def reminder():
    try:
        f = open('remindme.json')
        reminder_dict = json.load(f)
        date_file = open('reminddate.json')
        reminddate_dict = json.load(date_file)
        lst = []
        lst1 = []
        for key in reminder_dict:
            date_of = datetime.strptime(key.strip(),
                                        '%Y-%m-%d %H:%M:%S.%f')
            if datetime.now() >= date_of:
                channel = client.get_channel(reminder_dict[key][2])
                await channel.send(
                    f"<@{reminder_dict[key][1]}> {reminder_dict[key][0]}!")
                lst.append(key)
        f.close()
        if lst:
            for item in lst:
                del reminder_dict[item]
            with open("remindme.json", "w") as f:
                json.dump(reminder_dict, f)
        for key in reminddate_dict:
            date_of = datetime.strptime(key.strip(),
                                        "%Y-%m-%d")
            if datetime.now() >= date_of:
                channel = client.get_channel(reminddate_dict[key][2])
                await channel.send(
                    f"<@{reminddate_dict[key][1]}> {reminddate_dict[key][0]}!")
                lst1.append(key)
        f.close()
        if lst1:
            for item in lst1:
                del reminddate_dict[item]
            with open("reminddate.json", "w") as f:
                json.dump(reminddate_dict, f)
    except json.decoder.JSONDecodeError:
        pass


@client.command()
async def remindme(ctx):
    try:
        msg = ctx.message.content.split()  # HH:MM Reminder
        dates = msg[1].split(':')
        dates = [int(i) for i in dates]
        remind_msg = msg[2]
        for i in range(3, len(msg)):
            remind_msg += ' ' + msg[i]
        await ctx.send(f'You will be reminded in {str(dates[0])} hours and '
                       f'{str(dates[1])} minutes: {remind_msg}')
        date = datetime.now() + timedelta(hours=dates[0]) + \
               timedelta(minutes=dates[1]) + \
               timedelta(seconds=dates[2] if len(dates) >= 3 else 0)
        with open('remindme.json', 'r+') as f:
            data = json.load(f)
            data.update({f'{date}': [remind_msg, ctx.author.id,
                                     ctx.channel.id]})
            f.seek(0)
            json.dump(data, f)
    except (ValueError, IndexError):
        await ctx.send('`Command used incorrectly. Remember to format the '
                       'command as "+remindme HH:MM:SS <Reminder message>" '
                       '(seconds is optional)`')


@client.command()
async def reminddate(ctx):
    try:
        msg = ctx.message.content.split()
        remind_msg = msg[2]
        for i in range(3, len(msg)):
            remind_msg += ' ' + msg[i]
        date = msg[1]
        await ctx.send(f'You will be reminded on {date}: {remind_msg}')
        with open('reminddate.json', 'r+') as f:
            data = json.load(f)
            data.update({f'{date}': [remind_msg, ctx.author.id,
                                     ctx.channel.id]})
            f.seek(0)
            json.dump(data, f)
    except (ValueError, IndexError):
        await ctx.send('`Command used incorrectly. Remember to format the '
                       'command as "+remindme YYYY-MM-DD '
                       '<Reminder message>`')


@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency * 1000)}ms')


@client.command(aliases=['conga', 'blobnuts', 'pcwob', 'blobroll',
                         'thisisfine', 'wobble', 'catdance', 'thonk', 'sadge',
                         'pensivecheese', 'menacing', 'kirbo', 'kirb', 'death', 'kirbgun'])
async def wob(ctx):
    user = str(ctx.author)
    await ctx.message.delete()
    await ctx.send(f'**{user[:-5]}**')
    await ctx.send(EMOTES[ctx.invoked_with])


@client.command()
async def help(ctx):
    embed = discord.Embed(color=discord.Colour.green())
    embed.set_author(name='Help')
    embed.add_field(name='Emotes',
                    value='conga, wob, blobnuts, pcwob, '
                          'blobroll, thisisfine, wobble, catdance, thonk, '
                          'sadge, pensivecheese, menacing, kirbo, kirb, death, kirbgun',
                    inline=False)
    embed.add_field(name='AFK', value='Lets user go afk.', inline=False)
    embed.add_field(name='Av', value='Shows avatar of user.', inline=False)
    embed.add_field(name='Misc (no prefix)',
                    value='dad joke (occasionally react to "i am"), pog, pain',
                    inline=False)
    embed.add_field(name='<a:conga:818437963616092183>',
                    value="Occasionally reacts with this emote based on "
                          "specific keywords",
                    inline=False)
    embed.add_field(name='Ping', value='Pong', inline=False)
    embed.add_field(name='Remindme', value='Reminder for something upcoming\n'
                                           'Format: HH:MM:SS <reminder message>'
                                           ' (seconds optional)', inline=False)
    embed.add_field(name='Reminddate', value='Reminder for an event\n'
                                             'Format: YYYY-MM-DD'
                                             '<reminder message>', inline=False)
    embed.add_field(name='Future plans',
                    value="- add clear/remove feature for remindme\n"
                          "- add reminderlist feature\n"
                          "- add schedule for upcoming school tests/assignments"
                          "- google results",
                    inline=False)
    await ctx.send(embed=embed)


@client.command()
async def av(ctx):
    acc = ctx.message.mentions[0].avatar_url if ctx.message.mentions \
        else ctx.author.avatar_url
    embed = discord.Embed(title=f"{ctx.author}",
                          description='**Avatar**',
                          color=0xecce8b)
    embed.set_image(url=acc)
    await ctx.send(embed=embed)


@client.command()
async def afk(ctx):
    AFK[ctx.author] = 'AFK' if ctx.message.content[4:].strip() == '' \
        else ctx.message.content[4:].strip()
    await ctx.send(f"<@{ctx.author.id}> I set you as AFK: "
                   f"{AFK[ctx.author]}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    msg = message.content.lower()
    split_msg = msg.split()
    send = message.channel.send
    guild = message.guild
    msg.replace("'", "")
    if message.author in AFK:
        del AFK[message.author]
        bot_msg = await send(f"<@!{message.author.id}> is no longer afk.")
        time.sleep(5)
        await bot_msg.delete()
    for key in AFK:
        if f'<@!{key.id}>' in message.content:
            user = str(key)
            await send(f"{user[:-5]} is afk: {str(AFK[key])}")

    elif msg.startswith('pog'):
        async with message.channel.typing():
            # do expensive stuff here
            await asyncio.sleep(2)
        await send(random.choice(POG) * 5)

    elif msg == 'pain':
        async with message.channel.typing():
            # do expensive stuff here
            await asyncio.sleep(2)
        await send(client.get_emoji(798310247952547940))

    elif (msg.startswith(('im ', 'i am ', "i'm "))) and \
            random.random() < 0.1 and guild.id != 754030333384589415:
        i = msg.find('m')
        new_msg = msg[i + 2:].strip()
        async with message.channel.typing():
            # do expensive stuff here
            await asyncio.sleep(2)
        await send(f"Hi {new_msg}, I'm dad!")

    elif msg == 'sus':
        async with message.channel.typing():
            # do expensive stuff here
            await asyncio.sleep(2)
        await send('https://tenor.com/view/hop-on-amoung-us-gif-18612031')

    if any(word in split_msg for word in HAPPY):
        await message.add_reaction('<:dance:818498443973492756>')

    if random.random() < 0.001:
        async with message.channel.typing():
            # do expensive stuff here
            await asyncio.sleep(3)
        await send(random.choice(RANDOM_STUFF))
    await client.process_commands(message)


keep_alive()
client.run(os.getenv('TOKEN'))
# client.close()
