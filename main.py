# Import necessary libraries
import discord
import random
from discord import activity
import itertools
from discord.ext import commands
from discord.ext import tasks
from discord import app_commands, ui
from typing import Optional
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import datetime
from collections import defaultdict
import re
import json
import os
from dotenv import load_dotenv
import aiohttp
import asyncio
from functools import partial
import aiomysql
import webserver

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = 1247440062870851625

async def get_db_conn():
    return await aiomysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        db=os.getenv('DB_NAME'),
        autocommit=True
    )

async def add_warning_db(user_id, guild_id, moderator, reason):
    conn = await get_db_conn()
    async with conn.cursor() as cur:
        # Insert the new warning
        await cur.execute(
            "INSERT INTO user_warnings (user_id, guild_id, moderator, reason, date) VALUES (%s, %s, %s, %s, %s)",
            (user_id, guild_id, moderator, reason, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        # Get the new total count
        await cur.execute("SELECT COUNT(*) FROM user_warnings WHERE user_id=%s AND guild_id=%s", (user_id, guild_id))
        result = await cur.fetchone()
    conn.close()
    return result[0]

class Client(commands.Bot):
    def __init__(self):
        # We need message_content intent for your !hello command to work
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True # Useful for many bots
        
        super().__init__(
            command_prefix='!', 
            intents=intents
        )

    async def setup_hook(self):
        cogs = ["fun", "automod", "utils", "info"]
        for cog in cogs:
            try:
                await self.load_extension(f'cogs.{cog}')
                print(f'{cog} cog loaded.')
            except Exception as e:
                print(f'Failed to load {cog} cog: {e}')

    async def on_ready(self):
        guild = discord.Object(id=GUILD_ID)
        
        client.remove_command("help")
        self.change_status.start()
        print(f"Logged in as {self.user}!")
        print("Bot is online and ready to use.")
        self.tree.copy_global_to(guild=guild)
        synced = await self.tree.sync(guild=guild)
        print(f"--- Synced {len(synced)} commands to guild {GUILD_ID} ---")

    async def on_message(self, message):
        # Prevent the bot from replying to itself
        if message.author == self.user:
            return
            
        # Hardcoded check for !hello (outside of cogs)
        if message.content.startswith('!hello'):
            await message.channel.send('Hello!')

        # IMPORTANT: This line allows Cog commands to process
        await self.process_commands(message)
    
    def __init__(self, *args, **kwargs):
        # 1. Initialize the parent discord.Client class
        super().__init__(*args, **kwargs)
        
        # 2. Define the status_index attribute HERE
        self.status_index = itertools.cycle([0, 1, 2, 3])

    @tasks.loop(seconds=10)
    async def change_status(self):
        guild = self.get_guild(GUILD_ID)
        members = guild.member_count if guild else "many"

        statuses = [
            f"Watching {members} members",
            "Watching Shiku Gamer's content",
            "Helping with /help",
            "Listening to the community"
        ]

        # Now 'self.status_index' will exist because it was made in __init__
        current_index = next(self.status_index)
        new_status_text = statuses[current_index]

        await self.change_presence(activity=discord.CustomActivity(name=new_status_text))

    @change_status.before_loop
    async def before_change_status(self):
        await self.wait_until_ready()
    
# Set up the bot with the specified command prefix and intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = Client(command_prefix='!', help_command=None, intents=intents)

guild_id = discord.Object(id=1247440062870851625)
member_logs = 1393183220400656446
server_logs = 1393183313883037696
voice_chat_logs = 1393183390576152606
message_logs = 1393183478257942558
join_leave_logs = 1393183604170821722
reaction_logs = 1474945032401326264
owner_id = 929610842142539846

def creating_welcome_image(member):
    canvas_width = 800
    canvas_height = 250
    pfp_size = 170
    
    # Create black canvas
    canvas = Image.new("RGB", (canvas_width, canvas_height), (0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    
    # Try to load font, fallback to default if file not found
    try:
        username_font = ImageFont.truetype("arial.ttf", 30)
        rank_font = ImageFont.truetype("arial.ttf", 22)
    except:
        username_font = ImageFont.load_default()
        rank_font = ImageFont.load_default()
    
    # Get Avatar
    avatar_url = member.display_avatar.url
    response = requests.get(avatar_url)
    pfp = Image.open(BytesIO(response.content)).convert("RGBA")
    pfp = pfp.resize((pfp_size, pfp_size))
    
    # Create Circle Mask
    mask = Image.new("L", (pfp_size, pfp_size), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, pfp_size, pfp_size), fill=255)
    
    # Paste Avatar
    pfp_x = 50
    pfp_y = (canvas_height - pfp_size) // 2
    canvas.paste(pfp, (pfp_x, pfp_y), mask)
    
    # Draw Text
    text_x = pfp_x + pfp_size + 30
    draw.text((text_x, 80), f"Welcome {member.name}!", font=username_font, fill=(255, 255, 255))
    draw.text((text_x, 130), f"You are member #{member.guild.member_count}.", font=rank_font, fill=(177, 177, 177))
    
    return canvas

@client.event
async def on_member_join(member):
    channel_id = 1332304420775399476
    channel = client.get_channel(channel_id)
    
    if channel is None:
        print(f"Error: Could not find channel with ID {channel_id}")
        return

    # Generate the image
    try:
        canvas = creating_welcome_image(member)
        
        # Save to buffer
        buffer = BytesIO()
        canvas.save(buffer, format="PNG")
        buffer.seek(0)
        
        # Prepare the file
        file = discord.File(buffer, filename="welcome.png")
        
        # Build Embed
        embed = discord.Embed(
            title="Welcome!", 
            description=f"Welcome to **The Shiku Gamer**, {member.mention}! We hope you'll have a great time hanging out with our members, Shiku and staffs!\n\n"
                        "⁠・🗨️︰main-chat\n"
                        "⁠・📳︰notify\n"
                        "⁠・📢︰announcements\n"
                        "⁠・🔔︰updates", 
            color=0x00ff00
        )
        
        # This MUST match the filename in discord.File
        embed.set_image(url="attachment://welcome.png")
        
        # Send both together
        await channel.send(embed=embed, file=file)
        
    except Exception as e:
        print(f"An error occurred: {e}")

# Error handling for command errors
@client.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
    elif isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message("You don't meet the requirements to use this command.", ephemeral=True)
    else:
        await interaction.response.send_message(f"An error occurred: {error}", ephemeral=True)
        
# Global error handler
@client.event
async def on_error(event_method, /, *args, **kwargs):
    print(f"An error occurred in {event_method}:")
    import traceback
    traceback.print_exc()
    
# Mod Logging
@client.event
async def on_member_ban(guild, user):
    channel_id = member_logs
    channel = client.get_channel(channel_id)
    embed = discord.Embed(title="Member Banned", color=discord.Color.red())
    embed.add_field(name="User", value=user.mention, inline=True)
    embed.add_field(name="User ID", value=user.id, inline=True)
    await channel.send(embed=embed)

@client.event   
async def on_member_unban(guild, user):
    channel_id = member_logs
    channel = client.get_channel(channel_id)
    embed = discord.Embed(title="Member Unbanned", color=discord.Color.green())
    embed.add_field(name="User", value=user.mention, inline=True)
    embed.add_field(name="User ID", value=user.id, inline=True)
    await channel.send(embed=embed)

@client.event
async def on_member_update(before, after):
    channel_id = member_logs
    channel = client.get_channel(channel_id)
    
    if before.roles != after.roles:
        added_roles = [role for role in after.roles if role not in before.roles]
        removed_roles = [role for role in before.roles if role not in after.roles]
        
        if added_roles:
            embed = discord.Embed(title="Role Added", color=discord.Color.green())
            embed.add_field(name="User", value=after.mention, inline=True)
            embed.add_field(name="Roles Added", value=', '.join(role.mention for role in added_roles), inline=False)
            await channel.send(embed=embed)
        if removed_roles:
            embed = discord.Embed(title="Role Removed", color=discord.Color.red())
            embed.add_field(name="User", value=after.mention, inline=True)
            embed.add_field(name="Roles Removed", value=', '.join(role.mention for role in removed_roles), inline=False)
            await channel.send(embed=embed)

@client.event            
async def on_member_remove(member):
    channel_id = member_logs
    channel = client.get_channel(channel_id)
    embed = discord.Embed(title="Member Left", color=discord.Color.orange())
    embed.add_field(name="User", value=member.mention, inline=True)
    embed.add_field(name="User ID", value=member.id, inline=True)
    await channel.send(embed=embed)

@client.event
async def on_member_join(member):
    channel_id = member_logs
    channel = client.get_channel(channel_id)
    embed = discord.Embed(title="Member Joined", color=discord.Color.green())
    embed.add_field(name="User", value=member.mention, inline=True)
    embed.add_field(name="User ID", value=member.id, inline=True)
    await channel.send(embed=embed)

@client.event
async def on_message_delete(message):
    # 1. Ignore bots
    if message.author.bot:
        return

    channel = client.get_channel(message_logs)
    if not channel:
        return

    embed = discord.Embed(
        title="Message Deleted", 
        color=discord.Color.red(),
        timestamp=discord.utils.utcnow()
    )
    embed.add_field(name="User", value=message.author.mention, inline=True)
    embed.add_field(name="Channel", value=message.channel.mention, inline=True)

    # 2. Handle Text Content
    content = message.content if message.content else "[No text content]"
    embed.add_field(name="Content", value=content[:1024], inline=False)

    # 3. Handle Attachments (Images, Files, etc.)
    if message.attachments:
        attachment_list = []
        for file in message.attachments:
            attachment_list.append(f"📄 {file.filename}")
        
        embed.add_field(
            name="Attachments", 
            value="\n".join(attachment_list), 
            inline=False
        )
        
        # If the attachment was an image, try to show the thumbnail
        # Note: This only works if Discord hasn't purged the cache yet
        if message.attachments[0].proxy_url:
            embed.set_thumbnail(url=message.attachments[0].proxy_url)

    await channel.send(embed=embed)

@client.event
async def on_message_edit(before, after):
    if before.author.bot:
        return

    if before.content == after.content:
        return

    channel = client.get_channel(message_logs)
    if not channel:
        return

    embed = discord.Embed(title="Message Edited", color=discord.Color.blue())
    embed.add_field(name="User", value=before.author.mention, inline=True)
    
    before_text = before.content if before.content else "[No text content]"
    after_text = after.content if after.content else "[No text content]"

    embed.add_field(name="Before", value=before_text[:1024], inline=False)
    embed.add_field(name="After", value=after_text[:1024], inline=False)
    
    await channel.send(embed=embed)

@client.event
async def on_voice_state_update(member, before, after):
    channel_id = voice_chat_logs
    channel = client.get_channel(channel_id)
    
    if before.channel is None and after.channel is not None:
        embed = discord.Embed(title="Voice Channel Joined", color=discord.Color.green())
        embed.add_field(name="User", value=member.mention, inline=True)
        embed.add_field(name="Channel", value=after.channel.name, inline=True)
        await channel.send(embed=embed)
    elif before.channel is not None and after.channel is None:
        embed = discord.Embed(title="Voice Channel Left", color=discord.Color.red())
        embed.add_field(name="User", value=member.mention, inline=True)
        embed.add_field(name="Channel", value=before.channel.name, inline=True)
        await channel.send(embed=embed)
    elif before.channel != after.channel:
        embed = discord.Embed(title="Voice Channel Switched", color=discord.Color.orange())
        embed.add_field(name="User", value=member.mention, inline=True)
        embed.add_field(name="From", value=before.channel.name, inline=True)
        embed.add_field(name="To", value=after.channel.name, inline=True)
        await channel.send(embed=embed)

@client.event 
async def on_guild_update(before, after):
    channel_id = server_logs
    channel = client.get_channel(channel_id)
    
    if before.name != after.name:
        embed = discord.Embed(title="Server Name Changed", color=discord.Color.blue())
        embed.add_field(name="Before", value=before.name, inline=True)
        embed.add_field(name="After", value=after.name, inline=True)
        await channel.send(embed=embed)
        
    if before.icon != after.icon:
        embed = discord.Embed(title="Server Icon Changed", color=discord.Color.blue())
        embed.set_thumbnail(url=after.icon.url if after.icon else None)
        await channel.send(embed=embed)

@client.event
async def on_guild_channel_create(channel):
    channel_id = server_logs
    log_channel = client.get_channel(channel_id)
    embed = discord.Embed(title="Channel Created", color=discord.Color.green())
    embed.add_field(name="Channel Name", value=channel.name, inline=True)
    embed.add_field(name="Channel Type", value=str(channel.type).split('.')[-1], inline=True)
    await log_channel.send(embed=embed)

@client.event
async def on_guild_channel_delete(channel):
    channel_id = server_logs
    log_channel = client.get_channel(channel_id)
    embed = discord.Embed(title="Channel Deleted", color=discord.Color.red())
    embed.add_field(name="Channel Name", value=channel.name, inline=True)
    embed.add_field(name="Channel Type", value=str(channel.type).split('.')[-1], inline=True)
    await log_channel.send(embed=embed)

@client.event
async def on_guild_channel_update(before, after):
    channel_id = server_logs
    log_channel = client.get_channel(channel_id)
    if not log_channel:
        return

    if before.name != after.name:
        embed = discord.Embed(title="Channel Name Changed", color=discord.Color.blue())
        embed.add_field(name="Before", value=before.name, inline=True)
        embed.add_field(name="After", value=after.name, inline=True)
        await log_channel.send(embed=embed)

    if isinstance(before, discord.TextChannel):
        if before.topic != after.topic:
            embed = discord.Embed(title="Channel Topic Changed", color=discord.Color.blue())
            embed.add_field(name="Channel", value=before.name, inline=True)
            embed.add_field(name="Before", value=before.topic or "None", inline=False)
            embed.add_field(name="After", value=after.topic or "None", inline=False)
            await log_channel.send(embed=embed)

@client.event
async def on_guild_role_create(role):
    channel_id = server_logs
    log_channel = client.get_channel(channel_id)
    embed = discord.Embed(title="Role Created", color=discord.Color.green())
    embed.add_field(name="Role Name", value=role.name, inline=True)
    embed.add_field(name="Role Color", value=str(role.color), inline=True)
    await log_channel.send(embed=embed)

@client.event
async def on_guild_role_delete(role):
    channel_id = server_logs
    log_channel = client.get_channel(channel_id)
    embed = discord.Embed(title="Role Deleted", color=discord.Color.red())
    embed.add_field(name="Role Name", value=role.name, inline=True)
    embed.add_field(name="Role Color", value=str(role.color), inline=True)
    await log_channel.send(embed=embed)

@client.event    
async def on_guild_role_update(before, after):
    channel_id = server_logs
    log_channel = client.get_channel(channel_id)
    
    if before.name != after.name:
        embed = discord.Embed(title="Role Name Changed", color=discord.Color.blue())
        embed.add_field(name="Before", value=before.name, inline=True)
        embed.add_field(name="After", value=after.name, inline=True)
        await log_channel.send(embed=embed)
        
    if before.color != after.color:
        embed = discord.Embed(title="Role Color Changed", color=discord.Color.blue())
        embed.add_field(name="Role", value=before.name, inline=True)
        embed.add_field(name="Before", value=str(before.color), inline=True)
        embed.add_field(name="After", value=str(after.color), inline=True)
        await log_channel.send(embed=embed)

@client.event        
async def on_guild_update(before, after):
    channel_id = server_logs
    log_channel = client.get_channel(channel_id)
    
    if before.name != after.name:
        embed = discord.Embed(title="Server Name Changed", color=discord.Color.blue())
        embed.add_field(name="Before", value=before.name, inline=True)
        embed.add_field(name="After", value=after.name, inline=True)
        await log_channel.send(embed=embed)
        
    if before.icon != after.icon:
        embed = discord.Embed(title="Server Icon Changed", color=discord.Color.blue())
        embed.set_thumbnail(url=after.icon.url if after.icon else None)
        await log_channel.send(embed=embed)

@client.event        
async def on_guild_channel_pins_update(channel, last_pin):
    channel_id = message_logs
    log_channel = client.get_channel(channel_id)
    embed = discord.Embed(title="Channel Pins Updated", color=discord.Color.blue())
    embed.add_field(name="Channel", value=channel.mention, inline=True)
    embed.add_field(name="Last Pin Time", value=last_pin.strftime("%b %d, %Y at %H:%M:%S"), inline=True)
    await log_channel.send(embed=embed)
    
@client.event
async def on_guild_emojis_update(guild, before, after):
    channel_id = server_logs
    log_channel = client.get_channel(channel_id)
    
    if before != after:
        embed = discord.Embed(title="Server Emojis Updated", color=discord.Color.blue())
        embed.add_field(name="Before", value=f"{len(before)} emojis", inline=True)
        embed.add_field(name="After", value=f"{len(after)} emojis", inline=True)
        await log_channel.send(embed=embed)

@client.event
async def on_guild_stickers_update(guild, before, after):
    channel_id = server_logs
    log_channel = client.get_channel(channel_id)
    
    if before != after:
        embed = discord.Embed(title="Server Stickers Updated", color=discord.Color.blue())
        embed.add_field(name="Before", value=f"{len(before)} stickers", inline=True)
        embed.add_field(name="After", value=f"{len(after)} stickers", inline=True)
        await log_channel.send(embed=embed)

@client.event
async def on_guild_integrations_update(guild):
    channel_id = server_logs
    log_channel = client.get_channel(channel_id)
    embed = discord.Embed(title="Server Integrations Updated", color=discord.Color.blue())
    await log_channel.send(embed=embed)
    
@client.event
async def on_guild_webhooks_update(guild):
    channel_id = server_logs
    log_channel = client.get_channel(channel_id)
    embed = discord.Embed(title="Server Webhooks Updated", color=discord.Color.blue())
    await log_channel.send(embed=embed)
    
@client.event
async def on_guild_audit_log_entry_create(entry):
    channel_id = server_logs
    log_channel = client.get_channel(channel_id)
    embed = discord.Embed(title="Audit Log Entry Created", color=discord.Color.blue())
    embed.add_field(name="Action", value=str(entry.action), inline=True)
    embed.add_field(name="User", value=entry.user.mention if entry.user else "Unknown", inline=True)
    embed.add_field(name="Target", value=str(entry.target) if entry.target else "Unknown", inline=True)
    await log_channel.send(embed=embed)
    
@client.event
async def on_guild_scheduled_event_create(event):
    channel_id = server_logs
    log_channel = client.get_channel(channel_id)
    embed = discord.Embed(title="Scheduled Event Created", color=discord.Color.green())
    embed.add_field(name="Event Name", value=event.name, inline=True)
    embed.add_field(name="Start Time", value=event.start_time.strftime("%b %d, %Y at %H:%M:%S"), inline=True)
    await log_channel.send(embed=embed)
    
@client.event
async def on_guild_scheduled_event_delete(event):
    channel_id = server_logs
    log_channel = client.get_channel(channel_id)
    embed = discord.Embed(title="Scheduled Event Deleted", color=discord.Color.red())
    embed.add_field(name="Event Name", value=event.name, inline=True)
    await log_channel.send(embed=embed)
    
@client.event
async def on_guild_scheduled_event_update(before, after):
    channel_id = server_logs
    log_channel = client.get_channel(channel_id)
    
    if before.name != after.name:
        embed = discord.Embed(title="Scheduled Event Updated", color=discord.Color.blue())
        embed.add_field(name="Before", value=before.name, inline=True)
        embed.add_field(name="After", value=after.name, inline=True)
        await log_channel.send(embed=embed)
        
@client.event
async def on_guild_scheduled_event_user_add(event, user):
    channel_id = server_logs
    log_channel = client.get_channel(channel_id)
    embed = discord.Embed(title="User Added to Scheduled Event", color=discord.Color.green())
    embed.add_field(name="Event Name", value=event.name, inline=True)
    embed.add_field(name="User", value=user.mention, inline=True)
    await log_channel.send(embed=embed)
    
@client.event
async def on_guild_scheduled_event_user_remove(event, user):
    channel_id = server_logs
    log_channel = client.get_channel(channel_id)
    embed = discord.Embed(title="User Removed from Scheduled Event", color=discord.Color.red())
    embed.add_field(name="Event Name", value=event.name, inline=True)
    embed.add_field(name="User", value=user.mention, inline=True)
    await log_channel.send(embed=embed)
    
@client.event
async def on_guild_scheduled_event_user_update(event, user):
    channel_id = server_logs
    log_channel = client.get_channel(channel_id)
    embed = discord.Embed(title="User Updated in Scheduled Event", color=discord.Color.blue())
    embed.add_field(name="Event Name", value=event.name, inline=True)
    embed.add_field(name="User", value=user.mention, inline=True)
    await log_channel.send(embed=embed)
    
@client.event
async def on_guild_scheduled_event_participants_update(event):
    channel_id = server_logs
    log_channel = client.get_channel(channel_id)
    embed = discord.Embed(title="Scheduled Event Participants Updated", color=discord.Color.blue())
    embed.add_field(name="Event Name", value=event.name, inline=True)
    embed.add_field(name="Total Participants", value=event.user_count, inline=True)
    await log_channel.send(embed=embed)
    
@client.event
async def on_guild_scheduled_event_status_update(event, old_status):
    channel_id = server_logs
    log_channel = client.get_channel(channel_id)
    embed = discord.Embed(title="Scheduled Event Status Updated", color=discord.Color.blue())
    embed.add_field(name="Event Name", value=event.name, inline=True)
    embed.add_field(name="Old Status", value=str(old_status), inline=True)
    embed.add_field(name="New Status", value=str(event.status), inline=True)
    await log_channel.send(embed=embed)
    
@client.event
async def on_guild_scheduled_event_location_update(event, old_location):
    channel_id = server_logs
    log_channel = client.get_channel(channel_id)
    embed = discord.Embed(title="Scheduled Event Location Updated", color=discord.Color.blue())
    embed.add_field(name="Event Name", value=event.name, inline=True)
    embed.add_field(name="Old Location", value=old_location or "None", inline=True)
    embed.add_field(name="New Location", value=event.location or "None", inline=True)
    await log_channel.send(embed=embed)
    
@client.event
async def on_guild_scheduled_event_description_update(event, old_description):
    channel_id = server_logs
    log_channel = client.get_channel(channel_id)
    embed = discord.Embed(title="Scheduled Event Description Updated", color=discord.Color.blue())
    embed.add_field(name="Event Name", value=event.name, inline=True)
    embed.add_field(name="Old Description", value=old_description or "None", inline=False)
    embed.add_field(name="New Description", value=event.description or "None", inline=False)
    await log_channel.send(embed=embed)
    
@client.event
async def on_guild_scheduled_event_image_update(event, old_image):
    channel_id = server_logs
    log_channel = client.get_channel(channel_id)
    embed = discord.Embed(title="Scheduled Event Image Updated", color=discord.Color.blue())
    embed.add_field(name="Event Name", value=event.name, inline=True)
    if event.image:
        embed.set_thumbnail(url=event.image.url)
    await log_channel.send(embed=embed)
    
@client.event
async def on_guild_scheduled_event_entity_metadata_update(event, old_metadata):
    channel_id = server_logs
    log_channel = client.get_channel(channel_id)
    embed = discord.Embed(title="Scheduled Event Metadata Updated", color=discord.Color.blue())
    embed.add_field(name="Event Name", value=event.name, inline=True)
    await log_channel.send(embed=embed)
    
@client.event
async def on_guild_scheduled_event_entity_type_update(event, old_entity_type):
    channel_id = server_logs
    log_channel = client.get_channel(channel_id)
    embed = discord.Embed(title="Scheduled Event Entity Type Updated", color=discord.Color.blue())
    embed.add_field(name="Event Name", value=event.name, inline=True)
    embed.add_field(name="Old Entity Type", value=str(old_entity_type), inline=True)
    embed.add_field(name="New Entity Type", value=str(event.entity_type), inline=True)
    await log_channel.send(embed=embed)
    
@client.event
async def on_guild_scheduled_event_privacy_level_update(event, old_privacy_level):
    channel_id = server_logs
    log_channel = client.get_channel(channel_id)
    embed = discord.Embed(title="Scheduled Event Privacy Level Updated", color=discord.Color.blue())
    embed.add_field(name="Event Name", value=event.name, inline=True)
    embed.add_field(name="Old Privacy Level", value=str(old_privacy_level), inline=True)
    embed.add_field(name="New Privacy Level", value=str(event.privacy_level), inline=True)
    await log_channel.send(embed=embed)
    
@client.event
async def on_guild_scheduled_event_status_update(event, old_status):
    channel_id = server_logs
    log_channel = client.get_channel(channel_id)
    embed = discord.Embed(title="Scheduled Event Status Updated", color=discord.Color.blue())
    embed.add_field(name="Event Name", value=event.name, inline=True)
    embed.add_field(name="Old Status", value=str(old_status), inline=True)
    embed.add_field(name="New Status", value=str(event.status), inline=True)
    await log_channel.send(embed=embed)
    
@client.event
async def on_reaction_add(reaction, user):
    channel_id = reaction_logs
    log_channel = client.get_channel(channel_id)
    embed = discord.Embed(title="Reaction Added", color=discord.Color.green())
    embed.add_field(name="User", value=user.mention, inline=True)
    embed.add_field(name="Channel", value=reaction.message.channel.mention, inline=True)
    embed.add_field(name="Message ID", value=reaction.message.id, inline=True)
    embed.add_field(name="Emoji", value=str(reaction.emoji), inline=True)
    await log_channel.send(embed=embed)
    
@client.event
async def on_reaction_remove(reaction, user):
    channel_id = reaction_logs
    log_channel = client.get_channel(channel_id)
    embed = discord.Embed(title="Reaction Removed", color=discord.Color.red())
    embed.add_field(name="User", value=user.mention, inline=True)
    embed.add_field(name="Channel", value=reaction.message.channel.mention, inline=True)
    embed.add_field(name="Message ID", value=reaction.message.id, inline=True)
    embed.add_field(name="Emoji", value=str(reaction.emoji), inline=True)
    await log_channel.send(embed=embed)
    
@client.event
async def on_reaction_clear(message, reactions):
    channel_id = reaction_logs
    log_channel = client.get_channel(channel_id)
    embed = discord.Embed(title="Reactions Cleared", color=discord.Color.orange())
    embed.add_field(name="Channel", value=message.channel.mention, inline=True)
    embed.add_field(name="Message ID", value=message.id, inline=True)
    embed.add_field(name="Total Reactions Cleared", value=str(len(reactions)), inline=True)
    await log_channel.send(embed=embed)
    
@client.event
async def on_reaction_clear_emoji(message, emoji):
    channel_id = reaction_logs
    log_channel = client.get_channel(channel_id)
    embed = discord.Embed(title="Reactions Cleared for Emoji", color=discord.Color.orange())
    embed.add_field(name="Channel", value=message.channel.mention, inline=True)
    embed.add_field(name="Message ID", value=message.id, inline=True)
    embed.add_field(name="Emoji", value=str(emoji), inline=True)
    await log_channel.send(embed=embed)
    
@client.event
async def on_reaction_clear_user(message, user):
    channel_id = reaction_logs
    log_channel = client.get_channel(channel_id)
    embed = discord.Embed(title="Reactions Cleared for User", color=discord.Color.orange())
    embed.add_field(name="User", value=user.mention, inline=True)
    embed.add_field(name="Channel", value=message.channel.mention, inline=True)
    embed.add_field(name="Message ID", value=message.id, inline=True)
    await log_channel.send(embed=embed)
    
@client.event
async def on_reaction_clear_user_emoji(message, user, emoji):
    channel_id = reaction_logs
    log_channel = client.get_channel(channel_id)
    embed = discord.Embed(title="Reactions Cleared for User and Emoji", color=discord.Color.orange())
    embed.add_field(name="User", value=user.mention, inline=True)
    embed.add_field(name="Channel", value=message.channel.mention, inline=True)
    embed.add_field(name="Message ID", value=message.id, inline=True)
    embed.add_field(name="Emoji", value=str(emoji), inline=True)
    await log_channel.send(embed=embed)
            
STAFF_LOG_CHANNEL_ID = 1288061318515134485  # Private Staff Channel ID

MAX_EMOJIS = 5
MAX_MESSAGES_FLOOD = 5
BANNED_LINKS = ["http://", "https://", ".gg/", ".com/invite"]

# Trackers
user_msg_tracker = defaultdict(list)

# --- DATABASE HELPERS ---
def load_warns():
    if os.path.exists('warns.json'):
        with open('warns.json', 'r') as f:
            return json.load(f)
    return {}

def save_warns(data):
    with open('warns.json', 'w') as f:
        json.dump(data, f, indent=4)

def add_warning(user_id, moderator_name, reason):
    warns = load_warns()
    uid = str(user_id)
    if uid not in warns:
        warns[uid] = []

    new_warn = {
        "reason": reason,
        "moderator": moderator_name,
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    warns[uid].append(new_warn)
    save_warns(warns)
    return len(warns[uid])

# --- STAFF INTERACTION VIEW ---
class ModerationActions(ui.View):
    def __init__(self, target_user: discord.Member, original_message: discord.Message, reason: str):
        super().__init__(timeout=None)
        self.target_user = target_user
        self.original_message = original_message
        self.reason = reason

    @ui.button(label="Confirm Warn", style=discord.ButtonStyle.danger, emoji="⚠️")
    async def confirm_warn(self, interaction: discord.Interaction, button: ui.Button):
        total = add_warning(self.target_user.id, str(interaction.user), self.reason)
        
        # Update the log message
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(content=f"✅ {interaction.user.mention} issued a warning. (Total: {total})", view=self)
        
        # DM the user
        try:
            await self.target_user.send(f"⚠️ You received a warning in **{interaction.guild.name}**\nReason: {self.reason}\nTotal Warnings: {total}")
        except:
            pass

    @ui.button(label="Delete Msg", style=discord.ButtonStyle.primary, emoji="🗑️")
    async def delete_msg(self, interaction: discord.Interaction, button: ui.Button):
        try:
            await self.original_message.delete()
            await interaction.response.send_message("Done. Message deleted.", ephemeral=True)
            embed = discord.Embed(title="Message Deleted by Automod", color=discord.Color.red())
            embed.add_field(name="User", value=self.original_message.author.mention, inline=True)
            embed.add_field(name="Channel", value=self.original_message.channel.mention, inline=True)
            embed.add_field(name="Reason", value=self.reason, inline=False)
            await interaction.edit_original_response(content="✅ Message deleted.", embed=embed, view=None)
        except discord.NotFound:
            await interaction.response.send_message("Message already deleted.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to delete: {e}", ephemeral=True)

    @ui.button(label="Dismiss", style=discord.ButtonStyle.secondary, emoji="✔️")
    async def dismiss_action(self, interaction: discord.Interaction, button: ui.Button):
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(content=f"❄️ Ignored by {interaction.user.mention}.", view=self)

# --- EVENTS ---

@client.event
async def on_message(message):
    if message.author.bot or (message.guild and message.author.guild_permissions.manage_messages):
        return

    content = message.content.lower()
    violation = None

    # 1. Check for Links
    if any(link in content for link in BANNED_LINKS):
        violation = "Automod: Sending Links"

    # 2. Check for GIFs
    elif "tenor.com" in content or "giphy.com" in content or any(a.content_type == 'image/gif' for a in message.attachments if a.content_type):
        violation = "Automod: GIF Usage"

    # 3. Check for Emoji Spam
    else:
        custom_emojis = re.findall(r'<a?:\w+:\d+>', message.content)
        unicode_emojis = [c for c in message.content if 1000 < ord(c) < 100000]
        if (len(custom_emojis) + len(unicode_emojis)) > MAX_EMOJIS:
            violation = "Automod: Emoji Spam"

    # 4. Check for Message Flood
    if not violation:
        uid = message.author.id
        now = datetime.datetime.now(datetime.timezone.utc)
        user_msg_tracker[uid] = [t for t in user_msg_tracker[uid] if (now - t).total_seconds() < 5]
        user_msg_tracker[uid].append(now)

        if len(user_msg_tracker[uid]) > MAX_MESSAGES_FLOOD:
            violation = "Automod: Message Flooding"

    # --- ACTION: LOG TO STAFF ---
    if violation:
        log_channel = client.get_channel(STAFF_LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title="🔍 Automod Review Required",
                description=f"**User:** {message.author.mention}\n**Reason:** {violation}",
                color=discord.Color.orange(),
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            embed.add_field(name="Channel", value=message.channel.mention, inline=True)
            embed.add_field(name="Message Content", value=message.content[:1024] or "No text content", inline=False)
            
            view = ModerationActions(target_user=message.author, original_message=message, reason=violation)
            await log_channel.send(embed=embed, view=view)
        return

    await client.process_commands(message)

# --- SLASH COMMANDS ---
@client.tree.command(name="warn", description="Manually warn a member", guild=guild_id)
@app_commands.checks.has_permissions(manage_guild=True)
async def manual_warn(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
    # Using the DB function instead of JSON
    total = await add_warning_db(user.id, interaction.guild.id, str(interaction.user), reason)
    
    await interaction.response.send_message(f"⚠️ {user.mention} warned. Total: {total}", ephemeral=True)
    try:
        await user.send(f"You were warned in **{interaction.guild.name}**\nReason: {reason}")
    except:
        pass

@client.tree.command(name="warns", description="View warnings for a member", guild=guild_id)
async def view_warns(interaction: discord.Interaction, user: discord.User):
    conn = await get_db_conn()
    async with conn.cursor(aiomysql.DictCursor) as cur:
        await cur.execute("SELECT reason, moderator, date FROM user_warnings WHERE user_id=%s AND guild_id=%s", (user.id, interaction.guild.id))
        warns = await cur.fetchall()
    conn.close()

    if not warns:
        await interaction.response.send_message(f"{user.display_name} has no warnings.", ephemeral=True)
        return

    embed = discord.Embed(title=f"Warnings for {user.display_name}", color=discord.Color.orange())
    for i, w in enumerate(warns, 1):
        embed.add_field(
            name=f"Warning #{i}",
            # Note: dictionary keys must match your SQL column names
            value=f"**Reason:** {w['reason']}\n**Mod:** {w['moderator']}\n**Date:** {w['date']}",
            inline=False
        )
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="clearwarns", description="Clear all warnings for a user", guild=guild_id)
@app_commands.checks.has_permissions(administrator=True)
async def clear_warns(interaction: discord.Interaction, user: discord.User):
    conn = await get_db_conn()
    async with conn.cursor() as cur:
        await cur.execute("DELETE FROM user_warnings WHERE user_id=%s AND guild_id=%s", (user.id, interaction.guild.id))
        affected_rows = cur.rowcount
    conn.close()

    if affected_rows > 0:
        await interaction.response.send_message(f"🧹 Cleared {affected_rows} warnings for {user.mention}.", ephemeral=True)
    else:
        await interaction.response.send_message("User has no warnings to clear.", ephemeral=True)
        
@client.event
async def command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error



webserver.keep_alive()
# Run the bot with the token from the environment variable
client.run(TOKEN)
