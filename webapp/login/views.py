from django.shortcuts import render
from django.contrib.auth import authenticate, login

def indexL(request):

    return render(request, 'indexL.html')
