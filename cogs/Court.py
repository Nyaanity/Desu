import discord
from discord.ext import commands
from __bot.embeds import Embeds as embeds


class Court(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.court_gif = 'https://imgur.com/a/KuQ2HB0'
        self.bot.db.execute('''CREATE TABLE IF NOT EXISTS court(
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            court_channel_id TEXT,
            guild_id TEXT,
                PRIMARY KEY (id))''')

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def court(self, ctx):
        prefix = self.bot.config._get_prefix(self.bot, ctx)
        embed = discord.Embed(title='Court',
                              description=f"**<>** = required\n**[]** = optional",
                              color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None,
                              timestamp=ctx.message.created_at)
        embed.add_field(
            name='Add a user to court', value='`{}court add <member>`'.format(prefix))
        embed.add_field(
            name='Remove a user from court', value='`{}court remove <member>`'.format(prefix))
        embed.add_field(
            name='Set the court channel', value='`{}court channel [channel]`'.format(prefix))
        embed.add_field(
            name='Delete this servers court', value='`{}court delete`'.format(prefix))
        await ctx.send(embed=embed)

    @court.command()
    @commands.has_guild_permissions(ban_members=True)
    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_channels=True, manage_roles=True)
    async def add(self, ctx, member: discord.Member):
        prefix = self.bot.config._get_prefix(self.bot, ctx)
        if not member.guild_permissions.administrator and not member.top_role.position >= ctx.guild.me.top_role.position:
            court_channel_id = self.bot.db.execute(
                'SELECT court_channel_id FROM court WHERE guild_id = "{}"'.format(ctx.guild.id))
            court_channel_id = self.bot.db.fetchone()
            if not court_channel_id:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Court channel not found.'))
            if not 'muted' in [str(x.name).lower() for x in ctx.guild.roles]:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, '**Muted** role was not found.'))
            if member == ctx.author:
                return await ctx.send(embed=embeds.Error._text_to_embed('You can\'t bring yourself to court.'))
            court_channel = discord.utils.find(lambda c: str(
                c.id) == str(court_channel_id[0]), ctx.guild.channels)
            if not court_channel:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'A court channel ID record was found, but the channel was not found on this server.'))
            muted_role = discord.utils.find(
                lambda r: 'muted' in str(r.name).lower(), ctx.guild.roles)
            if muted_role:
                if not muted_role in member.roles:
                    await member.add_roles(muted_role, reason='Court Add')
            await court_channel.set_permissions(member, read_messages=True, send_messages=True)
            await court_channel.send('Welcome {} to the court. That\'s the part where u beg to the almighty Discord Mods to not try {}ban on u.\n{}'.format(member.mention, prefix, self.court_gif))
            await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Added {} to the court'.format(member.mention)))
        else:
            await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, ('I can\'t bring administrators to court. They ARE the court.' if member.guild_permissions.administrator
                                                                             else 'I can\'t bring users to court with the same or higher rank.' if member.top_role.position >= ctx.guild.me.top_role.position
                                                                             else 'I can\'t bring this user to court.')))

    @court.command()
    @commands.has_guild_permissions(ban_members=True)
    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_channels=True, manage_roles=True)
    async def remove(self, ctx, member: discord.Member):
        if not member.guild_permissions.administrator and not member.top_role.position >= ctx.guild.me.top_role.position:
            court_channel_id = self.bot.db.execute(
                'SELECT court_channel_id FROM court WHERE guild_id = "{}"'.format(ctx.guild.id))
            court_channel_id = self.bot.db.fetchone()
            if not court_channel_id:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Court channel not found.'))
            if member == ctx.author:
                return await ctx.send(embed=embeds.Error._text_to_embed('You can\'t remove yourself from court.'))
            court_channel = discord.utils.find(lambda c: str(
                c.id) == str(court_channel_id[0]), ctx.guild.channels)
            if not court_channel:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'A court channel ID record was found, but the channel was not found on this server.'))
            if not member in court_channel.members:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This user is not in court.'))
            muted_role = discord.utils.find(
                lambda r: 'muted' in str(r.name).lower(), ctx.guild.roles)
            if muted_role:
                if muted_role in member.roles:
                    await member.remove_roles(muted_role, reason='Court Remove')
            await court_channel.set_permissions(member, read_messages=False, send_messages=False)
            await court_channel.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Removed {} from the court'.format(member.mention)))
        else:
            await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, ('I can\'t remove administrators from court. They ARE the court.' if member.guild_permissions.administrator
                                                                             else 'I can\'t remove users from court with the same or higher rank.' if member.top_role.position >= ctx.guild.me.top_role.position
                                                                             else 'I can\'t remove this user from court.')))

    @court.command()
    @commands.has_guild_permissions(manage_channels=True)
    @commands.guild_only()
    async def channel(self, ctx, channel: discord.TextChannel = None):
        channel = ctx.channel if not channel else channel
        court_channel = self.bot.db.execute(
            'SELECT court_channel_id FROM court WHERE guild_id = "{}"'.format(ctx.guild.id))
        court_channel = self.bot.db.fetchone()
        if not court_channel:
            self.bot.db.execute('INSERT INTO court (court_channel_id,guild_id) VALUES ("{}","{}")'.format(
                channel.id, ctx.guild.id))
        elif court_channel:
            self.bot.db.execute('UPDATE court SET court_channel_id = "{}" WHERE guild_id = "{}"'.format(
                channel.id, ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Set the court channel to {}'.format(channel.mention)))

    @court.command()
    @commands.has_guild_permissions(manage_channels=True)
    @commands.guild_only()
    async def delete(self, ctx):
        court_channel = self.bot.db.execute(
            'SELECT court_channel_id FROM court WHERE guild_id = "{}"'.format(ctx.guild.id))
        court_channel = self.bot.db.fetchone()
        if not court_channel:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This server doesn\'t have a court channel set.'))
        elif court_channel:
            self.bot.db.execute('DELETE FROM court WHERE court_channel_id = "{}" AND guild_id = "{}"'.format(
                court_channel[0], ctx.guild.id))
        court_channel = discord.utils.find(lambda c: str(
            c.id) == str(court_channel[0]), ctx.guild.channels)
        await ctx.send(embed=embeds.Success._text_to_embed('{} is no longer this server\'s court channel'.format('**N/A**' if not court_channel else court_channel.mention)))


def setup(bot):
    bot.add_cog(Court(bot))
