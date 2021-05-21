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
from connect4 import Board
import math

load_dotenv('.env')

client = commands.Bot(command_prefix='+', case_insensitive=True)
client.remove_command('help')
BOT_ID = 834873988907139142
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
    '<:quagpog:819646454649323591>', '<:pog:819262750802575371>',
    '<:ppog:819262750751457341>', '<:pogu:819262751020023828>',
    '<:fishpog:819262750952783912>', '<a:pog:818437856779436102>',
    '<a:kannapog:825964713585147904>']

EMOTES = {
    'wob': '<a:wob:818437838588608573>',
    'wob2': '<a:wob2:835252304159834122>',
    'wobs': '<a:wob2:835252304159834122> <a:wob:818437838588608573>',
    'conga': '<a:conga:818437963616092183>' * 5,
    'blobnuts': '<a:blobNUTS:837091554933211197>',
    'pcwob': '<a:pcwob:837090418218631217>',
    'blobroll': '<a:blobroll:837090486459301971>',
    'thisisfine': '<a:thisisfine:837090507111792661>',
    'wobble': '<a:wobble:819661113515180102>',
    'catdance': '<a:catdance:821203420064382986>',
    'thonk': '<:thonk:822681360215965746>',
    'sadge': '<:sadge:822682645996503050>',
    'pensivecheese': '<:pensivecheese:823324747516608522>',
    'menacing': '<a:menacing:823417218431844372>' * 5,
    'kirbo': '<a:kirbo:832056783065186315>',
    'kirb': '<:kirb:833042433385168947>',
    'death': '<:death:833042433809580062>',
    'kirbgun': '<:kirbgun:833043498537320508>',
    'happy': '<:happy:834623832311857163>',
    'leak': '<:leak:834623832651202570>',
    'confoos': '<:confoos:834624292703961088>',
    'uhh': '<:uhh:834623832643469334>', 'oof': '<:oof:834623832466784287>'
}

PLAYER_PIECE = 'R'
AI_PIECE = 'Y'
# Emotes used for the player to choose their move
CONNECT4 = {'1️⃣': 0, '2️⃣': 1, '3️⃣': 2, '4️⃣': 3, '5️⃣': 4, '6️⃣': 5,
            '7️⃣': 6, '🏳': 'F'}
# numbers to print above connect 4 board
TOP_NUM = '** **\n:one: :two: :three: :four: :five: :six: :seven: \n'
# dictionary to keep track of where the game is happening
IDS = {}
# what index stands for what in IDS
BRD, P1, P2, CURR_P, TIMER, CHAN = 0, 1, 2, 3, 4, 5
# to differentiate between both players
P_DICT = {True: [P1, 'R', discord.Colour.red()],
          False: [P2, 'Y', discord.Colour.gold()]}
# list of gifs to send when a player wins
GIFS = []
gif_file = open("win_gifs.txt", "r")
content = gif_file.readline()
while content != '':
    content = gif_file.readline()
    GIFS.append(content)


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    reminder.start()
    afk_connect4.start()
    await client.change_presence(activity=discord.Game(' reality surf '
                                                       '| +help'))


@tasks.loop(seconds=60)
async def afk_connect4():
    remove = []
    for key in IDS:
        if IDS[key][TIMER] == 240:
            channel = IDS[key][CHAN]
            await channel.send(f'{IDS[key][P1].display_name} :crossed_swords:'
                               f' {IDS[key][P2].display_name}: '
                               f'Game ended due to inactivity')
            remove.append(key)
        else:
            IDS[key][TIMER] += 1
    for key in remove:
        del IDS[key]


@client.command()
async def connect4(ctx):
    """Starts a game with either a mentioned user or the bot and then
    adds it to IDS with message id as key, and a list with the board,
    player ids, and first move as the values"""
    # Doesn't start if no one or a bot is mentioned
    if len(ctx.message.mentions) == 0 or ctx.message.mentions[0] == client.user:
        player2 = client.user
    elif ctx.message.mentions[0].bot or \
            ctx.message.mentions[0] == ctx.author:
        await ctx.send(':x: ERROR: You cannot tag a bot or yourself. '
                       '\nEither tag another user you want to play with'
                       ' or the bot/no one if you want to play with the bot.')
        return None
    else:
        player2 = ctx.message.mentions[0]
    player1 = ctx.author
    board = Board()
    # Prints starting board
    message = await ctx.send(f':red_circle: '
                             f'{player1.display_name} :crossed_swords: '
                             f'{player2.display_name} :yellow_circle: \n'
                             + TOP_NUM + board.print_board() +
                             f'\n Current player: <@{player1.id}>'
                             f'\n :flag_white:: Forfeit')
    # Adds the emotes the players will be clicking on and adds
    # the game to the global dictionary
    for emoji in CONNECT4:
        await message.add_reaction(emoji)
    IDS[message.id] = [board, player1, player2, 'R', 0, ctx.channel]


@client.event
async def on_reaction_add(reaction, user) -> None:
    """Check which reaction role was pressed and changes the board
    accordingly."""
    # If reaction is in a channel where no one is playing, or if the person
    # adding the reactions is the bot, do nothing.
    if reaction.message.id not in IDS or \
            user.id == BOT_ID:
        return None
    curr_channel = IDS[reaction.message.id]
    channel = curr_channel[CHAN]
    curr_piece = curr_channel[CURR_P]
    curr_board = curr_channel[BRD]
    # for P_DICT
    player_red = True if curr_piece == 'R' else False
    curr_player = curr_channel[P_DICT[player_red][0]]
    other_player = curr_channel[P_DICT[not player_red][0]]
    await reaction.remove(user)
    # stops the function if a reaction was added or if the reaction
    # was sent by a non-player
    if reaction.emoji not in CONNECT4.keys() \
            or (user != curr_player and user != other_player):
        return None
    # At this point we know it's one of the two players who reacted to an emote.
    # Thus, we can directly cancel the game if one of the players forfeit.
    elif CONNECT4[reaction.emoji] == 'F':
        del IDS[reaction.message.id]
        embed = discord.Embed(title=f' {user.display_name} forfeited, '
                                    f'{curr_channel[1].display_name}'
                                    f' :crossed_swords: '
                                    f'{curr_channel[2].display_name}',
                              color=discord.Colour.green())
        embed.set_image(url='https://media1.tenor.com/images/'
                            '8c3cb918305bf277589c6ad84dfcea53/tenor.gif')
        await channel.send(embed=embed)
        return None
    # if the column is already filled, sends error message and does nothing
    # with the board
    if not curr_board.is_valid_location(0, CONNECT4[reaction.emoji]):
        await reaction.message.edit(content=f':red_circle:'
                                            f'{curr_channel[1].display_name}'
                                            f' :crossed_swords: '
                                            f'{curr_channel[2].display_name}'
                                            f' :yellow_circle: \n'
                                            + TOP_NUM + curr_board.print_board()
                                            + f':x: ERROR: Column full. :x:'
                                              f'\n Current player: '
                                              f'<@{curr_player.id}>'
                                              f'\n :flag_white:: Forfeit')
        return None
    # stops the function if user is the other player
    if user != curr_player:
        return None
    # changes current piece to next player
    curr_channel[CURR_P] = P_DICT[not player_red][1]
    r = 5
    # finds a valid location to drop the piece in starting from the bottom
    # of the column
    while not curr_board.is_valid_location(r, CONNECT4[reaction.emoji]):
        r -= 1
    # drops the piece then edits the message to the updated board
    curr_board.drop_piece(r, CONNECT4[reaction.emoji], curr_piece)
    # reset afk timer
    curr_channel[TIMER] = 0
    # Checks if there are no more positions to drop a piece, then ends the game
    # as a draw if this is true.
    if len(curr_board.get_valid_locations()) == 0:
        del IDS[reaction.message.id]
        embed = discord.Embed(title="It's a draw!",
                              color=discord.Colour.red())
        embed.set_image(url='https://media1.tenor.com/images/'
                            '729fc07335063f9d8a23002a71fdb0a8/tenor.gif')
        await channel.send(embed=embed)
        return None
    # Checks if there is a connect 4, and if so, sends a winner message and
    # removes the game from IDS
    if curr_board.is_win(curr_piece):
        curr_color = P_DICT[player_red][2]
        embed = discord.Embed(title=f'{curr_player.display_name} wins!',
                              color=curr_color)
        embed.set_image(url=random.choice(GIFS))
        await channel.send(embed=embed)
        await reaction.message.edit(content=f':red_circle: '
                                            f'{curr_channel[1].display_name}'
                                            f' :crossed_swords: '
                                            f'{curr_channel[2].display_name}'
                                            f' :yellow_circle: \n'
                                            + TOP_NUM + curr_board.print_board()
                                            + f'\n<@{curr_player.id}> wins!')
        del IDS[reaction.message.id]
        return None
    # If there is no connect 4, print the board and go to the next turn.
    else:
        await reaction.message.edit(content=f':red_circle: '
                                            f'{curr_channel[1].display_name}'
                                            f' :crossed_swords: '
                                            f'{curr_channel[2].display_name}'
                                            f' :yellow_circle: \n'
                                            + TOP_NUM + curr_board.print_board()
                                            + f'\n Current player: '
                                              f'<@{other_player.id}>'
                                              f'\n :flag_white:: Forfeit')
    # If playing with bot, run the minimax algorithm and then drop the piece
    # the algorithm has chosen.
    if other_player.bot:
        await asyncio.sleep(1)
        # Goes 6 layers deep into the tree
        col, minimax_score = curr_board.minimax(5, -math.inf, math.inf, True)
        row = curr_board.get_valid_locations()[col]
        # drop the piece into the board
        curr_board.drop_piece(row, col, AI_PIECE)
        curr_channel[TIMER] = 0
        # If bot plays winning move, send winning message and delete
        # game from IDS.
        if curr_board.is_win(curr_channel[CURR_P]):
            other_color = P_DICT[not player_red][2]
            embed = discord.Embed(title=f'{other_player.display_name} '
                                        f'wins!', color=other_color)
            embed.set_image(url=random.choice(GIFS))
            await channel.send(embed=embed)
            await reaction.message.edit(
                content=f':red_circle: '
                        f'{curr_channel[1].display_name}'
                        f' :crossed_swords: '
                        f'{curr_channel[2].display_name}'
                        f' :yellow_circle: \n'
                        + TOP_NUM + curr_board.print_board()
                        + f'\n<@{other_player.id}> wins!')
            del IDS[reaction.message.id]
        # Otherwise, just print the board
        else:
            await reaction.message.edit(
                content=f':red_circle: '
                        f'{curr_channel[1].display_name}'
                        f' :crossed_swords: '
                        f'{curr_channel[2].display_name}'
                        f' :yellow_circle: \n'
                        + TOP_NUM + curr_board.print_board()
                        + f'\n Current player:'
                          f' <@{curr_player.id}>'
                          f'\n :flag_white:: Forfeit')
        # changes current piece back to user
        curr_channel[CURR_P] = curr_piece


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


@client.command(aliases=['wob', 'wob2', 'wobs', 'blobnuts', 'pcwob',
                         'blobroll', 'thisisfine', 'wobble', 'catdance',
                         'thonk', 'sadge', 'pensivecheese', 'menacing', 'kirbo',
                         'kirb', 'death', 'kirbgun', 'happy', 'leak', 'confoos',
                         'uhh', 'oof'])
async def conga(ctx):
    user = str(ctx.author)
    await ctx.message.delete()
    await ctx.send(f'**{user[:-5]}**')
    await ctx.send(EMOTES[ctx.invoked_with])


@client.command()
async def help(ctx):
    embed = discord.Embed(color=discord.Colour.green())
    embed.set_author(name='Help')
    embed.add_field(name='Emotes',
                    value='conga, wob, wob2, wobs, blobnuts, pcwob, '
                          'blobroll, thisisfine, wobble, catdance, thonk, '
                          'sadge, pensivecheese, menacing, kirbo, kirb, '
                          'death, kirbgun, happy, leak, confoos, uhh, oof',
                    inline=False)
    embed.add_field(name='AFK', value='Lets user go afk.', inline=False)
    embed.add_field(name='Av', value='Shows avatar of user.', inline=False)
    embed.add_field(name='Misc (no prefix)',
                    value='dad joke (occasionally react to "i am"), pog, pain',
                    inline=False)
    embed.add_field(name='<a:conga:818437963616092183> '
                         '<:sheesh:844348540327297025>',
                    value="Occasionally reacts with this emote based on "
                          "specific keywords",
                    inline=False)
    embed.add_field(name='Ping', value='Pong!', inline=False)
    embed.add_field(name='Remindme', value='Reminder for something upcoming\n'
                                           'Format: HH:MM:SS <reminder message>'
                                           ' (seconds optional)', inline=False)
    embed.add_field(name='Reminddate', value='Reminder for an event\n'
                                             'Format: YYYY-MM-DD '
                                             '<reminder message>', inline=False)
    embed.add_field(name='Connect4 <:connect4:840473222846742549>',
                    value='Play connect 4 with others or with'
                          ' the bot! Mention the user you want'
                          ' to play with or mention the bot/no'
                          ' one to play with the bot', inline=False)
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

    if msg.startswith('pog'):
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

    if 'bussin' in split_msg or (msg.startswith('shee') and
                                 msg.endswith('esh')) or 'cheese' in split_msg:
        await message.add_reaction('<:sheesh:844348540327297025>')

    if random.random() < 0.001:
        async with message.channel.typing():
            # do expensive stuff here
            await asyncio.sleep(3)
        await send(random.choice(RANDOM_STUFF))
    await client.process_commands(message)


keep_alive()
client.run(os.getenv('TOKEN'))
# client.close()
