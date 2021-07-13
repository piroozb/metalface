import discord
import os
from dotenv import load_dotenv
from keep_alive import keep_alive
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice
from discord.ext import commands, tasks
import asyncio
from connect4 import Board
import random
from datetime import datetime
import math
from discord_slash_components import DiscordComponents
from discord_components import Button
from dateutil.relativedelta import relativedelta
import json

load_dotenv('.env')

client = commands.Bot(command_prefix="+", intents=discord.Intents.all())
# Declares slash commands through the client.
slash = SlashCommand(client, sync_commands=True)
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
    "I never leave the bed when the sun is looking into my soul",
    "Words are like clay. It is not the person who speaks "
    "the words that shapes the clay. The one who is listening does.",
    "It is not the size of the bag, it is the size of who holds it.",
    "even if you are unmuted it is you who must decide to open your mouth"
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
    'uhh': '<:uhh:834623832643469334>',
    'sheesh': '<:sheesh:844348540327297025>'
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
    DiscordComponents(client, slash)
    await client.change_presence(activity=discord.Game('Slash commands!'
                                                       ' | /help'))


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


@slash.slash(name="connect4",
             description="Play against another user or our bot.",
             options=[create_option(
                 name="user",
                 description='If you want to play with another user',
                 option_type=6, required=False)])
async def _connect4(ctx, player2=None):
    """Starts a game with either a mentioned user or the bot and then
    adds it to IDS with message id as key, and a list with the board,
    player ids, and first move as the values"""
    # Starts against bot if no one or bot is mentioned
    player1, board = ctx.author, Board()
    if player2 is None or player2 == client.user:
        player2 = client.user
        message = await ctx.send('Loading board...')
        async with message.channel.typing():
            # do expensive stuff here
            await asyncio.sleep(1)
        await message.delete()
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
    # Doesn't start if other bot or user itself is mentioned
    elif player2.bot or \
            player2 == ctx.author:
        await ctx.send(':x: ERROR: You cannot tag a bot or yourself. '
                       '\nEither tag another user you want to play with'
                       ' or the bot/no one if you want to play with the bot.')
        return None
    # At this point someone must've been mentioned, so starts game against them
    else:
        # Asks second user if they want to accept the invite.
        message = await ctx.send(f"<@{player2.id}> Accept invite?", components=[
            [Button(label="Accept", style=1), Button(label="Decline")]])
        try:
            interaction = await client.wait_for(
                "button_click", timeout=60, check=lambda i: i.author == player2)
            if interaction.component.label == "Accept":
                # Prints starting board
                message2 = await ctx.send(f':red_circle: '
                                          f'{player1.display_name} '
                                          f':crossed_swords: '
                                          f'{player2.display_name} '
                                          f':yellow_circle: \n'
                                          + TOP_NUM + board.print_board() +
                                          f'\n Current player: <@{player1.id}>'
                                          f'\n :flag_white:: Forfeit')
                await interaction.respond(content="Accepted!")
                # Adds the emotes the players will be clicking on and adds
                # the game to the global dictionary
                for emoji in CONNECT4:
                    await message2.add_reaction(emoji)
                IDS[message2.id] = [board, player1, player2,
                                    'R', 0, ctx.channel]
            elif interaction.component.label == "Decline":
                await ctx.send(f"Game cancelled: "
                               f"invite was declined by <@{player2.id}>.")
                await interaction.respond(content="Declined!")
            await asyncio.sleep(2)
            await message.delete()
            return None
        except Exception as e:  # TimeoutError doesn't work for some reason
            await ctx.send("Game cancelled: invite timed out.")
            await asyncio.sleep(5)
            await message.delete()
            return e


@client.event
async def on_reaction_add(reaction, user) -> None:
    """
    Check which reaction role was pressed and changes the board accordingly.
    """
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
    player_red = curr_piece == 'R'
    curr_player = curr_channel[P_DICT[player_red][0]]
    other_player = curr_channel[P_DICT[not player_red][0]]
    await reaction.remove(user)
    # stops the function if a reaction was added or if the reaction
    # was sent by a non-player
    if reaction.emoji not in CONNECT4.keys() or user not in [curr_player,
                                                             other_player]:
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
        # Goes 5 layers deep into the tree
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


@tasks.loop(seconds=15)
async def reminder():
    f = open('remindme.json', 'r')
    data = json.load(f)
    i = len(data) - 1
    if data:
        while i >= 0 and datetime.strptime(
                data[i]['time'], "%m/%d/%Y, %H:%M:%S") <= datetime.now():
            val = data.pop()
            embed = discord.Embed(color=discord.Colour.blue(),
                                  title='Reminder',
                                  description=val['message'])
            embed.set_thumbnail(url='https://i.imgur.com/HFPdTGU.png')
            await client.get_user(val['user']).send(embed=embed)
            i -= 1
        f.close()
        with open("remindme.json", "w") as f:
            json.dump(data, f)


@slash.slash(name="remindme", description="Set a reminder",
             options=[create_option(
                 name='message', description='Reminder message',
                 option_type=3, required=True),
                 create_option(
                     name="time",
                     description='Time at which to send the reminder.'
                                 'Ex: "in 3 days" or "on July 29th at 3pm"',
                     option_type=3, required=True)])
async def _remindme(ctx, message: str, time: str):
    dates = time.split()
    types = {'year': 0, 'month': 0, 'day': 0, 'hour': 0, 'hr': 0, 'min': 0}
    embed = discord.Embed(color=discord.Colour.red(),
                          description='Sorry, I could not understand what '
                                      'reminder you wanted to set. '
                                      'Please try again.')
    try:
        if any(typ in time for typ in types):
            for i in range(len(dates)):
                for item in types:
                    if item in dates[i]:
                        types[item] += int(dates[i - 1])
            date = datetime.now() + relativedelta(years=+types['year']) + \
                   relativedelta(months=types['month']) + \
                   relativedelta(days=+types['day']) + \
                   relativedelta(hours=+types['hour'] + types['hr']) + \
                   relativedelta(minutes=+types['min'])
        else:
            months = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5,
                      'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10,
                      'nov': 11, 'dec': 12}
            date = datetime.now()
            for i in range(len(dates)):
                for month in months:
                    if month in dates[i].lower():
                        date = date.replace(month=months[month])
                        if i < len(dates) - 1:
                            if dates[i + 1].isdigit():
                                date = date.replace(day=int(dates[i + 1]))
                            elif dates[i + 1][:-2].isdigit():
                                date = date.replace(day=int(dates[i + 1][:-2]))
                if dates[i][-2:].lower() in ['pm', 'am']:
                    num = dates[i][:-2]
                    if num.isdigit():
                        date = date.replace(hour=int(num)
                        if dates[i][-2:].lower() == 'am'
                        else int(num) + 12)
                    elif num.replace(':', '').isnumeric():
                        if ':' in dates[i]:
                            val = num.split(':')
                            date = date.replace(hour=int(val[0]))
                            date = date.replace(minute=int(val[1]))
                        else:
                            await ctx.send(embed=embed)
                            return None
                elif dates[i].isdigit():
                    if len(dates[i]) <= 2:
                        pass
                    elif len(dates[i]) == 4:
                        date = date.replace(year=int(dates[i]))
                        print(date)
                    else:
                        await ctx.send(embed=embed)
                        return None

        if date <= datetime.now():
            await ctx.send(embed=embed)
            return None
        embed = discord.Embed(color=discord.Colour.green(),
                              description=f'You will be reminded on '
                                          f'{date:%b %d, %Y at %H:%M}: '
                                          f'{message}')
        await ctx.send(embed=embed)
        with open('remindme.json', 'r+') as f:
            data = json.load(f)
            data.append({'user': ctx.author.id, 'message': message,
                         'time': date.strftime("%m/%d/%Y, %H:%M:%S")})
            data = sorted(data, key=lambda k:
            datetime.
                          strptime(k['time'], "%m/%d/%Y, %H:%M:%S"))
            data.reverse()
            f.seek(0)
            json.dump(data, f)
    except (TypeError, ValueError, IndexError):
        await ctx.send(embed=embed)


@slash.slash(name="ping", description="Ping the bot.")
async def _ping(ctx):  # Defines a new "context" (ctx) command called "ping."
    await ctx.send(f"Pong! ({round(client.latency * 1000)}ms)")


@slash.slash(name="emote", description="Use an emote.",
             options=[create_option(
                 name="emote",
                 description='The emote you want to output',
                 option_type=3,
                 required=True,
                 choices=[
                        create_choice(name='wob', value='wob'),
                        create_choice(name='wob2', value='wob2'),
                        create_choice(name='wobs', value='wobs'),
                        create_choice(name='pcwob', value='pcwob'),
                        create_choice(name='blobroll', value='blobroll'),
                        create_choice(name='thisisfine', value='thisisfine'),
                        create_choice(name='catdance', value='catdance'),
                        create_choice(name='thonk', value='thonk'),
                        create_choice(name='sadge', value='sadge'),
                        create_choice(name='pensivecheese',
                                      value='pensivecheese'),
                        create_choice(name='menacing', value='menacing'),
                        create_choice(name='kirbo', value='kirbo'),
                        create_choice(name='kirb', value='kirb'),
                        create_choice(name='death', value='death'),
                        create_choice(name='kirbgun', value='kirbgun'),
                        create_choice(name='happy', value='happy'),
                        create_choice(name='oof', value='oof'),
                        create_choice(name='sheesh', value='sheesh')
                          ])])
async def _emote(ctx, emote: str):
    await ctx.send(EMOTES[emote])


@slash.slash(name='help', description='Bot information.')
async def _help(ctx):
    embed = discord.Embed(title='Help', color=discord.Colour.green())
    embed.add_field(name='Emotes',
                    value='wob, wob2, wobs, pcwob, '
                          'blobroll, thisisfine, catdance, thonk, '
                          'sadge, pensivecheese, menacing, kirbo, kirb, '
                          'death, kirbgun, happy, oof, sheesh',
                    inline=False)
    embed.add_field(name='AFK', value='Lets user go afk.', inline=False)
    embed.add_field(name='Avatar', value='Shows avatar of user.', inline=False)
    embed.add_field(name='Misc (no prefix)',
                    value='dad joke (occasionally react to "i am"), pog, pain',
                    inline=False)
    embed.add_field(name='<a:catdance:821203420064382986>, '
                         '<:sheesh:844348540327297025>',
                    value="Occasionally reacts with these emote based on "
                          "specific keywords",
                    inline=False)
    embed.add_field(name='Ping', value='Pong!', inline=False)
    embed.add_field(name='Remindme', value='Reminder for something upcoming\n',
                    inline=False)
    embed.add_field(name='Connect4 <:connect4:840473222846742549>',
                    value='Play connect 4 with others or with'
                          ' the bot! Mention the user you want'
                          ' to play with or mention the bot/no'
                          ' one to play with the bot', inline=False)
    embed.add_field(name='Future plans',
                    value="- add clear/remove feature for remindme\n"
                          "- add reminderlist feature\n"
                          "- add schedule for upcoming school tests/assignments"
                          "\n- google results",
                    inline=False)
    await ctx.send(embed=embed)


@slash.slash(name='avatar', description="Display a users' avatar",
             options=[create_option(
                 name="user",
                 description='Fetch avatar from',
                 option_type=6, required=False)])
async def _avatar(ctx, user=None):
    if user is not None:
        embed = discord.Embed(title=f"{user.display_name}",
                              description='**Avatar**',
                              color=0xecce8b)
        embed.set_image(url=user.avatar_url)
    else:
        embed = discord.Embed(title=f"{ctx.author.display_name}",
                              description='**Avatar**',
                              color=0xecce8b)
        embed.set_image(url=ctx.author.avatar_url)
    await ctx.send(embed=embed)


@slash.slash(name='afk', description="Set an AFK status",
             options=[create_option(
                 name="message",
                 description='Message when another user mentions',
                 option_type=3, required=True)])
async def _afk(ctx, message: str):
    AFK[ctx.author] = message
    await ctx.send(f"{ctx.author.display_name} I set you as AFK: "
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
        await asyncio.sleep(5)
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
        await send('<:pain:798310247952547940>')

    elif (msg.startswith(('im ', 'i am ', "i'm "))) and \
            random.random() < 0.1 and guild.id != 754030333384589415:
        i = msg.find('m')
        new_msg = msg[i + 2:].strip()
        async with message.channel.typing():
            # do expensive stuff here
            await asyncio.sleep(2)
        await send(f"Hi {new_msg}, I'm dad!")

    elif msg.startswith('+'):
        async with message.channel.typing():
            # do expensive stuff here
            await asyncio.sleep(2)
        embed = discord.Embed(description="We have migrated to slash commands. "
                                          "Type /help to see what features are "
                                          "available. If that doesn't work, you"
                                          " may have to re-invite the bot "
                                          "[here](https://discord.com/api/oauth2/authorize?client_id=834873988907139142&permissions=2148006976&scope=bot%20applications.commands)."
                                          "If slash commands have just been"
                                          "implemented, you may have to wait"
                                          "a couple hours before it starts "
                                          "working again",
                              color=discord.Colour.dark_purple())
        await send(embed=embed)

    if any(word in split_msg for word in HAPPY):
        await message.add_reaction(EMOTES['catdance'])

    if 'bussin' in split_msg or (msg.startswith('shee') and
                                 msg.endswith('esh')) or 'cheese' in split_msg:
        await message.add_reaction(EMOTES['sheesh'])
    if 'fax' in msg:
        await message.add_reaction('📠')
    if random.random() < 0.001:
        async with message.channel.typing():
            # do expensive stuff here
            await asyncio.sleep(3)
        await send(random.choice(RANDOM_STUFF))
    await client.process_commands(message)


keep_alive()
client.run(os.getenv('TOKEN'))
# client.close()
