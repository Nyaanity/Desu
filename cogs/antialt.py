import discord
from discord.ext import commands
from datetime import datetime, timezone
import asyncio
from __bot.embeds import Embeds as embeds


class Antialt(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.db.execute('''CREATE TABLE IF NOT EXISTS antialt(
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            guild_id TEXT,
            enabled TEXT,
            minimum_age TEXT,
            action TEXT,
                PRIMARY KEY (id))''')
        self.bot.db.execute('''CREATE TABLE IF NOT EXISTS antialtflags(
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            guild_id TEXT,
            user_id TEXT,
            flag_expire TEXT,
                PRIMARY KEY (id))''')

    @commands.Cog.listener()  # ! antialt
    async def on_member_join(self, member):
        self.bot.db.execute(
            'SELECT * FROM antialt WHERE guild_id = "{}"'.format(member.guild.id))
        result = self.bot.db.fetchone()
        if not result:
            return
        if str(result[2]) == 'N/A' or str(result[3]) == 'N/A' or str(result[4]) == 'N/A':
            return
        if not member.guild.me.guild_permissions.ban_members or not member.guild.me.guild_permissions.kick_members:
            return
        self.bot.db.execute(
            'SELECT * FROM antialtflags WHERE guild_id = "{}" AND user_id = "{}"'.format(member.guild.id, member.id))
        flag = self.bot.db.fetchone()
        if flag:
            if datetime.now(tz=timezone.utc).timestamp() - member.created_at.timestamp() < (int(flag[3])*86400):
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
                                                                                                                                                                                                        f'Alt Protection: Account not older than {result[3]} days.',
                                                                                                                                                                                                        member.guild.id))
                self.bot.db.execute(
                    'SELECT id FROM moderation WHERE user_id = {} AND punished_at = {} AND guild_id = {}'.format(member.id, punished_at, member.guild.id))
                punishment_id = self.bot.db.fetchone()[0]
                try:
                    dm = await member.create_dm()
                    await dm.send(embed=embeds.Warning._text_to_embed('You were **banned** from **{}** because your account was flagged as a rejoining alt account (not older than **{}** days).\n\nCase ID: **{}**'.format(member.guild.name, result[3], punishment_id)))
                except:
                    pass
                return await member.ban(reason='Alt Protection: Account not older than {} days.'.format(result[3]))
        if datetime.now(tz=timezone.utc).timestamp() - member.created_at.timestamp() < (int(result[3])*86400):
            if str(result[4]) == 'kick':
                punished_at = int(datetime.now(tz=timezone.utc).timestamp())
                self.bot.db.execute(
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
                                                                                                                                                                                                        f'Account not older than {result[3]} days.',
                                                                                                                                                                                                        member.guild.id))
                self.bot.db.execute(
                    'SELECT id FROM moderation WHERE user_id = {} AND punished_at = {} AND guild_id = {}'.format(member.id, punished_at, member.guild.id))
                punishment_id = self.bot.db.fetchone()[0]
                try:
                    dm = await member.create_dm()
                    await dm.send(embed=embeds.Warning._text_to_embed('You were **kicked** from **{}** because your account was flagged as an alt account (not older than **{}** days). To avoid ratelimits, you will be permanently banned next time you join without meeting the join requirement.\n\nCase ID: **{}**'.format(member.guild.name, result[3], punishment_id)))
                except:
                    pass
                self.bot.db.execute('INSERT INTO antialtflags(guild_id,user_id,flag_expire) VALUES("{}","{}","{}")'.format(
                    member.guild.id, member.id, result[3]))
                await member.kick(reason='Alt Protection: Account not older than {} days.'.format(result[3]))
            elif str(result[4]) == 'ban':
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
                                                                                                                                                                                                        f'Account not older than {result[3]} days.',
                                                                                                                                                                                                        member.guild.id))
                self.bot.db.execute(
                    'SELECT id FROM moderation WHERE user_id = {} AND punished_at = {} AND guild_id = {}'.format(member.id, punished_at, member.guild.id))
                punishment_id = self.bot.db.fetchone()[0]
                try:
                    dm = await member.create_dm()
                    await dm.send(embed=embeds.Warning._text_to_embed('You were **banned** from **{}** because your account was flagged as an alt account (not older than **{}** days). Please don\'t join back, as you will be banned next time to avoid ratelimits.\n\nCase ID: **{}**'.format(member.guild.name, result[3], punishment_id)))
                except:
                    pass
                await member.ban(reason='Alt Protection: Account not older than {} days.'.format(result[3]))

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def antialt(self, ctx):
        prefix = self.bot.config._get_prefix(self.bot, ctx)
        embed = discord.Embed(title='Alt Protection',
                              description=f"**<>** = required\n**[]** = optional",
                              color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None,
                              timestamp=ctx.message.created_at)
        embed.add_field(
            name='Enable/disable alt-account protection', value='`{}antialt toggle`'.format(prefix))
        embed.add_field(
            name='Set a minimum account age for joining members', value='`{}antialt age <days>`'.format(prefix))
        embed.add_field(
            name='Set an action if an alt-account joins', value='`{}antialt action <ban/kick>`'.format(prefix))
        embed.add_field(
            name='Delete the anti-alt config', value='`{}antialt delete`'.format(prefix))
        await ctx.send(embed=embed)

    @antialt.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def toggle(self, ctx):
        self.bot.db.execute(
            'SELECT * FROM antialt WHERE guild_id = "{}"'.format(ctx.guild.id))
        result = self.bot.db.fetchone()
        if not result:
            self.bot.db.execute('INSERT INTO antialt(guild_id,enabled,minimum_age,action) VALUES("{}","{}","{}","{}")'.format(
                ctx.guild.id, 1, 'N/A', 'N/A'))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Enabled** alt protection'))
        if str(result[2]) == '1':
            self.bot.db.execute('UPDATE antialt SET enabled = "{}" WHERE guild_id ="{}"'.format(
                0, ctx.guild.id))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Disabled** alt protection'))
        self.bot.db.execute('UPDATE antialt SET enabled = "{}" WHERE guild_id ="{}"'.format(
            1, ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Enabled** alt protection'))

    @antialt.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def age(self, ctx, age):
        if not age.isdigit():
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Please use an integer.'))
        if int(age) > 40:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Please set the age below 40.'))
        if int(age) == 0:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Please set the age above 0.'))
        self.bot.db.execute(
            'SELECT * FROM antialt WHERE guild_id = "{}"'.format(ctx.guild.id))
        result = self.bot.db.fetchone()
        if not result:
            self.bot.db.execute('INSERT INTO antialt(guild_id,enabled,minimum_age,action) VALUES("{}","{}","{}","{}")'.format(
                ctx.guild.id, 1, age, 'N/A'))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Set the minimum required joining account age to **{}** days'.format(age)))
        self.bot.db.execute('UPDATE antialt SET minimum_age = "{}" WHERE guild_id = "{}"'.format(
            age, ctx.guild.id))
        return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Set the minimum required joining account age to **{}** days'.format(age)))

    @antialt.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def action(self, ctx, action):
        actions = ['ban', 'kick']
        if not action in actions:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Please only use **ban** or **kick**.'))
        self.bot.db.execute(
            'SELECT * FROM antialt WHERE guild_id = "{}"'.format(ctx.guild.id))
        result = self.bot.db.fetchone()
        if not result:
            self.bot.db.execute('INSERT INTO antialt(guild_id,enabled,minimum_age,action) VALUES("{}","{}","{}","{}")'.format(
                ctx.guild.id, 'N/A', 'N/A', action))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Set the alt protection action to **{}**'.format(action)))
        self.bot.db.execute('UPDATE antialt SET action = "{}" WHERE guild_id ="{}"'.format(
            action, ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Set the alt protection action to **{}**'.format(action)))

    @antialt.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def delete(self, ctx):
        self.bot.db.execute(
            'SELECT * FROM antialt WHERE guild_id = "{}"'.format(ctx.guild.id))
        result = self.bot.db.fetchone()
        if not result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This server doesn\'t have an alt protection config set.'))
        self.bot.db.execute(
            'DELETE FROM antialt WHERE guild_id = "{}"'.format(ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Deleted the alt protection config'))


def setup(bot):
    bot.add_cog(Antialt(bot))
