import discord
from discord.ext import commands
import asyncio
from __bot.embeds import Embeds as embeds


class ReactionRole(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._user_limiter_dict = []
        # delay between the bot's ability to add a role to the user. useful to prevent lag from reaction spamming.
        self.USER_REACTION_RATELIMIT = 5
        self.bot.db.execute('''CREATE TABLE IF NOT EXISTS reactionrole(
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            message_id TEXT,
            message_url TEXT,
            emoji_id TEXT,
            emoji_mention TEXT,
            role_id TEXT,
            guild_id TEXT,
            enabled TEXT,
                PRIMARY KEY (id))''')

    # @commands.Cog.listener() # delete message: remove react event automatically from db. # ! (CACHED MESSAGES ONLY)
    # async def on_message_delete(self, ctx):
    #     if str(ctx.channel.type) == 'private':
    #         return
    #     self.bot.db.execute('SELECT FROM reactionrole WHERE guild_id = "{}" AND message_id = "{}"'.format(ctx.guild.id, ctx.id))
    #     result =self.bot.db.fetchone()
    #     if result:
    #         self.bot.db.execute('DELETE FROM reactionrole WHERE guild_id = "{}" AND message_id = "{}"')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if not payload.guild_id:
            return
        if payload.member.bot:
            return
        guild = discord.utils.find(lambda g: str(
            g.id) == str(payload.guild_id), self.bot.guilds)
        if not guild:
            return
        self.bot.db.execute(
            'SELECT enabled FROM reactionrole WHERE guild_id = "{}"'.format(guild.id))
        enabled = self.bot.db.fetchone()
        if enabled:
            if enabled[0]:
                if int(enabled[0]) == 0:
                    return
        if {'user_id': payload.user_id, 'guild_id': guild.id, 'message_id': payload.message_id} in self._user_limiter_dict:
            return
        self.bot.db.execute('SELECT message_id FROM reactionrole WHERE guild_id = {} AND message_id = {}'.format(
            guild.id, payload.message_id))
        message_id = self.bot.db.fetchone()
        if not message_id:
            return
        self.bot.db.execute('SELECT emoji_id FROM reactionrole WHERE guild_id = {} AND message_id = {}'.format(
            guild.id, payload.message_id))
        emoji_id = self.bot.db.fetchone()
        if not emoji_id:
            return
        self.bot.db.execute('SELECT role_id FROM reactionrole WHERE guild_id = {} AND emoji_id = {}'.format(
            guild.id, payload.emoji.id))
        role_id = self.bot.db.fetchone()
        if not role_id:
            return
        role = discord.utils.find(lambda r: str(
            r.id) == str(role_id[0]), guild.roles)
        if not role:
            return self.bot.db.execute('DELETE FROM reactionrole WHERE guild_id = {} AND role_id = {}'.format(role_id[0]))
        if role in payload.member.roles:
            return
        if not guild.me.guild_permissions.manage_roles:
            return
        if int(role.position) >= int(guild.me.top_role.position):
            return
        await payload.member.add_roles(role)
        self._user_limiter_dict.append(
            {'user_id': payload.user_id, 'guild_id': guild.id, 'message_id': payload.message_id})
        await asyncio.sleep(self.USER_REACTION_RATELIMIT)
        self._user_limiter_dict.remove(
            {'user_id': payload.user_id, 'guild_id': guild.id, 'message_id': payload.message_id})

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if not payload.guild_id:
            return
        guild = discord.utils.find(lambda g: str(
            g.id) == str(payload.guild_id), self.bot.guilds)
        if not guild:
            return
        self.bot.db.execute(
            'SELECT enabled FROM reactionrole WHERE guild_id = "{}"'.format(guild.id))
        enabled = self.bot.db.fetchone()
        if enabled:
            if enabled[0]:
                if int(enabled[0]) == 0:
                    return
        member = discord.utils.find(lambda m: str(
            m.id) == str(payload.user_id), guild.members)
        if not member:
            return
        if member.bot:
            return
        if {'user_id': payload.user_id, 'guild_id': guild.id, 'message_id': payload.message_id} in self._user_limiter_dict:
            return
        self.bot.db.execute('SELECT message_id FROM reactionrole WHERE guild_id = {} AND message_id = {}'.format(
            guild.id, payload.message_id))
        message_id = self.bot.db.fetchone()
        if not message_id:
            return
        self.bot.db.execute('SELECT emoji_id FROM reactionrole WHERE guild_id = {} AND message_id = {}'.format(
            guild.id, payload.message_id))
        emoji_id = self.bot.db.fetchone()
        if not emoji_id:
            return
        self.bot.db.execute('SELECT role_id FROM reactionrole WHERE guild_id = {} AND emoji_id = {}'.format(
            guild.id, payload.emoji.id))
        role_id = self.bot.db.fetchone()
        if not role_id:
            return
        role = discord.utils.find(lambda r: str(
            r.id) == str(role_id[0]), guild.roles)
        if not role:
            return self.bot.db.execute('DELETE FROM reactionrole WHERE guild_id = {} AND role_id = {}'.format(role_id[0]))
        if not role in member.roles:
            return
        if not guild.me.guild_permissions.manage_roles:
            return
        if int(role.position) >= int(guild.me.top_role.position):
            return
        await member.remove_roles(role)
        self._user_limiter_dict.append(
            {'user_id': payload.user_id, 'guild_id': guild.id, 'message_id': payload.message_id})
        await asyncio.sleep(self.USER_REACTION_RATELIMIT)
        self._user_limiter_dict.remove(
            {'user_id': payload.user_id, 'guild_id': guild.id, 'message_id': payload.message_id})

    @commands.group(invoke_without_command=True, aliases=['reactrole', 'rr'])
    @commands.guild_only()
    async def reactionrole(self, ctx):
        prefix = self.bot.config._get_prefix(self.bot, ctx)
        embed = discord.Embed(title='Reaction Roles',
                              description=f"**<>** = required\n**[]** = optional",
                              color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None,
                              timestamp=ctx.message.created_at)
        embed.add_field(
            name='Add a reaction role event', value='`{}reactionrole add <role> <emoji> <message>`'.format(prefix))
        embed.add_field(
            name='Enable/disable reaction role events', value='`{}reactionrole toggle`'.format(prefix))
        embed.add_field(
            name='List all reaction role events', value='`{}reactionrole list`'.format(prefix))
        embed.add_field(
            name='Delete all reaction role events', value='`{}reactionrole deleteall`'.format(prefix))
        embed.add_field(
            name='Delete a reaction role event', value='`{}reactionrole delete <event ID>`'.format(prefix))
        await ctx.send(embed=embed)

    @reactionrole.command()
    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_roles=True, add_reactions=True)
    @commands.has_guild_permissions(administrator=True)
    async def add(self, ctx, role: discord.Role, emoji: discord.Emoji, message: discord.Message):
        self.bot.db.execute('SELECT * FROM reactionrole WHERE guild_id = {} AND emoji_id = {} AND role_id = {} AND message_id = {}'.format(
            ctx.guild.id, emoji.id, role.id, message.id))
        result = self.bot.db.fetchone()
        if result and str(emoji.id) in str(message.reactions):
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Emote with that message already exists.'))
        elif result and not str(emoji.id) in str(message.reactions):
            self.bot.db.execute('DELETE FROM reactionrole WHERE guild_id = {} AND emoji_id = {} AND message_id = {}'.format(
                ctx.guild.id, emoji.id, message.id))
        if role.position >= ctx.guild.me.top_role.position:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'I can\'t add roles with the same or higher rank to users.'))
        self.bot.db.execute('INSERT INTO reactionrole (message_id,message_url,emoji_id,emoji_mention,role_id,guild_id) VALUES ("{}","{}","{}","{}","{}","{}")'.format(
            message.id, message.jump_url, emoji.id, str(emoji), role.id, ctx.guild.id))
        await message.add_reaction(emoji)
        self.bot.db.execute('SELECT id FROM reactionrole WHERE guild_id = {} AND emoji_id = "{}" AND message_id = "{}" AND role_id = "{}"'.format(
            ctx.guild.id, emoji.id, message.id, role.id
        ))
        command_id = self.bot.db.fetchone()
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Added reaction role event to message **{}** with emoji {} for role **{}**\n\nEvent ID: **{}**'.format(f'https://discord.com/channels/{ctx.guild.id}/{message.channel.id}/{message.id}', emoji, role.name, command_id[0])))

    @reactionrole.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def toggle(self, ctx):
        self.bot.db.execute(
            'SELECT * FROM reactionrole WHERE guild_id = "{}"'.format(ctx.guild.id))
        result = self.bot.db.fetchall()
        if not result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No reaction role events were found on this server.'))
        self.bot.db.execute(
            'SELECT enabled FROM reactionrole WHERE guild_id = "{}"'.format(ctx.guild.id))
        enabled = self.bot.db.fetchone()
        if not enabled[0]:
            self.bot.db.execute(
                'UPDATE reactionrole SET enabled = 0 WHERE guild_id = "{}"'.format(ctx.guild.id))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Disabled reaction role events'))
        elif enabled[0]:
            if int(enabled[0]) == 0:
                self.bot.db.execute(
                    'UPDATE reactionrole SET enabled = 1 WHERE guild_id = "{}"'.format(ctx.guild.id))
                return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Enabled reaction role events'))
            self.bot.db.execute(
                'UPDATE reactionrole SET enabled = 0 WHERE guild_id = "{}"'.format(ctx.guild.id))
            await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Disabled reaction role events'))

    @reactionrole.command(name='list')
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def _list(self, ctx):
        self.bot.db.execute(
            'SELECT * FROM reactionrole WHERE guild_id = "{}"'.format(ctx.guild.id))
        result = self.bot.db.fetchall()
        if not result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No reaction role events were found on this server.'))
        embed = discord.Embed(description='\n'.join(
            '**Event ID {}**: ({}) {}'.format(str(x[0]), str(x[4]), str(x[2])) for x in result), color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
            None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None)
        embed.set_author(
            name='Total events: {}'.format(len([x for x in result])))
        await ctx.send(embed=embed)

    @reactionrole.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def deleteall(self, ctx):
        self.bot.db.execute(
            'SELECT * FROM reactionrole WHERE guild_id = "{}"'.format(ctx.guild.id))
        result = self.bot.db.fetchall()
        if not result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No reaction role events were found on this server.'))
        self.bot.db.execute(
            'DELETE FROM reactionrole WHERE guild_id = "{}"'.format(ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Deleted **{}** reaction role events'.format(len([x for x in result]))))

    @reactionrole.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def delete(self, ctx, event_id):
        self.bot.db.execute(
            'SELECT * FROM reactionrole WHERE guild_id = "{}"'.format(ctx.guild.id))
        result = self.bot.db.fetchall()
        if not result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No reaction role events were found on this server.'))
        self.bot.db.execute(
            'SELECT * FROM reactionrole WHERE guild_id = "{}" AND id = "{}"'.format(ctx.guild.id, event_id))
        result = self.bot.db.fetchone()
        if not result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No reaction role event with that ID was found.'))
        self.bot.db.execute(
            'DELETE FROM reactionrole WHERE guild_id = "{}" AND id = "{}"'.format(ctx.guild.id, event_id))
        role = discord.utils.find(lambda r: str(
            r.id) == str(result[5]), ctx.guild.roles)
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Deleted reaction role event with emoji {} from **{}** for role **{}**'.format(result[4], result[2], 'N/A' if not role else role.name)))


def setup(bot):
    bot.add_cog(ReactionRole(bot))
