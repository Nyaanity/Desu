import discord
from discord.ext import commands
from __bot.embeds import Embeds as embeds


class CustomCommand(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.db.execute('''CREATE TABLE IF NOT EXISTS customcommand(
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            enabled TEXT,
            command TEXT,
            response TEXT,
            guild_id TEXT,
                PRIMARY KEY (id))''')

    @commands.Cog.listener()
    async def on_message(self, ctx):
        try:
            if str(ctx.channel.type) == 'private':
                return
            try:
                self.bot.db.execute(
                    'SELECT enabled FROM customcommand WHERE guild_id = "{}"'.format(ctx.guild.id))
            except:
                return
            enabled = self.bot.db.fetchone()
            if enabled:
                if enabled[0]:
                    if int(enabled[0]) == 0:
                        return
            try:
                self.bot.db.execute('SELECT * FROM {} WHERE guild_id = {} AND command = "{}"'.format(
                    'customcommand', ctx.guild.id, ctx.content))
                result = self.bot.db.fetchone()
                if result:
                    await ctx.channel.send(result[3])
            except:
                return
        except:
            return

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def customcommand(self, ctx):
        prefix = self.bot.config._get_prefix(self.bot, ctx)
        embed = discord.Embed(title='Custom Commands',
                              description=f"**<>** = required\n**[]** = optional",
                              color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None,
                              timestamp=ctx.message.created_at)
        embed.add_field(
            name='Set up a custom command', value='`{}customcommand setup`'.format(prefix))
        embed.add_field(name='Delete a command',
                        value='`{}customcommand delete <commandid>`'.format(prefix))
        embed.add_field(name='Delete all commands',
                        value='`{}customcommand deleteall`'.format(prefix))
        embed.add_field(name='Enable/disable custom message commands',
                        value='`{}customcommand toggle`'.format(prefix))
        embed.add_field(name='List all custom message commands',
                        value='`{}customcommand list`'.format(prefix))
        await ctx.send(embed=embed)

    @customcommand.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def setup(self, ctx):
        self.bot.db.execute('SELECT command FROM {} WHERE guild_id = {}'.format(
            'customcommand', ctx.guild.id))
        commands = self.bot.db.fetchall()
        await ctx.send(embed=embeds.AwaitInput._text_to_embed(self.bot, ctx, 'Please enter a message that should trigger the response, e.g. **!twitch**, **!youtube**. Cancel with **cancel**'))
        while 1:
            command = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
            if str(command.content) == 'cancel':
                return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Cancelled'))
            if str(command.content) in [x[0] for x in commands]:
                await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This command already exists. Please enter something else.'))
                continue
            break
        await ctx.send(embed=embeds.AwaitInput._text_to_embed(self.bot, ctx, 'Please enter a response that should be sent if the given command is sent, e.g. **Link to my website: https://example.com/**. Cancel with **cancel**'))
        response = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
        if str(response.content) == 'cancel':
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Cancelled'))
        self.bot.db.execute('INSERT INTO customcommand (command,response,guild_id) VALUES ("{}","{}","{}")'.format(
            command.content, response.content, ctx.guild.id))
        self.bot.db.execute('SELECT id FROM customcommand WHERE guild_id = {} AND command = "{}" AND response = "{}"'.format(
            str(ctx.guild.id), str(command.content), str(response.content)))
        command_id = self.bot.db.fetchone()
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Added command **{}**\n\nCommand ID: **{}**'.format(command.content, command_id[0])))

    @customcommand.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def delete(self, ctx, command_id):
        self.bot.db.execute(
            'SELECT * FROM customcommand WHERE guild_id = {} AND id = {}'.format(ctx.guild.id, command_id))
        exists = self.bot.db.fetchone()
        if not exists:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No record with that command ID was found.'))
        self.bot.db.execute('DELETE FROM customcommand WHERE guild_id = {} AND id = {}'.format(
            ctx.guild.id, command_id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Deleted command **{}**'.format(exists[2])))

    @customcommand.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def deleteall(self, ctx):
        self.bot.db.execute(
            'SELECT * FROM customcommand WHERE guild_id = {}'.format(ctx.guild.id))
        exists = self.bot.db.fetchall()
        if not exists:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No records were found on this server.'))
        self.bot.db.execute('DELETE FROM customcommand WHERE guild_id = {}'.format(
            ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Deleted **{}** command(s)'.format(len(exists))))

    @customcommand.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def toggle(self, ctx):
        self.bot.db.execute(
            'SELECT * FROM customcommand WHERE guild_id = "{}"'.format(ctx.guild.id))
        exists = self.bot.db.fetchall()
        if not exists:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No commands were found on this server.'))
        self.bot.db.execute(
            'SELECT enabled FROM customcommand WHERE guild_id = "{}"'.format(ctx.guild.id))
        enabled = self.bot.db.fetchone()
        if not enabled[0]:
            self.bot.db.execute(
                'UPDATE customcommand SET enabled = 0 WHERE guild_id = "{}"'.format(ctx.guild.id))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Disabled custom commands'))
        elif enabled[0]:
            if int(enabled[0]) == 0:
                self.bot.db.execute(
                    'UPDATE customcommand SET enabled = 1 WHERE guild_id = "{}"'.format(ctx.guild.id))
                return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Enabled custom commands'))
            self.bot.db.execute(
                'UPDATE customcommand SET enabled = 0 WHERE guild_id = "{}"'.format(ctx.guild.id))
            await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Disabled custom commands'))

    @customcommand.command(name='list')
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def _list(self, ctx):
        self.bot.db.execute('SELECT * FROM {} WHERE guild_id = {}'.format(
            'customcommand', ctx.guild.id))
        commands = self.bot.db.fetchall()
        if not commands:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No commands were found on this server.'))
        embed = discord.Embed(description='\n'.join(
            '**Command ID {}**: '.format(str(x[0])) + str(x[2]) for x in commands), color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
            None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None)
        embed.set_author(
            name='Total commands: {}'.format(len([x for x in commands])))
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(CustomCommand(bot))
