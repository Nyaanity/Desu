import discord
from discord.ext import commands
from __bot.embeds import Embeds as embeds


class Automod(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.db.execute('''CREATE TABLE IF NOT EXISTS maxinfractions(
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            guild_id TEXT,
            max TEXT,
            action TEXT,
                PRIMARY KEY (id))''')

    @commands.group(invoke_without_command=True, aliases=['maxwarns'])
    @commands.guild_only()
    async def maxinfractions(self, ctx):
        prefix = self.bot.config._get_prefix(self.bot, ctx)
        embed = discord.Embed(title='Warn Limit',
                              description=f"**<>** = required\n**[]** = optional",
                              color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None,
                              timestamp=ctx.message.created_at)
        embed.add_field(
            name='Set the max infractions (0 = off)', value='`{}maxinfractions max <max>`'.format(prefix))
        embed.add_field(
            name='Set an action when a user reaches the warn limit', value='`{}maxinfractions action <ban/kick/mute>`'.format(prefix))
        await ctx.send(embed=embed)

    @maxinfractions.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def max(self, ctx, max):
        self.bot.db.execute(
            'SELECT * FROM maxinfractions WHERE guild_id = "{}"'.format(ctx.guild.id))
        result = self.bot.db.fetchone()
        if not result and str(max) != '0':
            self.bot.db.execute('INSERT INTO maxinfractions(guild_id,max,action) VALUES("{}","{}","{}")'.format(
                ctx.guild.id, max, 'N/A'))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Set the max warn limit to **{}**'.format(max)))
        elif not result and str(max) == '0':
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Couldn\'t disable warn limit, max infractions are not set up on this server.'))
        elif result and str(max) == '0':
            self.bot.db.execute('UPDATE maxinfractions SET max = "{}" WHERE guild_id ="{}"'.format(
                0, ctx.guild.id))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Disabled** max infraction limit'))
        self.bot.db.execute('UPDATE maxinfractions SET max = "{}" WHERE guild_id ="{}"'.format(
            max, ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Set the max warn limit to **{}**'.format(max)))

    @maxinfractions.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def action(self, ctx, action):
        actions = ['ban', 'mute', 'kick']
        if not action in actions:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Please only use **ban**, **kick**, or **mute**.'))
        self.bot.db.execute(
            'SELECT * FROM maxinfractions WHERE guild_id = "{}"'.format(ctx.guild.id))
        result = self.bot.db.fetchone()
        if not result:
            self.bot.db.execute('INSERT INTO maxinfractions(guild_id,max,action) VALUES("{}","{}","{}")'.format(
                ctx.guild.id, 'N/A', action))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Set the max warn limit action to **{}**'.format(action)))
        self.bot.db.execute('UPDATE maxinfractions SET action = "{}" WHERE guild_id ="{}"'.format(
            action, ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Set the max warn limit action to **{}**'.format(action)))


def setup(bot):
    bot.add_cog(Automod(bot))
