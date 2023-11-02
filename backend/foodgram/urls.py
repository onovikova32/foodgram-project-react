from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('api/', include('recipes.urls')),
    path('api/', include('api.urls')),
    path('api/users/', include('users.urls')),
    path('admin/', admin.site.urls),
    path('api/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
]
