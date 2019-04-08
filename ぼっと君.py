import discord
import asyncio
from discord.ext.commands import Bot
from discord.ext import commands
from datetime import datetime

bot_description = '''ぼっと君です。
コマンド一覧はヘルプを確認してください
©2017 Prrism
'''
bot_command_prefix = "!"

if not discord.opus.is_loaded():
        discord.opus.load_opus('opus')

#チャンネルID/ボットTOKEN　置き場--------------------------------------------#
onngaku_channel_id = ""
bot_token = ""
error_channel_id = ""
modrole = ['admin','mods']
#-------------------------------------------------------------------------#


#エラーをerror_channelに表示する場合はTrueに変更すること-----------------------#
logerror = True
#-------------------------------------------------------------------------#

bot = Bot(command_prefix=bot_command_prefix, description=bot_description)
bot.remove_command('help')

helpembed = discord.Embed(title="サーバーコマンド　ヘルプ", description="コマンド一覧：", color=0x00ff00)
helpembed.add_field(name="市民用コマンド", value="!help   - ヘルプ表示\n!play   - 音楽再生\n!pause   - 音楽一時停止\n!stop   - 音楽停止\n!playlist   - 音楽再生リスト", inline=False)
helpembed.add_field(name="コマンドヘルプ", value='コマンドごとのヘルプを表示するには  **!コマンド help**  と入力してください')
        
adminhelpembed = discord.Embed(title="サーバーコマンド　ヘルプ", description="コマンド一覧：", color=0x00ff00)
adminhelpembed.add_field(name="市民用コマンド", value="!help   - ヘルプ表示\n!play   - 音楽再生\n!pause   - 音楽一時停止\n!stop   - 音楽停止\n!playlist   - 音楽再生リスト", inline=False)
adminhelpembed.add_field(name="運営用コマンド", value="!mute   - ミュート\n!warn   - 注意\n!warnings   - 注意者リスト表示\n!ban   - バン", inline=False)
adminhelpembed.add_field(name="コマンドヘルプ", value='コマンドごとのヘルプを表示するには  **!コマンド help**  と入力してください')

async def logerror(exc, message, author):
    if logerror:
        error_embed = discord.Embed()
        error_embed.add_field(name=datetime.now().strftime('%Y/%m/%d - %H:%M:%S'), value="コマンド： "+str(message)+"\n"+"ユーザー： "+str(author)+"\n\n"+"{}".format(exc))
        await bot.send_message(bot.get_channel(error_channel_id), embed=error_embed)

class VoiceEntry:
    def __init__(self, message, player):
        self.requester = message.author
        self.channel = message.channel
        self.player = player

    def __str__(self):
        fmt = '*{0.title}* -　リクエスト者： {1.display_name}'
        duration = self.player.duration
        if duration:
            fmt = fmt + ' [曲の長さ: {0[0]}分 {0[1]}秒]'.format(divmod(duration, 60))
        return fmt.format(self.player, self.requester)

class VoiceState:
    def __init__(self, bot):
        self.current = None
        self.voice = None
        self.bot = bot
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False

        player = self.current.player
        return not player.is_done()

    @property
    def player(self):
        return self.current.player

    def skip(self):
        if self.is_playing():
            self.player.stop()

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            await self.bot.send_message(self.current.channel, '再生中： ' + str(self.current))
            self.current.player.start()
            await self.play_next_song.wait()

class Music:
    """Voice related commands.

    Works in multiple servers at once.
    """
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[server.id] = state

        return state

    async def create_voice_client(self, channel):
        voice = await self.bot.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice

    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except:
                pass

#    @commands.command(pass_context=True, no_pm=True)
#    async def join(self, ctx, *, channel : discord.Channel):
#        """Joins a voice channel."""
#        try:
#            await self.create_voice_client(channel)
#        except discord.ClientException:
#            await self.bot.say('Already in a voice channel...')
#        except discord.InvalidArgument:
#            await self.bot.say('This is not a voice channel...')
#        else:
#            await self.bot.say('Ready to play audio in ' + channel.name)

    @commands.command(pass_context=True, no_pm=True)
    async def summon(self, ctx):
        """Summons the bot to join your voice channel."""
        summoned_channel = ctx.message.author.voice_channel
        if summoned_channel is None:
            await self.bot.say('ボイスチャンネルに接続してください')
            return False

        state = self.get_voice_state(ctx.message.server)
        if state.voice is None:
            state.voice = await self.bot.join_voice_channel(summoned_channel)
        else:
            await state.voice.move_to(summoned_channel)

        return True

    @commands.command(pass_context=True, no_pm=True)
    async def play(self, ctx, *, song : str):
        """Plays a song.

        If there is a song currently in the queue, then it is
        queued until the next song is done playing.

        This command automatically searches as well from YouTube.
        The list of supported sites can be found here:
        https://rg3.github.io/youtube-dl/supportedsites.html
        """
        if state.is_playing():
            player = state.player
            player.resume()
            return
        
        if song == "":
                await self.bot.say("曲を指定してください")
        else:                
                state = self.get_voice_state(ctx.message.server)
                opts = {
                    'default_search': 'auto',
                    'quiet': True,
                }

                if state.voice is None:
                    await bot.join_voice_channel(bot.get_channel(onngaku_channel_id))

                try:
                    player = await state.voice.create_ytdl_player(song, ytdl_options=opts, after=state.toggle_next)
                except Exception as exc:
                    await logerror(exc, ctx.message.content, ctx.message.author)            
                else:
                    player.volume = 0.6
                    entry = VoiceEntry(ctx.message, player)
                    await state.songs.put(entry)
                    await self.bot.say(str(entry)+'を再生リストに追加しました ')

    @commands.command(pass_context=True, no_pm=True)
    async def test(self, ctx):
        await self.bot.say(self.get_voice_state(ctx.message.server).songs)

    @commands.command(pass_context=True, no_pm=True)
    async def volume(self, ctx, value : int):
        """Sets the volume of the currently playing song."""

        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.volume = value / 100
            await self.bot.say('ボリュームを {:.0%}にセットしました'.format(player.volume))

    @commands.command(pass_context=True, no_pm=True)
    async def pause(self, ctx):
        """Pauses the currently played song."""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.pause()

    @commands.command(pass_context=True, no_pm=True)
    async def resume(self, ctx):
        """Resumes the currently played song."""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.resume()

    @commands.command(pass_context=True, no_pm=True)
    async def stop(self, ctx):
        """Stops playing audio and leaves the voice channel.

        This also clears the queue.
        """
        server = ctx.message.server
        state = self.get_voice_state(server)

        if state.is_playing():
            player = state.player
            player.stop()

        #try:
        #    state.audio_player.cancel()
        #    del self.voice_states[server.id]
        #    await state.voice.disconnect()
        #except:
        #    pass

    @commands.command(pass_context=True, no_pm=True)
    async def skip(self, ctx):
        """Vote to skip a song. The song requester can automatically skip.

        3 skip votes are needed for the song to be skipped.
        """

        state = self.get_voice_state(ctx.message.server)
        if not state.is_playing():
            await self.bot.say('曲を再生していません')
            return

        await self.bot.say('曲をスキップします…')
        state.skip()

    @commands.command(pass_context=True, no_pm=True)
    async def playing(self, ctx):
        """Shows info about the currently played song."""

        state = self.get_voice_state(ctx.message.server)
        if state.current is None:
            await self.bot.say('何も再生していません')
        else:
            skip_count = len(state.skip_votes)
            await self.bot.say('再生中： {}'.format(state.current))


@bot.event
async def on_ready():
	print('ログイン名: '+bot.user.name+'(ID:'+bot.user.id+') | サーバー数: '+str(len(bot.servers))+' | ユーザー数: '+str(len(set(bot.get_all_members()))))
	print('--------------------------------------------------------------------------------')
	print('                     しとお都市Discordリンク: discord.gg/AD8DrrD')
	print('--------------------------------------------------------------------------------')
	print('                                Prrism氏制作')
	print('--------------------------------------------------------------------------------')

@bot.event
async def on_message(message):
        if (message.content.startswith('こんにちは') or message.content.startswith('こんにちわ')) and message.author != bot.user:
                await bot.send_message(message.channel, 'こんにちは！ ' + str(message.author.mention) + 'さん')
        elif (message.content.startswith('こんばんは') or message.content.startswith('こんばんわ')) and message.author != bot.user:
                await bot.send_message(message.channel, 'こんばんは！ ' + str(message.author.mention) + 'さん')
        await bot.process_commands(message)

@bot.command(pass_context = True)
async def help(ctx):
    if ctx.message.content == "!help":
            author_role = str(ctx.message.author.top_role).lower()
            if author_role in modrole:
                await bot.say(embed=adminhelpembed)
            else:
                await bot.say(embed=helpembed)



bot.add_cog(Music(bot))

bot.run(bot_token)
