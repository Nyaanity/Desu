import discord
from discord.ext import commands
from __bot.emojis import Emojis as emojis


class Guild(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['users'])
    @commands.guild_only()
    async def members(self, ctx):
        embed = discord.Embed(
            color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
            None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None, timestamp=ctx.message.created_at)
        embed.add_field(name='Total [{}]'.format(len([member for member in ctx.guild.members])),
                        value='{} members, {} bots'.format(len([member for member in ctx.guild.members if not member.bot]), len([member for member in ctx.guild.members if member.bot])))
        embed.add_field(name='Members Online', value='{} {}'.format(emojis.ONLINE, len(
            [member for member in ctx.guild.members if str(member.status) == 'online'])))
        embed.add_field(name='Members Idle', value='{} {}'.format(emojis.IDLE, len(
            [member for member in ctx.guild.members if str(member.status) == 'idle'])))
        embed.add_field(name='Members Dnd', value='{} {}'.format(emojis.DND, len(
            [member for member in ctx.guild.members if str(member.status) == 'dnd'])))
        embed.add_field(name='Members Offline', value='{} {}'.format(emojis.OFFLINE, len(
            [member for member in ctx.guild.members if str(member.status) == 'offline'])))
        await ctx.send(embed=embed)

    @commands.command(aliases=['guildinfo'])
    @commands.guild_only()
    async def serverinfo(self, ctx):
        voices, texts = len([channel for channel in ctx.guild.voice_channels]), len(
            [channel for channel in ctx.guild.text_channels])
        embed = discord.Embed(
            color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
            None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None, timestamp=ctx.message.created_at)
        embed.add_field(name='Members [{}]'.format(len([member for member in ctx.guild.members])),
                        value='{} members, {} bots'.format(len([member for member in ctx.guild.members if not member.bot]), len([member for member in ctx.guild.members if member.bot])))
        embed.add_field(name='Owner',
                        value=ctx.guild.owner)
        embed.add_field(name='Region',
                        value=str(ctx.guild.region).title())
        embed.add_field(name='Categories',
                        value=len([cat for cat in ctx.guild.categories]))
        embed.add_field(name='Channels [{}]'.format(voices + texts),
                        value='{} text, {} voice'.format(texts, voices))
        embed.add_field(name='Roles',
                        value=len([role for role in ctx.guild.roles]))
        embed.add_field(name='Created at', value=ctx.guild.created_at.strftime(
            '%a, %b %d, %Y %I:%M %p'))
        embed.set_footer(text='ID: {}'.format(ctx.guild.id))
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def channelinfo(self, ctx, channel: discord.TextChannel = None):
        channel = ctx.channel if not channel else channel
        embed = discord.Embed(
            color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
            None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None, timestamp=ctx.message.created_at)
        embed.add_field(name='Name',
                        value=channel.name)
        embed.add_field(name='Category',
                        value=channel.category if channel.category else 'N/A')
        embed.add_field(name='Created at', value=channel.created_at.strftime(
            '%a, %b %d, %Y %I:%M %p'))
        embed.add_field(name='Position',
                        value=channel.position)
        embed.add_field(name='Slowmode',
                        value=channel.slowmode_delay)
        embed.add_field(name='Members with Access',
                        value=len(channel.members))
        embed.add_field(name='Topic',
                        value=channel.topic if channel.topic else 'N/A')
        embed.add_field(name='NSFW',
                        value='Yes' if channel.nsfw else 'No')
        embed.set_footer(text='ID: {}'.format(ctx.guild.id))
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Guild(bot))
