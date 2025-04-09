from django.contrib import admin
from django.urls import path
# from django.urls import include
from inventory import views
from django.conf import settings
from django.conf.urls.static import static

 

urlpatterns = [

    path('', views.recent_it_equipment_base, name='recent_it_equipment'),
    path('success_add/', views.success_page, name='success_add_page'),

    #desktop_details
    path('desktop_details/', views.desktop_package_base, name='desktop_details'),  # URL pattern for desktop details
    path('desktop_details_view/<int:desktop_id>/', views.desktop_details_view, name='desktop_details_view'),  # URL pattern for desktop details view
    
    #keyboard
    path('keyboard_details/', views.keyboard_details, name='keyboard_details'),
    path('success_disposed/<int:keyboard_id>/', views.keyboard_disposed, name='keyboard_disposed'),  # Add keyboard ID for disposal
    path('success_disposed_monitor/<int:monitor_id>/', views.monitor_disposed, name='monitor_disposed'),  # Add keyboard ID for disposal change this to mouse
    path('success_disposed_mouse/<int:mouse_id>/', views.mouse_disposed, name='mouse_disposed'),  # Dispose of a specific mouse
    path('success_disposed_ups/<int:ups_id>/', views.ups_disposed, name='ups_disposed'),  # Dispose of a specific ups

    #add keyboard
    path('add_keyboard/<int:package_id>/', views.add_keyboard_to_package, name='add_keyboard_to_package'),
    path('add_monitor/<int:package_id>/', views.add_monitor_to_package, name='add_monitor_to_package'),
    path('add_mouse/<int:package_id>/', views.add_mouse_to_package, name='add_mouse_to_package'),
    path('add_ups/<int:package_id>/', views.add_ups_to_package, name='add_ups_to_package'),

    # Keyboard detailed view
    path('keyboard_detailed_view/<int:keyboard_id>/', views.keyboard_detailed_view, name='keyboard_detailed_view'),

    
    # Keyboard disposal paths
    path('disposed_keyboards/', views.disposed_keyboards, name='disposed_keyboards'),


    # Mouse URLs
    path('mouse_details/', views.mouse_details, name='mouse_details'),  # View all mice
   

    # Mouse detailed view
    path('mouse_detailed_view/<int:mouse_id>/', views.mouse_detailed_view, name='mouse_detailed_view'),

    # Mouse disposal paths
    path('disposed_mice/', views.disposed_mice, name='disposed_mice'),
    

    # http://127.0.0.1:8000/add_desktop_package_with_details/
    path('add_desktop_package_with_details/', views.add_desktop_package_with_details, name='add_desktop_package_with_details'),

    #employees

    path('employees/', views.employee_list, name='employee_list'),  # Handles both GET (list) and POST (add) employees
    path('employees/update/<int:employee_id>/', views.update_employee, name='update_employee'), # update employee
    path('employees/delete/<int:employee_id>/', views.delete_employee, name='delete_employee'), # delete employee
    path('updateeee_end_user/<int:desktop_id>/', views.update_end_user, name='update_end_user'), # update user
    path('updateeee_asset_onwer/<int:desktop_id>/', views.update_asset_owner, name='update_asset_owner'), # update asset owner

    path('monitor/<int:pk>/update/', views.update_monitor, name='update_monitor'),


    # path('desktop/<int:desktop_id>/dispose/', views.dispose_desktop_view, name='dispose_desktop'),
    path('dispose-desktop/<int:desktop_id>/', views.dispose_desktop, name='dispose_desktop'),
    
    

    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

  