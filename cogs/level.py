from discord import user
from discord.ext import commands
import aiohttp
import discord
from random import randint
import asyncio
import io
from __bot.embeds import Embeds as embeds
from __bot.emojis import Emojis as emojis


class Level(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.LVL_API = 'https://api.no-api-key.com/api/v2/rank'
        self.author_stash = []
        self.XP_ADDABLE_DELAY = 60  # be gone, spammers
        self.bot.db.execute('''CREATE TABLE IF NOT EXISTS level(
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            enabled TEXT,
            guild_id TEXT,
            level_up_channel TEXT,
            level_up_text TEXT,
                PRIMARY KEY (id))''')
        self.bot.db.execute('''CREATE TABLE IF NOT EXISTS levelcache(
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            guild_id TEXT,
            user_id TEXT,
            totalxp TEXT,
            xp_towards_lvl TEXT,
            lvl TEXT,
                PRIMARY KEY (id))''')
        self.bot.db.execute('''CREATE TABLE IF NOT EXISTS levelusernotifyenabled(
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            guild_id TEXT,
            user_id TEXT,
            enabled TEXT,
                PRIMARY KEY (id))''')
        self.bot.db.execute(
            'ALTER TABLE `level` CHANGE `level_up_text` `level_up_text` VARCHAR(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL;')
        self.bot.db.execute(
            'ALTER TABLE `levelcache` CHANGE `totalxp` `totalxp` INT')

    async def gen_xp(self):
        return randint(15, 25)

    async def givetotalxp(self, guild_id, user_id, xp):
        self.bot.db.execute('UPDATE levelcache SET totalxp = "{}" WHERE guild_id = "{}" AND user_id = "{}"'.format(
            xp, guild_id, user_id))

    async def givetowardsxp(self, guild_id, user_id, xp):
        self.bot.db.execute('UPDATE levelcache SET xp_towards_lvl = "{}" WHERE guild_id = "{}" AND user_id = "{}"'.format(
            xp, guild_id, user_id))

    async def lvlup(self, guild_id, user_id, lvl):
        self.bot.db.execute('UPDATE levelcache SET lvl = "{}" WHERE guild_id = "{}" AND user_id = "{}"'.format(
            lvl, guild_id, user_id))

    async def get_towards_xp(self, guild_id, user_id):
        self.bot.db.execute('SELECT xp_towards_lvl FROM levelcache WHERE guild_id = "{}" AND user_id = "{}"'.format(
            guild_id, user_id))
        result = self.bot.db.fetchone()
        return None if not result else int(result[0])

    async def get_total_xp(self, guild_id, user_id):
        self.bot.db.execute('SELECT totalxp FROM levelcache WHERE guild_id = "{}" AND user_id = "{}"'.format(
            guild_id, user_id))
        result = self.bot.db.fetchone()
        return None if not result else int(result[0])

    async def get_lvl(self, guild_id, user_id):
        self.bot.db.execute('SELECT lvl FROM levelcache WHERE guild_id = "{}" AND user_id = "{}"'.format(
            guild_id, user_id))
        result = self.bot.db.fetchone()
        return None if not result else int(result[0])

    async def get_leaderboard_rank(self, guild_id, user_id, startfrom=0):
        self.bot.db.execute(
            'SELECT * FROM levelcache WHERE guild_id = "{}" ORDER BY totalxp DESC'.format(guild_id))
        results = self.bot.db.fetchall()
        if results:
            for result in results:
                startfrom += 1
                if str(result[2]) == str(user_id):
                    return startfrom
        return startfrom

    async def get_leaderboard(self, guild_id):
        self.bot.db.execute(
            'SELECT * FROM levelcache WHERE guild_id = "{}" ORDER BY totalxp DESC LIMIT 10'.format(guild_id))
        results = self.bot.db.fetchall()
        return results

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or str(message.channel.type) == 'private':
            return
        if {'guild_id': message.guild.id, 'user_id': message.author.id} in self.author_stash:
            return
        xp_generated = await self.gen_xp()
        self.author_stash.append(
            {'guild_id': message.guild.id, 'user_id': message.author.id})
        self.bot.db.execute(
            'SELECT * FROM level WHERE guild_id = "{}"'.format(message.guild.id))
        level = self.bot.db.fetchone()
        if level:
            if str(level[1]) == '0':
                await asyncio.sleep(self.XP_ADDABLE_DELAY)
                self.author_stash.remove(
                    {'guild_id': message.guild.id, 'user_id': message.author.id})
                return
        else:
            self.bot.db.execute('INSERT INTO level (enabled,guild_id,level_up_channel,level_up_text) VALUES ("{}","{}","{}","{}")'.format(
                1, message.guild.id, 'N/A', 'GG {membermention}, you just leveled up to lvl **{memberlvl}**! ' + emojis.BLOB_AMUSED))
            self.bot.db.execute(
                'SELECT * FROM level WHERE guild_id = "{}"'.format(message.guild.id))
            level = self.bot.db.fetchone()
        self.bot.db.execute('SELECT * FROM levelcache WHERE guild_id = "{}" AND user_id = "{}"'.format(
            message.guild.id, message.author.id))
        levelcache = self.bot.db.fetchone()
        if not levelcache:
            self.bot.db.execute('INSERT INTO levelcache (guild_id,user_id,totalxp,xp_towards_lvl,lvl) VALUES ("{}","{}","{}","{}","{}")'.format(
                message.guild.id, message.author.id, 0, 0, 0))
            self.bot.db.execute('SELECT * FROM levelcache WHERE guild_id = "{}" AND user_id = "{}"'.format(
                message.guild.id, message.author.id))
            levelcache = self.bot.db.fetchone()
        lvl = int(levelcache[5])
        xptowardslvl = int(levelcache[4])
        totalxp = int(levelcache[3])
        xptowardslvl += xp_generated
        totalxp += xp_generated
        membermention = str(message.author.mention)
        memberfullname = str(message.author)
        membername = str(message.author.name)
        guildname = str(message.guild.name)
        memberid = str(message.author.id)
        membertotalxp = str(totalxp)
        memberlvl = str(lvl+1)
        await self.givetowardsxp(message.guild.id, message.author.id, xptowardslvl)
        await self.givetotalxp(message.guild.id, message.author.id, totalxp)
        required_xp = (5 * (lvl ^ 2) + (50 * lvl) + 100 - xptowardslvl)
        if required_xp <= 0:
            await self.lvlup(message.guild.id, message.author.id, lvl+1)
            await self.givetowardsxp(message.guild.id, message.author.id, 0)
            self.bot.db.execute('SELECT enabled FROM levelusernotifyenabled WHERE guild_id = "{}" AND user_id = "{}"'.format(
                message.guild.id, message.author.id))
            notifier = self.bot.db.fetchone()
            if not notifier:
                lvlchannel = self.bot.get_channel(
                    0 if str(level[3]) == 'N/A' else int(level[3]))
                if lvlchannel:
                    await lvlchannel.send(level[4].format(membermention=membermention, memberfullname=memberfullname, membername=membername, guildname=guildname, memberid=memberid, memberlvl=memberlvl, membertotalxp=membertotalxp))
                else:
                    await message.channel.send(level[4].format(membermention=membermention, memberfullname=memberfullname, membername=membername, guildname=guildname, memberid=memberid, memberlvl=memberlvl, membertotalxp=membertotalxp))
            elif notifier:
                if str(notifier) == '1':
                    lvlchannel = self.bot.get_channel(
                        0 if str(level[3]) == 'N/A' else int(level[3]))
                    if lvlchannel:
                        await lvlchannel.send(level[4].format(membermention=membermention, memberfullname=memberfullname, membername=membername, guildname=guildname, memberid=memberid, memberlvl=memberlvl, membertotalxp=membertotalxp))
                    else:
                        await message.channel.send(level[4].format(membermention=membermention, memberfullname=memberfullname, membername=membername, guildname=guildname, memberid=memberid, memberlvl=memberlvl, membertotalxp=membertotalxp))
        await asyncio.sleep(self.XP_ADDABLE_DELAY)
        self.author_stash.remove(
            {'guild_id': message.guild.id, 'user_id': message.author.id})

    @commands.command(aliases=['level'])
    @commands.guild_only()
    @commands.bot_has_guild_permissions(attach_files=True)
    async def rank(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        self.bot.db.execute(
            'SELECT * FROM level WHERE guild_id = "{}"'.format(ctx.guild.id))
        level = self.bot.db.fetchone()
        if level:
            if str(level[1]) == '0':
                return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'Leveling on this server was disabled by an administrator.'))
        if member.bot:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This user is a bot.'))
        _ = await self.get_total_xp(ctx.guild.id, member.id)
        if not _:
            return await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'This user isn\'t ranked yet.'))
        required_xp = (5 * (await self.get_lvl(ctx.guild.id, member.id) ^ 2) + (50 * await self.get_lvl(ctx.guild.id, member.id)) + 100 - await self.get_towards_xp(ctx.guild.id, member.id))
        async with aiohttp.ClientSession() as session:
            async with session.get(self.LVL_API + '/2?current={}&total={}&rank={}&level={}&discrim={}&username={}&avatar={}&status={}&barFill={}&mainColor={}&background={}'.format(
                await self.get_towards_xp(ctx.guild.id, member.id), required_xp + await self.get_towards_xp(ctx.guild.id, member.id), await self.get_leaderboard_rank(ctx.guild.id, member.id), await self.get_lvl(ctx.guild.id, member.id), member.discriminator, member.name, member.avatar_url_as(format='jpg'), ctx.author.status, 'grey', 'yellow', 'https://cdn.discordapp.com/attachments/652535148008701982/875157736285929552/blackbar.jpg'
            )) as request:
                image = io.BytesIO(await request.read())
                await ctx.send(file=discord.File(image, str(randint(0, 999999999999999)) + '.jpg'))

    @commands.command()
    @commands.guild_only()
    async def leaderboard(self, ctx):
        result = await self.get_leaderboard(ctx.guild.id)
        if not result:
            await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No one here has gained any xp yet.'))
        places = [(emojis.FIRST_PLACE + ' N/A' + f' (**{result[i][3]}** XP, Lvl **{result[i][5]}**)' if not discord.utils.find(lambda m: m.id == int(result[i][2]), ctx.guild.members) else emojis.FIRST_PLACE + discord.utils.find(lambda m: m.id == int(result[i][2]), ctx.guild.members).mention + f' (**{result[i][3]}** XP, Lvl **{result[i][5]}**)') if i == 0 else
                  (emojis.SECOND_PLACE + ' N/A' + f' (**{result[i][3]}** XP, Lvl **{result[i][5]}**)' if not discord.utils.find(lambda m: m.id == int(result[i][2]), ctx.guild.members) else emojis.SECOND_PLACE + discord.utils.find(lambda m: m.id == int(result[i][2]), ctx.guild.members).mention + f' (**{result[i][3]}** XP, Lvl **{result[i][5]}**)') if i == 1 else
                  (emojis.THIRD_PLACE + ' N/A' + f' (**{result[i][3]}** XP, Lvl **{result[i][5]}**)\n' if not discord.utils.find(lambda m: m.id == int(result[i][2]), ctx.guild.members) else emojis.THIRD_PLACE + discord.utils.find(lambda m: m.id == int(result[i][2]), ctx.guild.members).mention + f' (**{result[i][3]}** XP, Lvl **{result[i][5]}**)\n') if i == 2 else
                  (' N/A' + f' (**{result[i][3]}** XP, Lvl **{result[i][5]}**)' if not discord.utils.find(lambda m: m.id == int(result[i][2]), ctx.guild.members)
                   else discord.utils.find(lambda m: m.id == int(result[i][2]), ctx.guild.members).mention + f' (**{result[i][3]}** XP, Lvl **{result[i][5]}**)')
                  for i in range(len(result))]
        embed = discord.Embed(title='Top 10 XP Leaderboard', description='\n'.join(place for place in places), color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None)
        await ctx.send(embed=embed)

    @commands.command(aliases=['toggleranknotify', 'togglelvlnotify'])
    @commands.guild_only()
    async def togglelevelnotify(self, ctx):
        self.bot.db.execute(
            'SELECT * FROM levelusernotifyenabled WHERE guild_id = "{}" AND user_id = "{}"'.format(ctx.guild.id, ctx.author.id))
        result = self.bot.db.fetchone()
        if not result:
            self.bot.db.execute('INSERT INTO levelusernotifyenabled (guild_id,user_id,enabled) VALUES("{}","{}","{}")'.format(
                ctx.guild.id, ctx.author.id, 0))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Disabled** your level up notification. When leveling up, you\'ll now not get notified on this server anymore.'))
        if str(result[3]) == '1':
            self.bot.db.execute('UPDATE levelusernotifyenabled SET enabled = "{}" WHERE guild_id ="{}" AND user_id = "{}"'.format(
                0, ctx.guild.id, ctx.author.id))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Disabled** your level up notification. When leveling up, you\'ll now not get notified on this server anymore.'))
        self.bot.db.execute('UPDATE levelusernotifyenabled SET enabled = "{}" WHERE guild_id ="{}" AND user_id = "{}"'.format(
            1, ctx.guild.id, ctx.author.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Enabled** your level up notification. When leveling up, you\'ll now not get notified on this server anymore.'))

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def leveling(self, ctx):
        prefix = self.bot.config._get_prefix(self.bot, ctx)
        embed = discord.Embed(title='Leveling',
                              description=f"**<>** = required\n**[]** = optional",
                              color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                              None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None,
                              timestamp=ctx.message.created_at)
        embed.add_field(
            name='Set a level up notification channel', value='`{}leveling channel <channel>`'.format(prefix))
        embed.add_field(
            name='Set a custom level up notification text', value='`{}leveling text`'.format(prefix))
        embed.add_field(
            name='Toggle leveling on this server', value='`{}leveling toggle`'.format(prefix))
        await ctx.send(embed=embed)

    @leveling.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def channel(self, ctx, channel: discord.TextChannel = None):
        channel = ctx.channel if not channel else channel
        self.bot.db.execute(
            'SELECT level_up_channel FROM level WHERE guild_id = "{}"'.format(ctx.guild.id))
        level_channel = self.bot.db.fetchone()
        if not level_channel:
            self.bot.db.execute('INSERT INTO level (level_up_channel,guild_id,level_up_text,enabled) VALUES ("{}","{}","{}","{}")'.format(
                channel.id, ctx.guild.id, 'GG {membermention}, you just leveled up to lvl **{memberlvl}**! ' + emojis.BLOB_AMUSED, 1))
        elif level_channel:
            self.bot.db.execute('UPDATE level SET level_up_channel = "{}" WHERE guild_id = "{}"'.format(
                channel.id, ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Set the level up notification channel to {}'.format(channel.mention)))

    @leveling.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def text(self, ctx):
        await ctx.send(embed=embeds.AwaitInput._text_to_embed(self.bot, ctx, 'Please enter the text that should be sent when members level up. Enter **cancel** to cancel.\n\nYou may include **{membermention}**, **{memberfullname}**, **{membername}**, **{guildname}**, **{memberid}** and **{membertotalxp}** to format the sent text.'))
        while 1:
            lvl_text_msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
            if str(lvl_text_msg.content) == 'cancel':
                return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Cancelled'))
            lvl_text = lvl_text_msg.content
            break
        self.bot.db.execute(
            'SELECT level_up_text FROM level WHERE guild_id = "{}"'.format(ctx.guild.id))
        level_text = self.bot.db.fetchone()
        if not level_text:
            self.bot.db.execute('INSERT INTO level (level_up_channel,guild_id,level_up_text,enabled) VALUES ("{}","{}","{}","{}")'.format(
                'N/A', ctx.guild.id, lvl_text, 1))
        elif level_text:
            self.bot.db.execute('UPDATE level SET level_up_text = "{}" WHERE guild_id = "{}"'.format(
                lvl_text, ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, 'Updated the level up text'))

    @leveling.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def toggle(self, ctx):
        self.bot.db.execute(
            'SELECT * FROM level WHERE guild_id = "{}"'.format(ctx.guild.id))
        result = self.bot.db.fetchone()
        if not result:
            self.bot.db.execute('INSERT INTO level (level_up_channel,guild_id,level_up_text,enabled) VALUES ("{}","{}","{}","{}")'.format(
                'N/A', ctx.guild.id, 'GG {membermention}, you just leveled up to lvl **{memberlvl}**!  <a:omg:894221102203670549>', 0))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Disabled** leveling on this server'))
        if str(result[1]) == '1':
            self.bot.db.execute('UPDATE level SET enabled = "{}" WHERE guild_id ="{}"'.format(
                0, ctx.guild.id))
            return await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Disabled** leveling on this server'))
        self.bot.db.execute('UPDATE level SET enabled = "{}" WHERE guild_id ="{}"'.format(
            1, ctx.guild.id))
        await ctx.send(embed=embeds.Success._text_to_embed(self.bot, ctx, '**Enabled** leveling on this server'))


def setup(bot):
    bot.add_cog(Level(bot))
