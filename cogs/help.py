import discord
from discord.ext import commands
from __bot.embeds import Embeds as embeds


class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.command_cats = {  # way more overview over your commands instead of having to create a new command for everything.
            "Moderation": [{
                "fetchalts": {
                    "Description": "List all accounts that are younger than the specified creation date.",
                    "Usage": "fetchalts <age in days>"
                },
                "audit": {
                    "Description": "Set up logging for this server.",
                    "Usage": "audit"
                },
                "nuke": {
                    "Description": "Nuke a channel and delete all their messages.",
                    "Usage": "nuke"
                },
                "court": {
                    "Description": "Bring users to court. Discuss which punishment they shall receive.",
                    "Usage": "court"
                },
                "case": {
                    "Description": "Investigate a punishment using the case ID.",
                    "Usage": "case <case ID>"
                },
                "deletecase": {
                    "Description": "Delete a case ID and its records.",
                    "Usage": "deletecase <case ID>",
                },
                "purgecases": {
                    "Description": "Completely clear this guild's case records.",
                    "Usage": "purgecases",
                },
                "clearcases": {
                    "Description": "Clear a user's cases.",
                    "Usage": "clearcases [member]"
                },
                "cases": {
                    "Description": "View a user's total cases.",
                    "Usage": "cases [member]"
                },
                "ban": {
                    "Description": "Ban a user.",
                    "Usage": "ban <member> [reason]",
                    "Aliases": ["ara ara~ sayonara"]
                },
                "kick":{
                    "Description": "Kick a user.",
                    "Usage": "kick <member> [reason]"
                },
                "bans": {
                    "Description": "View this guild's bans.",
                    "Usage": "bans"
                },
                "unban": {
                    "Description": "Unban a user.",
                    "Usage": "unban <id/tag>"
                },
                "softban": {
                    "Description": "Ban a user and immediately unban them to delete their messages..",
                    "Usage": "softban <member>"
                },
                "warn": {
                    "Description": "Warn a user.",
                    "Usage": "warn <member> [reason]"
                },
                "warnings": {
                    "Description": "View a user's warnings.",
                    "Usage": "warnings [member]",
                    "Aliases": ["warns"]
                },
                "clearwarnings": {
                    "Description": "Clear a user's warnings.",
                    "Usage": "clearwarnings [member]",
                    "Aliases": ["clearwarns"]
                },
                "tempban": {
                    "Description": "Temporarily ban a user.",
                    "Usage": "tempban <member> <duration: s|m|h|d|w|y> [reason]"
                },
                "clear": {
                    "Description": "Clear the chat.",
                    "Usage": "clear [amount]",
                    "Aliases": ['purge']
                },
                "clearfrom": {
                    "Description": "Clear the whole chat history of a user.",
                    "Usage": "clearfrom [member]",
                    "Aliases": ['purgefrom']
                },
                "mute": {
                    "Description": "Mute a user.",
                    "Usage": "mute <member> [reason]",
                    "Aliases": ['silence', 'shut']
                },
                "tempmute": {
                    "Description": "Temporarily mute a user.",
                    "Usage": "tempmute <member> <duration: s|m|h|d|w|y> [reason]"
                },
                "unmute": {
                    "Description": "Unmute a user.",
                    "Usage": "unmute [member]"
                },
                "lockdown": {
                    "Description": "Toggle lockdown for a channel. This only affects the default role @everyone.",
                    "Usage": "lockdown [channel]",
                    "Aliases": ["lock"]
                },
                "slowmode": {
                    "Description": "Set slowmode in a channel.",
                    "Usage": "slowmode [delay] [channel]"
                },
                "dm": {
                    "Description": "Send a user a staff dm.",
                    "Usage": "dm <member> <message>",
                    "Cooldown": "300"
                },
                "adm": {
                    "Description": "Send a user an anonymous staff dm. The user will not see the author.",
                    "Usage": "adm <member> <message>",
                    "Cooldown": "300"
                },
                "unbanall": {
                    "Description": "Unban all users that are currently banned on this server.",
                    "Usage": "unbanall",
                    "Cooldown": "300"
                },
                "rename": {
                    "Description": "Rename a user.",
                    "Usage": "rename <member> [name]",
                    "Aliases": ["nick"]
                },
                "banid": {
                    "Description": "Ban a user before they even get to join.",
                    "Usage": "banid <id> [reason]"
                },
                "clearuntil": {
                    "Description": "Clear a channel until the specified message.",
                    "Usage": "clearuntil <messageid>",
                    "Aliases": ["purgeuntil"]
                },
                "clearfromto": {
                    "Description": "Clear a specific part of the channel.",
                    "Usage": "clearfromto <message: from> <message: until>",
                    "Aliases": ["purgefromto"]
                },
                "nukefrom": {
                    "Description": "Nuke the entire message history of a member.",
                    "Usage": "nukefrom [member]"
                },
                "lockrole": {
                    "Description": "Toggle lockdown for a channel. This only affects the given role.",
                    "Usage": "lockrole <role> [channel]"
                }
            }],
            "Leveling": [{
                "rank": {
                    "Description": "View your level on this server.",
                    "Usage": "rank [member]",
                    "Aliases": "level"
                },
                "leaderboard": {
                    "Description": "View this server\'s top 10 leaderboard.",
                    "Usage": "leaderboard"
                },
                "togglelevelnotify": {
                    "Description": "Don\'t want to get pinged when leveling up? Disable your level up notification.",
                    "Usage": "togglelevelnotify",
                    "Aliases": ['toggleranknotify', 'togglelvlnotify']
                },
                "leveling": {
                    "Description": "Advanced leveling commands.",
                    "Usage": "leveling"
                }
            }],
            "Automod": [{
                "autopurge": {
                    "Description": "Set a channel whose messages should be completely deleted regularly.",
                    "Usage": "autopurge"
                },
                "antiselfbot": {
                    "Description": "Detect members sending embeds. Normal users can\'t send embeds without using a modified client.",
                    "Usage":  "antiselfbot"
                },
                "joinblock": {
                    "Description": "Instantly ban members that try to join the server.",
                    "Usage": "joinblock"
                },
                "maxinfractions": {
                    "Description": "Set a warn limit and an action if someone exceeds that limit.",
                    "Usage": "maxinfractions"
                },
                "antialt": {
                    "Description": 'Prevent alt-accounts from joining this server. This will first kick the user if "kick" was chosen as an action, then ban them if they attempt to join again without meeting the join requirement.',
                    "Usage": "antialt"
                },
                "antispam": {
                    "Description": "Prevent users from spamming the chat.",
                    "Usage": "antispam"
                },
                "antispamv2": {
                    "Description": "Prevent potential scammers from spamming fake links in every channel.",
                    "Usage": "antispamv2"
                },
                "linkblock": {
                    "Description": "Prevent members from sending links into any chat.",
                    "Usage": "linkblock"
                },
                "banword": {
                    "Description": "Automatically delete messages that include a specific word.",
                    "Usage": "banword"
                },
                "banwordstrict": {
                    "Description": "Automatically delete messages that equal a specific word.",
                    "Usage": "banwordstrict"
                }
            }],
            "Roles": [{
                "deleterole": {
                    "Description": "Delete a role from this server.",
                    "Usage": "deleterole <role>",
                    "Aliases": ["delrole"]
                },
                "removerole": {
                    "Description": "Remove a role from a user.",
                    "Usage": "removerole <role> [member]",
                    "Aliases": ["remrole", "-role"]
                },
                "giverole": {
                    "Description": "Add a role to a user.",
                    "Usage": "giverole <role> [member]",
                    "Aliases": ["+role", "addrole"]
                },
                "roleall": {
                    "Description": "Add a role to all users on this server (including bots).",
                    "Usage": "roleall <role>"
                },
                "roleallusers": {
                    "Description": "Add a role to all users on this server (members only).",
                    "Usage": "roleallusers <role>",
                },
                "roleallbots": {
                    "Description": "Add a role to all users in this server (bots only).",
                    "Usage": "roleallbots <role>"
                },
                "roleinfo": {
                    "Description": "Get information about a role.",
                    "Usage": "roleinfo <role>"
                },
                "rolecolor": {
                    "Description": "Change the color of a role.",
                    "Usage": "rolecolor <role> <hex value>"
                },
                "reactionrole": {
                    "Description": "Add a reaction role event to a message.",
                    "Usage": "reactionrole",
                    "Aliases": ["reactrole", "rr"]
                },
                "autorole": {
                    "Description": "Set up autoroling for this server.",
                    "Usage": "autorole",
                    "Aliases": ["ar"]
                }
            }],
            "Guild": [{
                "ticket": {
                    "Description": "Set up a ticket system for your server.",
                    "Usage": "ticket"
                },
                "members": {
                    "Description": "Get the total members and their statuses in this server.",
                    "Usage": "members",
                    "Aliases": ["users"]
                },
                "customcommand": {
                    "Description": "Set up custom commands for your server.",
                    "Usage": "customcommand"
                },
                "serverinfo": {
                    "Description": "Get information about this server.",
                    "Usage": "serverinfo",
                    "Aliases": ["guildinfo"]
                },
                "channelinfo": {
                    "Description": "Get information about a channel.",
                    "Usage": "channelinfo [channel]"
                },
                "welcome": {
                    "Description": "Welcome new members.",
                    "Usage": "welcome",
                    "Aliases": ["greet"]
                },
                "autosupport": {
                    "Description": "Set up autosupport commands for your server.",
                    "Usage": "autosupport"
                }
            }],
            "Miscellaneous": [{
                "utcnow": {
                    "Description": "Get the time elapsed in seconds (UTC) since 1970.",
                    "Usage": "utcnow"
                },
                "firstmessage": {
                    "Description": "Get a user\'s first sent message. This does not detect any messages that were already deleted or not visible to the bot. This command\'s main purpose is to get the oldest message of a member that is not in this server anymore.",
                    "Usage": "firstmessage <member ID>",
                    "Aliases": ['firstmsg', 'oldestmsg', 'oldestmessage']
                },
                "whoplays": {
                    "Description": "Search for a game by word that users are currently playing.",
                    "Usage": "whoplays <game>"
                },
                "botinfo": {
                    "Description": "Get some of this bot\'s information.",
                    "Usage": "botinfo"
                },
                "doujin": {
                    "Description": "Find a random doujin.",
                    "Usage": "doujin"
                },
                "viewcolor": {
                    "Description": "View a hex\'s color.",
                    "Usage": "viewcolor <hex>"
                },
                "totalmessages": {
                    "Description": "Get total messages sent by a user since this bot is in this server.",
                    "Usage": "totalmessages [member]"
                },
                "voiceest": {
                    "Description": "Get the total time spent in voice chat since this bot is in this server.",
                    "Usage": "voiceest [member]"
                },
                "genpass": {
                    "Description": "Generate a random and secure password.",
                    "Usage": "genpass [length]"
                },
                "gencaptcha": {
                    "Description": "Generate a random captcha image.",
                    "Usage": "gencaptcha [length]"
                },
                "embed": {
                    "Description": "Send an embed message.",
                    "Usage": "embed <message>",
                    "Aliases": ["emb"]
                },
                "emotes": {
                    "Description": "Get this guild's emotes.",
                    "Usage": "emotes",
                    "Aliases": ["emojis"]
                },
                "say": {
                    "Description": "Say a message.",
                    "Usage": "say <message>"
                },
                "nyanify": {
                    "Description": "Make your message look a little bit more.. adorable.",
                    "Usage": "nyanify <message>"
                },
                "steal": {
                    "Description": "Get the link of an emote.",
                    "Usage": "steal <emote>",
                    "Aliases": ["emoji", "emote"]
                },
                "ping": {
                    "Description": "Get this bot's or a domain's ping.",
                    "Usage": "ping [domain]"
                },
                "setprefix": {
                    "Description": "Change this bot's server prefix.",
                    "Usage": "setprefix [prefix]"
                },
                "av": {
                    "Description": "Get a user's avatar.'",
                    "Usage": "av [member]",
                    "Aliases": ["pfp", "avatar"]
                },
                "userinfo": {
                    "Description": "Get user information.",
                    "Usage": "userinfo [member]"
                },
                "joinedat": {
                    "Description": "Get a user\'s joined at date.",
                    "Usage": "joinedat [member]"
                },
                "createdat": {
                    "Description": "Get a user\'s created at date.",
                    "Usage": "createdat [member]"
                },
                "react": {
                    "Description": "Add a reaction to a message.",
                    "Usage": "react <emoji> [message]"
                },
                "ascii": {
                    "Description": "Convert text to ascii art.",
                    "Usage": "ascii <text>"
                },
                "emojify": {
                    "Description": "Convert text to emojis.",
                    "Usage": "emojify <text>"
                },
                "invite": {
                    "Description": "Get this bot\'s OAuth2 invite link.",
                    "Usage": "invite"
                },
                "uptime": {
                    "Description": "Get the exact date the bot is online since.",
                    "Usage": "uptime"
                },
                "replace": {
                    "Description": "Replace text with text.",
                    "Usage": "replace <text> | <text to find> | <text to replace with>"
                },
                "hash": {
                    "Description": "Convert text into a hash.",
                    "Usage": "hash <md5/sha1/sha256/sha512> <text>"
                },
                "tts": {
                    "Description": "Send a text to speech message.",
                    "Usage": "tts <text>"
                },
                "snipe": {
                    "Description": "Get the latest deleted message of a user.",
                    "Usage": "snipe [member]"
                },
                "encode": {
                    "Description": "Encode text.",
                    "Usage": "encode <text>"
                },
                "decode": {
                    "Description": "Decode encoded text.",
                    "Usage": "decode <text>"
                },
                "lyrics": {
                    "Description": "Get a song\'s lyrics.",
                    "Usage": "lyrics <title>"
                },
                "nyanlyrics": {
                    "Description": "Get a song\'s lyrics, except it\'s more adorable.",
                    "Usage": "nyanlyrics <title>"
                },
                "minecraft": {
                    "Description": "Get some simple information about a user.",
                    "Usage": "minecraft <username>",
                    "Aliases": ['mc']
                }
            }],
            "Invite Tracer": [{
                "invites": {
                    "Description": "Get the total invites of a user.",
                    "Usage": "invites [member]"
                },
                "giveinvites": {
                    "Description": "Give bonus invites to a user.",
                    "Usage": "giveinvites [member] [amount]",
                    "Aliases": ["+invites", "addinvites"]
                },
                "removeinvites": {
                    "Description": "Remove invites of a user (IRREVERSIBLE).",
                    "Usage": "removeinvites [member]",
                    "Aliases": ["reminvites", "-invites"]
                },
                "removeallinvites": {
                    "Description": "Remove all of this server\'s invites.",
                    "Usage": "removeallinvites",
                    "Aliases": ["remallinvites", "-allinvites"]
                },
                "restoreinvites": {
                    "Description": "Restore all removed invites of this server. This only applies to invites removed by removeallinvites (IRREVERSIBLE).",
                    "Usage": "restoreinvites",
                    "Aliases": ["recoverinvites"]
                },
                "nukeinvites": {
                    "Description": "Delete all active invite codes of this server.",
                    "Usage": "nukeinvites"
                },
                "clearinvites": {
                    "Description": "Clear a user\'s invites (IRREVERSIBLE).",
                    "Usage": "clearinvites [member]",
                    "Aliases": ["purgeinvites"]
                },
                "inviter": {
                    "Description": "Find out who invited a user to this server.",
                    "Usage": "inviter [member]"
                },
                "invitedlist": {
                    "Description": "Get a list of users that got invited by a user.",
                    "Usage": "invitedlist [member]"
                },
                "invitecodes": {
                    "Description": "Get a list of invites that are currently active by a user.",
                    "Usage": "invitecodes [member]"
                },
                "allinvitecodes": {
                    "Description": "Get a list of all invites that are currently active in this server.",
                    "Usage": "allinvitecodes"
                },
                "inviteblacklist": {
                    "Description": "Add a user to the invite blacklist. Blacklisted user\'s invites will always stay at 0.",
                    "Usage": "inviteblacklist"
                },
                "traceinvite": {
                    "Description": "Trace an invite to get advanced information about the invite used.",
                    "Usage": "traceinvite <invite ID>"
                }
            }],
            "Images": [{
                "yandere": {
                    "Description": "Search yande.re for images.",
                    "Usage": "yandere <tag>"
                },
                "awwnime": {
                    "Description": "Get cute anime images.",
                    "Usage": "awwnime"
                },
                "animegif": {
                    "Description": "Get some anime gifs.",
                    "Usage": "animegif"
                },
                "animewp": {
                    "Description": "Get some anime wallpapers.",
                    "Usage": "animewp"
                },
                "moe": {
                    "Description": "Get some moe images.",
                    "Usage": "moe"
                },
                "aww": {
                    "Description": "Get some cute images.",
                    "Usage": "aww"
                },
                "floof": {
                    "Description": "Floofers!",
                    "Usage": "floof"
                },
                "cat": {
                    "Description": "Generate a random cat image.",
                    "Usage": "cat"
                },
                "dog": {
                    "Description": "Generate a random dog image.",
                    "Usage": "dog"
                },
                "koala": {
                    "Description": "Generate a random koala image.",
                    "Usage": "koala"
                },
                "bird": {
                    "Description": "Generate a random birb image.",
                    "Usage": "bird",
                    "Aliases": ['birb']
                },
                "panda": {
                    "Description": "Generate a random panda image.",
                    "Usage": "panda"
                },
                "raccoon": {
                    "Description": "Generate a random raccoon image.",
                    "Usage": "raccoon"
                },
                "kangaroo": {
                    "Description": "Generate a random kangaroo image.",
                    "Usage": "kangaroo"
                },
                "redpanda": {
                    "Description": "Generate a random red panda image.",
                    "Usage": "redpanda"
                },
                "fox": {
                    "Description": "Generate a random fox image.",
                    "Usage": "fox"
                },
                "neko": {
                    "Description": "Generate a random neko image.",
                    "Usage": "neko"
                },
                "hneko": {
                    "Description": "Generate a random hentai neko image.",
                    "Usage": "hneko"
                },
                "hass": {
                    "Description": "Generate a random hentai ass.",
                    "Usage": "hass"
                },
                "hmidriff": {
                    "Description": "Generate a random hentai midriff image.",
                    "Usage": "hmidriff"
                },
                "pgif": {
                    "Description": "Generate a random NSFW gif.",
                    "Usage": "pgif"
                },
                "4k": {
                    "Description": "Generate a random NSFW 4k image.",
                    "Usage": "4k"
                },
                "hentai": {
                    "Description": "Generate a random hentai.",
                    "Usage": "hentai"
                },
                "holo": {
                    "Description": "Generate a random holo image.",
                    "Usage": "holo"
                },
                "hkitsune": {
                    "Description": "Generate a random hentai kitsune image.",
                    "Usage": "hkitsune"
                },
                "kemonomimi": {
                    "Description": "Generate a random komonomimi image.",
                    "Usage": "kemonomimi"
                },
                "anal": {
                    "Description": "Generate a random NSFW anal.",
                    "Usage": "anal"
                },
                "hanal": {
                    "Description": "Generate a random hentai anal.",
                    "Usage": "hanal"
                },
                "gonewild": {
                    "Description": "Generate a random NSFW image that has gone wild.",
                    "Usage": "gonewild"
                },
                "kanna": {
                    "Description": "Generate a random kanna.",
                    "Usage": "kanna"
                },
                "ass": {
                    "Description": "Generate a random NSFW ass.",
                    "Usage": "ass"
                },
                "pussy": {
                    "Description": "Generate a random NSFW pussy.",
                    "Usage": "pussy"
                },
                "thigh": {
                    "Description": "Generate random NSFW thighs.",
                    "Usage": "thigh"
                },
                "hthigh": {
                    "Description": "Generate random hentai thighs.",
                    "Usage": "hthigh"
                },
                "gah": {
                    "Description": "Oh my gah!",
                    "Usage": "gah"
                },
                "coffee": {
                    "Description": "Generate a random coffee image.",
                    "Usage": "coffee"
                },
                "food": {
                    "Description": "Generate a random food image.",
                    "Usage": "food"
                },
                "paizuri": {
                    "Description": "Generate a random hentai paizuri.",
                    "Usage": "paizuri"
                },
                "tentacle": {
                    "Description": "We all know what that does...",
                    "Usage": "tentacle"
                },
                "boobs": {
                    "Description": "BOOBAS",
                    "Usage": "boobs",
                    "Aliases": ['booba']
                },
                "hboobs": {
                    "Description": "BOOBAS",
                    "Usage": "hboobs",
                    "Aliases": ['hbooba']
                },
                "yaoi": {
                    "Description": "Generate a random NSFW yaoi.",
                    "Usage": "yaoi"
                }
            }],
            "Fun": [{
                "triggered": {
                    "Description": "Trigger someone\'s avatar.",
                    "Usage": "triggered [member]"
                },
                "roll": {
                    "Description": "Roll for points!",
                    "Usage": "roll [max points]"
                },
                "trash": {
                    "Description": "Trash a member\'s anime avatar.",
                    "Usage": "trash [member]"
                },
                "fact": {
                    "Description": "Spill facts in form of an anime girl holding a sign.",
                    "Usage": "fact <text>"
                },
                "magik": {
                    "Description": "Magikify someone\'s avatar.",
                    "Usage": "magik <intensity: 0-10> [member]",
                    "Aliases": ['magikify']
                },
                "phcomment": {
                    "Description": "Comment something on PornHub.",
                    "Usage": "phcomment <message>"
                },
                "token": {
                    "Description": "Generate a fake discord bot token.",
                    "Usage": "token"
                },
                "insult": {
                    "Description": "Get an insult.",
                    "Usage": "insult"
                },
                "dadjoke": {
                    "Description": "Get a dadjoke."
                },
                "simpforwho": {
                    "Description": "Find out who they\'re simping for.",
                    "Usage": "simpforwho [member]"
                },
                "howgay": {
                    "Description": "Find out how gay someone is.",
                    "Usage": "howgay [member]"
                },
                "simprate": {
                    "Description": "Find out how much of a simp someone is.",
                    "Usage": "simprate [member]",
                    "Aliases": ['simpr8']
                },
                "hug": {
                    "Description": "Give someone a hug!",
                    "Usage": "hug [member]"
                },
                "slap": {
                    "Description": "Give someone a slap!",
                    "Usage": "slap [member]"
                },
                "pat": {
                    "Description": "Give someone some pats!",
                    "Usage": "pat [member]"
                },
                "cuddle": {
                    "Description": "Cuddle with someone!",
                    "Usage": "cuddle [member]"
                },
                "gay": {
                    "Description": "Rainbow someone\'s avatar.",
                    "Usage": "gay [member]",
                    "Aliases": ['lgbtq', 'rainbow']
                },
                "glass": {
                    "Description": "Glass someone\'s avatar.",
                    "Usage": "glass [member]"
                },
                "wasted": {
                    "Description": "Wasted over someone\'s avatar.",
                    "Usage": "wasted [member]"
                },
                "missionpassed": {
                    "Description": "Misson Passed over someone\'s avatar.",
                    "Usage": "missionpassed [member]",
                    "Aliases": ['passed']
                },
                "jail": {
                    "Description": "Jail someone\'s avatar.",
                    "Usage": "jail [member]"
                },
                "comrade": {
                    "Description": "Welcome back, comrade!",
                    "Usage": "comrade [member]"
                },
                "pixelate": {
                    "Description": "Pixelate someone\'s avatar.",
                    "Usage": "pixelate [member]"
                },
                "simpcard": {
                    "Description": "Put someone\'s avatar over a simpcard.",
                    "Usage": "simpcard [member]"
                },
                "horny": {
                    "Description": "Put someone\'s avatar over a hornycard.",
                    "Usage": "horny [member]"
                },
                "lolice": {
                    "Description": "Loli police.",
                    "Usage": "lolice [member]"
                },
                "blur": {
                    "Description": "Blur someone\'s avatar.",
                    "Usage": "blur [member]"
                },
                "stupid": {
                    "Description": "Stoopid someone!",
                    "Usage": "stupid <member> <text>"
                },
                "tweet": {
                    "Description": "Post something on Twitter!",
                    "Usage": "tweet <message>",
                    "Aliases": ['twitter']
                },
                "youtubecomment": {
                    "Description": "Comment something on YouTube!",
                    "Usage": "youtubecomment <message>",
                    "Aliases": ['ytcomment']
                },
                "meme": {
                    "Description": "Generate a random reddit meme.",
                    "Usage": "meme",
                    "Aliases": ['memes', 'redditmeme']
                },
                "dankmeme": {
                    "Description": "Generate a random dankmeme.",
                    "Usage": "dankmeme"
                },
                "animeme": {
                    "Description": "Generate a random anime meme.",
                    "Usage": "animeme"
                },
                "8ball": {
                    "Description": "Get the answer to all of your questions.",
                    "Usage": "8ball"
                },
                "searchgif": {
                    "Description": "Search for gifs by name.",
                    "Usage": "searchgif <name>",
                    "Aliases": ['gifsearch']
                },
                "searchimage": {
                    "Description": "Search for images by name.",
                    "Usage": "searchimage <name>",
                    "Aliases": ['imagesearch']
                },
                "textflip": {
                    "Description": "Flip your text!",
                    "Usage": "textflip <text>",
                    "Aliases": "fliptext"
                },
                "spacetext": {
                    "Description": "Leave your text some space.",
                    "Usage": "spacetext <text>"
                },
                "bigtext": {
                    "Description": "Enlarge your text.",
                    "Usage": "bigtext <text>"
                },
                "iq": {
                    "Description": "Whose still doing IQ tests when you have Discord Bots?",
                    "Usage": "iq [member]"
                },
                "hack": {
                    "Description": "Hack someone!",
                    "Usage": "hack [member]",
                    "Cooldown": 32
                },
                "clap": {
                    "Description": "Clap your text.",
                    "Usage": "clap <text>"
                },
                "1337": {
                    "Description": "Transform your text into leetspeak.",
                    "Usage": "1337 <text>",
                    "Aliases": ['leetspeak', '1337speak']
                },
                "findip": {
                    "Description": "Get someone\'s IP.",
                    "Usage": "findip [member]",
                    "Aliases": ['getip']
                },
                "flip": {
                    "Description": "Flip a coin!",
                    "Usage": "flip",
                    "Aliases": ['flipcoin', 'coinflip']
                },
                "greyscale": {
                    "Description": "Grey out someone\'s avatar.",
                    "Usage": "greyscale [member]"
                },
                "invert": {
                    "Description": "Invert someone\'s avatar colors.",
                    "Usage": "invert [member]"
                },
                "invertgreyscale": {
                    "Description": "Invert + greyscale!",
                    "Usage": "invertgreyscale [member]"
                },
                "brightness": {
                    "Description": "Brighten someone\'s avatar.",
                    "Usage": "brightness <brightness: 0-100> [member]"
                },
                "blurpify": {
                    "Description": "Blurpify someone\'s avatar.",
                    "Usage": "blurpify [member]"
                },
                "deepfry": {
                    "Description": "Deepfry someone\'s avatar.",
                    "Usage": "deepfry [member]"
                },
                "trumptweet": {
                    "Description": "Tweet as ðŸŽº!",
                    "Usage": "trumptweet <text>",
                    "Aliases": ['trumptwitter']
                },
                "trap": {
                    "Description": "Trap someone!",
                    "Usage": "trap <member>"
                },
                "awooify": {
                    "Description": "Awooify someone\'s avatar.",
                    "Usage": "awooify [member]"
                },
                "iphonex": {
                    "Description": "iPhoneX someone.",
                    "Usage": "iphonex [member]"
                },
                "kannafy": {
                    "Description": "Kannafy text!",
                    "Usage": "kannafy <text>"
                },
                "android": {
                    "Description": 'Convert a member\'s avatar into "android" quality (no hate android users).',
                    "Usage": "android [member]",
                    "Aliases": "jpeg"
                },
                "threshold": {
                    "Description": "Threshold someone\'s avatar.",
                    "Usage": "threshold <threshold: 0-255> [member]"
                },
                "ddlc": {
                    "Description": "Doki doki!",
                    "Usage": 'ddlc <character> "<captioned text>" [background] [body] [face]',
                    "Aliases": "dokidoki"
                },
                "changemymind": {
                    "Description": "Change My Mind text.",
                    "Usage": "changemymind <text>"
                },
                "whowouldwin": {
                    "Description": "Who would win?",
                    "Usage": "whowouldwin <member1> <member2>"
                },
                "captcha": {
                    "Description": "Captchafy someone\'s avatar.",
                    "Usage": "captcha <member> <text>"
                },
                "ship": {
                    "Description": "Don\'t look at other women while u already have one!",
                    "Usage": "ship <member1> <member2>"
                },
                "clyde": {
                    "Description": "Send a message as clyde.",
                    "Usage": "clyde <text>"
                },
                "baguette": {
                    "Description": "Baguettify someone\'s avatar.",
                    "Usage": "baguette [member]"
                },
                "threats": {
                    "Description": "3 biggest threats on earth.",
                    "Usage": "threats [member]"
                },
                "sepia": {
                    "Description": "Put a sepia filter over someone\'s avatar.",
                    "Usage": "sepia [member]"
                },
                "red": {
                    "Description": "Put a red filter over someone\'s avatar.",
                    "Usage": "red [member]"
                },
                "green": {
                    "Description": "Put a green filter over someone\'s avatar.",
                    "Usage": "green [member]"
                },
                "blue": {
                    "Description": "Put a blue filter over someone\'s avatar.",
                    "Usage": "blue [member]"
                },
                "blurple": {
                    "Description": "Put a blurple filter over someone\'s avatar.",
                    "Usage": "blurple [member]"
                },
                "blurple2": {
                    "Description": "Put another blurple filter over someone\'s avatar.",
                    "Usage": "blurple2 [member]"
                },
                "color": {
                    "Description": "Put a custom color filter over someone\'s avatar.",
                    "Usage": "color <hex> [member]"
                }
            }],
            "Math": [{
                "randnum": {
                    "Description": "Get a random number between 2 numbers.",
                    "Usage": "randnum <number: min> <number: max>"
                },
                "multiply": {
                    "Description": "Multiply 2 numbers.",
                    "Usage": "multiply <number: a> <number: b>"
                },
                "divide": {
                    "Description": "Divide 2 numbers.",
                    "Usage": "divide <number: a> <number: b>"
                },
                "add": {
                    "Description": "Add 2 numbers.",
                    "Usage": "add <number: a> <number: b>"
                },
                "subtract": {
                    "Description": "Subtract 2 numbers.",
                    "Usage": "subtract <number: a> <number: b>"
                }
            }]
        }

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def help(self, ctx, cn=None):
        prefix = self.bot.config._get_prefix(self.bot, ctx)
        if not cn:
            embed = discord.Embed(title='Command Help', description=f"This is a list of commands you can use. Type `{prefix}help <command>` to get advanced help for a specific command.",
                                  color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR != None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random(
                                  ) if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None,
                                  timestamp=ctx.message.created_at)
            for command_cat in self.command_cats:
                for command_name in self.command_cats[command_cat]:
                    c_name = [f'`{c_name}`' for c_name in command_name]
                    embed.add_field(
                        name=command_cat, value=', '.join(c_name), inline=False)
            await ctx.send(embed=embed)
        elif cn:
            for command_cat in self.command_cats:
                for command_name in self.command_cats[command_cat]:
                    for c_name in command_name:
                        if str(cn) == str(c_name):
                            embed = discord.Embed(title=command_cat,
                                                  description=f"**<>** = required\n**[]** = optional",
                                                  color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR !=
                                                  None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random() if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None,
                                                  timestamp=ctx.message.created_at)
                            embed.add_field(
                                name='Command', value=f'`{c_name}`', inline=False)
                            for c_inclusive in self.command_cats[command_cat][0][c_name]:
                                if not 'list' in str(
                                        type(self.command_cats[command_cat][0][c_name][c_inclusive])):
                                    embed.add_field(name=c_inclusive,
                                                    value=f'`{self.command_cats[command_cat][0][c_name][c_inclusive]}`'.replace(
                                                        self.command_cats[command_cat][0][c_name][c_inclusive], prefix +
                                                        self.command_cats[command_cat][0][c_name][c_inclusive]
                                                        if self.command_cats[command_cat][0][c_name][c_inclusive][:1]
                                                        != self.command_cats[command_cat][0][c_name][c_inclusive][:1].upper()
                                                        # and c_inclusive != 'Aliases'
                                                        else self.command_cats[command_cat][0][c_name][c_inclusive]))
                                else:
                                    embed.add_field(name=c_inclusive, value=', '.join(
                                        '`' + x + '`' for x in self.command_cats[command_cat][0][c_name][c_inclusive]))

                            return await ctx.channel.send(embed=embed)
            await ctx.send(embed=embeds.Error._text_to_embed(self.bot, ctx, 'No help for the command **{}** found or it wasn\'t added yet. Perhaps you want to try **{}help** for a list of commands?'.format(cn, prefix)))
            embed = discord.Embed(title='Command Help', description=f"This is a list of commands you can use. Type `{prefix}help <command>` to get advanced help for a specific command.",
                                  color=self.bot.DEFAULT_COLOR if self.bot.DEFAULT_COLOR != None and self.bot.DEFAULT_COLOR != 'random' else discord.Color.random(
                                  ) if self.bot.DEFAULT_COLOR == 'random' else ctx.author.color if not self.bot.DEFAULT_COLOR else None,
                                  timestamp=ctx.message.created_at)
            for command_cat in self.command_cats:
                for command_name in self.command_cats[command_cat]:
                    c_name = [f'`{c_name}`' for c_name in command_name]
                    embed.add_field(
                        name=command_cat, value=', '.join(c_name), inline=False)
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
