from django.shortcuts import render  # Pastikan render diimpor

def indexM(request):
    context = {
        'nama': 'hello world',
    }
    return render(request, 'indexM.html', context)  
