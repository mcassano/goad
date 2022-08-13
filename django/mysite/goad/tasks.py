from __future__ import print_function
from slack import WebClient
from slack.errors import SlackApiError
import steam.webapi
from steam.webapi import WebAPI
import json
from types import SimpleNamespace as Namespace
import os
import pickle
from dotenv import load_dotenv
load_dotenv()

def checkSteamUser():
    players = ['76561197977971907', '76561197960270543']

    priorGameState = readGameFromMemory()
    
    currentGameState = readSteamGamesAndExtractGameStateFromPlayers(players)

    gamesWithPlayerLists = {}
    for game in currentGameState.values():
        playersInGame = []
        for player, playerGame in currentGameState.items():
            if game == playerGame:
                playersInGame.append(player)
        playersInGame.sort()
        gamesWithPlayerLists[game] = playersInGame

    for game, currentPlayerList in gamesWithPlayerLists.items():
        priorPlayerList = []
        try:
            priorPlayerList = priorGameState[game]
        except:
            priorPlayerList = []

        if priorPlayerList == currentPlayerList:
            print("player lists same %s: (%s) (%s)" % (game, priorPlayerList, currentPlayerList))
        else:
            print("something different %s: (%s) (%s)" % (game, priorPlayerList, currentPlayerList))
            

    with open('memory.pickle', 'wb') as handle:
        pickle.dump(gamesWithPlayerLists, handle, protocol=pickle.HIGHEST_PROTOCOL)

def readGameFromMemory():
    try:
        with open('memory.pickle', 'rb') as handle:
            game = pickle.load(handle)
    except:
        game = {}
        with open('memory.pickle', 'wb') as handle:
            pickle.dump(game, handle, protocol=pickle.HIGHEST_PROTOCOL)
    return game

def readSteamGamesFromPlayers(players):
    api = steam.webapi.WebAPI(key=os.environ['STEAM_KEY'],
                          format='json',
                          raw='false',
                          https=True,
                          http_timeout=60,
                          apihost='api.steampowered.com',
                          auto_load_interfaces=True
                          )
    data = api.call('ISteamUser.GetPlayerSummaries', steamids=",".join(players))
    x = json.loads(data, object_hook=lambda d: Namespace(**d))
    return x

def extractGameState(response):
    currentGameState = {}
    for player in response.players:
        gameName = None
        try:
            gameName = player.gameextrainfo
        except:
            gameName = None
        currentGameState[player.personaname] = gameName
    return currentGameState

def readSteamGamesAndExtractGameStateFromPlayers(players):
    response = readSteamGamesFromPlayers(players)
    response = response.response
    currentGameState = extractGameState(response)
    return currentGameState