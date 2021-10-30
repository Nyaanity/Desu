from discord.ext import commands
import discord
from datetime import datetime, timezone
import pytz
from discord import Webhook, AsyncWebhookAdapter
import aiohttp
import asyncio
from __bot.emojis import Emojis as emojis
from __bot.embeds import Embeds as embeds


green = 0x3A7248
red = 0x723A3A
invisible = 0x2f3134
orange = 0xFF903A


class Logging(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.CACHE_PATH = 'cache'
        self.session = aiohttp.ClientSession()
        self.callstack = {}
        self.CALLSTACK_MESSAGE_EMBEDS_MAX = 10
        self.CALLSTACK_LOOPTHROUGH_DELAY = 5
        self.bot.db.execute('''CREATE TABLE IF NOT EXISTS auditlogs(
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            guild_id TEXT,
            webhook_url TEXT,
                PRIMARY KEY (id))''')

    async def get_webhook(self, webhook_url):
        webhook = Webhook.from_url(
            webhook_url, adapter=AsyncWebhookAdapter(self.session))
        return None if not webhook else webhook

    async def get_webhook_url(self, guild_id):
        self.bot.db.execute('SELECT webhook_url FROM auditlogs WHERE guild_id = "{}"'.format(
            guild_id))
        result = self.bot.db.fetchone()
        return None if not result else result[0]

    async def has_alt_flag(self, member):
        self.bot.db.execute(
            'SELECT minimum_age FROM antialt WHERE guild_id = "{}"'.format(member.guild.id))
        altresult = self.bot.db.fetchone()
        return False if not altresult else False if str(altresult[0]) == 'N/A' else True if datetime.now(tz=timezone.utc).timestamp() - member.created_at.timestamp() < (int(altresult[0])*86400) else False

    async def not_allowed_flag(self, member):
        self.bot.db.execute(
            'SELECT enabled FROM joinblock WHERE guild_id = "{}"'.format(member.guild.id))
        allowedresult = self.bot.db.fetchone()
        return False if not allowedresult else True if str(allowedresult[0]) == '1' else False if str(allowedresult[0]) == '0' else False

    async def addcall(self, guild_id: int, call):
        try:
            self.callstack[guild_id]['callstack']
        except KeyError:
            self.callstack[guild_id] = {}
            self.callstack[guild_id]['callstack'] = []
            self.callstack[guild_id]['callstack'].append(call)
            return
        self.callstack[guild_id]['callstack'].append(call)

    @commands.Cog.listener()
    async def on_ready(self):
        while 1:
            for guild in self.bot.guilds:
                try:
                    self.callstack[guild.id]
                except KeyError:
                    continue
                guildwebhookurl = await self.get_webhook_url(guild.id)
                if not guildwebhookurl:
                    continue
                guildwebhook = await self.get_webhook(guildwebhookurl)
                if not guildwebhook:
                    continue
                if self.callstack[guild.id]['callstack'] != []:
                    # message can only contain max. 10 embeds (i think, lol. not adding that tho until error.)
                    await guildwebhook.send(embeds=[embed for embed in self.callstack[guild.id]['callstack']])
                    self.callstack[guild.id]['callstack'] = []
            # bot sends max. 1 message every 10s containing multiple embeds (if given)
            await asyncio.sleep(self.CALLSTACK_LOOPTHROUGH_DELAY)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        webhook_url = await self.get_webhook_url(guild.id)
        if not webhook_url:
            return
        webhook = await self.get_webhook(webhook_url)
        if not webhook:
            return
        embed = discord.Embed(title='Member Ban',
                              description=user.mention,
                              color=invisible,
                              timestamp=datetime.now(tz=pytz.utc))
        embed.set_author(
            name=user, icon_url=user.avatar_url, url=user.avatar_url)
        embed.set_footer(text='Member ID: {}'.format(user.id))
        await self.addcall(guild.id, embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        webhook_url = await self.get_webhook_url(guild.id)
        if not webhook_url:
            return
        webhook = await self.get_webhook(webhook_url)
        if not webhook:
            return
        embed = discord.Embed(title='Member Unban',
                              description=user.mention,
                              color=invisible,
                              timestamp=datetime.now(tz=pytz.utc))
        embed.set_author(
            name=user, icon_url=user.avatar_url, url=user.avatar_url)
        embed.set_footer(text='Member ID: {}'.format(user.id))
        await self.addcall(guild.id, embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.author.bot:
            return
        webhook_url = await self.get_webhook_url(after.guild.id)
        if not webhook_url:
            return
        webhook = await self.get_webhook(webhook_url)
        if not webhook:
            return
        if before.content != after.content:
            embed = discord.Embed(title='Message Edit',
                                  description=after.author.mention +
                                  '\'s message was edited in {}'.format(
                                      after.channel.mention),
                                  color=invisible,
                                  timestamp=datetime.now(tz=pytz.utc))
            embed.add_field(name='Before', value='{}'.format(
                before.content if before.content else 'N/A'), inline=False)
            embed.add_field(name='After', value='{}'.format(
                after.content if after.content else 'N/A'), inline=False)
            embed.set_author(
                name=after.author, icon_url=after.author.avatar_url, url=after.author.avatar_url)
            embed.set_footer(text='Member ID: {}'.format(after.id))
            await self.addcall(after.guild.id, embed)
        # elif not before.pinned and after.pinned:
        #     embed = discord.Embed(title='Message Pin',
        #                           description='**[Message]({})** sent from '.format(
        #                               after.jump_url) + after.author.mention + ' was pinned',
        #                           color=green,
        #                           timestamp=datetime.now(tz=pytz.utc))
        #     embed.set_author(
        #         name=after.author, icon_url=after.author.avatar_url, url=after.author.avatar_url)
        #     embed.set_footer(text='Member ID: {}'.format(after.id))
        #     await webhook.send(embed=embed)
        # elif before.pinned and not after.pinned:
        #     embed = discord.Embed(title='Message Pin Remove',
        #                           description='**[Message]({})** sent from '.format(
        #                               after.jump_url) + after.author.mention + ' was unpinned',
        #                           color=red,
        #                           timestamp=datetime.now(tz=pytz.utc))
        #     embed.set_author(
        #         name=after.author, icon_url=after.author.avatar_url, url=after.author.avatar_url)
        #     embed.set_footer(text='Member ID: {}'.format(after.id))
        #     await webhook.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        webhook_url = await self.get_webhook_url(message.guild.id)
        if not webhook_url:
            return
        webhook = await self.get_webhook(webhook_url)
        if not webhook:
            return
        embed = discord.Embed(title='Message Delete',
                              description=message.author.mention +
                              '\'s message was deleted in {}'.format(
                                  message.channel.mention),
                              color=invisible,
                              timestamp=datetime.now(tz=pytz.utc))
        embed.add_field(name='Content', value='{}'.format(
            message.content if message.content else 'N/A'), inline=False)
        embed.set_author(
            name=message.author, icon_url=message.author.avatar_url, url=message.author.avatar_url)
        embed.set_footer(text='Member ID: {}'.format(message.author.id))
        await self.addcall(message.guild.id, embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        webhook_url = await self.get_webhook_url(member.guild.id)
        if not webhook_url:
            return
        webhook = await self.get_webhook(webhook_url)
        if not webhook:
            return
        embed = discord.Embed(title='Server Join',
                              description='{}{} member: '.format(len(member.guild.members),
                                                                 'th' if len(member.guild.members) >= 4
                                                                 else 'rd' if len(member.guild.members) == 3
                                                                 else 'nd' if len(member.guild.members) == 2 else 'N/A') + member.mention,
                              color=invisible,
                              timestamp=datetime.now(tz=pytz.utc))
        embed.add_field(name='Status', value=('{} Accepted'.format(emojis.YES_TICK) if not (await self.has_alt_flag(member)) and not (await self.not_allowed_flag(member)) else '{} Blocked'.format(emojis.NO_TICK)),
                        inline=False)
        embed.add_field(name='Flags', value=('{} Alt\n{} Join blocked'.format(emojis.NO_TICK, emojis.NO_TICK) if not (await self.has_alt_flag(member)) and not (await self.not_allowed_flag(member))
                                             else '{} Alt\n{} Join blocked'.format(emojis.YES_TICK, emojis.NO_TICK) if (await self.has_alt_flag(member)) and not (await self.not_allowed_flag(member))
                                             else '{} Alt\n{} Join blocked'.format(emojis.NO_TICK, emojis.YES_TICK) if not (await self.has_alt_flag(member)) and (await self.not_allowed_flag(member))
                                             else '{} Alt\n{} Join blocked'.format(emojis.YES_TICK, emojis.YES_TICK) if (await self.has_alt_flag(member)) and (await self.not_allowed_flag(member))
                                             else 'N/A'),
                        inline=False)
        embed.set_author(
            name=member, icon_url=member.avatar_url, url=member.avatar_url)
        embed.set_footer(text='Member ID: {}'.format(member.id))
        await self.addcall(member.guild.id, embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return
        webhook_url = await self.get_webhook_url(member.guild.id)
        if not webhook_url:
            return
        webhook = await self.get_webhook(webhook_url)
        if not webhook:
            return
        if not before.channel and after.channel:
            embed = discord.Embed(title='Voicechat Join',
                                  description=member.mention + ' joined ' + after.channel.mention,
                                  color=invisible,
                                  timestamp=datetime.now(tz=pytz.utc))
            embed.set_author(
                name=member, icon_url=member.avatar_url, url=member.avatar_url)
            embed.set_footer(text='Member ID: {}'.format(member.id))
            await self.addcall(member.guild.id, embed)
        elif before.channel != after.channel and after.channel:
            embed = discord.Embed(title='Voicechat Move',
                                  description=member.mention + ' moved from ' +
                                  before.channel.mention + ' to ' + after.channel.mention,
                                  color=invisible,
                                  timestamp=datetime.now(tz=pytz.utc))
            embed.set_author(
                name=member, icon_url=member.avatar_url, url=member.avatar_url)
            embed.set_footer(text='Member ID: {}'.format(member.id))
            await self.addcall(member.guild.id, embed)
        elif not after.channel:
            embed = discord.Embed(title='Voicechat Leave',
                                  description=member.mention + ' left ' + before.channel.mention,
                                  color=invisible,
                                  timestamp=datetime.now(tz=pytz.utc))
            embed.set_author(
                name=member, icon_url=member.avatar_url, url=member.avatar_url)
            embed.set_footer(text='Member ID: {}'.format(member.id))
            await self.addcall(member.guild.id, embed)
        elif not before.mute and after.mute:
            embed = discord.Embed(title='Server Mute',
                                  description=member.mention,
                                  color=invisible,
                                  timestamp=datetime.now(tz=pytz.utc))
            embed.set_author(
                name=member, icon_url=member.avatar_url, url=member.avatar_url)
            embed.set_footer(text='Member ID: {}'.format(member.id))
            await self.addcall(member.guild.id, embed)
        elif before.mute and not after.mute:
            embed = discord.Embed(title='Server Unmute',
                                  description=member.mention,
                                  color=invisible,
                                  timestamp=datetime.now(tz=pytz.utc))
            embed.set_author(
                name=member, icon_url=member.avatar_url, url=member.avatar_url)
            embed.set_footer(text='Member ID: {}'.format(member.id))
            await self.addcall(member.guild.id, embed)
        elif before.deaf and not after.deaf:
            embed = discord.Embed(title='Server Undeaf',
                                  description=member.mention,
                                  color=invisible,
                                  timestamp=datetime.now(tz=pytz.utc))
            embed.set_author(
                name=member, icon_url=member.avatar_url, url=member.avatar_url)
            embed.set_footer(text='Member ID: {}'.format(member.id))
            await self.addcall(member.guild.id, embed)
        elif not before.deaf and after.deaf:
            embed = discord.Embed(title='Server Deaf',
                                  description=member.mention,
                                  color=invisible,
                                  timestamp=datetime.now(tz=pytz.utc))
            embed.set_author(
                name=member, icon_url=member.avatar_url, url=member.avatar_url)
            embed.set_footer(text='Member ID: {}'.format(member.id))
            await self.addcall(member.guild.id, embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        perm = []
        webhook_url = await self.get_webhook_url(channel.guild.id)
        if not webhook_url:
            return
        webhook = await self.get_webhook(webhook_url)
        if not webhook:
            return
        embed = discord.Embed(title='Channel Create',
                              description='{} in category **{}**'.format(
                                  channel.mention, 'N/A' if not channel.category else channel.category.name),
                              color=invisible,
                              timestamp=datetime.now(tz=pytz.utc))
        for overwrite in channel.overwrites:
            for perms in channel.overwrites_for(overwrite):
                if perms[1]:
                    perm.append('{} {}'.format(
                        emojis.YES_TICK if perms[1] else emojis.NO_TICK, perms[0].replace('_', ' ').title()))
            if perm:
                embed.add_field(name='Permission override for {}'.format(overwrite),
                                value='\n'.join(perm))
        embed.set_footer(text='Channel ID: {}'.format(channel.id))
        await self.addcall(channel.guild.id, embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        webhook_url = await self.get_webhook_url(channel.guild.id)
        if not webhook_url:
            return
        webhook = await self.get_webhook(webhook_url)
        if not webhook:
            return
        embed = discord.Embed(title='Channel Delete',
                              description='**{}** in category **{}**'.format(
                                  channel.name, 'N/A' if not channel.category else channel.category.name),
                              color=invisible,
                              timestamp=datetime.now(tz=pytz.utc))
        embed.set_footer(text='Channel ID: {}'.format(channel.id))
        await self.addcall(channel.guild.id, embed)

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        # required if multiple updates are done. e.g. user changes icon AND name of server at once
        befores, afters = [], []
        webhook_url = await self.get_webhook_url(after.id)
        if not webhook_url:
            return
        webhook = await self.get_webhook(webhook_url)
        if not webhook:
            return
        embed = discord.Embed(title='Server Update',
                              color=invisible,
                              timestamp=datetime.now(tz=pytz.utc))
        if before.name != after.name:
            befores.append(
                '**Name**: ' + before.name), afters.append('**Name**: ' + after.name)
        if before.icon_url != after.icon_url:
            embed.set_image(url=after.icon_url)
            befores.append(
                '**Icon**: New icon'), afters.append('**Icon**: New icon')
        if before.region != after.region:
            befores.append('**Region**: ' + str(before.region).title()
                           ), afters.append('**Region**: ' + str(after.region).title())
        if before.verification_level != after.verification_level:
            befores.append('**Verification level**: ' + str(before.verification_level).title()
                           ), afters.append('**Verification level**: ' + str(after.verification_level).title())
        if before.mfa_level != after.mfa_level:
            befores.append('**Moderators require 2FA**: ' + 'Yes' if str(before.mfa_level) == '1' else 'No'), afters.append(
                '**Moderators require 2FA**: ' + 'Yes' if str(after.mfa_level) == '1' else 'No')
        if before.explicit_content_filter != after.explicit_content_filter:
            befores.append('**Members to check for NSFW**: ' + str(before.explicit_content_filter).replace('_', ' ').title()
                           ), afters.append('**Members to check for NSFW**: ' + str(after.explicit_content_filter).replace('_', ' ').title())
        if not befores:  # skips updates that are not listed in befores/afters
            return
        embed.add_field(name='Before', value='\n'.join(
            before for before in befores), inline=False)
        embed.add_field(name='After', value='\n'.join(
            after for after in afters), inline=False)
        embed.set_author(
            name=after, icon_url=after.icon_url, url=after.icon_url)
        embed.set_footer(text='Guild ID: {}'.format(after.id))
        await self.addcall(after.guild.id, embed)

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        webhook_url = await self.get_webhook_url(guild.id)
        if not webhook_url:
            return
        webhook = await self.get_webhook(webhook_url)
        if not webhook:
            return
        if len(before) > len(after):
            removed_emoji = list(set(before + after))
            embed = discord.Embed(title='Emoji Remove',
                                  description='**{}** was removed from this server'.format(
                                      removed_emoji[0]),
                                  color=invisible,
                                  timestamp=datetime.now(tz=pytz.utc))
            embed.set_author(
                name=guild, icon_url=guild.icon_url, url=guild.icon_url)
            embed.set_footer(text='Emoji ID: {}'.format(removed_emoji[0].id))
            return await self.addcall(after.guild.id, embed)
        elif len(before) < len(after):
            added_emoji = list(set(before + after))
            embed = discord.Embed(title='Emoji Add',
                                  description='{} was added to this server'.format(
                                      added_emoji[0], after),
                                  color=invisible,
                                  timestamp=datetime.now(tz=pytz.utc))
            embed.set_author(
                name=guild, icon_url=guild.icon_url, url=guild.icon_url)
            embed.set_footer(text='Emoji ID: {}'.format(added_emoji[0].id))
            await self.addcall(after.guild.id, embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        webhook_url = await self.get_webhook_url(member.guild.id)
        if not webhook_url:
            return
        webhook = await self.get_webhook(webhook_url)
        if not webhook:
            return
        embed = discord.Embed(title='Member Leave',
                              description=member.mention,
                              color=invisible,
                              timestamp=datetime.now(tz=pytz.utc))
        embed.set_author(
            name=member, icon_url=member.avatar_url, url=member.avatar_url)
        embed.set_footer(text='Member ID: {}'.format(member.id))
        await self.addcall(member.guild.id, embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        webhook_url = await self.get_webhook_url(after.guild.id)
        if not webhook_url:
            return
        webhook = await self.get_webhook(webhook_url)
        if not webhook:
            return
        if before.display_name != after.display_name:
            if after.display_name == before.name:
                embed = discord.Embed(title='Nickname Reset',
                                      description=after.mention,
                                      color=invisible,
                                      timestamp=datetime.now(tz=pytz.utc))
                embed.add_field(name='Before', value='{}'.format(
                    before.display_name), inline=False)
                embed.add_field(name='After', value='{}'.format(
                    after.display_name), inline=False)
                embed.set_author(
                    name=after, icon_url=after.avatar_url, url=after.avatar_url)
                embed.set_footer(text='Member ID: {}'.format(after.id))
                return await self.addcall(after.guild.id, embed)
            embed = discord.Embed(title='Nickname Change',
                                  description=after.mention,
                                  color=invisible,
                                  timestamp=datetime.now(tz=pytz.utc))
            embed.add_field(name='Before', value='{}'.format(
                before.display_name), inline=False)
            embed.add_field(name='After', value='{}'.format(
                after.display_name), inline=False)
            embed.set_author(
                name=after, icon_url=after.avatar_url, url=after.avatar_url)
            embed.set_footer(text='Member ID: {}'.format(after.id))
            return await self.addcall(after.guild.id, embed)
        elif before.roles != after.roles:
            if len(before.roles) > len(after.roles):
                removed_role = list(set(before.roles + after.roles))
                embed = discord.Embed(title='Role Remove',
                                      description='Role {} was removed from {}'.format(
                                          removed_role[1].mention, after.mention),
                                      color=invisible,
                                      timestamp=datetime.now(tz=pytz.utc))
                embed.set_author(
                    name=after, icon_url=after.avatar_url, url=after.avatar_url)
                embed.set_footer(text='Member ID: {}'.format(after.id))
                return await self.addcall(after.guild.id, embed)
            elif len(before.roles) < len(after.roles):
                added_role = list(set(before.roles + after.roles))
                embed = discord.Embed(title='Role Add',
                                      description='Role {} was added to {}'.format(
                                          added_role[1].mention, after.mention),
                                      color=invisible,
                                      timestamp=datetime.now(tz=pytz.utc))
                embed.set_author(
                    name=after, icon_url=after.avatar_url, url=after.avatar_url)
                embed.set_footer(text='Member ID: {}'.format(after.id))
                return await self.addcall(after.guild.id, embed)

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        for guild in self.bot.guilds:  # loop through all guilds since before/after doesn't have 'guild'
            if not after in guild.members:
                return
            webhook_url = await self.get_webhook_url(guild.id)
            if not webhook_url:
                continue
            webhook = await self.get_webhook(webhook_url)
            if not webhook:
                continue
            if before.avatar_url != after.avatar_url:
                embed = discord.Embed(title='Avatar Update',
                                      description=after.mention,
                                      color=invisible,
                                      timestamp=datetime.now(tz=pytz.utc))
                embed.set_author(
                    name=after, icon_url=after.avatar_url, url=after.avatar_url)
                embed.set_thumbnail(url=after.avatar_url)
                embed.set_footer(text='Member ID: {}'.format(after.id))
                await self.addcall(guild.id, embed)
            if before.name != after.name:
                embed = discord.Embed(title='Name Change',
                                      description=after.mention,
                                      color=invisible,
                                      timestamp=datetime.now(tz=pytz.utc))
                embed.add_field(name='Before', value='{}'.format(
                    before.name), inline=False)
                embed.add_field(name='After', value='{}'.format(
                    after.name), inline=False)
                embed.set_author(
                    name=after, icon_url=after.avatar_url, url=after.avatar_url)
                embed.set_footer(text='Member ID: {}'.format(after.id))
                await self.addcall(guild.id, embed)
            elif before.discriminator != after.discriminator:
                embed = discord.Embed(title='Discriminator Change',
                                      description=after.mention,
                                      color=invisible,
                                      timestamp=datetime.now(tz=pytz.utc))
                embed.add_field(name='Before', value='{}'.format(
                    f'#{before.discriminator}'), inline=False)
                embed.add_field(name='After', value='{}'.format(
                    f'#{after.discriminator}'), inline=False)
                embed.set_author(
                    name=after, icon_url=after.avatar_url, url=after.avatar_url)
                embed.set_footer(text='Member ID: {}'.format(after.id))
                await self.addcall(guild.id, embed)

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        webhook_url = await self.get_webhook_url(messages[0].guild.id)
        if not webhook_url:
            return
        webhook = await self.get_webhook(webhook_url)
        if not webhook:
            return
        embed = discord.Embed(title='Bulk Message Delete',
                              description='Deleted **{}** messages in {}'.format(
                                  len(messages)-1, messages[0].channel.mention),
                              color=invisible,
                              timestamp=datetime.now(tz=pytz.utc))
        embed.add_field(name='Messages', value=str('\n'.join(
            ['**{}**: {}'.format(message.author, message.content) for message in messages]))[:1024])
        embed.set_footer(text='Channel ID: {}'.format(messages[0].channel.id))
        await self.addcall(messages.guild.id, embed)

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def audit(self, ctx):
        prefix = self.bot.config._get_prefix(self.bot, ctx)
        embed = discord.Embed(title='Audit Logging',
                              description=f"**<>** = required\n**[]** = optional",
                              color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None,
                              timestamp=ctx.message.created_at)
        embed.add_field(
            name='Interactive logger setup', value='`{}audit setup`'.format(prefix))
        embed.add_field(
            name='Delete this servers logger config', value='`{}audit delete`'.format(prefix))
        await ctx.send(embed=embed)

    @audit.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    @commands.bot_has_guild_permissions(administrator=True)
    async def setup(self, ctx):
        prefix = self.bot.config._get_prefix(self.bot, ctx)
        self.bot.db.execute(
            'SELECT webhook_url FROM auditlogs WHERE guild_id = {}'.format(ctx.guild.id))
        result = self.bot.db.fetchone()
        if result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This server already has a logger config. Delete it with **{}**.'.format(prefix + 'audit delete')))
        await ctx.send(embed=embeds.AwaitInput._text_to_embed(self.bot, ctx, 'Please mention the channel events should be logged in. Enter **cancel** to cancel.'))
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
        bot_avatar_url = self.bot.user.avatar_url_as(format="png", size=256)
        async with aiohttp.ClientSession() as session:
            async with session.get(str(bot_avatar_url)) as response:
                avatar = await response.read()
        webhook = await channel.create_webhook(name=str('[LOG] ' + self.bot.user.name), avatar=avatar)
        self.bot.db.execute('INSERT INTO auditlogs (guild_id,webhook_url) VALUES ("{}","{}")'.format(
            ctx.guild.id, webhook.url))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'You\'re all set up! Events will now be logged in {}'.format(channel.mention)))

    @audit.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    @commands.bot_has_guild_permissions(administrator=True)
    async def delete(self, ctx):
        prefix = self.bot.config._get_prefix(self.bot, ctx)
        self.bot.db.execute(
            'SELECT webhook_url FROM auditlogs WHERE guild_id = {}'.format(ctx.guild.id))
        result = self.bot.db.fetchone()
        if not result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This server doesn\'t have a logger config. Create one with **{}**.'.format(prefix + 'audit setup')))
        self.bot.db.execute(
            'DELETE FROM auditlogs WHERE guild_id = {}'.format(ctx.guild.id))
        webhook = await self.get_webhook(result[0])
        if webhook:
            await webhook.delete()
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Deleted** logger config'))


def setup(bot):
    bot.add_cog(Logging(bot))
