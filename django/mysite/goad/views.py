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
    #slack_client.chat_postMessage(
    #    channel='#goad',
    #    text="@notmarkmiranda for how long and when shall I begin?")
    return HttpResponse("hi slack")

def steamCheckUser(request):
    return HttpResponse("(%s) (%s) (%s)" %(personaname, game, gameextrainfo))


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
    print(team_id)
    peopleInThisSlack = Person.objects.filter(team_id=team_id)
    games = {
        
    }
        
    for person in peopleInThisSlack:
        data = steam.webapi.webapi_request(f'http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={os.environ["STEAM_KEY"]}&steamid={person.steam_id}&format=json')
        for game in data['response']['games']:
            appId = game['appid']
            playtime_2weeks = game['playtime_2weeks']
            name = game['name']
            
            print()
            if(appId in games.keys()):
                games[appId]["players"] = games[appId]["players"] + 1
                games[appId]["playtime_2weeks"] = games[appId]["playtime_2weeks"] + playtime_2weeks
            else:
                games[appId] = {
                    "players": 1,
                    "playtime_2weeks": playtime_2weeks,
                    "name": name,
                    "appId": appId
                }
        
        
    def sortedfunc(x):
        return x["playtime_2weeks"] * ( x["players"] * 2 )
    
    sortedGames = sorted(games.values(), key=sortedfunc, reverse=True)
    return Response(f'Looks like *{sortedGames[0]["name"]}* is the most popular game in this slack group...runner up is *{sortedGames[1]["name"]}*')
