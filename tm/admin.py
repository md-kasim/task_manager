from django.contrib import admin
from .models import Team, Task, Comment

# Register your models here.
admin.site.register(Team)
admin.site.register(Task)
admin.site.register(Comment)