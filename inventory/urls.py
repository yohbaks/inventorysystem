from django.contrib import admin
from django.urls import path
# from django.urls import include
from inventory import views




urlpatterns = [
    path('', views.desktop_list_func, name='desktop_list_page'),
    path('add_equipment/', views.add_equipment_func, name='add_equipment_func_input'),
    path('success_add/', views.success_page, name='success_add_page'),
    path('<int:id>/', views.desktop_detailed_view, name='desktop_detailed_view'),  # Correct pattern for detailed view
]

  