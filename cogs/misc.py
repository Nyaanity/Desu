import discord
from discord.ext import commands
from random import choice, sample
import aiohttp
import asyncio
import hashlib
from datetime import datetime, timezone, timedelta
import string
import os
import base64
from __bot.embeds import Embeds as embeds
from __bot.ascii import Ascii as _ascii
from __bot.captcha import Captcha as captcha


class Miscellaneous(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.random_api = 'https://some-random-api.ml/'

    @commands.command()
    @commands.guild_only()
    async def genpass(self, ctx, length=16):
        try:
            lenght = int(length)
        except:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Please enter an integer.'))
        if lenght > 62:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Please enter a value below 62.'))
        elif lenght == 0:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Please enter a value above 0.'))
        lower = string.ascii_lowercase
        upper_char = string.ascii_uppercase
        digits = string.digits
        symbols = string.punctuation
        all = lower + upper_char + digits
        temp = sample(all, lenght)
        password = "".join(temp)
        embed = discord.Embed(description='Your randomly generated password is: **{}**'.format(password), color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None)
        embed.set_author(
            name=ctx.author, icon_url=ctx.author.avatar_url, url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=['emb'])
    @commands.guild_only()
    async def embed(self, ctx, *, text):
        embed = discord.Embed(description='{}'.format(text), color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None, timestamp=ctx.message.created_at)
        embed.set_author(
            name=ctx.author, icon_url=ctx.author.avatar_url, url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=['emojis'])
    @commands.guild_only()
    async def emotes(self, ctx):
        animated = [str(x) for x in ctx.guild.emojis if '.gif' in str(x.url)]
        default = [str(x)
                   for x in ctx.guild.emojis if not '.gif' in str(x.url)]
        if int(len(default) + len(animated)) == 0:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This server doesn\'t have any emotes.'))
        embed = discord.Embed(description=' '.join([str(x) for x in ctx.guild.emojis]), color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None)
        embed.set_author(
            name='{} emotes, {} animated, {} total'.format(len(default), len(animated), len(default) + len(animated)))
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def say(self, ctx, *, message):
        if len(message) > 1800:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Please keep the message smaller than 1800 characters.'))
        await ctx.send('{}\n\n\t\t\t~ **{}**'.format(str(message), ctx.author.name))

    @commands.command()
    @commands.guild_only()
    async def nyanify(self, ctx, *, message):
        if len(message) > 1800:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Please keep the message smaller than 1800 characters.'))
        await ctx.send(message.replace('r', 'w').replace('l', 'w') + ' ' + choice(['UwU', 'OwO', '>_<', 'ÙwÚ', 'ÒwÓ', 'uwu', 'owo', 'ùwú', 'òwó']))

    @commands.command(aliases=['emoji', 'emote'])
    @commands.guild_only()
    async def steal(self, ctx, emoji: discord.Emoji):
        await ctx.reply(str(emoji.url))

    @commands.command()
    @commands.guild_only()
    async def ping(self, ctx, domain_addr=None):
        async with ctx.typing():
            if domain_addr:
                domain_addr = str(
                    'https://' + domain_addr) if not 'http' in domain_addr else domain_addr
                msg = await ctx.send(embed=embeds.Loading._text_to_embed(self.bot, ctx, 'Awaiting response from **{}**...'.format(domain_addr)))
                try:
                    async with aiohttp.ClientSession() as session:
                        start = datetime.now(tz=timezone.utc).timestamp()
                        async with session.get(domain_addr, timeout=7):
                            end = datetime.now(tz=timezone.utc).timestamp()
                            return await msg.edit(embed=embeds.Success._text_to_embed(self.bot, ctx, '**{}** took **{}ms** to respond'.format(domain_addr, round((end-start)*100, 3))))
                except asyncio.TimeoutError:
                    return await msg.edit(embed=embeds.Error._text_to_embed(self.bot, ctx, '**{}** failed to respond.'.format(domain_addr)))
                except:
                    return await msg.edit(embed=embeds.Error._text_to_embed(self.bot, ctx, '**{}** is not a valid address.'.format(domain_addr)))
            async with aiohttp.ClientSession() as session:
                start = datetime.now(tz=timezone.utc).timestamp()
                async with session.get('https://1.1.1.1', timeout=7):
                    end = datetime.now(tz=timezone.utc).timestamp()
            embed = discord.Embed(description='Discord API bot latency: **{}ms**\nBot latency: **{}ms**'.format(
                round(self.bot.latency * 1000), round((end-start)*100)), color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None)
            embed.set_author(name='Ping')
            await ctx.send(embed=embed)

    @commands.command(aliases=['pfp', 'avatar'])
    @commands.guild_only()
    async def av(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        embed = discord.Embed(color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None, timestamp=ctx.message.created_at)
        embed.set_author(name='Avatar of {}'.format(
            member), url=member.avatar_url)
        embed.set_image(url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def userinfo(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        punishments = self.bot._db._search_by_user_id(self.bot.db,
                                                      'moderation', ctx.guild.id, member.id)
        perms = [x for x in member.guild_permissions]
        _perm_keys = ['Administrator', 'Manage Server', 'Manage Roles', 'Manage Channels',
                      'Manage Messages', 'Manage Webhooks', 'Manage Nicknames',
                      'Manage Emojis', 'Kick Members', 'Ban Members', 'Mention Everyone']
        perms = ', '.join(str(x[0]).replace('_', ' ').title() for x in perms if x[1] == True and str(
            x[0]).replace('_', ' ').title() in _perm_keys) if len(perms) != 0 else 'N/A'
        roles = [x for x in member.roles if not '@everyone' in x.name]
        embed = discord.Embed(description=member.mention,
                              color=ctx.author.color, timestamp=ctx.message.created_at)
        embed.set_author(name=member, url=member.avatar_url,
                         icon_url=member.avatar_url)
        embed.add_field(name='Joined Server at', value=datetime.fromtimestamp(member.joined_at.timestamp(), tz=timezone.utc).strftime(
            '%a, %b %d, %Y %I:%M %p'))
        embed.add_field(name='Joined Discord at', value=datetime.fromtimestamp(member.created_at.timestamp(), tz=timezone.utc).strftime(
            '%a, %b %d, %Y %I:%M %p'))
        embed.add_field(name='Roles [{}]'.format(len(roles)),
                        value=' '.join(x.mention for x in member.roles if not '@everyone' in x.name) if len(roles) != 0 else 'N/A', inline=False)
        embed.add_field(name='Permissions',
                        value=perms if perms else 'N/A', inline=False)
        embed.add_field(name='Server Punishments',
                        value=str(len(punishments)) + ' total')
        embed.set_footer(text='ID: {}'.format(member.id))
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def createdat(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        duration = datetime.now(
            tz=timezone.utc) - datetime.fromtimestamp(member.created_at.timestamp(), tz=timezone.utc)
        hours, remainder = divmod(int(duration.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        months, remainder = divmod(int(duration.total_seconds()), 2629746)
        years, months = divmod(months, 12)
        embed = discord.Embed(description='Account was created **{}** days ago, which was at **{}**, **{}** years and **{}** months ago.'.format(
            days, datetime.fromtimestamp(member.created_at.timestamp(), tz=timezone.utc).strftime(
                '%a, %b %d, %Y %I:%M %p'), years, months), color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
            None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None)
        embed.set_author(
            name=member, icon_url=member.avatar_url, url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def joinedat(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        duration = datetime.now(
            tz=timezone.utc) - datetime.fromtimestamp(member.joined_at.timestamp(), tz=timezone.utc)
        hours, remainder = divmod(int(duration.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        months, remainder = divmod(int(duration.total_seconds()), 2629746)
        years, months = divmod(months, 12)
        embed = discord.Embed(description='Joined **{}** days ago, which was at **{}**, **{}** years and **{}** months ago.'.format(
            days, datetime.fromtimestamp(member.joined_at.timestamp(), tz=timezone.utc).strftime(
                '%a, %b %d, %Y %I:%M %p'), years, months), color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
            None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None)
        embed.set_author(
            name=member, icon_url=member.avatar_url, url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_guild_permissions(add_reactions=True)
    async def react(self, ctx, emoji: discord.Emoji, message: discord.Message = None):
        message = ctx.message if not message else message
        if not message.channel == ctx.channel:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Please use a message that\'s inside this channel.'))
        await message.add_reaction(emoji)
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Added reaction {} to **{}**'.format(emoji, message.jump_url)))

    @commands.command()
    @commands.guild_only()
    async def ascii(self, ctx, *, text):
        return await ctx.reply('```' + _ascii.str_to_ascii(text) + '```')

    @commands.command()
    @commands.guild_only()
    async def emojify(self, ctx, *, text):
        await ctx.reply(text.lower().replace('a', ' *🇦* ').replace('b', ' *🇧* ').replace('c', ' *🇨* ').replace('d', ' *🇩* ').replace('e', '*🇪* ').replace('f', '*🇫* ').replace('g', ' *🇬* ')
                        .replace('h', ' *🇭* ').replace('i', ' *🇮* ').replace('j', ' *🇯* ').replace('k', ' *🇰* ').replace('l', ' *🇱* ').replace('m', '*🇲* ').replace('n', ' *🇳* ')
                        .replace('o', ' *🇴* ').replace('p', ' *🇵* ').replace('q', ' *🇶* ').replace('r', ' *🇷* ').replace('s', ' *🇸* ').replace('t', '*🇹* ').replace('u', ' *🇺* ')
                        .replace('v', ' *🇻* ').replace('w', ' *🇼* ').replace('x', ' *🇽* ').replace('y', ' *🇾* ').replace('z', ' *🇿* ').replace('1', ' *:one:* ').replace('2', ' *:two:* ')
                        .replace('3', ' *:three:* ').replace('4', ' *:four:* ').replace('5', ' *:five:* ').replace('6', ' *:six:* ').replace('7', ' *:seven:* ')
                        .replace('8', ' *:eight:* ').replace('9', ' *:nine:* ').replace('0', ' *:zero:* '))

    @commands.command()
    @commands.guild_only()
    async def invite(self, ctx):
        embed = discord.Embed(title='Invite {}!'.format(self.bot.user.name),
                              description='[All permissions](https://canary.discord.com/api/oauth2/authorize?client_id={}&permissions=8&scope=bot%20applications.commands)\n[Custom permissions](https://canary.discord.com/api/oauth2/authorize?client_id={}&permissions=4294967287&scope=bot%20applications.commands)'.format(
                                  self.bot.user.id, self.bot.user.id),
                              color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def uptime(self, ctx):
        await ctx.reply('Online since **{}**.'.format(self.bot.up_since))

    @commands.command(name='replace')
    @commands.guild_only()
    async def _replace(self, ctx, *, text):
        prefix = self.bot.config._get_prefix(self.bot, ctx)
        try:
            text = text.split(' | ')
            text[0], text[1], text[2]
        except:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Invalid text formatting. Please split the message with "** | **", like that: **{}replace i\'m hungry | hungry | thirsty**'.format(prefix)))
        return await ctx.send(text[0].replace(text[1], text[2]))

    @commands.command(name='hash')
    @commands.guild_only()
    async def _hash(self, ctx, hash_type, *, text):
        hash_types = ['md5', 'sha1', 'sha256', 'sha512']
        if not hash_type.lower() in hash_types:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This bot doesn\'t support this hash type. Please only use **md5**, **sha1**, **sha256** or **sha512**.'))
        if hash_type == 'md5':
            await ctx.reply(hashlib.md5(text.encode('utf-8')).hexdigest())
        elif hash_type == 'sha1':
            await ctx.reply(hashlib.sha1(text.encode('utf-8')).hexdigest())
        elif hash_type == 'sha256':
            await ctx.reply(hashlib.sha256(text.encode('utf-8')).hexdigest())
        elif hash_type == 'sha512':
            await ctx.reply(hashlib.sha512(text.encode('utf-8')).hexdigest())
        else:
            return

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_guild_permissions(send_tts_messages=True)
    # @commands.has_guild_permissions(send_tts_messages=True)
    async def tts(self, ctx, *, text):
        if len(text) > 1800:
            return await ctx.send(embed=embeds.Error._text_to_embed('Please keep the text smaller than 1800 characters.'))
        await ctx.send('{}\n\n\t\t\t~ **{}**'.format(str(text), ctx.author.name).replace("@", "**@**"), tts=True)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_guild_permissions(attach_files=True)
    async def gencaptcha(self, ctx, length=7):
        c = captcha(length).gen_captcha_img()
        await ctx.reply(file=discord.File(c['captcha_img_path']))
        await asyncio.sleep(0.5)
        os.remove(c['captcha_img_path'])

    @commands.command()
    @commands.guild_only()
    async def totalmessages(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        self.bot.db.execute(
            'SELECT * FROM totalmessages WHERE guild_id = "{}" AND user_id = "{}"'.format(ctx.guild.id, member.id))
        result = self.bot.db.fetchone()
        if not result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No records for that user were found.'))
        embed = discord.Embed(description='Sent **{}** total messages since their first recorded message that was sent at **{}**.'.format(result[3], datetime.fromtimestamp(int(float(result[4]))).strftime('%a, %b %d, %Y %I:%M %p')), color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else member.color if not self.bot.DEFAULT_COLOR else None)
        embed.set_author(
            name=member, icon_url=member.avatar_url, url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def voiceest(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        self.bot.db.execute(
            'SELECT * FROM voicetimerecorder WHERE guild_id = "{}" AND user_id = "{}"'.format(ctx.guild.id, member.id))
        result = self.bot.db.fetchone()
        if not result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No records for that user were found.'))
        embed = discord.Embed(description='Seen in voice chat for **{}** hours and **{}** minutes since their first recorded voice chat join that was at **{}**.'.format(str(timedelta(seconds=int(result[3]))).split(':')[0], str(timedelta(seconds=int(result[3]))).split(':')[1], datetime.fromtimestamp(int(float(result[4]))).strftime('%a, %b %d, %Y %I:%M %p')), color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else member.color if not self.bot.DEFAULT_COLOR else None)
        embed.set_author(
            name=member, icon_url=member.avatar_url, url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name='encode')
    @commands.guild_only()
    async def _encode(self, ctx, *, text):
        i = text.encode('ascii')
        b = base64.b64encode(i)
        b64 = b.decode('ascii')
        await ctx.reply(b64)

    @commands.command(name='decode')
    @commands.guild_only()
    async def _decode(self, ctx, *, text):
        i = text.encode('ascii')
        b = base64.b64decode(i)
        b64 = b.decode('ascii')
        await ctx.reply(b64)

    @commands.command()
    @commands.guild_only()
    async def lyrics(self, ctx, *, title):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.random_api + 'lyrics?title={}'.format(title)) as r:
                    r = await r.json()
                    try:
                        embed = discord.Embed(title=r['title'], description=r['lyrics'], color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None)
                        embed.set_author(name='by {}'.format(
                            r['author']), url=r['links']['genius'])
                        embed.set_thumbnail(url=r['thumbnail']['genius'])
                        await ctx.send(embed=embed)
                    except:
                        await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Couldn\'t find the lyrics for **{}**.'.format(title)))

    @commands.command()
    @commands.guild_only()
    async def nyanlyrics(self, ctx, *, title):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.random_api + 'lyrics?title={}&cancer=true'.format(title)) as r:
                    r = await r.json()
                    try:
                        embed = discord.Embed(title=r['title'], description=r['lyrics'], color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None)
                        embed.set_author(name='by {}'.format(
                            r['author']), url=r['links']['genius'])
                        embed.set_thumbnail(url=r['thumbnail']['genius'])
                        await ctx.send(embed=embed)
                    except:
                        await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Couldn\'t find the lyrics for **{}**.'.format(title)))

    @commands.command(aliases=['mc'])
    @commands.guild_only()
    async def minecraft(self, ctx, *, username):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.random_api + 'mc?username={}'.format(username)) as r:
                    r = await r.json()
                    try:
                        embed = discord.Embed(
                            color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                            None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None, timestamp=ctx.message.created_at)
                        embed.add_field(name='Username',
                                        value=r['username'])
                        embed.add_field(name='Name History',
                                        value='\n'.join(['{} ({})'.format(str(x['name']), str(y['changedToAt'] if not 'Original' in str(y['changedToAt']) else 'Account Created')) for x, y in zip(r['name_history'], r['name_history'])]))
                        embed.set_footer(text='UUID: {}'.format(r['uuid']))
                        await ctx.send(embed=embed)
                    except:
                        await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Couldn\'t find the user **{}**.'.format(username)))

    @commands.command()
    @commands.guild_only()
    async def viewcolor(self, ctx, _hex):
        color = str(_hex).replace('#', '').replace('0x', '')
        async with ctx.typing():
            await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, '0x' + color, 'https://some-random-api.ml/canvas/colorviewer?hex={}'.format(color)))

    @commands.command()
    @commands.guild_only()
    async def doujin(self, ctx):
        if not ctx.channel.nsfw:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This channel is not NSFW.'))
        async with ctx.typing():
            async with aiohttp.ClientSession() as cs:
                async with cs.get("http://nhentai.net/random/") as res:
                    res = res.url
        await ctx.reply(str(res))

    @commands.command()
    @commands.guild_only()
    async def botinfo(self, ctx):
        shard_count = len(self.bot.shards)
        cogs_count = len(self.bot.cogs)
        commands_count = len(self.bot.commands)
        embed = discord.Embed(color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None, timestamp=ctx.message.created_at)
        embed.set_author(name=self.bot.user, url=self.bot.user.avatar_url,
                         icon_url=self.bot.user.avatar_url)
        embed.add_field(name='Running since',
                        value=self.bot.up_since)
        embed.add_field(name='Servers',
                        value=len(self.bot.guilds))
        embed.add_field(name='Shards',
                        value=shard_count)
        embed.add_field(name='Cogs',
                        value=cogs_count)
        embed.add_field(name='Commands',
                        value=commands_count)
        embed.add_field(name='Members',
                        value=sum([len(guild.members) for guild in self.bot.guilds]))
        embed.add_field(name='Developer',
                        value=discord.utils.find(lambda m: m.id == self.bot.OWNER_ID, self.bot.get_all_members()))
        embed.add_field(name='Created at', value=datetime.fromtimestamp(self.bot.user.created_at.timestamp(), tz=timezone.utc).strftime(
            '%a, %b %d, %Y %I:%M %p'))
        embed.add_field(name='Written in',
                        value='Python')
        embed.set_footer(text='ID: {}'.format(self.bot.user.id))
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def whoplays(self, ctx, *, game_name):
        users = ['**{}**: {}'.format([str(timedelta(seconds=(ctx.message.created_at.timestamp()-activity.created_at.timestamp()))).split('.')[0] for activity in member.activities if str(
            game_name).lower() in str(activity).lower()][0], member.mention) for member in ctx.guild.members if str(game_name).lower() in str([str(activity).lower() for activity in member.activities])]
        if not users:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No users currently playing **{}** found.'.format(game_name)))
        embed = discord.Embed(description='\n'.join(
            x for x in users), color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
            None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None)
        embed.set_author(
            name='Total users playing {}: {}'.format(game_name, len(users)))
        await ctx.send(embed=embed)

    @commands.command(aliases=['firstmsg', 'oldestmsg', 'oldestmessage'])
    @commands.cooldown(1, 120, commands.BucketType.guild)
    @commands.guild_only()
    async def firstmessage(self, ctx, member_id: int = None):
        oldest_message = None
        member_id = ctx.author.id if not member_id else member_id
        async with ctx.typing():
            for channel in ctx.guild.text_channels:
                if not dict(channel.permissions_for(ctx.guild.me))['read_messages']:
                    continue
                msgs = await channel.history(limit=10**100).flatten()
                author_messages = [
                    msg for msg in msgs if msg.author.id == member_id]
                if author_messages:
                    if not oldest_message:
                        oldest_message = author_messages[-1]
                    elif oldest_message:
                        if author_messages[-1].created_at.timestamp() < oldest_message.created_at.timestamp():
                            oldest_message = author_messages[-1]
        if not oldest_message:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This member hasn\'t sent any messages yet.'))
        member = discord.utils.find(
            lambda m: m.id == member_id, ctx.guild.members)
        embed = discord.Embed(description='Sent their first still visible **[message]({})** on this server at **{}**, in {}.'.format(oldest_message.jump_url, oldest_message.created_at.strftime('%a, %b %d, %Y %I:%M %p'), oldest_message.channel.mention), color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else member.color if not self.bot.DEFAULT_COLOR else None)
        embed.set_author(
            name=member if member else 'N/A', icon_url=member.avatar_url if member else 'http://404.MemberNotFound.zzz', url=member.avatar_url if member else 'http://404.MemberNotFound.zzz')
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def utcnow(self, ctx):
        await ctx.reply(int(datetime.now(tz=timezone.utc).timestamp()))


def setup(bot):
    bot.add_cog(Miscellaneous(bot))
