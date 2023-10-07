import json
from discord.ext import commands
from discord import app_commands

class Settings(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Logged in as')
        print(self.client.user.name)
        print(self.client.user.id)
        print('------')
        
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        print(guild)
        with open('prefixes.json', 'r') as f:
          prefixes = json.load(f)
        prefixes[str(guild.id)] = '++'
        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)
        prefixes.pop(str(guild.id))
        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot==False and self.client.user.mentioned_in(message) and len(message.content)==len(self.client.user.mention):
            await message.channel.send(f'Hello, I am {self.client.user.mention}! My prefix is {self.client.command_prefix(None,message)}')
    
    @app_commands.command(description="Shows the latency of the bot.")
    async def ping(self, interaction):
        await interaction.response.send_message(f'*Pong!* Ping: **{round(self.client.latency*1000)}ms**')
  
    @commands.command(hidden=True)
    async def sync(self,ctx):
        if ctx.author.id == 591825462393569294:
        	fmt = await ctx.bot.tree.sync()
        	await ctx.send(f"Synced {len(fmt)} commands.")

    #@commands.command()
    async def say(self, ctx, *msg):
      a = ''
      for x in msg:        
       a += f' {x}'
      await ctx.send(a)     
      await ctx.message.delete(delay=5)
      
    @commands.command(description="Changes the prefix of your guild.", usage="<prefix>")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def prefix(self, ctx, prefix):
        with open('prefixes.json', 'r') as f:
          prefixes = json.load(f)
        prefixes[str(ctx.guild.id)] = prefix
        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)
        await ctx.channel.send(f'The prefix has changed to: {prefix}')
      
        
async def setup(client):
    await client.add_cog(Settings(client))