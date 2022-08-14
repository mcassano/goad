from __future__ import print_function
from slack import WebClient
from slack.errors import SlackApiError
import steam.webapi
from steam.webapi import WebAPI
import json
from types import SimpleNamespace as Namespace
import os
import pickle
from .models import Game, GameSession, Person, GameSessionPerson
from datetime import datetime
from django.utils import timezone
from dotenv import load_dotenv
load_dotenv()

def checkSteamUser():
    players = Person.objects.all()

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

    for game, playerList in gamesWithPlayerLists.items():
        gameEntity = Game.objects.get(name=game)
        gameSession = GameSession.objects.filter(game=gameEntity, time_end=None).first()

        if len(playerList) > 1:
            if not gameSession:
                gameSession = GameSession(game=gameEntity, time_started=timezone.now())
                gameSession.save()

        if len(playerList) > 1:
            for player in playerList:
                personEntity = Person.objects.get(steam_id=player)
                gameSessionPerson = GameSessionPerson.objects.get_or_create(person=personEntity, game_session=gameSession, defaults={"time_joined": timezone.now()})

    gameSessions = GameSession.objects.filter(time_end=None)
    for gameSession in gameSessions:
        game = gameSession.game
        playerListForGame = gamesWithPlayerLists[game.name]
        if len(playerListForGame) < 2:
            gameSession.time_end = timezone.now()
            gameSession.save()

            for gameSessionPerson in GameSessionPerson.objects.filter(game_session=gameSession):
                gameSessionPerson.time_left = timezone.now()
                gameSessionPerson.save()

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
    steam_ids = []
    for player in players:
        steam_ids.append(player.steam_id)

    api = steam.webapi.WebAPI(key=os.environ['STEAM_KEY'],
                          format='json',
                          raw='false',
                          https=True,
                          http_timeout=60,
                          apihost='api.steampowered.com',
                          auto_load_interfaces=True
                          )
    data = api.call('ISteamUser.GetPlayerSummaries', steamids=",".join(steam_ids))
    x = json.loads(data, object_hook=lambda d: Namespace(**d))
    return x

def extractGameState(response):
    currentGameState = {}
    for player in response.players:
        gameName = None
        try:
            gameName = player.gameextrainfo
        except:
            pass
        if gameName:
            currentGameState[player.steamid] = gameName
    return currentGameState

def readSteamGamesAndExtractGameStateFromPlayers(players):
    response = readSteamGamesFromPlayers(players)
    response = response.response
    createNewGames(response)
    currentGameState = extractGameState(response)
    return currentGameState

def createNewGames(response):
    games = {}
    for player in response.players:
        game = None
        try:
            game = player.gameextrainfo
        except:
            pass
        if game and not (game in games.keys()):
            games[game] = player.gameid

    if games:
        for game, gameid in games.items():
            Game.objects.update_or_create(steam_app_id=gameid, defaults={"name": game})
