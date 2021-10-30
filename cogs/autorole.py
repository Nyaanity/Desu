from discord.ext import commands
import discord
from __bot.embeds import Embeds as embeds


class Autorole(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.db.execute('''CREATE TABLE IF NOT EXISTS autorole(
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            guild_id TEXT,
            role_id TEXT,
            enabled TEXT,
            botsenabled TEXT,
                PRIMARY KEY (id))''')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not member.guild.me.guild_permissions.manage_roles:
            return
        self.bot.db.execute(
            'SELECT * FROM autorole WHERE guild_id = "{}"'.format(member.guild.id))
        res = self.bot.db.fetchall()
        for result in res:
            if result[4]:
                if int(result[4]) == 0 and member.bot:
                    return
            if result[3]:
                if int(result[3]) == 0:
                    return
            role = discord.utils.find(lambda r: str(
                r.id) == str(result[2]), member.guild.roles)
            if not role:
                return self.bot.db.execute('DELETE FROM autorole WHERE guild_id = "{}" AND role_id = "{}"'.format(member.guild.id, result[2]))
            if role.position >= member.guild.me.top_role.position:
                return
            await member.add_roles(role)

    @commands.group(invoke_without_command=True, aliases=['ar'])
    @commands.guild_only()
    async def autorole(self, ctx):
        prefix = self.bot.config._get_prefix(self.bot, ctx)
        embed = discord.Embed(title='Autorole',
                              description=f"**<>** = required\n**[]** = optional",
                              color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None,
                              timestamp=ctx.message.created_at)
        embed.add_field(
            name='Add a role to autoroling', value='`{}autorole add <role>`'.format(prefix))
        embed.add_field(
            name='Enable/disable autoroling', value='`{}autorole toggle`'.format(prefix))
        embed.add_field(
            name='Enable/disable autoroling for bots', value='`{}autorole togglebots`'.format(prefix))
        embed.add_field(
            name='Remove a role from autoroling', value='`{}autorole remove <role>`'.format(prefix))
        embed.add_field(name='List all autorole roles',
                        value='`{}autorole list`'.format(prefix))
        embed.add_field(
            name='Remove all roles from autoroling', value='`{}autorole removeall`'.format(prefix))
        await ctx.send(embed=embed)

    @autorole.command()
    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.has_guild_permissions(administrator=True)
    async def add(self, ctx, role: discord.Role):
        self.bot.db.execute('SELECT role_id FROM autorole WHERE guild_id = "{}" AND role_id = "{}"'.format(
            ctx.guild.id, role.id))
        role_id = self.bot.db.fetchone()
        if role_id:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This role is already added to autoroling.'))
        if role.position >= ctx.guild.me.top_role.position:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'I can\'t add roles with the same or higher rank to users.'))
        self.bot.db.execute('INSERT INTO autorole (guild_id,role_id) VALUES ("{}","{}")'.format(
            ctx.guild.id, role.id))
        self.bot.db.execute('SELECT id FROM autorole WHERE guild_id = {} AND role_id = "{}"'.format(
            ctx.guild.id, role.id))
        command_id = self.bot.db.fetchone()
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Added role **{}** to autoroling\n\nEvent ID: **{}**'.format(role.name, command_id[0])))

    @autorole.command(name='list')
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def _list(self, ctx):
        self.bot.db.execute(
            'SELECT * FROM autorole WHERE guild_id = "{}"'.format(ctx.guild.id))
        result = self.bot.db.fetchall()
        if not result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No autorole events were found on this server.'))
        embed = discord.Embed(description='\n'.join(
            '**Event ID {}**: {}'.format(str(x[0]), 'N/A' if not str(x[2]) in str([r for r in ctx.guild.roles]) else discord.utils.find(lambda r: str(r.id) == str(x[2]), ctx.guild.roles).name) for x in result), color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
            None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None)
        embed.set_author(
            name='Total events: {}'.format(len([x for x in result])))
        await ctx.send(embed=embed)

    @autorole.command()
    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.has_guild_permissions(administrator=True)
    async def toggle(self, ctx):
        self.bot.db.execute(
            'SELECT * FROM autorole WHERE guild_id = "{}"'.format(ctx.guild.id))
        result = self.bot.db.fetchall()
        if not result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No roles for autoroling were found.'))
        self.bot.db.execute(
            'SELECT enabled FROM autorole WHERE guild_id = "{}"'.format(ctx.guild.id))
        enabled = self.bot.db.fetchone()
        if not enabled[0]:
            self.bot.db.execute(
                'UPDATE autorole SET enabled = 0 WHERE guild_id = "{}"'.format(ctx.guild.id))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Disabled autoroling'))
        elif enabled[0]:
            if int(enabled[0]) == 0:
                self.bot.db.execute(
                    'UPDATE autorole SET enabled = 1 WHERE guild_id = "{}"'.format(ctx.guild.id))
                return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Enabled autoroling'))
            self.bot.db.execute(
                'UPDATE autorole SET enabled = 0 WHERE guild_id = "{}"'.format(ctx.guild.id))
            await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Disabled autoroling'))

    @autorole.command()
    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.has_guild_permissions(administrator=True)
    async def togglebots(self, ctx):
        self.bot.db.execute(
            'SELECT * FROM autorole WHERE guild_id = "{}"'.format(ctx.guild.id))
        result = self.bot.db.fetchall()
        if not result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No roles for autoroling were found.'))
        self.bot.db.execute(
            'SELECT botsenabled FROM autorole WHERE guild_id = "{}"'.format(ctx.guild.id))
        enabled = self.bot.db.fetchone()
        if not enabled[0]:
            self.bot.db.execute(
                'UPDATE autorole SET botsenabled = 1 WHERE guild_id = "{}"'.format(ctx.guild.id))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Enabled autoroling for bots'))
        elif enabled[0]:
            if int(enabled[0]) == 0:
                self.bot.db.execute(
                    'UPDATE autorole SET botsenabled = 1 WHERE guild_id = "{}"'.format(ctx.guild.id))
                return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Enabled autoroling for bots'))
            self.bot.db.execute(
                'UPDATE autorole SET botsenabled = 0 WHERE guild_id = "{}"'.format(ctx.guild.id))
            await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Disabled autoroling for bots'))

    @autorole.command()
    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.has_guild_permissions(administrator=True)
    async def remove(self, ctx, event_id):
        self.bot.db.execute(
            'SELECT * FROM autorole WHERE guild_id = "{}"'.format(ctx.guild.id))
        exists = self.bot.db.fetchone()
        if not exists:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No roles for autoroling were found.'))
        self.bot.db.execute(
            'SELECT * FROM autorole WHERE guild_id = "{}" AND id = "{}"'.format(ctx.guild.id, event_id))
        result = self.bot.db.fetchone()
        if not result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No autorole event with that ID was found.'))
        self.bot.db.execute('DELETE FROM autorole WHERE guild_id = "{}" AND id = "{}"'.format(
            ctx.guild.id, event_id))
        role = discord.utils.find(lambda r: str(
            r.id) == str(result[2]), ctx.guild.roles)
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Removed role **{}** to autoroling'.format('N/A' if not role else role.name)))

    @autorole.command()
    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.has_guild_permissions(administrator=True)
    async def removeall(self, ctx):
        self.bot.db.execute(
            'SELECT * FROM autorole WHERE guild_id = "{}"'.format(ctx.guild.id))
        result = self.bot.db.fetchall()
        if not result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No autorole events were found on this server.'))
        self.bot.db.execute(
            'DELETE FROM autorole WHERE guild_id = "{}"'.format(ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Deleted **{}** autorole events'.format(len([x for x in result]))))


def setup(bot):
    bot.add_cog(Autorole(bot))
