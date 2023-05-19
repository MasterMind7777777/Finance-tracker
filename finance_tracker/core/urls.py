from django.contrib import admin
from django.urls import path
from core.views import home

app_name = 'core'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
]