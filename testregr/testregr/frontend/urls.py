from django.urls import path,re_path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('loadview',views.lookup),
    path('getsubtotals',views.lookup_subtotals),
]