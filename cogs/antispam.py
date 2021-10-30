from discord.ext import commands
import discord
import asyncio
from datetime import datetime, timezone
from __bot.embeds import Embeds as embeds


class Antispam(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.author_stash = []
        self.bot.db.execute('''CREATE TABLE IF NOT EXISTS antispam(
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            guild_id TEXT,
            enabled TEXT,
            action TEXT,
                PRIMARY KEY (id))''')
        self.bot.db.execute('''CREATE TABLE IF NOT EXISTS antispamv2(
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            guild_id TEXT,
            enabled TEXT,
            action TEXT,
                PRIMARY KEY (id))''')

    @commands.Cog.listener()
    async def on_message(self, message):
        message_stash = []
        if message.author.bot:
            return
        if str(message.channel.type) == 'private':
            return
        if message.author.top_role.position >= message.guild.me.top_role.position or message.author.guild_permissions.administrator:
            return
        if {'author_id': message.author.id, 'guild_id': message.guild.id} in self.author_stash:
            return
        self.author_stash.append(
            {'author_id': message.author.id, 'guild_id': message.guild.id})
        message_stash.append(message)
        for i in range(4):
            try:
                msg = await self.bot.wait_for('message', timeout=3, check=lambda m: m.author.id == message.author.id and message.guild.id == m.guild.id)
            except asyncio.TimeoutError:
                return self.author_stash.remove({'author_id': message.author.id, 'guild_id': message.guild.id})
            message_stash.append(msg)
            if msg.channel.id != message.channel.id:
                try:
                    _msg = await self.bot.wait_for('message', timeout=4, check=lambda m: m.author.id == message.author.id and message.guild.id == m.guild.id)
                except asyncio.TimeoutError:
                    return self.author_stash.remove({'author_id': message.author.id, 'guild_id': message.guild.id})
                if _msg.channel.id != msg.channel.id and _msg.channel.id != message.channel.id and 'http' in str(msg.content):
                    for message in message_stash:
                        await message.channel.purge(check=lambda m: m.id in [m.id for m in message_stash])
                    self.bot.db.execute(
                        'SELECT * FROM antispamv2 WHERE guild_id = "{}"'.format(message.guild.id))
                    result = self.bot.db.fetchone()
                    if result:
                        if str(result[2]) == 'N/A' or str(result[3]) == 'N/A':
                            return
                        elif str(result[2]) == '1':
                            if str(result[3]) == 'delete':
                                await message.reply(message.author.mention + ', fake links are not allowed.', delete_after=5)
                            elif str(result[3]) == 'ban':
                                if not message.guild.me.guild_permissions.ban_members or message.author.top_role.position >= message.guild.me.top_role.position:
                                    return
                                punished_at = int(datetime.now(
                                    tz=timezone.utc).timestamp())
                                self.bot.db.execute(
                                    'INSERT INTO moderation(action,sanctioned_by,sanctioned_by_id,user,user_id,punished_at,punished_until,reason,guild_id) VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format('Ban',
                                                                                                                                                                                                                        self.bot.user.name + '#' +
                                                                                                                                                                                                                        str(
                                                                                                                                                                                                                            self.bot.user.discriminator),
                                                                                                                                                                                                                        self.bot.user.id,
                                                                                                                                                                                                                        message.author.name + '#' +
                                                                                                                                                                                                                        str(
                                                                                                                                                                                                                            message.author.discriminator),
                                                                                                                                                                                                                        message.author.id,
                                                                                                                                                                                                                        punished_at,
                                                                                                                                                                                                                        'N/A',
                                                                                                                                                                                                                        'Spam Protection v2: Sent fake links',
                                                                                                                                                                                                                        message.guild.id))
                                await message.author.ban(reason='Spam Protection v2: Sent fake links')
                            elif str(result[3]) == 'kick':
                                if not message.guild.me.guild_permissions.kick_members or message.author.top_role.position >= message.guild.me.top_role.position:
                                    return
                                punished_at = int(datetime.now(
                                    tz=timezone.utc).timestamp())
                                self.bot.db.execute(
                                    'INSERT INTO moderation(action,sanctioned_by,sanctioned_by_id,user,user_id,punished_at,punished_until,reason,guild_id) VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format('Kick',
                                                                                                                                                                                                                        self.bot.user.name + '#' +
                                                                                                                                                                                                                        str(
                                                                                                                                                                                                                            self.bot.user.discriminator),
                                                                                                                                                                                                                        self.bot.user.id,
                                                                                                                                                                                                                        message.author.name + '#' +
                                                                                                                                                                                                                        str(
                                                                                                                                                                                                                            message.author.discriminator),
                                                                                                                                                                                                                        message.author.id,
                                                                                                                                                                                                                        punished_at,
                                                                                                                                                                                                                        'N/A',
                                                                                                                                                                                                                        'Spam Protection v2: Sent fake links',
                                                                                                                                                                                                                        message.guild.id))
                                await message.author.kick(reason='Spam Protection v2: Sent fake links')
                            elif str(result[3]) == 'mute':
                                if not message.guild.me.guild_permissions.manage_roles or message.author.top_role.position >= message.guild.me.top_role.position or not 'muted' in [str(x.name).lower() for x in message.guild.roles]:
                                    return
                                muted_role = [
                                    x for x in message.guild.roles if 'muted' in str(x.name).lower()][0]
                                if muted_role.position > message.guild.me.top_role.position:
                                    return
                                punished_at = int(datetime.now(
                                    tz=timezone.utc).timestamp())
                                self.bot.db.execute(
                                    'INSERT INTO moderation(action,sanctioned_by,sanctioned_by_id,user,user_id,punished_at,punished_until,reason,guild_id) VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format('Mute',
                                                                                                                                                                                                                        self.bot.user.name + '#' +
                                                                                                                                                                                                                        str(
                                                                                                                                                                                                                            self.bot.user.discriminator),
                                                                                                                                                                                                                        self.bot.user.id,
                                                                                                                                                                                                                        message.author.name + '#' +
                                                                                                                                                                                                                        str(
                                                                                                                                                                                                                            message.author.discriminator),
                                                                                                                                                                                                                        message.author.id,
                                                                                                                                                                                                                        punished_at,
                                                                                                                                                                                                                        'N/A',
                                                                                                                                                                                                                        'Spam Protection v2: Sent fake links',
                                                                                                                                                                                                                        message.guild.id))
                                await message.author.add_roles(muted_role, reason='Spam Protection v2: Sent fake links')
                            elif str(result[3]) == 'warn':
                                if message.author.top_role.position >= message.guild.me.top_role.position:
                                    return
                                punished_at = int(datetime.now(
                                    tz=timezone.utc).timestamp())
                                self.bot.db.execute(
                                    'INSERT INTO moderation(action,sanctioned_by,sanctioned_by_id,user,user_id,punished_at,punished_until,reason,guild_id) VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format('Warn',
                                                                                                                                                                                                                        self.bot.user.name + '#' +
                                                                                                                                                                                                                        str(
                                                                                                                                                                                                                            self.bot.user.discriminator),
                                                                                                                                                                                                                        self.bot.user.id,
                                                                                                                                                                                                                        message.author.name + '#' +
                                                                                                                                                                                                                        str(
                                                                                                                                                                                                                            message.author.discriminator),
                                                                                                                                                                                                                        message.author.id,
                                                                                                                                                                                                                        punished_at,
                                                                                                                                                                                                                        'N/A',
                                                                                                                                                                                                                        'Spam Protection v2: Sent fake links',
                                                                                                                                                                                                                        message.guild.id))
                                await message.reply(message.author.mention + ', fake links are not allowed.', delete_after=5)
                        else:
                            ...
                        return self.author_stash.remove({'author_id': message.author.id, 'guild_id': message.guild.id})
        self.author_stash.remove(
            {'author_id': message.author.id, 'guild_id': message.guild.id})
        self.bot.db.execute(
            'SELECT * FROM antispam WHERE guild_id = "{}"'.format(message.guild.id))
        result = self.bot.db.fetchone()
        if result:
            if str(result[2]) == 'N/A' or str(result[3]) == 'N/A':
                return
            elif str(result[2]) == '1':
                await message_stash[0].channel.purge(check=lambda m: m.id in [m.id for m in message_stash])
                if str(result[3]) == 'delete':
                    await message.channel.send(message.author.mention + ', please stop spamming.', delete_after=5)
                elif str(result[3]) == 'ban':
                    if not message.guild.me.guild_permissions.ban_members or message.author.top_role.position >= message.guild.me.top_role.position:
                        return
                    punished_at = int(datetime.now(
                        tz=timezone.utc).timestamp())
                    self.bot.db.execute(
                        'INSERT INTO moderation(action,sanctioned_by,sanctioned_by_id,user,user_id,punished_at,punished_until,reason,guild_id) VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format('Ban',
                                                                                                                                                                                                            self.bot.user.name + '#' +
                                                                                                                                                                                                            str(
                                                                                                                                                                                                                self.bot.user.discriminator),
                                                                                                                                                                                                            self.bot.user.id,
                                                                                                                                                                                                            message.author.name + '#' +
                                                                                                                                                                                                            str(
                                                                                                                                                                                                                message.author.discriminator),
                                                                                                                                                                                                            message.author.id,
                                                                                                                                                                                                            punished_at,
                                                                                                                                                                                                            'N/A',
                                                                                                                                                                                                            'Spam Protection: Spammed',
                                                                                                                                                                                                            message.guild.id))
                    await message.author.ban(reason='Spam Protection: Spammed')
                elif str(result[3]) == 'kick':
                    if not message.guild.me.guild_permissions.kick_members or message.author.top_role.position >= message.guild.me.top_role.position:
                        return
                    punished_at = int(datetime.now(
                        tz=timezone.utc).timestamp())
                    self.bot.db.execute(
                        'INSERT INTO moderation(action,sanctioned_by,sanctioned_by_id,user,user_id,punished_at,punished_until,reason,guild_id) VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format('Kick',
                                                                                                                                                                                                            self.bot.user.name + '#' +
                                                                                                                                                                                                            str(
                                                                                                                                                                                                                self.bot.user.discriminator),
                                                                                                                                                                                                            self.bot.user.id,
                                                                                                                                                                                                            message.author.name + '#' +
                                                                                                                                                                                                            str(
                                                                                                                                                                                                                message.author.discriminator),
                                                                                                                                                                                                            message.author.id,
                                                                                                                                                                                                            punished_at,
                                                                                                                                                                                                            'N/A',
                                                                                                                                                                                                            'Spam Protection: Spammed',
                                                                                                                                                                                                            message.guild.id))
                    await message.author.kick(reason='Spam Protection: Spammed')
                elif str(result[3]) == 'mute':
                    if not message.guild.me.guild_permissions.manage_roles or message.author.top_role.position >= message.guild.me.top_role.position or not 'muted' in [str(x.name).lower() for x in message.guild.roles]:
                        return
                    muted_role = [
                        x for x in message.guild.roles if 'muted' in str(x.name).lower()][0]
                    if muted_role.position > message.guild.me.top_role.position:
                        return
                    punished_at = int(datetime.now(
                        tz=timezone.utc).timestamp())
                    self.bot.db.execute(
                        'INSERT INTO moderation(action,sanctioned_by,sanctioned_by_id,user,user_id,punished_at,punished_until,reason,guild_id) VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format('Mute',
                                                                                                                                                                                                            self.bot.user.name + '#' +
                                                                                                                                                                                                            str(
                                                                                                                                                                                                                self.bot.user.discriminator),
                                                                                                                                                                                                            self.bot.user.id,
                                                                                                                                                                                                            message.author.name + '#' +
                                                                                                                                                                                                            str(
                                                                                                                                                                                                                message.author.discriminator),
                                                                                                                                                                                                            message.author.id,
                                                                                                                                                                                                            punished_at,
                                                                                                                                                                                                            'N/A',
                                                                                                                                                                                                            'Spam Protection: Spammed',
                                                                                                                                                                                                            message.guild.id))
                    await message.author.add_roles(muted_role, reason='Spam Protection: Spammed')
                elif str(result[3]) == 'warn':
                    if message.author.top_role.position >= message.guild.me.top_role.position:
                        return
                    punished_at = int(datetime.now(
                        tz=timezone.utc).timestamp())
                    self.bot.db.execute(
                        'INSERT INTO moderation(action,sanctioned_by,sanctioned_by_id,user,user_id,punished_at,punished_until,reason,guild_id) VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format('Warn',
                                                                                                                                                                                                            self.bot.user.name + '#' +
                                                                                                                                                                                                            str(
                                                                                                                                                                                                                self.bot.user.discriminator),
                                                                                                                                                                                                            self.bot.user.id,
                                                                                                                                                                                                            message.author.name + '#' +
                                                                                                                                                                                                            str(
                                                                                                                                                                                                                message.author.discriminator),
                                                                                                                                                                                                            message.author.id,
                                                                                                                                                                                                            punished_at,
                                                                                                                                                                                                            'N/A',
                                                                                                                                                                                                            'Spam Protection: Spammed',
                                                                                                                                                                                                            message.guild.id))
                    await message.reply(message.author.mention + ', please stop spamming.', delete_after=5)

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def antispam(self, ctx):
        prefix = self.bot.config._get_prefix(self.bot, ctx)
        embed = discord.Embed(title='Spam Protection',
                              description=f"**<>** = required\n**[]** = optional",
                              color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None,
                              timestamp=ctx.message.created_at)
        embed.add_field(
            name='Enable/disable spam protection', value='`{}antispam toggle`'.format(prefix))
        embed.add_field(
            name='Set an action if a spamming user is detected', value='`{}antispam action <warn/mute/kick/delete>`'.format(prefix))
        embed.add_field(
            name='Delete the anti-spam config', value='`{}antispam delete`'.format(prefix))
        await ctx.send(embed=embed)

    @antispam.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def toggle(self, ctx):
        self.bot.db.execute(
            'SELECT * FROM antispam WHERE guild_id = "{}"'.format(ctx.guild.id))
        result = self.bot.db.fetchone()
        if not result:
            self.bot.db.execute('INSERT INTO antispam(guild_id,enabled,action) VALUES("{}","{}","{}")'.format(
                ctx.guild.id, 1, 'N/A'))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Enabled** spam protection'))
        if str(result[2]) == '1':
            self.bot.db.execute('UPDATE antispam SET enabled = "{}" WHERE guild_id = "{}"'.format(
                0, ctx.guild.id))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Disabled** spam protection'))
        self.bot.db.execute('UPDATE antispam SET enabled = "{}" WHERE guild_id = "{}"'.format(
            1, ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Enabled** spam protection'))

    @antispam.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def action(self, ctx, action):
        actions = ['warn', 'mute', 'kick', 'delete']
        if not action in actions:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Please only use **warn**, **kick**, **delete** or **mute**.'))
        self.bot.db.execute(
            'SELECT * FROM antispam WHERE guild_id = "{}"'.format(ctx.guild.id))
        result = self.bot.db.fetchone()
        if not result:
            self.bot.db.execute('INSERT INTO antispam(guild_id,enabled,action) VALUES("{}","{}","{}")'.format(
                ctx.guild.id, 'N/A', action))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Set the spam protection action to **{}**'.format(action)))
        self.bot.db.execute('UPDATE antispam SET action = "{}" WHERE guild_id ="{}"'.format(
            action, ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Set the spam protection action to **{}**'.format(action)))

    @antispam.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def delete(self, ctx):
        self.bot.db.execute(
            'SELECT * FROM antispam WHERE guild_id = "{}"'.format(ctx.guild.id))
        result = self.bot.db.fetchone()
        if not result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This server doesn\'t have a spam protection config set.'))
        self.bot.db.execute(
            'DELETE FROM antispam WHERE guild_id = "{}"'.format(ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Deleted the spam protection config'))

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def antispamv2(self, ctx):
        prefix = self.bot.config._get_prefix(self.bot, ctx)
        embed = discord.Embed(title='Spam Protection v2',
                              description=f"**<>** = required\n**[]** = optional",
                              color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None,
                              timestamp=ctx.message.created_at)
        embed.add_field(
            name='Enable/disable spam protection', value='`{}antispamv2 toggle`'.format(prefix))
        embed.add_field(
            name='Set an action if a spamming user is detected', value='`{}antispamv2 action <ban/kick/mute/warn/delete>`'.format(prefix))
        embed.add_field(
            name='Delete the anti-spam config', value='`{}antispamv2 delete`'.format(prefix))
        await ctx.send(embed=embed)

    @antispamv2.command(name='toggle')
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def _toggle(self, ctx):
        self.bot.db.execute(
            'SELECT * FROM antispamv2 WHERE guild_id = "{}"'.format(ctx.guild.id))
        result = self.bot.db.fetchone()
        if not result:
            self.bot.db.execute('INSERT INTO antispamv2(guild_id,enabled,action) VALUES("{}","{}","{}")'.format(
                ctx.guild.id, 1, 'N/A'))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Enabled** spam protection'))
        if str(result[2]) == '1':
            self.bot.db.execute('UPDATE antispamv2 SET enabled = "{}" WHERE guild_id = "{}"'.format(
                0, ctx.guild.id))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Disabled** spam protection'))
        self.bot.db.execute('UPDATE antispamv2 SET enabled = "{}" WHERE guild_id = "{}"'.format(
            1, ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Enabled** spam protection'))

    @antispamv2.command(name='action')
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def _action(self, ctx, action):
        actions = ['warn', 'mute', 'kick', 'ban', 'delete']
        if not action in actions:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Please only use **warn**, **kick** or **mute**.'))
        self.bot.db.execute(
            'SELECT * FROM antispamv2 WHERE guild_id = "{}"'.format(ctx.guild.id))
        result = self.bot.db.fetchone()
        if not result:
            self.bot.db.execute('INSERT INTO antispamv2(guild_id,enabled,action) VALUES("{}","{}","{}")'.format(
                ctx.guild.id, 'N/A', action))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Set the spam protection action to **{}**'.format(action)))
        self.bot.db.execute('UPDATE antispamv2 SET action = "{}" WHERE guild_id ="{}"'.format(
            action, ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Set the spam protection action to **{}**'.format(action)))

    @antispamv2.command(name='delete')
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def _delete(self, ctx):
        self.bot.db.execute(
            'SELECT * FROM antispamv2 WHERE guild_id = "{}"'.format(ctx.guild.id))
        result = self.bot.db.fetchone()
        if not result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This server doesn\'t have a spam protection config set.'))
        self.bot.db.execute(
            'DELETE FROM antispamv2 WHERE guild_id = "{}"'.format(ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Deleted** the spam protection config'))


def setup(bot):
    bot.add_cog(Antispam(bot))
