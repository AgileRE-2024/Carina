from django.shortcuts import render

def indexA(request):
    context = {
        'nama' : 'hello world',
    }
    return render(request, 'indexA.html', context)