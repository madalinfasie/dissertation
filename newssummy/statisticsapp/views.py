from django.shortcuts import render


def index(request):
    return render(request, 'statisticsapp/statistics.html', {'nbar': 'statistics'})
