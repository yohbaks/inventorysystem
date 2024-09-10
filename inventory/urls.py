from django.contrib import admin
from django.urls import path
# from django.urls import include
from inventory import views
from django.conf import settings
from django.conf.urls.static import static






urlpatterns = [
    path('', views.desktop_list_func, name='desktop_list_page'),
    path('add_equipment/', views.add_equipment_func, name='add_equipment_func_input'),
    path('success_add/', views.success_page, name='success_add_page'),
    path('<int:id>/', views.desktop_detailed_view, name='desktop_detailed_view'),  # Correct pattern for detailed view
    path('desktop_all_detailed_view/', views.all_detailed_view, name='desktop_all_detailed_view'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

  