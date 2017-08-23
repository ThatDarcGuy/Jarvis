import discord
from discord.ext import commands

from config import ConfigManager

class AdministrationCommands:
    bot = None
    configManager = None
   
    def __init__(self, bot, configMgr: ConfigManager):
        self.bot = bot
        self.configManager = configMgr
        self.bot.add_command(self.addRole)
        self.bot.add_command(self.remRole)
        self.bot.add_command(self.addRoleMgr)
        self.bot.add_command(self.remRoleMgr)
        self.bot.add_command(self.listRoleMgrs)
        self.bot.add_command(self.adminHelp)
        self.bot.add_command(self.updateConfig)
    
    @commands.command()
    @commands.guild_only()
    async def adminHelp(self, ctx):
        output = 'Available Commands:\nAdd a user to a Role: !addRole <role> <user>\nRemove a user from a Role: !remRole <role> <user>'
        if ctx.author.guild_permissions.administrator:
            output += '\nAdd a Role Manager: !addRoleMgr <role> <user>\nRemove a Role Manager: !remRoleMgr <role> <user>\nList Role Managers: !listRoleMgrs <role>'
        if self.bot.is_owner(ctx.author):
            output += "\nShut it all down: !shutdown"
        await ctx.send(output)

    @commands.command()
    @commands.guild_only()
    async def addRole(self, ctx, role: discord.Role, member: discord.Member):
        if not (
            self.configManager.isCommander(ctx.guild, role, ctx.author) or 
            (
                ctx.author.guild_permissions.manage_roles and 
                ctx.author.top_role.position >= role.position
            )
        ):
            await ctx.send("You don't have permission to add users to roles!")
            return
        await member.add_roles(role, reason='Added by ' + ctx.author.name)
        await ctx.send('Added ' + member.name + ' to @' + role.name)

    @addRole.error
    async def addRole_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            if 'Role ' in error.args[0]:
                await ctx.send('Invalid Role! Usage: !addRole <role> <user>')
                return
            if 'Member ' in error.args[0]:
                await ctx.send('Invalid Member! Usage: !addRole <role> <user>')
                return

    @commands.command()
    @commands.guild_only()
    async def remRole(self, ctx, role: discord.Role, member: discord.Member):
        if not (
            self.configManager.isCommander(ctx.guild, role, ctx.author) or 
            (
                ctx.author.guild_permissions.manage_roles and 
                ctx.author.top_role.position >= role.position
            )
        ):
            await ctx.send("You don't have permission to add users to roles!")
            return
        await member.add_roles(role, reason='Removed by ' + ctx.author.name)
        await ctx.send('Removed ' + member.name + ' from @' + role.name)

    @remRole.error
    async def remRole_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            if 'Role ' in error.args[0]:
                await ctx.send('Invalid Role! Usage: !remRole <role> <user>')
                return
            if 'Member ' in error.args[0]:
                await ctx.send('Invalid Member! Usage: !remRole <role> <user>')
                return
    
    def is_admin():
        async def predicate(ctx):
            return ctx.author.guild_permissions.administrator
        return commands.check(predicate)
    
    @commands.command()
    @commands.guild_only()
    @is_admin()
    async def addRoleMgr(self, ctx, role: discord.Role, member: discord.Member):
        self.configManager.addCommander(ctx.guild, role, member);
        self.configManager.writeConfig()
        await ctx.send(member.name + ' can now add users to ' + role.name)

    @addRoleMgr.error
    async def addRoleMgr_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            if 'Role ' in error.args[0]:
                await ctx.send('Invalid Role! Usage: !addRoleMgr <role> <user>')
                return
            if 'Member ' in error.args[0]:
                await ctx.send('Invalid Member! Usage: !addRoleMgr <role> <user>')
                return
    
    @commands.command()
    @commands.guild_only()
    @is_admin()
    async def remRoleMgr(self, ctx, role: discord.Role, member: discord.Member):
        self.configManager.remCommander(ctx.guild, role, member);
        self.configManager.writeConfig()
        await ctx.send(member.name + ' can no longer add users to ' + role.name)

    @remRoleMgr.error
    async def remRoleMgr_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            if 'Role ' in error.args[0]:
                await ctx.send('Invalid Role! Usage: !remRoleMgr <role> <user>')
                return
            if 'Member ' in error.args[0]:
                await ctx.send('Invalid Member! Usage: !remRoleMgr <role> <user>')
                return
    
    @commands.command()
    @commands.guild_only()
    @is_admin()
    async def listRoleMgrs(self, ctx, role: discord.Role):
        commanders = self.configManager.listCommanders(ctx.guild, role)
        if len(commanders) < 1:
            commanders = 'None'
        await ctx.send('Managers for @' + role.name + ":\n" + commanders)
    
    @listRoleMgrs.error
    async def listRoleMgrs_error(self, ctx, error):
        if isinstance(error,  commands.BadArgument):
            await ctx.send('Invalid Role! Usage: !listRoleMgrs <role>')
            
    @commands.command()
    @commands.guild_only()
    @is_admin()
    async def updateConfig(self,  ctx):
        self.configManager.updateServerData(ctx.guild)
        self.configManager.writeConfig()
        await ctx.send('Server Data Updated!')
