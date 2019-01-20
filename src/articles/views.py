from django.shortcuts import render


def home(request):
    context = {
        # top articles
        # top channels
    }
    return render(request, 'index.html', {})
