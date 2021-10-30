import discord
from discord.ext import commands
from datetime import datetime, timezone
from __bot.embeds import Embeds as embeds


class Roles(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._roleall_limiter_dict = []

    @commands.command(aliases=['delrole'])
    @commands.guild_only()
    @commands.has_guild_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def deleterole(self, ctx, role: discord.Role):
        if not role.position >= ctx.guild.me.top_role.position:
            await role.delete()
            await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Deleted role **{}**'.format(role.name)))
        else:
            await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'I can\'t delete roles with the same or higher rank.'))

    @commands.command(aliases=['remrole', '-role'])
    @commands.guild_only()
    @commands.has_guild_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def removerole(self, ctx, role: discord.Role, member: discord.Member = None):
        member = ctx.author if not member else member
        if not member.guild_permissions.administrator and not member.top_role.position >= ctx.guild.me.top_role.position and not role.position >= ctx.guild.me.top_role.position:
            if not role in member.roles:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This user doesn\'t have this role.'))
            await member.remove_roles(role)
            await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Removed role **{}** from **{}**'.format(role.name, member)))
        else:
            await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, ('I have no permission to remove roles from administrators.' if member.guild_permissions.administrator
                                                                             else 'I have no permission to remove roles from users with the same or higher rank.' if member.top_role.position >= ctx.guild.me.top_role.position
                                                                             else 'I have no permission to remove roles with the same or higher rank.' if role.position >= ctx.guild.me.top_role.position
                                                                             else 'I have no permission to remove that role.')))

    @commands.command(aliases=['addrole', '+role'])
    @commands.guild_only()
    @commands.has_guild_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def giverole(self, ctx, role: discord.Role, member: discord.Member = None):
        member = ctx.author if not member else member
        if not role.position >= ctx.guild.me.top_role.position:
            if role in member.roles:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This user already has this role.'))
            await member.add_roles(role)
            await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Added role **{}** to **{}**'.format(role.name, member)))
        else:
            await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, ('I have no permission to add roles with the same or higher rank.' if role.position >= ctx.guild.me.top_role.position
                                                                             else 'I have no permission to add that role.')))

    @commands.command()
    @commands.guild_only()
    @commands.has_guild_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def rolecolor(self, ctx, role: discord.Role, color='2f3136'):
        if not role.position >= ctx.guild.me.top_role.position:
            try:
                hex_str = str(
                    '0x' + str(color).replace('0x', '').replace('#', ''))
                res = int(hex_str, 16)
                if str(hex(res)).replace('0x', '#') == str(role.color):
                    return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Please actually change the color value.'))
                await role.edit(color=res)
                await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Set the role color of **{}** to **{}**'.format(role.name, str(color).replace('0x', '').replace('#', ''))))
            except:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Please provide a valid color value. Examples: **0x42f563**, **#7242f5**, **f5425a**'))
        else:
            await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, ('I have no permission to edit roles with the same or higher rank.' if role.position >= ctx.guild.me.top_role.position
                                                                             else 'I have no permission to edit that role.')))

    @commands.command()
    @commands.guild_only()
    async def roleinfo(self, ctx, role: discord.Role):
        embed = discord.Embed(
            color=role.color, timestamp=ctx.message.created_at)
        embed.add_field(name='Name',
                        value=role.name)
        embed.add_field(name='Created at', value=datetime.fromtimestamp(role.created_at.timestamp(), tz=timezone.utc).strftime(
            '%a, %b %d, %Y %I:%M %p'))
        embed.add_field(name='Color',
                        value=role.color)
        embed.add_field(name='Mention',
                        value='`{}`'.format(role.mention))
        embed.add_field(name='Position',
                        value=role.position)
        embed.add_field(name='Mentionable',
                        value='Yes' if role.mentionable else 'No')
        embed.add_field(name='Hoisted',
                        value='Yes' if role.hoist else 'No')
        embed.add_field(name='Users with role',
                        value=len([member for member in ctx.guild.members if role in member.roles]))
        embed.set_footer(text='ID: {}'.format(role.id))
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.has_guild_permissions(administrator=True)
    async def roleall(self, ctx, role: discord.Role):
        if not role.position >= ctx.guild.me.top_role.position:
            members = [
                member for member in ctx.guild.members if not role in member.roles]
            if len(members) == 0:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Seems like everyone already has this role.'.format(role.name, len(members))))
            await ctx.send(embed=embeds.Loading._text_to_embed(self.bot, ctx, 'Adding role **{}** to **{}** users...'.format(role.name, len(members))))
            n = 0
            # continue giving roles unless no perms or role deleted.
            while ctx.guild.me.guild_permissions.manage_roles and role in ctx.guild.roles and not role.position >= ctx.guild.me.top_role.position:
                for member in members:
                    if not role in member.roles:
                        await member.add_roles(role)
                    else:
                        n += 1
                break
            else:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Roleall process was cancelled because the role **{}** was either deleted or my permissions were revoked.'.format(role.name)))
            await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Added role **{}** to **{}/{}** users'.format(role.name, len(members), len(members) - n)))
        else:
            await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, ('I have no permission to add roles with the same or higher rank to everyone.' if role.position >= ctx.guild.me.top_role.position
                                                                             else 'I have no permission to add that role to everyone.')))

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.has_guild_permissions(administrator=True)
    async def roleallusers(self, ctx, role: discord.Role):
        if not role.position >= ctx.guild.me.top_role.position:
            members = [
                member for member in ctx.guild.members if not role in member.roles and not member.bot]
            if len(members) == 0:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Seems like everyone already has this role.'.format(role.name, len(members))))
            await ctx.send(embed=embeds.Loading._text_to_embed(self.bot, ctx, 'Adding role **{}** to **{}** members...'.format(role.name, len(members))))
            n = 0
            # continue giving roles unless no perms or role deleted.
            while ctx.guild.me.guild_permissions.manage_roles and role in ctx.guild.roles and not role.position >= ctx.guild.me.top_role.position:
                for member in members:
                    if not role in member.roles:
                        await member.add_roles(role)
                    else:
                        n += 1
                break
            else:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Roleall process was cancelled because the role **{}** was either deleted or my permissions were revoked.'.format(role.name)))
            await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Added role **{}** to **{}/{}** members'.format(role.name, len(members), len(members) - n)))
        else:
            await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, ('I have no permission to add roles with the same or higher rank to everyone.' if role.position >= ctx.guild.me.top_role.position
                                                                             else 'I have no permission to add that role to everyone.')))

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.has_guild_permissions(administrator=True)
    async def roleallbots(self, ctx, role: discord.Role):
        if not role.position >= ctx.guild.me.top_role.position:
            members = [
                member for member in ctx.guild.members if not role in member.roles and member.bot]
            if len(members) == 0:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Seems like everyone already has this role.'.format(role.name, len(members))))
            await ctx.send(embed=embeds.Loading._text_to_embed(self.bot, ctx, 'Adding role **{}** to **{}** bots...'.format(role.name, len(members))))
            n = 0
            # continue giving roles unless no perms or role deleted.
            while ctx.guild.me.guild_permissions.manage_roles and role in ctx.guild.roles and not role.position >= ctx.guild.me.top_role.position:
                for member in members:
                    if not role in member.roles:
                        await member.add_roles(role)
                    else:
                        n += 1
                break
            else:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Roleall process was cancelled because the role **{}** was either deleted or my permissions were revoked.'.format(role.name)))
            await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Added role **{}** to **{}/{}** bots'.format(role.name, len(members), len(members) - n)))
        else:
            await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, ('I have no permission to add roles with the same or higher rank to everyone.' if role.position >= ctx.guild.me.top_role.position
                                                                             else 'I have no permission to add that role to everyone.')))


def setup(bot):
    bot.add_cog(Roles(bot))
