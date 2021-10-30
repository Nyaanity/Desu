from discord.ext import commands
import discord
import re
from datetime import datetime, timezone
from __bot.embeds import Embeds as embeds


class Selfbotblock(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.db.execute('''CREATE TABLE IF NOT EXISTS selfbotblock(
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            guild_id TEXT,
            enabled TEXT,
            action TEXT,
                PRIMARY KEY (id))''')

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.embeds:
            return
        urls = re.findall(
            'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.content.lower())
        if urls:
            return
        if message.author.bot:
            return
        if str(message.channel.type) == 'private':
            return
        if message.author.top_role.position >= message.guild.me.top_role.position or message.author.guild_permissions.administrator:
            return

        self.bot.db.execute(
            'SELECT * FROM selfbotblock WHERE guild_id = "{}"'.format(message.guild.id))
        result = self.bot.db.fetchone()
        if result:
            if str(result[2]) == 'N/A' or str(result[3]) == 'N/A':
                return
            elif str(result[2]) == '1':
                if str(result[3]) == 'delete':
                    await message.reply(message.author.mention + ', please refrain from using selfbots.', delete_after=5)
                    await message.delete()
                elif str(result[3]) == 'ban':
                    if not message.guild.me.guild_permissions.ban_members or message.author.top_role.position >= message.guild.me.top_role.position:
                        return
                    punished_at = int(datetime.now(
                        tz=timezone.utc).timestamp())
                    self.bot.db.execute(
                        'INSERT INTO moderation(action,sanctioned_by,sanctioned_by_id,user,user_id,punished_at,punished_until,reason,guild_id) VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format('Ban',
                                                                                                                                                                                                            self.bot.user.name + '#' +
                                                                                                                                                                                                            str(
                                                                                                                                                                                                                self.bot.user.discriminator),
                                                                                                                                                                                                            self.bot.user.id,
                                                                                                                                                                                                            message.author.name + '#' +
                                                                                                                                                                                                            str(
                                                                                                                                                                                                                message.author.discriminator),
                                                                                                                                                                                                            message.author.id,
                                                                                                                                                                                                            punished_at,
                                                                                                                                                                                                            'N/A',
                                                                                                                                                                                                            'Selfbot Protection: Sent illegal embed',
                                                                                                                                                                                                            message.guild.id))
                    await message.author.ban(reason='Selfbot Protection: Sent illegal embed')
                    await message.delete()
                elif str(result[3]) == 'kick':
                    if not message.guild.me.guild_permissions.kick_members or message.author.top_role.position >= message.guild.me.top_role.position:
                        return
                    punished_at = int(datetime.now(
                        tz=timezone.utc).timestamp())
                    self.bot.db.execute(
                        'INSERT INTO moderation(action,sanctioned_by,sanctioned_by_id,user,user_id,punished_at,punished_until,reason,guild_id) VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format('Kick',
                                                                                                                                                                                                            self.bot.user.name + '#' +
                                                                                                                                                                                                            str(
                                                                                                                                                                                                                self.bot.user.discriminator),
                                                                                                                                                                                                            self.bot.user.id,
                                                                                                                                                                                                            message.author.name + '#' +
                                                                                                                                                                                                            str(
                                                                                                                                                                                                                message.author.discriminator),
                                                                                                                                                                                                            message.author.id,
                                                                                                                                                                                                            punished_at,
                                                                                                                                                                                                            'N/A',
                                                                                                                                                                                                            'Selfbot Protection: Sent illegal embed',
                                                                                                                                                                                                            message.guild.id))
                    await message.author.kick(reason='Selfbot Protection: Sent illegal embed')
                    await message.delete()
                elif str(result[3]) == 'mute':
                    if not message.guild.me.guild_permissions.manage_roles or message.author.top_role.position >= message.guild.me.top_role.position or not 'muted' in [str(x.name).lower() for x in message.guild.roles]:
                        return
                    muted_role = [
                        x for x in message.guild.roles if 'muted' in str(x.name).lower()][0]
                    if muted_role.position > message.guild.me.top_role.position:
                        return
                    punished_at = int(datetime.now(
                        tz=timezone.utc).timestamp())
                    self.bot.db.execute(
                        'INSERT INTO moderation(action,sanctioned_by,sanctioned_by_id,user,user_id,punished_at,punished_until,reason,guild_id) VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format('Mute',
                                                                                                                                                                                                            self.bot.user.name + '#' +
                                                                                                                                                                                                            str(
                                                                                                                                                                                                                self.bot.user.discriminator),
                                                                                                                                                                                                            self.bot.user.id,
                                                                                                                                                                                                            message.author.name + '#' +
                                                                                                                                                                                                            str(
                                                                                                                                                                                                                message.author.discriminator),
                                                                                                                                                                                                            message.author.id,
                                                                                                                                                                                                            punished_at,
                                                                                                                                                                                                            'N/A',
                                                                                                                                                                                                            'Selfbot Protection: Sent illegal embed',
                                                                                                                                                                                                            message.guild.id))
                    await message.author.add_roles(muted_role, reason='Selfbot Protection: Sent illegal embed')
                    await message.delete()
                elif str(result[3]) == 'warn':
                    if message.author.top_role.position >= message.guild.me.top_role.position:
                        return
                    punished_at = int(datetime.now(
                        tz=timezone.utc).timestamp())
                    self.bot.db.execute(
                        'INSERT INTO moderation(action,sanctioned_by,sanctioned_by_id,user,user_id,punished_at,punished_until,reason,guild_id) VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format('Warn',
                                                                                                                                                                                                            self.bot.user.name + '#' +
                                                                                                                                                                                                            str(
                                                                                                                                                                                                                self.bot.user.discriminator),
                                                                                                                                                                                                            self.bot.user.id,
                                                                                                                                                                                                            message.author.name + '#' +
                                                                                                                                                                                                            str(
                                                                                                                                                                                                                message.author.discriminator),
                                                                                                                                                                                                            message.author.id,
                                                                                                                                                                                                            punished_at,
                                                                                                                                                                                                            'N/A',
                                                                                                                                                                                                            'Selfbot Protection: Sent illegal embed',
                                                                                                                                                                                                            message.guild.id))
                    await message.reply(message.author.mention + ', please refrain from using selfbots.', delete_after=5)
                    await message.delete()
                else:
                    ...

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def antiselfbot(self, ctx):
        prefix = self.bot.config._get_prefix(self.bot, ctx)
        embed = discord.Embed(title='Selfbot Protection',
                              description=f"**<>** = required\n**[]** = optional",
                              color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None,
                              timestamp=ctx.message.created_at)
        embed.add_field(
            name='Enable/disable selfbot protection', value='`{}antiselfbot toggle`'.format(prefix))
        embed.add_field(
            name='Set an action if a selfbot is detected', value='`{}antiselfbot action <warn/mute/kick/delete/ban>`'.format(prefix))
        embed.add_field(
            name='Delete the anti-spam config', value='`{}antiselfbot delete`'.format(prefix))
        await ctx.send(embed=embed)

    @antiselfbot.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def toggle(self, ctx):
        self.bot.db.execute(
            'SELECT * FROM selfbotblock WHERE guild_id = "{}"'.format(ctx.guild.id))
        result = self.bot.db.fetchone()
        if not result:
            self.bot.db.execute('INSERT INTO selfbotblock(guild_id,enabled,action) VALUES("{}","{}","{}")'.format(
                ctx.guild.id, 1, 'N/A'))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Enabled** selfbot protection'))
        if str(result[2]) == '1':
            self.bot.db.execute('UPDATE selfbotblock SET enabled = "{}" WHERE guild_id = "{}"'.format(
                0, ctx.guild.id))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Disabled** selfbot protection'))
        self.bot.db.execute('UPDATE selfbotblock SET enabled = "{}" WHERE guild_id = "{}"'.format(
            1, ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Enabled** selfbot protection'))

    @antiselfbot.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def action(self, ctx, action):
        actions = ['warn', 'mute', 'kick', 'delete', 'ban']
        if not action in actions:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Please only use **warn**, **kick**, **delete**, **ban** or **mute**.'))
        self.bot.db.execute(
            'SELECT * FROM selfbotblock WHERE guild_id = "{}"'.format(ctx.guild.id))
        result = self.bot.db.fetchone()
        if not result:
            self.bot.db.execute('INSERT INTO selfbotblock(guild_id,enabled,action) VALUES("{}","{}","{}")'.format(
                ctx.guild.id, 'N/A', action))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Set the selfbot protection action to **{}**'.format(action)))
        self.bot.db.execute('UPDATE selfbotblock SET action = "{}" WHERE guild_id ="{}"'.format(
            action, ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Set the selfbot protection action to **{}**'.format(action)))

    @antiselfbot.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def delete(self, ctx):
        self.bot.db.execute(
            'SELECT * FROM selfbotblock WHERE guild_id = "{}"'.format(ctx.guild.id))
        result = self.bot.db.fetchone()
        if not result:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This server doesn\'t have a selfbot protection config set.'))
        self.bot.db.execute(
            'DELETE FROM selfbotblock WHERE guild_id = "{}"'.format(ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Deleted** the selfbot protection config'))


def setup(bot):
    bot.add_cog(Selfbotblock(bot))
