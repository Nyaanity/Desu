from discord.ext import commands
import discord
from datetime import timezone, datetime
from __bot.embeds import Embeds as embeds
from __bot.time import TimeConverter as _time


class Autopurge(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.author_stash = []
        self.bot.db.execute('''CREATE TABLE IF NOT EXISTS autopurge(
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            enabled TEXT,
            channel_id TEXT,
            guild_id TEXT,
            frequency TEXT,
            next_purge_at TEXT,
                PRIMARY KEY (id))''')

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def autopurge(self, ctx):
        prefix = self.bot.config._get_prefix(self.bot, ctx)
        embed = discord.Embed(title='Autopurge',
                              description=f"**<>** = required\n**[]** = optional",
                              color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None,
                              timestamp=ctx.message.created_at)
        embed.add_field(
            name='Enable/disable autopurging', value='`{}autopurge toggle`'.format(prefix))
        embed.add_field(
            name='Set a channel to autopurge', value='`{}autopurge channel [channel]`'.format(prefix))
        embed.add_field(
            name='Set the purge frequency', value='`{}autopurge frequency <frequency>`'.format(prefix))
        embed.add_field(
            name='Delete the autopurge config', value='`{}autopurge delete`'.format(prefix))
        await ctx.send(embed=embed)

    @autopurge.command()
    @commands.guild_only()
    @commands.bot_has_guild_permissions(administrator=True)
    @commands.has_guild_permissions(administrator=True)
    async def toggle(self, ctx):
        self.bot.db.execute(
            'SELECT * FROM autopurge WHERE guild_id = "{}"'.format(ctx.guild.id))
        result = self.bot.db.fetchone()
        if not result:
            self.bot.db.execute('INSERT INTO autopurge(guild_id,enabled,channel_id,frequency,next_purge_at) VALUES("{}","{}","{}","{}","{}")'.format(
                ctx.guild.id, 1, 'N/A', 'N/A', 'N/A'))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Enabled** autopurging'))
        if str(result[1]) == '1':
            self.bot.db.execute('UPDATE autopurge SET enabled = "{}" WHERE guild_id = "{}"'.format(
                0, ctx.guild.id))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Disabled** autopurging'))
        self.bot.db.execute('UPDATE autopurge SET enabled = "{}" WHERE guild_id = "{}"'.format(
            1, ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Enabled** autopurge'))

    @autopurge.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def channel(self, ctx, channel: discord.TextChannel = None):
        channel = ctx.channel if not channel else channel
        self.bot.db.execute(
            'SELECT channel_id FROM autopurge WHERE guild_id = "{}"'.format(ctx.guild.id))
        autopurge_channel = self.bot.db.fetchone()
        if not autopurge_channel:
            self.bot.db.execute('INSERT INTO autopurge(guild_id,enabled,channel_id,frequency,next_purge_at) VALUES("{}","{}","{}","{}","{}")'.format(
                ctx.guild.id, 0, channel.id, 'N/A', 'N/A'))
        elif autopurge_channel:
            self.bot.db.execute('UPDATE autopurge SET channel_id = "{}" WHERE guild_id = "{}"'.format(
                channel.id, ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Set the autopurge channel to {}'.format(channel.mention)))

    @autopurge.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def frequency(self, ctx, frequency):
        if not frequency.isdigit():
            try:
                if int(_time._to_seconds(str(frequency))) < _time._to_seconds('10m'):
                    return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'To avoid ratelimits, the autopurge frequency has to be at least 10m.'))
            except ValueError:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Bad time given. Please enter the frequency like that: **60s**/**60m**/**24h**/**7d**/**4w**/**1y**'))
        else:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Bad time given. Please enter the frequency like that: **60s**/**60m**/**24h**/**7d**/**4w**/**1y**'))
        self.bot.db.execute(
            'SELECT * FROM autopurge WHERE guild_id = "{}"'.format(ctx.guild.id))
        autopurge = self.bot.db.fetchone()
        if not autopurge:
            self.bot.db.execute('INSERT INTO autopurge(guild_id,enabled,channel_id,frequency,next_purge_at) VALUES("{}","{}","{}","{}","{}")'.format(
                ctx.guild.id, 0, 'N/A', _time._to_seconds(str(frequency)), datetime.now(tz=timezone.utc).timestamp() + _time._to_seconds(str(frequency))))
        elif autopurge:
            self.bot.db.execute('UPDATE autopurge SET frequency = "{}", next_purge_at = "{}" WHERE guild_id = "{}"'.format(
                _time._to_seconds(str(frequency)), datetime.now(tz=timezone.utc).timestamp() + _time._to_seconds(str(frequency)), ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Set the autopurge frequency to **{}**'.format(frequency)))

    @autopurge.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def delete(self, ctx):
        self.bot.db.execute(
            'SELECT * FROM autopurge WHERE guild_id = "{}"'.format(ctx.guild.id))
        result = self.bot.db.fetchone()
        if not result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This server doesn\'t have an autopurge config set.'))
        self.bot.db.execute(
            'DELETE FROM autopurge WHERE guild_id = "{}"'.format(ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Deleted** the autopurge config'))


def setup(bot):
    bot.add_cog(Autopurge(bot))
