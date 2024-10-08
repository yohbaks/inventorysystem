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
    path('disposed_desktop_list/', views.disposed_desktop_list, name='disposed_desktop_list'),  # List disposed desktops
    path('dispose_desktop/<int:desktop_id>/', views.dispose_desktop, name='dispose_desktop'),  # Dispose a desktop
    path('desktop_all_detailed_view/', views.all_detailed_view, name='desktop_all_detailed_view'),

    #desktop_details
    path('desktop_details/', views.desktop_details, name='desktop_details'),  # URL pattern for desktop details
    
    #keyboard
    path('keyboard_details/', views.keyboard_details, name='keyboard_details'),
    path('keyboard_details/<int:keyboard_id>/', views.keyboard_disposed, name='keyboard_disposed'),  # Add keyboard ID for disposal
    # Keyboard detailed view
    path('keyboard_detailed_view/<int:keyboard_id>/', views.keyboard_detailed_view, name='keyboard_detailed_view'),


    # Keyboard disposal paths
    path('disposed_keyboards/', views.disposed_keyboards, name='disposed_keyboards'),
    
    

    # #mouse
    # path('keyboard_details/', views.mouse_details, name='mouse_details'),

    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

  