from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/slack', views.slack, name='slack'),
    path('api/steam', views.steamCheckUser, name='steamCheckUser'),
    path('slacklink', views.slacklink, name="slacklink"),
    path('potentialGames', views.potentialGames, name="potentialGames")
]