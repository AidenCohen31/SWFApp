from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('validate',views.validate),
    path('insert', views.insert),
    path('postvalidate',views.validatepost),
    path('postupdatevalidate',views.updatevalidatepost),
    path('updatevalidate', views.validateupdate),
    path('update',views.update),
    path('populate',views.populate),
    path('deletevalidate',views.deletevalidate),
    path('fileupload',views.files),
    path('filedownload',views.filedownload),
    path('inputs',views.inputs),
    path('writeinputs', views.writeinputs)
]