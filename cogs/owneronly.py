import discord
from discord.ext import commands
from discord import Embed
import inspect
from __bot.embeds import Embeds as embeds


col = 0xffffff # sry ausversehen gelöscht idk welche farbe das war xd


class OwnerOnly(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.verified = [851344098597797948]

    @commands.command()
    async def remotedb(self, ctx):
        if ctx.author.id in self.verified:
            await ctx.send(embed=embeds.AwaitInput._text_to_embed(self.bot, ctx, 'Awaiting query...'))
            query = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
            self.bot.db.execute(query.content)
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Done'))
        raise commands.errors.NotOwner(
            message='You are not the owner of this bot.')

    @commands.guild_only()
    @commands.command(help="Enable or disable a command!")
    async def toggle(self, ctx, *, command):
        if ctx.author.id == 851344098597797948:
            command = self.bot.get_command(command)

            if command is None:
                await ctx.send("I can't find a command with that name!")

            elif ctx.command == command:
                await ctx.send("You cannot disable this command.")

            else:
                command.enabled = not command.enabled
                ternary = "Enabled <a:active:878224932843159572>" if command.enabled else "Disabled <a:off:878225677885784114>"
                await ctx.send(f" {ternary} {command.qualified_name}!")

    @commands.command()
    async def purgedb(self, ctx):
        if ctx.author.id in self.verified:
            self.bot.db.execute('SHOW TABLES')
            tables = self.bot.db.fetchall()
            for table in tables:
                self.bot.db.execute('DELETE FROM {}'.format(table[0]))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Purged **{}** tables'.format(len(tables))))
        raise commands.errors.NotOwner(
            message='You are not the owner of this bot.')

    @commands.command()
    async def leave(self, ctx, guild_id: int = None):
        guild_id = ctx.guild.id if not guild_id else guild_id
        if ctx.author.id in self.verified:
            guild = discord.utils.get(self.bot.guilds, id=guild_id)
            await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Bye, **{}**!'.format(guild.name)))
            return await guild.leave()
        raise commands.errors.NotOwner(
            message='You are not the owner of this bot.')

    @commands.command(help="Shows the Guild the bot is in")
    async def serverlist(self, ctx):
        if ctx.author.id == 851344098597797948:
            msg = "\n".join(f"{x}" for x in self.bot.guilds)
            embed = Embed(
                title="",
                description="",
                color=col
            )
            embed.add_field(name="All Bots Guilds", value=f"```\n{msg}\n```")
            await ctx.send(embed=embed)

    @commands.command()
    # a pog way of adding new stuff to the bot without having to restart
    async def loadcog(self, ctx, *, cog):
        if ctx.author.id in self.verified:
            try:
                self.bot.load_extension('cogs.{}'.format(cog))
                return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Loaded extension **{}**'.format(cog)))
            except commands.ExtensionAlreadyLoaded:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Extension **{}** already loaded.'.format(cog)))
            except commands.ExtensionNotFound:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Extension **{}** not found.'.format(cog)))
            except:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Extension **{}** couldn\'t be loaded. Perhaps check the syntax?'.format(cog)))
        raise commands.errors.NotOwner(
            message='You are not the owner of this bot.')

    @commands.command()
    # a even more pog way of disabling corrupt extensions to e.g. fix bugs without having to restart
    async def unloadcog(self, ctx, *, cog):
        if ctx.author.id in self.verified:
            try:
                self.bot.unload_extension('cogs.{}'.format(cog))
                return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Unloaded extension **{}**'.format(cog)))
            except commands.ExtensionNotFound:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Extension **{}** not found.'.format(cog)))
            except:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Extension **{}** couldn\'t be unloaded. Perhaps check the syntax?'.format(cog)))
        raise commands.errors.NotOwner(
            message='You are not the owner of this bot.')

    @commands.command()
    # same as loadcog except its just 1 command
    async def loadcommand(self, ctx, *, command):
        if ctx.author.id in self.verified:
            cmd = self.bot.get_command(command)
            if not cmd:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Command **{}** not found.'.format(command)))
            elif cmd.enabled:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Command **{}** already loaded.'.format(command)))
            elif not cmd.enabled:
                cmd.enabled = True
                return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Command **{}** enabled'.format(command)))
        raise commands.errors.NotOwner(
            message='You are not the owner of this bot.')

    @commands.command()
    # same as unloadcog except its just 1 command
    async def unloadcommand(self, ctx, *, command):
        if ctx.author.id in self.verified:
            cmd = self.bot.get_command(command)
            if not cmd:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Command **{}** not found.'.format(command)))
            elif not cmd.enabled:
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Command **{}** already unloaded.'.format(command)))
            elif cmd.enabled:
                cmd.enabled = False
                return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Command **{}** disabled'.format(command)))
        raise commands.errors.NotOwner(
            message='You are not the owner of this bot.')


def setup(bot):
    bot.add_cog(OwnerOnly(bot))
