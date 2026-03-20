import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import asyncio

# Create bot with necessary intents
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{"="*50}')
    print(f'{bot.user} is now running!')
    print(f'Bot ID: {bot.user.id}')
    print(f'Connected at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'{"="*50}')
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

@bot.tree.command(name="unbanall", description="Unban ALL users from the server (UNLIMITED)")
@app_commands.checks.has_permissions(administrator=True)
async def unbanall(interaction: discord.Interaction):
    """Unban all banned users with NO LIMIT"""
    
    # Defer the response since this might take a while
    await interaction.response.defer()
    
    start_time = datetime.now()
    
    print(f'\n{"="*50}')
    print(f'UNBAN ALL COMMAND INITIATED - UNLIMITED MODE')
    print(f'Server: {interaction.guild.name} (ID: {interaction.guild.id})')
    print(f'Executed by: {interaction.user.name} (ID: {interaction.user.id})')
    print(f'Start Time: {start_time.strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'{"="*50}\n')
    
    try:
        # Get all banned users (NO LIMIT)
        print('🔍 Fetching ALL bans (this may take a while for large ban lists)...')
        banned_users = []
        
        # Fetch all bans without limit
        async for ban_entry in interaction.guild.bans(limit=None):
            banned_users.append(ban_entry)
        
        total_bans = len(banned_users)
        
        print(f'📊 Total banned users found: {total_bans}\n')
        
        if total_bans == 0:
            print('ℹ️  No banned users to unban.\n')
            await interaction.followup.send("ℹ️ There are no banned users in this server.")
            return
        
        # Unban all users concurrently for maximum speed
        unbanned_count = 0
        failed_count = 0
        
        print(f'🚀 Starting mass unban process for ALL {total_bans} users...\n')
        
        async def unban_user(ban_entry, index):
            """Unban a single user"""
            nonlocal unbanned_count, failed_count
            
            user = ban_entry.user
            reason = ban_entry.reason or "No reason provided"
            
            try:
                await interaction.guild.unban(user)
                unbanned_count += 1
                
                # Print every 10 unbans to reduce spam
                if index % 10 == 0 or index == total_bans - 1:
                    print(f'✅ [{index + 1}/{total_bans}] Progress: {unbanned_count} unbanned, {failed_count} failed')
                
                # Detailed log for first 50 and last 10
                if index < 50 or index >= total_bans - 10:
                    print(f'   └─ Unbanned: {user.name}#{user.discriminator} (ID: {user.id})')
                
                return True
                
            except discord.Forbidden:
                failed_count += 1
                print(f'❌ [{index + 1}/{total_bans}] Failed: {user.name}#{user.discriminator} - Missing permissions')
                return False
            except discord.HTTPException as e:
                failed_count += 1
                if "rate limit" in str(e).lower():
                    print(f'⚠️  Rate limit hit, waiting 5 seconds...')
                    await asyncio.sleep(5)
                print(f'❌ [{index + 1}/{total_bans}] Failed: {user.name}#{user.discriminator} - {str(e)}')
                return False
            except Exception as e:
                failed_count += 1
                print(f'❌ [{index + 1}/{total_bans}] Error: {user.name}#{user.discriminator} - {str(e)}')
                return False
        
        # Process all unbans concurrently in batches
        batch_size = 100  # Increased batch size for faster processing
        
        for i in range(0, total_bans, batch_size):
            batch = banned_users[i:i + batch_size]
            tasks = [unban_user(ban_entry, i + j) for j, ban_entry in enumerate(batch)]
            await asyncio.gather(*tasks, return_exceptions=True)
            
            if i + batch_size < total_bans:
                print(f'\n⏭️  Processed {min(i + batch_size, total_bans)}/{total_bans} - Moving to next batch...\n')
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Summary
        print(f'\n{"="*50}')
        print(f'UNBAN ALL COMPLETED')
        print(f'Total bans processed: {total_bans}')
        print(f'Successfully unbanned: {unbanned_count}')
        print(f'Failed: {failed_count}')
        print(f'Success rate: {(unbanned_count/total_bans)*100:.1f}%')
        print(f'Total duration: {duration:.2f} seconds')
        print(f'Average speed: {total_bans/duration:.2f} unbans/second')
        print(f'Completion time: {end_time.strftime("%Y-%m-%d %H:%M:%S")}')
        print(f'{"="*50}\n')
        
        # Send result to Discord
        embed = discord.Embed(
            title="🔓 Unban All Complete - UNLIMITED",
            description=f"Processed **{total_bans}** banned user(s) in {duration:.2f} seconds",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.add_field(name="✅ Successfully Unbanned", value=f"{unbanned_count:,}", inline=True)
        embed.add_field(name="❌ Failed", value=f"{failed_count:,}", inline=True)
        embed.add_field(name="📊 Success Rate", value=f"{(unbanned_count/total_bans)*100:.1f}%", inline=True)
        embed.add_field(name="⚡ Speed", value=f"{total_bans/duration:.2f} unbans/sec", inline=True)
        embed.add_field(name="⏱️ Duration", value=f"{duration:.2f}s", inline=True)
        embed.add_field(name="📈 Total Processed", value=f"{total_bans:,} users", inline=True)
        embed.set_footer(text=f"Executed by {interaction.user.name}")
        
        await interaction.followup.send(embed=embed)
        
    except discord.Forbidden:
        error_msg = "❌ I don't have permission to view bans or unban users."
        print(f'\n{error_msg}\n')
        await interaction.followup.send(error_msg)
    except Exception as e:
        error_msg = f"❌ An error occurred: {str(e)}"
        print(f'\n{error_msg}\n')
        await interaction.followup.send(error_msg)

@unbanall.error
async def unbanall_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ You need Administrator permission to use this command.", ephemeral=True)
        print(f'⚠️  Unauthorized unbanall attempt by {interaction.user.name} (ID: {interaction.user.id})')

# Run the bot
bot.run('MTQ2Njc5MjQzMzQwNzc1NDQ5Nw.Gh2atP.-iXNHZ76ezs7Nys5TuJhFwcvyhdixKuvbOhSTs')