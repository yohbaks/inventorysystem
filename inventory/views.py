from django.shortcuts import render, redirect
from django.contrib import messages

from inventory.models import Desktop_Package, DesktopDetails, KeyboardDetails, DisposedKeyboard, MouseDetails, MonitorDetails, UPSDetails, DisposedMouse, DisposedMonitor, UserDetails, DisposedUPS
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse # sa disposing ni sya sa desktop
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction


 


# Create your views here.
##############################################################################
# code for the list in the homepage
def desktop_list_func(request):
    

    # Get all equipment except the disposed one.
    desktop_list = DESKTOPPACKAGE.objects.filter(is_disposed=False)

    # Count the total number of equipment
    desktop_count = desktop_list.count()

    # Render the list of equipment and the count to the template
    return render(request, 'base.html', {'desktop_List': desktop_list, 'desktop_count': desktop_count})
    

##############################################################################
#add equipment functions

# def add_equipment_func(request):
    if request.method == 'POST':
        equipment_type = request.POST.get('name_input', '')
        nameany = request.POST.get('name_input', '')
        serialany = request.POST.get('desktop_serial_input', '')
        brandnameany = request.POST.get('desktop_brand_input', '')
        modelany = request.POST.get('desktop_model_input', '')
        processorany = request.POST.get('desktop_processor_input', '')
        memoryany = request.POST.get('desktop_memory_input', '')
        driveany = request.POST.get('desktop_drive_input', '')
        desktop_gpu_input_any = request.POST.get('desktop_gpu_input', '') #desktop_gpu_input
        desktop_gpusize_input_any = request.POST.get('desktop_gpusize_input', '') #desktop_gpusize_input
        
        desktop_os_input_any = request.POST.get('desktop_os_input', '') #desktop_os_input
        desktop_office_input_any = request.POST.get('desktop_office_input', '') #desktop_office_input
        desktop_OSkeys_input_any = request.POST.get('desktop_OSkeys_input', '') #desktop_OSkeys_input
        desktop_Officekeys_input_any = request.POST.get('desktop_Officekeys_input', '') #desktop_Officekeys_input
        monitor_serial_input_any = request.POST.get('monitor_serial_input', '') #monitor_serial_input
        monitor_brand_input_any = request.POST.get('monitor_brand_input', '') #monitor_brand_input
        monitor_model_input_any = request.POST.get('monitor_model_input', '') #monitor_model_input
        monitor_size_input_any = request.POST.get('monitor_size_input', '') #monitor_size_input
        keyboard_serial_input_any = request.POST.get('keyboard_serial_input', '') #keyboard_serial_input
        keyboard_brand_input_any = request.POST.get('keyboard_brand_input', '') #keyboard_brand_input
        keyboard_model_input_any = request.POST.get('keyboard_model_input', '') #keyboard_model_input
        mouse_serial_input_any = request.POST.get('mouse_serial_input', '') #mouse_serial_input
        mouse_brand_input_any = request.POST.get('mouse_brand_input', '') #mouse_brand_input
        mouse_model_input_any = request.POST.get('mouse_model_input', '') #mouse_model_input
        ups_serial_input_any = request.POST.get('ups_serial_input', '') #ups_serial_input
        ups_brand_input_any = request.POST.get('ups_brand_input', '') #ups_brand_input
        ups_model_input_any = request.POST.get('ups_model_input', '') #ups_model_input
        asset_owner_input_any = request.POST.get('asset_owner_input', '') #asset_owner_input
        designation_Asset_input_any = request.POST.get('designation_Asset_input', '') #designation_Asset_input
        asset_section_input_any = request.POST.get('asset_section_input', '') #asset_section_input
        end_user_input_any = request.POST.get('end_user_input', '') #end_user_input
        enduser_designation_input_any = request.POST.get('enduser_designation_input', '') #enduser_designation_input
        enduser_section_input_any = request.POST.get('enduser_section_input', '') #aenduser_section_input
        par_number_input_any = request.POST.get('par_number_input', '') #par_number_input
        property_number_input_any = request.POST.get('property_number_input', '') #property_number_input
        acquisition_type_input_any = request.POST.get('acquisition_type_input', '') #acquisition_type_input
        value_desktop_input_any = request.POST.get('value_desktop_input', '') #value_desktop_input
        date_received_input_any = request.POST.get('date_received_input', '') #date_received_input
        date_inspected_input_any = request.POST.get('date_inspected_input', '') #date_inspected_input
        supplier_name_input_any = request.POST.get('supplier_name_input', '') #supplier_name_input
        status_desktop_input_any = request.POST.get('status_desktop_input', '') #status_desktop_input
        computer_name_input_any = request.POST.get('computer_name_input', '') #computer_name_input
        image = request.FILES.get('desktop_image_input')
        
        if equipment_type == 'Desktop':
            if len(nameany) < 2 or len(serialany) < 1 or len(brandnameany) < 2 or len(modelany) < 2 or len(processorany) < 2 or len(memoryany)<2 or len(desktop_gpu_input_any)<2:
                messages.error(request, "Please fill out all required fields.")
                # Render the form again with error messages and existing data
                return render(request, 'add_equipment.html', {
                    'equipment_type': equipment_type,
                    'nameany': nameany,
                    'serialany': serialany,
                    'brandnameany': brandnameany,
                    'modelany': modelany,
                    'processorany' : processorany,
                    'memoryany' : memoryany,
                    'driveany' : driveany,
                    'image' : image,
                    'desktop_gpu_input_any' : desktop_gpu_input_any,
                    'desktop_gpusize_input_any' : desktop_gpu_input_any,
                    'desktop_office_input_any' : desktop_gpu_input_any,
                    'desktop_OSkeys_input_any' : desktop_gpu_input_any,
                    'desktop_Officekeys_input_any' : desktop_gpu_input_any,
                    'monitor_serial_input_any' : desktop_gpu_input_any,
                    'monitor_brand_input_any' : desktop_gpu_input_any,
                    'monitor_model_input_any' : desktop_gpu_input_any,
                    'monitor_size_input_any' : desktop_gpu_input_any,
                    'keyboard_serial_input_any' : desktop_gpu_input_any,
                    'keyboard_brand_input_any' : desktop_gpu_input_any,
                    'keyboard_model_input_any' : desktop_gpu_input_any,
                    'mouse_serial_input_any' : desktop_gpu_input_any,
                    'mouse_brand_input_any' : desktop_gpu_input_any,
                    'mouse_model_input_any' : desktop_gpu_input_any,
                    'ups_serial_input_any' : desktop_gpu_input_any,
                    'ups_model_input_any' : desktop_gpu_input_any,
                    'asset_owner_input_any' : desktop_gpu_input_any,
                    'designation_Asset_input_any' : desktop_gpu_input_any,
                    'asset_section_input_any' : desktop_gpu_input_any,
                    'end_user_input_any' : desktop_gpu_input_any,
                    'enduser_designation_input_any' : desktop_gpu_input_any,
                    'enduser_section_input_any' : desktop_gpu_input_any,
                    'par_number_input_any' : desktop_gpu_input_any,
                    'property_number_input_any' : desktop_gpu_input_any,
                    'acquisition_type_input_any' : desktop_gpu_input_any,
                    'value_desktop_input_any' : desktop_gpu_input_any,
                    'date_received_input_any' : desktop_gpu_input_any,
                    'date_inspected_input_any' : desktop_gpu_input_any,
                    'supplier_name_input_any' : desktop_gpu_input_any,
                    'status_desktop_input_any' : desktop_gpu_input_any,
                    'computer_name_input_any' : desktop_gpu_input_any,  
                })
            else:
                additemany = DESKTOPPACKAGE(name=nameany, desktop_SerialNo=serialany, desktop_BrandName=brandnameany, 
                                            desktop_Model=modelany, desktop_Processor=processorany, desktop_Memory=memoryany, 
                                            desktop_Drive=driveany, desktop_Image=image, desktop_Graphics=desktop_gpu_input_any, desktop_Graphics_Size=desktop_gpusize_input_any, desktop_OS=desktop_os_input_any, desktop_Office=desktop_office_input_any, desktop_OS_keys=desktop_OSkeys_input_any,
                                            desktop_Office_keys=desktop_Officekeys_input_any, desktop_Monitor_SN=monitor_serial_input_any, desktop_Monitor_Brand=monitor_brand_input_any, desktop_Monitor_Model=monitor_model_input_any, 
                                            desktop_Monitor_Size=monitor_size_input_any, desktop_Keyboard_SN=keyboard_serial_input_any, desktop_keyboard_Brand=keyboard_brand_input_any, desktop_keyboard_Model=keyboard_model_input_any, desktop_Mouse_SN=mouse_serial_input_any, desktop_Mouse_Brand=mouse_brand_input_any, 
                                            desktop_Mouse_Model=mouse_model_input_any, desktop_UPS_SN=ups_serial_input_any, desktop_UPS_Brand=ups_brand_input_any, desktop_UPS_Model=ups_model_input_any, desktop_Asset_owner=asset_owner_input_any, desktop_Asset_designation=designation_Asset_input_any, desktop_Asset_section=asset_section_input_any,
                                            desktop_Enduser=end_user_input_any, desktop_Enduser_designation=enduser_designation_input_any, desktop_Enduser_section=enduser_section_input_any, desktop_PAR=par_number_input_any, desktop_Propertyno=property_number_input_any, desktop_Acquisition_Type=acquisition_type_input_any, 
                                            desktop_Value=value_desktop_input_any, desktop_Datereceived=date_received_input_any, desktop_Dateinspected=date_inspected_input_any, desktop_Supplier=supplier_name_input_any, desktop_Status=status_desktop_input_any, desktop_Computer_name=computer_name_input_any)
                additemany.save()
                messages.success(request, 'Your Desktop Package was successfully added')
    # Render the form with default values if not a POST request
    return render(request, 'add_equipment.html', {
        'equipment_type': '',
        'nameany': '',
        'serialany': '',
        'brandnameany': '',
    })
 #####################################   
def success_page(request):
    return render(request, 'success_add.html')  # Render the success page template


# all detailed view

# def all_detailed_view(request):
#    # Get all equipment
#     desktop_list = DESKTOPPACKAGE.objects.all()
#     # Render the list of equipment and the count to the template
#     return render(request, 'desktop_all_detailed_view.html', {'desktop_List': desktop_list})

# edit

############################


# Edit function

# def desktop_detailed_view(request, id):
#     # Get the specific desktop package by its ID
#     desktop = get_object_or_404(DESKTOPPACKAGE, id=id)

#     if request.method == 'POST':
#         # Update the data if the form is submitted (editing functionality)
#         desktop.desktop_SerialNo = request.POST.get('serial_input', desktop.desktop_SerialNo)
#         desktop.desktop_BrandName = request.POST.get('brand_input', desktop.desktop_BrandName)
#         desktop.desktop_Model = request.POST.get('model_input', desktop.desktop_Model)
#         desktop.desktop_Processor = request.POST.get('processor_input', desktop.desktop_Processor)
#         desktop.desktop_Memory = request.POST.get('memory_input', desktop.desktop_Memory)
#         desktop.desktop_Drive = request.POST.get('drive_input', desktop.desktop_Drive)

#         # Monitor fields
#         desktop.desktop_Monitor_SN = request.POST.get('monitor_sn_input', desktop.desktop_Monitor_SN)
#         desktop.desktop_Monitor_Brand = request.POST.get('monitor_brand_input', desktop.desktop_Monitor_Brand)
#         desktop.desktop_Monitor_Model = request.POST.get('monitor_model_input', desktop.desktop_Monitor_Model)
#         desktop.desktop_Monitor_Size = request.POST.get('monitor_size_input', desktop.desktop_Monitor_Size)

#         # Keyboard fields
#         desktop.desktop_Keyboard_SN = request.POST.get('keyboard_sn_input', desktop.desktop_Keyboard_SN)
#         desktop.desktop_keyboard_Brand = request.POST.get('keyboard_brand_input', desktop.desktop_keyboard_Brand)
#         desktop.desktop_keyboard_Model = request.POST.get('keyboard_model_input', desktop.desktop_keyboard_Model)

#         # Mouse fields
#         desktop.desktop_Mouse_SN = request.POST.get('mouse_sn_input', desktop.desktop_Mouse_SN)
#         desktop.desktop_Mouse_Brand = request.POST.get('mouse_brand_input', desktop.desktop_Mouse_Brand)
#         desktop.desktop_Mouse_Model = request.POST.get('mouse_model_input', desktop.desktop_Mouse_Model)

#         # UPS fields
#         desktop.desktop_UPS_SN = request.POST.get('ups_sn_input', desktop.desktop_UPS_SN)
#         desktop.desktop_UPS_Brand = request.POST.get('ups_brand_input', desktop.desktop_UPS_Brand)
#         desktop.desktop_UPS_Model = request.POST.get('ups_model_input', desktop.desktop_UPS_Model)

#         # User details
#         desktop.desktop_Asset_owner = request.POST.get('asset_owner_input', desktop.desktop_Asset_owner)
#         desktop.desktop_Asset_designation = request.POST.get('asset_designation_input', desktop.desktop_Asset_designation)
#         desktop.desktop_Asset_section = request.POST.get('asset_section_input', desktop.desktop_Asset_section)
#         desktop.desktop_Enduser = request.POST.get('enduser_input', desktop.desktop_Enduser)
#         desktop.desktop_Enduser_designation = request.POST.get('enduser_designation_input', desktop.desktop_Enduser_designation)
#         desktop.desktop_Enduser_section = request.POST.get('enduser_section_input', desktop.desktop_Enduser_section)

#         # Documents
#         desktop.desktop_PAR = request.POST.get('par_number_input', desktop.desktop_PAR)
#         desktop.desktop_Propertyno = request.POST.get('property_number_input', desktop.desktop_Propertyno)
#         desktop.desktop_Acquisition_Type = request.POST.get('acquisition_type_input', desktop.desktop_Acquisition_Type)
#         desktop.desktop_Value = request.POST.get('value_desktop_input', desktop.desktop_Value)
#         desktop.desktop_Datereceived = request.POST.get('date_received_input', desktop.desktop_Datereceived)
#         desktop.desktop_Dateinspected = request.POST.get('date_inspected_input', desktop.desktop_Dateinspected)
#         desktop.desktop_Supplier = request.POST.get('supplier_name_input', desktop.desktop_Supplier)
#         desktop.desktop_Status = request.POST.get('status_desktop_input', desktop.desktop_Status)
#         desktop.desktop_Computer_name = request.POST.get('computer_name_input', desktop.desktop_Computer_name)

#         # Handle image file if uploaded
#         if 'desktop_image_input' in request.FILES:
#             desktop.desktop_Image = request.FILES['desktop_image_input']

#         # Validate and save changes
#         if desktop.desktop_SerialNo and desktop.desktop_BrandName and desktop.desktop_Model:
#             desktop.save()
#             # Notify success message
#             return render(request, 'desktop_detailed_view.html', {
#                 'desktops': desktop,
#                 'notify_message': 'Desktop details updated successfully!',
#                 'notify_type': 'success'
#             })
#         else:
#             # Notify error message if required fields are missing
#             return render(request, 'desktop_detailed_view.html', {
#                 'desktops': desktop,
#                 'notify_message': 'Error: Please fill in all required fields.',
#                 'notify_type': 'danger'
#             })

#     # Render the template with the current desktop details for editing
#     return render(request, 'desktop_detailed_view.html', {'desktops': desktop})



# #dispose function

# def dispose_desktop(request, desktop_id):
#     if request.method == 'POST':
#         desktop_package = get_object_or_404(DESKTOPPACKAGE, id=desktop_id)
#         desktop_package.is_disposed = True
#         desktop_package.disposal_date = timezone.now()  # Assuming you are tracking the disposal date
#         desktop_package.save()
#         return JsonResponse({'success': True})
#     return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


# def disposed_desktop_list(request):
#     # Assuming there's an `is_disposed` field to filter disposed desktops
#     disposed_desktops = DESKTOPPACKAGE.objects.filter(is_disposed=True)
#     return render(request, 'disposed_desktop_list.html', {'disposed_desktops': disposed_desktops})

###########################################################################################
#Template: Desktop_details_view
def desktop_package_base(request):
    # Fetch all desktop details
    desktop_details = DesktopDetails.objects.all()
    
    # Create a combined list where each desktop is paired with its keyboards
    desktops_with_items = []
    for desktop in desktop_details:
        keyboards = KeyboardDetails.objects.filter(desktop_package=desktop.desktop_package, is_disposed=False)
        user = UserDetails.objects.filter(desktop_package_db=desktop.desktop_package)
        desktops_with_items.append({
            'desktop': desktop,
            'keyboards': keyboards,  # This can have multiple entries per desktop
            'user': user
        })

    return render(request, 'desktop_details.html', {
        'desktops_with_items': desktops_with_items,
    })      


def desktop_details_view(request, desktop_id):
    # Get the specific desktop by ID
    desktop_details = get_object_or_404(DesktopDetails, id=desktop_id)
    desktop_package = desktop_details.desktop_package  # Get the associated package directly from desktop_details
    
    # Get all keyboards,mouse, monitor in desktop_details_view related to the desktop package
    keyboard_detailsx = KeyboardDetails.objects.filter(desktop_package=desktop_package, is_disposed=False)
    mouse_details = MouseDetails.objects.filter(desktop_package=desktop_package, is_disposed=False)
    monitor_detailsx = MonitorDetails.objects.filter(desktop_package_db=desktop_package, is_disposed=False)
    ups_details = UPSDetails.objects.filter(desktop_package=desktop_package, is_disposed=False)
    user_details = UserDetails.objects.filter(desktop_package_db=desktop_package).first()

    # Get disposed keyboards,mouse, monitor in desktop_details_view
    disposed_keyboards = DisposedKeyboard.objects.filter(keyboard_dispose_db__desktop_package=desktop_package)
    disposed_mouse = DisposedMouse.objects.filter(mouse_db__desktop_package=desktop_package)
    disposed_monitor = DisposedMonitor.objects.filter(monitor_disposed_db__desktop_package_db=desktop_package)
    disposed_ups = DisposedUPS.objects.filter(ups_db__desktop_package=desktop_package)


    # active keyboards,mouse, monitor in desktop_details_view
    has_active_keyboards = KeyboardDetails.objects.filter(desktop_package=desktop_package, is_disposed=False).exists()
    has_active_mouse = MouseDetails.objects.filter(desktop_package=desktop_package, is_disposed=False).exists()
    has_active_monitor = MonitorDetails.objects.filter(desktop_package_db=desktop_package, is_disposed=False).exists()
    has_active_ups = UPSDetails.objects.filter(desktop_package=desktop_package, is_disposed=False).exists()

    #ownership
    # transfer_history = OwnershipTransfer.objects.filter(desktop_package=desktop_package).order_by('-transfer_date')

    return render(request, 'desktop_details_view.html', {
        'desktop_detailsx': desktop_details,
        'keyboard_detailse': keyboard_detailsx.first(),  # Assuming you only need one related keyboard detail
        'disposed_keyboards': disposed_keyboards,
        'disposed_mouse' : disposed_mouse,
        'disposed_monitor' : disposed_monitor,
        'disposed_ups' : disposed_ups,
        'has_active_keyboards': has_active_keyboards,
        'has_active_mouse': has_active_mouse,
        'has_active_monitor': has_active_monitor,
        'has_active_ups' : has_active_ups, 
        'monitor_detailse': monitor_detailsx.first(),
        'mouse_detailse': mouse_details.first(),
        'ups_detailse': ups_details.first(),
        'user_details' : user_details,
        'desktop_package': desktop_package,  # Pass desktop_package to the template for URL resolution
       })




################# (KEYBOAR AND MOUSE)

def keyboard_details(request):
   # Get all equipment
    keyboard_details = KeyboardDetails.objects.all()
    mouse_details = MouseDetails.objects.all()
    # Render the list of equipment and the count to the template
    return render(request, 'keyboard_details.html', {'keyboard_details': keyboard_details, 
                                                     'mouse_details': mouse_details})


def keyboard_detailed_view(request, keyboard_id):
    # Get the specific keyboard using its ID
    keyboard = get_object_or_404(KeyboardDetails, id=keyboard_id)
    # Render the detailed view of the keyboard
    return render(request, 'keyboard_detailed_view.html', {'keyboard': keyboard})
    


def keyboard_disposed(request, keyboard_id):
    if request.method == 'POST':
        # Retrieve the keyboard by its ID
        keyboard = get_object_or_404(KeyboardDetails, id=keyboard_id)
        
        # Set the keyboard as disposed and save
        keyboard.is_disposed = True
        keyboard.save()
        
        # Create a new DisposedKeyboard entry
        disposed_keyboard = DisposedKeyboard(
            keyboard_dispose_db=keyboard,
            disposal_date=timezone.now()
        )
        disposed_keyboard.save()

        # Get the package ID to redirect to the same page
        desktop_package_id = keyboard.desktop_package.id
        
        # Redirect back to the desktop details view with the Keyboard tab active
        return redirect(f'/desktop_details_view/{desktop_package_id}/#pills-keyboard')

    # Fallback in case the request method is not POST
    return redirect('desktop_details_view', package_id=keyboard.desktop_package.id)

def monitor_disposed(request, monitor_id):
    if request.method == 'POST':
        # Retrieve the keyboard by its ID
        monitor = get_object_or_404(MonitorDetails, id=monitor_id)
        
        # Set the keyboard as disposed and save
        monitor.is_disposed = True
        monitor.save()
        
        # Create a new DisposedKeyboard entry
        disposed_monitor = DisposedMonitor(
            monitor_disposed_db=monitor,
            disposal_date=timezone.now()
        )
        disposed_monitor.save()

        # Get the package ID to redirect to the same page
        desktop_package_id = monitor.desktop_package_db.id
        
        # Redirect back to the desktop details view with the Keyboard tab active
        return redirect(f'/desktop_details_view/{desktop_package_id}/#pills-monitor')

    # Fallback in case the request method is not POST
    return redirect('desktop_details_view', package_id=monitor_id)

def mouse_disposed(request, mouse_id):
    # Only proceed if the request is POST
    if request.method == 'POST':
        # Retrieve the mouse by its ID
        mouse = get_object_or_404(MouseDetails, id=mouse_id)
        
        # Set the mouse as disposed and save
        mouse.is_disposed = True
        mouse.save()
        
        # Create a new DisposedMouse entry
        disposed_mouse = DisposedMouse(
            mouse_db=mouse,
            disposal_date=timezone.now()
        )
        disposed_mouse.save()

        # Get the package ID to redirect to the same page
        desktop_package_id = mouse.desktop_package.id

        # Redirect back to the desktop details view with the Mouse tab active
        return redirect(f'/desktop_details_view/{desktop_package_id}/#pills-mouse')

    # Fallback for non-POST requests: redirect to an appropriate page or show an error
    return redirect('desktop_details_view', package_id=mouse_id)


#disposed UPS
def ups_disposed(request, ups_id):
    # Only proceed if the request is POST
    if request.method == 'POST':
        # Retrieve the UPS by its ID
        ups = get_object_or_404(UPSDetails, id=ups_id)
        
        # Set the ups as disposed and save
        ups.is_disposed = True
        ups.save()
        
        # Create a new DisposedUps entry
        disposed_mups = DisposedUPS(
            ups_db=ups,
            disposal_date=timezone.now()
        )
        disposed_mups.save()

        # Get the package ID to redirect to the same page
        desktop_package_id = ups.desktop_package.id

        # Redirect back to the desktop details view with the UPS tab active
        return redirect(f'/desktop_details_view/{desktop_package_id}/#pills-ups')

    # Fallback for non-POST requests: redirect to an appropriate page or show an error
    return redirect('desktop_details_view', package_id=ups_id)


def add_keyboard_to_package(request, package_id):
    if request.method == 'POST':
        # Retrieve the desktop package by its ID
        desktop_package = get_object_or_404(Desktop_Package, id=package_id)
        
        # Get form data
        keyboard_sn = request.POST.get('keyboard_sn')
        keyboard_brand = request.POST.get('keyboard_brand')
        keyboard_model = request.POST.get('keyboard_model')
        
        # Create a new keyboard associated with the desktop package
        KeyboardDetails.objects.create(
            desktop_package=desktop_package,
            keyboard_sn_db=keyboard_sn,
            keyboard_brand_db=keyboard_brand,
            keyboard_model_db=keyboard_model
        )
        
        # Redirect back to the desktop details view, focusing on the Keyboard tab
        return redirect(f'/desktop_details_view/{package_id}/#pills-keyboard')
    
    return redirect('desktop_details_view', package_id=package_id)

def add_monitor_to_package(request, package_id):
    if request.method == 'POST':
        # Retrieve the desktop package by its ID
        desktop_package = get_object_or_404(Desktop_Package, id=package_id)
        
        # Get form data
        monitor_sn = request.POST.get('monitor_sn')
        monitor_brand = request.POST.get('monitor_brand')
        monitor_model = request.POST.get('monitor_model')
        
        # Create a new keyboard associated with the desktop package
        MonitorDetails.objects.create(
            desktop_package_db=desktop_package,
            monitor_sn_db=monitor_sn,
            monitor_brand_db=monitor_brand,
            monitor_model_db=monitor_model
        )
        
        # Redirect back to the desktop details view, focusing on the Keyboard tab
        return redirect(f'/desktop_details_view/{package_id}/#pills-monitor')
    
    return redirect('desktop_details_view', package_id=package_id)


#viewing of all keyboard disposed
def disposed_keyboards(request):
    # Get all disposed keyboards
    disposed_keyboards = DisposedKeyboard.objects.all()
    # Render the list of disposed keyboards to the template
    return render(request, 'disposed_keyboards.html', {'disposed_keyboards': disposed_keyboards})



# END ################ (KEYBOARD END)


# BEGIN ################ (MOUSE)

#This function retrieves all mouse records and renders them in a similar way as mouse_details.
def mouse_details(request):
    # Get all mouse equipment
    mouse_details = MouseDetails.objects.all()
    # Render the list of mice and the count to the template
    return render(request, 'mouse_details.html', {'mouse_details': mouse_details})


#This function retrieves the details of a specific mouse by its ID.
def mouse_detailed_view(request, mouse_id):
    # Get the specific mouse using its ID
    mouse = get_object_or_404(MouseDetails, id=mouse_id)
    # Render the detailed view of the mouse
    return render(request, 'mouse_detailed_view.html', {'mouse': mouse})

#This function marks a specific mouse as disposed, saves it, and then redirects back to the desktop details view with the "Mouse" tab active.



#This function allows adding a new mouse to a specific desktop package, then redirects back to the "Mouse" tab of the desktop details view.
def add_mouse_to_package(request, package_id):
    if request.method == 'POST':
        # Retrieve the desktop package by its ID
        desktop_package = get_object_or_404(Desktop_Package, id=package_id)
        
        # Get form data
        mouse_sn = request.POST.get('mouse_sn')
        mouse_brand = request.POST.get('mouse_brand')
        mouse_model = request.POST.get('mouse_model')
        
        # Create a new mouse associated with the desktop package
        MouseDetails.objects.create(
            desktop_package=desktop_package,
            mouse_sn_db=mouse_sn,
            mouse_brand_db=mouse_brand,
            mouse_model_db=mouse_model
        )
        
        # Redirect back to the desktop details view, focusing on the Mouse tab
        return redirect(f'/desktop_details_view/{package_id}/#pills-mouse')
    
    return redirect('desktop_details_view', package_id=package_id)


def add_ups_to_package(request, package_id):
    if request.method == 'POST':
        # Retrieve the desktop package by its ID
        desktop_package = get_object_or_404(Desktop_Package, id=package_id)
        
        # Get form data
        ups_sn = request.POST.get('ups_sn')
        ups_brand = request.POST.get('ups_brand')
        ups_model = request.POST.get('ups_model')
        
        # Create a new mouse associated with the desktop package
        UPSDetails.objects.create(
            desktop_package=desktop_package,
            ups_sn_db=ups_sn,
            brand_db=ups_brand,
            model_db=ups_model
        )
        
        # Redirect back to the desktop details view, focusing on the Mouse tab
        return redirect(f'/desktop_details_view/{package_id}/#pills-ups')
    
    return redirect('desktop_details_view', package_id=package_id)

#This function lists all disposed mice, assuming you have a DisposedMouse model similar to DisposedKeyboard.
def disposed_mice(request):
    # Get all disposed mice
    disposed_mice = DisposedMouse.objects.all()
    # Render the list of disposed mice to the template
    return render(request, 'disposed_mice.html', {'disposed_mice': disposed_mice})


# END ################ (MOUSE END)



# adding Desktop packages
def add_desktop_package_with_details(request):
    if request.method == 'POST':
        with transaction.atomic():  # Ensure all or nothing for database changes
            # Create Desktop Package
            desktop_package = Desktop_Package.objects.create(is_disposed=False)
            package_id = desktop_package.id  # Retrieve the auto-generated ID

            # Create Desktop Details without manually setting id
            DesktopDetails.objects.create(
                desktop_package=desktop_package,
                serial_no=request.POST.get('desktop_serial_no'),
                computer_name=request.POST.get('computer_name'),
                brand_name=request.POST.get('desktop_brand_name'),
                model=request.POST.get('desktop_model'),
                processor=request.POST.get('desktop_processor'),
                memory=request.POST.get('desktop_memory'),
                drive=request.POST.get('desktop_drive'),
                asset_owner=request.POST.get('asset_owner'),
                desktop_Graphics=request.POST.get('desktop_Graphics'),
                desktop_Graphics_Size=request.POST.get('desktop_Graphics_Size'),
                desktop_OS=request.POST.get('desktop_OS'),
                desktop_Office=request.POST.get('desktop_Office'),
                desktop_OS_keys=request.POST.get('desktop_OS_keys'),
                desktop_Office_keys=request.POST.get('desktop_Office_keys')
            )

            # Create Keyboard Details without manually setting id
            KeyboardDetails.objects.create(
                desktop_package=desktop_package,
                keyboard_sn=request.POST.get('keyboard_sn'),
                brand=request.POST.get('keyboard_brand'),
                model=request.POST.get('keyboard_model')
            )

            # Create Monitor Details without manually setting id
            MonitorDetails.objects.create(
                desktop_package_db=desktop_package,
                monitor_sn_db=request.POST.get('monitor_sn'),
                monitor_brand_db=request.POST.get('monitor_brand'),
                monitor_model_db=request.POST.get('monitor_model'),
                monitor_size_db=request.POST.get('monitor_size')
            )

            # Create Mouse Details without manually setting id
            MouseDetails.objects.create(
                desktop_package=desktop_package,
                mouse_sn_db=request.POST.get('mouse_sn'),
                mouse_brand_db=request.POST.get('mouse_brand'),
                mouse_model_db=request.POST.get('mouse_model')
            )

            # Create UPS Details without manually setting id
            UPSDetails.objects.create(
                desktop_package=desktop_package,
                ups_sn_db=request.POST.get('ups_sn'),
                brand_db=request.POST.get('ups_brand'),
                model_db=request.POST.get('ups_model')
            )

        return redirect('success_add_page')

    return render(request, 'add_desktop_package_with_details.html')


############### (KEYBOARD AND MOUSE)


############### (RECENT at BASE)

def recent_it_equipment_base(request):
    recent_desktops = DesktopDetails.objects.filter(is_disposed=False).order_by('-created_at')[:10]


    return render(request, 'base.html', {
        'recent_desktops': recent_desktops,
        # 'recent_keyboards': recent_keyboards,
    })

