from discord.ext import commands
import discord
from random import randint
import os
import asyncio
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from .invitetrace import *


class Welcomer(commands.Cog):

    def __init__(self, bot):
        self.CACHE_PATH = 'cache'
        self.bot = bot
        self.bot.db.execute('''CREATE TABLE IF NOT EXISTS welcomer(
                id MEDIUMINT NOT NULL AUTO_INCREMENT,
                welcome_image TEXT,
                guild_id TEXT,
                channel_id TEXT,
                dm_text TEXT,
                text TEXT,
                deletion_delay TEXT,
                    PRIMARY KEY (id))''')
        self.bot.db.execute(
            'ALTER TABLE `welcomer` CHANGE `text` `text` VARCHAR(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL;')  # ! non utf8, accepts emotes etc
        self.bot.db.execute(
            'ALTER TABLE `welcomer` CHANGE `dm_text` `dm_text` VARCHAR(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL;')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        joined_at = int(datetime.now(tz=timezone.utc).timestamp())
        if member.bot:
            return
        await asyncio.sleep(0.5)
        self.bot.db.execute(
            'SELECT * FROM welcomer WHERE guild_id = {}'.format(member.guild.id))
        result = self.bot.db.fetchone()
        if not result:
            return
        channel = discord.utils.find(lambda i: str(
            i.id) == str(result[3]), member.guild.channels)
        if not channel:
            return
        self.bot.db.execute('SELECT inviter_id FROM invites WHERE guild_id = "{}" AND invited_at = "{}"'.format(
            member.guild.id, joined_at))
        invitedby = self.bot.db.fetchone()
        if not invitedby:
            invitedbyid = 'N/A'
            invitedbyname = 'N/A'
            invitedbyfullname = 'N/A'
            invitedbymention = 'N/A'
        else:
            invitedby = discord.utils.find(lambda m: str(
                m.id) == str(invitedby[0]), member.guild.members)
            if not invitedby:
                invitedbyid = result[0]
                invitedbyname = result[0]
                invitedbyfullname = result[0]
                invitedbymention = result[0]
            else:
                invitedbyid = invitedby.id
                invitedbyname = invitedby.name
                invitedbyfullname = invitedby
                invitedbymention = invitedby.mention
        self.bot.db.execute(
            'SELECT * FROM invitestats WHERE guild_id = "{}" AND member_id = "{}"'.format(member.guild.id, invitedbyid))
        _result = self.bot.db.fetchone()
        if not _result:
            total = 'N/A'
        else:
            total = _result[3]
        totalinvites = total
        totalmembers = str('{}{}').format(len(member.guild.members), 'th' if len(member.guild.members) >= 4
                                          else 'rd' if len(member.guild.members) == 3
                                          else 'nd' if len(member.guild.members) == 2 else 'N/A')
        membermention = str(member.mention)
        memberfullname = str(member)
        membername = str(member.name)
        guildname = str(member.guild.name)
        memberid = str(member.id)
        if result[4] != 'None':  # dmtext
            try:
                await member.send(str(result[4]).format(
                    totalmembers=totalmembers, memberfullname=memberfullname, membername=membername, membermention=membermention, guildname=guildname, memberid=memberid, totalinvites=totalinvites,
                    invitedbyid=invitedbyid, invitedbyname=invitedbyname, invitedbyfullname=invitedbyfullname, invitedbymention=invitedbymention))
            except discord.Forbidden:
                pass
        if result[5]:  # channeltext
            custom_channel_text = str(result[5]).format(
                totalmembers=totalmembers, memberfullname=memberfullname, membername=membername, membermention=membermention, guildname=guildname, memberid=memberid, totalinvites=totalinvites,
                invitedbyid=invitedbyid, invitedbyname=invitedbyname, invitedbyfullname=invitedbyfullname, invitedbymention=invitedbymention)
        else:
            custom_channel_text = None

    @commands.group(invoke_without_command=True, aliases=['greet'])
    @commands.guild_only()
    async def welcome(self, ctx):
        prefix = self.bot.config._get_prefix(self.bot, ctx)
        embed = discord.Embed(title='Welcomer',
                              description=f"**<>** = required\n**[]** = optional",
                              color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None,
                              timestamp=ctx.message.created_at)
        embed.add_field(
            name='Interactive welcome setup', value='`{}welcome setup`'.format(prefix))
        embed.add_field(
            name='Delete this servers welcome config', value='`{}welcome delete`'.format(prefix))
        await ctx.send(embed=embed)

    @welcome.command()
    @commands.guild_only()
    @commands.bot_has_guild_permissions(attach_files=True)
    @commands.has_guild_permissions(administrator=True)
    async def setup(self, ctx):
        prefix = self.bot.config._get_prefix(self.bot, ctx)
        self.bot.db.execute(
            'SELECT channel_id FROM welcomer WHERE guild_id = {}'.format(ctx.guild.id))
        result = self.bot.db.fetchone()
        if result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This server already has a welcome config. Delete it with **{}**.'.format(prefix + 'welcome delete')))
        await ctx.send(embed=embeds.AwaitInput._text_to_embed(self.bot, ctx, 'Please mention the channel the welcome messages should be sent in. Enter **cancel** to cancel.'))
        while 1:
            channel_msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
            if str(channel_msg.content) == 'cancel':
                return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Cancelled'))
            try:
                channel_id = int(channel_msg.content.replace(
                    '<#', '').replace('>', ''))
                channel = discord.utils.find(lambda i: str(
                    i.id) == str(channel_id), ctx.guild.channels)
                if not channel:
                    await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Channel wasn\'t found. Please mention the channel like that: **#channel**'))
                    continue
                channel_id = channel.id
                break
            except:
                await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Channel wasn\'t found. Please mention the channel like that: **#channel**'))
        await ctx.send(embed=embeds.AwaitInput._text_to_embed(self.bot, ctx, 'Please enter the text that should be sent to the new members privately. Enter **skip** to skip or **cancel** to cancel.\n\nYou may include **{totalmembers}**, **{membermention}**, **{memberfullname}**, **{membername}**, **{memberid}**, **{totalinvites}**, **{invitedbymention}**, **{invitedbyfullname}**, **{invitedbyname}**, **{invitedbyid}** and **{guildname}** to format the sent text.'))
        while 1:
            dm_text_msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
            if str(dm_text_msg.content) == 'cancel':
                return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Cancelled'))
            elif str(dm_text_msg.content) == 'skip':
                dm_text = None
                break
            dm_text = dm_text_msg.content
            break
        text = await ctx.send(embed=embeds.AwaitInput._text_to_embed(self.bot, ctx, 'Please enter the text that should be sent above the welcome image. Enter **skip** to skip or **cancel** to cancel.\n\nYou may include **{totalmembers}**, **{membermention}**, **{memberfullname}**, **{membername}**, **{memberid}**, **{totalinvites}**, **{invitedbymention}**, **{invitedbyfullname}**, **{invitedbyname}**, **{invitedbyid}** and **{guildname}** to format the sent text.'))
        while 1:
            text = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
            if str(text.content) == 'cancel':
                return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Cancelled'))
            elif str(text.content) == 'skip':
                text = None
                break
            text = text.content
            break
        deletion_delay = await ctx.send(embed=embeds.AwaitInput._text_to_embed(self.bot, ctx, 'Please enter the deletion delay when the user was welcomed. This will greet the new member, and delete the welcome message after the given time. This does not apply to DMs. Enter **0** if you don\'t want any deletion or **cancel** to cancel.'))
        while 1:
            deletion_delay = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
            if str(deletion_delay.content) == 'cancel':
                return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Cancelled'))
            elif str(deletion_delay.content) == '0':
                deletion_delay = 0
                break
            elif not str(deletion_delay.content).isdigit():
                await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Bad time given. Please reenter the deletion delay.'))
                continue
            deletion_delay = deletion_delay.content
            break
        self.bot.db.execute('INSERT INTO welcomer (guild_id,channel_id,dm_text,text,deletion_delay) VALUES ("{}","{}","{}","{}","{}")'.format(ctx.guild.id,
                                                                                                                                              channel_id,
                                                                                                                                                   dm_text if dm_text else None,
                                                                                                                                                   text if text else None,
                                                                                                                                                   deletion_delay))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'You\'re all set up! Members will now be greeted in {}'.format(channel.mention)))

    @welcome.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def delete(self, ctx):
        prefix = self.bot.config._get_prefix(self.bot, ctx)
        self.bot.db.execute(
            'SELECT channel_id FROM welcomer WHERE guild_id = {}'.format(ctx.guild.id))
        result = self.bot.db.fetchone()
        if not result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This server doesn\'t have a welcome config. Create one with **{}**.'.format(prefix + 'welcome setup')))
        channel = discord.utils.find(lambda i: str(
            i.id) == str(result[0]), ctx.guild.channels)
        channel = '**N/A**' if not channel else channel.mention
        self.bot.db.execute(
            'DELETE FROM welcomer WHERE guild_id = {}'.format(ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Deleted welcome config from channel {}'.format(channel)))


def setup(bot):
    bot.add_cog(Welcomer(bot))
