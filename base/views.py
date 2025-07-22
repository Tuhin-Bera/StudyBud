from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Room, Topic, Message, User  # this "User"  is a customized User model 
from .forms import RoomForm, UserForm, MyUserCreationForm
# from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.forms import UserCreationForm






# Create your views here.


## login page
def login_page(request):
    
    page = 'login'
    # Redirect if user is already authenticated
    if request.user.is_authenticated:   
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')
            
        # Authenticate user
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or Password does not exists')
        
    context = {'page':page}
    return render(request, 'base/login_register.html', context)



## logout user
def logout_user(request):
    logout(request)             ## using predifed logout model provided by django
    return redirect('home')


## register page
def register_page(request):
    form  = MyUserCreationForm()
    
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registration')
        
    return render(request, 'base/login_register.html', {'form':form})


## home 
def home(request):
    # Get search query
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    # Filter rooms based on query
    rooms = Room.objects.filter(Q(topic__name__icontains = q)
                                | Q(name__icontains = q)
                                | Q(description__icontains=q))
    
    topics = Topic.objects.all()[0:5]     # Show top 5 topics
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    
    context  = {'rooms': rooms, 'topics':topics, 'room_count':room_count, 'room_messages':room_messages}
    return render(request, 'base/home.html', context)



## room details 
def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()    # All messages in the room
    participants = room.participants.all()    # All participants
    
    if request.method == 'POST':
        # Create new message
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)   # Add user to participants
        return redirect('room', pk=room.id)
    
    context  = {'room': room, 'room_messages':room_messages, 'participants':participants}
    return render(request, 'base/room.html', context)



## user profile 
def user_profile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user':user, 'rooms':rooms, 'room_messages':room_messages, 'topics':topics}
    return render(request, 'base/profile.html', context)


## create room 
@login_required(login_url='login')
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        
        # Create a new room
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description')
        )
        # Create a new room with the topic
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     room.save()
        return redirect('home')       #sending the data to home view
    
    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)



## update existing room 
@login_required(login_url='login')
def update_room(request, pk):
    room = Room.objects.get(id = pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    
    # Check if the logged-in user is the host
    if request.user != room.host:
        return HttpResponse('You are not allowed here, boy')
    
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        form = RoomForm(request.POST, instance=room)
        room.name = request.POST.get('name')
        room.name = topic
        room.description = request.POST.get('description')
        room.save()
        
        # if form.is_valid():
        #     form.save()
        
        return redirect('home')
    
    context = {'form':form, 'topics':topics, 'room':room}
    return render(request, 'base/room_form.html', context)



## delete room 
@login_required(login_url='login')
def delete_room(request, pk):
    room = Room.objects.get(id = pk)
    
    # Only host can delete the room
    if request.user != room.host:
        return HttpResponse('You are not allowed here, boy')
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':room})


## delete meassage  
@login_required(login_url='login')
def delete_message(request, pk):
    message = Message.objects.get(id = pk)
    
    # Only message owner can delete
    if request.user != message.user:
        return HttpResponse('You are not allowed here, boy')
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':message})






## update user 
@login_required(login_url='login')
def update_user(request):
    user = request.user
    form = UserForm(instance=user)
    
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES,   instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_profile', pk=user.id)
    
    return render(request, 'base/update_user.html', {'form':form})


## topic listing 
def topics_page(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''       
    topics = Topic.objects.filter(name__icontains=q)
    
    context = {'topics': topics}
    return render(request, 'base/topics.html', context)


## activity feed page
def activity_page(request):
    room_messages = Message.objects.all()      # All messages site-wide
    context = {'room_messages': room_messages}
    return render(request, 'base/activity.html', context)





 
