from django.db import models

class Person(models.Model):
    slack_id = models.CharField(primary_key=True, max_length=40)
    slack_name = models.CharField(max_length=40)
    steam_id = models.CharField(max_length=40)
    team_id = models.CharField(max_length=40)
    def __str__(self):
        return '{} - {}'.format(self.steam_id, self.slack_name)

class Game(models.Model):
    name = models.CharField(max_length=300)
    steam_app_id = models.CharField(max_length=20)
    def __str__(self):
        return '{} - {}'.format(self.name, self.steam_app_id)

class GameSession(models.Model):
    time_started = models.DateTimeField()
    time_end = models.DateTimeField(null=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    def __str__(self):
        return '{} - {} - {}'.format(self.game.name, self.time_started, self.time_end)

class GameSessionPerson(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE)
    time_joined = models.DateTimeField()
    time_left = models.DateTimeField(null=True)
    def __str__(self):
        return '{} - {} - {}'.format(self.person.steam_id, self.game_session.game.name, self.time_left)
