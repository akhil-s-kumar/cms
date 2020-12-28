import discord
import asyncio

class Discord(discord.Client):
    def __init__(self, **options):
        super().__init__(**options)
        self.makeFalse()
        
    def makeFalse(self):
        self.boolSendReport = False
        self.boolKickMember = False
        self.boolAddMember = False
        self.boolCheckIfMember = False

    def sendReport(self, obj, msg):
        self.obj = obj
        self.msg = msg
        self.boolSendReport = True

    def kickMember(self, obj, user_id):
        self.obj = obj
        self.user_id = user_id
        self.boolKickMember = True

    def addMember(self, obj, user_id):
        self.obj = obj
        self.user_id = user_id
        self.boolAddMember = True

    def checkIfMember(self, obj, user_id):
        self.obj = obj
        self.boolCheckIfMember = True
        self.guild = self.get_guild(int(self.obj[0]))
        self.channel = self.get_channel(int(self.obj[1]))

        ids = [member.id for member in self.guild.members]
        
        if user_id in ids:
            return True

        return False

    async def on_ready(self):
        print(f'{self.user} has logged in')
        
        if self.boolSendReport == True:
            guild = self.get_guild(int(self.obj[0]))
            channel = self.get_channel(int(self.obj[1]))
            await channel.send(self.msg)

        if self.boolKickMember == True:
            guild = self.get_guild(int(self.obj[0]))
            channel = self.get_channel(int(self.obj[1]))
            await guild.kick(discord.Object(int(self.user_id)))

        if self.boolAddMember == True:
            guild = self.get_guild(int(self.obj[0]))
            channel = self.get_channel(int(self.obj[1]))
            await channel.send(f"Please add <@" + str(self.user_id) +">")

        await self.logout()