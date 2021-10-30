from discord.ext import commands
import discord
from datetime import datetime, timezone
import asyncio
import os
from discord_components import Button, ButtonStyle
from __bot.embeds import Embeds as embeds


class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.CACHE_PATH = 'cache'
        self.author_stash = []
        self.bot.db.execute('''CREATE TABLE IF NOT EXISTS tickets(
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            guild_id TEXT,
            ticket_create_channel_id TEXT,
            ticket_cat_id TEXT,
            log_channel_id TEXT,
                PRIMARY KEY (id))''')
        self.bot.db.execute('''CREATE TABLE IF NOT EXISTS ticketcache(
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            guild_id TEXT,
            user_name TEXT,
            user_id TEXT,
            ticket_opened_timestamp TEXT,
            ticket_closed_timestamp TEXT,
            ticket_closed_by TEXT,
            ticket_closed_by_id TEXT,
            ticket_channel_id TEXT,
            PRIMARY KEY (id))''')
        self.bot.db.execute(
            'ALTER TABLE `ticketcache` CHANGE `ticket_closed_by` `ticket_closed_by` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL;')
        self.bot.db.execute(
            'ALTER TABLE `ticketcache` CHANGE `user_name` `user_name` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL;')

    @commands.Cog.listener()
    async def on_button_click(self, button):
        try:
            x = button.component.label
        except:
            return
        if str(button.component.label) == 'Create Ticket':
            if not button.guild.me.guild_permissions.read_message_history:
                return await button.respond(embed=embeds.Error._text_to_embed(self.bot, button, 'I\'m missing the **Read Message History** permission to create tickets. Please contact your server administrator if this is an issue.'))
            if not button.guild.me.guild_permissions.manage_channels:
                return await button.respond(embed=embeds.Error._text_to_embed(self.bot, button, 'I\'m missing the **Manage Channels** permission to create tickets. Please contact your server administrator if this is an issue.'))
            self.bot.db.execute(
                'SELECT user_id FROM ticketcache WHERE guild_id = {}'.format(button.guild.id))
            user_tickets_created_sum = self.bot.db.fetchall()
            if len(user_tickets_created_sum) > 3:
                return await button.respond(embed=embeds.Error._text_to_embed(self.bot, button, 'You\'re being blocked from creating new tickets. Please close your other tickets first.'))
            self.bot.db.execute(
                'SELECT * FROM tickets WHERE guild_id = {}'.format(button.guild.id))
            result = self.bot.db.fetchone()
            if not result:
                return await button.respond(embed=embeds.Error._text_to_embed(self.bot, button, 'This guild doesn\'t have a ticket system set up. Please contact your server administrator if this is an issue.'))
            self.bot.db.execute('SELECT ticket_cat_id FROM tickets WHERE guild_id = "{}"'.format(
                button.guild.id))
            cat_id = self.bot.db.fetchone()
            cat = discord.utils.find(lambda c: str(c.id) == str(
                cat_id[0]), button.guild.categories)
            if not cat:
                return await button.respond(embed=embeds.Error._text_to_embed(self.bot, button, 'This server does have a set ticket category, but it wasn\'t found. Please contact your server administrator if this is an issue.'))
            if {'user_id': button.author.id, 'guild_id': button.guild.id} in self.author_stash:
                return await button.respond(embed=embeds.Error._text_to_embed(self.bot, button, 'You\'re being ratelimited! Please wait a moment before trying again.'))
            self.author_stash.append(
                {'user_id': button.author.id, 'guild_id': button.guild.id})
            ticket_channel = await cat.create_text_channel(name='ticket-{}'.format(button.author.name))
            ticket_created_timestamp = int(
                datetime.now(tz=timezone.utc).timestamp())  # ! timestamp
            self.bot.db.execute('INSERT INTO ticketcache(guild_id,user_name,user_id,ticket_opened_timestamp,ticket_channel_id) VALUES ("{}","{}","{}","{}","{}")'.format(
                button.guild.id, str(button.author), button.author.id, ticket_created_timestamp, ticket_channel.id))
            await asyncio.sleep(0.5)
            await ticket_channel.set_permissions(button.author, read_messages=True, send_messages=True)
            embed = discord.Embed(title='Tickets', description='Close the ticket using the **Close Ticket** button.', color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                                  None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else button.author.color if not self.bot.DEFAULT_COLOR else None)
            await ticket_channel.send('Hey {}!'.format(button.author.mention), embed=embed, components=[[Button(style=ButtonStyle.blue, label='Close Ticket')]])
            await button.respond(embed=embeds.Success._text_to_embed(self.bot, button, 'Your ticket {} was created. Hop right in!'.format(ticket_channel.mention)))
            await asyncio.sleep(120)
            self.author_stash.remove(
                {'user_id': button.author.id, 'guild_id': button.guild.id})

        elif str(button.component.label) == 'Close Ticket':
            if not button.guild.me.guild_permissions.manage_channels:
                return await button.respond(embed=embeds.Error._text_to_embed(self.bot, button, 'I\'m missing the **Manage Channels** permission to close tickets. Please contact your server administrator if this is an issue.'))
            if not button.guild.me.guild_permissions.read_message_history:
                return await button.respond(embed=embeds.Error._text_to_embed(self.bot, button, 'I\'m missing the **Read Message History** permission to create tickets. Please contact your server administrator if this is an issue.'))
            await button.respond(embed=embeds.Loading._text_to_embed(self.bot, button, 'Closing ticket. This may take a bit...'))
            self.bot.db.execute('SELECT log_channel_id FROM tickets WHERE guild_id = "{}"'.format(
                button.guild.id))
            ticket_log_channel_id = self.bot.db.fetchone()
            if not ticket_log_channel_id:
                return await button.message.edit(embed=embeds.Error._text_to_embed(self.bot, button, 'Can\'t save the ticket because the saved ticket log channel ID seems to be missing.'), components=[])
            ticket_log_channel = discord.utils.find(
                lambda c: str(c.id) == str(ticket_log_channel_id[0]), button.guild.text_channels)
            if not ticket_log_channel:
                return await button.message.edit(embed=embeds.Error._text_to_embed(self.bot, button, 'Can\'t save the ticket because the saved ticket log channel seems to be missing.'), components=[])
            self.bot.db.execute('SELECT ticket_opened_timestamp FROM ticketcache WHERE guild_id = "{}" AND ticket_channel_id = "{}"'.format(
                button.guild.id, button.channel.id))
            tct = self.bot.db.fetchone()
            if not tct:
                return
            ticket_created_timestamp = int(
                datetime.fromtimestamp(int(tct[0]), tz=timezone.utc).timestamp())  # !timestamp
            self.bot.db.execute('UPDATE ticketcache SET ticket_closed_timestamp = "{}", ticket_closed_by = "{}", ticket_closed_by_id = "{}" WHERE guild_id = "{}" AND ticket_opened_timestamp = "{}"'.format(
                datetime.now(tz=timezone.utc).timestamp(), button.author, button.author.id, button.guild.id, ticket_created_timestamp))
            await asyncio.sleep(0.5)
            self.bot.db.execute(
                'SELECT * FROM ticketcache WHERE guild_id = "{}" AND ticket_opened_timestamp = "{}"'.format(
                    button.guild.id, ticket_created_timestamp))  # !timestamp
            ticketcache = self.bot.db.fetchone()
            messages = await button.channel.history(limit=999999999999).flatten()
            timestamps = list(reversed(
                [int(datetime.fromtimestamp(x.created_at.timestamp(), tz=timezone.utc).timestamp()) for x in messages if not x.author.bot]))  # ! timestamp
            authors = list(reversed([str(y.author)
                                     for y in messages if not y.author.bot]))
            contents = list(reversed([str(z.content)
                                      for z in messages if not z.author.bot]))
            result = ['[{}] {}: {}'.format(datetime.fromtimestamp(x), y, z) for x, y, z in zip(
                timestamps, authors, contents)]

            with open('{}/{}.log'.format(self.CACHE_PATH, str(button.channel.name)), 'w+') as log_file:
                await asyncio.sleep(1)
            with open('{}/{}.log'.format(self.CACHE_PATH, str(button.channel.name)), 'w+') as log_file:
                log_file.write('[Ticket: {}]\n[Ticket ID: {}]\n[Ticket Opened By: {} ({})]\n[Ticket Closed By: {} ({})]\n[Ticket Created At: {}]\n[Ticket Closed At: {}]\n\nChat log:\n\n{}'.format(
                    button.channel.name,
                    ticketcache[0],
                    ticketcache[2], ticketcache[3],
                    ticketcache[6], ticketcache[7],
                    datetime.fromtimestamp(float(ticketcache[4]), tz=timezone.utc).strftime(  # ! timestamp
                        '%a, %b %d, %Y %I:%M %p'),
                    datetime.now(tz=timezone.utc).strftime(  # ! timestamp
                        '%a, %b %d, %Y %I:%M %p'),
                    '\n'.join([x for x in result])))
                log_file.close()
                await ticket_log_channel.send(file=discord.File('{}/{}.log'.format(self.CACHE_PATH, str(button.channel.name))))
            await button.channel.delete()
            self.bot.db.execute(
                'DELETE FROM ticketcache WHERE guild_id = "{}" AND ticket_opened_timestamp = "{}" AND user_id = "{}"'.format(
                    button.guild.id, ticket_created_timestamp, ticketcache[3]))
            await asyncio.sleep(1)
            os.remove('{}/{}.log'.format(
                self.CACHE_PATH, str(button.channel.name)))

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def ticket(self, ctx):
        prefix = self.bot.config._get_prefix(self.bot, ctx)
        embed = discord.Embed(title='Ticket System',
                              description=f"**<>** = required\n**[]** = optional",
                              color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None,
                              timestamp=ctx.message.created_at)
        embed.add_field(
            name='Set up the ticket system', value='`{}ticket setup`'.format(prefix))
        embed.add_field(
            name='Delete this servers ticket system', value='`{}ticket delete`'.format(prefix))
        await ctx.send(embed=embed)

    @ticket.command()
    @commands.has_guild_permissions(administrator=True)
    @commands.bot_has_guild_permissions(manage_channels=True, read_message_history=True)
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def setup(self, ctx):
        prefix = self.bot.config._get_prefix(self.bot, ctx)
        everyone = ctx.guild.default_role
        self.bot.db.execute(
            f'SELECT * FROM tickets WHERE guild_id = {ctx.guild.id}')
        _existing = self.bot.db.fetchone()
        if _existing:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'There seems to be an exisiting Ticket System. Delete it with **{}ticket delete**.'.format(prefix)))
        main_msg = await ctx.send(embed=embeds.Loading._text_to_embed(self.bot, ctx, 'Creating **Tickets** category...'))
        cat = await ctx.guild.create_category(name='Tickets')
        await cat.set_permissions(self.bot.user, read_messages=True, send_messages=True)
        await cat.set_permissions(everyone, read_messages=False, send_messages=False)
        await main_msg.edit(embed=embeds.Loading._text_to_embed(self.bot, ctx, 'Creating **ticket-logs** channel...'))
        ticket_log_channel = await cat.create_text_channel(name='ticket-logs')
        await main_msg.edit(embed=embeds.AwaitInput._text_to_embed(self.bot, ctx, 'Please mention a channel the tickets should be created in. Enter **cancel** to cancel.'))
        while 1:
            ticket_create_channel = await self.bot.wait_for('message', check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
            _ticket_create_channel_msg = ticket_create_channel
            if ticket_create_channel.content == 'cancel':
                await ticket_log_channel.delete()
                await cat.delete()
                return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Cancelled'))
            else:
                try:
                    ticket_create_channel = ticket_create_channel.content.replace(
                        '<#', '').replace('>', '')
                    ticket_create_channel = discord.utils.get(
                        ctx.guild.text_channels, id=int(ticket_create_channel))
                    if not ticket_create_channel:
                        await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This channel doesn\'t exist. Please mention the channel like that: **#channel**'), delete_after=3)
                        continue
                    break
                except:
                    await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This channel doesn\'t exist. Please mention the channel like that: **#channel**'), delete_after=3)
                    continue
        await main_msg.edit(embed=embeds.Loading._text_to_embed(self.bot, ctx, 'Baking a cake...'))
        await asyncio.sleep(1)
        self.bot.db.execute('INSERT INTO tickets(guild_id,ticket_create_channel_id,ticket_cat_id,log_channel_id) VALUES("{}","{}","{}","{}")'.format(
            ctx.guild.id, ticket_create_channel.id, cat.id, ticket_log_channel.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'You\'re all set up! Tickets can now be created by pressing the **Create Ticket** button in {}'.format(ticket_create_channel.mention)))
        await _ticket_create_channel_msg.delete()
        await main_msg.delete()
        embed = discord.Embed(title='Tickets', description='You may create a ticket by pressing the **Create Ticket** button.', color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None)
        await ticket_create_channel.send(embed=embed, components=[[Button(style=ButtonStyle.blue, label='Create Ticket')]])

    @ticket.command()
    @commands.has_guild_permissions(administrator=True)
    @commands.bot_has_guild_permissions(manage_channels=True)
    async def delete(self, ctx):
        self.bot.db.execute(
            'SELECT * FROM tickets WHERE guild_id = {}'.format(ctx.guild.id))
        result = self.bot.db.fetchone()
        if not result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'There\'s no ticket system to delete.'))
        mes = await ctx.send(embed=embeds.Warning._text_to_embed(self.bot, ctx, 'This command will delete all channels and categories bound to the ticket system or having "ticket" in their name. This also includes logs and open tickets. Are you sure?'),
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
                        prgrss = await ctx.send(embed=embeds.Loading._text_to_embed(self.bot, ctx, 'Deleting ticket system...'))
                        cat = discord.utils.find(lambda c: str(
                            c.id) == str(result[3]), ctx.guild.categories)
                        if cat:
                            for channel in cat.channels:
                                await channel.delete()
                        ticket_create_channel = discord.utils.find(
                            lambda c: str(c.id) == str(result[2]), ctx.guild.text_channels)
                        if ticket_create_channel:
                            await ticket_create_channel.delete()
                        log_channel = discord.utils.find(lambda c: str(
                            c.id) == str(result[4]), ctx.guild.text_channels)
                        if log_channel:
                            await log_channel.delete()
                        channel_remainders = [
                            channel for channel in ctx.guild.text_channels if 'ticket' in channel.name.lower()]
                        for channel in channel_remainders:
                            await channel.delete()
                        if cat:
                            await cat.delete()
                        category_remainders = [
                            cat for cat in ctx.guild.categories if 'ticket' in cat.name.lower()]
                        for category in category_remainders:
                            await category.delete()
                        self.bot._db._purge_records(self.bot.db, 'tickets', ctx.guild.id)
                        self.bot._db._purge_records(self.bot.db,
                            'ticketcache', ctx.guild.id)
                        await mes.delete()
                        await prgrss.edit(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Done'), components=[])
                        return
            except asyncio.TimeoutError:
                await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Timed out.'), delete_after=3)
                await mes.delete()
                return await ctx.message.delete()


def setup(bot):
    bot.add_cog(Ticket(bot))
