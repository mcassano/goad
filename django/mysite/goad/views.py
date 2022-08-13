from __future__ import print_function
from django.shortcuts import render
from django.http import HttpResponse
import os
import time
import re
from slack import WebClient
from slack.errors import SlackApiError
import steam.webapi
from steam.webapi import WebAPI
import json
from types import SimpleNamespace as Namespace
from dotenv import load_dotenv
load_dotenv()

def index(request):
    return HttpResponse("goad")

def slack(request):
    slack_client = WebClient(os.environ['SLACK_KEY'])
    starterbot_id = None
    #slack_client.chat_postMessage(
    #    channel='#goad',
    #    text="@notmarkmiranda for how long and when shall I begin?")
    return HttpResponse("hi slack")

def steamCheckUser(request):
    return HttpResponse("(%s) (%s) (%s)" %(personaname, game, gameextrainfo))