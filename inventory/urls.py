from django.contrib import admin
from django.urls import path
# from django.urls import include
from inventory import views
from django.conf import settings
from django.conf.urls.static import static






urlpatterns = [
    # path('', views.desktop_list_func, name='desktop_list_page'),
    path('', views.recent_it_equipment_base, name='recent_it_equipment'),
    path('add_equipment/', views.add_equipment_func, name='add_equipment_func_input'),
    path('success_add/', views.success_page, name='success_add_page'),
    path('<int:id>/', views.desktop_detailed_view, name='desktop_detailed_view'),  # Correct pattern for detailed view
    path('disposed_desktop_list/', views.disposed_desktop_list, name='disposed_desktop_list'),  # List disposed desktops
    path('dispose_desktop/<int:desktop_id>/', views.dispose_desktop, name='dispose_desktop'),  # Dispose a desktop
    path('desktop_all_detailed_view/', views.all_detailed_view, name='desktop_all_detailed_view'),

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
    

    # Add this to your urlpatterns
    
    path('add_desktop_package_with_details/', views.add_desktop_package_with_details, name='add_desktop_package_with_details'),





    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

  