from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('core.urls')),
    path('', include('users.urls')),
    path('transactions/', include('transactions.urls')),
    path('budgets/', include('budgets.urls')),
    path('analytics/', include('analytics.urls')),
    path('api_v1/', include('api_v1.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
