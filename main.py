import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
from datetime import datetime, timedelta
import asyncio
import os
from flask import after_this_request
import yt_dlp
import aiohttp
from pystyle import Colors, Colorate
import random
import shutil
import subprocess
from datetime import datetime
from typing import Optional

timestamp = datetime.utcnow()


# ========================================
# BOT INSTANCE
# ========================================
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.messages = True
intents.message_content = True
intents.voice_states = True
intents.invites = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree  # Slash command handler
intents.moderation = True  # Required for audit logs
intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.members = True



#store invite data
invite_cache = {}


TOKEN = "MTM2MDU4NDU5OTM2NDcwMjM5OQ.Gfz2Vx.mVBthgZc6xhZRoOsTHMVI1Yzj-TcaV7yBfthkc"  # Replace with your bot token



WELCOME_CHANNEL_ID = 1357335173389353086
LEAVE_CHANNEL_ID = 1357335175025004544
LOG_CHANNEL_ID = 1357335200723501086 # Replace with your log channel ID

# Intents are required for accessing certain information
intents = discord.Intents.default()
intents.message_content = True  # Enable if you need to read message content


# Store voice clients and queues
voice_clients = {}
music_queues = {}
current_playing = {}

TRANSCRIPT_PATH = r"C:\Users\alex\Desktop\project alex\alex project"

if not os.path.exists(TRANSCRIPT_PATH):
    os.makedirs(TRANSCRIPT_PATH)



# Configuration (adjust these)
SUPPORT_TICKET_CATEGORY_ID = 1428391800590307461  # Replace with your category ID
BUG_TICKET_CATEGORY_ID = 1428463578012455103  # Replace with your category ID
PURCHASE_TICKET_CATEGORY_ID = 1428395363076804762  # Replace with your category ID
STAFF_ROLE_ID = 1357337569955938406  # Your staff role ID or None
TICKET_LOG_CHANNEL_ID = 1428398041186172988  # Replace with your log channel ID or None
TICKET_COUNTER = 0
APPLICATION_CHANNEL_ID = 1431660029781479516
ACCEPTED_ROLE_ID = 1357420438082293912


# ✅ Add this line
guild_settings = {}


# YouTube DLP options
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)  # type: ignore[arg-type]

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.duration = data.get('duration')
        self.thumbnail = data.get('thumbnail')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        
        if 'entries' in data:
            data = data['entries'][0]
        
        # Ensure we have a valid source string for FFmpegPCMAudio
        if stream:
            filename = data.get('url')
            if not filename:
                raise ValueError("Could not retrieve stream URL from ytdl data")
        else:
            filename = ytdl.prepare_filename(data)
            if not filename:
                raise ValueError("Could not prepare filename from ytdl data")
        
        return cls(discord.FFmpegPCMAudio(source=str(filename), **ffmpeg_options), data=data)



@bot.event
async def on_ready():
    """Cache all invites when bot starts up and set activity"""
    print(f'{bot.user} has logged in!')
    
    # Set bot activity/status
    activity = discord.Streaming(
        name="! 𝐀 𝐋 𝐄 𝐗 🔱",  # What the bot appears to be streaming
        url="https://www.twitch.tv/alxafricahub"  # Replace with actual Twitch URL
    )
    await bot.change_presence(status=discord.Status.online, activity=activity)
    
    # Cache invites for all guilds
    for guild in bot.guilds:
        try:
            invites = await guild.invites()
            invite_cache[guild.id] = {invite.code: invite.uses for invite in invites}
        except discord.Forbidden:
            print(f"No permission to view invites in {guild.name}")
        except Exception as e:
            print(f"Error caching invites for {guild.name}: {e}")
    
    print(f"Bot is ready and streaming! Cached invites for {len(bot.guilds)} guilds.")
    try:
            synced = await bot.tree.sync()
            print(f"Synced {len(synced)} commands.")
    except Exception as e:
            print(f"Error syncing commands: {e}")



####################################
# FUNCTION AUDIT LOG
####################################
def get_log_channel(guild):
    """Get the log channel for a guild."""
    return guild.get_channel(LOG_CHANNEL_ID)

def create_log_embed(title,description,color,guild,timestamp=None):
    """create a standardized log embed"""
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=timestamp or datetime.utcnow()
    )
    embed.set_footer(text=guild.name, icon_url=guild.icon.url if guild.icon else None)
    return embed

async def get_audit_log_entry(guild, action, target=None, limit=5):
    """get audit log entry for an action"""
    try:
        async for entry in guild.audit_logs(limit=limit, action=action):
            if target is None or entry.target.id == target.id:
                return entry
    except:
        pass
    return None

###################################
# MEMBER JOIN/LEAVE GUILD
###################################

@bot.event
async def on_member_join(member: discord.Member):

    print(f"✅ MEMBER JOINED: {member.name} ({member.id}) dkhoul l-server {member.guild.name}. Daba kayn {member.guild.member_count} members.")

    # 1. T-jib l-Channel object
    channel = member.guild.get_channel(WELCOME_CHANNEL_ID)

    # 2. T-checkki wach l-channel kayn
    if channel is not None:
        
        # 3. T-Saayeb l-Embed
        welcome_embed = discord.Embed(
            title=f"🎉 Mar7ba bik, Fl {member.guild.name}!",
            description=f"Hello {member.mention} We're thrilled to have you join our community!😊",
            color=discord.Color.green()
        )

        welcome_embed.set_thumbnail(url=member.avatar.url)
        welcome_embed.set_footer(text=f"Server: {member.guild.name}")

        # 4. T-Siffeṭ l-Embed
        try:
            await channel.send(embed=welcome_embed)
        except discord.Forbidden:
            print(f"❌ ERR: L-Bot ma 9adarch y-sifeṭ message f-channel {channel.name} 3la 9bel {member.name}")



@bot.event
async def on_member_remove(member: discord.Member):
    
    # 1. 🔍 T-jib l-Channel w-T-checkki l-woujoud dyalou
    channel = member.guild.get_channel(LEAVE_CHANNEL_ID)
    if channel is not None:
        
        # 2. 📝 T-Saayeb l-Embed (Message d'adieu)
        leave_embed = discord.Embed(
            # T-Title dial l-Embed
            title="👋 Thala w Dir L'mdala",
            
            # T-Description: T-sta3mel f-string ssa7i7a w-member.mention
            description=f"Sir lah isahal 3lik f-dik triq li ghadi fiha a **{member.mention}**.",
            
            # L-Loun: T-sta3mel C Capital (Color)
            color=discord.Color.red()
        )

        # T-zid l-Avatar dial l-Member
        leave_embed.set_thumbnail(url=member.avatar.url)
        
        # T-zid smit l-Server, w-kay7att l-3adad l-jdide dial l-members
        leave_embed.set_footer(
            text=f"Server: {member.guild.name} | L-3adad l-Jdide: {member.guild.member_count}"
        )

        # 3. 📨 T-Siffeṭ l-Message w-T-7ami mn l-Forbidden Errors
        try:
            await channel.send(embed=leave_embed)
            
            # 4. 💻 T-Logging f-L-Terminal        
        except discord.Forbidden:
            # Ila kan l-Bot ma 3andoux l-permissions
            print(f"❌ ERR: L-Bot ma 9adarch y-sifeṭ message f-channel {channel.name} 3la 9bel {member.name}. Forbidden.")
            
        except Exception as e:
            # Ayyi erreur akhora ma t-w9e3atch
             print(f"❌ ERR: Failed to send leave message for {member.name}: {e}")


             
####################################
# MEMBER ACTION LOGS
####################################

@bot.event
async def on_member_update(before, after):
    """Log member updates (roles, nickname,)"""
    log_channel = get_log_channel(after.guild)
    if not log_channel:
        return
    
    # Role changes
    if before.roles != after.roles:
        added_roles = set(after.roles) - set(before.roles)
        removed_roles = set(before.roles) - set(after.roles)

        if added_roles:
            roles = ', '.join([role.mention for role in added_roles])
            
            # Try to get user who added the role from audit logs
            added_by = "Unknown"
            try:
                entry = await get_audit_log_entry(after.guild, discord.AuditLogAction.member_role_update, after)
                if entry and entry.user:
                    added_by = entry.user.mention
                    # Check if it was the member themselves (via role reaction, etc.)
                    if entry.user.id == after.id:
                        added_by = f"{entry.user.mention} (self-assigned)"
            except Exception as e:
                print(f"Error getting audit log for role add: {e}")
            
            embed = create_log_embed(
                title="➕ Role Added",
                description=f"**Member:** {after.mention} ({after})\n"
                            f"**Roles Added:** {roles}\n"
                            f"**Added By:** {added_by}\n"
                            f"**Member ID:** {after.id}",
                color=discord.Color.green(),
                guild=after.guild
            )
            await log_channel.send(embed=embed)

        if removed_roles:
            roles = ', '.join([role.mention for role in removed_roles])
            
            # Try to get user who removed the role from audit logs
            removed_by = "Unknown"
            try:
                entry = await get_audit_log_entry(after.guild, discord.AuditLogAction.member_role_update, after)
                if entry and entry.user:
                    removed_by = entry.user.mention
                    # Check if it was the member themselves
                    if entry.user.id == after.id:
                        removed_by = f"{entry.user.mention} (self-removed)"
                    # Check for common bot actions
                    elif entry.user.bot:
                        removed_by = f"{entry.user.mention} (Bot)"
            except Exception as e:
                print(f"Error getting audit log for role remove: {e}")
            
            embed = create_log_embed(
                title="➖ Role Removed",
                description=f"**Member:** {after.mention} ({after})\n"
                            f"**Roles Removed:** {roles}\n"
                            f"**Removed By:** {removed_by}\n"
                            f"**Member ID:** {after.id}",
                color=discord.Color.orange(),
                guild=after.guild
            )
            await log_channel.send(embed=embed)

    # Nickname changes
    if before.display_name != after.display_name:
        # Try to get who changed the nickname
        changed_by = "Unknown"
        try:
            entry = await get_audit_log_entry(after.guild, discord.AuditLogAction.member_update, after)
            if entry and entry.user:
                changed_by = entry.user.mention
                if entry.user.id == after.id:
                    changed_by = f"{entry.user.mention} (self-changed)"
        except Exception as e:
            print(f"Error getting audit log for nickname change: {e}")
        
        embed = create_log_embed(
            title="✏️ Nickname Changed",
            description=f"**Member:** {after.mention} ({after})\n"
                        f"**Before:** {before.display_name}\n"
                        f"**After:** {after.display_name}\n"
                        f"**Changed By:** {changed_by}\n"
                        f"**Member ID:** {after.id}",
            color=discord.Color.blue(),
            guild=after.guild
        )
        await log_channel.send(embed=embed)

################################
# ban/unban logs
################################# 
@bot.event
async def on_member_ban(guild, user):
    """Log when a member is banned"""
    log_channel = get_log_channel(guild)
    if not log_channel:
        return
    
    # Get ban info from audit logs
    entry = await get_audit_log_entry(guild, discord.AuditLogAction.ban, user)
    ban_reason = entry.reason if entry and entry.reason else "No reason provided"
    banned_by = entry.user.mention if entry and entry.user else "Unknown"  # Fixed typo here
    
    embed = create_log_embed(
        title="🔨 Member Banned",
        description=(
            f"**Member:** {user} ({user.id})\n"
            f"**Banned by:** {banned_by}\n"
            f"**Reason:** {ban_reason}\n"
            f"**Timestamp:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        ),
        color=discord.Color.red(),
        guild=guild
    )
    if user.avatar:
        embed.set_thumbnail(url=user.avatar.url)
    else:
        embed.set_thumbnail(url=user.default_avatar.url)

    await log_channel.send(embed=embed)

@bot.event
async def on_member_unban(guild, user):
    """Log when a member is unbanned"""
    log_channel = get_log_channel(guild)
    if not log_channel:
        return
    
    # Get unban info from audit logs
    entry = await get_audit_log_entry(guild, discord.AuditLogAction.unban, user)
    unbanned_by = entry.user.mention if entry and entry.user else "Unknown"
    unban_reason = entry.reason if entry and entry.reason else "No reason provided"
    
    embed = create_log_embed(
        title="🔓 Member Unbanned",
        description=(
            f"**Member:** {user} ({user.id})\n"
            f"**Unbanned by:** {unbanned_by}\n"
            f"**Reason:** {unban_reason}\n"
            f"**Timestamp:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        ),
        color=discord.Color.green(),
        guild=guild
    )
    if user.avatar:
        embed.set_thumbnail(url=user.avatar.url)
    else:
        embed.set_thumbnail(url=user.default_avatar.url)

    await log_channel.send(embed=embed)


################################
# kick/unkick logs
#################################

@bot.event
async def on_member_remove(member):
    """Log when a member leaves or is kicked"""
    log_channel = get_log_channel(member.guild)
    if not log_channel:
        return
    
    # Wait a bit for audit logs to populate
    await asyncio.sleep(1)
    
    # Check if it was a kick
    kick_entry = await get_audit_log_entry(member.guild, discord.AuditLogAction.kick, member)
    
    if kick_entry:
        # Member was kicked
        kick_reason = kick_entry.reason if kick_entry.reason else "No reason provided"
        kicked_by = kick_entry.user.mention if kick_entry.user else "Unknown"
        
        embed = create_log_embed(
            title="👢 Member Kicked",
            description=(
                f"**Member:** {member.mention} ({member})\n"
                f"**Kicked by:** {kicked_by}\n"
                f"**Reason:** {kick_reason}\n"
                f"**Member ID:** {member.id}\n"
                f"**Account Created:** {member.created_at.strftime('%Y-%m-%d %H:%M:%S')} UTC"
            ),
            color=discord.Color.orange(),
            guild=member.guild
        )
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        else:
            embed.set_thumbnail(url=member.default_avatar.url)
            
        await log_channel.send(embed=embed)


###############################
# message delete/edit logs
###############################

@bot.event
async def on_message_delete(message):
    """Log when a message is deleted"""
    if message.author.bot:
        return  # Ignore bot messages
    
    log_channel = get_log_channel(message.guild)
    if not log_channel:
        return
    
    embed = create_log_embed(
        title="🗑️ Message Deleted",
        description=(
            f"**Author:** {message.author.mention} ({message.author})\n"
            f"**Channel:** {message.channel.mention}\n"
            f"**Message ID:** {message.id}\n"
            f"**Content:** {message.content if message.content else 'No text content'}\n"
            f"**Timestamp:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        ),
        color=discord.Color.dark_grey(),
        guild=message.guild
    )
    if message.attachments:
        embed.add_field(name="Attachments", value='\n'.join([att.url for att in message.attachments]), inline=False)
    
    await log_channel.send(embed=embed)


@bot.event
async def on_message_edit(before, after):
    """Log when a message is edited"""
    if before.author.bot:
        return  # Ignore bot messages
    
    log_channel = get_log_channel(before.guild)
    if not log_channel:
        return
    
    if before.content == after.content:
        return  # Ignore embed or attachment-only edits
    
    embed = create_log_embed(
        title="✏️ Message Edited",
        description=(
            f"**Author:** {before.author.mention} ({before.author})\n"
            f"**Channel:** {before.channel.mention}\n"
            f"**Message ID:** {before.id}\n"
            f"**Before:** {before.content if before.content else 'No text content'}\n"
            f"**After:** {after.content if after.content else 'No text content'}\n"
            f"**Timestamp:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        ),
        color=discord.Color.blue(),
        guild=before.guild
    )
    await log_channel.send(embed=embed)

###############################
# voice join/leave/move logs
###############################

@bot.event
async def on_voice_state_update(member, before, after):
    """Log when a member joins, leaves, or moves voice channels"""
    log_channel = get_log_channel(member.guild)
    if not log_channel:
        return

    action = None
    if before.channel is None and after.channel is not None:
        action = "🔊 Joined Voice Channel"
        description = (
            f"**Member:** {member.mention} ({member})\n"
            f"**Channel:** {after.channel.mention}\n"
            f"**Member ID:** {member.id}\n"
            f"**Timestamp:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        )
        color = discord.Color.green()
    elif before.channel is not None and after.channel is None:
        action = "🔇 Left Voice Channel"
        description = (
            f"**Member:** {member.mention} ({member})\n"
            f"**Channel:** {before.channel.mention}\n"
            f"**Member ID:** {member.id}\n"
            f"**Timestamp:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        )
        color = discord.Color.red()
    elif before.channel is not None and after.channel is not None and before.channel != after.channel:
        action = "🔀 Moved Voice Channel"
        description = (
            f"**Member:** {member.mention} ({member})\n"
            f"**From:** {before.channel.mention}\n"
            f"**To:** {after.channel.mention}\n"
            f"**Member ID:** {member.id}\n"
            f"**Timestamp:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        )
        color = discord.Color.orange()

    if action:
        embed = create_log_embed(
            title=action,
            description=description,
            color=color,
            guild=member.guild
        )
        await log_channel.send(embed=embed)

###############################
# server role/channel/invite updates
###############################

@bot.event
async def on_guild_role_create(role):
    """Log when a role is created"""
    log_channel = get_log_channel(role.guild)
    if not log_channel:
        return
    
    # Get who created the role from audit logs
    entry = await get_audit_log_entry(role.guild, discord.AuditLogAction.role_create, role)
    created_by = entry.user.mention if entry and entry.user else "Unknown"
    
    embed = create_log_embed(
        title="🆕 Role Created",
        description=(
            f"**Role:** {role.name} ({role.id})\n"
            f"**Created by:** {created_by}\n"
            f"**Color:** {role.color}\n"
            f"**Hoisted:** {role.hoist}\n"
            f"**Mentionable:** {role.mentionable}\n"
            f"**Position:** {role.position}\n"
            f"**Timestamp:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        ),
        color=discord.Color.green(),
        guild=role.guild
    )
    await log_channel.send(embed=embed)

@bot.event
async def on_guild_role_delete(role):
    """Log when a role is deleted"""
    log_channel = get_log_channel(role.guild)
    if not log_channel:
        return
    
    # Get who deleted the role from audit logs
    entry = await get_audit_log_entry(role.guild, discord.AuditLogAction.role_delete, role)
    deleted_by = entry.user.mention if entry and entry.user else "Unknown"
    
    embed = create_log_embed(
        title="🗑️ Role Deleted",
        description=(
            f"**Role:** {role.name} ({role.id})\n"
            f"**Deleted by:** {deleted_by}\n"
            f"**Color:** {role.color}\n"
            f"**Hoisted:** {role.hoist}\n"
            f"**Mentionable:** {role.mentionable}\n"
            f"**Position:** {role.position}\n"
            f"**Timestamp:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        ),
        color=discord.Color.red(),
        guild=role.guild
    )
    await log_channel.send(embed=embed)

@bot.event
async def on_guild_role_update(before, after):
    """Log when a role is updated"""
    log_channel = get_log_channel(after.guild)
    if not log_channel:
        return
    
    # Get who updated the role from audit logs
    entry = await get_audit_log_entry(after.guild, discord.AuditLogAction.role_update, after)
    updated_by = entry.user.mention if entry and entry.user else "Unknown"
    
    changes = []
    if before.name != after.name:
        changes.append(f"**Name:** {before.name} ➔ {after.name}")
    if before.color != after.color:
        changes.append(f"**Color:** {before.color} ➔ {after.color}")
    if before.hoist != after.hoist:
        changes.append(f"**Hoisted:** {before.hoist} ➔ {after.hoist}")
    if before.mentionable != after.mentionable:
        changes.append(f"**Mentionable:** {before.mentionable} ➔ {after.mentionable}")
    if before.position != after.position:
        changes.append(f"**Position:** {before.position} ➔ {after.position}")
    
    if not changes:
        return  # No significant changes to log
    
    embed = create_log_embed(
        title="✏️ Role Updated",
        description=(
            f"**Role:** {after.name} ({after.id})\n"
            f"**Updated by:** {updated_by}\n"
            f"**Changes:**\n" + "\n".join(changes) + "\n"
            f"**Timestamp:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        ),
        color=discord.Color.blue(),
        guild=after.guild
    )
    await log_channel.send(embed=embed)

@bot.event
async def on_guild_channel_create(channel):
    """Log when a channel is created"""
    log_channel = get_log_channel(channel.guild)
    if not log_channel:
        return
    
    # Get who created the channel from audit logs
    entry = await get_audit_log_entry(channel.guild, discord.AuditLogAction.channel_create, channel)
    created_by = entry.user.mention if entry and entry.user else "Unknown"
    
    embed = create_log_embed(
        title="🆕 Channel Created",
        description=(
            f"**Channel:** {channel.mention} ({channel.id})\n"
            f"**Type:** {str(channel.type).split('.')[-1].title()}\n"
            f"**Created by:** {created_by}\n"
            f"**Category:** {channel.category.mention if channel.category else 'None'}\n"
            f"**NSFW:** {channel.is_nsfw()}\n"
            f"**Timestamp:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        ),
        color=discord.Color.green(),
        guild=channel.guild
    )
    await log_channel.send(embed=embed)

@bot.event
async def on_guild_channel_delete(channel):
    """Log when a channel is deleted"""
    log_channel = get_log_channel(channel.guild)
    if not log_channel:
        return
    
    # Get who deleted the channel from audit logs
    entry = await get_audit_log_entry(channel.guild, discord.AuditLogAction.channel_delete, channel)
    deleted_by = entry.user.mention if entry and entry.user else "Unknown"
    
    embed = create_log_embed(
        title="🗑️ Channel Deleted",
        description=(
            f"**Channel:** {channel.name} ({channel.id})\n"
            f"**Type:** {str(channel.type).split('.')[-1].title()}\n"
            f"**Deleted by:** {deleted_by}\n"
            f"**Category:** {channel.category.mention if channel.category else 'None'}\n"
            f"**NSFW:** {channel.is_nsfw()}\n"
            f"**Timestamp:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        ),
        color=discord.Color.red(),
        guild=channel.guild
    )
    await log_channel.send(embed=embed)

@bot.event
async def on_guild_channel_update(before, after):
    """Log when a channel is updated"""
    log_channel = get_log_channel(after.guild)
    if not log_channel:
        return
    
    # Get who updated the channel from audit logs
    entry = await get_audit_log_entry(after.guild, discord.AuditLogAction.channel_update, after)
    updated_by = entry.user.mention if entry and entry.user else "Unknown"
    
    changes = []
    if before.name != after.name:
        changes.append(f"**Name:** {before.name} ➔ {after.name}")
    if before.category != after.category:
        changes.append(f"**Category:** {before.category.mention if before.category else 'None'} ➔ {after.category.mention if after.category else 'None'}")
    if hasattr(before, 'is_nsfw') and before.is_nsfw() != after.is_nsfw():
        changes.append(f"**NSFW:** {before.is_nsfw()} ➔ {after.is_nsfw()}")
    if hasattr(before, 'bitrate') and before.bitrate != after.bitrate:
        changes.append(f"**Bitrate:** {before.bitrate} ➔ {after.bitrate}")
    if hasattr(before, 'user_limit') and before.user_limit != after.user_limit:
        changes.append(f"**User Limit:** {before.user_limit} ➔ {after.user_limit}")
    
    if not changes:
        return  # No significant changes to log
    
    embed = create_log_embed(
        title="✏️ Channel Updated",
        description=(
            f"**Channel:** {after.mention} ({after.id})\n"
            f"**Updated by:** {updated_by}\n"
            f"**Changes:**\n" + "\n".join(changes) + "\n"
            f"**Timestamp:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        ),
        color=discord.Color.blue(),
        guild=after.guild
    )
    await log_channel.send(embed=embed)

@bot.event
async def on_guild_invite_create(invite):
    """Log when an invite is created"""
    log_channel = get_log_channel(invite.guild)
    if not log_channel:
        return
    
    # Get who created the invite from audit logs
    entry = await get_audit_log_entry(invite.guild, discord.AuditLogAction.invite_create, None)
    created_by = entry.user.mention if entry and entry.user else "Unknown"
    
    embed = create_log_embed(
        title="🆕 Invite Created",
        description=(
            f"**Invite:** {invite.url}\n"
            f"**Code:** {invite.code}\n"
            f"**Created by:** {created_by}\n"
            f"**Channel:** {invite.channel.mention if invite.channel else 'Unknown'}\n"
            f"**Max Uses:** {invite.max_uses if invite.max_uses else 'Unlimited'}\n"
            f"**Temporary:** {invite.temporary}\n"
            f"**Expires At:** {invite.expires_at.strftime('%Y-%m-%d %H:%M:%S') if invite.expires_at else 'Never'} UTC\n"
            f"**Timestamp:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        ),
        color=discord.Color.green(),
        guild=invite.guild
    )
    await log_channel.send(embed=embed)


##########################################################################
# give ban/unban/kick/unkick/timeout
##########################################################################

# Ban command
@bot.tree.command(name="ban", description="Ban a member from the server")
@app_commands.describe(member="The member to ban", reason="Reason for the ban")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = None):
    # Ensure we have a guild Member to check permissions (static analyzers treat interaction.user as User)
    invoker = interaction.guild.get_member(interaction.user.id) if interaction.guild else None
    if not invoker or not invoker.guild_permissions.administrator:
        await interaction.response.send_message("❌ You don't have permission to ban members.", ephemeral=True)
        return
    try:
        await member.ban(reason=reason)
        await interaction.response.send_message(f"✅ {member} has been banned. Reason: {reason or 'No reason provided'}")
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to ban this member.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"⚠️ Failed to ban {member}: {e}", ephemeral=True)
        await interaction.response.send_message(f"⚠️ Failed to ban {member}: {e}", ephemeral=True)


# Unban command
@bot.tree.command(name="unban", description="Unban a user")
@app_commands.describe(user="The user to unban")
async def unban(interaction: discord.Interaction, user: discord.User):
    # Ensure this command is used in a guild and resolve the invoking user to a Member
    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message("❌ This command can only be used in a server (guild).", ephemeral=True)
        return

    invoker = guild.get_member(interaction.user.id)
    if not invoker or not invoker.guild_permissions.administrator:
        await interaction.response.send_message("❌ You don't have permission to unban members.", ephemeral=True)
        return
    try:
        await guild.unban(user)
        await interaction.response.send_message(f"✅ {user} has been unbanned.")
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to unban that user.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"⚠️ Failed to unban {user}: {e}", ephemeral=True)


# Kick command
@bot.tree.command(name="kick", description="Kick a member from the server")
@app_commands.describe(member="The member to kick", reason="Reason for the kick")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = None):
    # Ensure this command is used in a guild
    if interaction.guild is None:
        await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
        return

    # Resolve the invoking user to a Member so we can check guild permissions
    invoker = interaction.guild.get_member(interaction.user.id)
    if not invoker or not invoker.guild_permissions.administrator:
        await interaction.response.send_message("❌ You don't have permission to kick members.", ephemeral=True)
        return

    try:
        await member.kick(reason=reason)
        await interaction.response.send_message(f"✅ {member} has been kicked. Reason: {reason or 'No reason provided'}")
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to kick this member.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"⚠️ Failed to kick {member}: {e}", ephemeral=True)


# Timeout command
@bot.tree.command(name="timeout", description="Timeout a member for a certain number of seconds")
@app_commands.describe(member="The member to timeout", seconds="Number of seconds to timeout", reason="Reason for timeout")
async def timeout(interaction: discord.Interaction, member: discord.Member, seconds: int, reason: Optional[str] = None):
    # Ensure this command is used in a guild and resolve the invoking user to a Member
    if interaction.guild is None:
        await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
        return

    invoker = interaction.guild.get_member(interaction.user.id)
    if not invoker or not invoker.guild_permissions.administrator:
        await interaction.response.send_message("❌ You don't have permission to timeout members.", ephemeral=True)
        return
    try:
        duration = timedelta(seconds=seconds)
        until = datetime.utcnow() + duration
        # Use Member.edit to set the timed_out_until field (discord.py API)
        await member.edit(timed_out_until=until, reason=reason)
        await interaction.response.send_message(
            f"✅ {member.mention} has been timed out for {seconds} seconds. Reason: {reason or 'No reason provided'}"
        )
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to timeout this member.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"⚠️ Failed to timeout {member}: {e}", ephemeral=True)

# Remove timeout command
@bot.tree.command(name="remove_timeout", description="Remove a timeout from a member")
@app_commands.describe(member="The member to remove timeout from")
async def remove_timeout(interaction: discord.Interaction, member: discord.Member):
    # Ensure this command is used in a guild and resolve the invoking user to a Member
    if interaction.guild is None:
        await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
        return

    invoker = interaction.guild.get_member(interaction.user.id)
    if not invoker or not invoker.guild_permissions.administrator:
        await interaction.response.send_message("❌ You don't have permission to remove timeouts.", ephemeral=True)
        return
    try:
        # Use Member.edit to clear the timeout
        await member.edit(timed_out_until=None, reason=f"Timeout removed by {interaction.user}")
        await interaction.response.send_message(f"✅ Timeout removed from {member}.")
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to remove timeout from this member.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"⚠️ Error: {e}", ephemeral=True)

    

#########################################
# SEND MESSAGE MEMBERS TO DM
#########################################

@bot.command()
@commands.has_permissions(administrator=True)
async def dm_all(ctx, *, message):
    """DM all members in the server"""
    success_count = 0
    fail_count = 0
    for member in ctx.guild.members:
        if member.bot:
            continue  # Skip bots
        try:
            await member.send(message)
            success_count += 1
            await asyncio.sleep(1)  # Sleep to avoid rate limits
        except Exception as e:
            fail_count += 1
            print(f"Failed to DM {member}: {e}")
    await ctx.send(f"DM sent to {success_count} members. Failed to DM {fail_count} members.")

###########################################
# send dm to member
###########################################

@bot.tree.command(name="dm_member", description="DM a specific member")
@app_commands.describe(member="The member to DM", message="The message to send")
async def dm_member(interaction: discord.Interaction, member: discord.Member, message: str):
    """DM a specific member via slash command"""
    try:
        await member.send(message)
        await interaction.response.send_message(f"✅ DM sent to {member.mention}.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to DM {member.mention}: {e}", ephemeral=True)


#########################################
# exemple Slash cmd
#########################################
###        @bot.tree.command(name="help", description="Take info about ")
###      async def help_command(interaction: discord.Interaction):
###          embed = discord.Embed(
###              title="ALX Morocco",
###              description=(
###                  "ALX Morocco is part of **ALX Africa**, an organization that trains the next generation of "
###                  "leaders and innovators across Africa.\n\n"
###                  "They provide **tech programs** (Software Engineering, Data Analysis, Cloud Computing, and more), "
###                  "as well as **leadership and soft skills training**. Learners get access to both online learning "
###                  "and **physical hubs** in Morocco (Casablanca, Rabat, etc.) for collaboration and networking.\n\n"
###                  "✨ A great place if you're starting your journey in tech or leadership!"
###              ),
###              color=discord.Color.blue()
###          )
###          embed.set_thumbnail(url="https://r2.fivemanage.com/2Fmxtyz3enFCAcfC5wghD/IMG_1071.jpg")
###          embed.add_field(name="🌍 Programs", value="Software Engineering, Data Analysis, Cloud Computing, and more", inline=False)
###          embed.add_field(name="📍 Hubs", value="Casablanca, Rabat, and other cities", inline=True)
###          embed.add_field(name="💡 Benefits", value="Global-standard training, community support, and career opportunities", inline=False)
###          embed.set_footer(text=f"Powered by ALX Africa | Requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)
###          await interaction.response.send_message(embed=embed)



bot.tree.command(name="give_role", description="Give a role to a member")
@app_commands.describe(member="The member to give the role to", role="The role to give")
async def give_role(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    # Ensure this command is used in a guild and resolve the invoking user to a Member
    if interaction.guild is None:
        await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
        return
    invoker = interaction.guild.get_member(interaction.user.id)
    if not invoker or not invoker.guild_permissions.manage_roles:
        await interaction.response.send_message("❌ You don't have permission to manage roles.", ephemeral=True)
        return
    try:
        await member.add_roles(role)
        await interaction.response.send_message(f"✅ {role.mention} has been given to {member.mention}.")
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to assign that role.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"⚠️ Error: {e}", ephemeral=True)

# remove role command
bot.tree.command(name="remove_role", description="Remove a role from a member")
@app_commands.describe(member="The member to remove the role from", role="The role to remove")
async def remove_role(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    # Ensure this command is used in a guild and resolve the invoking user to a Member
    if interaction.guild is None:
        await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
        return
    invoker = interaction.guild.get_member(interaction.user.id)
    if not invoker or not invoker.guild_permissions.manage_roles:
        await interaction.response.send_message("❌ You don't have permission to manage roles.", ephemeral=True)
        return
    try:
        await member.remove_roles(role)
        await interaction.response.send_message(f"✅ {role.mention} has been removed from {member.mention}.")
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to remove that role.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"⚠️ Error: {e}", ephemeral=True)


# clear messages command
bot.tree.command(name="clear", description="Clear messages in a channel")
@app_commands.describe(number="Number of messages to delete (max 100)")
async def clear(interaction: discord.Interaction, number: int):
    # Ensure this command is used in a guild and resolve the invoking user to a Member
    if interaction.guild is None:
        await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
        return
    invoker = interaction.guild.get_member(interaction.user.id)
    if not invoker or not invoker.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ You don't have permission to manage messages.", ephemeral=True)
        return
    if number < 1 or number > 100:
        await interaction.response.send_message("❌ Please specify a number between 1 and 100.", ephemeral=True)
        return

    channel = interaction.channel
    # Only allow clearing in a guild text channel (not forum/category/DM/group)
    if channel is None or not isinstance(channel, discord.TextChannel):
        await interaction.response.send_message("❌ This command can only be used in a text channel.", ephemeral=True)
        return

    try:
        # Collect the messages to delete then bulk delete them (avoids calling purge on non-text channels)
        messages = [msg async for msg in channel.history(limit=number)]
        if not messages:
            await interaction.response.send_message("No messages to delete.", ephemeral=True)
            return

        deleted = await channel.delete_messages(messages)
        # delete_messages may return None or a list depending on the library version; derive count safely
        count = len(deleted) if deleted else len(messages)
        await interaction.response.send_message(f"🗑️ Deleted {count} messages.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"⚠️ Failed to delete messages: {e}", ephemeral=True)

# lock/unlock channel commands
bot.tree.command(name="lock", description="disable @everyone from sending messages in a channel")
async def lock(interaction: discord.Interaction):
    # Ensure this command is used in a guild and resolve the invoking user to a Member
    if interaction.guild is None:
        await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
        return
    invoker = interaction.guild.get_member(interaction.user.id)
    if not invoker or not invoker.guild_permissions.manage_roles:
        await interaction.response.send_message("❌ You don't have permission to manage roles.", ephemeral=True)
        return

    channel = interaction.channel
    # Ensure the channel is a guild channel that supports set_permissions (avoid Threads/DMs/GroupChannels)
    if channel is None or not isinstance(channel, discord.abc.GuildChannel):
        await interaction.response.send_message("❌ This command can only be used in a server text channel.", ephemeral=True)
        return

    try:
        await channel.set_permissions(interaction.guild.default_role, send_messages=False)
        await interaction.response.send_message("🔒 Channel has been locked.")
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to change channel permissions.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"⚠️ Failed to lock channel: {e}", ephemeral=True)


bot.tree.command(name="unlock", description="enable @everyone to send messages in a channel")
async def unlock(interaction: discord.Interaction):
    # Ensure this command is used in a guild and resolve the invoking user to a Member
    if interaction.guild is None:
        await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
        return
    invoker = interaction.guild.get_member(interaction.user.id)
    if not invoker or not invoker.guild_permissions.manage_roles:
        await interaction.response.send_message("❌ You don't have permission to manage roles.", ephemeral=True)
        return

    channel = interaction.channel
    # Ensure the channel is a guild channel that supports set_permissions (avoid Threads/DMs/GroupChannels)
    if channel is None or not isinstance(channel, discord.abc.GuildChannel):
        await interaction.response.send_message("❌ This command can only be used in a server text channel.", ephemeral=True)
        return

    try:
        await channel.set_permissions(interaction.guild.default_role, send_messages=True)
        await interaction.response.send_message("🔓 Channel has been unlocked.")
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to change channel permissions.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"⚠️ Failed to unlock channel: {e}", ephemeral=True)

# Move all members to the voice channel you are in
bot.tree.command(name="move all", description="Move all members to the voice channel you are in")
async def move_all(interaction: discord.Interaction):
    # Ensure this command is used in a guild and resolve the invoking user to a Member
    if interaction.guild is None:
        await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
        return
    invoker = interaction.guild.get_member(interaction.user.id)
    if not invoker or not invoker.guild_permissions.move_members:
        await interaction.response.send_message("❌ You don't have permission to move members.", ephemeral=True)
        return
    if not invoker.voice or not invoker.voice.channel:
        await interaction.response.send_message("❌ You need to be in a voice channel to use this command.", ephemeral=True)
        return
    target_channel = invoker.voice.channel
    moved_count = 0
    for member in interaction.guild.members:
        if member.voice and member.voice.channel and member != invoker:
            try:
                await member.move_to(target_channel)
                moved_count += 1
                print(f"Moved {member} to {target_channel}")
            except Exception as e:
                # Log the failure and continue with other members
                print(f"Failed to move {member} to {target_channel}: {e}")
    # Send a summary response after attempting to move members
    try:
        await interaction.response.send_message(f"✅ Moved {moved_count} members to {target_channel.mention}.")
    except Exception:
        # In case the interaction response cannot be sent (already responded or other), just log
        print(f"Could not send interaction response for move_all command in guild {interaction.guild.id}")

# Move a specific user to the voice channel you are in
bot.tree.command(name="move user", description="Move a specific user to the voice channel you are in")
@app_commands.describe(member="The member to move")
async def move_user(interaction: discord.Interaction, member: discord.Member):
    # Ensure this command is used in a guild and resolve the invoking user to a Member
    if interaction.guild is None:
        await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
        return

    invoker = interaction.guild.get_member(interaction.user.id)
    if not invoker or not invoker.guild_permissions.move_members:
        await interaction.response.send_message("❌ You don't have permission to move members.", ephemeral=True)
        return
    if not invoker.voice or not invoker.voice.channel:
        await interaction.response.send_message("❌ You need to be in a voice channel to use this command.", ephemeral=True)
        return
    target_channel = invoker.voice.channel
    if not member.voice or not member.voice.channel:
        await interaction.response.send_message(f"❌ {member.mention} is not in a voice channel.", ephemeral=True)
        return
    try:
        await member.move_to(target_channel)
        await interaction.response.send_message(f"✅ Moved {member.mention} to {target_channel.mention}.")
    except Exception as e:
        await interaction.response.send_message(f"⚠️ Failed to move {member.mention}: {e}", ephemeral=True)

# Move yourself to another voice channel
bot.tree.command(name="moveme", description="Move yourself to another voice channel")
async def moveme(interaction: discord.Interaction, channel: discord.VoiceChannel):
    # Ensure this command is used in a guild and resolve the invoking user to a Member
    if interaction.guild is None:
        await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
        return
    invoker = interaction.guild.get_member(interaction.user.id)
    if not invoker or not invoker.guild_permissions.move_members:
        await interaction.response.send_message("❌ You don't have permission to move members.", ephemeral=True)
        return
    if not invoker.voice or not invoker.voice.channel:
        await interaction.response.send_message("❌ You need to be in a voice channel to use this command.", ephemeral=True)
        return
    if not channel or not isinstance(channel, discord.VoiceChannel):
        await interaction.response.send_message("❌ Please specify a valid voice channel.", ephemeral=True)
        return
    try:
        await invoker.move_to(channel)
        await interaction.response.send_message(f"✅ Moved you to {channel.mention}.")
    except Exception as e:
        await interaction.response.send_message(f"⚠️ Failed to move you: {e}", ephemeral=True)
        print(f"Failed to move {invoker} to {channel}: {e}")

#########################################
# Function to log ticket closure
#########################################
async def log_ticket_close(guild, channel, closed_by, reason):
    if not TICKET_LOG_CHANNEL_ID:
        return
    
    log_channel = guild.get_channel(TICKET_LOG_CHANNEL_ID)
    if not log_channel:
        return
    
    # Get ticket opener from channel topic
    ticket_opener = "Unknown"
    if channel.topic:
        ticket_opener = channel.topic.split("Ticket by ")[1] if "Ticket by " in channel.topic else "Unknown"
    
    # Create transcript
    messages = []
    async for msg in channel.history(limit=100, oldest_first=True):
        timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
        messages.append(f"[{timestamp}] {msg.author}: {msg.content}")
    
    transcript_text = "\n".join(messages)
    
    # Create log embed
    log_embed = discord.Embed(
        title="🔒 Ticket Closed",
        color=discord.Color.red(),
        timestamp=datetime.utcnow()
    )
    log_embed.add_field(name="📋 Ticket Name", value=channel.name, inline=True)
    log_embed.add_field(name="👤 Opened By", value=ticket_opener, inline=True)
    log_embed.add_field(name="🔐 Closed By", value=closed_by.mention, inline=True)
    log_embed.add_field(name="📝 Reason", value=reason, inline=False)
    log_embed.set_footer(text=f"Ticket ID: {channel.id}")
    
    # Save transcript to file
    filename = f"transcript-{channel.name}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Ticket Transcript: {channel.name}\n")
        f.write(f"Opened by: {ticket_opener}\n")
        f.write(f"Closed by: {closed_by}\n")
        f.write(f"Reason: {reason}\n")
        f.write(f"Closed at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*50 + "\n\n")
        f.write(transcript_text)
    
    # Send log with transcript
    await log_channel.send(embed=log_embed, file=discord.File(filename))

# Modal for close reason
# Modal for close reason
class CloseReasonModal(discord.ui.Modal, title="Close Ticket with Reason"):
    reason = discord.ui.TextInput(
        label="Reason for closing",
        placeholder="Enter the reason for closing this ticket...",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=500
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.channel
        
        # Generate transcript
        messages = []
        async for msg in channel.history(limit=None, oldest_first=True):
            timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
            content = msg.content if msg.content else "[No text content]"
            attachments = f" [Attachments: {', '.join([a.filename for a in msg.attachments])}]" if msg.attachments else ""
            messages.append(f"[{timestamp}] {msg.author.name}: {content}{attachments}")
        
        transcript_text = "\n".join(messages)
        filename = os.path.join(TRANSCRIPT_PATH, f"transcript-{channel.name}.txt")
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Ticket Transcript: {channel.name}\n")
            f.write(f"Channel ID: {channel.id}\n")
            f.write(f"Closed at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
            f.write(f"Closed by: {interaction.user.name}\n")
            f.write(f"Close Reason: {self.reason.value}\n")
            f.write("="*70 + "\n\n")
            f.write(transcript_text)
        
        # Send log with transcript before closing
        if LOG_CHANNEL_ID:
            log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                log_embed = discord.Embed(
                    title="🔒 Ticket Closed",
                    color=discord.Color.red(),
                    timestamp=datetime.utcnow()
                )
                log_embed.add_field(name="Ticket", value=channel.name, inline=True)
                log_embed.add_field(name="Closed by", value=interaction.user.mention, inline=True)
                log_embed.add_field(name="Reason", value=self.reason.value, inline=False)
                log_embed.add_field(name="Messages", value=f"{len(messages)} messages", inline=True)
                log_embed.set_footer(text=f"Ticket ID: {channel.id}")

            await log_channel.send(embed=log_embed, file=discord.File(filename))
        
        embed = discord.Embed(
            title="🔒 Ticket Closing",
            description=f"**Closed by:** {interaction.user.mention}\n**Reason:** {self.reason.value}\n\nThis ticket will be deleted in 5 seconds...",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        
        await interaction.response.send_message(embed=embed)
        await asyncio.sleep(5)
        await channel.delete()

# Ticket Control Buttons (Close/Close with Reason)
class TicketControlView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="🔒 Close", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_button(self, interaction: discord.Interaction, button: Button):
        channel = interaction.channel
        
        # Generate transcript
        messages = []
        async for msg in channel.history(limit=None, oldest_first=True):
            timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
            content = msg.content if msg.content else "[No text content]"
            attachments = f" [Attachments: {', '.join([a.filename for a in msg.attachments])}]" if msg.attachments else ""
            messages.append(f"[{timestamp}] {msg.author.name}: {content}{attachments}")
        
        transcript_text = "\n".join(messages)
        filename = f"transcript-{channel.name}.txt"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Ticket Transcript: {channel.name}\n")
            f.write(f"Channel ID: {channel.id}\n")
            f.write(f"Closed at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
            f.write(f"Closed by: {interaction.user.name}\n")
            f.write("="*70 + "\n\n")
            f.write(transcript_text)
        
        # Send log with transcript before closing
        if LOG_CHANNEL_ID:
            log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                log_embed = discord.Embed(
                    title="🔒 Ticket Closed",
                    color=discord.Color.red(),
                    timestamp=datetime.utcnow()
                )
                log_embed.add_field(name="Ticket", value=channel.name, inline=True)
                log_embed.add_field(name="Closed by", value=interaction.user.mention, inline=True)
                log_embed.add_field(name="Reason", value="No reason provided", inline=False)
                log_embed.add_field(name="Messages", value=f"{len(messages)} messages", inline=True)
                log_embed.set_footer(text=f"Ticket ID: {channel.id}")

            await log_channel.send(embed=log_embed, file=discord.File(filename))
        
        embed = discord.Embed(
            title="🔒 Ticket Closing",
            description=f"This ticket will be closed in 5 seconds...\nClosed by {interaction.user.mention}",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        
        await interaction.response.send_message(embed=embed)
        await asyncio.sleep(5)
        await channel.delete()
    
    @discord.ui.button(label="📝 Close with Reason", style=discord.ButtonStyle.gray, custom_id="close_ticket_reason")
    async def close_reason_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(CloseReasonModal())

# Ticket Button View
class TicketButton(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="🔹 Support", style=discord.ButtonStyle.success, custom_id="create_ticket")
    async def ticket_button(self, interaction: discord.Interaction, button: Button):
        global TICKET_COUNTER
        TICKET_COUNTER += 1
        
        guild = interaction.guild
        category = discord.utils.get(guild.categories, id=SUPPORT_TICKET_CATEGORY_ID) if SUPPORT_TICKET_CATEGORY_ID else None

        ticket_name = f"Support Ticket-{interaction.user.name}-{TICKET_COUNTER}-"

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        if STAFF_ROLE_ID:
            staff_role = guild.get_role(STAFF_ROLE_ID)
            if staff_role:
                overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        
        channel = await guild.create_text_channel(
            name=ticket_name,
            category=category,
            overwrites=overwrites,
            topic=f"Ticket by {interaction.user.name}"
        )
        
        embed = discord.Embed(
            title="🎫 New Support Ticket Created",
            description=f"**Opened by:** {interaction.user.mention}\n\nPlease describe your issue and wait for staff to assist you.",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Ticket #{TICKET_COUNTER}")
        
        control_view = TicketControlView()
        await channel.send(f"{interaction.user.mention}", embed=embed, view=control_view)
        await interaction.response.send_message(f"✅ Support Ticket created! {channel.mention}", ephemeral=True)

    @discord.ui.button(label="💳 Purchase", style=discord.ButtonStyle.primary, custom_id="create_purchase_ticket")
    async def purchase_ticket_button(self, interaction: discord.Interaction, button: Button):
        global TICKET_COUNTER
        TICKET_COUNTER += 1

        guild = interaction.guild
        category = discord.utils.get(guild.categories, id=PURCHASE_TICKET_CATEGORY_ID) if PURCHASE_TICKET_CATEGORY_ID else None

        ticket_name = f"Purchase Ticket-{interaction.user.name}-{TICKET_COUNTER}-"

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        if STAFF_ROLE_ID:
            staff_role = guild.get_role(STAFF_ROLE_ID)
            if staff_role:
                overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        channel = await guild.create_text_channel(
            name=ticket_name,
            category=category,
            overwrites=overwrites,
            topic=f"Ticket by {interaction.user.name}"
        )

        embed = discord.Embed(
            title="💳 New Purchase Ticket Created",
            description=f"**Opened by:** {interaction.user.mention}\n\nPlease describe the Bug and wait for staff to assist you.",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Ticket #{TICKET_COUNTER}")

        control_view = TicketControlView()
        await channel.send(f"{interaction.user.mention}", embed=embed, view=control_view)
        await interaction.response.send_message(f"✅ Purchase Ticket created! {channel.mention}", ephemeral=True)

    @discord.ui.button(label="🐞 Bug", style=discord.ButtonStyle.danger, custom_id="create_bug_ticket")
    async def bug_ticket_button(self, interaction: discord.Interaction, button: Button):
         global TICKET_COUNTER
         TICKET_COUNTER += 1

         guild = interaction.guild
         category = discord.utils.get(guild.categories, id=BUG_TICKET_CATEGORY_ID) if BUG_TICKET_CATEGORY_ID else None

         ticket_name = f"Bug Ticket-{interaction.user.name}-{TICKET_COUNTER}-"

         overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

         if STAFF_ROLE_ID:
            staff_role = guild.get_role(STAFF_ROLE_ID)
            if staff_role:
                overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

         channel = await guild.create_text_channel(
            name=ticket_name,
            category=category,
            overwrites=overwrites,
            topic=f"Ticket by {interaction.user.name}"
        )

         embed = discord.Embed(
            title="🐞 Bug New Bug Ticket Created",
            description=f"**Opened by:** {interaction.user.mention}\n\nPlease describe the Bug and wait for staff to assist you.",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
         embed.set_footer(text=f"Ticket #{TICKET_COUNTER}")

         control_view = TicketControlView()
         await channel.send(f"{interaction.user.mention}", embed=embed, view=control_view)
         await interaction.response.send_message(f"✅ Bug Ticket created! {channel.mention}", ephemeral=True)



# Command to send ticket panel
@bot.tree.command(name="ticket-panel", description="Send the ticket panel with button")
@app_commands.checks.has_permissions(administrator=True)
async def ticket_panel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎫 Ticket System",
        description="Need help? Click the button below to create a help ticket.\n\n**📌 Interact with the topic ticket based on what you need:**\n\n",
        color=discord.Color.red()
    )

    embed.set_image(url="https://r2.fivemanage.com/poTLxCGLNuOK6bV2kOopL/trailer.jpg")
    embed.set_thumbnail(url="https://r2.fivemanage.com/poTLxCGLNuOK6bV2kOopL/layer.png")


    embed.add_field(name="📋 The Button Ticket", value="🔹 Support → If you need general help with the server (rules, features, or how something works).\n\n  💳 Purchase → If you are interested in buying a pack, benefit, or service within the server.\n\n  🐞 Bug → If you found an error, glitch, or bug in the server and want to report it so we can fix it.", inline=False)
    embed.set_footer(text="Our staff will respond as soon as possible")
    
    view = TicketButton()
    await interaction.channel.send(embed=embed, view=view)
    await interaction.response.send_message("✅ Ticket panel sent!", ephemeral=True)

@bot.tree.command(name="close", description="Close the current ticket")
async def close(interaction: discord.Interaction):
    channel = interaction.channel
    
    if not channel.name.startswith("ticket-"):
        await interaction.response.send_message("❌ This command can only be used in ticket channels!", ephemeral=True)
        return
    
    # Generate transcript
    messages = []
    async for msg in channel.history(limit=None, oldest_first=True):
        timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
        content = msg.content if msg.content else "[No text content]"
        attachments = f" [Attachments: {', '.join([a.filename for a in msg.attachments])}]" if msg.attachments else ""
        messages.append(f"[{timestamp}] {msg.author.name}: {content}{attachments}")
    
    transcript_text = "\n".join(messages)
    filename = f"transcript-{channel.name}.txt"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Ticket Transcript: {channel.name}\n")
        f.write(f"Channel ID: {channel.id}\n")
        f.write(f"Closed at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
        f.write(f"Closed by: {interaction.user.name}\n")
        f.write("="*70 + "\n\n")
        f.write(transcript_text)
    
    # Send log with transcript before closing
    if LOG_CHANNEL_ID:
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="🔒 Ticket Closed",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            log_embed.add_field(name="Ticket", value=channel.name, inline=True)
            log_embed.add_field(name="Closed by", value=interaction.user.mention, inline=True)
            log_embed.add_field(name="Reason", value="Closed via command", inline=False)
            log_embed.add_field(name="Messages", value=f"{len(messages)} messages", inline=True)
            log_embed.set_footer(text=f"Ticket ID: {channel.id}")
            await log_channel.send(embed=log_embed, file=discord.File(filename))
    
    embed = discord.Embed(
        title="🔒 Ticket Closing",
        description=f"This ticket will be closed in 5 seconds...\nClosed by {interaction.user.mention}",
        color=discord.Color.red(),
        timestamp=datetime.utcnow()
    )
    
    await interaction.response.send_message(embed=embed)
    await asyncio.sleep(5)
    await channel.delete()

@bot.tree.command(name="add", description="Add a user to the ticket")
@app_commands.describe(member="The member to add to this ticket")
async def add(interaction: discord.Interaction, member: discord.Member):
    channel = interaction.channel
    
    if not channel.name.startswith("ticket-"):
        await interaction.response.send_message("❌ This command can only be used in ticket channels!", ephemeral=True)
        return
    
    await channel.set_permissions(member, read_messages=True, send_messages=True)
    
    embed = discord.Embed(
        description=f"✅ {member.mention} has been added to the ticket by {interaction.user.mention}",
        color=discord.Color.blue()
    )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="remove", description="Remove a user from the ticket")
@app_commands.describe(member="The member to remove from this ticket")
async def remove(interaction: discord.Interaction, member: discord.Member):
    channel = interaction.channel
    
    if not channel.name.startswith("ticket-"):
        await interaction.response.send_message("❌ This command can only be used in ticket channels!", ephemeral=True)
        return
    
    await channel.set_permissions(member, overwrite=None)
    
    embed = discord.Embed(
        description=f"✅ {member.mention} has been removed from the ticket by {interaction.user.mention}",
        color=discord.Color.orange()
    )
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="transcript", description="Generate a transcript of the ticket")
async def transcript(interaction: discord.Interaction):
    channel = interaction.channel
    
    if not channel.name.startswith("ticket-"):
        await interaction.response.send_message("❌ This command can only be used in ticket channels!", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    
    messages = []
    async for msg in channel.history(limit=None, oldest_first=True):
        timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
        messages.append(f"[{timestamp}] {msg.author}: {msg.content}")
    
    transcript_text = "\n".join(messages)
    
    filename = f"transcript-{channel.name}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Ticket Transcript: {channel.name}\n")
        f.write(f"Generated at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*50 + "\n\n")
        f.write(transcript_text)
    
    await interaction.followup.send("📄 Transcript generated!", file=discord.File(filename), ephemeral=True)
    






# ======================
# 🔧 Slash Command Setup
# ======================
@bot.tree.command(name="setup-voice", description="Set up OneTap voice system")
@app_commands.describe(
    hub_channel="The hub voice channel users join to create their own room",
    category="The category where personal rooms will appear"
)
async def setup_voice(interaction: discord.Interaction, hub_channel: discord.VoiceChannel, category: discord.CategoryChannel):
    guild_settings[interaction.guild.id] = {
        "hub_id": hub_channel.id,
        "category_id": category.id
    }
    await interaction.response.send_message(
        f"✅ Setup complete!\nHub channel: **{hub_channel.name}**\nCategory: **{category.name}**"
    )

# ======================
# one tap voice event
# ======================
@bot.event
async def on_voice_state_update(member, before, after):
    # Ignore bots
    if member.bot:
        return

    # Check if guild has setup data
    data = guild_settings.get(member.guild.id)
    if not data:
        return

    hub_id = data["hub_id"]
    category = member.guild.get_channel(data["category_id"])

    # User joins the hub channel
    if after.channel and after.channel.id == hub_id:
        new_channel = await member.guild.create_voice_channel(
            name=f"{member.display_name}'s Room",
            category=category,
            user_limit=None  # You can set a limit if desired
        )

        await new_channel.set_permissions(member, manage_channels=True, connect=True, move_members=True)
        await member.move_to(new_channel)

        print(f"🎤 Created room for {member.display_name}")

        # Background task: delete room when empty
        async def delete_when_empty(channel):
            await asyncio.sleep(1)  # small delay to prevent instant deletion
            while True:
                await asyncio.sleep(2)
                if len(channel.members) == 0:
                    await channel.delete()
                    print(f"🗑️ Deleted empty room {channel.name}")
                    break

        bot.loop.create_task(delete_when_empty(new_channel))




############################
# application commands runner
############################
class ApplicationModal(discord.ui.Modal, title="Application Form"):
    name = discord.ui.TextInput(
        label="Full Name (rp)",
        placeholder="Enter your full name...",
        required=True,
        max_length=50
    )
    
    age = discord.ui.TextInput(
        label="Your Age (rp)",
        placeholder="Enter your age...",
        required=True,
        max_length=3
    )
    
    reason = discord.ui.TextInput(
        label="Why do you want to Join server?",
        placeholder="Tell us why you want to be part of our community...",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=500
    )
    
    experience = discord.ui.TextInput(
        label="Previous Experience (Optional)",
        placeholder="Tell us about your relevant experience...",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=500
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        # Create application embed
        embed = discord.Embed(
            title="📝 New Application",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Applicant", value=interaction.user.mention, inline=True)
        embed.add_field(name="User ID", value=interaction.user.id, inline=True)
        embed.add_field(name="Name", value=self.name.value, inline=False)
        embed.add_field(name="Age", value=self.age.value, inline=True)
        embed.add_field(name="Reason", value=self.reason.value, inline=False)
        
        if self.experience.value:
            embed.add_field(name="Experience", value=self.experience.value, inline=False)
        
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(text=f"Application ID: {interaction.user.id}")
        
        # Send to application channel with review buttons
        if APPLICATION_CHANNEL_ID:
            app_channel = interaction.guild.get_channel(APPLICATION_CHANNEL_ID)
            if app_channel:
                view = ApplicationReviewView(interaction.user.id)
                await app_channel.send(embed=embed, view=view)
        
        # Confirm to user
        await interaction.response.send_message(
            "✅ Your application has been submitted successfully! Our staff will review it soon.",
            ephemeral=True
        )

# Application Review Buttons
class ApplicationReviewView(View):
    def __init__(self, applicant_id):
        super().__init__(timeout=None)
        self.applicant_id = applicant_id
    
    @discord.ui.button(label="✅ Accept", style=discord.ButtonStyle.green, custom_id="accept_app")
    async def accept_button(self, interaction: discord.Interaction, button: Button):
        # Get the applicant
        member = interaction.guild.get_member(self.applicant_id)
        
        if not member:
            await interaction.response.send_message("❌ User not found in server!", ephemeral=True)
            return
        
        # Add role if configured
        if ACCEPTED_ROLE_ID:
            role = interaction.guild.get_role(ACCEPTED_ROLE_ID)
            if role:
                await member.add_roles(role)
        
        # Update embed
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.green()
        embed.title = "✅ Application Accepted"
        embed.add_field(name="Reviewed by", value=interaction.user.mention, inline=True)
        embed.add_field(name="Status", value="ACCEPTED", inline=True)
        
        # Disable buttons
        for item in self.children:
            item.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)
        
        # DM the applicant
        try:
            dm_embed = discord.Embed(
                title="✅ Application Accepted!",
                description=f"Congratulations! Your application for **{interaction.guild.name}** has been accepted!",
                color=discord.Color.green()
            )
            await member.send(embed=dm_embed)
        except:
            pass
    
    @discord.ui.button(label="❌ Reject", style=discord.ButtonStyle.red, custom_id="reject_app")
    async def reject_button(self, interaction: discord.Interaction, button: Button):
        modal = RejectReasonModal(self.applicant_id, interaction.message)
        await interaction.response.send_modal(modal)

# Reject Reason Modal
class RejectReasonModal(discord.ui.Modal, title="Rejection Reason"):
    reason = discord.ui.TextInput(
        label="Reason for rejection",
        placeholder="Enter the reason (optional)...",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=500
    )
    
    def __init__(self, applicant_id, message):
        super().__init__()
        self.applicant_id = applicant_id
        self.message = message
    
    async def on_submit(self, interaction: discord.Interaction):
        member = interaction.guild.get_member(self.applicant_id)
        
        # Update embed
        embed = self.message.embeds[0]
        embed.color = discord.Color.red()
        embed.title = "❌ Application Rejected"
        embed.add_field(name="Reviewed by", value=interaction.user.mention, inline=True)
        embed.add_field(name="Status", value="REJECTED", inline=True)
        
        if self.reason.value:
            embed.add_field(name="Rejection Reason", value=self.reason.value, inline=False)
        
        # Disable buttons
        view = ApplicationReviewView(self.applicant_id)
        for item in view.children:
            item.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=view)
        
        # DM the applicant
        if member:
            try:
                dm_embed = discord.Embed(
                    title="❌ Application Rejected",
                    description=f"Unfortunately, your application for **{interaction.guild.name}** has been rejected.",
                    color=discord.Color.red()
                )
                if self.reason.value:
                    dm_embed.add_field(name="Reason", value=self.reason.value)
                await member.send(embed=dm_embed)
            except:
                pass

# Application Button
class ApplicationButton(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="📝 Apply Now", style=discord.ButtonStyle.blurple, custom_id="apply_button")
    async def apply_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(ApplicationModal())

# Command to send application panel
@bot.tree.command(name="application-panel", description="Send the application panel")
@app_commands.checks.has_permissions(administrator=True)
async def application_panel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📝 Join Our Team!",
        description="Interested in joining our community? Click the button below to submit your application.\n\n**Requirements:**\n• Be respectful\n• Be active\n• Follow our rules",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="📋 What to expect",
        value="Fill out a short form and our staff will review your application within 24-48 hours.",
        inline=False
    )
    embed.set_footer(text="Good luck with your application!")
    
    view = ApplicationButton()
    await interaction.channel.send(embed=embed, view=view)
    await interaction.response.send_message("✅ Application panel sent!", ephemeral=True)

bot.run(TOKEN)