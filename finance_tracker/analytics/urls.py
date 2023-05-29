from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.analytics_view, name='analytics'),
    path('<int:board_id>/', views.analytics_view, name='analytics_add'),
    path('fetch-sticky-notes/', views.fetch_sticky_notes, name='fetch_sticky_notes'),
    path('create-board/', views.create_board, name='create_board'),
    path('board/<int:board_id>/sticky-notes/', views.fetch_board_sticky_notes, name='fetch_board_sticky_notes'),
]
