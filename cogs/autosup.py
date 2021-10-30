import discord
from discord.ext import commands
import asyncio
from __bot.embeds import Embeds as embeds


class AutoSupport(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.db.execute('''CREATE TABLE IF NOT EXISTS autosupport(
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            enabled TEXT,
            command TEXT,
            response TEXT,
            guild_id TEXT,
            channel_id TEXT,
            deletion_delay TEXT,
                PRIMARY KEY (id))''')
        self.bot.db.execute(
            'ALTER TABLE `autosupport` CHANGE `command` `command` VARCHAR(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL;')
        self.bot.db.execute(
            'ALTER TABLE `autosupport` CHANGE `response` `response` VARCHAR(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL;')

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if str(ctx.channel.type) == 'private':
            return
        if ctx.author.bot:
            return
        self.bot.db.execute(
            'SELECT enabled FROM autosupport WHERE guild_id = "{}"'.format(ctx.guild.id))
        enabled = self.bot.db.fetchone()
        if enabled:
            if enabled[0]:
                if int(enabled[0]) == 0:
                    return
        self.bot.db.execute('SELECT command FROM autosupport WHERE guild_id = "{}" AND channel_id = "{}"'.format(
            ctx.guild.id, ctx.channel.id))
        result = self.bot.db.fetchall()
        if not result:
            return
        if not str(ctx.content) in str(result):
            try:
                return await ctx.delete()
            except:
                return
        try:
            self.bot.db.execute('SELECT * FROM {} WHERE guild_id = {} AND command = "{}" AND channel_id = "{}"'.format(
                'autosupport', ctx.guild.id, ctx.content, ctx.channel.id))
            result = self.bot.db.fetchone()
            if result:
                _m = await ctx.channel.send(result[3])
                if str(result[6]) != '0':
                    await asyncio.sleep(int(result[6]))
                    if ctx.guild.me.guild_permissions.manage_messages:
                        try:
                            await ctx.delete()
                        except:
                            return
                        try:
                            await _m.delete()
                        except:
                            pass
        except:
            return

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def autosupport(self, ctx):
        prefix = self.bot.config._get_prefix(self.bot, ctx)
        embed = discord.Embed(title='Autosupport',
                              description=f"**<>** = required\n**[]** = optional",
                              color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None,
                              timestamp=ctx.message.created_at)
        embed.add_field(
            name='Set up a autosupport command', value='`{}autosupport setup`'.format(prefix))
        embed.add_field(name='Delete a autosupport command',
                        value='`{}autosupport delete <commandid>`'.format(prefix))
        embed.add_field(name='Delete all autosupport commands',
                        value='`{}autosupport deleteall`'.format(prefix))
        embed.add_field(name='Enable/disable autosupport commands',
                        value='`{}autosupport toggle`'.format(prefix))
        embed.add_field(name='List all autosupport commands',
                        value='`{}autosupport list`'.format(prefix))
        await ctx.send(embed=embed)

    @autosupport.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def setup(self, ctx):
        self.bot.db.execute('SELECT command FROM {} WHERE guild_id = "{}"'.format(
            'autosupport', ctx.guild.id))
        commands = self.bot.db.fetchall()
        await ctx.send(embed=embeds.AwaitInput._text_to_embed(self.bot, ctx, 'Please enter a message that should trigger the response, e.g. **!twitch**, **!youtube**. Cancel with **cancel**'))
        while 1:
            command = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
            if str(command.content) == 'cancel':
                return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Cancelled'))
            if str(command.content) in [x[0] for x in commands]:
                await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This autosupport command already exists. Please enter something else.'))
                continue
            break
        await ctx.send(embed=embeds.AwaitInput._text_to_embed(self.bot, ctx, 'Please enter a response that should be sent if the given command is sent, e.g. **Link to my website: https://example.com/**. Cancel with **cancel**'))
        response = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
        if str(response.content) == 'cancel':
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Cancelled'))
        await ctx.send(embed=embeds.AwaitInput._text_to_embed(self.bot, ctx, 'Please mention the channel the support command should be sent in. Cancel with **cancel**'))
        while 1:
            autosupport_channel = await self.bot.wait_for('message', check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
            if autosupport_channel.content == 'cancel':
                return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Cancelled'))
            else:
                try:
                    autosupport_channel = autosupport_channel.content.replace(
                        '<#', '').replace('>', '')
                    autosupport_channel = discord.utils.get(
                        ctx.guild.text_channels, id=int(autosupport_channel))
                    if not autosupport_channel:
                        await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This channel doesn\'t exist. Please mention the channel like that: **#channel**'), delete_after=3)
                        continue
                    break
                except:
                    await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This channel doesn\'t exist. Please mention the channel like that: **#channel**'), delete_after=3)
                    continue

        await ctx.send(embed=embeds.AwaitInput._text_to_embed(self.bot, ctx, 'Please enter a deletion delay for the message sent by the user and the bot. Cancel with **cancel**'))
        while 1:
            deletion_delay = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
            if str(deletion_delay.content) == 'cancel':
                return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Cancelled'))
            if not str(deletion_delay.content).isdigit():
                await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Please enter an integer.'))
                continue
            break
        await ctx.send(embed=embeds.AwaitInput._text_to_embed(self.bot, ctx, 'Please enter a slowmode delay for the autosupport channel. At least 30s are required. Cancel with **cancel**'))
        while 1:
            slowmode_delay = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
            if str(slowmode_delay.content) == 'cancel':
                return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Cancelled'))
            if not str(slowmode_delay.content).isdigit():
                await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Please enter an integer.'))
                continue
            if int(slowmode_delay.content) < 30:
                await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Please enter something above 10s.'))
                continue
            elif int(slowmode_delay.content) > 2880:
                await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Slowmode can\'t be longer than 48m.'))
                continue
            break
        await autosupport_channel.edit(slowmode_delay=int(slowmode_delay.content))
        self.bot.db.execute('INSERT INTO autosupport (command,response,guild_id,channel_id,deletion_delay) VALUES ("{}","{}","{}","{}","{}")'.format(
            command.content, response.content, ctx.guild.id, autosupport_channel.id, deletion_delay.content))
        self.bot.db.execute('SELECT id FROM autosupport WHERE guild_id = {} AND command = "{}" AND response = "{}"'.format(
            str(ctx.guild.id), str(command.content), str(response.content)))
        command_id = self.bot.db.fetchone()
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Added autosupport command **{}**\n\nCommand ID: **{}**'.format(command.content, command_id[0])))

    @autosupport.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def delete(self, ctx, command_id):
        self.bot.db.execute(
            'SELECT * FROM autosupport WHERE guild_id = {} AND id = {}'.format(ctx.guild.id, command_id))
        exists = self.bot.db.fetchone()
        if not exists:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No record with that autosupport command ID was found.'))
        self.bot.db.execute('DELETE FROM autosupport WHERE guild_id = {} AND id = {}'.format(
            ctx.guild.id, command_id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Deleted autosupport command **{}**'.format(exists[2])))

    @autosupport.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def deleteall(self, ctx):
        self.bot.db.execute(
            'SELECT * FROM autosupport WHERE guild_id = {}'.format(ctx.guild.id))
        exists = self.bot.db.fetchall()
        if not exists:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No records were found on this server.'))
        self.bot.db.execute('DELETE FROM autosupport WHERE guild_id = {}'.format(
            ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Deleted **{}** autosupport command(s)'.format(len(exists))))

    @autosupport.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def toggle(self, ctx):
        self.bot.db.execute(
            'SELECT * FROM autosupport WHERE guild_id = {}'.format(ctx.guild.id))
        exists = self.bot.db.fetchall()
        if not exists:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No autosupport commands were found on this server.'))
        self.bot.db.execute(
            'SELECT enabled FROM autosupport WHERE guild_id = {}'.format(ctx.guild.id))
        enabled = self.bot.db.fetchone()
        if not enabled[0]:
            self.bot.db.execute(
                'UPDATE autosupport SET enabled = 0 WHERE guild_id = {}'.format(ctx.guild.id))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Disabled autosupport'))
        elif enabled[0]:
            if int(enabled[0]) == 0:
                self.bot.db.execute(
                    'UPDATE autosupport SET enabled = 1 WHERE guild_id = {}'.format(ctx.guild.id))
                return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Enabled autosupport'))
            self.bot.db.execute(
                'UPDATE autosupport SET enabled = 0 WHERE guild_id = {}'.format(ctx.guild.id))
            await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Disabled autosupport'))

    @autosupport.command(name='list')
    @commands.guild_only()
    async def _list(self, ctx):
        self.bot.db.execute('SELECT * FROM {} WHERE guild_id = {}'.format(
            'autosupport', ctx.guild.id))
        commands = self.bot.db.fetchall()
        if not commands:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No autosupport commands were found on this server.'))
        embed = discord.Embed(description='\n'.join(
            '**Command ID {}**: '.format(str(x[0])) + str(x[2]) for x in commands), color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
            None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None)
        embed.set_author(
            name='Total autosupport commands: {}'.format(len([x for x in commands])))
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(AutoSupport(bot))
