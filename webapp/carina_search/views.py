from django.shortcuts import render

def index(request):
    context = {
        'nama' : 'hello world',
    }
    return render(request, 'index.html', context)