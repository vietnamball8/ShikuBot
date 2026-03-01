import discord
import datetime
import html
import requests
from discord.ext import commands
from discord import app_commands
from wonderwords import RandomWord
import random
import asyncio
import aiohttp

guild_id = 1247440062870851625

EIGHTBALL_RESPONSES = [
    "It is certain.", "It is decidedly so.", "Without a doubt.",
    "Yes, definitely.", "You may rely on it.", "As I see it, yes.",
    "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.",
    "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
    "Cannot predict now.", "Concentrate and ask again.",
    "Don't count on it.", "My reply is no.", "My sources say no.",
    "Outlook not so good.", "Very doubtful."]

STAGES = [
    "```\n  +---+\n  |   |\n      |\n      |\n      |\n      |\n=========\n```",
    "```\n  +---+\n  |   |\n  O   |\n      |\n      |\n      |\n=========\n```",
    "```\n  +---+\n  |   |\n  O   |\n  |   |\n      |\n      |\n=========\n```",
    "```\n  +---+\n  |   |\n  O   |\n /|   |\n      |\n      |\n=========\n```",
    "```\n  +---+\n  |   |\n  O   |\n /|\\  |\n      |\n      |\n=========\n```",
    "```\n  +---+\n  |   |\n  O   |\n /|\\  |\n /    |\n      |\n=========\n```",
    "```\n  +---+\n  |   |\n  O   |\n /|\\  |\n / \\  |\n      |\n=========\n```"
]

emoji_cards = {
    "2♣️": "<:Club2Poker:1474241616595386409>", 
    "3♣️": "<:Club3Poker:1474241613743132703>",
    "4♣️": "<:Club4Poker:1474241611813621831>",
    "5♣️": "<:Club5Poker:1474241610131705917>",
    "6♣️": "<:Club6Poker:1474241608223428651>",
    "7♣️": "<:Club7Poker:1474241606378065981>",
    "8♣️": "<:Club8Poker:1474241604675178649>",
    "9♣️": "<:Club9Poker:1474241602997452830>",
    "10♣️": "<:Club10Poker:1474241601042780363>",
    "J♣️": "<:ClubJPoker:1474241598886908066>",
    "Q♣️": "<:ClubQPoker:1474241596601143348>",
    "K♣️": "<:ClubKPoker:1474241595153846312>",
    "A♣️": "<:ClubAPoker:1474241619317227603>",
    "2♦️": "<:Diamond2Poker:1474198867967738030>",
    "3♦️": "<:Diamond3Poker:1474198866055397519>",
    "4♦️": "<:Diamond4Poker:1474198864192868467>",
    "5♦️": "<:Diamond5Poker:1474198862083391540>",
    "6♦️": "<:Diamond6Poker:1474198860154015926>",
    "7♦️": "<:Diamond7Poker:1474198858031431740>",
    "8♦️": "<:Diamond8Poker:1474198855632290014>",
    "9♦️": "<:Diamond9Poker:1474198853115838607>",
    "10♦️": "<:Diamond10Poker:1474198851253702811>",
    "J♦️": "<:DiamondJPoker:1474198848657293433>",
    "Q♦️": "<:DiamondQPoker:1474198846077796524>",
    "K♦️": "<:DiamondKPoker:1474198843917598964>",
    "A♦️": "<:DiamondAPoker:1474198869767229602>",
    "2❤️": "<:Heart2Poker:1474250752716177479>",
    "3❤️": "<:Heart3Poker:1474250750883266863>",
    "4❤️": "<:Heart4Poker:1474250748417019988>",
    "5❤️": "<:Heart5Poker:1474250745204183081>",
    "6❤️": "<:Heart6Poker:1474250742905835560>",
    "7❤️": "<:Heart7Poker:1474250740678787122>",
    "8❤️": "<:Heart8Poker:1474250738678104146>",
    "9❤️": "<:Heart9Poker:1474250736891199509>",
    "10❤️": "<:Heart10Poker:1474250734894579742>",
    "J❤️": "<:HeartJPoker:1474250732793364707>",
    "Q❤️": "<:HeartQPoker:1474250730956128256>",
    "K❤️": "<:HeartKPoker:1474250728162721792>",
    "A❤️": "<:HeartAPoker:1474250754872054035>",
    "2♠️": "<:Spade2Poker:1474323560779612303>",
    "3♠️": "<:Spade3Poker:1474323558346784889>",
    "4♠️": "<:Spade4Poker:1474323556639834253>",
    "5♠️": "<:Spade5Poker:1474323554781757480>",
    "6♠️": "<:Spade6Poker:1474323553032736899>",
    "7♠️": "<:Spade7Poker:1474323550822338581>",
    "8♠️": "<:Spade8Poker:1474323548641431664>",
    "9♠️": "<:Spade9Poker:1474323545952616562>",
    "10♠️": "<:Spade10Poker:1474323543629103197>",
    "J♠️": "<:SpadeJPoker:1474323542093861008>",
    "Q♠️": "<:SpadeQPoker:1474323540286374033>",
    "K♠️": "<:SpadeKPoker:1474323538658983946>",
    "A♠️": "<:SpadeAPoker:1474323562625105940>"
}

class RPSView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60) # Buttons will disable after 60 seconds of inactivity

    @discord.ui.button(label="Rock", style=discord.ButtonStyle.blurple, emoji="🪨")
    async def rock(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.resolve_game(interaction, "Rock")

    @discord.ui.button(label="Paper", style=discord.ButtonStyle.green, emoji="📜")
    async def paper(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.resolve_game(interaction, "Paper")

    @discord.ui.button(label="Scissors", style=discord.ButtonStyle.red, emoji="✂️")
    async def scissors(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.resolve_game(interaction, "Scissors")

    async def resolve_game(self, interaction: discord.Interaction, user_choice):
        bot_choice = random.choice(["Rock", "Paper", "Scissors"])
        
        # Determine Winner
        if user_choice == bot_choice:
            result = "It's a tie! 👔"
            color = discord.Color.light_gray()
        elif (user_choice == "Rock" and bot_choice == "Scissors") or \
             (user_choice == "Paper" and bot_choice == "Rock") or \
             (user_choice == "Scissors" and bot_choice == "Paper"):
            result = "You win! 🎉"
            color = discord.Color.green()
        else:
            result = "I win! 🤖"
            color = discord.Color.red()

        embed = discord.Embed(
            title="Rock, Paper, Scissors", 
            description=f"You chose **{user_choice}**\nI chose **{bot_choice}**\n\n**{result}**", 
            color=color
        )
        
        # We keep 'view=self' so the buttons stay there for another round!
        await interaction.response.edit_message(content="Want to go again?", embed=embed, view=self)

    # This handles when the 60 second timer runs out
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        # You can't easily edit the message here without a stored message object, 
        # but this prevents further clicks.
        

# --- THE GAMEPLAY VIEW (Buttons for Rock/Paper/Scissors) ---
class RPSPlayerView(discord.ui.View):
    def __init__(self, challenger, opponent):
        super().__init__(timeout=60)
        self.challenger = challenger
        self.opponent = opponent
        self.choices = {}

    async def handle_choice(self, interaction, choice):
        if interaction.user not in [self.challenger, self.opponent]:
            return await interaction.response.send_message("You aren't in this battle!", ephemeral=True)
        
        if interaction.user.id in self.choices:
            return await interaction.response.send_message("You already chose!", ephemeral=True)

        self.choices[interaction.user.id] = choice
        await interaction.response.defer() 
        
        if len(self.choices) == 2:
            p1_c = self.choices[self.challenger.id]
            p2_c = self.choices[self.opponent.id]
            
            # Simplified result logic
            if p1_c == p2_c:
                res = "It's a tie! 👔"
            elif (p1_c == "Rock" and p2_c == "Scissors") or \
                 (p1_c == "Paper" and p2_c == "Rock") or \
                 (p1_c == "Scissors" and p2_c == "Paper"):
                res = f"{self.challenger.display_name} wins! 🎉"
            else:
                res = f"{self.opponent.display_name} wins! 🎉"

            embed = discord.Embed(title="Battle Results!", description=f"{self.challenger.mention}: **{p1_c}**\n{self.opponent.mention}: **{p2_c}**\n\n**{res}**", color=0xFFD700)
            await interaction.message.edit(content=None, embed=embed, view=None)
        else:
            await interaction.followup.send("Choice recorded! Waiting for opponent...", ephemeral=True)

    @discord.ui.button(label="Rock", emoji="🪨")
    async def rock(self, interaction, button): await self.handle_choice(interaction, "Rock")
    @discord.ui.button(label="Paper", emoji="📜")
    async def paper(self, interaction, button): await self.handle_choice(interaction, "Paper")
    @discord.ui.button(label="Scissors", emoji="✂️")
    async def scissors(self, interaction, button): await self.handle_choice(interaction, "Scissors")

# --- THE INVITATION VIEW (The "Accept" Button) ---
class RPSInviteView(discord.ui.View):
    def __init__(self, challenger, opponent):
        super().__init__(timeout=30)
        self.challenger = challenger
        self.opponent = opponent

    @discord.ui.button(label="Accept Challenge", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.opponent:
            return await interaction.response.send_message("Only the challenged player can accept!", ephemeral=True)
        
        # Switch to the Game View
        game_view = RPSPlayerView(self.challenger, self.opponent)
        await interaction.response.edit_message(content=f"Battle Started! {self.challenger.mention} vs {self.opponent.mention}\nChoose your weapon!", view=game_view)

    async def on_timeout(self):
        # Disable buttons if no one accepts
        for item in self.children:
            item.disabled = True
            
class BlackjackView(discord.ui.View):
    def __init__(self, user_hand, bot_hand, deck):
        super().__init__(timeout=60)
        self.user_hand = user_hand
        self.bot_hand = bot_hand
        self.deck = deck

    def calculate_score(self, hand):
        score = 0
        aces = 0
        # Mapping ranks to values
        values = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, 
                  "10": 10, "J": 10, "Q": 10, "K": 10, "A": 11}
        
        for card in hand:
            # Extract rank by removing the last 2 characters (the emoji)
            # We handle '10' vs 'A' by checking if the card starts with '10'
            rank = "10" if card.startswith("10") else card[0]
            score += values[rank]
            if rank == "A":
                aces += 1
        
        # Optimization: Reduce Ace value from 11 to 1 if score > 21
        while score > 21 and aces:
            score -= 10
            aces -= 1
        return score

    def create_embed(self, title="Blackjack", color=discord.Color.blue(), show_all=False):
        user_score = self.calculate_score(self.user_hand)
        bot_score = self.calculate_score(self.bot_hand)
        
        embed = discord.Embed(title=title, color=color)
        embed.add_field(
            name="Your Hand", 
            value=f"{format_hand(self.user_hand)}\n**Total: {user_score}**", 
            inline=False
        )
        
        if show_all:
            embed.add_field(
                name="Bot's Hand", 
                value=f"{format_hand(self.bot_hand)}\n**Total: {bot_score}**", 
                inline=False
            )
        else:
            # Hide the bot's second card during the game
            hidden_bot_hand = self.bot_hand.copy()
            hidden_bot_hand[1] = "❓"  # Replace second card with a question mark
            embed.add_field(
                name="Bot's Hand", 
                value=f"{format_hand(self.bot_hand)}\n**Total: {bot_score}**", 
                inline=False
            )
        return embed

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.green)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Draw a card and check for bust
        self.user_hand.append(self.deck.pop())
        user_score = self.calculate_score(self.user_hand)
        
        if user_score > 21:
            embed = self.create_embed(title="Bust! 💥", color=discord.Color.red(), show_all=True)
            embed.description = f"You went over 21 with {user_score}. Better luck next time!"
            await interaction.response.edit_message(embed=embed, view=None)
            self.stop()
        else:
            await interaction.response.edit_message(embed=self.create_embed())

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.gray)
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Bot's turn: Dealer must hit until they have at least 17
        while self.calculate_score(self.bot_hand) < 17:
            self.bot_hand.append(self.deck.pop())

        user_score = self.calculate_score(self.user_hand)
        bot_score = self.calculate_score(self.bot_hand)
        
        if bot_score > 21:
            result = "The bot busted! **You win!** 🎉"
            color = discord.Color.green()
        elif user_score > bot_score:
            result = f"**You win!** {user_score} beats {bot_score} 🎉"
            color = discord.Color.green()
        elif bot_score > user_score:
            result = f"**Bot wins!** {bot_score} beats {user_score} 🤖"
            color = discord.Color.red()
        else:
            result = "It's a **Tie!** 👔"
            color = discord.Color.light_gray()

        embed = self.create_embed(title="Final Results", color=color, show_all=True)
        embed.description = result
        await interaction.response.edit_message(embed=embed, view=None)
        self.stop()
        
def format_hand(hand):
    return " ".join([emoji_cards.get(card, card) for card in hand])

class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client
        
        self.rw = RandomWord()
    
    # RPS    
    @commands.hybrid_command(name="rps", description="Play Rock Paper Scissors!")
    async def rps(self, ctx):
        # We use self.bot because 'bot' is stored in the class instance
        await ctx.send("Choose your weapon!", view=RPSView())
    
    # RPS battle    
    @commands.hybrid_command(name="rps-battle", description="Challenge a player to RPS!")
    async def battle(self, ctx, opponent: discord.Member):
        if opponent == ctx.author:
            return await ctx.send("Self-harm is not allowed! (Don't battle yourself).")
    
        view = RPSInviteView(ctx.author, opponent)
        await ctx.send(f"⚔️ {ctx.author.mention} has challenged {opponent.mention} to a duel!", view=view)
    
    # 8ball    
    @commands.hybrid_command(name="8ball", description="Ask the magic 8ball a question!")
    async def eightball(self, ctx, *, question: str):
        answer = random.choice(EIGHTBALL_RESPONSES)
    
        # Create a nice UI experience with an Embed
        embed = discord.Embed(
            title="🔮 The Magic 8-Ball",
            color=0x2b2d31  # A sleek dark grey color
        )
        embed.add_field(name="Question:", value=question, inline=False)
        embed.add_field(name="Answer:", value=f"**{answer}**", inline=False)
        embed.set_footer(text=f"Asked by {ctx.author.display_name}")
    
        await ctx.send(embed=embed)
    
    # Blackjack
    @commands.hybrid_command(name="blackjack", description="Play a game of Blackjack with suit icons!")
    async def blackjack(self, ctx):
        suits = ["♠️", "❤️", "♦️", "♣️"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    
        # Generate and shuffle a fresh deck
        deck = [f"{rank}{suit}" for rank in ranks for suit in suits]
        random.shuffle(deck)
    
        # Initial deal
        user_hand = [deck.pop(), deck.pop()]
        bot_hand = [deck.pop(), deck.pop()]
        
        view = BlackjackView(user_hand, bot_hand, deck)
        # If it's an immediate Blackjack for the player
        if view.calculate_score(user_hand) == 21:
            embed = view.create_embed(title="Blackjack! 🃏", color=discord.Color.gold(), show_all=True)
            embed.description = "Natural 21! You win instantly!"
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=view.create_embed(), view=view)
            
    # Coinflip command
    @commands.hybrid_command(name="coinflip", description="Flip a coin and see the result!")
    async def coinflip(self, ctx):
        result = random.choice(["Heads", "Tails"])
        try:
            embed = discord.Embed(title="Coin Flip Result", description=f"You flipped **{result}**!", color=0x00ff00)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Failed to flip coin: {e}", ephemeral=True)
            
    # Snake Eyes command
    @commands.hybrid_command(name="snakeeyes", description="Roll two dice and see if you get snake eyes!")
    async def snakeeyes(self, ctx):
        die1 = random.randint(1, 6)
        die2 = random.randint(1, 6)
        
        if die1 == 1 and die2 == 1:
            result = "Snake Eyes! 🎲🎲 You rolled double ones!"
            color = discord.Color.green()
        else:
            result = f"You rolled a {die1} and a {die2}. Better luck next time!"
            color = discord.Color.red()
        
        embed = discord.Embed(title="Snake Eyes Result", description=result, color=color)
        await ctx.send(embed=embed)
        
    @commands.hybrid_command(name="russian-roulette", description="Duel the bot in a 6-round game!", guild=guild_id)
    async def russian_roulette(self, ctx):
        # 1. Setup
        chambers = [0, 0, 0, 0, 0, 1]
        random.shuffle(chambers)
        player_name = ctx.author.display_name
        bot_name = self.client.user.name
        
        # Initial "Loading" message
        embed = discord.Embed(
            title="Russian Roulette Duel", 
            description=f"**{player_name}** vs **{bot_name}**\nSpinning the cylinder... 🎰", 
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

        full_log = ""
        
        # 2. Loop through 6 rounds
        for i in range(6):
            await asyncio.sleep(2) # Suspense pause
            
            current_round = i + 1
            # Determine whose turn it is
            # Round 1, 3, 5 = Player | Round 2, 4, 6 = Bot
            is_player_turn = (current_round % 2 != 0)
            current_actor = player_name if is_player_turn else bot_name
            
            # Check the chamber
            if chambers[i] == 1:
                full_log += f"**Round {current_round}:** {current_actor} pulls the trigger... 💥 **BANG!**"
                
                # If the player died, red. If the bot died, gold (player wins!)
                final_color = discord.Color.red() if is_player_turn else discord.Color.gold()
                result_text = f"{current_actor} is out of the game! " + ("You lost..." if is_player_turn else "You won!")
                
                embed = discord.Embed(title=result_text, description=full_log, color=final_color)
                await ctx.interaction.edit_original_response(embed=embed)
                return
            
            else:
                full_log += f"**Round {current_round}:** {current_actor} pulls the trigger... *Click.* 😅\n"
                
                # Update the UI for the "Safe" result
                embed = discord.Embed(
                    title=f"Duel: Round {current_round}/6", 
                    description=full_log + f"\n*Next up: {bot_name if is_player_turn else player_name}...*", 
                    color=discord.Color.green()
                )
                await ctx.interaction.edit_original_response(embed=embed)

        # In the rare case of a dud (though mathematically 1/6 always hits)
        await ctx.interaction.edit_original_response(content="The gun jammed? Everyone survived! (This shouldn't happen with a proper shuffle, but hey, it's Russian Roulette! 😅)")
        
        
     # Roll a dice command
    @commands.hybrid_command(name="dice", description="Rolls a dice and responds with the result!")
    async def dice(self, ctx):
        result = random.randint(1, 6)
        try:
            await ctx.send(f'You rolled a {result}!')
        except Exception as e:
            await ctx.send(f"Failed to roll dice: {e}")
            
    @commands.hybrid_command(name="meme", description="Get a random meme from Reddit")
    async def meme(self, ctx: commands.Context):
        await ctx.defer() # Fetching from an API takes time

        # List of safe subreddits
        subreddits = ["memes", "dankmemes", "wholesomememes"]
        chosen_sub = random.choice(subreddits)

        async with aiohttp.ClientSession() as session:
            # We use the meme-api.com service
            async with session.get(f"https://meme-api.com/gimme/{chosen_sub}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # SAFETY CHECK: If the post is NSFW, we inform the user and stop.
                    # Alternatively, you could wrap this in a 'while' loop to retry.
                    if data.get("nsfw"):
                        await ctx.send("🚫 The meme found was NSFW and has been blocked.")
                        return

                    embed = discord.Embed(
                        title=data.get("title"),
                        url=data.get("postLink"),
                        color=discord.Color.random()
                    )
                    embed.set_image(url=data.get("url"))
                    embed.set_footer(text=f"👍 {data.get('ups')} | Source: r/{data.get('subreddit')}")
                    
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("💥 Error connecting to the Meme API.") 
                    
                    
    @commands.hybrid_command(name="quote", description="Get an inspirational quote")
    async def quote(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://zenquotes.io/api/random") as response:
                if response.status == 200:
                    data = await response.json()
                    quote_text = data[0]['q']
                    author = data[0]['a']
                    await ctx.send(f"“{quote_text}” — **{author}**")
                else:
                    await ctx.send("I couldn't grab a quote right now. Try again later!")
                    
    @commands.hybrid_command(name="news", description="Fetch the latest news in the world")
    async def news(self, ctx):
        NEWSDATA_API_KEY = "pub_40352fd6a3a84d38af293cf08303d885"
        url = "https://newsdata.io/api/1/latest?apikey=pub_40352fd6a3a84d38af293cf08303d885"
        url = f"https://newsdata.io/api/1/latest?apikey={NEWSDATA_API_KEY}&language=en"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    results = data.get("results", [])

                    if not results:
                        await ctx.send("No news found right now.")
                        return

                    # Create an embed for the first (top) story
                    # We'll show the top story in detail and list others below
                    top_story = results[0]
                    embed = discord.Embed(
                        title=top_story.get("title", "No Title"),
                        url=top_story.get("link"),
                        description=top_story.get("description", "No description available.")[:200] + "...",
                        color=discord.Color.brand_green()
                    )
                    
                    # Add the news image if it exists
                    if top_story.get("image_url"):
                        embed.set_image(url=top_story.get("image_url"))

                    # Add a "More News" section for the next 2 headlines
                    more_news = ""
                    for article in results[1:3]:
                        more_news += f"🔹 [{article['title']}]({article['link']})\n\n"
                    
                    if more_news:
                        embed.add_field(name="More Headlines", value=more_news, inline=False)

                    embed.set_footer(text=f"Source: {top_story.get('source_id')} | NewsData.io")
                    
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"Error fetching news: Code {response.status}")
                    
    @commands.hybrid_command(name="cat", description="Show a picture of a cat")
    async def cat(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.thecatapi.com/v1/images/search") as resp:
                image = await resp.json()
                await ctx.send(image[0]["url"])
                
    @commands.hybrid_command(name="dadjoke", description="Send a random dadjoke")
    async def dadjoke(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://icanhazdadjoke.com/", headers={"Accept": "application/json"}) as resp:
                data = await resp.json()
                await ctx.send(f"**Dad joke alert** ☝️\n{data['joke']}")
                
    @commands.hybrid_command(name="trivia", description="Send a trivia and answer a random question!")
    async def trivia(self, ctx: commands.Context):
        await ctx.defer()
        
        response = requests.get("https://opentdb.com/api.php?amount=1&type=boolean")
        data = response.json()
        
        if data['response_code'] == 0:
            result = data['results'][0]
            category = result['category']
            # Use html.unescape to fix characters like &quot; or &#039;
            question = html.unescape(result['question'])
            correct_answer = result['correct_answer']

            # 2. Send the question
            await ctx.send(f"**Category:** {category}\n**Question:** {question}\n*(Reply with True or False)*")

            # 3. Wait for the user's answer
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            try:
                msg = await self.client.wait_for('message', check=check, timeout=30.0)
                if msg.content.lower() == correct_answer.lower():
                    await ctx.send(f"✅ Correct, {ctx.author.mention}!")
                else:
                    await ctx.send(f"❌ Wrong! The correct answer was **{correct_answer}**.")
            except:
                await ctx.send(f"⏰ Time's up! The answer was **{correct_answer}**.")
                
    @commands.hybrid_command(name="fact", description="Get a random, possibly useless, fact!")
    async def fact(self, ctx: commands.Context):
        await ctx.defer()
        
        # We use 'random' for a new fact every time
        url = "https://uselessfacts.jsph.pl/api/v2/facts/random"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    fact_text = data.get('text')
                    source = data.get('source', 'Unknown')
                    
                    embed = discord.Embed(
                        title="💡 Did you know?",
                        description=f"### {fact_text}",
                        color=discord.Color.random() # Makes every fact feel a bit different!
                    )
                    embed.set_footer(text=f"Source: {source}")
                    
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ I couldn't find a fact right now. Try again in a moment!")
                    
    @commands.hybrid_command(name="hangman", description="Play a game of hangman!")
    async def hangman(self, ctx: commands.Context):
        target_word = self.rw.word(include_parts_of_speech=["nouns"], word_min_length=5, word_max_length=10)
        guessed_letters = []
        tries = 0
        max_tries = 6

        def get_display_word():
            return " ".join([letter if letter in guessed_letters else "_" for letter in target_word])

        # Initial Message
        embed = discord.Embed(title="Hangman Game", color=discord.Color.blue())
        embed.description = f"{STAGES[tries]}\n\n**Word:** `{get_display_word()}`\n**Guessed:** None"
        game_msg = await ctx.send(embed=embed)

        while tries < max_tries:
            try:
                # Wait for a message from the user who started the game
                message = await ctx.bot.wait_for(
                    "message",
                    check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                    timeout=30.0
                )
            except asyncio.TimeoutError:
                return await ctx.send(f"Game timed out! The word was **{target_word}**.")

            guess = message.content.lower()
            
            # Validation
            if len(guess) != 1 or not guess.isalpha():
                continue # Ignore invalid inputs
            
            await message.delete() # Keep the channel clean

            if guess in guessed_letters:
                continue
            
            guessed_letters.append(guess)

            if guess not in target_word:
                tries += 1
            
            # Update Embed
            display = get_display_word()
            embed.description = f"{STAGES[tries]}\n\n**Word:** `{display}`\n**Guessed:** {', '.join(guessed_letters)}"
            
            if "_" not in display:
                embed.title = "You Won! 🎉"
                embed.color = discord.Color.green()
                await game_msg.edit(embed=embed)
                return

            await game_msg.edit(embed=embed)

        # Game Over
        embed.title = "Game Over! 💀"
        embed.color = discord.Color.red()
        embed.description = f"{STAGES[6]}\n\nThe word was: **{target_word}**"
        await game_msg.edit(embed=embed)
        
    @commands.hybrid_command(name="history", description="On this day in history...")
    async def history(self, ctx: commands.Context):
        now = datetime.datetime.now()
        month = now.strftime("%m")
        day = now.strftime("%d")
        
        url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{month}/{day}"
        
        # FIX: Provide a specific User-Agent string
        # Replace 'YourUsername' with your actual Discord tag
        headers = {
            'User-Agent': 'DiscordHistoryBot/1.0 (contact: YourUsername#0000; mail: your@email.com)'
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    events = data.get("events", [])
                    
                    if not events:
                        return await ctx.send("No events found for today!")

                    event = random.choice(events)
                    year = event.get("year")
                    text = event.get("text")
                    
                    embed = discord.Embed(
                        title=f"On This Day: {now.strftime('%B %d')}, {year}",
                        description=text,
                        color=discord.Color.gold()
                    )
                    
                    # Check for a thumbnail image
                    pages = event.get("pages", [])
                    if pages and "thumbnail" in pages[0]:
                        embed.set_thumbnail(url=pages[0]["thumbnail"]["source"])
                    
                    await ctx.send(embed=embed)
                elif response.status == 403:
                    await ctx.send("Wikipedia blocked the request (403). Try updating your User-Agent string!")
                else:
                    await ctx.send(f"Failed to fetch history. (Error: {response.status})")
                    
    @commands.hybrid_command(name="number-guess", description="Guess the number from 1-100!")
    async def guessnumber(self, ctx):
        number = random.randint(1, 100)
        attempts = 0
        
        await ctx.send("I'm thinking of a number between **1 and 100**. Can you guess it?")

        def check(m):
            # Check that the message is from the same user, same channel, and is a number
            return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()

        while True:
            try:
                # Wait 30 seconds for each guess
                msg = await self.client.wait_for("message", check=check, timeout=30.0)
                guess = int(msg.content)
                attempts += 1

                if guess < number:
                    await ctx.send(f"🔺 **Higher!** (Attempt {attempts})")
                elif guess > number:
                    await ctx.send(f"🔻 **Lower!** (Attempt {attempts})")
                else:
                    # They guessed it!
                    embed = discord.Embed(
                        title="Correct! 🎉",
                        description=f"You found the number **{number}** in **{attempts}** attempts!",
                        color=discord.Color.green()
                    )
                    await ctx.send(embed=embed)
                    break # Exit the loop

            except asyncio.TimeoutError:
                return await ctx.send(f"⌛ Time's up! The number was **{number}**.")
         
        
        
async def setup(client):
    await client.add_cog(Fun(client=client))