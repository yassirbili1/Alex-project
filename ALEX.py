import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from datetime import datetime

class TurboBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True 
        intents.guilds = True
        super().__init__(command_prefix="!", intents=intents)
    
    async def setup_hook(self):
        await self.tree.sync()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🤖 Bot Online: {self.user}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Slash commands synced.")

bot = TurboBot()

# Helper to log to terminal with timestamps
def log_action(action, user_name, status="Success"):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {action.upper():<7} | User: {user_name:<20} | Status: {status}")

# Statistics tracking
class UnbanStats:
    def __init__(self):
        self.total = 0
        self.unbanned = 0
        self.dm_sent = 0
        self.dm_failed = 0
        self.unban_failed = 0
    
    def summary(self):
        return (
            f"📊 **STATISTICS**\n"
            f"Total Users: {self.total}\n"
            f"✅ Unbanned: {self.unbanned}\n"
            f"📨 DMs Sent: {self.dm_sent}\n"
            f"❌ DMs Failed: {self.dm_failed}\n"
            f"⚠️ Unban Failed: {self.unban_failed}"
        )

async def process_unban(guild, user, message, invite, stats):
    # 1. Attempt DM
    dm_success = False
    try:
        await user.send(f"{message}\n\n{invite}")
        log_action("DM", user.name, "Sent")
        stats.dm_sent += 1
        dm_success = True
    except discord.Forbidden:
        log_action("DM", user.name, "Failed (DMs Closed)")
        stats.dm_failed += 1
    except Exception as e:
        log_action("DM", user.name, f"Error: {e}")
        stats.dm_failed += 1
    
    # 2. Attempt Unban
    try:
        await guild.unban(user)
        log_action("UNBAN", user.name, "LIFTED")
        stats.unbanned += 1
    except discord.NotFound:
        log_action("UNBAN", user.name, "Already Unbanned")
    except discord.Forbidden:
        log_action("UNBAN", user.name, "Missing Permissions")
        stats.unban_failed += 1
    except Exception as e:
        log_action("UNBAN", user.name, f"Failed: {e}")
        stats.unban_failed += 1

@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! `{latency}ms`", ephemeral=True)

@bot.tree.command(name="turbo_unban", description="High-speed mass unban with DM and logging")
@app_commands.describe(
    message="The message to send to unbanned users",
    invite="Your server invite link"
)
@app_commands.checks.has_permissions(administrator=True)
async def turbo_unban(interaction: discord.Interaction, message: str, invite: str):
    await interaction.response.defer(ephemeral=True)
    
    guild = interaction.guild
    
    # Fetch all banned users
    try:
        bans = [entry async for entry in guild.bans()]
    except discord.Forbidden:
        await interaction.followup.send("❌ I don't have permission to view bans!")
        return
    
    if not bans:
        await interaction.followup.send("✅ Ban list is empty. No users to unban.")
        return
    
    # Confirmation
    print(f"\n{'='*60}")
    print(f"🚀 STARTING MASS UNBAN: {len(bans)} USERS")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    stats = UnbanStats()
    stats.total = len(bans)
    
    # Process in batches
    batch_size = 10  # Process 10 users at a time
    total_batches = (len(bans) + batch_size - 1) // batch_size
    
    for batch_num, i in enumerate(range(0, len(bans), batch_size), 1):
        batch = bans[i:i + batch_size]
        
        print(f"--- Processing Batch {batch_num}/{total_batches} ({len(batch)} users) ---")
        
        tasks = [process_unban(guild, entry.user, message, invite, stats) for entry in batch]
        await asyncio.gather(*tasks)
        
        # Rate limit protection (adjust as needed)
        if batch_num < total_batches:
            await asyncio.sleep(0.3)
    
    # Final summary
    print(f"\n{'='*60}")
    print(f"✅ MASS UNBAN COMPLETE")
    print(f"⏰ Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Total: {stats.total} | Unbanned: {stats.unbanned} | DMs: {stats.dm_sent}/{stats.total}")
    print(f"{'='*60}\n")
    
    await interaction.followup.send(
        f"✅ **Mass Unban Complete!**\n\n{stats.summary()}",
        ephemeral=True
    )

@bot.tree.command(name="bans", description="View all currently banned users")
@app_commands.checks.has_permissions(administrator=True)
async def view_bans(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    
    try:
        bans = [entry async for entry in interaction.guild.bans()]
    except discord.Forbidden:
        await interaction.followup.send("❌ I don't have permission to view bans!")
        return
    
    if not bans:
        await interaction.followup.send("✅ No users are currently banned.", ephemeral=True)
        return
    
    # Create embed
    embed = discord.Embed(
        title=f"🔨 Banned Users ({len(bans)})",
        color=discord.Color.red(),
        timestamp=datetime.utcnow()
    )
    
    # Show first 25 (Discord embed limit)
    ban_list = []
    for ban_entry in bans[:25]:
        reason = ban_entry.reason or "No reason provided"
        ban_list.append(f"**{ban_entry.user.name}** (`{ban_entry.user.id}`)\n└ *{reason}*")
    
    embed.description = "\n\n".join(ban_list)
    
    if len(bans) > 25:
        embed.set_footer(text=f"Showing first 25 of {len(bans)} bans")
    
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="unban", description="Unban a specific user by ID")
@app_commands.describe(
    user_id="The ID of the user to unban",
    reason="Reason for unbanning"
)
@app_commands.checks.has_permissions(ban_members=True)
async def unban_single(interaction: discord.Interaction, user_id: str, reason: str = "No reason provided"):
    try:
        user_id_int = int(user_id)
        user = await bot.fetch_user(user_id_int)
        
        # Check if banned
        try:
            await interaction.guild.fetch_ban(user)
        except discord.NotFound:
            await interaction.response.send_message(f"❌ User **{user.name}** is not banned.", ephemeral=True)
            return
        
        # Unban
        await interaction.guild.unban(user, reason=reason)
        await interaction.response.send_message(
            f"✅ Unbanned **{user.name}** (`{user.id}`)\n**Reason:** {reason}",
            ephemeral=True
        )
        log_action("UNBAN", user.name, "Single Unban")
        
    except ValueError:
        await interaction.response.send_message("❌ Invalid user ID format.", ephemeral=True)
    except discord.NotFound:
        await interaction.response.send_message("❌ User not found.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to unban users.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

@bot.tree.command(name="ban", description="Ban a user from the server")
@app_commands.describe(
    user="The user to ban",
    reason="Reason for the ban",
    delete_days="Days of messages to delete (0-7)"
)
@app_commands.checks.has_permissions(ban_members=True)
async def ban_user(
    interaction: discord.Interaction,
    user: discord.Member,
    reason: str = "No reason provided",
    delete_days: int = 0
):
    if delete_days < 0 or delete_days > 7:
        await interaction.response.send_message("❌ delete_days must be between 0 and 7", ephemeral=True)
        return
    
    if user.id == interaction.user.id:
        await interaction.response.send_message("❌ You cannot ban yourself!", ephemeral=True)
        return
    
    if user.top_role >= interaction.user.top_role:
        await interaction.response.send_message("❌ You cannot ban someone with equal or higher role!", ephemeral=True)
        return
    
    try:
        await interaction.guild.ban(user, reason=reason, delete_message_days=delete_days)
        await interaction.response.send_message(
            f"✅ Banned **{user.name}** (`{user.id}`)\n**Reason:** {reason}",
            ephemeral=True
        )
        log_action("BAN", user.name, reason)
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to ban this user.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)


@bot.tree.command(name="alex")
@app_commands.describe(
    message="Your message",
    invite="Invite link", 
    channel="Channel for announcement"
)
@app_commands.checks.has_permissions(administrator=True)
async def unban_announce(
    interaction: discord.Interaction,
    message: str,
    invite: str,
    channel: discord.TextChannel
):
    await interaction.response.defer(ephemeral=True)
    
    bans = [entry async for entry in interaction.guild.bans()]
    
    if not bans:
        await interaction.followup.send("No bans found.")
        return
    
    # Create list of unbanned users
    user_list = "\n".join([f"• {entry.user.name}" for entry in bans[:50]])
    if len(bans) > 50:
        user_list += f"\n... and {len(bans) - 50} more"
    
    # Post announcement BEFORE unbanning
    embed = discord.Embed(
        title="🎉 Mass Unban Announcement",
        description=f"**{len(bans)} users have been unbanned!**\n\n{message}",
        color=discord.Color.green()
    )
    embed.add_field(name="Rejoin Server", value=f"[Click Here]({invite})", inline=False)
    embed.add_field(name="Unbanned Users", value=user_list, inline=False)
    
    await channel.send(embed=embed)
    
    # Now unban everyone
    stats = UnbanStats()
    stats.total = len(bans)
    
    for entry in bans:
        try:
            await interaction.guild.unban(entry.user)
            stats.unbanned += 1
            
            # Still try to DM, but don't expect success
            try:
                await entry.user.send(f"{message}\n\n{invite}")
                stats.dm_sent += 1
            except:
                stats.dm_failed += 1
                
        except:
            stats.unban_failed += 1
    
    await interaction.followup.send(f"✅ Done!\n{stats.summary()}")


# Error handlers
@turbo_unban.error
@view_bans.error
@unban_single.error
@ban_user.error
async def command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message(
            "❌ You don't have permission to use this command!",
            ephemeral=True
        )

bot.run('MTQ2Njc5MjQzMzQwNzc1NDQ5Nw.Gh2atP.-iXNHZ76ezs7Nys5TuJhFwcvyhdixKuvbOhSTs')