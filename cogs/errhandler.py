from discord.ext import commands
import discord
import math

from .help import Help as help
from __bot.embeds import Embeds as embeds


class ErrorHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.help = help(self.bot)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        try:
            try:
                prefix = self.bot.config._get_prefix(self.bot, ctx)
                command_used = str(ctx.message.content).split(' ')[
                    0].replace(prefix, '') if not ' ' in prefix else str(ctx.message.content).split(' ')[
                    1].replace(prefix, '')
                if hasattr(ctx.command, 'on_error'):
                    return
                elif isinstance(error, commands.CommandNotFound):
                    return
                    # await ctx.reply(embed=embeds.Error._text_to_embed(self.bot, ctx, error), delete_after=5)
                elif 'converting to' in str(error).lower():
                    for command_cat in self.help.command_cats:
                        for command_name in self.help.command_cats[command_cat]:
                            for c_name in command_name:
                                if str(command_used) == str(c_name):
                                    embed = embeds.Error._text_to_embed(self.bot, ctx,
                                                                        'Some argument you passed had to be an integer, not string.\n\nHere\'s the correct usage of **{}**: `{}{}`'
                                                                        .format(command_used, prefix, self.help.command_cats[command_cat][0][c_name]['Usage']))
                                    embed.set_footer(
                                        text='Deleting this message in 15s')
                                    await ctx.reply(embed=embed, delete_after=15)
                elif isinstance(error, commands.MissingRequiredArgument):
                    for command_cat in self.help.command_cats:
                        for command_name in self.help.command_cats[command_cat]:
                            for c_name in command_name:
                                if str(command_used) == str(c_name):
                                    embed = embeds.Error._text_to_embed(self.bot, ctx,
                                                                        'You\'re missing arguments: **{}**\n\nHere\'s the correct usage of **{}**: `{}{}`'
                                                                        .format(str(error).replace(' is a required argument that is missing.', ''), command_used, prefix, self.help.command_cats[command_cat][0][c_name]['Usage']))
                                    embed.set_footer(
                                        text='Deleting this message in 15s')
                                    await ctx.reply(embed=embed, delete_after=15)
                elif isinstance(error, commands.EmojiNotFound):
                    await ctx.reply(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Emoji not found.'), delete_after=5)
                elif isinstance(error, commands.BadArgument):
                    for command_cat in self.help.command_cats:
                        for command_name in self.help.command_cats[command_cat]:
                            for c_name in command_name:
                                if str(command_used) == str(c_name):
                                    embed = embeds.Error._text_to_embed(self.bot, ctx,
                                                                        'Looks like a bad argument was passed. Please reenter the command.\n\nHere\'s the correct usage of **{}{}**: `{}{}`'.format(
                                                                            command_used, prefix, self.help.command_cats[command_cat][0][c_name]['Usage']))
                                    embed.set_footer(
                                        text='Deleting this message in 15s')
                                    await ctx.reply(embed=embed, delete_after=15)
                elif isinstance(error, commands.MemberNotFound):
                    await ctx.reply(embed=embeds.Error._text_to_embed(self.bot, ctx, str(error)), delete_after=5)
                elif isinstance(error, commands.MissingPermissions):
                    await ctx.reply(embed=embeds.Error._text_to_embed(self.bot, ctx, str(error)), delete_after=5)
                elif isinstance(error, commands.BotMissingPermissions):
                    await ctx.reply(embed=embeds.Error._text_to_embed(self.bot, ctx, str(error)), delete_after=5)
                elif isinstance(error, commands.CommandOnCooldown):
                    await ctx.reply(embed=embeds.Error._text_to_embed(self.bot, ctx, str(error)), delete_after=5)
                elif isinstance(error, commands.NotOwner):
                    await ctx.reply(embed=embeds.Error._text_to_embed(self.bot, ctx, str(error)), delete_after=5)
                # elif isinstance(error, commands.DisabledCommand):
                #     await ctx.reply(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Command **{}** is currently disabled.'.format(command_used)), delete_after=5
                else:
                    print('[error] {}'.format(str(error).capitalize()))
                    await ctx.reply(embed=embeds.Error._text_to_embed(self.bot, ctx, 'An unhandled error occured! The error was logged. {}'.format(str(error).capitalize())), delete_after=5)
            except Exception as e:
                if 'Replacement index 3' in str(e):
                    return await ctx.reply(embed=embeds.Error._text_to_embed(self.bot, ctx, str(error)), delete_after=5)
                print('[fatal error] {}'.format(str(e).capitalize()))
                await ctx.reply(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Ignoring fatal unhandled error. Error was logged.'), delete_after=5)
        except:
            return


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
