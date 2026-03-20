import discord
from discord import app_commands
from discord.ext import commands

# Replace 'YOUR_BOT_TOKEN' with your actual token
TOKEN = 'MTQ1NTk1NjA0OTIxODc2NDkwMQ.GgFWDS.kyZpuRkiSY0jU36xhGDRNX5SY8x_uSDCpAO8OY'

class MyBot(commands.Bot):
    def __init__(self):
        # We need default intents to interact with the server
        intents = discord.Intents.default()
        intents.guilds = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # This syncs the slash commands with Discord
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}")

bot = MyBot()

@bot.tree.command(name="nuke_channels", description="Deletes every channel in the server")
@app_commands.checks.has_permissions(administrator=True)
async def nuke_channels(interaction: discord.Interaction):
    """
    Deletes all channels in the guild where the command is executed.
    """
    # Acknowledge the command immediately to prevent timeout
    await interaction.response.send_message("Initiating server wipe... Please wait.", ephemeral=True)
    
    guild = interaction.guild
    
    # Loop through all channels (categories, text, and voice)
    for channel in guild.channels:
        try:
            await channel.delete()
            print(f"Deleted: {channel.name}")
        except discord.Forbidden:
            print(f"Permission denied for: {channel.name}")
        except discord.HTTPException as e:
            print(f"Failed to delete {channel.name}: {e}")

    # Note: After deleting all channels, the bot won't be able to send 
    # a follow-up message because there are no channels left!
    print("All possible channels have been deleted.")

# Error handling for permissions
@nuke_channels.error
async def nuke_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("You don't have permission to use this!", ephemeral=True)

bot.run(TOKEN)