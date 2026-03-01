import discord
import datetime
from discord.ext import commands
from discord import app_commands

guild_id = 1247440062870851625

class AutoMod(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    # Role management command
    @commands.hybrid_command(name="role", description="Add or remove a role from a member")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.describe(member="The member to modify", role="The role to add or remove")
    async def role(self, ctx: commands.Context, member: discord.Member, role: discord.Role):
        if role >= ctx.guild.me.top_role:
            return await ctx.send("I can't manage that role; it's higher than mine!", ephemeral=True)

        if role in member.roles:
            try:
                await member.remove_roles(role)
                embed = discord.Embed(title="Role Removed", description=f"✅ Removed {role.mention} from {member.mention}", color=discord.Color.red())
                await ctx.send(embed=embed)
            except Exception as e:
                await ctx.send(f"Failed to remove role: {e}", ephemeral=True)
        else:
            try:
                await member.add_roles(role)
                embed = discord.Embed(title="Role Added", description=f"✅ Added {role.mention} to {member.mention}", color=discord.Color.green())
                await ctx.send(embed=embed)
            except Exception as e:
                await ctx.send(f"Failed to add role: {e}", ephemeral=True)
                
    @commands.hybrid_command(name="purge", description="Clears messages with optional filters (user or text)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, ctx: commands.Context, amount: int, member: discord.Member = None, contains: str = None):
        # 1. Defer because purging can take more than 3 seconds
        await ctx.defer(ephemeral=True)

        # 2. Validation Check
        if amount > 100 or amount < 1:
            return await ctx.send("Please pick a number between 1 and 100.")

        # 3. Define the filter logic
        def purge_check(msg):
            # If a member was specified, skip messages NOT by them
            if member and msg.author != member:
                return False
            # If text was specified, skip messages NOT containing it
            if contains and contains.lower() not in msg.content.lower():
                return False
            return True

        # 4. Execute the Purge
        try:
            # We use the purge_check function here
            deleted = await ctx.channel.purge(limit=amount, check=purge_check)
            
            # Construct a detailed success message
            details = []
            if member: details.append(f"from {member.mention}")
            if contains: details.append(f"containing '{contains}'")
            filter_str = f" {' and '.join(details)}" if details else ""

            embed = discord.Embed(
                title="Purge Successful", 
                description=f"✅ Cleared {len(deleted)} messages{filter_str}!", 
                color=discord.Color.green()
            )
            await ctx.send(embed=embed, delete_after=5)
            
        except discord.Forbidden:
            await ctx.send("I'm missing the 'Manage Messages' permission.")
        except Exception as e:
            await ctx.send(f"Something went wrong: {e}")
            
    # Slowmode command
    @commands.hybrid_command(name="slowmode", description="Set the channel slowmode")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int):
        try:
            await ctx.channel.edit(slowmode_delay=seconds)
            embed = discord.Embed(title="Slowmode Updated", description=f"Slowmode is now **{seconds}** seconds.", color=discord.Color.green())
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Failed to set slowmode: {e}", ephemeral=True)
            
    # Kick command   
    @commands.hybrid_command(name="kick", description="Kicks a member from the server")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, reason: str = "No reason provided"):
        if member.top_role >= ctx.me.top_role:
            return await ctx.send("I cannot kick this user; their role is higher than mine!", ephemeral=True)
        
        try:
            await member.kick(reason=reason)
            embed = discord.Embed(title="Member Kicked", description=f"✅ **{member.name}** has been kicked. Reason: {reason}", color=discord.Color.orange())
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Failed to kick user: {e}", ephemeral=True)
            
    # Ban command
    @commands.hybrid_command(name="ban", description="Bans a member from the server")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, reason: str = "No reason provided"):
        if member.top_role >= ctx.me.top_role:
            return await ctx.send("I cannot ban this user; their role is higher than mine!", ephemeral=True)
            
        try:
            await member.ban(reason=reason)
            embed = discord.Embed(title="Member Banned", description=f"🚫 **{member.name}** has been banned. Reason: {reason}", color=discord.Color.red())
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Failed to ban user: {e}", ephemeral=True)
            
    # Timeout command
    @commands.hybrid_command(name="timeout", description="Timeout a member for a specific duration")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, minutes: int, reason: str = "No reason provided"):
        duration = datetime.timedelta(minutes=minutes)
        try:
            await member.timeout(duration, reason=reason)
            embed = discord.Embed(title="Member Timed Out", color=discord.Color.orange())
            embed.add_field(name="User", value=member.mention, inline=True)
            embed.add_field(name="Duration", value=f"{minutes} minutes", inline=True)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Failed to timeout user: {e}", ephemeral=True)
        
async def setup(client):
    await client.add_cog(AutoMod(client=client))