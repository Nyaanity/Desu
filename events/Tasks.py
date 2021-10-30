import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime, timezone


class Temp(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        __umc = self.bot._db.db.get_connection()
        self.unmuter_cursor = __umc.cursor(buffered=True)
        self.unmuter.start()

        __ubc = self.bot._db.db.get_connection()
        self.unbanner_cursor = __ubc.cursor(buffered=True)
        self.unbanner.start()

        __ivb = self.bot._db.db.get_connection()
        self.inviteblacklist_cursor = __ivb.cursor(buffered=True)
        self.inviteblacklist.start()

        __vtr = self.bot._db.db.get_connection()
        self.voicetimerecorder_cursor = __vtr.cursor(buffered=True)
        self.voicetimerecorder.start()

        __wlr = self.bot._db.db.get_connection()
        self.warnlimiter_cursor = __wlr.cursor(buffered=True)
        self.warnlimiter.start()

        __atp = self.bot._db.db.get_connection()
        self.autopurge_cursor = __atp.cursor(buffered=True)
        self.autopurge.start()

        self.bot.db.execute('''CREATE TABLE IF NOT EXISTS voicetimerecorder(
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            guild_id TEXT,
            user_id TEXT,
            total_time_spent TEXT,
            first_time_joined_vc TEXT,
                PRIMARY KEY (id))''')

    @tasks.loop()
    async def voicetimerecorder(self):
        _users = [[[user for user in channel.members if not user.bot]
                   for channel in guild.voice_channels] for guild in self.bot.guilds]
        for users in _users:
            for inmate in users:
                try:
                    self.voicetimerecorder_cursor.execute('SELECT total_time_spent FROM voicetimerecorder WHERE guild_id = "{}" AND user_id = "{}"'.format(
                        inmate[0].guild.id, inmate[0].id))
                    result = self.voicetimerecorder_cursor.fetchone()
                    if not result:
                        self.voicetimerecorder_cursor.execute('INSERT INTO voicetimerecorder(guild_id,user_id,total_time_spent,first_time_joined_vc) VALUES ("{}","{}","{}","{}")'.format(
                            inmate[0].guild.id, inmate[0].id, 0, int(datetime.now(tz=timezone.utc).timestamp())))
                        continue
                    self.voicetimerecorder_cursor.execute('UPDATE voicetimerecorder SET total_time_spent = "{}" WHERE guild_id = "{}" AND user_id = "{}"'.format(
                        int(result[0])+30, inmate[0].guild.id, inmate[0].id))
                except:
                    continue
        await asyncio.sleep(60)

    @voicetimerecorder.before_loop
    async def before_voicetimerecorder(self):
        await self.bot.wait_until_ready()

    @tasks.loop()
    async def unmuter(self):
        for guild in self.bot.guilds:
            villains = [member for member in guild.members if str(member.id) in str(
                self.bot._db._search_by_user_id(self.unmuter_cursor, 'moderation', guild.id, member.id))]
            if villains != []:
                villains = [self.bot._db._search_by_user_id(self.unmuter_cursor, 'moderation', guild.id, villain.id)[
                    0] for villain in villains]
                for villain in villains:
                    if str(villain[1]) == 'Tempmute' and (int(villain[7]) < int(datetime.now(tz=timezone.utc).timestamp())):
                        if not guild.me.guild_permissions.manage_roles:
                            self.bot._db._delete_by_id(self.unmuter_cursor,
                                                       'moderation', guild.id, villain[0])
                            continue
                        muted_member = discord.utils.find(
                            lambda m: str(m.id) == str(villain[5]), guild.members)
                        if not muted_member:
                            self.bot._db._delete_by_id(self.unmuter_cursor,
                                                       'moderation', guild.id, villain[0])
                            continue
                        muted_role = discord.utils.find(
                            lambda m: 'muted' in str(m.name).lower(), guild.roles)
                        if not muted_role:
                            self.bot._db._delete_by_id(self.unmuter_cursor,
                                                       'moderation', guild.id, villain[0])
                            continue
                        if not muted_role in muted_member.roles:
                            self.bot._db._delete_by_id(self.unmuter_cursor,
                                                       'moderation', guild.id, villain[0])
                            continue
                        await muted_member.remove_roles(muted_role, reason='Tempmute expired')
                        self.bot._db._delete_by_id(self.unmuter_cursor,
                                                   'moderation', guild.id, villain[0])
            await asyncio.sleep(0.001)
        await asyncio.sleep(60)

    @unmuter.before_loop
    async def before_unmuter(self):
        await self.bot.wait_until_ready()

    @tasks.loop()
    async def unbanner(self):
        for guild in self.bot.guilds:
            if guild.me.guild_permissions.ban_members:
                self.unbanner_cursor.execute(
                    'SELECT * FROM moderation WHERE guild_id = "{}" AND action = "{}"'.format(guild.id, 'Tempban'))
                villains = self.unbanner_cursor.fetchall()
                if villains != []:
                    for villain in villains:
                        if (int(villain[7]) < int(datetime.now(tz=timezone.utc).timestamp())):
                            banned_users = await guild.bans()
                            if banned_users:
                                for ban_entry in banned_users:
                                    if str(ban_entry.user.id) == str(villain[5]):
                                        await guild.unban(ban_entry.user, reason='Tempban expired')
                                        self.bot._db._delete_by_id(
                                            'moderation', guild.id, villain[0])
                            self.bot._db._delete_by_id(
                                'moderation', guild.id, villain[0])
            await asyncio.sleep(0.001)
        await asyncio.sleep(60)

    @unbanner.before_loop
    async def before_unbanner(self):
        await self.bot.wait_until_ready()

    @tasks.loop()
    async def inviteblacklist(self):
        for guild in self.bot.guilds:
            self.inviteblacklist_cursor.execute('SELECT user_id FROM moderation WHERE guild_id = "{}" AND action = "{}"'.format(
                guild.id, 'Invite Blacklist'))
            villains = self.inviteblacklist_cursor.fetchall()
            if villains != []:
                for villain in villains:
                    self.inviteblacklist_cursor.execute('DELETE FROM invites WHERE guild_id = "{}" AND inviter_id = "{}"'.format(
                        guild.id, villain[0]))
                    self.inviteblacklist_cursor.execute('UPDATE invitestats SET total = "{}", regular = "{}", leaves = "{}", fake = "{}", bonus = "{}", removed = "{}" WHERE guild_id = "{}" AND member_id = "{}"'.format(
                        0, 0, 0, 0, 0, 0,
                        guild.id, villain[0]
                    ))
            await asyncio.sleep(0.001)
        await asyncio.sleep(60)

    @inviteblacklist.before_loop
    async def before_inviteblacklist(self):
        await self.bot.wait_until_ready()

    @tasks.loop()
    async def warnlimiter(self):
        for guild in self.bot.guilds:
            self.warnlimiter_cursor.execute('SELECT user_id FROM moderation WHERE guild_id = "{}" AND action = "{}"'.format(
                guild.id, 'Warn'))
            villains = self.warnlimiter_cursor.fetchall()
            self.warnlimiter_cursor.execute(
                'SELECT * FROM maxinfractions WHERE guild_id = "{}"'.format(guild.id))
            infractions = self.warnlimiter_cursor.fetchone()
            if villains != [] and infractions:
                if str(infractions[2]) == '0' or str(infractions[2]) == 'N/A' or str(infractions[3]) == 'N/A':
                    continue
                for villain in villains:
                    self.warnlimiter_cursor.execute('SELECT * FROM moderation WHERE guild_id = "{}" AND action = "{}" AND user_id = "{}"'.format(
                        guild.id, 'Warn', villain[0]))
                    warns = self.warnlimiter_cursor.fetchall()
                    if not warns:
                        continue
                    if len(warns) >= int(infractions[2]):
                        if str(infractions[3]) == 'kick':
                            if guild.me.guild_permissions.kick_members:
                                member = discord.utils.find(lambda m: str(
                                    m.id) == str(villain[0]), guild.members)
                                if not member:
                                    continue
                                if not member.guild_permissions.administrator and not member.top_role.position >= guild.me.top_role.position:
                                    punished_at = int(datetime.now(
                                        tz=timezone.utc).timestamp())
                                    self.warnlimiter_cursor.execute(
                                        'INSERT INTO moderation(action,sanctioned_by,sanctioned_by_id,user,user_id,punished_at,punished_until,reason,guild_id) VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format('Kick',
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
                                                                                                                                                                                                                            'Reached max warn limit {}'.format(
                                                                                                                                                                                                                                infractions[2]),
                                                                                                                                                                                                                            guild.id))
                                    self.warnlimiter_cursor.execute('DELETE FROM moderation WHERE guild_id = "{}" AND user_id = "{}" AND action = "{}"'.format(
                                        guild.id, member.id, 'Warn'))  # clears warns so the member can rejoin if possible.
                                    await member.kick(reason='Reached max warn limit {}'.format(infractions[2]))
                        elif str(infractions[3]) == 'ban':
                            if guild.me.guild_permissions.ban_members:
                                member = discord.utils.find(lambda m: str(
                                    m.id) == str(villain[0]), guild.members)
                                if not member:
                                    continue
                                if not member.guild_permissions.administrator and not member.top_role.position >= guild.me.top_role.position:
                                    punished_at = int(datetime.now(
                                        tz=timezone.utc).timestamp())
                                    self.warnlimiter_cursor.execute(
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
                                                                                                                                                                                                                            'Reached max warn limit {}'.format(
                                                                                                                                                                                                                                infractions[2]),
                                                                                                                                                                                                                            guild.id))
                                    self.warnlimiter_cursor.execute('DELETE FROM moderation WHERE guild_id = "{}" AND user_id = "{}" AND action = "{}"'.format(
                                        guild.id, member.id, 'Warn'))  # clears warns so the member can rejoin if possible.
                                    await member.ban(reason='Reached max warn limit {}'.format(infractions[2]))
                        elif str(infractions[3]) == 'mute':
                            if guild.me.guild_permissions.manage_roles:
                                member = discord.utils.find(lambda m: str(
                                    m.id) == str(villain[0]), guild.members)
                                if not member:
                                    continue
                                if not member.guild_permissions.administrator and not member.top_role.position >= guild.me.top_role.position:
                                    if not 'muted' in [str(x.name).lower() for x in guild.roles]:
                                        continue
                                    if 'muted' in [str(x).lower() for x in member.roles]:
                                        continue
                                    muted_role = [
                                        x for x in guild.roles if 'muted' in str(x.name).lower()][0]
                                    if muted_role.position > guild.me.top_role.position:
                                        continue
                                    punished_at = int(datetime.now(
                                        tz=timezone.utc).timestamp())
                                    self.warnlimiter_cursor.execute(
                                        'INSERT INTO moderation(action,sanctioned_by,sanctioned_by_id,user,user_id,punished_at,punished_until,reason,guild_id) VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format('Mute',
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
                                                                                                                                                                                                                            'Reached max warn limit {}'.format(
                                                                                                                                                                                                                                infractions[2]),
                                                                                                                                                                                                                            guild.id))
                                    self.warnlimiter_cursor.execute('DELETE FROM moderation WHERE guild_id = "{}" AND user_id = "{}" AND action = "{}"'.format(
                                        guild.id, member.id, 'Warn'))  # clears warns so the member can rejoin if possible.
                                    await member.add_roles(muted_role, reason='Reached max warn limit {}'.format(infractions[2]))
            await asyncio.sleep(0.001)
        await asyncio.sleep(10)

    @warnlimiter.before_loop
    async def before_warnlimiter(self):
        await self.bot.wait_until_ready()

    @tasks.loop()
    async def autopurge(self):
        for guild in self.bot.guilds:
            if not guild.me.guild_permissions.manage_messages:
                continue
            self.autopurge_cursor.execute(
                'SELECT * FROM autopurge WHERE guild_id = "{}"'.format(guild.id))
            result = self.autopurge_cursor.fetchone()
            if not result:
                continue
            if str(result[1]) != '1' or str(result[2]) == 'N/A' or str(result[4]) == 'N/A' or str(result[5]) == 'N/A':
                continue
            channel = self.bot.get_channel(int(result[2]))
            if not channel:
                continue
            if (datetime.now(tz=timezone.utc).timestamp()) > (int(result[4]) + float(result[5])):
                await channel.purge(check=lambda m: not m.pinned)
                self.autopurge_cursor.execute('UPDATE autopurge SET next_purge_at = "{}" WHERE guild_id = "{}"'.format(
                    datetime.now(tz=timezone.utc).timestamp() + int(result[4]), guild.id))
            await asyncio.sleep(0.001)
        await asyncio.sleep(60)

    @autopurge.before_loop
    async def before_autopurge(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Temp(bot))
