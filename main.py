import os
from discord.ext import commands
from discord_components import DiscordComponents
from discord_slash import SlashCommand
import discord
import json
import mariadb
from datetime import datetime, timezone
from __bot.embeds import Embeds as embeds


# (just used as database name, feel free to change this to anything you want)
BOT_NAME = 'desu'
# if the server doesn't have a custom prefix set, this will be their prefix.
DEFAULT_PREFIX = 'd!'
OWNER_ID = 381843366683344897  # for owner_only commands.
DEV_ID = 381843366683344897


class Database:

    def __init__(self, pool_name):
        self.db = mariadb.ConnectionPool(
            pool_name=pool_name,
            pool_size=50,
            pool_reset_connection=False,
            user='root',
            host='localhost',
            password="",
            database=BOT_NAME, # replace BOT_NAME with "database name"
            port=3306
        )
        self.c1 = self.db.get_connection()
        self.c = self.c1.cursor(buffered=True)
        self.c.execute('SET AUTOCOMMIT=1')
        self.c.execute('''CREATE TABLE IF NOT EXISTS prefixes(
            prefix TEXT,
            guild_id TEXT)''')
        self.c.execute(
            'ALTER DATABASE {} CHARACTER SET utf8 COLLATE utf8_unicode_ci;'.format(BOT_NAME))  # no idea what that does but y not

    def _search_by_id(self, cursor, table, guild_id, id):
        """
        Searches the database for all items with the given id and table.
        """
        cursor.execute(
            'SELECT * FROM {} WHERE guild_id = {} AND id = {}'.format(table, guild_id, id))
        return cursor.fetchone()

    def _search_by_user_id(self, cursor, table, guild_id, user_id):
        """
        Searches the database for all items with the given user id and table.
        """
        cursor.execute(
            'SELECT * FROM {} WHERE guild_id = {} AND user_id = {}'.format(table, guild_id, user_id))
        return cursor.fetchall()

    def _delete_by_id(self, cursor, table, guild_id, id):
        """
        Deletes row from table that contains the given id.
        """
        cursor.execute('DELETE FROM {} WHERE guild_id = "{}" AND id = "{}"'.format(
            table, guild_id, id))

    def _delete_user_records(self,cursor, table, guild_id, user_id):
        """
        Completely purge user's records from a table.
        """
        cursor.execute(
            'DELETE FROM {} WHERE guild_id = {} AND user_id = {}'.format(table, guild_id, user_id))

    def _purge_records(self, cursor, table, guild_id):
        """
        Deletes all records from a guild.
        """
        cursor.execute(
            'DELETE FROM {} WHERE guild_id = {}'.format(table, guild_id))

    def _get_all_records(self, cursor, table, guild_id):
        """
        Gets every record from a guild.
        """
        cursor.execute(
            'SELECT * FROM {} WHERE guild_id = {}'.format(table, guild_id))
        return cursor.fetchall()
    
_db = Database('mainer')
db = _db.c


class Config:

    def __init__(self):
        self.config = self._get_config()

    def _get_config(self):
        with open('config.json', 'r') as config_file:
            return json.load(config_file)

    @staticmethod
    def _get_prefix(bot, ctx):
        """
        Tries to get server's custom prefix.
        Returns DEFAULT_PREFIX if not found.
        """
        try:
            db.execute(
                'SELECT prefix FROM prefixes WHERE guild_id = {}'.format(ctx.guild.id))
            result = db.fetchone()
            if not result:
                return DEFAULT_PREFIX
            return result[0]
        except:
            return DEFAULT_PREFIX

    @staticmethod
    def _set_prefix(ctx, prefix):
        """
        Sets the bot's new server prefix.
        """
        try:
            db.execute(
                'SELECT prefix FROM prefixes WHERE guild_id = {}'.format(ctx.guild.id))
            result = db.fetchone()
            if not result:
                return db.execute(
                    'INSERT INTO prefixes (prefix,guild_id) VALUES ("{}","{}")'.format(prefix, ctx.guild.id))
            db.execute(
                'UPDATE prefixes SET PREFIX = "{}" WHERE guild_id = "{}"'.format(prefix, ctx.guild.id))
        except Exception as e:
            return DEFAULT_PREFIX


config = Config()


bot = commands.AutoShardedBot(command_prefix=config._get_prefix, owner_id=OWNER_ID,
                              intents=discord.Intents.all(), case_insensitive=True,
                              self_bot=False)
bot._db = _db
bot.db = db
bot.config = config
bot.up_since = datetime.now(tz=timezone.utc).strftime('%a, %b %d, %Y %I:%M %p')
bot.OWNER_ID = 381843366683344897  # for owner_only commands.
bot.DEV_ID = 381843366683344897

# set your bots default embed color. Leaving this to None will use the author's color. Putting "random" will use Discord's random colors.
bot.DEFAULT_COLOR = int(bot.config.config['default_color'], 16)


bot.remove_command('help')


@bot.event
async def on_ready():
    DiscordComponents(bot)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='that fly on the wall'))
    print('[client] {} running ({} guilds, {} users)'.format(
        bot.user.name, len(bot.guilds), len(list(bot.get_all_members()))))


@bot.command()
@commands.has_guild_permissions(administrator=True)
@commands.guild_only()
async def setprefix(ctx, *, prefix=None):
    prefix = DEFAULT_PREFIX if not prefix else prefix
    if len(prefix) > 20:
        return await ctx.send(embed=embeds.Error._text_to_embed(bot, ctx, 'Prefix can\'t be longer than 20 characters.'))
    bot.config._set_prefix(ctx, prefix)
    await ctx.send(embed=embeds.Success._text_to_embed(bot, ctx, 'This server\'s prefix was set to **{}**.'.format(prefix)))


def main():
    bot.run(bot.config.config['token'])


if __name__ == '__main__':
    for file in os.listdir('cache'):
        os.remove('cache/' + file)
        print('[cache] {} deleted.'.format(file))
    for file in os.listdir('cogs'):
        if file.endswith(".py") and not file.startswith('_'):
            bot.load_extension('cogs.{}'.format(file[:-3]))
            print('[cogs] {} loaded.'.format(file[:-3]))
    for file in os.listdir('events'):
        if file.endswith(".py") and not file.startswith('_'):
            bot.load_extension('events.{}'.format(file[:-3]))
            print('[events] {} loaded.'.format(file[:-3]))
    main()
