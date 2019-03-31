from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth
from django.core.exceptions import ObjectDoesNotExist
from .models import *


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['pswd']
        nextPath = request.GET.get('next','/')
        try:
            user = auth.authenticate(username=username,password=password)
            if user is not None:
                auth.login(request,user)
                return redirect('%s' % nextPath)
            else:
                err = "Password didn't match"
                return render(request,"login.html",{"err":err,})
        except ObjectDoesNotExist:
            err = "Invalid User"
            return render(request,"login.html",{"err":err,})
    return render(request,"login.html",{})

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        pswd = request.POST['pswd']
        confirm_pswd = request.POST['pswd2']
        email = request.POST['email']
        if confirm_pswd == pswd:
            User.objects.create_user(username=username,email=email,password=pswd,first_name=first_name,last_name=last_name)
            return redirect('login')
        return render(request, 'signup.html', {'err':'Password didnot match'})
    return render(request, 'signup.html', {})

def home(request):
    if not request.user.is_authenticated:
        return redirect('/login/?next=%s' % request.path)
    tasks = Task.objects.filter(creator=request.user).order_by('-date')
    my_tasks = {}
    for task in tasks:
        team = task.team
        team_name = None
        if team is not None:
            team_name = Team.objects.get(id=team.id).team_name
        task_title = task.title
        assigned_to = []
        for user in task.assigned_to.all():
            assigned_to.append(user.username)
        description = task.description
        task_url = task.task_url
        dictionary = {'title':task_title,'assignees':assigned_to, 'description':description, 'url':task_url}
        if team_name == None:
            team_name = "Under No Team"
        if not team_name in my_tasks:
            my_tasks[team_name] = []
        my_tasks[team_name].append(dictionary)
    other_tasks = {}
    team = Team.objects.filter(creator=request.user)
    teams = []
    for x in team:
        teams.append(x.id)
    team = Team.objects.filter(members=request.user)
    for x in team:
        teams.append(x.id)
    for x in teams:
        othertasks = Task.objects.filter(team=x).order_by('-date')
        if othertasks:
            for othertask in othertasks:
                if othertask.creator != request.user:
                    team_name = Team.objects.get(id=x).team_name
                    task_title = othertask.title
                    assigned_to = []
                    for user in othertask.assigned_to.all():
                        assigned_to.append(user.username)
                    description = othertask.description
                    task_url = othertask.task_url
                    dictionary = {'title': task_title, 'assignees': assigned_to, 'description':description, 'url': task_url}
                    if not team_name in other_tasks:
                        other_tasks[team_name] = []
                    other_tasks[team_name].append(dictionary)
    all_task = {'my_tasks':my_tasks,'other_tasks' : other_tasks}
    return render(request, "home.html", {'all_task' : all_task})

def createTask(request):
    if not request.user.is_authenticated:
        return redirect('/login/?next=%s' % request.path)
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        team_name = request.POST['team_name']
        assignee = request.POST.get('assignee','')
        status = request.POST['status']
        assigned = []
        invalid = []
        if team_name != 'No Team' and assignee != '':
            lst = assignee.split(',')
            for x in lst:
                x=x.strip()
                if x != '':
                    if Team.objects.filter(members=User.objects.get(username=x).id,team_name=team_name).exists():
                        assigned.append(x)
                    elif Team.objects.filter(creator=User.objects.get(username=x).id,team_name=team_name).exists():
                        assigned.append(x)
                    else:
                        invalid.append(x)
        else:
            assigned.append(request.user)
        if invalid:
            return render(request,"createtask.html",{'members':invalid})
        task_url = title.replace(" ","_")
        try:
            if not Task.objects.filter(title=title).exists():
                task = Task(title=title,description=description,creator=request.user,status=status,task_url="/task/"+task_url+"/")
                if team_name != 'No Team':
                    task.team = Team.objects.get(team_name=team_name)
                task.save()
            else:
                return render(request,"createtask.html",{'err':'Task of this title has already been created. Try to choose another title'})
            for member in assigned:
                for x in User.objects.filter(username=member):
                    task.assigned_to.add(x.id)
        except Exception as e:
            return render(request,"createtask.html",{'err':str(e)})
    team = Team.objects.filter(creator=request.user)
    teams = []
    for x in team:
        teams.append(x.team_name)
    team = Team.objects.filter(members=request.user)
    for x in team:
        teams.append(x.team_name)
    return render(request,"createtask.html",{'teams':teams})

def teams(request):
    if not request.user.is_authenticated:
        return redirect('/login/?next=%s' % request.path)
    myteams = Team.objects.filter(creator=request.user)
    my_teams = []
    for team in myteams:
        team_name = team.team_name
        owner = request.user
        team_url = team.team_url
        my_team = {'team_name':team_name,'owner':owner,'team_url':team_url}
        my_teams.append(my_team)
    otherteams = Team.objects.filter(members=request.user)
    other_teams = []
    for team in otherteams:
        team_name = team.team_name
        owner = team.creator
        team_url = team.team_url
        other_team = {'team_name': team_name, 'owner': owner, 'team_url': team_url}
        other_teams.append(other_team)
    all_teams = {'my_teams':my_teams,'other_teams':other_teams}
    return render(request, "teams.html",{'all_teams':all_teams})

def createTeam(request):
    if not request.user.is_authenticated:
        return redirect('/login/?next=%s' % request.path)
    if request.method == 'POST':
        team_name = request.POST['teamname'].strip()
        noOfuser = request.POST['no']
        lst = []
        invalid = []
        for n in range(0,int(noOfuser)):
            user = request.POST.get('member'+str(n),'')
            if user != '':
                if User.objects.filter(username=user).exists():
                    lst.append(user)
                else:
                    invalid.append(user)
        if invalid:
            return render(request,"createteam.html",{'members':invalid})
        team_url = team_name.replace(" ","_")
        try:
            if not Team.objects.filter(team_name=team_name).exists():
                team = Team(team_name=team_name, creator=request.user, team_url='/team/'+team_url+'/')
                team.save()
                for member in lst:
                    team.members.add(User.objects.get(username=member))
            else:
                return render(request,"createteam.html",{'err':'Team Name already exists'})
        except Exception as e:
            return render(request, "createteam.html", {'err' : str(e)})
    return render(request,"createteam.html",{})

def show_task(request):
    if not request.user.is_authenticated:
        return redirect('/login/?next=%s' % request.path)
    title = request.path.split('/')[2]
    title = title.replace('_',' ')
    if request.method == 'POST':
        text = request.POST['comment']
        comment = Comment(comments=text,task=Task.objects.get(title=title),commented_by=request.user)
        comment.save()
        return redirect('/task/%s/' % title)
    task = Task.objects.get(title=title)
    assigned_to = []
    for user in task.assigned_to.all():
        assigned_to.append(user.username)
    team_name = "Under No Team"
    if task.team != None:
        team_name = task.team.team_name
    editable = False
    if task.creator == request.user:
        editable = True
    comments = Comment.objects.filter(task=task).order_by('-date')
    cmments = []
    for comment in comments:
        cmments.append({'commentor':comment.commented_by.username,'date':comment.date.date(),'text':comment.comments})
    return render(request,"show_task.html",{'title':title,'creator':task.creator,'team_name':team_name,'task_url':task.task_url,'date':task.date.date(),'des':task.description,'assigned_to':assigned_to,'status':task.status,'editable':editable,'comments':cmments})

def edit_task(request):
    if not request.user.is_authenticated:
        return redirect('/login/?next=%s' % request.path)
    title = request.path.split('/')[2]
    title = title.replace('_',' ')
    if request.method == 'POST':
        task_title = request.POST['title']
        description = request.POST['description']
        team_name = request.POST['teamname']
        assignee = request.POST.get('assignee', '')
        status = request.POST['status']
        assigned = []
        invalid = []
        if team_name != 'No Team' and assignee != '':
            lst = assignee.split(',')
            for x in lst:
                x = x.strip()
                if x != '':
                    if Team.objects.filter(members=User.objects.get(username=x).id, team_name=team_name).exists():
                        assigned.append(x)
                    elif Team.objects.filter(creator=User.objects.get(username=x).id, team_name=team_name).exists():
                        assigned.append(x)
                    else:
                        invalid.append(x)
        else:
            assigned.append(request.user)
        if invalid:
            return render(request, "createtask.html", {'members': invalid})
        task_url = task_title.replace(" ", "_")
        try:
            if title == task_title:
                Task.objects.filter(title=title).update(description=description,status=status,task_url="/task/"+task_url+"/")
            elif not Task.objects.filter(title=task_title).exists():
                Task.objects.filter(title=title).update(title=task_title,description=description, status=status,task_url="/task/" + task_url + "/")
            else:
                return render(request, "edittask.html",{'err': 'Task of this title has already been created. Try to choose another title'})
            Task.objects.get(title=task_title).assigned_to.clear()
            task = Task.objects.get(title=task_title)
            for member in assigned:
                task.assigned_to.add(User.objects.get(username=member))
            return redirect('home')
        except Exception as e:
            return render(request,"edittask.html",{'err':str(e)})
    task = Task.objects.get(title=title)
    if task.creator == request.user:
        assigned_to = []
        for user in task.assigned_to.all():
            assigned_to.append(user.username)
        team_name = "Under No Team"
        if task.team != None:
            team_name = task.team.team_name
        return render(request,"edittask.html",{'title':title,'description':task.description,'teamname':team_name,'assignees':assigned_to,'status':task.status})
    return redirect('home')

def show_team(request):
    if not request.user.is_authenticated:
        return redirect('/login/?next=%s' % request.path)
    team_name = request.path.split('/')[2]
    team_name = team_name.replace('_',' ')
    if request.method == 'POST':
        teamname = request.POST['team_name'].strip()
        noOfuser = request.POST['no']
        lst = []
        invalid = []
        for n in range(0, int(noOfuser)):
            user = request.POST.get('member' + str(n), '')
            if user != '':
                if User.objects.filter(username=user).exists():
                    lst.append(user)
                else:
                    invalid.append(user)
        if invalid:
            return render(request, "show_team.html", {'members': invalid})
        team_url = teamname.replace(" ", "_")
        try:
            if teamname == team_name:
                pass
            elif not Team.objects.filter(team_name=teamname).exists():
                Team.objects.filter(team_name=team_name).update(team_name=teamname, team_url='/team/' + team_url + '/')
            else:
                return render(request, "show_team.html", {'err': 'Team Name already exists'})
            Team.objects.get(team_name=teamname).members.clear()
            team = Team.objects.get(team_name=teamname)
            for member in lst:
                team.members.add(User.objects.get(username=member))
            return redirect('home')
        except Exception as e:
            return render(request, "show_team.html", {'err' : str(e)})
    team = Team.objects.get(team_name=team_name)
    members = []
    users = team.members.all()
    for user in users:
        members.append(user.username)
    teamname = []
    teams = Team.objects.filter(members=request.user)
    for x in teams:
        teamname.append(x.team_name)
    editable = False
    if team.creator == request.user:
        editable = True
    return render(request,"show_team.html",{'team_name': team_name, 'teams':teamname, 'creator': team.creator, 'members' : members,'editable':editable})

def profile(request):
    if not request.user.is_authenticated:
        return redirect('/login/?next=%s' % request.path)
    return render(request,"profile.html",{'user_name':request.user,'first_name':request.user.first_name,'last_name':request.user.last_name,'email':request.user.email})

def edit_profile(request):
    if not request.user.is_authenticated:
        return redirect('/login/?next=%s' % request.path)
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        User.objects.filter(username=request.user).update(first_name=first_name,last_name=last_name,email=email)
        return redirect('home')
    return render(request,"editprofile.html",{'first_name':request.user.first_name,'last_name':request.user.last_name,'email':request.user.email})

def contact(request):
    return render(request,"contact.html")

def logout(request):
    auth.logout(request)
    return redirect('login')
