import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import asyncio
from typing import Optional

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

# --- Slash Commands ---

# 1. SEND MESSAGE TO ALL MEMBERS VIA DM
@bot.tree.command(name="dm_all", description="Send a DM to all members in the server")
@app_commands.describe(
    message="The message to send (optional if you attach a file)",
    file="A .txt file containing the message to send"
)
@app_commands.default_permissions(administrator=True)
@app_commands.guild_only() # Only allow this command in a server
async def dm_all_slash(
    interaction: discord.Interaction,
    message: Optional[str] = None, # Use Optional[str] for better type hinting
    file: Optional[discord.Attachment] = None
):
    """DM all members in the server using slash command"""
    
    # Defer the response immediately to prevent timeout
    try:
        # Using ephemeral=True is standard for admin commands like this
        await interaction.response.defer(ephemeral=True, thinking=True) 
    except discord.InteractionResponded:
        # Handle case if already responded, though defer should be first
        pass
    except Exception as e:
        print(f"Error deferring response: {e}")
        return
    
    final_message = message
    
    # Process file attachment
    if file:
        file_content = await read_attachment_content(file)
        if file_content is None:
            await interaction.followup.send("❌ Please attach a valid `.txt` file!", ephemeral=True)
            return
        final_message = file_content
    
    # Final check for message content
    if not final_message or not final_message.strip():
        await interaction.followup.send("❌ Please provide a message or attach a non-empty `.txt` file!", ephemeral=True)
        return
    
    # Send confirmation before starting
    preview = final_message.strip()[:100] + ('...' if len(final_message.strip()) > 100 else '')
    await interaction.followup.send(
        f"📤 Starting to send DM to **{interaction.guild.member_count}** members...\n"
        f"**Preview:**\n```\n{preview}\n```",
        ephemeral=True
    )
    
    success_count = 0
    fail_count = 0
    
    # Get members, ensuring to use interaction.guild.members which is cached
    # If the list is large, consider fetching them: await interaction.guild.chunk()
    members_to_dm = [m for m in interaction.guild.members if not m.bot]
    
    for member in members_to_dm:
        try:
            # Create a DM channel explicitly if needed, though send() usually handles it
            await member.send(final_message)
            success_count += 1
        except discord.Forbidden:
            fail_count += 1
            # Rate limit the console output to prevent flooding
            if fail_count % 10 == 0:
                print(f"Failed to DM {member.id}: DMs disabled or bot is blocked (Count: {fail_count})")
        except Exception as e:
            fail_count += 1
            if fail_count % 10 == 0:
                print(f"Failed to DM {member.id}: {type(e).__name__} (Count: {fail_count})")

        # Crucial for avoiding rate limits, slightly increased sleep time for safety
        await asyncio.sleep(2) 

    
    # Final report
    await interaction.followup.send(
        f"✅ **DM Report:**\n"
        f"• Total members attempted (excluding bots): {len(members_to_dm)}\n"
        f"• Sent successfully: **{success_count}**\n"
        f"• Failed (DMs disabled/blocked/other): **{fail_count}**",
        ephemeral=True
    )


# 2. SEND DM TO SPECIFIC MEMBER
@bot.tree.command(name="dm_member", description="Send a DM from .txt file to a specific member")
@app_commands.describe(
    member="The member to send the message to",
    file="A .txt file containing the message to send"
)
@app_commands.default_permissions(administrator=True)
@app_commands.guild_only()
async def dm_member_slash(
    interaction: discord.Interaction,
    member: discord.Member,
    file: discord.Attachment
):
    """Send a DM to a specific member from a .txt file"""
    
    # Defer immediately to prevent timeout
    try:
        await interaction.response.defer(ephemeral=True, thinking=True)
    except Exception as e:
        print(f"Error deferring response: {e}")
        return
    
    # Use the utility function to read content
    final_message = await read_attachment_content(file)
    
    if final_message is None:
        # read_attachment_content returns None if file is not .txt or fails to read
        await interaction.followup.send("❌ Failed to read the attachment. Ensure it's a valid `.txt` file.", ephemeral=True)
        return
    
    if not final_message.strip():
        await interaction.followup.send("❌ The file is empty!", ephemeral=True)
        return
    
    try:
        await member.send(final_message)
        await interaction.followup.send(f"✅ Message sent successfully to **{member.display_name}**!", ephemeral=True)
    except discord.Forbidden:
        await interaction.followup.send(f"❌ Failed to DM **{member.display_name}**: DMs are disabled or bot is blocked.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Error sending DM: {e}", ephemeral=True)


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


# --- Bot Run ---
# Securely load the token here or use the hardcoded one from the original
# For a real application, load it from an environment variable:
# import os
# TOKEN = os.getenv("DISCORD_TOKEN")
# ... use your actual token here ...
TOKEN = "MTE4ODU2NDgzNzIxOTk1ODkzNA.G5KqCi.6BAjyvyKGNDGHC3VkM1PGZE1WWG5UZ64Ufmfxw"

if TOKEN == "YOUR_DISCORD_BOT_TOKEN_HERE":
    print("FATAL: Please replace 'YOUR_DISCORD_BOT_TOKEN_HERE' with your actual bot token.")
else:
    try:
        bot.run(TOKEN)
    except discord.HTTPException as e:
        print(f"An HTTPException occurred. Check your token and intents.\nDetails: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")