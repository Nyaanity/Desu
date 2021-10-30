import discord
from discord import member
from discord.ext import commands
from time import time
from datetime import datetime, timezone
from discord_components import Button, ButtonStyle
import asyncio
from __bot.embeds import Embeds as embeds
from __bot.time import TimeConverter as _time


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.db.execute('''CREATE TABLE IF NOT EXISTS moderation(
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            action TEXT,
            sanctioned_by TEXT,
            sanctioned_by_id TEXT,
            user TEXT,
            user_id TEXT,
            punished_at TEXT,
            punished_until TEXT,
            reason TEXT,
            guild_id TEXT,
            channel_id TEXT,
                PRIMARY KEY (id))''')  # channel_id used to get the channel/guild the user was punished in and the
        # bot can't revert that temporary punishment,
        # e.g. user was tempbanned, but bot no longer has permission to unban -> notify in channel. (not used though lol)
        # guild + channel id information wont show using the "case" command.
        self.bot.db.execute(
            'ALTER TABLE `moderation` CHANGE `reason` `reason` VARCHAR(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL;')
        self.bot.db.execute(
            'ALTER TABLE `moderation` CHANGE `sanctioned_by` `sanctioned_by` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL;')
        self.bot.db.execute(
            'ALTER TABLE `moderation` CHANGE `user` `user` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL;')

    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    @commands.guild_only()
    async def case(self, ctx, id):
        result = self.bot._db._search_by_id(
            self.bot.db, 'moderation', ctx.guild.id, id)
        if not result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No record with that case ID was found.'))
        embed = discord.Embed(description='Action: **{}**\nPunished: **{}** (**{}**)\nSanctioned by: **{}** (**{}**)\nPunished at: **{}**\nPunishment expire: **{}**\nReason: **{}**'.format(
            result[1], result[4], result[5], result[2], result[3], result[6] if not result[6].isdigit(
            ) else datetime.fromtimestamp(int(result[6])),
            result[7] if not result[7].isdigit() else datetime.fromtimestamp(int(result[7])), result[8]), color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
            None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None)
        embed.set_author(name='Case ID: {}'.format(result[0]))
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    @commands.guild_only()
    async def deletecase(self, ctx, _id):
        result = self.bot._db._search_by_id(
            self.bot.db, 'moderation', ctx.guild.id, _id)
        if not result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No record with that case ID was found.'))
        self.bot._db._delete_by_id(self.bot.db, 'moderation', ctx.guild.id, _id)
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Cleared case **{}** from **{}**'.format(result[0], result[4])))

    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    @commands.guild_only()
    async def purgecases(self, ctx):
        result = self.bot._db._get_all_records(self.bot.db, 'moderation', ctx.guild.id)
        if not result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No records were found on this server.'))
        mes = await ctx.send(embed=embeds.Warning._text_to_embed(self.bot, ctx, 'This command will delete all cases of this server and will remove ID bans. Tempmutes and tempbans will become permanent. Are you sure?'),
                             components=[[Button(style=ButtonStyle.green, label='Yes'),
                                          Button(style=ButtonStyle.red, label='No')]])
        while 1:
            try:
                i = await self.bot.wait_for('button_click', timeout=15)
                if not i.author == ctx.author:
                    await i.respond(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Currently only **{}** can perform this action.'.format(ctx.author)))
                else:
                    if i.component.label == 'No':
                        await ctx.message.delete()
                        return await mes.delete()
                    elif i.component.label == 'Yes':
                        self.bot._db._purge_records(self.bot.db, 'moderation', ctx.guild.id)
                        return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Purged **{}** case(s)'.format(len(result))), components=None)
            except asyncio.TimeoutError:
                await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Timed out.'), delete_after=3)
                await mes.delete()
                return await ctx.message.delete()

    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    @commands.guild_only()
    async def clearcases(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        result = self.bot._db._search_by_user_id(self.bot.db,
                                                 'moderation', ctx.guild.id, member.id)
        if not result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No records for that user were found.'))
        self.bot._db._delete_user_records(self.bot.db,
            'moderation', ctx.guild.id, member.id)
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Cleared **{}** case(s) from **{}**'.format(len(result), member)))

    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    @commands.guild_only()
    async def cases(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        result = self.bot._db._search_by_user_id(self.bot.db,
                                                 'moderation', ctx.guild.id, member.id)
        if not result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No records for that user were found.'))
        embed = discord.Embed(description='\n'.join(
            '**Case ID {}**: '.format(str(x[0])) + str(x[1]) for x in result), color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
            None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None)
        embed.set_author(
            name='Total cases: {}'.format(len([x for x in result])))
        await ctx.send(embed=embed)

    @commands.command(aliases=['ara ara~ sayonara'])
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(self, ctx, member: discord.Member, *, reason='N/A'):
        if not member.guild_permissions.administrator and not member.top_role.position >= ctx.guild.me.top_role.position:
            if member == ctx.author:
                return await ctx.send(embed=embeds.Error._text_to_embed('You can\'t ban yourself.'))
            punished_at = int(datetime.now(tz=timezone.utc).timestamp())
            self.bot.db.execute(
                'INSERT INTO moderation(action,sanctioned_by,sanctioned_by_id,user,user_id,punished_at,punished_until,reason,guild_id) VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format('Ban',
                                                                                                                                                                                                    ctx.author.name + '#' +
                                                                                                                                                                                                    str(
                                                                                                                                                                                                        ctx.author.discriminator),
                                                                                                                                                                                                    ctx.author.id,
                                                                                                                                                                                                    member.name + '#' +
                                                                                                                                                                                                    str(
                                                                                                                                                                                                        member.discriminator),
                                                                                                                                                                                                    member.id,
                                                                                                                                                                                                    punished_at,
                                                                                                                                                                                                    'N/A',
                                                                                                                                                                                                    reason,
                                                                                                                                                                                                    ctx.guild.id))
            await member.ban(reason=reason)
            self.bot.db.execute(
                'SELECT id FROM moderation WHERE user_id = {} AND punished_at = {} AND guild_id = {}'.format(member.id, punished_at, ctx.guild.id))
            punishment_id = self.bot.db.fetchone()[0]
            await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Banned **{}**\n\nCase ID: **{}**'.format(member, punishment_id)))
        else:
            await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, ('I have no permission to ban administrators.' if member.guild_permissions.administrator
                                                                             else 'I have no permission to ban users with the same or higher rank.' if member.top_role.position >= ctx.guild.me.top_role.position
                                                                             else 'I have no permission to ban that user.')))

    @commands.command()
    @commands.has_guild_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(kick_members=True)
    @commands.guild_only()
    async def kick(self, ctx, member: discord.Member, *, reason='N/A'):
        if not member.guild_permissions.administrator and not member.top_role.position >= ctx.guild.me.top_role.position:
            if member == ctx.author:
                return await ctx.send(embed=embeds.Error._text_to_embed('You can\'t kick yourself.'))
            punished_at = int(datetime.now(tz=timezone.utc).timestamp())
            self.bot.db.execute(
                'INSERT INTO moderation(action,sanctioned_by,sanctioned_by_id,user,user_id,punished_at,punished_until,reason,guild_id) VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format('Kick',
                                                                                                                                                                                                    ctx.author.name + '#' +
                                                                                                                                                                                                    str(
                                                                                                                                                                                                        ctx.author.discriminator),
                                                                                                                                                                                                    ctx.author.id,
                                                                                                                                                                                                    member.name + '#' +
                                                                                                                                                                                                    str(
                                                                                                                                                                                                        member.discriminator),
                                                                                                                                                                                                    member.id,
                                                                                                                                                                                                    punished_at,
                                                                                                                                                                                                    'N/A',
                                                                                                                                                                                                    reason,
                                                                                                                                                                                                    ctx.guild.id))
            await member.kick(reason=reason)
            self.bot.db.execute(
                'SELECT id FROM moderation WHERE user_id = {} AND punished_at = {} AND guild_id = {}'.format(member.id, punished_at, ctx.guild.id))
            punishment_id = self.bot.db.fetchone()[0]
            await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Kicked **{}**\n\nCase ID: **{}**'.format(member, punishment_id)))
        else:
            await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, ('I have no permission to kick administrators.' if member.guild_permissions.administrator
                                                                             else 'I have no permission to kick users with the same or higher rank.' if member.top_role.position >= ctx.guild.me.top_role.position
                                                                             else 'I have no permission to kick that user.')))

    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.guild_only()
    async def bans(self, ctx):
        bans = []
        banned_users = await ctx.guild.bans()
        for ban_entry in banned_users:
            bans.append(
                '{} (**{}**)'.format(ban_entry.user, ban_entry.user.id))
        if len(bans) == 0:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No banned users were found on this server.'))
        embed = discord.Embed(description='\n'.join(bans), color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None)
        embed.set_author(
            name='Total bans on this server: {}'.format(len(bans)))
        await ctx.send(embed=embed)

    @commands.command(aliases=['pardon'])
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.guild_only()
    async def unban(self, ctx, *, villain):
        banned_users = await ctx.guild.bans()
        if not villain.isdigit():
            for ban_entry in banned_users:
                if str(ban_entry.user) == str(villain):
                    await ctx.guild.unban(ban_entry.user)
                    return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Unbanned **{}**'.format(ban_entry.user)))
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'User **{}** not found.'.format(villain)))
        for ban_entry in banned_users:
            if str(ban_entry.user.id) == str(villain):
                await ctx.guild.unban(ban_entry.user)
                return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Unbanned **{}**'.format(ban_entry.user)))
        return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'User with ID **{}** not found.'.format(villain)))

    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.guild_only()
    async def softban(self, ctx, member: discord.Member, *, reason='N/A'):
        if not member.guild_permissions.administrator and not member.top_role.position >= ctx.guild.me.top_role.position:
            if member == ctx.author:
                return await ctx.send(embed=embeds.Error._text_to_embed('You can\'t ban yourself.'))
            punished_at = int(datetime.now(tz=timezone.utc).timestamp())
            self.bot.db.execute(
                'INSERT INTO moderation(action,sanctioned_by,sanctioned_by_id,user,user_id,punished_at,punished_until,reason,guild_id) VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format('Softban',
                                                                                                                                                                                                    ctx.author.name + '#' +
                                                                                                                                                                                                    str(
                                                                                                                                                                                                        ctx.author.discriminator),
                                                                                                                                                                                                    ctx.author.id,
                                                                                                                                                                                                    member.name + '#' +
                                                                                                                                                                                                    str(
                                                                                                                                                                                                        member.discriminator),
                                                                                                                                                                                                    member.id,
                                                                                                                                                                                                    punished_at,
                                                                                                                                                                                                    'N/A',
                                                                                                                                                                                                    reason,
                                                                                                                                                                                                    ctx.guild.id))
            await member.ban(reason='Softban: {}'.format(reason))
            await member.unban(reason='Softban: {}'.format(reason))
            self.bot.db.execute(
                'SELECT id FROM moderation WHERE user_id = {} AND punished_at = {} AND guild_id = {}'.format(member.id, punished_at, ctx.guild.id))
            punishment_id = self.bot.db.fetchone()[0]
            await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Softbanned **{}**\n\nCase ID: **{}**'.format(member, punishment_id)))
        else:
            await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, ('I have no permission to ban administrators.' if member.guild_permissions.administrator
                                                                             else 'I have no permission to ban users with the same or higher rank.' if member.top_role.position >= ctx.guild.me.top_role.position
                                                                             else 'I have no permission to ban that user.')))

    @commands.command()
    @commands.has_guild_permissions(kick_members=True)
    @commands.guild_only()
    async def warn(self, ctx, member: discord.Member, *, reason=None):
        if not reason:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Please specify a reason.'))
        if not member.guild_permissions.administrator and not member.top_role.position >= ctx.guild.me.top_role.position:
            if member == ctx.author:
                return await ctx.send(embed=embeds.Error._text_to_embed('You can\'t warn yourself.'))
            punished_at = int(datetime.now(tz=timezone.utc).timestamp())
            self.bot.db.execute(
                'INSERT INTO moderation(action,sanctioned_by,sanctioned_by_id,user,user_id,punished_at,punished_until,reason,guild_id) VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format('Warn',
                                                                                                                                                                                                    str(ctx.author.name) + '#' +
                                                                                                                                                                                                    str(
                                                                                                                                                                                                        ctx.author.discriminator),
                                                                                                                                                                                                    ctx.author.id,
                                                                                                                                                                                                    member.name + '#' +
                                                                                                                                                                                                    str(
                                                                                                                                                                                                        member.discriminator),
                                                                                                                                                                                                    member.id,
                                                                                                                                                                                                    punished_at,
                                                                                                                                                                                                    'N/A',
                                                                                                                                                                                                    reason,
                                                                                                                                                                                                    ctx.guild.id))
            self.bot.db.execute(
                'SELECT id FROM moderation WHERE user_id = {} AND punished_at = {} AND guild_id = {}'.format(member.id, punished_at, ctx.guild.id))
            punishment_id = self.bot.db.fetchone()[0]
            warns = self.bot._db._search_by_user_id(self.bot.db,
                                                    'moderation', ctx.guild.id, member.id)
            await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Warned **{}** for **{}**. This user now has **{}** warning(s).\n\nCase ID: **{}**'.format(member, reason, len([x for x in warns if 'Warn' in str(x)]), punishment_id)))
        else:
            await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, ('I can\'t warn administrators.' if member.guild_permissions.administrator
                                                                             else 'I can\'t warn users with the same or higher rank.' if member.top_role.position >= ctx.guild.me.top_role.position
                                                                             else 'I can\'t warn that user.')))

    @commands.command(aliases=['warns'])
    @commands.has_guild_permissions(kick_members=True)
    @commands.guild_only()
    async def warnings(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        if not member.guild_permissions.administrator and not member.top_role.position >= ctx.guild.me.top_role.position:
            warns = self.bot._db._search_by_user_id(self.bot.db,
                                                    'moderation', ctx.guild.id, member.id)
            if not 'Warn' in str(warns):
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This member doesn\'t have any warnings.'))
            embed = discord.Embed(color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                                  None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None)
            embed.set_author(
                name='Total warnings of {}: {}'.format(member, len([x for x in warns if 'Warn' in str(x)])))
            embed.add_field(name='Reasons', value=', '.join(
                '`' + str(x[8]) + '`' for x in warns if 'Warn' in str(x)))
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, ('Administrators can\'t be warned.' if member.guild_permissions.administrator
                                                                             else 'Users with the same or higher rank can\'t be warned.' if member.top_role.position >= ctx.guild.me.top_role.position
                                                                             else 'This user can\'t be warned.')))

    @commands.command(aliases=['clearwarns'])
    @commands.has_guild_permissions(kick_members=True)
    @commands.guild_only()
    async def clearwarnings(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        if not member.guild_permissions.administrator and not member.top_role.position >= ctx.guild.me.top_role.position:
            warns = self.bot._db._search_by_user_id(self.bot.db,
                                                    'moderation', ctx.guild.id, member.id)
            if not 'Warn' in str(warns):
                return await ctx.send(embeds.Error._text_to_embed(self.bot, ctx, 'This user doesn\'t have any warnings.'))
            warn_total = len([x for x in warns if 'Warn' in str(x)])
            self.bot.db.execute('DELETE FROM moderation WHERE user_id = {} AND action = "Warn" AND guild_id = {}'.format(
                member.id, ctx.guild.id))
            await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Cleared **{}** warning(s) from **{}**'.format(warn_total, member)))
        else:
            await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, ('Administrators can\'t be warned.' if member.guild_permissions.administrator
                                                                             else 'Users with the same or higher rank can\'t be warned.' if member.top_role.position >= ctx.guild.me.top_role.position
                                                                             else 'This user can\'t be warned.')))

    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.guild_only()
    async def tempban(self, ctx, member: discord.Member, duration, *, reason='N/A'):
        if not member.guild_permissions.administrator and not member.top_role.position >= ctx.guild.me.top_role.position:
            if member == ctx.author:
                return await ctx.send(embed=embeds.Error._text_to_embed('You can\'t ban yourself.'))
            punished_at = int(datetime.now(tz=timezone.utc).timestamp())
            if not duration.isdigit():
                try:
                    if int(_time._to_seconds(str(duration))) < 30:
                        return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'The ban has to be at least 30s long.'))
                    punished_until = int(
                        datetime.now(tz=timezone.utc).timestamp() + _time._to_seconds(str(duration)))
                except ValueError:
                    return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Bad time given. Please enter the duration like that: **60s**/**60m**/**24h**/**7d**/**4w**/**1y**'))
            else:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Bad time given. Please enter the duration like that: **60s**/**60m**/**24h**/**7d**/**4w**/**1y**'))
            self.bot.db.execute(
                'INSERT INTO moderation(action,sanctioned_by,sanctioned_by_id,user,user_id,punished_at,punished_until,reason,guild_id,channel_id) VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format('Tempban',
                                                                                                                                                                                                                    ctx.author.name + '#' +
                                                                                                                                                                                                                    str(
                                                                                                                                                                                                                        ctx.author.discriminator),
                                                                                                                                                                                                                    ctx.author.id,
                                                                                                                                                                                                                    member.name + '#' +
                                                                                                                                                                                                                    str(
                                                                                                                                                                                                                        member.discriminator),
                                                                                                                                                                                                                    member.id,
                                                                                                                                                                                                                    punished_at,
                                                                                                                                                                                                                    punished_until,
                                                                                                                                                                                                                    reason,
                                                                                                                                                                                                                    ctx.guild.id,
                                                                                                                                                                                                                    ctx.channel.id))
            await member.ban(reason='Tempban: {}'.format(reason))
            self.bot.db.execute(
                'SELECT id FROM moderation WHERE user_id = {} AND punished_at = {} AND guild_id = {}'.format(member.id, punished_at, ctx.guild.id))
            punishment_id = self.bot.db.fetchone()[0]
            await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Tempbanned **{}** for **{}**\n\nCase ID: **{}**'.format(member, duration, punishment_id)))
        else:
            await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, ('I have no permission to ban administrators.' if member.guild_permissions.administrator
                                                                             else 'I have no permission to ban users with the same or higher rank.' if member.top_role.position >= ctx.guild.me.top_role.position
                                                                             else 'I have no permission to ban that user.')))

    @commands.command(aliases=['purge'])
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_guild_permissions(manage_messages=True)
    @commands.guild_only()
    async def clear(self, ctx, limit: int = 1):
        deleted = await ctx.channel.purge(limit=limit+1, check=lambda i: not i.pinned)
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Deleted **{}** message(s)'.format(len(deleted)-1)), delete_after=3)

    @commands.command()
    @commands.has_guild_permissions(manage_channels=True)
    @commands.bot_has_guild_permissions(manage_channels=True)
    @commands.guild_only()
    async def nuke(self, ctx):
        mes = await ctx.send(embed=embeds.Warning._text_to_embed(self.bot, ctx, 'This command will delete and clone this channel to delete all messages. This will also make configs like welcomer useless and they will need to be set up again. Are you sure?'),
                             components=[[Button(style=ButtonStyle.green, label='Yes'),
                                          Button(style=ButtonStyle.red, label='No')]])
        while 1:
            try:
                i = await self.bot.wait_for('button_click', timeout=15)
                if not i.author == ctx.author:
                    await i.respond(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Currently only **{}** can perform this action.'.format(ctx.author)))
                else:
                    if i.component.label == 'No':
                        await ctx.message.delete()
                        return await mes.delete()
                    _pos = ctx.channel.position
                    _clone = await ctx.channel.clone()
                    await ctx.channel.delete()
                    return await _clone.edit(position=_pos)
            except asyncio.TimeoutError:
                await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Timed out.'), delete_after=3)
                await mes.delete()
                return await ctx.message.delete()

    @commands.command(aliases=['shut', 'silence'])
    @commands.bot_has_guild_permissions(manage_roles=True, manage_channels=True)
    @commands.has_guild_permissions(kick_members=True)
    @commands.guild_only()
    async def mute(self, ctx, member: discord.Member, *, reason='N/A'):
        if not member.guild_permissions.administrator and not member.top_role.position >= ctx.guild.me.top_role.position:
            if not 'muted' in [str(x.name).lower() for x in ctx.guild.roles]:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, '**Muted** role was not found.'))
            if 'muted' in [str(x).lower() for x in member.roles]:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This user is already muted.'))
            if member == ctx.author:
                return await ctx.send(embed=embeds.Error._text_to_embed('You can\'t mute yourself.'))
            muted_role = [
                x for x in ctx.guild.roles if 'muted' in str(x.name).lower()][0]
            if muted_role.position > ctx.guild.me.top_role.position:
                return await ctx.send(embed=embeds.Error._text_to_embed('I have no permission to add roles with the same or higher rank to users.'))
            await member.add_roles(muted_role)
            punished_at = int(datetime.now(tz=timezone.utc).timestamp())
            self.bot.db.execute(
                'INSERT INTO moderation(action,sanctioned_by,sanctioned_by_id,user,user_id,punished_at,punished_until,reason,guild_id) VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format('Mute',
                                                                                                                                                                                                    str(ctx.author.name) + '#' +
                                                                                                                                                                                                    str(
                                                                                                                                                                                                        ctx.author.discriminator),
                                                                                                                                                                                                    ctx.author.id,
                                                                                                                                                                                                    member.name + '#' +
                                                                                                                                                                                                    str(
                                                                                                                                                                                                        member.discriminator),
                                                                                                                                                                                                    member.id,
                                                                                                                                                                                                    punished_at,
                                                                                                                                                                                                    'N/A',
                                                                                                                                                                                                    reason,
                                                                                                                                                                                                    ctx.guild.id))
            self.bot.db.execute(
                'SELECT id FROM moderation WHERE user_id = {} AND punished_at = {} AND guild_id = {}'.format(member.id, punished_at, ctx.guild.id))
            punishment_id = self.bot.db.fetchone()[0]
            await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Muted user **{}**\n\nCase ID: **{}**'.format(member, punishment_id)))
        else:
            await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, ('I can\'t mute an administrator.' if member.guild_permissions.administrator
                                                                             else 'I can\'t mute users with the same or higher rank.' if member.top_role.position >= ctx.guild.me.top_role.position
                                                                             else 'I can\'t mute this user.')))

    @commands.command()
    @commands.has_guild_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(manage_roles=True, manage_channels=True)
    @commands.guild_only()
    async def tempmute(self, ctx, member: discord.Member, duration='5m', *, reason='N/A'):
        if not member.guild_permissions.administrator and not member.top_role.position >= ctx.guild.me.top_role.position:
            if not 'muted' in [str(x.name).lower() for x in ctx.guild.roles]:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, '**Muted** role was not found.'))
            if 'muted' in [str(x).lower() for x in member.roles]:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This user is already muted.'))
            if member == ctx.author:
                return await ctx.send(embed=embeds.Error._text_to_embed('You can\'t mute yourself.'))
            muted_role = [
                x for x in ctx.guild.roles if 'muted' in str(x.name).lower()][0]
            if muted_role.position > ctx.guild.me.top_role.position:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx,  'I have no permission to add roles with the same or higher rank to users.'))
            punished_at = int(datetime.now(tz=timezone.utc).timestamp())
            if not duration.isdigit():
                try:
                    if int(_time._to_seconds(str(duration))) < 30:
                        return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'The mute has to be at least 30 seconds.'))
                    punished_until = int(
                        datetime.now(tz=timezone.utc).timestamp() + _time._to_seconds(str(duration)))
                    raw_duration = False
                except ValueError:
                    return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Bad time given. Please enter the duration like that: **60s**/**60m**/**24h**/**7d**/**4w**/**1y**'))
            else:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Bad time given. Please enter the duration like that: **60s**/**60m**/**24h**/**7d**/**4w**/**1y**'))
            await member.add_roles(muted_role)
            try:
                self.bot.db.execute(
                    'INSERT INTO moderation (action,sanctioned_by,sanctioned_by_id,user,user_id,punished_at,punished_until,reason,guild_id,channel_id) VALUES ("{}","{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format('Tempmute',
                                                                                                                                                                                                                          ctx.author.name + '#' +
                                                                                                                                                                                                                          str(
                                                                                                                                                                                                                              ctx.author.discriminator),
                                                                                                                                                                                                                          ctx.author.id,
                                                                                                                                                                                                                          member.name + '#' +
                                                                                                                                                                                                                          str(
                                                                                                                                                                                                                              member.discriminator),
                                                                                                                                                                                                                          member.id,
                                                                                                                                                                                                                          punished_at,
                                                                                                                                                                                                                          punished_until,
                                                                                                                                                                                                                          reason,
                                                                                                                                                                                                                          ctx.guild.id,
                                                                                                                                                                                                                          ctx.channel.id))
            except Exception as e:
                ...
            self.bot.db.execute(
                'SELECT id FROM moderation WHERE user_id = "{}" AND punished_at = "{}" AND guild_id = "{}"'.format(member.id, punished_at, ctx.guild.id))
            punishment_id = self.bot.db.fetchone()[0]
            await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Tempmuted **{}** for **{}**\n\nCase ID: **{}**'.format(member, duration, punishment_id)))
        else:
            await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, ('I have no permission to mute administrators.' if member.guild_permissions.administrator
                                                                             else 'I have no permission to mute users with the same or higher rank.' if member.top_role.position >= ctx.guild.me.top_role.position
                                                                             else 'I have no permission to mute that user.')))

    @commands.command()
    @commands.has_guild_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.guild_only()
    async def unmute(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        if not 'muted' in [str(x.name).lower() for x in ctx.guild.roles]:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, '**Muted** role was not found.'))
        if not 'muted' in [str(x).lower() for x in member.roles]:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This user is not muted.'))
        muted_role = [
            x for x in ctx.guild.roles if 'muted' in str(x.name).lower()][0]
        if muted_role.position > ctx.guild.me.top_role.position:
            return await ctx.send(embed=embeds.Error._text_to_embed('I have no permission to remove roles with the same or higher rank from users.'))
        await member.remove_roles(muted_role)
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Unmuted **{}**'.format(member)))

    @commands.command(aliases=['lock'])
    @commands.guild_only()
    @commands.has_guild_permissions(manage_channels=True)
    @commands.bot_has_guild_permissions(manage_channels=True)
    async def lockdown(self, ctx, channel: discord.TextChannel = None):
        channel = ctx.channel if not channel else channel
        if ctx.guild.default_role not in channel.overwrites:
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(
                    send_messages=False)
            }
            await channel.edit(overwrites=overwrites)
            await channel.send(embed=embeds.Warning._text_to_embed(self.bot, ctx, 'Channel locked.'))
        elif channel.overwrites[ctx.guild.default_role].send_messages == True or channel.overwrites[ctx.guild.default_role].send_messages == None:
            overwrites = channel.overwrites[ctx.guild.default_role]
            overwrites.send_messages = False
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrites)
            await channel.send(embed=embeds.Warning._text_to_embed(self.bot, ctx, 'Channel locked.'))
        else:
            overwrites = channel.overwrites[ctx.guild.default_role]
            overwrites.send_messages = True
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrites)
            await channel.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Channel unlocked'))

    @commands.command()
    @commands.guild_only()
    @commands.has_guild_permissions(manage_channels=True)
    @commands.bot_has_guild_permissions(manage_channels=True)
    async def lockrole(self, ctx, role: discord.Role, channel: discord.TextChannel = None):
        channel = ctx.channel if not channel else channel
        if not role.position >= ctx.guild.me.top_role.position:
            if role not in channel.overwrites:
                overwrites = {
                    role: discord.PermissionOverwrite(
                        send_messages=False)
                }
                await channel.edit(overwrites=overwrites)
                await channel.send(embed=embeds.Warning._text_to_embed(self.bot, ctx, 'Channel locked for **{}**.'.format(role.name)))
            elif channel.overwrites[role].send_messages == True or channel.overwrites[role].send_messages == None:
                overwrites = channel.overwrites[role]
                overwrites.send_messages = False
                await channel.set_permissions(role, overwrite=overwrites)
                await channel.send(embed=embeds.Warning._text_to_embed(self.bot, ctx, 'Channel locked for **{}**.'.format(role.name)))
            else:
                overwrites = channel.overwrites[role]
                overwrites.send_messages = True
                await channel.set_permissions(role, overwrite=overwrites)
                await channel.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Channel unlocked for **{}**'.format(role.name)))
        else:
            await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, ('I can\'t lock roles with the same or higher rank.' if role.position >= ctx.guild.me.top_role.position
                                                                             else 'I can\'t lock this role.')))

    @commands.command()
    @commands.guild_only()
    @commands.has_guild_permissions(manage_channels=True)
    @commands.bot_has_guild_permissions(manage_channels=True)
    async def slowmode(self, ctx, _duration='0s', channel: discord.TextChannel = None):
        channel = ctx.channel if not channel else channel
        if not _duration.isdigit():
            duration = _time._to_seconds(_duration)
            raw_duration = False
        else:
            duration = int(_duration)
            raw_duration = True
        if int(duration) > 2880:  # max: 2880m
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Slowmode can\'t be longer than 48m.'))
        await channel.edit(slowmode_delay=duration)
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, ('Slowmode set to **{}**s'.format(duration)) if raw_duration else 'Slowmode set to **{}**s'.format(duration)))

    @commands.command()
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    @commands.cooldown(1, 300, commands.BucketType.guild)
    async def dm(self, ctx, member: discord.Member, *, message):
        try:
            embed = discord.Embed(description='{}'.format(message), color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                                  None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None, timestamp=ctx.message.created_at)
            embed.set_author(
                name=ctx.author, icon_url=ctx.author.avatar_url, url=ctx.author.avatar_url)
            embed.set_footer(text='Staff DM from {}'.format(ctx.guild.name))
            await member.send(embed=embed)
            await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Sent dm to **{}**'.format(member)))
        except discord.Forbidden:
            await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Couldn\'t send dm to **{}**.'.format(member)))

    @commands.command()
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    @commands.cooldown(1, 300, commands.BucketType.guild)
    async def adm(self, ctx, member: discord.Member, *, message):
        try:
            embed = discord.Embed(description='{}'.format(message), color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                                  None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None, timestamp=ctx.message.created_at)
            embed.set_author(
                name='Anonymous Staff dm from {}'.format(ctx.guild.name), icon_url=ctx.guild.icon_url, url=ctx.guild.icon_url)
            await member.send(embed=embed)
            await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Sent dm to **{}**'.format(member)))
        except discord.Forbidden:
            await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Couldn\'t send dm to **{}**.'.format(member)))

    @commands.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.cooldown(1, 300, commands.BucketType.guild)
    async def unbanall(self, ctx):
        banned_users = await ctx.guild.bans()
        _total_banned_users = len([x for x in banned_users])
        if _total_banned_users == 0:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No banned users were found.'))
        msg = await ctx.send(embed=embeds.Loading._text_to_embed(self.bot, ctx, 'Unbanning **{}** members...'.format(_total_banned_users)))
        for ban_entry in banned_users:
            await ctx.guild.unban(ban_entry.user)
        await msg.edit(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Unbanned **{}** users'.format(_total_banned_users)))

    @commands.command(aliases=['nick'])
    @commands.guild_only()
    @commands.has_guild_permissions(manage_nicknames=True)
    @commands.bot_has_guild_permissions(manage_nicknames=True)
    async def rename(self, ctx, member: discord.Member, *, nick=None):
        nick = str(member.name) if not nick else nick
        if not member.guild_permissions.administrator and not member.top_role.position >= ctx.guild.me.top_role.position:
            if len(str(nick)) > 32:
                return await ctx.send(embed=embeds.Error._text_to_embed('Username can\'t contain more than 32 chacacters.'))
            await member.edit(nick=nick)
            await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Renamed **{}** to **{}**'.format(member, nick)))
        else:
            await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, ('I can\'t rename an administrator.' if member.guild_permissions.administrator
                                                                             else 'I can\'t rename users with the same or higher rank.' if member.top_role.position >= ctx.guild.me.top_role.position
                                                                             else 'I can\'t rename this user.')))

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.has_guild_permissions(ban_members=True)
    async def banid(self, ctx, id, *, reason='N/A'):
        if not id.isdigit():
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'ID must be an integer.'))
        member = discord.utils.find(lambda m: str(
            id) == str(m.id), ctx.guild.members)
        if member:
            if not member.guild_permissions.administrator and not member.top_role.position >= ctx.guild.me.top_role.position:
                if member == ctx.author:
                    return await ctx.send(embed=embeds.Error._text_to_embed('You can\'t ban yourself.'))
            else:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, ('I have no permission to ban administrators.' if member.guild_permissions.administrator
                                                                                        else 'I have no permission to ban users with the same or higher rank.' if member.top_role.position >= ctx.guild.me.top_role.position
                                                                                        else 'I have no permission to ban that user.')))
        try:
            await self.bot.http.ban(id, ctx.guild.id)
        except discord.NotFound:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'That user was not found.'))
        punished_at = int(datetime.now(tz=timezone.utc).timestamp())
        self.bot.db.execute(
            'INSERT INTO moderation(action,sanctioned_by,sanctioned_by_id,user,user_id,punished_at,punished_until,reason,guild_id,channel_id) VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format('ID Ban',
                                                                                                                                                                                                                ctx.author.name + '#' +
                                                                                                                                                                                                                str(
                                                                                                                                                                                                                    ctx.author.discriminator),
                                                                                                                                                                                                                ctx.author.id,
                                                                                                                                                                                                                'N/A',
                                                                                                                                                                                                                id,
                                                                                                                                                                                                                punished_at,
                                                                                                                                                                                                                'N/A',
                                                                                                                                                                                                                reason,
                                                                                                                                                                                                                ctx.guild.id,
                                                                                                                                                                                                                ctx.channel.id))
        self.bot.db.execute(
            'SELECT id FROM moderation WHERE user_id = {} AND punished_at = {} AND guild_id = {}'.format(id, punished_at, ctx.guild.id))
        punishment_id = self.bot.db.fetchone()[0]
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Banned **{}**\n\nCase ID: **{}**'.format(id if not member else member, punishment_id)))

    @commands.command(aliases=['purgeuntil'])
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_guild_permissions(manage_messages=True)
    @commands.guild_only()
    async def clearuntil(self, ctx, message: discord.Message):
        await ctx.message.delete()
        deleted = await ctx.channel.purge(check=lambda i: not i.pinned and not i.created_at.timestamp() < message.created_at.timestamp())
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Deleted **{}** message(s)'.format(len(deleted))), delete_after=3)

    @commands.command(aliases=['purgefromto'])
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_guild_permissions(manage_messages=True)
    @commands.guild_only()
    async def clearfromto(self, ctx, message_from: discord.Message, message_until: discord.Message):
        await ctx.message.delete()
        deleted = await ctx.channel.purge(check=lambda i: not i.pinned and not i.created_at.timestamp() < message_until.created_at.timestamp() and not i.created_at.timestamp() > message_from.created_at.timestamp())
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Deleted **{}** message(s)'.format(len(deleted))), delete_after=3)

    @commands.command(aliases=['purgefrom'])
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_guild_permissions(manage_messages=True)
    @commands.guild_only()
    async def clearfrom(self, ctx, member: discord.Member):
        await ctx.message.delete()
        member = ctx.author if not member else member
        deleted = await ctx.channel.purge(check=lambda m: m.author == member)
        if len(deleted) != 0:
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Deleted **{}** message(s) from **{}**'.format(len(deleted), member.name)), delete_after=3)
        await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Member hasn\'t typed in this chat.'))

    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    @commands.guild_only()
    async def fetchalts(self, ctx, minimum_account_age_in_days: int):
        alts = [m for m in ctx.guild.members if datetime.now(tz=timezone.utc).timestamp() - datetime.fromtimestamp(
            m.created_at.timestamp(), tz=timezone.utc).timestamp() < (minimum_account_age_in_days*86400) and not m.bot]
        if not alts:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No accounts younger than **{}** days were found.'.format(minimum_account_age_in_days)))
        alts = [m.mention + ' (**{}**)'.format(m.id) for m in alts]
        embed = discord.Embed(description='\n'.join(alts), color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None)
        embed.set_author(
            name='Total accounts younger than {} days: {}'.format(minimum_account_age_in_days, len(alts)))
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_guild_permissions(manage_messages=True)
    async def nukefrom(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        _deleted = 0
        async with ctx.typing():
            for channel in ctx.guild.text_channels:
                deleted = await channel.purge(check=lambda m: m.author == member)
                _deleted += len(deleted)
            if _deleted == 0:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Member hasn\'t typed in any chat.'))
            await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Deleted **{}** message(s) from **{}**'.format(_deleted, member.name)), delete_after=3)


def setup(bot):
    bot.add_cog(Moderation(bot))
