from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from inventory import views
from django.conf import settings
from django.conf.urls.static import static

 

urlpatterns = [

    #recent and conting in the base (combined) view
    path('', views.recent_it_equipment_and_count_base, name='recent_it_equipment'),
    path('success_add/<int:desktop_id>/', views.success_page, name='success_add_page'),
    
    
      
    

    #desktop_details
    path('desktop_details/', views.desktop_package_base, name='desktop_details'),  # URL pattern for desktop details
    # path('desktop_details_view/<int:desktop_id>/', views.desktop_details_view, name='desktop_details_view'),  # URL pattern for desktop details view
    path('desktop_details_view/<int:package_id>/', views.desktop_details_view, name='desktop_details_view'),
    
    
    

    
    
    path('success_disposed/<int:keyboard_id>/', views.keyboard_disposed, name='keyboard_disposed'),  # Dispose keyboard
    path('success_disposed_monitor/<int:monitor_id>/', views.monitor_disposed, name='monitor_disposed'),  # Dispose of a specific monitor
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

    # Keyboard, mouse, monitor,  ups details page
    path('keyboard_details/', views.keyboard_details, name='keyboard_details'),
    path('mouse_details/', views.mouse_details, name='mouse_details'),  # View all mice
    path('monitor_details/', views.monitor_details, name='monitor_details'),
    path('ups_details/', views.ups_details, name='ups_details'),
    
   

    # Mouse detailed view
    path('mouse_detailed_view/<int:mouse_id>/', views.mouse_detailed_view, name='mouse_detailed_view'),

    # Mouse disposal paths
    path('disposed_mice/', views.disposed_mice, name='disposed_mice'),
    

    path('add_desktop_package_with_details/', views.add_desktop_package_with_details, name='add_desktop_package_with_details'),
    path('check_computer_name/', views.check_computer_name, name='check_computer_name'),

    #employees

    path('employees/', views.employee_list, name='employee_list'),  # Handles both GET (list) and POST (add) employees
    path('employees/update/<int:employee_id>/', views.update_employee, name='update_employee'), # update employee
    path('employees/delete/<int:employee_id>/', views.delete_employee, name='delete_employee'), # delete employee
    path('updateeee_end_user/<int:desktop_id>/', views.update_end_user, name='update_end_user'), # update user
    path('updateeee_asset_owner/<int:desktop_id>/', views.update_asset_owner, name='update_asset_owner'), # update asset owner

    #update desktop, monitor, mouse, ups
    path('desktop/<int:pk>/update/',    views.update_desktop, name='update_desktop'),
    path('monitor/<int:pk>/update/',    views.update_monitor, name='update_monitor'),
    path('keyboard/<int:pk>/update/',   views.update_keyboard, name='update_keyboard'),
    path('mouse/<int:pk>/update/',      views.update_mouse, name='update_mouse'),
    path('documents<int:pk>/update/',   views.update_documents, name='update_documents'),
    path('ups/<int:pk>/update/',        views.update_ups, name='update_ups'),


   
    path('dispose-desktop/<int:desktop_id>/', views.dispose_desktop, name='dispose_desktop'),

    #brands
    path('add_brand/', views.add_brand, name='add_brand'),
    path('edit_brand/', views.edit_brand, name='edit_brand'),
    #print
    path('desktop/<int:desktop_id>/pdf/', views.generate_desktop_pdf, name='generate_desktop_pdf'),

    #excel export
    path('export/desktop/', views.export_desktop_packages_excel, name='export_desktop_excel'),
    
    #login
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    #maintenance
  
    path('maintenance/history/<int:desktop_id>/', views.maintenance_history_view, name='maintenance_history'),
    path('maintenance/checklist/<int:desktop_id>/', views.checklist, name='checklist'),
    path('maintenance/checklist/<int:desktop_id>/<int:schedule_id>/', views.checklist, name='checklist_scheduled'),

    # path('maintenance/get_schedule_dates/<int:quarter_id>/', views.get_schedule_date_range, name='get_schedule_dates'),
    path('maintenance/get_schedule_dates/<int:quarter_id>/<int:section_id>/', views.get_schedule_date_range, name='get_schedule_dates'),



    path('maintenance/pdf/<int:pm_id>/', views.generate_pm_excel_report, name='generate_pm_pdf'), #pdf prevenitve maintenance
    
    
    #pm overview
    path('maintenance/overview/', views.pm_overview_view, name='pm_overview'),
    path('maintenance/assign_pm_schedule/', views.assign_pm_schedule, name='assign_pm_schedule'),
    path('maintenance/schedules/', views.section_schedule_list_view, name='section_schedule_list'), # section schedule list view of pm
    path('office-sections/', views.office_section_list, name='office_section_list'), #office section list view

    #disposal
    path('disposal/', views.disposal_overview, name='disposal_overview'), #overview of disposal
    path('dispose/<str:category>/<int:id>/', views.dispose_component, name='dispose_component'), #logic for disposing components

    #salvage area
    path("salvage_overview/", views.salvage_overview, name="salvage_overview"),
    path("salvaged/monitor/<int:pk>/", views.salvaged_monitor_detail, name="salvaged_monitor_detail"),
    path("salvaged/keyboard/<int:pk>/", views.salvaged_keyboard_detail, name="salvaged_keyboard_detail"),
    path("salvaged/mouse/<int:pk>/", views.salvaged_mouse_detail, name="salvaged_mouse_detail"),
    path("salvaged/ups/<int:pk>/", views.salvaged_ups_detail, name="salvaged_ups_detail"),

    #dashboard chart
    path('dashboard/chart/', views.dashboard_view_chart, name='dashboard_view_chart'),

    #photo upload for monitor
    path('upload_monitor_photo/<int:monitor_id>/', views.upload_monitor_photo, name='upload_monitor_photo'),






] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
