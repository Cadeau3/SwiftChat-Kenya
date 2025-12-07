from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, Message
from .forms import SignUpForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required

def index(request):
    return redirect("room_list")

def room_list(request):
    rooms = Room.objects.all()
    return render(request, "chat/room_list.html", {"rooms": rooms})

@login_required
def room_detail(request, room_name):
    room = get_object_or_404(Room, name=room_name)
    messages = room.messages.select_related("user").all()[:50]
    return render(request, "chat/room_detail.html", {"room": room, "messages": messages})

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect("room_list")
    else:
        form = SignUpForm()
    return render(request, "chat/signup.html", {"form": form})
