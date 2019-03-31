from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    title_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=500,unique=True)
    description = models.TextField()
    creator = models.ForeignKey(User,on_delete=models.CASCADE)
    assigned_to = models.ManyToManyField(User,related_name='assignees')
    status = models.CharField(max_length=100)
    team = models.ForeignKey('Team',null=True,on_delete=models.SET_NULL)
    date = models.DateTimeField(auto_now=True)
    task_url = models.CharField(max_length=400)


class Team(models.Model):
    team_name = models.CharField(max_length=100,unique=True)
    creator = models.ForeignKey(User,on_delete=models.CASCADE)
    members = models.ManyToManyField(User,related_name='members')
    team_url = models.CharField(max_length=400)


class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    comments = models.TextField()
    date = models.DateTimeField(auto_now=True)
    task = models.ForeignKey(Task,on_delete=models.CASCADE)
    commented_by = models.ForeignKey(User,on_delete=models.CASCADE)