from django.shortcuts import render, redirect
from django.contrib import messages
from inventory.models import DESKTOPPACKAGE
from inventory.models import Desktop_Package, DesktopDetails, KeyboardDetails, DisposedKeyboard, MouseDetails, MonitorDetails, UPSDetails
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse # sa disposing ni sya sa desktop
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone





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
#add equipment function

def add_equipment_func(request):
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

def all_detailed_view(request):
   # Get all equipment
    desktop_list = DESKTOPPACKAGE.objects.all()
    # Render the list of equipment and the count to the template
    return render(request, 'desktop_all_detailed_view.html', {'desktop_List': desktop_list})

# edit

############################


# Edit function

def desktop_detailed_view(request, id):
    # Get the specific desktop package by its ID
    desktop = get_object_or_404(DESKTOPPACKAGE, id=id)

    if request.method == 'POST':
        # Update the data if the form is submitted (editing functionality)
        desktop.desktop_SerialNo = request.POST.get('serial_input', desktop.desktop_SerialNo)
        desktop.desktop_BrandName = request.POST.get('brand_input', desktop.desktop_BrandName)
        desktop.desktop_Model = request.POST.get('model_input', desktop.desktop_Model)
        desktop.desktop_Processor = request.POST.get('processor_input', desktop.desktop_Processor)
        desktop.desktop_Memory = request.POST.get('memory_input', desktop.desktop_Memory)
        desktop.desktop_Drive = request.POST.get('drive_input', desktop.desktop_Drive)

        # Monitor fields
        desktop.desktop_Monitor_SN = request.POST.get('monitor_sn_input', desktop.desktop_Monitor_SN)
        desktop.desktop_Monitor_Brand = request.POST.get('monitor_brand_input', desktop.desktop_Monitor_Brand)
        desktop.desktop_Monitor_Model = request.POST.get('monitor_model_input', desktop.desktop_Monitor_Model)
        desktop.desktop_Monitor_Size = request.POST.get('monitor_size_input', desktop.desktop_Monitor_Size)

        # Keyboard fields
        desktop.desktop_Keyboard_SN = request.POST.get('keyboard_sn_input', desktop.desktop_Keyboard_SN)
        desktop.desktop_keyboard_Brand = request.POST.get('keyboard_brand_input', desktop.desktop_keyboard_Brand)
        desktop.desktop_keyboard_Model = request.POST.get('keyboard_model_input', desktop.desktop_keyboard_Model)

        # Mouse fields
        desktop.desktop_Mouse_SN = request.POST.get('mouse_sn_input', desktop.desktop_Mouse_SN)
        desktop.desktop_Mouse_Brand = request.POST.get('mouse_brand_input', desktop.desktop_Mouse_Brand)
        desktop.desktop_Mouse_Model = request.POST.get('mouse_model_input', desktop.desktop_Mouse_Model)

        # UPS fields
        desktop.desktop_UPS_SN = request.POST.get('ups_sn_input', desktop.desktop_UPS_SN)
        desktop.desktop_UPS_Brand = request.POST.get('ups_brand_input', desktop.desktop_UPS_Brand)
        desktop.desktop_UPS_Model = request.POST.get('ups_model_input', desktop.desktop_UPS_Model)

        # User details
        desktop.desktop_Asset_owner = request.POST.get('asset_owner_input', desktop.desktop_Asset_owner)
        desktop.desktop_Asset_designation = request.POST.get('asset_designation_input', desktop.desktop_Asset_designation)
        desktop.desktop_Asset_section = request.POST.get('asset_section_input', desktop.desktop_Asset_section)
        desktop.desktop_Enduser = request.POST.get('enduser_input', desktop.desktop_Enduser)
        desktop.desktop_Enduser_designation = request.POST.get('enduser_designation_input', desktop.desktop_Enduser_designation)
        desktop.desktop_Enduser_section = request.POST.get('enduser_section_input', desktop.desktop_Enduser_section)

        # Documents
        desktop.desktop_PAR = request.POST.get('par_number_input', desktop.desktop_PAR)
        desktop.desktop_Propertyno = request.POST.get('property_number_input', desktop.desktop_Propertyno)
        desktop.desktop_Acquisition_Type = request.POST.get('acquisition_type_input', desktop.desktop_Acquisition_Type)
        desktop.desktop_Value = request.POST.get('value_desktop_input', desktop.desktop_Value)
        desktop.desktop_Datereceived = request.POST.get('date_received_input', desktop.desktop_Datereceived)
        desktop.desktop_Dateinspected = request.POST.get('date_inspected_input', desktop.desktop_Dateinspected)
        desktop.desktop_Supplier = request.POST.get('supplier_name_input', desktop.desktop_Supplier)
        desktop.desktop_Status = request.POST.get('status_desktop_input', desktop.desktop_Status)
        desktop.desktop_Computer_name = request.POST.get('computer_name_input', desktop.desktop_Computer_name)

        # Handle image file if uploaded
        if 'desktop_image_input' in request.FILES:
            desktop.desktop_Image = request.FILES['desktop_image_input']

        # Validate and save changes
        if desktop.desktop_SerialNo and desktop.desktop_BrandName and desktop.desktop_Model:
            desktop.save()
            # Notify success message
            return render(request, 'desktop_detailed_view.html', {
                'desktops': desktop,
                'notify_message': 'Desktop details updated successfully!',
                'notify_type': 'success'
            })
        else:
            # Notify error message if required fields are missing
            return render(request, 'desktop_detailed_view.html', {
                'desktops': desktop,
                'notify_message': 'Error: Please fill in all required fields.',
                'notify_type': 'danger'
            })

    # Render the template with the current desktop details for editing
    return render(request, 'desktop_detailed_view.html', {'desktops': desktop})



#dispose function

def dispose_desktop(request, desktop_id):
    if request.method == 'POST':
        desktop_package = get_object_or_404(DESKTOPPACKAGE, id=desktop_id)
        desktop_package.is_disposed = True
        desktop_package.disposal_date = timezone.now()  # Assuming you are tracking the disposal date
        desktop_package.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


def disposed_desktop_list(request):
    # Assuming there's an `is_disposed` field to filter disposed desktops
    disposed_desktops = DESKTOPPACKAGE.objects.filter(is_disposed=True)
    return render(request, 'disposed_desktop_list.html', {'disposed_desktops': disposed_desktops})

############################

def desktop_package(request):
    # Get all equipment
    desktop_package = Desktop_Package.objects.all()
    desktop_details = DesktopDetails.objects.all()
    return render(request, 'desktop_details.html', {'desktop_package': desktop_package, 'desktop_details': desktop_details})


def desktop_details_view(request, desktop_id):
    # Get the specific desktop by ID
    desktop_details = get_object_or_404(DesktopDetails, id=desktop_id)
    
    # Get all keyboards related to the desktop package
    keyboard_detailsx = KeyboardDetails.objects.filter(desktop_package=desktop_details.desktop_package)

    # Get all monitors related to the desktop package
    monitor_detailsx = MonitorDetails.objects.filter(desktop_package_db=desktop_details.desktop_package)

    # Get all mouse related to the desktop package
    mouse_details = MouseDetails.objects.filter(desktop_package=desktop_details.desktop_package)

    # Get all ups related to the desktop package
    ups_details = UPSDetails.objects.filter(desktop_package=desktop_details.desktop_package)

    return render(request, 'desktop_details_view.html', {
        'desktop_detailsx': desktop_details,
        'keyboard_detailse': keyboard_detailsx.first(),  # Assuming you only need one related keyboard detail
        'monitor_detailse': monitor_detailsx.first(),
        'mouse_detailse': mouse_details.first(),
        'ups_detailse': ups_details.first(),
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
        keyboard = get_object_or_404(KeyboardDetails, id=keyboard_id)
        
        # Set the keyboard as disposed and save
        keyboard.is_disposed = True
        keyboard.save()
        
        # Create a new DisposedKeyboard entry
        disposed_keyboard = DisposedKeyboard(
            keyboard=keyboard,
            disposal_date=timezone.now()
        )
        disposed_keyboard.save()

        return JsonResponse({'success': True, 'message': 'Keyboard disposed successfully.'})

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


def disposed_keyboards(request):
    # Get all disposed keyboards
    disposed_keyboards = DisposedKeyboard.objects.all()
    # Render the list of disposed keyboards to the template
    return render(request, 'disposed_keyboards.html', {'disposed_keyboards': disposed_keyboards})


# END ################ (KEYBOARD END)


# adding Desktop packages
def add_desktop_package_with_details(request):
    if request.method == 'POST':
        # Gather Desktop Package Information
        computer_name = request.POST.get('computer_name')
        asset_owner = request.POST.get('asset_owner')
        is_disposed = request.POST.get('is_disposed', 'False') == 'True'

        # Prevent data duplication - check if a package with the same computer_name exists
        if DesktopDetails.objects.filter(computer_name=computer_name).exists():
            return JsonResponse({'success': False, 'error': 'Desktop Package with this computer name already exists.'}, status=400)

        # Create Desktop Package
        desktop_package = Desktop_Package(
            is_disposed=is_disposed,
        )
        desktop_package.save() #savefirst the the package as a memory to have some id or pk, before adding the whole

        # Create Desktop Details associated with this Desktop Package
        desktop_serial_no = request.POST.get('desktop_serial_no')
        desktop_brand_name = request.POST.get('desktop_brand_name')
        desktop_model = request.POST.get('desktop_model')
        desktop_processor = request.POST.get('desktop_processor')
        desktop_memory = request.POST.get('desktop_memory')
        desktop_drive = request.POST.get('desktop_drive')

        desktop_Graphics = request.POST.get('desktop_Graphics')
        desktop_Graphics_Size = request.POST.get('desktop_Graphics_Size')
        desktop_OS = request.POST.get('desktop_OS')
        desktop_Office = request.POST.get('desktop_Office')
        desktop_OS_keys = request.POST.get('desktop_OS_keys')
        desktop_Office_keys = request.POST.get('desktop_Office_keys')

        desktop_details = DesktopDetails(
            desktop_package=desktop_package,
            serial_no=desktop_serial_no,
            computer_name=computer_name,
            brand_name=desktop_brand_name,
            model=desktop_model,
            processor=desktop_processor,
            memory=desktop_memory,
            drive=desktop_drive,
            asset_owner=asset_owner,
            desktop_Graphics=desktop_Graphics,
            desktop_Graphics_Size=desktop_Graphics_Size,
            desktop_OS=desktop_OS,
            desktop_Office=desktop_Office,
            desktop_OS_keys=desktop_OS_keys,
            desktop_Office_keys=desktop_Office_keys,
        )
        desktop_details.save()

        # Create Keyboard Details associated with this Desktop Package
        keyboard_sn = request.POST.get('keyboard_sn')
        keyboard_brand = request.POST.get('keyboard_brand')
        keyboard_model = request.POST.get('keyboard_model')

        keyboard_details = KeyboardDetails(
            desktop_package=desktop_package,
            keyboard_sn=keyboard_sn,
            brand=keyboard_brand,
            model=keyboard_model,
        )
        keyboard_details.save()

        # Create Monitor Details Associated with  this Desktop Package

        monitor_sn = request.POST.get('monitor_sn')
        monitor_brand = request.POST.get('monitor_brand')
        monitor_model = request.POST.get('monitor_model')
        monitor_size = request.POST.get('monitor_size')

        monitor_details = MonitorDetails(
            desktop_package_db=desktop_package,
            monitor_sn_db=monitor_sn,
            monitor_brand_db=monitor_brand,
            monitor_model_db=monitor_model,
            monitor_size_db=monitor_size,
        )
        monitor_details.save()    

        # Create Mouse Details Associated with  this Desktop Package
        mouse_sn = request.POST.get('mouse_sn')
        mouse_brand = request.POST.get('mouse_brand')
        mouse_model = request.POST.get('mouse_model')

        mouse_details = MouseDetails(
            desktop_package=desktop_package,
            mouse_sn_db=mouse_sn,
            mouse_brand_db=mouse_brand,
            mouse_model_db=mouse_model,
        )
        mouse_details.save()        

        # Create UPS Details Associated with  this Desktop Package
        ups_sn = request.POST.get('ups_sn')
        ups_brand = request.POST.get('ups_brand')
        ups_model = request.POST.get('ups_model')

        mouse_details = UPSDetails(
            desktop_package=desktop_package,
            ups_sn_db=ups_sn,
            brand_db=ups_brand,
            model_db=ups_model,
        )
        mouse_details.save()        

        # Redirect to prevent form resubmission
        return redirect('success_add_page')

    return render(request, 'add_desktop_package_with_details.html')

############### (KEYBOARD AND MOUSE)

