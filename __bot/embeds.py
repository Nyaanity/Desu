from discord import Embed, Color
from __bot.emojis import Emojis as emojis


green = 0x03fc52
red = 0xf00c0c
invisible = 0x2f3134


class Embeds(object):
    """
    All generally used embeds for the bot.
    """

    class Error(object):

        @staticmethod
        def _text_to_embed(bot, ctx, text):
            """
            Returns a small red error looking embed.
            """
            return Embed(description='{} {}'.format(
                emojis.NO_TICK, text), color=red)

    class Success(object):

        @staticmethod
        def _text_to_embed(bot, ctx, text):
            """
            Returns a small green success looking embed.
            """
            return Embed(description='{} {}'.format(emojis.YES_TICK, text), color=green)

    class Loading(object):

        @staticmethod
        def _text_to_embed(bot, ctx, text):
            """
            Returns a small loading looking embed.
            """
            return Embed(description='{} {}'.format(emojis.LOADING, text), color=invisible)

    class Soft(object):

        @staticmethod
        def _text_to_embed(bot, ctx, text):
            """
            Returns a small loading looking embed.
            """
            return Embed(description='{}'.format(text), color=invisible)

    class Warning(object):

        @staticmethod
        def _text_to_embed(bot, ctx, text):
            """
            Returns a small warning looking embed.
            """
            return Embed(description='{} {}'.format(emojis.WARNING, text), color=invisible)

    class AwaitInput(object):

        @staticmethod
        def _text_to_embed(bot, ctx, text):
            """
            Returns a small embed waiting for user to send a message.
            """
            return Embed(description='{} {}'.format(emojis.SIP, text), color=invisible)

    class TitleImage(object):

        @staticmethod
        def _text_to_embed(bot, ctx, text, image_url):
            """
            Returns a simple title-and-image embed.
            """
            emb = Embed(title=text, color=bot.DEFAULT_COLOR if bot.DEFAULT_COLOR !=
                        None and bot.DEFAULT_COLOR != 'random' else Color.random() if bot.DEFAULT_COLOR == 'random' else ctx.author.color if not bot.DEFAULT_COLOR else None, timestamp=ctx.message.created_at)
            emb.set_image(url=image_url)
            return emb

    class DescriptionImage(object):

        @staticmethod
        def _text_to_embed(bot, ctx, text, image_url):
            """
            Returns a simple description-and-image embed.
            """
            emb = Embed(description=text, color=bot.DEFAULT_COLOR if bot.DEFAULT_COLOR !=
                        None and bot.DEFAULT_COLOR != 'random' else Color.random() if bot.DEFAULT_COLOR == 'random' else ctx.author.color if not bot.DEFAULT_COLOR else None, timestamp=ctx.message.created_at)
            emb.set_image(url=image_url)
            return emb
