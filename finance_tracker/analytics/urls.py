from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.analytics_view, name='analytics'),
    path('<int:board_id>/', views.analytics_view, name='analytics_add'),
    path('fetch-sticky-notes/', views.fetch_sticky_notes, name='fetch_sticky_notes'),
    path('create-or-add-to-board/', views.create_or_add_to_board, name='create_or_add_to_board'),
    path('board/<int:board_id>/sticky-notes/', views.fetch_board_sticky_notes, name='fetch_board_sticky_notes'),
    path('delete-sticky-note/<int:board_id>/', views.delete_sticky_note_from_board, name='delete_sticky_note_from_board'),
    path('<int:board_id>/save_board/', views.save_board, name='save_board'),
]
