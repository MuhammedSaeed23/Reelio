from django.urls import path
from .import views
urlpatterns=[
    path('',views.download),
    path('download/',views.downlod_vedio),
    path('Get_vedio/<str:video_id>/',views.serve_vedio),
    path("preview/<str:video_id>/",views.preview_video),
    path("status/<str:video_id>/",views.video_status),
    path("progress/<str:uid>/",views.progresing),
    path("metadata/<str:uid>/",views.meta_view)

]
