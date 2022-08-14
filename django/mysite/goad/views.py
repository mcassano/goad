from __future__ import print_function
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
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

from .models import Person

def index(request):
    return HttpResponse("goad")

def slack(request):
    slack_client = WebClient(os.environ['SLACK_KEY'])
    starterbot_id = None
    slack_client.chat_postMessage(
       channel='#goad',
       text="yo")
    return HttpResponse("hi slack")

@api_view(['POST'])
def slacklink(request):
    player, created = Person.objects.update_or_create(slack_id=request.data['user_id'], defaults = {
        "slack_name":request.data['user_name'],
        "steam_id":request.data['text'],
        "team_id":request.data['team_id']})
    
    return Response("that probably worked, thanks")


@api_view(['POST'])
def potentialGames(request):
    team_id = request.data['team_id'] 
    peopleInThisSlack = Person.objects.filter(team_id=team_id)
    games = {}

    for person in peopleInThisSlack:
        data = steam.webapi.webapi_request(f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={os.environ["STEAM_KEY"]}&steamid={person.steam_id}&format=json')
        for game in data['response']['games']:
            appId = game['appid']
            playtime_forever = game['playtime_forever']
            
            if(appId in games.keys()):
                games[appId]["players"] = games[appId]["players"] + 1
                games[appId]["playtime_forever"] = games[appId]["playtime_forever"] + playtime_forever
            else:
                games[appId] = {
                    "players": 1,
                    "playtime_forever": playtime_forever,
                    "appid": appId,
                }
        
        
    def sortedfunc(x):
        return x["playtime_forever"] * ( x["players"] * 2 )
    
    sortedGames = sorted(games.values(), key=sortedfunc, reverse=True)
    topGames = []
    for game in sortedGames[:20]:
        appid = game["appid"]
        data = steam.webapi.webapi_request(f'https://store.steampowered.com/api/appdetails?appids={appid}')
        gameName = data[str(appid)]["data"]["name"]
        playTime = game["playtime_forever"]
        topGames.append("%s" % (gameName))
    return Response(f'%s' %(",".join(topGames)))
