"""
URL configuration for glucosemonitor project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from glucosemonitor.levels.views import LevelListView, LevelDetailView, LevelUploadView, MinMaxLevelView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/levels/', LevelListView.as_view(), name='level-list'),
    path('api/v1/levels/aggregates/minmax/', MinMaxLevelView.as_view(), name='level-maximum'),
    path('api/v1/levels/<int:pk>/', LevelDetailView.as_view(), name='level-detail'),
    path('api/v1/levels/upload/', LevelUploadView.as_view(), name='level-upload')
]
