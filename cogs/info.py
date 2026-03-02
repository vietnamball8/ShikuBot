import discord
from datetime import datetime
import aiohttp
import wikipediaapi
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import requests

guild_id = 1247440062870851625

load_dotenv()
        
weather_api_key = os.getenv("WEATHER_API_KEY")
exchange_currency_api_key = os.getenv("EXCHANGE_CURRENCY_API_KEY")
google_calendar_api_key = os.getenv("GOOGLE_CALENDAR_API_KEY")

# 1. Add this list of common currencies at the top of your Cog or file
CURRENCY_LIST = {
    "USD - US Dollar": "USD",
    "EUR - Euro": "EUR",
    "GBP - British Pound": "GBP",
    "JPY - Japanese Yen": "JPY",
    "CAD - Canadian Dollar": "CAD",
    "AUD - Australian Dollar": "AUD",
    "CNY - Chinese Yuan": "CNY",
    "INR - Indian Rupee": "INR",
    "MXN - Mexican Peso": "MXN",
    "BRL - Brazilian Real": "BRL"
    }

class HelpPaginator(discord.ui.View):
    def __init__(self, commands_list, chunk_size=10):
        super().__init__(timeout=60)
        self.commands_list = commands_list
        self.chunk_size = chunk_size
        self.current_page = 0
        # Split commands into groups of 10
        self.pages = [commands_list[i:i + chunk_size] for i in range(0, len(commands_list), chunk_size)]
        

    def create_embed(self):
        page = self.pages[self.current_page]
        embed = discord.Embed(
            title=f"Help Menu (Page {self.current_page + 1}/{len(self.pages)})",
            color=discord.Color.green()
        )
        for cmd in page:
            embed.add_field(name=f"/{cmd.name}", value=cmd.description or "No description provided.", inline=False)
        return embed

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.gray)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
        else:
            await interaction.response.send_message("You're on the first page!", ephemeral=True)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.gray)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
        else:
            await interaction.response.send_message("You're on the last page!", ephemeral=True)

class Info(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    # Avatar command
    @commands.hybrid_command(name="avatar", description="See someone's profile picture")
    async def avatar(self, ctx, member: discord.Member | None = None):
        member = member or ctx.author
        embed = discord.Embed(title=f"{member.display_name}'s Avatar", color=0x00ff00)
        embed.set_image(url=member.display_avatar.url)
        await ctx.send(embed=embed)
        
    # User info command
    @commands.hybrid_command(name="user_info", description="Get info about a member.")
    async def userinfo(self, ctx, member: discord.Member = None):
        member = member or ctx.author # Default to the person who ran the command
        
        embed = discord.Embed(title=f"User Info - {member.name}", color=member.color)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Joined Server", value=f"<t:{int(member.joined_at.timestamp())}:D>" if member.joined_at else "Unknown")
        embed.add_field(name="Joined Discord", value=f"<t:{int(member.created_at.timestamp())}:D>")
        embed.add_field(name="Top Role", value=member.top_role.mention)
        
    # Server info command
    @commands.hybrid_command(name="server_info", description="Get the lowdown on this server")
    async def serverinfo(self, ctx):
        guild = ctx.guild
        
        embed = discord.Embed(title=f"Welcome to {guild.name}", color=discord.Color.blue())
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)

        owner = guild.owner.mention if guild.owner else f"<@{guild.owner_id}>"
        
        embed.add_field(name="Owner", value=owner, inline=True)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Boost Level", value=f"Level {guild.premium_tier}", inline=True)
        embed.add_field(name="Channels", value=len(guild.channels), inline=True)
        embed.add_field(name="Created On", value=f"<t:{int(guild.created_at.timestamp())}:D>", inline=False)
        total_roles = len(guild.roles)
        total_emojis = len(guild.emojis)
        animated_emojis = len([e for e in guild.emojis if e.animated])
        static_emojis = total_emojis - animated_emojis
        embed.add_field(name="Total Roles", value=str((total_roles) - 1), inline=True)
        embed.add_field(name="Emojis", value=f"Total: {total_emojis}\n(Static: {static_emojis})\n(Animated: {animated_emojis})", inline=True)
        total_stickers = len(guild.stickers)
        embed.add_field(name="Stickers", value=f"{total_stickers}/{guild.sticker_limit}", inline=True)
        
        
        try:
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Failed to send server info: {e}")
            
    @commands.hybrid_command(name="role-info", description="Get the information of a role")
    async def roleinfo(self, ctx: commands.Context, role: discord.Role):
        member_count = len(role.members)
        created_at = f"<t:{int(role.created_at.timestamp())}:D>"
        embed = discord.Embed(title=f"Role Information: {role.name}", color=role.color if role.color.value != 0 else discord.Color.blue())
        
        embed.add_field(name="ID", value=f"'{role.id}'", inline=True)
        embed.add_field(name="Color", value=str(role.color).capitalize(), inline=True)
        embed.add_field(name="Position", value=role.position, inline=True)
        embed.add_field(name="Members Count", value=str(member_count), inline=True)
        embed.add_field(name="Mentionable?", value="Yes" if role.mentionable else "No", inline=True)
        embed.add_field(name="Displayed seperately?", value="Yes" if role.hoist else "No", inline=True)
        embed.add_field(name="Created On", value=created_at, inline=False)
        
        if role.display_icon:
            if isinstance(role.display_icon, discord.Asset):
                embed.set_thumbnail(url=role.display_icon.url)
            else:
                embed.description = f"**Role Icon:** {role.display_icon}"
                
        try:
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Failed to send role info: {e}")
            
    @commands.hybrid_command(name="help-list", description="List all available commands")
    async def help_list(self, ctx: commands.Context):
        # Get all commands registered to the bot
        all_commands = list(self.client.commands)
        
        if not all_commands:
            return await ctx.send("No commands found.")

        # Initialize the paginator
        view = HelpPaginator(all_commands, chunk_size=10)
        embed = view.create_embed()
    
        await ctx.send(embed=embed, view=view)
    
    @commands.hybrid_command(name="weather", description="Get the current weather for a city")
    async def weather(self, ctx: commands.Context, city: str):
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extracting data
                    name = data['name']
                    temp = data['main']['temp']
                    desc = data['weather'][0]['description']
                    humidity = data['main']['humidity']
                    wind = data['wind']['speed']
                    icon = data['weather'][0]['icon']

                    embed = discord.Embed(
                        title=f"Weather in {name}",
                        description=f"Currently: **{desc.capitalize()}**",
                        color=discord.Color.blue()
                    )
                    embed.set_thumbnail(url=f"http://openweathermap.org/img/wn/{icon}@2x.png")
                    embed.add_field(name="Temperature", value=f"{temp}°C")
                    embed.add_field(name="Humidity", value=f"{humidity}%")
                    embed.add_field(name="Wind Speed", value=f"{wind} m/s")
                    embed.set_footer(text="Data from OpenWeatherMap")

                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"Couldn't find weather for `{city}`. Check the spelling!", ephemeral=True)
                    
    @commands.hybrid_command(name="dictionary", description="Look up a word's definition and synonyms!")
    @app_commands.describe(word="The word you want to define")
    async def dictionary(self, ctx: commands.Context, word: str):
        await ctx.defer() 

        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return await ctx.send(f"❌ Could not find a definition for **{word}**.")

                data = await response.json()
                entry = data[0]
                
                word_name = entry.get('word', word).capitalize()
                phonetic = entry.get('phonetic', 'N/A')
                
                embed = discord.Embed(
                    title=f"📖 Dictionary: {word_name}",
                    color=discord.Color.gold()
                )
                embed.set_footer(text=f"Phonetic: {phonetic}")

                # 1. Definitions Logic
                for meaning in entry.get('meanings', [])[:2]:
                    part_of_speech = meaning.get('partOfSpeech', 'noun')
                    definitions = meaning.get('definitions', [])
                    
                    if definitions:
                        main_def = definitions[0].get('definition', 'No definition found.')
                        example = definitions[0].get('example', None)
                        
                        field_value = f"**Definition:** {main_def}"
                        if example:
                            field_value += f"\n*Example: \"{example}\"*"
                        
                        embed.add_field(name=part_of_speech.capitalize(), value=field_value, inline=False)

                # 2. Synonyms Logic
                # We collect synonyms from all 'meanings' sections
                all_synonyms = []
                for meaning in entry.get('meanings', []):
                    syns = meaning.get('synonyms', [])
                    all_synonyms.extend(syns)
                
                if all_synonyms:
                    # Limit to the first 5 synonyms and join with commas
                    syn_text = ", ".join(all_synonyms[:5])
                    embed.add_field(name="Synonyms", value=syn_text, inline=False)

                await ctx.send(embed=embed)
                
    @commands.hybrid_command(name="wiki", description="Summarize a Wikipedia page!")
    @app_commands.describe(query="What do you want to search for?")
    async def wiki(self, ctx: commands.Context, query: str):
        await ctx.defer()

        # Wikipedia-API requires a user agent (standard practice)
        wiki_wiki = wikipediaapi.Wikipedia(
            user_agent="MyDiscordBot/1.0 (contact: your@email.com)",
            language='en',
            extract_format=wikipediaapi.ExtractFormat.WIKI
        )

        page = wiki_wiki.page(query)

        if not page.exists():
            return await ctx.send(f"❌ I couldn't find a Wikipedia page for **{query}**.")

        # Get the first few sentences (summary)
        # We limit to 1000 characters to stay within Discord embed limits
        summary = page.summary
        if len(summary) > 1000:
            summary = summary[:997] + "..."

        embed = discord.Embed(
            title=page.title,
            url=page.fullurl,
            description=summary,
            color=discord.Color.light_grey()
        )
        
        # Optional: Add the first image if you want to get advanced, 
        # but the standard API summary is usually text-only.
        embed.set_footer(text="Source: Wikipedia")

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="currency", description="Convert currency amounts!")
    @app_commands.describe(
        amount="The amount to convert",
        currency="The base currency (e.g. USD)",
        convert_currency="The currency to convert to (e.g. EUR)"
    )
    async def currency_convert(self, ctx: commands.Context, amount: float, currency: str, convert_currency: str):
        await ctx.defer()
        
        # Use the same logic as before to fetch from API
        base = currency.upper()
        target = convert_currency.upper()
        
        url = f"https://v6.exchangerate-api.com/v6/{exchange_currency_api_key}/pair/{base}/{target}/{amount}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                
                if response.status != 200:
                    return await ctx.send(f"❌ Error: Could not find currency `{base}` or `{target}`.")

                result = data.get('conversion_result')
                rate = data.get('conversion_rate')

                embed = discord.Embed(title="💱 Currency Conversion", color=discord.Color.green())
                embed.add_field(name="Result", value=f"## {amount:,.2f} {base} = {result:,.2f} {target}", inline=False)
                embed.set_footer(text=f"Exchange Rate: 1 {base} = {rate:.4f} {target}")
                
                await ctx.send(embed=embed)

    # 3. Add the Autocomplete Logic
    @currency_convert.autocomplete('currency')
    @currency_convert.autocomplete('convert_currency')
    async def currency_auto(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name=name, value=code)
            for name, code in CURRENCY_LIST.items() if current.lower() in name.lower()
        ][:25]
        
    @commands.hybrid_command(name="holidays", description="Check upcoming public holidays!")
    async def holidays(self, ctx: commands.Context, country: str = "india"):
        await ctx.defer() # Crucial for API calls!
        
        # 1. Format the Calendar ID
        # Common formats: en.usa, en.uk, en.canadian, en.indian
        # Note: Some countries use their specific name (e.g., 'en.uk' vs 'en.usa')
        country_id = country.lower().replace(" ", "_")
        calendar_id = f"en.{country_id}#holiday@group.v.calendar.google.com"
            
        # 2. Build the API URL
        now = datetime.utcnow().isoformat() + "Z" # 'Z' indicates UTC time
        url = (
                f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events"
                f"?key={google_calendar_api_key}&timeMin={now}&maxResults=5&singleEvents=True&orderBy=startTime"
            )
        
        try:
            response = requests.get(url)
            data = response.json()
        
            if "items" not in data:
                return await ctx.send(f"❌ Could not find holidays for `{country}`. Try 'usa' or 'uk'.")
        
            # 3. Format the response into an Embed
            embed = discord.Embed(
                    title=f"Upcoming Holidays: {country.upper()}",
                    color=discord.Color.blue(),
                    timestamp=datetime.utcnow()
                    )
        
            for item in data["items"]:
                name = item.get("summary", "Unknown Holiday")
                # Holidays are usually 'date' only, not 'dateTime'
                start_date = item["start"].get("date", item["start"].get("dateTime"))
                embed.add_field(name=name, value=f"📅 {start_date}", inline=False)
        
            await ctx.send(embed=embed)
        
        except Exception as e:
            await ctx.send(f"⚠️ An error occurred: {e}")
        
async def setup(client):

    await client.add_cog(Info(client=client))




