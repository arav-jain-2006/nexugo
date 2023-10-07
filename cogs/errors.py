from discord.ext import commands


class ErrorHandler(commands.Cog):
    """A cog for global error handling."""

    def __init__(self, client):
        self.client = client
        self.hidden = True
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        """A global error handler cog."""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MemberNotFound):
            message = "User not found!"
        else:
            message = "Oh no! Something went wrong while running the command!"
            raise error
        
        await ctx.send(message, delete_after=5)
        await ctx.message.delete(delay=5)
    
async def setup(client):
    await client.add_cog(ErrorHandler(client))