from discord.ext import commands
import aiohttp
from random import choice
from __bot.embeds import Embeds as embeds


class Images(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.evergene_api = 'https://evergene.io/api/'
        self.random_animal_api = 'https://some-random-api.ml/animal/'
        self.neko_image_api = 'https://nekobot.xyz/api/image?type='

    @commands.command()
    @commands.guild_only()
    async def awwnime(self, ctx):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.evergene_api + 'awwnime') as request:
                    response = await request.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', response['url']))

    @commands.command()
    @commands.guild_only()
    async def animegif(self, ctx):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.evergene_api + 'animegif') as request:
                    response = await request.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', response['url']))

    @commands.command()
    @commands.guild_only()
    async def animewp(self, ctx):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.evergene_api + 'animewp') as request:
                    response = await request.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', response['url']))

    @commands.command()
    @commands.guild_only()
    async def moe(self, ctx):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.evergene_api + 'moe') as request:
                    response = await request.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', response['url']))

    @commands.command()
    @commands.guild_only()
    async def aww(self, ctx):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.evergene_api + 'aww') as request:
                    response = await request.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', response['url']))

    @commands.command()
    @commands.guild_only()
    async def floof(self, ctx):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.evergene_api + 'floof') as request:
                    response = await request.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', response['url']))

    @commands.command()
    @commands.guild_only()
    async def cat(self, ctx):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.random_animal_api + 'cat') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, r['fact'], r['image']))

    @commands.command()
    @commands.guild_only()
    async def dog(self, ctx):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.random_animal_api + 'dog') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, r['fact'], r['image']))

    @commands.command()
    @commands.guild_only()
    async def koala(self, ctx):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.random_animal_api + 'koala') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, r['fact'], r['image']))

    @commands.command(aliases=['birb'])
    @commands.guild_only()
    async def bird(self, ctx):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.random_animal_api + 'birb') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, r['fact'], r['image']))

    @commands.command()
    @commands.guild_only()
    async def panda(self, ctx):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.random_animal_api + 'panda') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, r['fact'], r['image']))

    @commands.command()
    @commands.guild_only()
    async def redpanda(self, ctx):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.random_animal_api + 'red_panda') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, r['fact'], r['image']))

    @commands.command()
    @commands.guild_only()
    async def raccoon(self, ctx):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.random_animal_api + 'raccoon') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, r['fact'], r['image']))

    @commands.command()
    @commands.guild_only()
    async def fox(self, ctx):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.random_animal_api + 'fox') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, r['fact'], r['image']))

    @commands.command()
    @commands.guild_only()
    async def kangaroo(self, ctx):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.random_animal_api + 'kangaroo') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, r['fact'], r['image']))

    @commands.command()
    @commands.guild_only()
    async def neko(self, ctx):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.neko_image_api + 'neko') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', r['message']))

    @commands.command()
    @commands.guild_only()
    async def hneko(self, ctx):
        if not ctx.channel.nsfw:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This channel is not NSFW.'))
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.neko_image_api + 'hneko') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', r['message']))

    @commands.command()
    @commands.guild_only()
    async def hass(self, ctx):
        if not ctx.channel.nsfw:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This channel is not NSFW.'))
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.neko_image_api + 'hass') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', r['message']))

    @commands.command()
    @commands.guild_only()
    async def hmidriff(self, ctx):
        if not ctx.channel.nsfw:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This channel is not NSFW.'))
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.neko_image_api + 'hmidriff') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', r['message']))

    @commands.command()
    @commands.guild_only()
    async def pgif(self, ctx):
        if not ctx.channel.nsfw:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This channel is not NSFW.'))
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.neko_image_api + 'pgif') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', r['message']))

    @commands.command(name='4k')
    @commands.guild_only()
    async def _4k(self, ctx):
        if not ctx.channel.nsfw:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This channel is not NSFW.'))
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.neko_image_api + '4k') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', r['message']))

    @commands.command()
    @commands.guild_only()
    async def hentai(self, ctx):
        if not ctx.channel.nsfw:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This channel is not NSFW.'))
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.neko_image_api + 'hentai') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', r['message']))

    @commands.command()
    @commands.guild_only()
    async def holo(self, ctx):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.neko_image_api + 'holo') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', r['message']))

    @commands.command()
    @commands.guild_only()
    async def hkitsune(self, ctx):
        if not ctx.channel.nsfw:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This channel is not NSFW.'))
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.neko_image_api + 'hkitsune') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', r['message']))

    @commands.command()
    @commands.guild_only()
    async def kemonomimi(self, ctx):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.neko_image_api + 'kemonomimi') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', r['message']))

    @commands.command()
    @commands.guild_only()
    async def anal(self, ctx):
        if not ctx.channel.nsfw:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This channel is not NSFW.'))
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.neko_image_api + 'anal') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', r['message']))

    @commands.command()
    @commands.guild_only()
    async def hanal(self, ctx):
        if not ctx.channel.nsfw:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This channel is not NSFW.'))
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.neko_image_api + 'hanal') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', r['message']))

    @commands.command()
    @commands.guild_only()
    async def gonewild(self, ctx):
        if not ctx.channel.nsfw:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This channel is not NSFW.'))
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.neko_image_api + 'gonewild') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', r['message']))

    @commands.command()
    @commands.guild_only()
    async def kanna(self, ctx):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.neko_image_api + 'kanna') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', r['message']))

    @commands.command()
    @commands.guild_only()
    async def ass(self, ctx):
        if not ctx.channel.nsfw:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This channel is not NSFW.'))
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.neko_image_api + 'ass') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', r['message']))

    @commands.command()
    @commands.guild_only()
    async def pussy(self, ctx):
        if not ctx.channel.nsfw:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This channel is not NSFW.'))
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.neko_image_api + 'pussy') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', r['message']))

    @commands.command()
    @commands.guild_only()
    async def thigh(self, ctx):
        if not ctx.channel.nsfw:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This channel is not NSFW.'))
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.neko_image_api + 'thigh') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', r['message']))

    @commands.command()
    @commands.guild_only()
    async def hthigh(self, ctx):
        if not ctx.channel.nsfw:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This channel is not NSFW.'))
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.neko_image_api + 'hthigh') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', r['message']))

    @commands.command()
    @commands.guild_only()
    async def gah(self, ctx):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.neko_image_api + 'gah') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', r['message']))

    @commands.command()
    @commands.guild_only()
    async def coffee(self, ctx):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.neko_image_api + 'coffee') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', r['message']))

    @commands.command()
    @commands.guild_only()
    async def food(self, ctx):
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.neko_image_api + 'food') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', r['message']))

    @commands.command()
    @commands.guild_only()
    async def paizuri(self, ctx):
        if not ctx.channel.nsfw:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This channel is not NSFW.'))
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.neko_image_api + 'paizuri') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', r['message']))

    @commands.command()
    @commands.guild_only()
    async def tentacle(self, ctx):
        if not ctx.channel.nsfw:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This channel is not NSFW.'))
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.neko_image_api + 'tentacle') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', r['message']))

    @commands.command(aliases=['booba'])
    @commands.guild_only()
    async def boobs(self, ctx):
        if not ctx.channel.nsfw:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This channel is not NSFW.'))
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.neko_image_api + 'boobs') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', r['message']))

    @commands.command(aliases=['hbooba'])
    @commands.guild_only()
    async def hboobs(self, ctx):
        if not ctx.channel.nsfw:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This channel is not NSFW.'))
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.neko_image_api + 'hboobs') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', r['message']))

    @commands.command()
    @commands.guild_only()
    async def yaoi(self, ctx):
        if not ctx.channel.nsfw:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This channel is not NSFW.'))
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.neko_image_api + 'yaoi') as r:
                    r = await r.json()
                    await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', r['message']))

    @commands.command()
    @commands.guild_only()
    async def yandere(self, ctx, *, tag):
        if not ctx.channel.nsfw:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This channel is not NSFW.'))
        query = ("https://yande.re/post.json?limit=100&tags=" + tag)
        async with ctx.typing():
            async with aiohttp.ClientSession() as cs:
                async with cs.get(query) as res:
                    res = await res.json()
            if res != []:
                img = choice(res)
                if "loli" in img["tags"] or "shota" in img["tags"]:
                    return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Loli or shota was found in this post.'))
                await ctx.send(embed=embeds.TitleImage._text_to_embed(self.bot, ctx, ' ', img['jpeg_url']))
            else:
                await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No results for **{}** were found.'.format(tag)))


def setup(bot):
    bot.add_cog(Images(bot))
