from discord.ext import commands
import discord
from __bot.embeds import Embeds as embeds


class Wordblock(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.duplicate_flags = []
        self.bot.db.execute('''CREATE TABLE IF NOT EXISTS banword(
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            guild_id TEXT,
            enabled TEXT,
                PRIMARY KEY (id))''')
        self.bot.db.execute('''CREATE TABLE IF NOT EXISTS banwordlist(
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            guild_id TEXT,
            word TEXT,
                PRIMARY KEY (id))''')
        self.bot.db.execute('''CREATE TABLE IF NOT EXISTS banwordstrict(
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            guild_id TEXT,
            enabled TEXT,
                PRIMARY KEY (id))''')
        self.bot.db.execute('''CREATE TABLE IF NOT EXISTS banwordstrictlist(
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            guild_id TEXT,
            word TEXT,
                PRIMARY KEY (id))''')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if str(message.channel.type) == 'private':
            return
        if message.author.top_role.position >= message.guild.me.top_role.position or message.author.guild_permissions.administrator:
            return
        self.bot.db.execute('SELECT enabled FROM banword WHERE guild_id = "{}"'.format(
            message.guild.id))
        banword = self.bot.db.fetchone()
        self.bot.db.execute('SELECT enabled FROM banwordstrict WHERE guild_id = "{}"'.format(
            message.guild.id))
        banwordstrict = self.bot.db.fetchone()
        if not banword and not banwordstrict:
            return
        if banword:
            if str(banword[0]) == '1':
                self.bot.db.execute('SELECT word FROM banwordlist WHERE guild_id = "{}"'.format(
                    message.guild.id))
                words = self.bot.db.fetchall()
                word = [x[0]
                        for x in words if str(x[0]) in str(message.content)]
                if word:
                    await message.reply('Your message included a blacklisted word, soz!', delete_after=5)
                    return await message.delete()
        if banwordstrict:
            if str(banwordstrict[0]) == '1':
                self.bot.db.execute('SELECT word FROM banwordstrictlist WHERE guild_id = "{}"'.format(
                    message.guild.id))
                words = self.bot.db.fetchall()
                word = [x[0]
                        for x in words if str(message.content) == str(x[0])]
                if word:
                    await message.reply('This word is not allowed here, soz!', delete_after=5)
                    return await message.delete()

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.author.bot:
            return
        if str(after.channel.type) == 'private':
            return
        if after.author.top_role.position >= after.guild.me.top_role.position or after.author.guild_permissions.administrator:
            return
        self.bot.db.execute(
            'SELECT enabled FROM banword WHERE guild_id = "{}"'.format(after.guild.id))
        banword = self.bot.db.fetchone()
        self.bot.db.execute('SELECT enabled FROM banwordstrict WHERE guild_id = "{}"'.format(
            after.guild.id))
        banwordstrict = self.bot.db.fetchone()
        if not banword and not banwordstrict:
            return
        if banword:
            if str(banword[0]) == '1':
                self.bot.db.execute(
                    'SELECT word FROM banwordlist WHERE guild_id = "{}"'.format(after.guild.id))
                words = self.bot.db.fetchall()
                word = [x[0] for x in words if str(x[0]) in str(after.content)]
                if word:
                    self.duplicate_flags.append(after.id)
                    await after.reply('Your message included a blacklisted word, soz!', delete_after=5)
                    await after.delete()
                    return self.duplicate_flags.remove(after.id)
        if banwordstrict:
            if str(banwordstrict[0]) == '1':
                self.bot.db.execute('SELECT word FROM banwordstrictlist WHERE guild_id = "{}"'.format(
                    after.guild.id))
                words = self.bot.db.fetchall()
                word = [x[0] for x in words if str(x[0]) == str(after.content)]
                if word:
                    self.duplicate_flags.append(after.id)
                    await after.reply('This word is not allowed here, soz!', delete_after=5)
                    await after.delete()
                    self.duplicate_flags.remove(after.id)

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def banword(self, ctx):
        prefix = self.bot.config._get_prefix(self.bot, ctx)
        embed = discord.Embed(title='Word Ban',
                              description=f"**<>** = required\n**[]** = optional",
                              color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None,
                              timestamp=ctx.message.created_at)
        embed.add_field(
            name='Enable/disable bad word protection', value='`{}banword toggle`'.format(prefix))
        embed.add_field(
            name='Add a word to the blacklist', value='`{}banword add <word>`'.format(prefix))
        embed.add_field(
            name='Remove a word from the blacklist', value='`{}banword remove <word>`'.format(prefix))
        embed.add_field(
            name='List all banned words', value='`{}banword list`'.format(prefix))
        embed.add_field(
            name='Delete all banned words', value='`{}banword deleteall`'.format(prefix))
        await ctx.send(embed=embed)

    @banword.command()
    @commands.has_guild_permissions(administrator=True)
    @commands.guild_only()
    async def toggle(self, ctx):
        self.bot.db.execute(
            'SELECT * FROM banword WHERE guild_id = "{}"'.format(ctx.guild.id))
        result = self.bot.db.fetchone()
        if not result:
            self.bot.db.execute('INSERT INTO banword(guild_id,enabled) VALUES("{}","{}")'.format(
                ctx.guild.id, 1))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Enabled** bad word protection'))
        if str(result[2]) == '1':
            self.bot.db.execute('UPDATE banword SET enabled = "{}" WHERE guild_id ="{}"'.format(
                0, ctx.guild.id))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Disabled** bad word protection'))
        self.bot.db.execute('UPDATE banword SET enabled = "{}" WHERE guild_id ="{}"'.format(
            1, ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Enabled** bad word protection'))

    @banword.command()
    @commands.has_guild_permissions(administrator=True)
    @commands.guild_only()
    async def add(self, ctx, *, word):
        self.bot.db.execute(
            'SELECT * FROM banwordlist WHERE guild_id = "{}" AND word = "{}"'.format(ctx.guild.id, word))
        result = self.bot.db.fetchone()
        if result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This word is already blacklisted.'))
        self.bot.db.execute('INSERT INTO banwordlist(guild_id,word) VALUES("{}","{}")'.format(
            ctx.guild.id, word))
        self.bot.db.execute('SELECT id FROM banwordlist WHERE guild_id = "{}" AND word = "{}"'.format(
            ctx.guild.id, word))
        id = self.bot.db.fetchone()
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Added **{}** to the blacklisted words\n\nWordblock ID: **{}**'.format(word, id[0])))

    @banword.command()
    @commands.has_guild_permissions(administrator=True)
    @commands.guild_only()
    async def remove(self, ctx, wordblock_id):
        self.bot.db.execute(
            'SELECT * FROM banwordlist WHERE guild_id = "{}" AND id = "{}"'.format(ctx.guild.id, wordblock_id))
        result = self.bot.db.fetchone()
        if not result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No blacklisted word with that Wordblock ID was found.'))
        self.bot.db.execute('DELETE FROM banwordlist WHERE guild_id = "{}" AND id = "{}"'.format(
            ctx.guild.id, wordblock_id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Removed **{}** from the blacklisted words'.format(result[2])))

    @banword.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def list(self, ctx):
        self.bot.db.execute(
            'SELECT * FROM banwordlist WHERE guild_id = "{}"'.format(ctx.guild.id))
        result = self.bot.db.fetchall()
        if not result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No banned words were found on this server.'))
        embed = discord.Embed(description='\n'.join(
            '**Wordblock ID {}**: {}'.format(str(x[0]), str(x[2])) for x in result), color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
            None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None)
        embed.set_author(
            name='Total bans: {}'.format(len([x for x in result])))
        await ctx.send(embed=embed)

    @banword.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def deleteall(self, ctx):
        self.bot.db.execute(
            'SELECT * FROM banwordlist WHERE guild_id = "{}"'.format(ctx.guild.id))
        result = self.bot.db.fetchall()
        if not result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No banned words were found on this server.'))
        self.bot.db.execute(
            'DELETE FROM banwordlist WHERE guild_id = "{}"'.format(ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Deleted **{}** banned words'.format(len([x for x in result]))))

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def banwordstrict(self, ctx):
        prefix = self.bot.config._get_prefix(self.bot, ctx)
        embed = discord.Embed(title='Strict Word Ban',
                              description=f"**<>** = required\n**[]** = optional",
                              color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None,
                              timestamp=ctx.message.created_at)
        embed.add_field(
            name='Enable/disable bad word protection', value='`{}banwordstrict toggle`'.format(prefix))
        embed.add_field(
            name='Add a word to the blacklist', value='`{}banwordstrict add <word>`'.format(prefix))
        embed.add_field(
            name='Remove a word from the blacklist', value='`{}banwordstrict remove <word>`'.format(prefix))
        embed.add_field(
            name='List all banned words', value='`{}banwordstrict list`'.format(prefix))
        embed.add_field(
            name='Delete all banned words', value='`{}banwordstrict deleteall`'.format(prefix))
        await ctx.send(embed=embed)

    @banwordstrict.command(name='toggle')
    @commands.has_guild_permissions(administrator=True)
    @commands.guild_only()
    async def _toggle(self, ctx):
        self.bot.db.execute(
            'SELECT * FROM banwordstrict WHERE guild_id = "{}"'.format(ctx.guild.id))
        result = self.bot.db.fetchone()
        if not result:
            self.bot.db.execute('INSERT INTO banwordstrict(guild_id,enabled) VALUES("{}","{}")'.format(
                ctx.guild.id, 1))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Enabled** strict bad word protection'))
        if str(result[2]) == '1':
            self.bot.db.execute('UPDATE banwordstrict SET enabled = "{}" WHERE guild_id ="{}"'.format(
                0, ctx.guild.id))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Disabled** strict bad word protection'))
        self.bot.db.execute('UPDATE banwordstrict SET enabled = "{}" WHERE guild_id ="{}"'.format(
            1, ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Enabled** strict bad word protection'))

    @banwordstrict.command(name='add')
    @commands.has_guild_permissions(administrator=True)
    @commands.guild_only()
    async def _add(self, ctx, *, word):
        self.bot.db.execute(
            'SELECT * FROM banwordstrictlist WHERE guild_id = "{}" AND word = "{}"'.format(ctx.guild.id, word))
        result = self.bot.db.fetchone()
        if result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This word is already blacklisted.'))
        self.bot.db.execute('INSERT INTO banwordstrictlist(guild_id,word) VALUES("{}","{}")'.format(
            ctx.guild.id, word))
        self.bot.db.execute('SELECT id FROM banwordstrictlist WHERE guild_id = "{}" AND word = "{}"'.format(
            ctx.guild.id, word))
        id = self.bot.db.fetchone()
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Added **{}** to the strict blacklisted words\n\nWordblock ID: **{}**'.format(word, id[0])))

    @banwordstrict.command(name='remove')
    @commands.has_guild_permissions(administrator=True)
    @commands.guild_only()
    async def _remove(self, ctx, wordblock_id):
        self.bot.db.execute(
            'SELECT * FROM banwordstrictlist WHERE guild_id = "{}" AND id = "{}"'.format(ctx.guild.id, wordblock_id))
        result = self.bot.db.fetchone()
        if not result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No blacklisted word with that Wordblock ID was found.'))
        self.bot.db.execute('DELETE FROM banwordstrictlist WHERE guild_id = "{}" AND id = "{}"'.format(
            ctx.guild.id, wordblock_id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Removed **{}** from the strict blacklisted words'.format(result[2])))

    @banwordstrict.command(name='list')
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def _list(self, ctx):
        self.bot.db.execute(
            'SELECT * FROM banwordstrictlist WHERE guild_id = "{}"'.format(ctx.guild.id))
        result = self.bot.db.fetchall()
        if not result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No strict banned words were found on this server.'))
        embed = discord.Embed(description='\n'.join(
            '**Wordblock ID {}**: {}'.format(str(x[0]), str(x[2])) for x in result), color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
            None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None)
        embed.set_author(
            name='Total bans: {}'.format(len([x for x in result])))
        await ctx.send(embed=embed)

    @banwordstrict.command(name='deleteall')
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def _deleteall(self, ctx):
        self.bot.db.execute(
            'SELECT * FROM banwordstrictlist WHERE guild_id = "{}"'.format(ctx.guild.id))
        result = self.bot.db.fetchall()
        if not result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No strict banned words were found on this server.'))
        self.bot.db.execute(
            'DELETE FROM banwordstrictlist WHERE guild_id = "{}"'.format(ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Deleted **{}** strict banned words'.format(len([x for x in result]))))


def setup(bot):
    bot.add_cog(Wordblock(bot))
