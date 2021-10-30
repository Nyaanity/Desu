from discord.ext import commands
import discord
import re
from __bot.embeds import Embeds as embeds


class Linkblock(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.duplicate_flags = []
        self.bot.db.execute('''CREATE TABLE IF NOT EXISTS linkblock(
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            guild_id TEXT,
            enabled TEXT,
                PRIMARY KEY (id))''')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if str(message.channel.type) == 'private':
            return
        if message.author.top_role.position >= message.guild.me.top_role.position or message.author.guild_permissions.administrator:
            return
        self.bot.db.execute(
            'SELECT enabled FROM linkblock WHERE guild_id = "{}"'.format(message.guild.id))
        linkblock = self.bot.db.fetchone()
        if not linkblock:
            return
        if str(linkblock[0]) == '1':
            if message.guild.me.guild_permissions.manage_messages:
                urls = re.findall(
                    'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.content.lower())
                if urls:
                    self.duplicate_flags.append(message.id)
                    await message.reply('No links allowed here, soz!', delete_after=5)
                    await message.delete()
                    self.duplicate_flags.remove(message.id)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.author.bot:
            return
        if str(after.channel.type) == 'private':
            return
        if after.author.top_role.position >= after.guild.me.top_role.position or after.author.guild_permissions.administrator:
            return
        self.bot.db.execute(
            'SELECT enabled FROM linkblock WHERE guild_id = "{}"'.format(after.guild.id))
        linkblock = self.bot.db.fetchone()
        if not linkblock:
            return
        if str(linkblock[0]) == '1':
            if after.guild.me.guild_permissions.manage_messages:
                urls = re.findall(
                    'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', after.content.lower())
                if urls:
                    if not after.id in self.duplicate_flags:
                        self.duplicate_flags.append(after.id)
                        await after.reply('No links allowed here, soz!', delete_after=5)
                        await after.delete()
                        self.duplicate_flags.remove(after.id)

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def linkblock(self, ctx):
        prefix = self.bot.config._get_prefix(self.bot, ctx)
        embed = discord.Embed(title='Link Blocker',
                              description=f"**<>** = required\n**[]** = optional",
                              color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None,
                              timestamp=ctx.message.created_at)
        embed.add_field(
            name='Enable/disable link blocker', value='`{}linkblock toggle`'.format(prefix))
        await ctx.send(embed=embed)

    @linkblock.command()
    @commands.has_guild_permissions(administrator=True)
    @commands.guild_only()
    async def toggle(self, ctx):
        self.bot.db.execute(
            'SELECT * FROM linkblock WHERE guild_id = "{}"'.format(ctx.guild.id))
        result = self.bot.db.fetchone()
        if not result:
            self.bot.db.execute('INSERT INTO linkblock(guild_id,enabled) VALUES("{}","{}")'.format(
                ctx.guild.id, 1))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Enabled** link protection'))
        if str(result[2]) == '1':
            self.bot.db.execute('UPDATE linkblock SET enabled = "{}" WHERE guild_id ="{}"'.format(
                0, ctx.guild.id))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Disabled** link protection'))
        self.bot.db.execute('UPDATE linkblock SET enabled = "{}" WHERE guild_id ="{}"'.format(
            1, ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Enabled** link protection'))


def setup(bot):
    bot.add_cog(Linkblock(bot))
