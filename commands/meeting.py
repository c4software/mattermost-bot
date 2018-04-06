# -*- coding: utf-8 -*-
import os
from commands.libs.context import mark_for_awaiting_response
from commands.libs.decorators import register_as_command
from tools.libs import get_username

SLACK_TOKEN = os.environ.get("LAURENCE_TOKEN_SLACK")
SLACK_REPORT_CHANNEL = os.environ.get("SLACK_REPORT_CHANNEL", "")

TODAY_MEETING = {}

@register_as_command("meeting_report", "Affiche le rapport global", "Meeting")
def cmd_report(msg):
    message = ""
    report = TODAY_MEETING
    for username in report:
        message = "@{0}: \r\n".format(username)
        for event in report[username]:
            message += "\t\t{0} : \r\n\t\t {1}\r\n\r\n".format(event, report[username][event])

    if message:
        if SLACK_REPORT_CHANNEL != "" and SLACK_TOKEN != "":
            send_slack_message_channel(message)
            return "Message envoyé dans @{0}".format(SLACK_REPORT_CHANNEL)
        else:
            return message
    else:
        return "Personne n'a fait de report pour l'instant"

def send_slack_message_channel(content):
    from slackclient import SlackClient
    sc = SlackClient(SLACK_TOKEN)
    sc.api_call("chat.postMessage", channel=SLACK_REPORT_CHANNEL, text=content)

@register_as_command("meeting", "Enregistre une nouvelle entrée", "Meeting")
def cmd_metting(msg):
    username = get_username(msg)
    task = msg["query"]

    if username not in TODAY_MEETING:
        TODAY_MEETING[username] = {}

    if task:
        if "yesterday" not in TODAY_MEETING[username]:
            TODAY_MEETING[username]["yesterday"] = task
        elif "today" not in TODAY_MEETING[username]:
            TODAY_MEETING[username]["today"] = task

    if "yesterday" not in TODAY_MEETING[username]:
        mark_for_awaiting_response(username, "meeting")
        return "Hey! T'as fait quoi hier ?"
    elif "today" not in TODAY_MEETING[username]:
        mark_for_awaiting_response(username, "meeting")
        return "Et aujourd'hui tu prévois quoi ?"
    else:
        return "Merci !"
