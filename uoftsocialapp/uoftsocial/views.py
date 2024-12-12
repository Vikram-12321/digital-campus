from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return render(request, 'uoftsocial/home.html')

def about(request):
    return render(request, 'uoftsocial/about.html')

def account(request):
    return render(request, 'uoftsocial/account.html')