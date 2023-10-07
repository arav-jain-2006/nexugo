import discord, json, os, asyncio
from discord.ext import commands

discord.utils.setup_logging()

def get_prefix(client, message):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
    if isinstance(message.channel, discord.channel.DMChannel):
        return ''
    try:
        if prefixes[str(message.guild.id)]:
            return prefixes[str(message.guild.id)]
    except KeyError:
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)
        prefixes[str(message.guild.id)] = '++'
        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)
        return '++'


class CustomHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):

        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)
        try:
            if prefixes[str(self.get_destination().guild.id)]:
                prefix = prefixes[str(self.get_destination().guild.id)]
        except:
            prefix = ''

        em = discord.Embed(color=0x3C86E4)
        em.set_author(name="Help Command", icon_url=client.user.avatar)
        em.set_footer(
            text=f"Use {prefix}help <cmd> for more details on a command.")
        srtedmp = sorted(filter((None), list(mapping.keys())),key=lambda x: x.qualified_name)
        for cog in srtedmp:
            if mapping[cog]:
                mapping[cog] = await self.filter_commands(mapping[cog])
                if mapping[cog] and cog:
                    em.add_field(
                        name=f"{cog.qualified_name}",
                        value=f" ‎ ‎ ‎`{','.join(map(str, mapping[cog]))}`",
                        inline=False)

        await self.get_destination().send(embed=em)

    async def send_command_help(self, command):
        em = discord.Embed(color=0x3C86E4)
        if command.description:
            em.add_field(name=self.get_command_signature(command),
                         value=command.description,
                         inline=False)
        else:
            em.set_author(name=self.get_command_signature(command))
        await self.get_destination().send(embed=em)


intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix=get_prefix,
                      intents=intents,
                      help_command=CustomHelpCommand())
#client = commands.Bot(command_prefix=get_prefix)
async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await client.load_extension(f'cogs.{filename[:-3]}')


            
@client.command(name="reload",hidden=True)
async def reload(ctx,file):
    try:
    	if ctx.author.id == 591825462393569294:
        	await client.reload_extension('cogs.'+file)
        	await ctx.send('Cog reloaded.')
    except Exception as e:
        await ctx.send(e)
            
async def main():
    async with client:
        await load_extensions()
        await client.start(os.environ['TOKEN'])
        
asyncio.run(main())
