from django.shortcuts import render

def index(request):
    return render(request, 'wee_app/login.html')
