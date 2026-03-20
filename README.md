# 🔱 TurboBot Pro: All-in-One Discord Management Suite

**TurboBot Pro** is a high-performance, multi-functional Discord bot built with `discord.py`. It combines advanced server moderation, a professional ticketing system, music streaming, and automated community management into a single package.

## ✨ Core Modules

### 🎫 Advanced Ticketing System
* **Multi-Category Support:** Dedicated buttons for Support, Purchases, and Bug Reporting.
* **Automated Transcripts:** Generates and logs full `.txt` transcripts of conversations upon ticket closure.
* **Staff Controls:** Easy-to-use commands to add/remove users from tickets and close with specific reasons.

### 📝 Recruitment & Applications
* **Interactive Forms:** Uses Discord Modals for clean, structured user applications.
* **Staff Review Panel:** Dedicated channel for staff to Accept or Reject applications with one click.
* **Automated Status DMs:** Notifies applicants immediately when their status changes.

### 🎵 Music & Voice Features
* **High-Quality Streaming:** Powered by `yt-dlp` and `FFmpeg` for stable audio playback from YouTube.
* **OneTap Voice Rooms:** Users join a "Hub" channel to automatically create their own private, temporary voice room.
* **Dynamic Deletion:** Rooms are automatically deleted when empty to keep the server clean.

### 🛡️ Security & Logging
* **Full Audit Logs:** Real-time logging of message edits, deletions, role updates, and voice movements.
* **Moderation Suite:** Standard `/ban`, `/kick`, and `/timeout` commands with permission-gate security.
* **Custom Branding:** Welcome and Leave messages featuring server statistics and user avatars.

## 🛠️ Command List

| Command | Description | Permissions |
| :--- | :--- | :--- |
| `/ticket-panel` | Deploy the interactive ticket creation system. | Administrator |
| `/application-panel` | Deploy the recruitment form. | Administrator |
| `/setup-voice` | Initialize the OneTap temporary voice system. | Administrator |
| `/ban` / `/kick` | High-level moderation with reason logging. | Administrator |
| `/timeout` | Temporarily mute members for a specific duration. | Administrator |
| `/clear` | Bulk delete messages (up to 100 at a time). | Manage Messages |
| `/move all` | Move everyone to your current voice channel. | Move Members |

## 🚀 Setup & Installation

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/yassirbili1/bot-discord.git](https://github.com/yassirbili1/bot-discord.git)
    cd bot-discord
    ```

2.  **Install Requirements:**
    ```bash
    pip install discord.py yt-dlp flask aiohttp pystyle python-dotenv
    ```

3.  **Configure Environment:**
    Create a file named `.env` in the main folder and add your token:
    ```env
    TOKEN=your_discord_bot_token_here
    ```

4.  **FFmpeg Requirement:**
    To use the music features, ensure [FFmpeg](https://ffmpeg.org/) is installed on your system and added to your PATH.

---

**Note:** Ensure the bot has `Members`, `Presence`, and `Message Content` intents enabled in the [Discord Developer Portal](https://discord.com/developers/applications).