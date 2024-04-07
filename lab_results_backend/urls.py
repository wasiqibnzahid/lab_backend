"""
URL configuration for lab_results_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
# from django.contrib import admin
# from django.urls import path

# urlpatterns = [
#     path('admin/', admin.site.urls),
# ]

from django.urls import path
from .views import Tumor, Ivis, PilotView, GroupView, Combined, Mice

urlpatterns = [
    path('tumor', Tumor.as_view(), name='tumor'),
    path('ivis', Ivis.as_view(), name='ivis'),
    path('pilot', PilotView.as_view(), name='pilot'),
    path('group', GroupView.as_view(), name='group'),
    path('combined', Combined.as_view(), name="view"),
    path('mouse', Mice.as_view(), name="mice")
]
