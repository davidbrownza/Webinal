from django.shortcuts import render, redirect
from django.core.context_processors import csrf

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

@login_required(login_url="/users/login")
def index(request):
    c = {}
    c.update(csrf(request))

    return render(request, 'index.html', c)

def sign_in(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        next = request.GET.get('next', '/')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect(next)
            else:
                return render(request,  'login.html', { "error": "Login attempt failed. User account is not active. Please contact an administrator." })
        else:
            return render(request,  'login.html', { "error": "Login attempt failed. Incorrect username or password." })

@login_required(login_url="/users/login")
def sign_out(request):
    logout(request)
    return redirect('/users/login')
