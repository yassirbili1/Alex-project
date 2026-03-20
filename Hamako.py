import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import asyncio
from typing import Optional
import logging
import sys

# --- Configuration ---
# BEST PRACTICE: Use a dedicated config system or environment variables for secrets.
# Hardcoding the token is a security risk. I'll keep the variable for structure,
# but note it should be loaded securely.
# TOKEN = "YOUR_DISCORD_BOT_TOKEN_HERE"  # Use env variable in real app!
# GUILD_ID = 1153139291921317948 

# BOT INSTANCE
# Use a cleaner way to specify intents
intents = discord.Intents.default()
intents.members = True # Required for fetching guild members
intents.message_content = False # Generally not needed for slash commands, better to keep off unless necessary

# Note: The 'moderation' intent does not exist. It's likely you meant to use the
# privileged `Intents.members` and `Intents.message_content` if needed.

# Use commands.Bot for prefix commands, or just discord.Client for only slash commands
# I'll keep commands.Bot as it was in the original code.
bot = commands.Bot(command_prefix="!", intents=intents)

# Global data stores (consider a database for persistence in a real app)
invite_cache = {}
guild_settings = {}
# Use a more appropriate timestamp variable
bot_start_time = datetime.utcnow()

# --- Bot Events ---

@bot.event
async def on_ready():
    """Event triggered when the bot is ready."""
    print(f'✅ Bot logged in as {bot.user} (ID: {bot.user.id})')

    # Set bot activity/status
    activity = discord.Streaming(
        name="by Hamako", 
        url="https://www.twitch.tv/hamako"
    )
    await bot.change_presence(status=discord.Status.online, activity=activity)

    # Cache invites for all guilds
    await cache_all_invites()
    
    # Sync slash commands
    try:
        # Use discord.Object(id=GUILD_ID) to sync to a specific guild for faster testing
        # For global sync: synced = await bot.tree.sync()
        synced = await bot.tree.sync() # Global sync (takes up to an hour)
        print(f"🔗 Synced {len(synced)} global commands.")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")

async def cache_all_invites():
    """Caches the current state of invites for all available guilds."""
    global invite_cache
    
    for guild in bot.guilds:
        # Only cache if the bot has the necessary permissions
        if guild.me.guild_permissions.manage_guild:
            try:
                invites = await guild.invites()
                # Store invite code and uses
                invite_cache[guild.id] = {invite.code: invite.uses for invite in invites}
            except discord.Forbidden:
                print(f"⚠️ No permission to view invites in {guild.name}")
            except Exception as e:
                print(f"❌ Error caching invites for {guild.name}: {e}")
        else:
            print(f"⚠️ Bot lacks 'Manage Server' permission in {guild.name}. Skipping invite cache.")
            
    print(f"✅ Cached invites for {len(invite_cache)} guilds with permission.")

# --- Utility Functions ---

async def read_attachment_content(file: discord.Attachment) -> Optional[str]:
    """Reads and decodes content from a discord.Attachment."""
    if not file.filename.endswith('.txt'):
        return None
    try:
        file_content = await file.read()
        return file_content.decode('utf-8')
    except Exception as e:
        print(f"Error reading attachment: {e}")
        return None
    
# --- ADD THIS PART ---
logging.basicConfig(
    level=logging.INFO,
    format='[\033[94m%(asctime)s\033[0m] [\033[92m%(levelname)s\033[0m] %(message)s',
    datefmt='%H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('discord_bot')
# ----------------------
    
@bot.tree.command(name="giveall", description="Give a role to every member with terminal logging")
@app_commands.describe(role="The role to assign")
@app_commands.checks.has_permissions(manage_roles=True)
async def giveall(interaction: discord.Interaction, role: discord.Role):
    await interaction.response.send_message(f"⏳ Process started for {role.name}. Check terminal for live logs.", ephemeral=True)
    
    members = interaction.guild.members
    total = len(members)
    added = 0
    errors = 0
    
    logger.info(f"--- Starting 'Give All' for role: {role.name} ({role.id}) ---")
    logger.info(f"Targeting {total} members in guild: {interaction.guild.name}")

    for index, member in enumerate(members, 1):
        if member.bot:
            continue
            
        if role in member.roles:
            # Optional: Log skips if you want high detail
            # logger.info(f"[{index}/{total}] Skipping {member.name} (Already has role)")
            continue

        try:
            await member.add_roles(role)
            added += 1
            logger.info(f"[{index}/{total}] Successfully added role to: {member.name}#{member.discriminator}")
            
            # Optimization: Rate limit buffer
            if added % 10 == 0:
                logger.info("Buffer: Sleeping for 1.5s to prevent Discord rate limits...")
                await asyncio.sleep(1.5)
                
        except discord.Forbidden:
            logger.error(f"[{index}/{total}] FAILED: No permission to edit {member.name}")
            errors += 1
        except Exception as e:
            logger.warning(f"[{index}/{total}] ERROR adding to {member.name}: {e}")
            errors += 1

    logger.info(f"--- Task Finished ---")
    logger.info(f"Total Added: {added} | Total Errors: {errors}")
    
    await interaction.followup.send(f"✅ Finished! Added to `{added}` members. Check terminal for details.")


# 3. PING COMMAND
@bot.tree.command(name="ping", description="Check the bot's Latency")
@app_commands.default_permissions(administrator=False)
async def ping_slash(interaction: discord.Interaction):
    """Check the bot's Latency"""
    # bot.latency is in seconds, * 1000 for milliseconds
    latency_ms = bot.latency * 1000 
    
    # Use the existing command to measure processing time for a more complete ping
    # The original implementation was trying to do this, but incorrectly.
    # The following is a common practice for a more detailed latency check:
    
    # Send an initial response/edit that will measure the websocket latency
    start_time = datetime.utcnow()
    await interaction.response.send_message('Pinging...', ephemeral=True)
    
    # Edit the message to show the rest of the latency measurements
    end_time = datetime.utcnow()
    
    # API Latency: Time taken to send and confirm the response message
    api_latency_ms = (end_time - start_time).total_seconds() * 1000
    
    await interaction.edit_original_response(
        content=f'🏓 **Pong!**\n'
                f'• **Websocket Latency:** `{latency_ms:.2f}ms` (Discord <-> Bot)\n'
                f'• **API Latency:** `{api_latency_ms:.2f}ms` (Bot -> Discord API -> Response)'
    )



TOKEN = "MTQ4MjI4NDQ2MjI2NzE3NTA4NA.GhvhlR.Dp1PwfV2IU1m7nBnIN30EarWym_1urdwwv1lr0"

if TOKEN == "YOUR_DISCORD_BOT_TOKEN_HERE":
    print("FATAL: Please replace 'YOUR_DISCORD_BOT_TOKEN_HERE' with your actual bot token.")
else:
    try:
        bot.run(TOKEN)
    except discord.HTTPException as e:
        print(f"An HTTPException occurred. Check your token and intents.\nDetails: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")