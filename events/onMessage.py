import discord
from discord.ext import commands


class OnMessage(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        
        __omc = self.bot._db.db.get_connection()
        self.on_message_cursor = __omc.cursor(buffered=True)
        self.on_message_cursor.execute('''CREATE TABLE IF NOT EXISTS totalmessages(
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            guild_id TEXT,
            user_id TEXT,
            total TEXT,
            first_message_timestamp TEXT,
                PRIMARY KEY (id))''')

    @commands.Cog.listener()
    async def on_message(self, message):
        if str(message.channel.type) == 'private':
            return
        if message.author.bot:
            return
        self.on_message_cursor.execute('SELECT total FROM totalmessages WHERE guild_id = "{}" AND user_id = "{}"'.format(
            message.guild.id, message.author.id))
        result = self.on_message_cursor.fetchone()
        if not result:
            return self.on_message_cursor.execute('INSERT INTO totalmessages(guild_id,user_id,total,first_message_timestamp) VALUES("{}","{}","{}","{}")'.format(message.guild.id, message.author.id, 1, int(message.created_at.timestamp())))
        self.on_message_cursor.execute('UPDATE totalmessages SET total = "{}" WHERE guild_id = "{}" AND user_id = "{}"'.format(
            int(result[0])+1, message.guild.id, message.author.id))


def setup(bot):
    bot.add_cog(OnMessage(bot))
