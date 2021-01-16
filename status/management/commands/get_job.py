import telegram
import discord
import asyncio

from django.core.management.base import BaseCommand
from datetime import date, datetime, timedelta
from members.models import Group
from django.core.mail import send_mail, EmailMultiAlternatives
from framework import settings
from django.utils.html import strip_tags
from django.utils import timezone
from django.core import mail
from attendance.generateSSID import refreshSSID

from status.fetcher import GMailFetcher
from status.logger import log
from status.StatusUpdateReporter import ReportMaker
from status.models import Thread
from utilities.models import Mailer, Emails
from registration.models import Application
from members.models import Profile
from status.discord import Discord
from utilities.models import Token

to_tz = timezone.get_default_timezone()

from_email = settings.EMAIL_HOST_USER

DISCORD_BOT_TOKEN = Token.objects.values().get(key='DISCORD_BOT_TOKEN')['value']

now = datetime.now().astimezone(to_tz)
day = now.strftime("%w")
time = now.strftime("%H%M")

intents = discord.Intents.none()
intents.guilds = True
intents.guild_messages = True
intents.emojis = True
intents.members = True
discord_client = Discord(intents=intents)

def getSubject(thread, d):
    return thread.name + ' [%s]' % d.strftime('%d-%m-%Y')


#
#
# Generating Status Update Thread
#
#
def sendThreadEmail(thread):
    send_mail(
        getSubject(thread, now),
        strip_tags(thread.threadMessage),
        from_email,
        [thread.email],
        html_message=thread.threadMessage,
        fail_silently=False,
    )


#
#
# Logging Status Updates
#
#
def logStatus(thread):
    d = date.today()
    if thread.generationTime > thread.logTime:
        d = d - timedelta(days=1)

    subject = getSubject(thread, d)

    logs = GMailFetcher(subject, d.strftime("%Y-%m-%d")).logs
    members = []
    groups = Group.objects.filter(thread=thread, statusUpdateEnabled=True)
    for group in groups:
        for member in group.members.all():
            members.append(member)
    log(logs, members, thread.id)


def sendTelegramReport(thread):
    d = date.today()
    if thread.generationTime > thread.logTime:
        d = d - timedelta(days=1)

    logs = ReportMaker(d, thread.id).message
    telegramAgents = []
    groups = Group.objects.filter(thread_id=thread.id, statusUpdateEnabled=True)
    for group in groups:
        obj = [group.telegramBot, group.telegramGroup]
        if obj not in telegramAgents:
            telegramAgents.append(obj)
    
    for agent in telegramAgents:
        bot = telegram.Bot(token=agent[0])
        bot.send_message(
            chat_id=agent[1],
            text=logs,
            parse_mode=telegram.ParseMode.MARKDOWN
        )

def sendDiscordReport(thread):
    d = date.today()
    if thread.generationTime > thread.logTime:
        d = d - timedelta(days=1)

    logs = ReportMaker(d, thread.id).message
    discordAgents = []
    groups = Group.objects.filter(thread_id=thread.id, statusUpdateEnabled=True)
    for group in groups:
        obj = [group.discordGroup, group.discordChannel]
        if obj not in discordAgents:
            discordAgents.append(obj)

    for agent in discordAgents:
        discord_client.sendReport(agent,logs)


def kickMembersFromGroup(thread):
    d = date.today()
    if thread.generationTime > thread.logTime:
        d = d - timedelta(days=1)

    shouldKick = ReportMaker(d, thread.id).membersToBeKicked
    telegramAgents = []
    discordAgents = []
    groups = Group.objects.filter(thread_id=thread.id, statusUpdateEnabled=True)
    for group in groups:
        discord_obj = [group.discordGroup, group.discordChannel]
        obj = [group.telegramBot, group.telegramGroup]
        if obj not in telegramAgents:
            telegramAgents.append(obj)

        if discord_obj not in discordAgents:
            discordAgents.append(discord_obj)

    for agent in telegramAgents:
        bot = telegram.Bot(token=agent[0])
        for user in shouldKick:
            profile = Profile.objects.get(user=user)
            try:
                bot.kick_chat_member(chat_id=agent[1], user_id=profile.telegram_id)
                bot.unban_chat_member(
                    chat_id=agent[1],
                    user_id=profile.telegram_id
                )
            except:
                pass

    for discordAgent in discordAgents:
        for user in shouldKick:
            profile = Profile.objects.get(user=user)
            try:
                discord_client.kickMember(discord_obj,profile.discord_id)
            except:
                pass


class Command(BaseCommand):
    help = 'Runs all tasks of CMS required to be done at the moment'

    def handle(self, *args, **options):

        # get all groups
        groups = Group.objects.all()

        # for each group
        for group in groups:

            # If the group has attendance enabled
            if group.attendanceEnabled:
                # generate new SSID name if refreshing is required
                refreshSSID(group.attendanceModule)

        threads = Thread.objects.filter(isActive=True)
        for thread in threads:
            if thread.generationTime == time:
                sendThreadEmail(thread)
            if thread.logTime == time:
                logStatus(thread)
                if thread.enableTelegramGroupNotification:
                    sendTelegramReport(thread)
                if thread.enableDiscordGroupNotification:
                    sendDiscordReport(thread)
                if thread.allowBotToKick:
                    kickMembersFromGroup(thread)

        mails = Mailer.objects.all()
        for m in mails:
            if date.today() == m.generationEmailDate and m.generationEmailTime == time:
                emails = []
                if m.form is not None:
                    applications = Application.objects.values().filter(form=m.form)
                else:
                    applications = Emails.objects.values().filter(category=m.category)
                for application in applications:
                    email = EmailMultiAlternatives(
                        m.subject,
                        strip_tags(m.threadMessage),
                        from_email,
                        [application['email']],
                    )
                    email.attach_alternative(m.threadMessage, "text/html")
                    emails.append(email)
                connection = mail.get_connection()
                return connection.send_messages(emails)
        
        if thread.logTime == time:
            discord_client.run(DISCORD_BOT_TOKEN)
