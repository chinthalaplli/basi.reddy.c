from django.shortcuts import render


def home(request):
    return render(request, 'main/home.html')


def profile(request):
    return render(request, 'main/profile.html')
