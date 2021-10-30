import discord
from discord.ext import commands
from datetime import datetime, timezone
from __bot.embeds import Embeds as embeds


class InviteTracer(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.invite_cache = {}
        self.bot.db.execute('''CREATE TABLE IF NOT EXISTS invites(
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            guild_id TEXT,
            inviter_id TEXT,
            invited_id TEXT,
            fake TEXT,
            bonus TEXT,
            code TEXT,
            invited_at TEXT,
                PRIMARY KEY (id))''')
        self.bot.db.execute('''CREATE TABLE IF NOT EXISTS invitestats(
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            guild_id TEXT,
            member_id TEXT,
            total TEXT,
            regular TEXT,
            leaves TEXT,
            fake TEXT,
            bonus TEXT,
            removed TEXT,
                PRIMARY KEY (id))''')
        self.bot.db.execute('''CREATE TABLE IF NOT EXISTS invitebackup(
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            guild_id TEXT,
            member_id TEXT,
            total TEXT,
            regular TEXT,
            leaves TEXT,
            fake TEXT,
            bonus TEXT,
            backed_up_at TEXT,
            removed TEXT,
                PRIMARY KEY (id))''')
        self.bot.db.execute('''CREATE TABLE IF NOT EXISTS invitesbackup(
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            guild_id TEXT,
            inviter_id TEXT,
            invited_id TEXT,
            fake TEXT,
            bonus TEXT,
            backed_up_at TEXT,
            code TEXT,
            invited_at TEXT,
                PRIMARY KEY (id))''')

    async def fetch_user_invites(self, member):
        """
        Gets a members total invites, regulars, leaves, fakes, and bonuses as a json object.
        """
        self.bot.db.execute(
            'SELECT * FROM invitestats WHERE guild_id = "{}" AND member_id = "{}"'.format(member.guild.id, member.id))
        result = self.bot.db.fetchone()
        if not result:
            total, regular, leaves, fake, bonus, removed = 0, 0, 0, 0, 0, 0
        else:
            total, regular, leaves, fake, bonus, removed = result[
                3], result[4], result[5], result[6], result[7], result[8]
        return {'total': total, 'regular': regular, 'leaves': leaves, 'fake': fake, 'bonus': bonus, 'removed': removed}

    async def fetch_uses(self, guild, invite):
        """
        Gets total uses of an invite.
        """
        invites = await guild.invites()
        for _invite in invites:
            if _invite == invite:
                return int(_invite.uses)

    async def fetch_inviter(self, guild, invite):
        """
        Gets inviter object as a user object.
        """
        invites = await guild.invites()
        for _invite in invites:
            if _invite == invite:
                return _invite.inviter

    async def fetch_by_code(self, inv_list, code):
        """
        Gets an invite object by code.
        """
        for invite in inv_list:
            if str(invite.code) == str(code):
                return invite

    async def fetch_updated_invite(self, guild, invites_before, invites_after):
        """
        Get the updated (used) invite object.
        """
        for invite in invites_before:
            if invite.uses < (await self.fetch_by_code(invites_after, invite.code)).uses:
                return invite

    @commands.Cog.listener()
    async def on_ready(self):
        guilds = [
            guild for guild in self.bot.guilds if guild.me.guild_permissions.manage_guild]
        for guild in guilds:
            self.invite_cache[guild.id] = await guild.invites()

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        if invite.guild.me.guild_permissions.manage_guild:
            self.invite_cache[invite.guild.id] = await invite.guild.invites()

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        if invite.guild.me.guild_permissions.manage_guild:
            self.invite_cache[invite.guild.id] = await invite.guild.invites()

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        self.bot.db.execute('SELECT inviter_id FROM invites WHERE guild_id = "{}" AND invited_id = "{}"'.format(
            member.guild.id, member.id))
        result = self.bot.db.fetchall()
        if not result:
            return
        for inviter in result:
            self.bot.db.execute('SELECT total, leaves FROM invitestats WHERE guild_id = "{}" AND member_id = "{}"'.format(
                member.guild.id, inviter[0]))
            stats = self.bot.db.fetchone()
            if not stats:
                self.bot.db.execute('INSERT INTO invitestats (guild_id,member_id,total,regular,leaves,fake,bonus) VALUES ("{}","{}","{}","{}","{}","{}","{}")'.format(
                    member.guild.id, inviter[0], 0, 1, 1, 0, 0
                ))
            else:
                self.bot.db.execute('UPDATE invitestats SET total = "{}", leaves = "{}" WHERE guild_id = "{}" AND member_id = "{}"'.format(
                    int(stats[0])-1 if int(stats[0]) > 0 else 0, int(stats[1]) + 1, member.guild.id, inviter[0]))
        self.bot.db.execute(
            'DELETE FROM invites WHERE invited_id = "{}"'.format(member.id))
        if member.guild.me.guild_permissions.manage_guild:
            self.invite_cache[member.guild.id] = await member.guild.invites()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        joined_at = int(datetime.now(tz=timezone.utc).timestamp())
        try:
            if member.bot:
                return
            if not member.guild.me.guild_permissions.manage_guild:
                return
            invite = await self.fetch_updated_invite(member.guild, self.invite_cache[member.guild.id], await member.guild.invites())
            if invite.inviter == member:
                self.bot.db.execute(
                    'SELECT fakes FROM invitestats WHERE guild_id = "{}" AND member_id = "{}"'.format(member.guild.id, invite.inviter.id))
                stats = self.bot.db.fetchone()
                if not stats:
                    self.bot.db.execute('INSERT INTO invitestats (guild_id,member_id,total,regular,leaves,fake,bonus,removed) VALUES ("{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format(
                        member.guild.id, invite.inviter.id, 0, 0, 0, 1, 0, 0
                    ))
                else:
                    self.bot.db.execute('UPDATE invitestats SET fakes = "{}" WHERE guild_id = "{}" AND member_id = "{}"'.format(
                        int(stats[0]) + 1, member.guild.id, invite.inviter.id))
                return self.bot.db.execute('INSERT INTO invites (guild_id,inviter_id,invited_id,fake,bonus,code,invited_at) VALUES("{}","{}","{}","{}","{}","{}","{}")'.format(
                    member.guild.id, invite.inviter.id, member.id, 1, 0, invite.code, joined_at))
            self.bot.db.execute('INSERT INTO invites (guild_id,inviter_id,invited_id,fake,bonus,code,invited_at) VALUES ("{}","{}","{}","{}","{}","{}","{}")'.format(
                member.guild.id, invite.inviter.id, member.id, 0, 0, invite.code, joined_at))
            self.bot.db.execute(
                'SELECT total, regular FROM invitestats WHERE guild_id = "{}" AND member_id = "{}"'.format(member.guild.id, invite.inviter.id))
            stats = self.bot.db.fetchone()
            if not stats:
                self.bot.db.execute('INSERT INTO invitestats (guild_id,member_id,total,regular,leaves,fake,bonus,removed) VALUES ("{}","{}","{}","{}","{}","{}","{}","{}")'.format(
                    member.guild.id, invite.inviter.id, 1, 1, 0, 0, 0, 0
                ))
            else:
                self.bot.db.execute('UPDATE invitestats SET total = "{}", regular = "{}" WHERE guild_id = "{}" AND member_id = "{}"'.format(
                    int(stats[0]) + 1, int(stats[1]) + 1, member.guild.id, invite.inviter.id))
            self.invite_cache[invite.guild.id] = await invite.guild.invites()
        except:
            return

    @commands.command()
    @commands.guild_only()
    async def invites(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        invites = await self.fetch_user_invites(member)
        embed = discord.Embed(description='**{}** total invites. (**{}** regular, **{}** leaves, **{}** fake, **{}** bonus, **{}** removed)'.format(invites['total'], invites['regular'], invites['leaves'], invites['fake'], invites['bonus'], invites['removed']), color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None)
        embed.set_author(
            name=member, icon_url=member.avatar_url, url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=['addinvites', '+invites'])
    @commands.has_guild_permissions(administrator=True)
    @commands.guild_only()
    async def giveinvites(self, ctx, member: discord.Member = None, amount: int = 1):
        member = ctx.author if not member else member
        self.bot.db.execute(
            'SELECT * FROM invitestats WHERE guild_id = "{}" AND member_id = "{}"'.format(member.guild.id, member.id))
        result = self.bot.db.fetchone()
        if not result:
            self.bot.db.execute('INSERT INTO invitestats (guild_id,member_id,total,regular,leaves,fake,bonus,removed) VALUES ("{}","{}","{}","{}","{}","{}","{}","{}")'.format(
                member.guild.id, member.id, amount, 0, 0, 0, amount, 0
            ))
        elif result:
            self.bot.db.execute('UPDATE invitestats SET bonus = "{}", total = "{}" WHERE guild_id = "{}" AND member_id = "{}"'.format(
                int(result[7]) + amount,
                int(result[3]) + amount,
                ctx.guild.id, member.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Added **{}** invite(s) to **{}**'.format(amount, member)))

    @commands.command(aliases=['reminvites', '-invites'])
    @commands.has_guild_permissions(administrator=True)
    @commands.guild_only()
    async def removeinvites(self, ctx, amount: int = 1, member: discord.Member = None):
        member = ctx.author if not member else member
        self.bot.db.execute(
            'SELECT * FROM invitestats WHERE guild_id = "{}" AND member_id = "{}"'.format(member.guild.id, member.id))
        result = self.bot.db.fetchone()
        if not result:
            self.bot.db.execute('INSERT INTO invitestats (guild_id,member_id,total,regular,leaves,fake,bonus,removed) VALUES ("{}","{}","{}","{}","{}","{}","{}","{}")'.format(
                member.guild.id, member.id, 0, 0, 0, 0, 0, 0
            ))
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No invites to remove were found.'))
        elif result:
            if int(result[1]) > 0:
                self.bot.db.execute('UPDATE invitestats SET total = "{}", regular = "{}", leaves = "{}", fake = "{}", bonus = "{}", removed = "{}" WHERE guild_id = "{}" AND member_id = "{}"'.format(
                    int(result[3]) -
                    amount if int(int(result[3]) - amount) > 0 else 0,
                    int(result[4]) -
                    amount if int(int(result[4]) - amount) > 0 else 0,
                    int(result[5]) -
                    amount if int(int(result[5]) - amount) > 0 else 0,
                    int(result[6]) - amount if int(int(result[6]
                                                       ) - amount) > 0 else 0,
                    int(result[7]) -
                    amount if int(int(result[7]) - amount) > 0 else 0,
                    int(result[8]) +
                    amount if int(int(result[8]) + amount) > 0 else 0,
                    ctx.guild.id, member.id))
                return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Removed **{}** invite(s) from **{}**'.format(amount, member)))
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No invites to remove were found.'))

    @commands.command(aliases=['remallinvites', '-allinvites'])
    @commands.has_guild_permissions(administrator=True)
    @commands.guild_only()
    async def removeallinvites(self, ctx):
        total = 0
        backed_up_at = datetime.now(tz=timezone.utc).timestamp()
        self.bot.db.execute(
            'SELECT * FROM invitestats WHERE guild_id = "{}"'.format(ctx.guild.id))
        invitestats = self.bot.db.fetchall()
        if len(invitestats) == 0:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No invites to remove were found.'))
        self.bot.db.execute(
            'SELECT * FROM invites WHERE guild_id = "{}"'.format(ctx.guild.id))
        invites = self.bot.db.fetchall()
        self.bot.db.execute(
            'DELETE FROM invitebackup WHERE guild_id = "{}"'.format(ctx.guild.id))
        self.bot.db.execute(
            'DELETE FROM invitesbackup WHERE guild_id = "{}"'.format(ctx.guild.id))
        for record in invitestats:
            total += int(record[3])
        for record in invitestats:
            self.bot.db.execute(
                'INSERT INTO invitebackup (guild_id,member_id,total,regular,leaves,fake,bonus,backed_up_at,removed) VALUES ("{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format(
                    ctx.guild.id, record[2], record[3], record[4], record[5], record[6], record[7], backed_up_at.strftime(
                        '%a, %b %d, %Y %I:%M %p'), record[8]
                ))
        for record in invites:
            self.bot.db.execute(
                'INSERT INTO invitesbackup (guild_id,inviter_id,invited_id,fake,bonus,backed_up_at,code,invited_at) VALUES ("{}","{}","{}","{}","{}","{}")'.format(
                    ctx.guild.id, record[2], record[3], record[4], record[5], backed_up_at.strftime(
                        '%a, %b %d, %Y %I:%M %p'), record[6], record[7]
                ))
        self.bot.db.execute(
            'DELETE FROM invitestats WHERE guild_id = "{}"'.format(ctx.guild.id))
        self.bot.db.execute(
            'DELETE FROM invites WHERE guild_id = "{}"'.format(ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Deleted **{}** total invite(s)'.format(total)))

    @commands.command(aliases=['recoverinvites'])
    @commands.has_guild_permissions(administrator=True)
    @commands.guild_only()
    async def restoreinvites(self, ctx):
        total = 0
        self.bot.db.execute(
            'SELECT * FROM invitebackup WHERE guild_id = "{}"'.format(ctx.guild.id))
        binvitestats = self.bot.db.fetchall()
        if len(binvitestats) == 0:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No invites to backup were found.'))
        self.bot.db.execute(
            'SELECT * FROM invitesbackup WHERE guild_id = "{}"'.format(ctx.guild.id))
        binvites = self.bot.db.fetchall()
        self.bot.db.execute(
            'DELETE FROM invitestats WHERE guild_id = "{}"'.format(ctx.guild.id))
        self.bot.db.execute(
            'DELETE FROM invites WHERE guild_id = "{}"'.format(ctx.guild.id))
        for record in binvitestats:
            total += int(record[3])
        for record in binvitestats:
            self.bot.db.execute(
                'INSERT INTO invitestats (guild_id,member_id,total,regular,leaves,fake,bonus,removed) VALUES ("{}","{}","{}","{}","{}","{}","{}","{}")'.format(
                    ctx.guild.id, record[2], record[3], record[4], record[5], record[6], record[7], record[8]
                ))
            backed_up_at = record[8]
        for record in binvites:
            self.bot.db.execute(
                'INSERT INTO invites (guild_id,inviter_id,invited_id,fake,bonus,code,invited_at) VALUES ("{}","{}","{}","{}","{}","{}","{}")'.format(
                    ctx.guild.id, record[2], record[3], record[4], record[5], record[6], record[7]
                ))
        self.bot.db.execute(
            'DELETE FROM invitebackup WHERE guild_id = "{}"'.format(ctx.guild.id))
        self.bot.db.execute(
            'DELETE FROM invitesbackup WHERE guild_id = "{}"'.format(ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Restored **{}** total invite(s) that were backed up at **{}**'.format(total, backed_up_at)))

    @commands.command(aliases=['purgeinvites'])
    @commands.has_guild_permissions(administrator=True)
    @commands.guild_only()
    async def clearinvites(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        self.bot.db.execute(
            'SELECT * FROM invitestats WHERE guild_id = "{}" AND member_id = "{}"'.format(member.guild.id, member.id))
        result = self.bot.db.fetchone()
        if not result:
            self.bot.db.execute('INSERT INTO invitestats (guild_id,member_id,total,regular,leaves,fake,bonus,removed) VALUES ("{}","{}","{}","{}","{}","{}","{}","{}")'.format(
                member.guild.id, member.id, 0, 0, 0, 0, 0
            ))
            return await ctx.send(embed=embeds.Error._text_to_embed('No invites to remove were found.'))
        elif result:
            self.bot.db.execute('DELETE FROM invitestats WHERE guild_id = "{}" AND member_id = "{}"'.format(
                ctx.guild.id, member.id))
            self.bot.db.execute('DELETE FROM invites WHERE guild_id = "{}" AND inviter_id = "{}"'.format(
                ctx.guild.id, member.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Cleared **{}** invite(s) from **{}**'.format(result[3], member)))

    @commands.command()
    @commands.guild_only()
    async def inviter(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        self.bot.db.execute(
            'SELECT * FROM invites WHERE guild_id = "{}" AND invited_id = "{}"'.format(ctx.guild.id, member.id))
        result = self.bot.db.fetchone()
        if not result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Coudn\'t find any invite records from that user.'))
        invited_by = discord.utils.find(lambda m: str(
            m.id) == str(result[2]), ctx.guild.members)
        embed = discord.Embed(description='**Invite ID**: {}\n**Invited by**: {}\n**Code**: {}\n**Invited at**: {}'.format(
            result[0],
            result[0] if not invited_by else invited_by.mention,
            result[6], str(datetime.fromtimestamp(float(result[7])).strftime('%a, %b %d, %Y %I:%M %p'))), color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
            None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None)
        embed.set_author(
            name=member, icon_url=member.avatar_url, url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def invitedlist(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        self.bot.db.execute(
            'SELECT * FROM invites WHERE guild_id = "{}" AND inviter_id = "{}"'.format(ctx.guild.id, member.id))
        result = self.bot.db.fetchall()
        if not result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Coudn\'t find any invite records for that user.'))
        embed = discord.Embed(description='\n'.join(['**Invite ID {}**: Invited {}'.format(
            invite[0], invite[3] if not discord.utils.find(lambda m: str(m.id) == str(invite[3]), ctx.guild.members) else (discord.utils.find(lambda m: str(m.id) == str(invite[3]), ctx.guild.members)).mention) for invite in result]), color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
            None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None)
        embed.set_author(
            name=member, icon_url=member.avatar_url, url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_guild=True)
    @commands.has_guild_permissions(ban_members=True)
    async def invitecodes(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        _invites = []
        invites = await ctx.guild.invites()
        for invite in invites:
            if invite.inviter == member:
                _invites.append(invite)
        if len(_invites) == 0:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No invites for that user were found.'))
        embed = discord.Embed(description='\n'.join(['**Invite Code**: {}'.format(invite.code) for invite in _invites]), color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None)
        embed.set_author(
            name=member, icon_url=member.avatar_url, url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_guild=True)
    @commands.has_guild_permissions(ban_members=True)
    async def allinvitecodes(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        invites = await ctx.guild.invites()
        if not invites:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No invites for this server were found.'))
        embed = discord.Embed(description='\n'.join(['{}: {}'.format(invite.inviter.mention, invite.code) for invite in invites]), color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None)
        embed.set_author(
            name='Total invite codes: {}'.format(len(invites)))
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    @commands.bot_has_guild_permissions(manage_channels=True, manage_guild=True)
    async def nukeinvites(self, ctx):
        invites = await ctx.guild.invites()
        if not invites:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No active invite codes were found on this server.'))
        for invite in invites:
            await invite.delete()
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Deleted **{}** active invite(s)'.format(len(invites))))

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def inviteblacklist(self, ctx):
        prefix = self.bot.config._get_prefix(self.bot, ctx)
        embed = discord.Embed(title='Invite Blacklist',
                              description=f"**<>** = required\n**[]** = optional",
                              color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None,
                              timestamp=ctx.message.created_at)
        embed.add_field(
            name='Add a user to the blacklist', value='`{}inviteblacklist add <member>`'.format(prefix))
        embed.add_field(
            name='List all blacklisted users', value='`{}inviteblacklist list`'.format(prefix))
        embed.add_field(
            name='Remove a user from the blacklist', value='`{}inviteblacklist remove <member>`'.format(prefix))
        await ctx.send(embed=embed)

    @inviteblacklist.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def add(self, ctx, member: discord.Member, *, reason='N/A'):
        if not member.guild_permissions.administrator and not member.top_role.position >= ctx.guild.me.top_role.position:
            if member == ctx.author:
                return await ctx.send(embed=embeds.Error._text_to_embed('You can\'t blacklist yourself.'))
            self.bot.db.execute('SELECT * FROM moderation WHERE action = "{}" AND user_id = "{}"'.format(
                'Invite Blacklist', member.id))
            result = self.bot.db.fetchone()
            if result:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This user is already blacklisted.'))
            punished_at = int(datetime.now(tz=timezone.utc).timestamp())
            self.bot.db.execute(
                'INSERT INTO moderation(action,sanctioned_by,sanctioned_by_id,user,user_id,punished_at,punished_until,reason,guild_id) VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format('Invite Blacklist',
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
            self.bot.db.execute(
                'SELECT id FROM moderation WHERE user_id = {} AND punished_at = {} AND guild_id = {}'.format(member.id, punished_at, ctx.guild.id))
            punishment_id = self.bot.db.fetchone()[0]
            await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Blacklisted **{}** from invites\n\nCase ID: **{}**'.format(member, punishment_id)))
        else:
            await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, ('I have no permission to blacklist administrators.' if member.guild_permissions.administrator
                                                                             else 'I have no permission to blacklist users with the same or higher rank.' if member.top_role.position >= ctx.guild.me.top_role.position
                                                                             else 'I have no permission to blacklist that user.')))

    @inviteblacklist.command(name='list')
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    async def _list(self, ctx):
        self.bot.db.execute('SELECT * FROM moderation WHERE action = "{}"'.format(
            'Invite Blacklist'))
        blacklists = self.bot.db.fetchall()
        if not blacklists:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'There are no blacklists on this server.'))
        embed = discord.Embed(description='\n'.join([('**Case ID**: {}'.format(blacklist[0]) if not discord.utils.find(lambda m: str(m.id) == str(blacklist[5]), ctx.guild.members) else (discord.utils.find(lambda m: str(m.id) == str(blacklist[5]), ctx.guild.members)).mention) for blacklist in blacklists]), color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None)
        embed.set_author(
            name='Total blacklists on this server: {}'.format(len(blacklists)))
        await ctx.send(embed=embed)

    @inviteblacklist.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def remove(self, ctx, member: discord.Member, *, reason='N/A'):
        if not member.guild_permissions.administrator and not member.top_role.position >= ctx.guild.me.top_role.position:
            if member == ctx.author:
                return await ctx.send(embed=embeds.Error._text_to_embed('You can\'t remove yourself from the blacklist.'))
            self.bot.db.execute('SELECT * FROM moderation WHERE action = "{}" AND user_id = "{}"'.format(
                'Invite Blacklist', member.id))
            result = self.bot.db.fetchone()
            if not result:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This user isn\'t blacklisted.'))
            self.bot.db.execute(
                'DELETE FROM moderation WHERE action = "{}" AND user_id = "{}"'.format('Invite Blacklist', member.id))
            await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Removed **{}** from the invite blacklist'.format(member)))
        else:
            await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, ('Administrators can\'t be blacklisted.' if member.guild_permissions.administrator
                                                                             else 'Users with the same or higher rank can\'t be blacklisted.' if member.top_role.position >= ctx.guild.me.top_role.position
                                                                             else 'I can\'t remove that user from the blacklist.')))

    @commands.command()
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    async def traceinvite(self, ctx, invite_id):
        self.bot.db.execute(
            'SELECT * FROM invites WHERE id = "{}" AND guild_id = "{}"'.format(invite_id, ctx.guild.id))
        result = self.bot.db.fetchone()
        if not result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No record with that invite ID was found.'))
        embed = discord.Embed(description='Inviter: **{}**\nInvited: **{}**\nIs Fake: **{}**\nIs Bonus: **{}**\nCode: **{}**\nInvited Joined at: **{}**'.format(
            result[2] if not (discord.utils.find(lambda m: str(m.id) == str(result[2]), ctx.guild.members)) else (
                discord.utils.find(lambda m: str(m.id) == str(result[2]), ctx.guild.members)).mention,
            result[3] if not (discord.utils.find(lambda m: str(m.id) == str(result[3]), ctx.guild.members)) else (
                discord.utils.find(lambda m: str(m.id) == str(result[3]), ctx.guild.members)).mention,
            'Yes' if str(result[4]) == '1' else 'No',
            'Yes' if str(result[5]) == '1' else 'No',
            result[6],
            str(datetime.fromtimestamp(float(result[7])).strftime('%a, %b %d, %Y %I:%M %p'))), color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
            None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None)
        embed.set_author(name='Invite ID: {}'.format(result[0]))
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(InviteTracer(bot))
