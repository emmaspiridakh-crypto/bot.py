

# ============================================
# SECTION 1 — IMPORTS & FLASK KEEP_ALIVE
# ============================================

print(">>> BOT FILE LOADED <<<")

import os
import discord
import asyncio
import time
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread
import datetime

app = Flask('')

@app.route('/')
def home():
    return "OK"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ============================================
# SECTION 2 — BOT SETUP & INTENTS
# ============================================

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 1465344517090840639

# ============================================
# SECTION 3 — IDs (ALL TOGETHER)
# ============================================

# ROLE IDs
CEO_ID = 1486463380129841183
OWNER_ID = 1486463380725305407
DEVELOPER_ID = 1486463386039484578
STAFF_ID = 1486463383363518565
MANAGER_ID = 1486463405320704162

# AUTOROLE
AUTOROLE_ID = 1486463413461979258

# CATEGORY IDs
MAIN_TICKET_CATEGORY_ID = 1486471497731149994

# LOG CHANNELS
BOT_LOG_ID = 1486463491337621586
MESSAGE_EDIT_LOG_CHANNEL_ID = 1486463497247395940
MESSAGE_DELETE_LOG_CHANNEL_ID = 1486463497247395940
MEMBER_JOIN_LOG_CHANNEL_ID = 1486463497247395940
MEMBER_LEAVE_LOG_CHANNEL_ID = 1486463497247395940
ROLE_UPDATE_LOG_CHANNEL_ID = 1486463502540607508
VOICE_LOG_CHANNEL_ID = 1486463493971382282
CHANNEL_CREATE_LOG_CHANNEL_ID = 1486463505057185822
CHANNEL_DELETE_LOG_CHANNEL_ID = 1486463505057185822
ROLE_CREATE_LOG_CHANNEL_ID = 1486463502540607508
ROLE_DELETE_LOG_CHANNEL_ID = 1486463502540607508
TICKET_LOG_ID = 1486472009641885736

# ============================================
# SECTION 4 — HELPERS
# ============================================

def is_owner_or_ceo(user: discord.Member):
    return any(r.id in (OWNER_ID, CEO_ID) for r in user.roles)

# ============================================
# SECTION 7 — VOICE LOGS (JOIN / LEAVE / MOVE)
# ============================================

@bot.event
async def on_voice_state_update(member, before, after):
    guild = member.guild
    log = bot.get_channel(VOICE_LOG_CHANNEL_ID)

    # ----------------------------------------
    # EMBED VOICE LOGS (JOIN / LEAVE / MOVE)
    # ----------------------------------------

    if not log:
        return

    # JOIN
    if before.channel is None and after.channel is not None:
        embed = discord.Embed(
            title="🔊 Voice Join",
            description=f"**{member.mention}** joined **{after.channel.name}**",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.avatar)
        embed.set_footer(text=f"User ID: {member.id}")
        await log.send(embed=embed)

    # LEAVE
    elif before.channel is not None and after.channel is None:
        embed = discord.Embed(
            title="🔇 Voice Leave",
            description=f"**{member.mention}** left **{before.channel.name}**",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=member.avatar)
        embed.set_footer(text=f"User ID: {member.id}")
        await log.send(embed=embed)

    # MOVE
    elif before.channel != after.channel:
        embed = discord.Embed(
            title="🔁 Voice Move",
            description=f"**{member.mention}** moved from **{before.channel.name}** to **{after.channel.name}**",
            color=discord.Color.yellow()
        )
        embed.set_thumbnail(url=member.avatar)
        embed.set_footer(text=f"User ID: {member.id}")
        await log.send(embed=embed)

# ============================================
# SECTION 8 — ROLE LOGS (CREATE / DELETE / ADD / REMOVE)
# ============================================

@bot.event
async def on_guild_role_create(role):
    log = bot.get_channel(ROLE_CREATE_LOG_CHANNEL_ID)
    if log:
        embed = discord.Embed(
            title="🆕 Role Created",
            description=f"**{role.name}**",
            color=discord.Color.green()
        )
        embed.add_field(name="Moderator", value=f"{entry.user.mention}", inline=False)
        embed.set_footer(text=f"Role ID: {role.id}")
        await log.send(embed=embed)

@bot.event
async def on_guild_role_delete(role):
    log = bot.get_channel(ROLE_DELETE_LOG_CHANNEL_ID)
    if log:
        embed = discord.Embed(
            title="🗑️ Role Deleted",
            description=f"**{role.name}**",
            color=discord.Color.red()
        )
        embed.add_field(name="Moderator", value=f"{entry.user.mention}", inline=False)
        embed.set_footer(text=f"Role ID: {role.id}")
        await log.send(embed=embed)

@bot.event
async def on_member_update(before, after):
    guild = after.guild
    log = bot.get_channel(ROLE_UPDATE_LOG_CHANNEL_ID)

    # ROLE ADDED
    if len(after.roles) > len(before.roles):
        new_role = next(role for role in after.roles if role not in before.roles)

        async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.member_role_update):
            if entry.target.id == after.id:
                if log:
                    embed = discord.Embed(
                        title="➕ Role Added",
                        color=discord.Color.green()
                    )
                    embed.add_field(name="User", value=f"{after.mention}", inline=False)
                    embed.add_field(name="Role", value=f"**{new_role.name}**", inline=False)
                    embed.add_field(name="Moderator", value=f"{entry.user.mention}", inline=False)
                    embed.set_footer(text=f"User ID: {after.id} | Role ID: {new_role.id}")
                    await log.send(embed=embed)
                break

    # ROLE REMOVED
    elif len(after.roles) < len(before.roles):
        removed_role = next(role for role in before.roles if role not in after.roles)

        async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.member_role_update):
            if entry.target.id == after.id:
                if log:
                    embed = discord.Embed(
                        title="➖ Role Removed",
                        color=discord.Color.red()
                    )
                    embed.add_field(name="User", value=f"{after.mention}", inline=False)
                    embed.add_field(name="Role", value=f"**{removed_role.name}**", inline=False)
                    embed.add_field(name="Moderator", value=f"{entry.user.mention}", inline=False)
                    embed.set_footer(text=f"User ID: {after.id} | Role ID: {removed_role.id}")
                    await log.send(embed=embed)
                break

# ============================================
# SECTION 9 — CHANNEL LOGS (CREATE / DELETE)
# ============================================

@bot.event
async def on_guild_channel_create(channel):
    log = bot.get_channel(CHANNEL_CREATE_LOG_CHANNEL_ID)
    if log:
        await log.send(
            f"📁 Channel created: **{channel.name}** "
            f"(Type: {str(channel.type).title()})"
        )

@bot.event
async def on_guild_channel_delete(channel):
    log = bot.get_channel(CHANNEL_DELETE_LOG_CHANNEL_ID)
    if log:
        await log.send(
            f"🗑️ Channel deleted: **{channel.name}** "
            f"(Type: {str(channel.type).title()})"
        )

# ============================================
# SECTION 10 — MESSAGE LOGS (EDIT / DELETE)
# ============================================

@bot.event
async def on_message_edit(before, after):
    if before.author.bot:
        return
    if before.content == after.content:
        return

    log = bot.get_channel(MESSAGE_EDIT_LOG_CHANNEL_ID)
    if log:
        embed = discord.Embed(
            title="✏️ Message Edited",
            color=discord.Color.orange()
        )
        embed.add_field(name="User", value=f"{before.author} ({before.author.id})", inline=False)
        embed.add_field(name="Channel", value=before.channel.mention, inline=False)
        embed.add_field(name="Before", value=before.content or "None", inline=False)
        embed.add_field(name="After", value=after.content or "None", inline=False)
        await log.send(embed=embed)

@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return

    log = bot.get_channel(MESSAGE_DELETE_LOG_CHANNEL_ID)
    if log:
        embed = discord.Embed(
            title="🗑️ Message Deleted",
            color=discord.Color.red()
        )
        embed.add_field(name="User", value=f"{message.author}", inline=False)
        embed.add_field(name="Channel", value=message.channel.mention, inline=False)
        embed.add_field(name="Content", value=message.content or "None", inline=False)
        await log.send(embed=embed)

# ============================================
# SECTION 11 — TICKET SYSTEM
# ============================================

# -------------------------------
# CLOSE BUTTON VIEW
# -------------------------------

class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket_button")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        log_channel = guild.get_channel(TICKET_LOG_ID)

        # LOG CLOSE
        if log_channel:
            embed = discord.Embed(
                title="❌ Ticket Closed",
                description=f"Το ticket έκλεισε από {interaction.user.mention}",
                color=discord.Color.red()
            )
            embed.add_field(name="Channel", value=interaction.channel.mention, inline=False)
            await log_channel.send(embed=embed)

        await interaction.response.send_message(
            "Το ticket θα κλείσει σε 4 δευτερόλεπτα...", ephemeral=False
        )

        await asyncio.sleep(4)

        try:
            await interaction.channel.delete(reason=f"Ticket closed by {interaction.user}")
        except:
            pass

# -------------------------------
# MAIN TICKET SELECT (CALLBACK)
# -------------------------------

class MainTicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Owner", emoji="👑"),
            discord.SelectOption(label="Bug", emoji="🐞"),
            discord.SelectOption(label="Report", emoji="📙"),
            discord.SelectOption(label="Support", emoji="💬"),
        ]

        super().__init__(
            custom_id="main_ticket_select",
            placeholder="Διάλεξε κατηγορία ticket",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        author = interaction.user

        category = guild.get_channel(MAIN_TICKET_CATEGORY_ID)
        if not category:
            return await interaction.response.send_message("Η κατηγορία ticket δεν βρέθηκε.", ephemeral=True)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            author: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        }

        if self.values[0] == "Owner":
            roles_ids = [OWNER_ID, CEO_ID]
            name = f"owner-{author.name}".replace(" ", "-").lower()
            ticket_type = "Owner Ticket"

        elif self.values[0] == "Bug":
            roles_ids = [DEVELOPER_ID, OWNER_ID, CEO_ID]
            name = f"bug-{author.name}".replace(" ", "-").lower()
            ticket_type = "Bug Report"

        elif self.values[0] == "Report":
            roles_ids = [MANAGER_ID, OWNER_ID, CEO_ID]
            name = f"report-{author.name}".replace(" ", "-").lower()
            ticket_type = "Report"

        else:
            roles_ids = [STAFF_ID, OWNER_ID, CEO_ID]
            name = f"support-{author.name}".replace(" ", "-").lower()
            ticket_type = "Support"

        for rid in roles_ids:
            role = guild.get_role(rid)
            if role:
                overwrites[role] = discord.PermissionOverwrite(
                    view_channel=True, send_messages=True, read_message_history=True
                )

        channel = await guild.create_text_channel(
            name=name,
            category=category,
            overwrites=overwrites,
            reason=f"Ticket created by {author} ({ticket_type})"
        )

        embed = discord.Embed(
            title=f"🎫 Ticket από {author.name}",
            description=f"{author.mention} άνοιξε **{ticket_type}**.\n"
                        f"Παρακαλώ περιμένετε θα σας εξυπηρετήσουμε σύντομα.",
            color=discord.Color.from_rgb(120, 120, 120)
        )

        await channel.send(embed=embed, view=TicketCloseView())

        # LOGGING
        log_channel = guild.get_channel(TICKET_LOG_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="📂 Νέο Ticket",
                description=f"Ο χρήστης {author.mention} άνοιξε ticket.",
                color=discord.Color.blue()
            )
            log_embed.add_field(name="Τύπος", value=ticket_type)
            log_embed.add_field(name="Channel", value=channel.mention)

            await log_channel.send(embed=log_embed)

        await interaction.response.send_message(
            f"Το ticket σου δημιουργήθηκε: {channel.mention}",
            ephemeral=True
        )


# -------------------------------
# DARK NEON MAIN TICKET PANEL
# -------------------------------

class MainTicketPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        embed = discord.Embed(
            title="Crown Studio — Support Panel",
            description=(
                "**Επίλεξε την κατηγορία που ταιριάζει στο αίτημά σου.**\n"
                "Το προσωπικό θα σε εξυπηρετήσει άμεσα."
            ),
            color=discord.Color.from_rgb(20, 20, 25)
        )

        embed.set_image(url="https://i.imgur.com/lLoG1Gz.jpeg")
        embed.timestamp = discord.utils.utcnow()

        self.embed = embed
        self.add_item(MainTicketSelect())

    async def send_panel(self, interaction_or_channel):
        if isinstance(interaction_or_channel, discord.Interaction):
            await interaction_or_channel.response.send_message(embed=self.embed, view=self)
        else:
            await interaction_or_channel.send(embed=self.embed, view=self)
# ============================================
# SECTION 12 — MODERATION COMMANDS
# ============================================

def has_staff_permissions(member: discord.Member):
    """Checks if user has moderation permissions."""
    return (
        member.guild_permissions.kick_members or
        member.guild_permissions.ban_members or
        any(r.id in (STAFF_ID, MANAGER_ID, OWNER_ID, CEO_ID) for r in member.roles)
    )

@bot.command()
async def ban(ctx, member: discord.Member = None, *, reason="No reason provided"):
    if not has_staff_permissions(ctx.author):
        return await ctx.reply("❌ Δεν έχεις δικαίωμα να κάνεις ban.")

    if not member:
        return await ctx.reply("Πρέπει να γράψεις ποιον θέλεις να κάνεις ban.")

    await member.ban(reason=reason)
    await ctx.reply(f"🔨 Ο χρήστης **{member}** έγινε ban.")

    log = bot.get_channel(BOT_LOG_ID)
    if log:
        await log.send(f"🔨 **{ctx.author}** banned **{member}** — Reason: {reason}")

@bot.command()
async def kick(ctx, member: discord.Member = None, *, reason="No reason provided"):
    if not has_staff_permissions(ctx.author):
        return await ctx.reply("❌ Δεν έχεις δικαίωμα να κάνεις kick.")

    if not member:
        return await ctx.reply("Πρέπει να γράψεις ποιον θέλεις να κάνεις kick.")

    await member.kick(reason=reason)
    await ctx.reply(f"👢 Ο χρήστης **{member}** έγινε kick.")

    log = bot.get_channel(BOT_LOG_ID)
    if log:
        await log.send(f"👢 **{ctx.author}** kicked **{member}** — Reason: {reason}")

@bot.command()
async def timeout(ctx, member: discord.Member = None, minutes: int = None, *, reason="No reason provided"):
    if not has_staff_permissions(ctx.author):
        return await ctx.reply("❌ Δεν έχεις δικαίωμα να κάνεις timeout.")

    if not member or not minutes:
        return await ctx.reply("Χρήση: `!timeout @user <minutes> <reason>`")

    duration = datetime.timedelta(minutes=minutes)
    await member.timeout(duration, reason=reason)

    await ctx.reply(f"⏳ Ο χρήστης **{member}** μπήκε timeout για {minutes} λεπτά.")

    log = bot.get_channel(BOT_LOG_ID)
    if log:
        await log.send(
            f"⏳ **{ctx.author}** timed out **{member}** for **{minutes} minutes** — Reason: {reason}"
        )

@bot.command()
async def clearmessage(ctx, amount: int = None):
    if not has_staff_permissions(ctx.author):
        return await ctx.reply("❌ Δεν έχεις δικαίωμα να κάνεις clear.")

    if not amount:
        return await ctx.reply("Χρήση: `!clearmessage <amount>`")

    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Διαγράφηκαν **{amount}** μηνύματα.", delete_after=3)

    log = bot.get_channel(BOT_LOG_ID)
    if log:
        await log.send(f"🧹 **{ctx.author}** cleared **{amount}** messages in {ctx.channel.mention}")

# ============================================
# SECTION 13 — UTILITY COMMANDS
# ============================================

@bot.command()
async def say(ctx, *, message: str):
    if not is_owner(ctx.author):
        return await ctx.reply("❌ Δεν έχεις δικαίωμα να χρησιμοποιήσεις αυτή την εντολή.")
    await ctx.send(message)

@bot.command()
async def dmall(ctx, *, message: str):
    # CEO ONLY
    ceo_role = ctx.guild.get_role(CEO_ID)

    if ceo_role not in ctx.author.roles:
        return await ctx.reply("❌ Μόνο ο CEO μπορεί να χρησιμοποιήσει αυτή την εντολή.")

    sent = 0
    for member in ctx.guild.members:
        if member.bot:
            continue
        try:
            await member.send(message)
            sent += 1
        except:
            continue

    await ctx.reply(f"📨 Το μήνυμα στάλθηκε σε **{sent}** μέλη.")


@bot.command()
async def panel(ctx):
    if not is_owner_or_ceo(ctx.author):
        return await ctx.reply("❌ Δεν έχεις δικαίωμα να χρησιμοποιήσεις αυτή την εντολή.")

    embed = discord.Embed(
        title="📌 Crown Studio — Command Panel",
        description="Όλες οι βασικές εντολές του bot.",
        color=discord.Color.dark_gray()
    )

    embed.add_field(
        name="🛠 Moderation",
        value="`!ban`, `!kick`, `!timeout`, `!clearmessage`",
        inline=False
    )

    embed.add_field(
        name="🧰 Utility (Only for: CEO/OWNER)",
        value="`!say`, `!dmall`",
        inline=False
    )

    await ctx.reply(embed=embed)

# ============================================
# SECTION 14 — AUTOROLE (ON MEMBER JOIN)
# ============================================

@bot.event
async def on_member_join(member):
    # --- AUTOROLE ---
    role = member.guild.get_role(AUTOROLE_ID)
    if role:
        try:
            await member.add_roles(role)
        except:
            pass

    # --- JOIN LOG (EMBED) ---
    log = bot.get_channel(MEMBER_JOIN_LOG_CHANNEL_ID)
    if log:
        embed = discord.Embed(
            title="🟢 Member Joined",
            description=f"{member.mention}",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.avatar)
        embed.set_footer(text=f"User ID: {member.id}")
        await log.send(embed=embed)

    # Update counters
    await update_voice_channels(member.guild)


@bot.event
async def on_member_remove(member):
    # --- LEAVE LOG (EMBED) ---
    log = bot.get_channel(MEMBER_LEAVE_LOG_CHANNEL_ID)
    if log:
        embed = discord.Embed(
            title="🔴 Member Left",
            description=f"{member.mention}",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=member.avatar)
        embed.set_footer(text=f"User ID: {member.id}")
        await log.send(embed=embed)

    # Update counters
    await update_voice_channels(member.guild)

# ============================================
# SECTION 15 — ON_READY
# ============================================

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    # Persistent views
    bot.add_view(MainTicketPanel())
    bot.add_view(TicketCloseView())

    guild = bot.get_guild(GUILD_ID)
    if guild:
        await update_voice_channels(guild)

    await bot.change_presence(
        activity=discord.Game(name="Crown Studio")
    )

    print("Bot is fully online and ready.")

# ============================================
# SECTION 16 — PANEL COMMANDS
# ============================================

@bot.command()
async def ticketpanel(ctx):
    if not is_owner_or_ceo(ctx.author):
        return await ctx.reply("Δεν έχεις δικαίωμα να στείλεις το panel.")

    embed = discord.Embed(
            title="Crown Studio — Support Panel",
            description=(
                "**Επίλεξε την κατηγορία που ταιριάζει στο αίτημά σου.**\n"
                "Το προσωπικό θα σε εξυπηρετήσει άμεσα."
            ),
            color=discord.Color.from_rgb(20, 20, 25)  # dark neon base
        )

    embed.set_image(url="https://i.imgur.com/lLoG1Gz.jpeg")
    embed.set_footer(text="Crown Studio • Support System")

    await ctx.send(embed=embed, view=MainTicketPanel())
    await ctx.reply("Το νέο ticket panel στάλθηκε.", delete_after=2)


# ============================================
# SECTION 17 — START BOT
# ============================================

if __name__ == "__main__":
    keep_alive()
    bot.run(TOKEN)








