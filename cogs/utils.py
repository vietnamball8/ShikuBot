import discord
import asyncio
import aiohttp
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError, available_timezones
from googletrans import Translator
from discord.ext import commands
from discord import app_commands

guild_id = 1247440062870851625
owner_id = 929610842142539846

translator = Translator()

def send_embed(title,
                   description,
                   footer1=None,
                   footer2=None,
                   footer3=None,
                   footer4=None,
                   title_url=None,
                   color=None,
                   author=None,
                   author_url=None,
                   author_icon_url=None,
                   image_url=None,
                   thumbnail_url=None,
                   timestamp=None,
                   footer_icon=None):
        # 1. Setup the Embed with your specific requirements
        embed = discord.Embed(
            title=title,
            description=description,
            url=title_url, # title_url
            color=color,
            timestamp=timestamp
        )

        # Author details
        embed.set_author(
            name=author or "", # author
            url=author_url, # author url
            icon_url=author_icon_url # author icon url
        )

        # Images
        embed.set_image(url=image_url) # image url
        embed.set_thumbnail(url=thumbnail_url) # thumbnail url

        # Footer (Combining 4 footers into the allowed 1 slot)
        
        footer_text = ""
        
        if not footer1:
            footer1 = ""
        else:
            footer_text = footer1
            
        if footer2:
            footer_text += f"\n{footer2}"
        if footer3:
            footer_text += f"\n{footer3}"
        if footer4:
            footer_text += f"\n{footer4}"
        embed.set_footer(
            text=footer_text if footer_text else None, # footer text (only if there's at least 1 footer):
            icon_url=footer_icon # footer icon
        )
        return embed

class Utils(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @commands.hybrid_command(name="ping", description="Checks the bot latency")
    async def ping(self, ctx):
        latency = round(self.client.latency * 1000)
        await ctx.send(f"Pong! {latency}ms")
        
    @commands.hybrid_command(name="embed-test", description="Responds with an embed!")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def embed(self, ctx):
        embed = discord.Embed(title="Example Embed", url="https://www.youtube.com/shorts/srdg-c9_ssQ", description="This is an example embed.", color=0x00ff00)
        embed.set_thumbnail(url="https://static.vecteezy.com/system/resources/thumbnails/057/068/323/small/single-fresh-red-strawberry-on-table-green-background-food-fruit-sweet-macro-juicy-plant-image-photo.jpg")
        embed.add_field(name="Field 1", value="This is the value for field 1. <:DiamondQPoker:1474198846077796524>", inline=False)
        embed.add_field(name="Field 2", value="This is the value for field 2.", inline=False)
        try:
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Failed to send embed: {e}")
            
    # Embed say command
    @commands.hybrid_command(name="say-embed", description="Print an advanced embed!")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def print_embed(self, ctx: commands.Context,
                        title: str, *,
                        description: str,
                        footer1: str | None = None,
                        footer2: str | None = None,
                        footer3: str | None = None,
                        footer4: str | None = None,
                        title_url: str | None = None,
                        color: str | None = None,
                        author: str | None = None,
                        author_url: str | None = None,
                        author_icon_url: str | None = None,
                        image_url: str | None = None,
                        thumbnail_url: str | None = None,
                        timestamp: str | None = None,
                        footer_icon: str | None = None):

        # 1. Print the embed with the provided parameters
        embed = send_embed(title=title,
                        description=description,
                        footer1=footer1,
                        footer2=footer2,
                        footer3=footer3,
                        footer4=footer4,
                        title_url=title_url,
                        color=color,
                        author=author,
                        author_url=author_url,
                        author_icon_url=author_icon_url,
                        image_url=image_url,
                        thumbnail_url=thumbnail_url,
                        timestamp=timestamp,
                        footer_icon=footer_icon)
        
        # 2. Send the Embed
        channel = ctx.channel
        
        try:
            await ctx.send("Message successfully sent: ", ephemeral=True)
            await channel.send(embed=embed)
            
            embed = discord.Embed(title="Embed Sent", description=f"{ctx.author} successfully sent an embed in channel {channel.mention}", color=discord.Color.green())
            
            owner = await self.client.fetch_user(owner_id)
            
            await owner.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Failed to send embed: {e}", ephemeral=True)
            
    # Reply with an embed to a specific message by its ID
    @commands.hybrid_command(name="reply-embed", description="Reply with an advanced embed to a specific message!")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def reply_embed(self, ctx: commands.Context,
                        message_id: str,
                        title: str, *,
                        description: str,
                        footer1: str | None = None,
                        footer2: str | None = None,
                        footer3: str | None = None,
                        footer4: str | None = None,
                        title_url: str | None = None,
                        color: str | None = None,
                        author: str | None = None,
                        author_url: str | None = None,
                        author_icon_url: str | None = None,
                        image_url: str | None = None,
                        thumbnail_url: str | None = None,
                        timestamp: str | None = None,
                        footer_icon: str | None = None):
        
        message_id = int(message_id)

        # 1. Print the embed with the provided parameters
        embed = send_embed(title=title,
                        description=description,
                        footer1=footer1,
                        footer2=footer2,
                        footer3=footer3,
                        footer4=footer4,
                        title_url=title_url,
                        color=color,
                        author=author,
                        author_url=author_url,
                        author_icon_url=author_icon_url,
                        image_url=image_url,
                        thumbnail_url=thumbnail_url,
                        timestamp=timestamp,
                        footer_icon=footer_icon)
        
        # 2. Send the Embed
        channel = ctx.channel
        try:
            await ctx.send("Message successfully sent: ", ephemeral=True)
            await channel.send(embed=embed, reference=discord.MessageReference(channel_id=channel.id, message_id=message_id))
            
            owner = await self.client.fetch_user(owner_id)
            
            embed = discord.Embed(title="Embed Replied", description=f"{ctx.author} successfully replied by the embed for message ID: {message_id}", color=discord.Color.green())
            await owner.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Failed to send embed: {e}", ephemeral=True)
            
    # Edit an embed to a specific message by its ID
    @commands.hybrid_command(name="edit-embed", description="Edit an advanced embed to a specific message!")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def edit_embed(self, ctx: commands.Context,
                        message_id: str,
                        title: str, *,
                        description: str,
                        footer1: str | None = None,
                        footer2: str | None = None,
                        footer3: str | None = None,
                        footer4: str | None = None,
                        title_url: str | None = None,
                        color: str | None = None,
                        author: str | None = None,
                        author_url: str | None = None,
                        author_icon_url: str | None = None,
                        image_url: str | None = None,
                        thumbnail_url: str | None = None,
                        timestamp: str | None = None,
                        footer_icon: str | None = None):
        
        message_id = int(message_id)

        # 1. Print the embed with the provided parameters
        embed = send_embed(title=title,
                        description=description,
                        footer1=footer1,
                        footer2=footer2,
                        footer3=footer3,
                        footer4=footer4,
                        title_url=title_url,
                        color=color,
                        author=author,
                        author_url=author_url,
                        author_icon_url=author_icon_url,
                        image_url=image_url,
                        thumbnail_url=thumbnail_url,
                        timestamp=timestamp,
                        footer_icon=footer_icon)
        
        # 2. Send the Embed
        channel = ctx.channel
        msg = await channel.fetch_message(int(message_id))
        try:
            await ctx.send("Message successfully edited: ", ephemeral=True)
            await msg.edit(embed=embed, reference=discord.MessageReference(channel_id=channel.id, message_id=message_id))
            
            owner = await self.client.fetch_user(owner_id)
            
            embed = discord.Embed(title="Embed Edited", description=f"{ctx.author} successfully edited the embed for message ID: {message_id}", color=discord.Color.green())
            await owner.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Failed to edit embed: {e}", ephemeral=True)
            
    # DM Command
    @commands.hybrid_command(name="dm", description="Send a direct message to a user")
    @app_commands.checks.has_permissions(administrator=True)
    async def dm(self, ctx, user: discord.User, message: str):
        try:
            # 1. Send the message to the target user
            await user.send(f"{message}")
            
            # 2. Log it to the bot owner
            # We use client.get_user to turn the ID into an object we can talk to
            owner = ctx.bot.get_user(owner_id)
            if owner:
                log_embed = discord.Embed(
                    title="DM Sent by Admin", 
                    description=f"**From:** {ctx.author}\n**To:** {user.mention}\n**Content:** {message}", 
                    color=discord.Color.green()
                )
                await owner.send(embed=log_embed)

            # 3. Respond to the interaction (This MUST happen or the command "fails")
            await ctx.send(f"✅ Message sent to {user.mention}", ephemeral=True)

        except discord.Forbidden:
            await ctx.send(f"❌ Could not DM {user.mention}. Their DMs are closed.", ephemeral=True)
        except Exception as e:
            # If interaction was already responded to, use followup
            if ctx.interaction.response.is_done():
                await ctx.send(f"An error occurred: {e}", ephemeral=True)
            else:
                await ctx.send(f"An error occurred: {e}", ephemeral=True)
                
    # Edit a specific message by its ID
    @commands.hybrid_command(name="edit", description="Edit a specific message by its ID.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def edit_msg(self, ctx: commands.Context, content: str, message_id: str):
        channel = ctx.channel
        try:
            message = await channel.fetch_message(int(message_id))
            await message.edit(content=content)
            await ctx.send("Message successfully edited!", ephemeral=True)
            
            owner = await ctx.bot.get_user(owner_id)
            
            embed = discord.Embed(title="Message Edited", description=f"{ctx.author} successfully edited the message with ID: {message_id}", color=discord.Color.green())
            await owner.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Failed to edit message: {e}", ephemeral=True)
            
    # Reply to a specific message with the message ID
    @commands.hybrid_command(name="reply-to", description="Reply to a specific message by its ID.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def print_msg(self, ctx: commands.Context, content: str, message_id: str):
        channel = ctx.channel
        message_id = int(message_id)
        # Replies to the message with the given ID
        await ctx.send("Message successfully sent: ", ephemeral=True)
        await channel.send(content, reference=discord.MessageReference(channel_id=channel.id, message_id=message_id))
        
        owner = await ctx.bot.get_user(owner_id)
        
        embed = discord.Embed(title="Message Replied", description=f"{ctx.author} successfully replied to the message for message ID: {message_id}", color=discord.Color.green())
        await owner.send(embed=embed)
        
    # Print the message sent by the user
    @commands.hybrid_command(name="say", description="Print a message!")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def print_msg(self, ctx: commands.Context, content: str):
        channel = ctx.channel
        # Just sends a fresh message
        await ctx.send("Message successfully sent: ", ephemeral=True)
        await channel.send(content)
        
        owner = await ctx.bot.get_user(owner_id)
        
        embed = discord.Embed(title="Message Sent", description=f"{ctx.author} successfully sent a message in channel {channel.mention}", color=discord.Color.green())
        await owner.send(embed=embed)
        
    @commands.hybrid_command(name="remind", description="Create a reminder for a task!")
    async def remind(self, ctx: commands.Context, message_remind: str, *, time: str):
        seconds = 0
        if time.endswith("s"):
            seconds = int(time[:-1])
        elif time.endswith("m"):
            seconds = int(time[:-1]) * 60
        elif time.endswith("h"):
            seconds = int(time[:-1]) * 3600

        await ctx.send(f"Okay! I'll remind you of {message_remind} in {time}!")
        
        await asyncio.sleep(seconds)
        await ctx.send(f"{ctx.author.mention}, here is your reminder: {message_remind}")
    
    @commands.hybrid_command(name="translate", description="Translate a certain message to English!")
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    async def translate(self, ctx: commands.Context, message_id: str):
        await ctx.defer()
        
        try:
            target_msg = await ctx.channel.fetch_message(int(message_id))
            if not target_msg.content:
                return await ctx.send("That message is empty or contains only an image.")

            # Perform translation
            result = translator.translate(target_msg.content, dest='en')

            # Check if the message is already in English
            if result.src == 'en':
                return await ctx.send("🔍 This message is already in English!", ephemeral=True)

            # Build the response
            embed = discord.Embed(description=result.text, color=0x3498db)
            embed.set_author(name=target_msg.author.display_name, icon_url=target_msg.author.display_avatar.url)
            embed.set_footer(text=f"Translated from {result.src.upper()} to EN")

            await ctx.send(embed=embed)

        except discord.NotFound:
            await ctx.send("I couldn't find a message with that ID in this channel.")
        except ValueError:
            await ctx.send("Please provide a valid numeric Message ID.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")      
    
    @staticmethod
    async def get_timezone_choices(current: str) -> list[app_commands.Choice[str]]:
        all_zones = sorted(list(available_timezones()))
        return [
            app_commands.Choice(name=zone, value=zone)
            for zone in all_zones if current.lower() in zone.lower()
        ][:25]

    @commands.hybrid_command(name="timezone-name", description="Check a timezone name!")
    @app_commands.describe(timezone="Start typing a city (e.g. London, New York, Tokyo)")
    async def timezone(self, ctx: commands.Context, timezone: str):
        try:
            # Clean up the input (remove accidental spaces)
            timezone = timezone.strip()
            zone = ZoneInfo(timezone)
            now = datetime.now(zone)
            
            embed = discord.Embed(
                title=f"🕒 {timezone}",
                description=f"## {now.strftime('%I:%M %p')}",
                color=discord.Color.blurple()
            )
            embed.add_field(name="Date", value=now.strftime("%A, %B %d"))
            embed.set_footer(text=f"Offset: {now.strftime('%z')} | {now.tzname()}")

            await ctx.send(embed=embed)

        except ZoneInfoNotFoundError:
            await ctx.send(f"❌ `{timezone}` is not a valid timezone. Please select an option from the list!", ephemeral=True)

    @timezone.autocomplete('timezone')
    async def timezone_auto(self, interaction: discord.Interaction, current: str):
        # Get all zones from the system
        all_zones = list(available_timezones())
        
        # FALLBACK: If your system has no zones (common on some Windows setups)
        if not all_zones:
            all_zones = ["UTC", "America/New_York", "Europe/London", "Asia/Tokyo", "Australia/Sydney"]

        # Filter the list based on what the user typed
        choices = [
            app_commands.Choice(name=zone, value=zone)
            for zone in sorted(all_zones) if current.lower() in zone.lower()
        ]
        
        # Return only the first 25 (Discord's hard limit)
        return choices[:25]
            
    
            
    
            
        
        
async def setup(client):

    await client.add_cog(Utils(client=client))

