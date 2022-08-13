from __future__ import print_function
from slack import WebClient
from slack.errors import SlackApiError
import steam.webapi
from steam.webapi import WebAPI
import json
from types import SimpleNamespace as Namespace
import os
from dotenv import load_dotenv
load_dotenv()

def checkSteamUser():
    slack_client = WebClient(os.environ['SLACK_KEY'])
    game = None
    api = steam.webapi.WebAPI(key=os.environ['STEAM_KEY'],
                          format='json',
                          raw='false',
                          https=True,
                          http_timeout=60,
                          apihost='api.steampowered.com',
                          auto_load_interfaces=True
                          )
    data = api.call('ISteamUser.GetPlayerSummaries', steamids="76561197960270543")
    x = json.loads(data, object_hook=lambda d: Namespace(**d))

    personaname = x.response.players[0].personaname
    gameextrainfo = None
    try:
        gameextrainfo = x.response.players[0].gameextrainfo
    except:
        gameextrainfo = None

    if game and gameextrainfo != game:
        slack_client.chat_postMessage(
            channel='#goad',
            text="%s now playing %s" % (personaname, gameextrainfo)
        )
        game = gameextrainfo
    elif not game and gameextrainfo:
        slack_client.chat_postMessage(
            channel='#goad',
            text="%s now playing %s" % (personaname, gameextrainfo)
        )
        game = gameextrainfo
    elif game and not x.gameextrainfo:
        slack_client.chat_postMessage(
            channel='#goad',
            text="%s has stopped playing %s" % (personaname, gameextrainfo)
        )
        game = gameextrainfo