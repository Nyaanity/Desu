import discord
from discord.ext import commands
import aiohttp
from random import choice, randint
import asyncio
from bs4 import BeautifulSoup as bs4
import io
import re
from random import randint
from __bot.embeds import Embeds as embeds
from __bot.emojis import Emojis as emojis


regionals = {
    'a': '\N{REGIONAL INDICATOR SYMBOL LETTER A}', 'b': '\N{REGIONAL INDICATOR SYMBOL LETTER B}',
    'c': '\N{REGIONAL INDICATOR SYMBOL LETTER C}',
    'd': '\N{REGIONAL INDICATOR SYMBOL LETTER D}', 'e': '\N{REGIONAL INDICATOR SYMBOL LETTER E}',
    'f': '\N{REGIONAL INDICATOR SYMBOL LETTER F}',
    'g': '\N{REGIONAL INDICATOR SYMBOL LETTER G}', 'h': '\N{REGIONAL INDICATOR SYMBOL LETTER H}',
    'i': '\N{REGIONAL INDICATOR SYMBOL LETTER I}',
    'j': '\N{REGIONAL INDICATOR SYMBOL LETTER J}', 'k': '\N{REGIONAL INDICATOR SYMBOL LETTER K}',
    'l': '\N{REGIONAL INDICATOR SYMBOL LETTER L}',
    'm': '\N{REGIONAL INDICATOR SYMBOL LETTER M}', 'n': '\N{REGIONAL INDICATOR SYMBOL LETTER N}',
    'o': '\N{REGIONAL INDICATOR SYMBOL LETTER O}',
    'p': '\N{REGIONAL INDICATOR SYMBOL LETTER P}', 'q': '\N{REGIONAL INDICATOR SYMBOL LETTER Q}',
    'r': '\N{REGIONAL INDICATOR SYMBOL LETTER R}',
    's': '\N{REGIONAL INDICATOR SYMBOL LETTER S}', 't': '\N{REGIONAL INDICATOR SYMBOL LETTER T}',
    'u': '\N{REGIONAL INDICATOR SYMBOL LETTER U}',
    'v': '\N{REGIONAL INDICATOR SYMBOL LETTER V}', 'w': '\N{REGIONAL INDICATOR SYMBOL LETTER W}',
    'x': '\N{REGIONAL INDICATOR SYMBOL LETTER X}',
    'y': '\N{REGIONAL INDICATOR SYMBOL LETTER Y}', 'z': '\N{REGIONAL INDICATOR SYMBOL LETTER Z}',
    '0': '0⃣', '1': '1⃣', '2': '2⃣', '3': '3⃣',
    '4': '4⃣', '5': '5⃣', '6': '6⃣', '7': '7⃣', '8': '8⃣', '9': '9⃣', '!': '\u2757',
    '?': '\u2753'
}

emoji_reg = re.compile(r'<:.+?:([0-9]{15,21})>')

text_flip = {}
char_list = "!#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}"
alt_char_list = "{|}zʎxʍʌnʇsɹbdouɯlʞɾᴉɥƃɟǝpɔqɐ,‾^[\\]Z⅄XMΛ∩┴SɹQԀONW˥ʞſIHפℲƎpƆq∀@¿<=>;:68ㄥ9ϛㄣƐᄅƖ0/˙-'+*(),⅋%$#¡"[
    ::-1]
for idx, char in enumerate(char_list):
    text_flip[char] = alt_char_list[idx]
    text_flip[alt_char_list[idx]] = char

monika_faces = [x for x in "abcdefghijklmnopqr"]
natsuki_faces = [x for x in "abcdefghijklmnopqrstuvwxyz"]
natsuki_faces.extend(["1t", "2bt", "2bta", "2btb", "2btc", "2btd", "2bte", "2btf", "2btg", "2bth", "2bti",
                      "2t", "2ta", "2tb", "2tc", "2td", "2te", "2tf", "2tg", "2th", "2ti"])
sayori_faces = [x for x in "abcdefghijklmnopqrstuvwxy"]
yuri_faces = [x for x in "abcdefghijklmnopqrstuvwx"]
yuri_faces.extend(["y1", "y2", "y3", "y4", "y5", "y6", "y7"])
ddlc_items = {
    "body": {
        "monika": ["1", "2"],
        "natsuki": ["1b", "1", "2b", "2"],
        "yuri": ["1b", "1", "2b", "2"],
        "sayori": ["1b", "1", "2b", "2"]
    },
    "face": {
        "monika": monika_faces,
        "natsuki": natsuki_faces,
        "yuri": yuri_faces,
        "sayori": sayori_faces
    }
}

ddlc_get_character = {
    "y": "yuri",
    "n": "natsuki",
    "m": "monika",
    "s": "sayori"
}


class Fun(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.evergene_api = 'https://evergene.io/api/'
        self.random_api = 'https://some-random-api.ml/'

    @commands.command()
    @commands.guild_only()
    async def insult(self, ctx):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get('https://evilinsult.com/generate_insult.php?lang=en&type=json') as request:
                    response = await request.json()
                    await ctx.reply(response["insult"])

    @commands.command()
    @commands.guild_only()
    async def dadjoke(self, ctx):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get('https://icanhazdadjoke.com', headers={'Accept': 'application/json'}) as request:
                    response = await request.json()
                    await ctx.reply(response["joke"])

    @commands.command()
    @commands.guild_only()
    async def simpforwho(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        embed = discord.Embed(description='You are simping for {}.'.format(choice([x.mention for x in ctx.guild.members if not x.bot])), color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else member.color if not self.bot.DEFAULT_COLOR else None)
        embed.set_author(
            name=member, icon_url=member.avatar_url, url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def howgay(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        embed = discord.Embed(description='**{}%** gay.'.format(randint(0, 100)), color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else member.color if not self.bot.DEFAULT_COLOR else None)
        embed.set_author(
            name=member, icon_url=member.avatar_url, url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=['simpr8'])
    @commands.guild_only()
    async def simprate(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        embed = discord.Embed(description='**{}%** simp.'.format(randint(0, 100)), color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else member.color if not self.bot.DEFAULT_COLOR else None)
        embed.set_author(
            name=member, icon_url=member.avatar_url, url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def hug(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.evergene_api + 'hug') as request:
                    response = await request.json()
                    await ctx.send(embed=embeds.DescriptionImage._text_to_embed(self.bot, ctx, '**{}** is giving **{}**{}'.format(ctx.author, 'themselves' if member == ctx.author else member.name, ' a hug...' if member == ctx.author else ' a hug!'), response['url']))

    @commands.command()
    @commands.guild_only()
    async def slap(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.evergene_api + 'slap') as request:
                    response = await request.json()
                    await ctx.send(embed=embeds.DescriptionImage._text_to_embed(self.bot, ctx, '**{}** is slapping **{}**{}'.format(ctx.author, 'themselves' if member == ctx.author else member.name, '...' if member == ctx.author else '!'), response['url']))

    @commands.command()
    @commands.guild_only()
    async def pat(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.evergene_api + 'pat') as request:
                    response = await request.json()
                    await ctx.send(embed=embeds.DescriptionImage._text_to_embed(self.bot, ctx, '**{}** is patting **{}**{}'.format(ctx.author, 'themselves' if member == ctx.author else member.name, '...' if member == ctx.author else '!'), response['url']))

    @commands.command()
    @commands.guild_only()
    async def cuddle(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.evergene_api + 'cuddle') as request:
                    response = await request.json()
                    await ctx.send(embed=embeds.DescriptionImage._text_to_embed(self.bot, ctx, '**{}** is cuddling with **{}**{}'.format(ctx.author, 'themselves' if member == ctx.author else member.name, '...' if member == ctx.author else '!'), response['url']))

    @commands.command(aliases=['rainbow', 'lgbtq'])
    @commands.guild_only()
    async def gay(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', 'https://some-random-api.ml/canvas/gay?avatar={}'.format(avatar)))

    @commands.command()
    @commands.guild_only()
    async def glass(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', 'https://some-random-api.ml/canvas/glass?avatar={}'.format(avatar)))

    @commands.command()
    @commands.guild_only()
    async def wasted(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', 'https://some-random-api.ml/canvas/wasted?avatar={}'.format(avatar)))

    @commands.command(aliases=['passed'])
    @commands.guild_only()
    async def missionpassed(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', 'https://some-random-api.ml/canvas/passed?avatar={}'.format(avatar)))

    @commands.command()
    @commands.guild_only()
    async def jail(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', 'https://some-random-api.ml/canvas/jail?avatar={}'.format(avatar)))

    @commands.command()
    @commands.guild_only()
    async def comrade(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', 'https://some-random-api.ml/canvas/comrade?avatar={}'.format(avatar)))

    @commands.command()
    @commands.guild_only()
    async def pixelate(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', 'https://some-random-api.ml/canvas/pixelate?avatar={}'.format(avatar)))

    @commands.command()
    @commands.guild_only()
    async def simpcard(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', 'https://some-random-api.ml/canvas/simpcard?avatar={}'.format(avatar)))

    @commands.command()
    @commands.guild_only()
    async def horny(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', 'https://some-random-api.ml/canvas/horny?avatar={}'.format(avatar)))

    @commands.command()
    @commands.guild_only()
    async def lolice(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', 'https://some-random-api.ml/canvas/lolice?avatar={}'.format(avatar)))

    @commands.command()
    @commands.guild_only()
    async def blur(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', 'https://some-random-api.ml/canvas/blur?avatar={}'.format(avatar)))

    @commands.command()
    @commands.guild_only()
    async def stupid(self, ctx, member: discord.Member = None, *, text):
        member = ctx.author if not member else member
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', 'https://some-random-api.ml/canvas/its-so-stupid?avatar={}&dog={}'.format(avatar, text.replace(' ', '+'))))

    @commands.command(aliases=['twitter'])
    @commands.guild_only()
    async def tweet(self, ctx, *, message):
        avatar = ctx.author.avatar_url_as(format='jpg')
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get('https://nekobot.xyz/api/imagegen?type=tweet&username={}&displayname={}&avatar={}&text={}'.format(ctx.author.name, ctx.author.name, avatar, message)) as r:
                    res = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, '{} tweeted!'.format(ctx.author.name), res['message']))

    @commands.command(aliases=['ytcomment'])
    @commands.guild_only()
    async def youtubecomment(self, ctx, *, message):
        avatar = ctx.author.avatar_url_as(format='jpg')
        async with ctx.typing():
            await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, '{} commented!'.format(ctx.author.name), 'https://some-random-api.ml/canvas/youtube-comment?username={}&avatar={}&comment={}'.format(ctx.author.name, avatar, message.replace(' ', '+'))))

    @commands.command(aliases=['redditmeme', 'memes'])
    @commands.guild_only()
    async def meme(self, ctx):
        async with ctx.typing():
            data = await self.get_res_data('r/memes/random', {'limit': 10})
            await self.send_post(ctx, data[0]['data']['children'][0])

    async def random_from_post_list(self, ctx, url_part: str, params: dict):
        res = await self.get_res_data(url_part, params)
        error = res.get('error')
        if error:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, error))
        posts = res['data']['children']
        posts = list(filter(self.post_safe_filter, posts))
        if not posts:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No memes found.'))
        if int(res['data']['ups']) < 7000:
            post = choice(posts)
        await self.send_post(ctx, post)

    async def get_res_data(self, url_part, params):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://reddit.com/{}.json'.format(url_part), params=params) as response:
                print(await response.json())
                return await response.json()

    async def send_post(self, ctx, post):
        post = post['data']
        img_url = post.get('url')
        title = post.get('title')
        ups = post.get('ups')
        num_comments = post.get('num_comments')
        embed = embeds.TitleImage._text_to_embed(self.bot, ctx, title, img_url)
        embed.set_footer(text=f"👍 {ups} | 💬 {num_comments}")
        await ctx.send(embed=embed)

    def post_safe_filter(self, post):
        return(
            post['data']['is_reddit_media_domain'] and
            not post['data']['over_18'] and
            int(post['data']['ups']) > 7000)

    async def close_session(self):
        # await session.close()
        ...

    @commands.command()
    @commands.guild_only()
    async def dankmeme(self, ctx):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.evergene_api + 'dankmemes') as request:
                    response = await request.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', response['url']))

    @commands.command()
    @commands.guild_only()
    async def animeme(self, ctx):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.evergene_api + 'animemes') as request:
                    response = await request.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', response['url']))

    @commands.command(name='8ball')
    @commands.guild_only()
    async def eight_ball(self, ctx, *, question):
        answers = [
            'Yesn\'t.',
            'Non\'t.',
            'Possibly.',
            'Perhaps..',
            'Ask again later..',
            'Try again.',
            'It\'s certain.',
            'Most likely no.',
            'Most likely yes.',
            'No.',
            'Yes.',
            'Definetly a yes.',
            'Definetly a no.',
            'What do you expect me to answer?',
            'Can\'t answer now, try again.',
            'Without a doubt.',
            'Yes, definitely.',
            'You may rely on it.',
            'As I see it, yes.',
            'Most likely.',
            'Outlook good.',
            'Signs point to yes.',
            'Computer says yes.',
            'Code told me to say yes.',
            'Code told me to say no.',
            'Ask again later.',
            'I\'ll better not tell you that..',
            'Unpredictable.',
            'U good? Ask your question again please.',
            'Don\'t count on it.',
            'My reply is no.',
            'My sources say no.',
            'Outlook not so good.',
            'Very doubtful.'
        ]
        await ctx.reply(choice(answers))

    @commands.command(aliases=['searchgif'])
    @commands.guild_only()
    async def gifsearch(self, ctx, *, gif_name):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        'https://api.giphy.com/v1/gifs/search?api_key=ldQeNHnpL3WcCxJE1uO8HTk17ICn8i34&q={}&limit=1&offset=0&rating=R&lang=en'.format(gif_name)) as r:
                    res = await r.json()
                    try:
                        await ctx.reply(res['data'][0]["url"])
                    except:
                        await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Couldn\'t find any results for **{}**.'.format(gif_name)))

    @commands.command(aliases=['searchimage'])
    @commands.guild_only()
    async def imagesearch(self, ctx, *, image_name):
        url = 'https://unsplash.com/search/photos/' + image_name
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as page:
                    soup = bs4(await page.text(), 'html.parser')
                    image_tags = soup.findAll('img')
                    if str(image_tags[2]['src']).find('https://trkn.us/pixel/imp/c='):
                        link = image_tags[2]['src']
                        async with session.get(link) as resp:
                            image = await resp.read()
                        with io.BytesIO(image) as file:
                            await ctx.reply(file=discord.File(file, '{}.png'.format(ctx.message.id)))
                    else:
                        await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Couldn\'t find any results for **{}**.'.format(image_name)))

    @commands.command(aliases=['fliptext'])
    @commands.guild_only()
    async def textflip(self, ctx, *, text):
        result = ""
        for char in text:
            if char in text_flip:
                result += text_flip[char]
            else:
                result += char
        await ctx.reply(result[::-1])

    @commands.command()
    @commands.guild_only()
    async def spacetext(self, ctx, *, text):
        result = ''
        for char in text:
            result += char + '  '
        await ctx.reply(result)

    @commands.command(pass_context=True)
    @commands.guild_only()
    async def bigtext(self, ctx, *, text):
        msg = list(text)
        regional_list = [regionals[x.lower()] if x.isalnum() or x in [
            "!", "?"] else x for x in msg]
        regional_output = ' '.join(regional_list)
        await ctx.reply(regional_output)

    @commands.command()
    @commands.guild_only()
    async def iq(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        embed = discord.Embed(description='**{}** IQ.'.format(randint(12, 200)), color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else member.color if not self.bot.DEFAULT_COLOR else None)
        embed.set_author(
            name=member, icon_url=member.avatar_url, url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 32, commands.BucketType.guild)
    @commands.guild_only()
    async def hack(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        async with ctx.typing():
            msg = await ctx.reply('⌛ Hacking started for user **{}**.'.format(member.name))
            await asyncio.sleep(2)
            await msg.edit(content='⏳ Getting user\'s email...')
            await asyncio.sleep(2)
            await msg.edit(content='⌛ Fetching login (token found)...')
            await asyncio.sleep(2)
            await msg.edit(content='⏳ Fetching user\'s DMs...')
            await asyncio.sleep(2)
            await msg.edit(content='⌛ Tracing user\'s IP from messages...')
            await asyncio.sleep(2)
            await msg.edit(content='⏳ Last DM: `stop pinging`')
            await asyncio.sleep(2)
            await msg.edit(content='⌛ Finding most used feature in discord...')
            await asyncio.sleep(2)
            await msg.edit(content='⏳ Most used feature: `Selfbots`')
            await asyncio.sleep(2)
            await msg.edit(content='⌛ Injecting threats `Trojan:Win32/Ymacco.AA53`, `Trojan:Win32/Wacatac.D5!ml` and `HackTool:Win32/Keygen`...')
            await asyncio.sleep(2)
            await msg.edit(content='⏳ Injected `Trojan:Win32/Wacatac.D5!ml`... (Status: `High`)')
            await asyncio.sleep(2)
            await msg.edit(content='⌛ Injected `Trojan:Win32/Ymacco.AA53`... (Status: `Severe`)')
            await asyncio.sleep(2)
            await msg.edit(content='⏳ Injected `HackTool:Win32/KeyGen`... (Status: `Very High`)')
            await asyncio.sleep(2)
            await msg.edit(content='⌛ Found AppData information... Nitro Stolen...')
            await asyncio.sleep(2)
            await msg.edit(content='⏳ Selling data to goverment')
            await asyncio.sleep(2)
            await msg.edit(content='⌛ Getting house info with discriminator of #{}'.format(member.discriminator))
            await asyncio.sleep(2)
            await msg.edit(content='⌛ Email: **{}h@gmail.com**\nPassword: **\\*\\*\\*\\*\\*\\*\\***'.format(member.name))
            await asyncio.sleep(1)
            await msg.edit(content='{} User has been hacked! Login info saved in DMs.'.format(emojis.SIP))

    @commands.command()
    @commands.guild_only()
    async def clap(self, ctx, *, text):
        await ctx.reply(' 👏 '.join(text.split(' ')))

    @commands.command(name='1337', aliases=['leetspeak', '1337speak'])
    @commands.guild_only()
    async def _1337(self, ctx, *, text):
        text = text.replace('a', '4').replace('A', '4').replace('e', '3') \
            .replace('E', '3').replace('i', '!').replace('I', '!') \
            .replace('o', '0').replace('O', '0')
        await ctx.reply(text)

    @commands.command(aliases=['getip'])
    @commands.guild_only()
    async def findip(self, ctx, *, member: discord.Member = None):
        member = ctx.author if not member else member
        nums = '1234567890'
        embed = discord.Embed(description=f'IP: **18' + choice(nums)+f'.{randint(2, 7)}'+''.join(choice(nums) for i in range(randint(1, 2)))+'.'+''.join(choice(nums) for i in range(randint(2, 3)))+'.'+''.join(choice(nums) for i in range(3))+'**', color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else member.color if not self.bot.DEFAULT_COLOR else None)
        embed.set_author(
            name=member, icon_url=member.avatar_url, url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=['coinflip', 'flipcoin'])
    @commands.guild_only()
    async def flip(self, ctx):
        v = ['Heads', 'Tails', 'Coin was lost... Try again.']
        await ctx.reply(choice(v))

    @commands.command()
    @commands.guild_only()
    async def joke(self, ctx):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.random_api + 'joke') as r:
                    r = await r.json()
                    await ctx.reply(r['joke'])

    @commands.command()
    @commands.guild_only()
    async def token(self, ctx):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.random_api + 'bottoken') as r:
                    r = await r.json()
                    await ctx.reply(r['token'])

    @commands.command()
    @commands.guild_only()
    async def greyscale(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', f'{self.random_api}canvas/greyscale?avatar={avatar}'))

    @commands.command()
    @commands.guild_only()
    async def invert(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', f'{self.random_api}canvas/invert?avatar={avatar}'))

    @commands.command()
    @commands.guild_only()
    async def invertgreyscale(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', f'{self.random_api}canvas/invertgreyscale?avatar={avatar}'))

    @commands.command()
    @commands.guild_only()
    async def brightness(self, ctx, brightness: int, member: discord.Member = None):
        if brightness not in range(0, 101):
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Brightness can\'t be larger than 100.'))
        member = ctx.author if not member else member
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', f'{self.random_api}canvas/brightness?avatar={avatar}&brightness={brightness}'))

    @commands.command()
    @commands.guild_only()
    async def threshold(self, ctx, threshold: int, member: discord.Member = None):
        if threshold not in range(0, 256):
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Threshold can\'t be larger than 255.'))
        member = ctx.author if not member else member
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', f'{self.random_api}canvas/threshold?avatar={avatar}&threshold={threshold}'))

    @commands.command()
    @commands.guild_only()
    async def sepia(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', f'{self.random_api}canvas/sepia?avatar={avatar}'))

    @commands.command()
    @commands.guild_only()
    async def red(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', f'{self.random_api}canvas/red?avatar={avatar}'))

    @commands.command()
    @commands.guild_only()
    async def green(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', f'{self.random_api}canvas/green?avatar={avatar}'))

    @commands.command()
    @commands.guild_only()
    async def blue(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', f'{self.random_api}canvas/blue?avatar={avatar}'))

    @commands.command()
    @commands.guild_only()
    async def blurple(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', f'{self.random_api}canvas/blurple?avatar={avatar}'))

    @commands.command()
    @commands.guild_only()
    async def blurple2(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', f'{self.random_api}canvas/blurple2?avatar={avatar}'))

    @commands.command()
    @commands.guild_only()
    async def color(self, ctx, _hex, member: discord.Member = None):
        member = ctx.author if not member else member
        _hex = _hex.replace('0x', '').replace('#', '')
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', f'{self.random_api}canvas/color?avatar={avatar}&color={_hex}'))

    @commands.command()
    @commands.guild_only()
    async def trash(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get('https://nekobot.xyz/api/imagegen?type=trash&url={}'.format(avatar)) as r:
                    res = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', res['message']))

    @commands.command()
    @commands.guild_only()
    async def fact(self, ctx, *, text):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get('https://nekobot.xyz/api/imagegen?type=fact&text={}'.format(text)) as r:
                    res = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', res['message']))

    @commands.command(aliases=['magikify'])
    @commands.guild_only()
    async def magik(self, ctx, intensity: int, member: discord.Member = None):
        if intensity not in range(0, 11):
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Intensity can\'t be larger than 10.'))
        member = ctx.author if not member else member
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get('https://nekobot.xyz/api/imagegen?type=magik&image={}&intensity={}'.format(avatar, intensity)) as r:
                    res = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', res['message']))

    @commands.command()
    @commands.guild_only()
    async def phcomment(self, ctx, *, message):
        avatar = ctx.author.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get('https://nekobot.xyz/api/imagegen?type=phcomment&username={}&image={}&text={}'.format(ctx.author.name, avatar, message)) as r:
                    res = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, '{} commented!'.format(ctx.author.name), res['message']))

    @commands.command()
    @commands.guild_only()
    async def blurpify(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get('https://nekobot.xyz/api/imagegen?type=blurpify&image={}'.format(avatar)) as r:
                    res = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, '‎ ', res['message']))

    @commands.command()
    @commands.guild_only()
    async def deepfry(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get('https://nekobot.xyz/api/imagegen?type=deepfry&image={}'.format(avatar)) as r:
                    res = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', res['message']))

    @commands.command(aliases=['trumptwitter'])
    @commands.guild_only()
    async def trumptweet(self, ctx, *, message):
        avatar = ctx.author.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get('https://nekobot.xyz/api/imagegen?type=trumptweet&text={}'.format(message)) as r:
                    res = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, 'The 100% real 🎺 tweeted!', res['message']))

    @commands.command()
    @commands.guild_only()
    async def trap(self, ctx, member: discord.Member):
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get('https://nekobot.xyz/api/imagegen?type=trap&name={}&author={}&image={}'.format(member.name, ctx.author.name, avatar)) as r:
                    res = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', res['message']))

    @commands.command()
    @commands.guild_only()
    async def awooify(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get('https://nekobot.xyz/api/imagegen?type=awooify&url={}'.format(avatar)) as r:
                    res = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', res['message']))

    @commands.command()
    @commands.guild_only()
    async def iphonex(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        avatar = ctx.author.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get('https://nekobot.xyz/api/imagegen?type=iphonex&url={}'.format(avatar)) as r:
                    res = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', res['message']))

    @commands.command()
    @commands.guild_only()
    async def kannafy(self, ctx, *, text):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get('https://nekobot.xyz/api/imagegen?type=kannagen&text={}'.format(text)) as r:
                    res = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', res['message']))

    @commands.command(aliases=['jpeg'])
    @commands.guild_only()
    async def android(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get('https://nekobot.xyz/api/imagegen?type=jpeg&url={}'.format(avatar)) as r:
                    res = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', res['message']))

    @commands.command(aliases=['dokidoki'])
    @commands.guild_only()
    async def ddlc(self, ctx, character, captioned_text, background="class", body="1", face="a"):
        characters = ["yuri", "monika", "sayori",
                      "natsuki", "y", "m", "s", "n"]
        character = character.lower()
        if character not in characters:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, "Not a valid character. Please only use {}.".format(", ".join("**%s**" % x for x in characters))))
        background = background.lower()
        backgrounds = ["bedroom", "class", "closet", "club", "corridor",
                       "house", "kitchen", "residential", "sayori_bedroom"]
        if background not in backgrounds:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, "Not a valid background. Please only use {}.".format(", ".join("**%s**" % x for x in backgrounds))))
        if len(character) == 1:
            character = ddlc_get_character.get(character)
        if not body in ddlc_items.get("body").get(character):
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, "Not a valid body for {}. Please only use {}.".format(character.title(), ", ".join("**%s**" % x for x in ddlc_items.get("body").get(character)))))
        if not face in ddlc_items.get("face").get(character):
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, "Not a valid face for {}. Please only use {}.".format(character.title(), ", ".join("**%s**" % x for x in ddlc_items.get("face").get(character)))))
        async with ctx.typing():
            async with aiohttp.ClientSession() as cs:
                async with cs.get("https://nekobot.xyz/api/imagegen?type=ddlc"
                                  "&character=%s"
                                  "&background=%s"
                                  "&body=%s"
                                  "&face=%s"
                                  "&text=%s" % (character, background, body, face, captioned_text)) as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', r['message']))

    @commands.command()
    @commands.guild_only()
    async def changemymind(self, ctx, *, text):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get('https://nekobot.xyz/api/imagegen?type=changemymind&text={}'.format(text)) as r:
                    res = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', res['message']))

    @commands.command()
    @commands.guild_only()
    async def whowouldwin(self, ctx, user1: discord.Member, user2: discord.Member):
        avatar1 = user1.avatar_url_as(format='jpg', size=256)
        avatar2 = user2.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get('https://nekobot.xyz/api/imagegen?type=whowouldwin&user1={}&user2={}'.format(avatar1, avatar2)) as r:
                    res = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', res['message']))

    @commands.command()
    @commands.guild_only()
    async def captcha(self, ctx, member: discord.Member, *, text):
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get('https://nekobot.xyz/api/imagegen?type=captcha&url={}&username={}'.format(avatar, text)) as r:
                    res = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', res['message']))

    @commands.command()
    @commands.guild_only()
    async def ship(self, ctx, user1: discord.Member, user2: discord.Member):
        avatar1 = user1.avatar_url_as(format='jpg', size=256)
        avatar2 = user2.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get('https://nekobot.xyz/api/imagegen?type=ship&user1={}&user2={}'.format(avatar1, avatar2)) as r:
                    res = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', res['message']))

    @commands.command()
    @commands.guild_only()
    async def clyde(self, ctx, *, text):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get('https://nekobot.xyz/api/imagegen?type=clyde&text={}'.format(text)) as r:
                    res = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', res['message']))

    @commands.command()
    @commands.guild_only()
    async def baguette(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get('https://nekobot.xyz/api/imagegen?type=baguette&url={}'.format(avatar)) as r:
                    res = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', res['message']))

    @commands.command()
    @commands.guild_only()
    async def threats(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get('https://nekobot.xyz/api/imagegen?type=threats&url={}'.format(avatar)) as r:
                    res = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', res['message']))

    @commands.command()
    @commands.guild_only()
    async def roll(self, ctx, number: int = 100):
        await ctx.reply('Rolled **{}** points!'.format(randint(0, number)))

    @commands.command()
    @commands.guild_only()
    async def triggered(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        avatar = member.avatar_url_as(format='jpg', size=256)
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        'https://some-random-api.ml/canvas/triggered?avatar={}'.format(avatar)) as request:
                    imgbytes = io.BytesIO(await request.read())
                    await ctx.reply(file=discord.File(imgbytes, 'triggered.gif'))


def setup(bot):
    bot.add_cog(Fun(bot))
