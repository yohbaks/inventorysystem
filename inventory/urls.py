from django.contrib import admin
from django.urls import path
# from django.urls import include
from inventory import views


#urls

urlpatterns = [
    path('', views.equipment_list, name='equipmentList'), # urls for summary equipment list
    path('tables/datatablescopy/', views.equipment_full_list, name='equipment_full_list'),  # url for euipment full list
    path('add_equipment/', views.add_equipment_func, name='add_equipment_func_input'), # urls for add equipment
    # path('<str:slug>/', views.equipment_detailed_slug, name='equipment_detailed_slug_input'),
]