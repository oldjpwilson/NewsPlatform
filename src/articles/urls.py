from django.urls import path

from .views import home, list_view, detail_view, create_view

app_name = 'articles'

urlpatterns = [
    path('', home, name='home'),
    path('articles/', list_view, name='list'),
    path('create/', create_view, name='create'),
    path('articles/<id>/', detail_view, name='detail')
]
