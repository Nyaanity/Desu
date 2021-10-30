from discord.ext import commands
import discord
from datetime import datetime, timezone
from __bot.embeds import Embeds as embeds


class Joinblock(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.duplicate_flags = []
        self.bot.db.execute('''CREATE TABLE IF NOT EXISTS joinblock(
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            guild_id TEXT,
            enabled TEXT,
                PRIMARY KEY (id))''')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        self.bot.db.execute(
            'SELECT enabled FROM joinblock WHERE guild_id = "{}"'.format(member.guild.id))
        joinblock = self.bot.db.fetchone()
        if not joinblock:
            return
        if str(joinblock[0]) == '1':
            if member.guild.me.guild_permissions.ban_members:
                punished_at = int(datetime.now(tz=timezone.utc).timestamp())
                self.bot.db.execute(
                    'INSERT INTO moderation(action,sanctioned_by,sanctioned_by_id,user,user_id,punished_at,punished_until,reason,guild_id) VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format('Ban',
                                                                                                                                                                                                        self.bot.user.name + '#' +
                                                                                                                                                                                                        str(
                                                                                                                                                                                                            self.bot.user.discriminator),
                                                                                                                                                                                                        self.bot.user.id,
                                                                                                                                                                                                        member.name + '#' +
                                                                                                                                                                                                        str(
                                                                                                                                                                                                            member.discriminator),
                                                                                                                                                                                                        member.id,
                                                                                                                                                                                                        punished_at,
                                                                                                                                                                                                        'N/A',
                                                                                                                                                                                                        'Blocked Join',
                                                                                                                                                                                                        member.guild.id))
                await member.ban(reason='Blocked Join')

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def joinblock(self, ctx):
        prefix = self.bot.config._get_prefix(self.bot, ctx)
        embed = discord.Embed(title='Join Blocker',
                              description=f"**<>** = required\n**[]** = optional",
                              color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None,
                              timestamp=ctx.message.created_at)
        embed.add_field(
            name='Enable/disable join blocker', value='`{}joinblock toggle`'.format(prefix))
        await ctx.send(embed=embed)

    @joinblock.command()
    @commands.has_guild_permissions(administrator=True)
    @commands.guild_only()
    async def toggle(self, ctx):
        self.bot.db.execute(
            'SELECT * FROM joinblock WHERE guild_id = "{}"'.format(ctx.guild.id))
        result = self.bot.db.fetchone()
        if not result:
            self.bot.db.execute('INSERT INTO joinblock(guild_id,enabled) VALUES("{}","{}")'.format(
                ctx.guild.id, 1))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Enabled** join block'))
        if str(result[2]) == '1':
            self.bot.db.execute('UPDATE joinblock SET enabled = "{}" WHERE guild_id ="{}"'.format(
                0, ctx.guild.id))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Disabled** join block'))
        self.bot.db.execute('UPDATE joinblock SET enabled = "{}" WHERE guild_id ="{}"'.format(
            1, ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Enabled** join block'))


def setup(bot):
    bot.add_cog(Joinblock(bot))
