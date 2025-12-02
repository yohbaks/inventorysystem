from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from inventory import views, pm_daily_views, pm_monthly_views, pm_weekly_views, pm_monthly_weekly_export, pm_main_dashboard, pm_downtime_views, asir_views, hdr_views
from django.conf import settings
from django.conf.urls.static import static


 

urlpatterns = [

    #recent and conting in the base (combined) view
    path("", views.dashboard_pro, name="dashboard"),
    # path('', views.recent_it_equipment_and_count_base, name='recent_it_equipment'),
    path('success_add/<int:package_id>/', views.success_page, name='success_page'),
    
    
      
    

    #desktop_details
    path('desktop_details/', views.equipment_package_base, name='desktop_details'),  # URL pattern for desktop details
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
    

    path('add_equipment_package_with_details/', views.add_equipment_package_with_details, name='add_equipment_package_with_details'),
    path('check_computer_name/', views.check_computer_name, name='check_computer_name'),

    #employees

    path('employees/', views.employee_list, name='employee_list'),  # Handles both GET (list) and POST (add) employees
    path('employees/update/<int:employee_id>/', views.update_employee, name='update_employee'), # update employee
    path('employees/delete/<int:employee_id>/', views.delete_employee, name='delete_employee'), # delete employee
    path('update_end_user/<int:desktop_id>/', views.update_end_user, name='update_end_user'), # update user
    path('update_asset_owner/<int:desktop_id>/', views.update_asset_owner, name='update_asset_owner'), # update asset owner

    # Employee Profile Routes
    path('employee/<int:employee_id>/profile/', views.employee_profile_view, name='employee_profile_view'),
    path('employee/<int:employee_id>/profile/update/', views.update_employee_profile, name='update_employee_profile'),
    path('employee/<int:employee_id>/profile/regenerate-qr/', views.regenerate_employee_qr, name='regenerate_employee_qr'),
    path('e/<uuid:token>/', views.employee_assets_public, name='employee_assets_public'),

    #update desktop, monitor, mouse, ups
    path('desktop/<int:pk>/update/',    views.update_desktop, name='update_desktop'),
    path('upload_desktop_photo/<int:pk>/', views.upload_desktop_photo, name='upload_desktop_photo'),
    path('delete_desktop_photo/<int:pk>/', views.delete_desktop_photo, name='delete_desktop_photo'),
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
    path('desktop/<int:package_id>/pdf/', views.generate_desktop_pdf, name='generate_desktop_pdf'),

    #excel export
    path('export/desktop/', views.export_equipment_packages_excel, name='export_desktop_excel'),
    
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
    # path('dispose/<str:category>/<int:id>/', views.dispose_component, name='dispose_component'), #logic for disposing components
    path("disposal_history/", views.disposal_history, name="disposal_history"),

    #salvage area
    path("salvage_overview/", views.salvage_overview, name="salvage_overview"),
    path("salvaged/monitor/<int:pk>/", views.salvaged_monitor_detail, name="salvaged_monitor_detail"),
    path("salvaged/keyboard/<int:pk>/", views.salvaged_keyboard_detail, name="salvaged_keyboard_detail"),
    path("salvaged/mouse/<int:pk>/", views.salvaged_mouse_detail, name="salvaged_mouse_detail"),
    path("salvaged/ups/<int:pk>/", views.salvaged_ups_detail, name="salvaged_ups_detail"),

    path('export_salvage_excel/', views.export_salvage_excel, name='export_salvage_excel'),
    path('print_salvage_overview/', views.print_salvage_overview, name='print_salvage_overview'),

    #dashboard chart
    path('dashboard/chart/', views.dashboard_view_chart, name='dashboard_view_chart'),

    #photo upload for all components
    path('upload_monitor_photo/<int:monitor_id>/', views.upload_monitor_photo, name='upload_monitor_photo'),
    path('upload_desktop_photo/<int:desktop_id>/', views.upload_desktop_photo, name='upload_desktop_photo'),
    path('upload_keyboard_photo/<int:keyboard_id>/', views.upload_keyboard_photo, name='upload_keyboard_photo'),
    path('upload_mouse_photo/<int:mouse_id>/', views.upload_mouse_photo, name='upload_mouse_photo'),
    path('upload_ups_photo/<int:ups_id>/', views.upload_ups_photo, name='upload_ups_photo'),

    #photo upload for documents
    path('upload_document_photo/<int:document_id>/', views.upload_document_photo, name='upload_document_photo'),
    path('delete_document_photo/<int:photo_id>/', views.delete_document_photo, name='delete_document_photo'),

    #photo upload for laptop
    path('upload_laptop_photo/<int:laptop_id>/', views.upload_laptop_photo, name='upload_laptop_photo'),
    path('delete_laptop_photo/<int:laptop_id>/', views.delete_laptop_photo, name='delete_laptop_photo'),

    #profile
    path("account/profile/", views.profile_view, name="profile"),
    path("account/profile/update/", views.update_profile, name="update_profile"),
    path("account/profile/change-password/", views.change_password, name="change_password"),
    path("account/profile/regenerate-qr/", views.regenerate_user_qr, name="regenerate_user_qr"),
    path("u/<uuid:token>/", views.user_assets_public, name="user_assets_public"),

    path('check_serial_no/', views.check_serial_no, name='check_serial_no'),

    # ================================
    # LAPTOP ROUTES (new)
    # ================================
    # Laptop paths - consistently use package_id
    path("laptops/", views.laptop_list, name="laptop_list"),
    path("laptops/<int:package_id>/", views.laptop_details_view, name="laptop_details_view"),

    path('laptop/<int:package_id>/pdf/', views.generate_laptop_pdf, name='generate_laptop_pdf'),

    path("laptops/edit/<int:laptop_id>/", views.edit_laptop, name="edit_laptop"),
    # Laptop User & Document Management
    path('laptop/<int:package_id>/update-enduser/', views.update_end_user_laptop, name='update_end_user_laptop'),
    path('laptop/<int:package_id>/update-assetowner/', views.update_asset_owner_laptop, name='update_asset_owner_laptop'),
    

    path('laptop/<int:package_id>/update-documents/', views.update_documents_laptop, name='update_documents_laptop'),
    
    path("laptops/dispose/<int:package_id>/", views.dispose_laptop, name="dispose_laptop"),
    path("laptops/disposed/", views.disposed_laptops, name="disposed_laptops"),
    
    # Maintenance (Laptop)
    path("maintenance/history/laptop/<int:package_id>/", views.maintenance_history_laptop, name="maintenance_history_laptop"),
    
    
    path("maintenance/checklist/laptop/<int:package_id>/", views.checklist_laptop, name="checklist_laptop"),

    

    # ================================
    # PRINTER ROUTES
    # ================================
    path("printers/", views.printer_list, name="printer_list"),
    path("printers/<int:printer_id>/", views.printer_details_view, name="printer_details_view"),
    path("printers/dispose/<int:printer_id>/", views.dispose_printer, name="dispose_printer"),
    path("printers/disposed/", views.disposed_printers, name="disposed_printers"),

    # ================================
    # OFFICE SUPPLIES ROUTES
    # ================================
    path("office_supplies/", views.office_supplies_list, name="office_supplies_list"),
    path("office_supplies/add/", views.add_office_supplies, name="add_office_supplies"),
    path("office_supplies/<int:package_id>/", views.office_supplies_details_view, name="office_supplies_details_view"),
    path("office_supplies/dispose/<int:package_id>/", views.dispose_office_supplies, name="dispose_office_supplies"),

    path("check_monitor_sn/", views.check_monitor_sn, name="check_monitor_sn"),
    path("check_keyboard_sn/", views.check_keyboard_sn, name="check_keyboard_sn"),
    path("check_mouse_sn/", views.check_mouse_sn, name="check_mouse_sn"),
    path("check_ups_sn/", views.check_ups_sn, name="check_ups_sn"),


    # ================================
    # NOTIFICATIONS PAGE ROUTES
    # ================================
    path('notifications/', views.notifications_center, name='notifications_center'),
    
    # Notification Actions
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('notifications/<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
    path('notifications/clear-all/', views.clear_all_notifications, name='clear_all_notifications'),
    
    # API Endpoint
    path('api/notifications/count/', views.get_notification_count, name='notification_count_api'),


    # ================================
    # PM CHECKLIST SYSTEM
    # ================================
    # Main PM Dashboard (All Forms)
    path('pm/', pm_main_dashboard.pm_main_dashboard, name='pm_main_dashboard'),

    # ANNEX A - Daily PM Dashboard and Completion
    path('pm/daily/', pm_daily_views.daily_pm_dashboard, name='pm_daily_dashboard'),
    path('pm/daily/complete/<int:schedule_id>/', pm_daily_views.complete_daily_pm, name='complete_daily_pm'),
    path('pm/daily/view/<int:completion_id>/', pm_daily_views.view_daily_pm_completion, name='view_daily_pm_completion'),
    path('pm/daily/backfill/', pm_daily_views.backfill_pm_checklist, name='backfill_pm_checklist'),

    # Daily/Weekly PDF Exports (Annex A)
    path('pm/daily/export/<int:completion_id>/', pm_daily_views.export_daily_pm_pdf, name='export_daily_pm_pdf'),
    path('pm/weekly/export/', pm_daily_views.export_weekly_pm_pdf, name='export_weekly_pm_pdf'),
    path('pm/weekly/view/', pm_daily_views.weekly_pm_report_view, name='weekly_pm_report_view'),

    # ================================
    # ANNEX B - Monthly PM Dashboard and Completion
    path('pm/monthly/', pm_monthly_views.monthly_pm_dashboard, name='monthly_pm_dashboard'),
    path('pm/monthly/complete/<int:schedule_id>/', pm_monthly_views.complete_monthly_pm, name='complete_monthly_pm'),
    path('pm/monthly/export/<int:completion_id>/', pm_monthly_weekly_export.export_monthly_pm_pdf, name='export_monthly_pm_pdf'),

    # ================================
    # ANNEX C - Weekly FD/BD (4 weeks/month) PM Dashboard and Completion
    path('pm/weekly-fdbd/', pm_weekly_views.weekly_pm_dashboard, name='weekly_fdbd_dashboard'),
    path('pm/weekly-fdbd/complete/<int:schedule_id>/<int:week_number>/', pm_weekly_views.complete_weekly_pm, name='complete_weekly_pm'),
    path('pm/weekly-fdbd/export/<int:completion_id>/', pm_monthly_weekly_export.export_weekly_pm_pdf, name='export_weekly_fdbd_pdf'),

    # ================================
    # Equipment Downtime Tracking
    path('pm/downtime/log/<int:item_completion_id>/', pm_downtime_views.log_downtime_event, name='log_downtime_event'),
    path('pm/downtime/get/<int:item_completion_id>/', pm_downtime_views.get_downtime_events, name='get_downtime_events'),
    path('pm/downtime/update/<int:event_id>/', pm_downtime_views.update_downtime_event, name='update_downtime_event'),
    path('pm/downtime/analytics/', pm_downtime_views.downtime_analytics_dashboard, name='downtime_analytics'),

    # ================================
    # SNMR - Server and Network Monitoring Report
    path('reports/snmr/', views.snmr_list, name='snmr_list'),
    path('reports/snmr/create/', views.snmr_create, name='snmr_create'),
    path('reports/snmr/<int:report_id>/', views.snmr_view, name='snmr_view'),
    path('reports/snmr/<int:report_id>/edit/', views.snmr_edit, name='snmr_edit'),
    path('reports/snmr/<int:report_id>/delete/', views.snmr_delete, name='snmr_delete'),
    path('reports/snmr/<int:report_id>/export/excel/', views.snmr_export_excel, name='snmr_export_excel'),
    path('reports/snmr/<int:report_id>/finalize/', views.snmr_finalize, name='snmr_finalize'),

    # ================================
    # ASIR - Application Systems Implementation Report
    path('reports/asir/', asir_views.asir_list, name='asir_list'),
    path('reports/asir/create/', asir_views.asir_create, name='asir_create'),
    path('reports/asir/<int:report_id>/', asir_views.asir_view, name='asir_view'),
    path('reports/asir/<int:report_id>/edit/', asir_views.asir_edit, name='asir_edit'),
    path('reports/asir/<int:report_id>/delete/', asir_views.asir_delete, name='asir_delete'),
    path('reports/asir/<int:report_id>/export/excel/', asir_views.asir_export_excel, name='asir_export_excel'),
    path('reports/asir/<int:report_id>/finalize/', asir_views.asir_finalize, name='asir_finalize'),

    # ================================
    # HDR - HelpDesk Report
    path('reports/hdr/', hdr_views.hdr_list, name='hdr_list'),
    path('reports/hdr/create/', hdr_views.hdr_create, name='hdr_create'),
    path('reports/hdr/<int:report_id>/', hdr_views.hdr_view, name='hdr_view'),
    path('reports/hdr/<int:report_id>/edit/', hdr_views.hdr_edit, name='hdr_edit'),
    path('reports/hdr/<int:report_id>/jobsheet/', hdr_views.hdr_jobsheet_form, name='hdr_jobsheet_form'),
    path('reports/hdr/entry/<int:entry_id>/', hdr_views.hdr_entry_detail, name='hdr_entry_detail'),
    path('reports/hdr/<int:report_id>/delete/', hdr_views.hdr_delete, name='hdr_delete'),
    path('reports/hdr/<int:report_id>/export/excel/', hdr_views.hdr_export_excel, name='hdr_export_excel'),
    path('reports/hdr/<int:report_id>/finalize/', hdr_views.hdr_finalize, name='hdr_finalize'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
