import random
from discord.ext import commands

class Math(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def randnum(self, ctx, min : int, max : int):
        await ctx.reply(random.randint(min, max))

    @commands.command()
    @commands.guild_only()
    async def multiply(self, ctx, a: int, b:int):
        await ctx.reply(a*b)
        
    @commands.command()
    @commands.guild_only()
    async def divide(self, ctx, a: int, b:int):
        await ctx.reply(a//b)
        
    @commands.command()
    @commands.guild_only()
    async def add(self, ctx, a: int, b:int):
        await ctx.reply(a+b)
        
    @commands.command()
    @commands.guild_only()
    async def subtract(self, ctx, a: int, b:int):
        await ctx.reply(a-b)
        

def setup(bot):
    bot.add_cog(Math(bot))