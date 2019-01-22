from django.urls import path

from .views import home, list_view, detail_view, create_view, update_view, delete_view

app_name = 'articles'

urlpatterns = [
    path('', home, name='home'),
    path('articles/', list_view, name='list'),
    path('create/', create_view, name='create'),
    path('articles/<id>/', detail_view, name='detail'),
    path('articles/<id>/update/', update_view, name='update'),
    path('articles/<id>/delete/', delete_view, name='delete')
]
