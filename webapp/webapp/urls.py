from django.contrib import admin
from django.urls import path

# Mengimpor views dari berbagai aplikasi dan memberikan alias agar tidak terjadi konflik
from carina_search import views as carina_search_views
from mindmap import views as mindmap_views
from login import views as login_views
from dsadmin import views as dsadmin_views

urlpatterns = [
    path('admin/', admin.site.urls),  # URL untuk admin Django
    path('', carina_search_views.index, name='index'),  # URL untuk halaman utama
    path('mindmap/', mindmap_views.indexM, name='indexM'),  # URL untuk halaman mindmap
    path('login/', login_views.indexL, name='indexL'),  # URL untuk halaman login
    path('dsadmin/', dsadmin_views.indexA, name='indexA'),  # URL untuk halaman admin khusus
]
