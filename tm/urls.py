from django.urls import path
from django.conf.urls import url
from .views import *

urlpatterns = [
    path('login/',login,name='login'),
    path('signup/',signup,name='register'),
    path('',home,name='home'),
    path('createtask/',createTask,name='createtask'),
    path('teams/',teams,name='teams'),
    path('createteam/',createTeam,name='createteam'),
    path('profile/',profile,name='profile'),
    path('contact/',contact,name='contact'),
    path('logout/',logout,name='logout'),

    url(r'^team\/[a-zA-Z0-9_]+\/$',show_team),
    url(r'^task\/[a-zA-Z0-9_]+\/$',show_task),
    url(r'^task\/[a-zA-Z0-9_]+\/edit/$',edit_task),
    url(r'profile\/[a-zA-Z0-9]+\/edit/',edit_profile),
]