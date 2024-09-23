from django.shortcuts import render, redirect
from django.contrib import messages
from inventory.models import DESKTOPPACKAGE
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
                return redirect('success_add_page')  # Redirect to success page
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
        desktop.desktop_Graphics = request.POST.get('graphics_input', desktop.desktop_Graphics)
        desktop.desktop_Graphics_Size = request.POST.get('graphics_size_input', desktop.desktop_Graphics_Size)
        desktop.desktop_OS = request.POST.get('os_input', desktop.desktop_OS)
        desktop.desktop_Office = request.POST.get('office_input', desktop.desktop_Office)
        desktop.desktop_OS_keys = request.POST.get('os_keys_input', desktop.desktop_OS_keys)
        desktop.desktop_Office_keys = request.POST.get('office_keys_input', desktop.desktop_Office_keys)

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

        desktop.desktop_PAR = request.POST.get('par_number_input', '') #par_number_input
        desktop.desktop_Propertyno = request.POST.get('property_number_input', '') #property_number_input
        desktop.desktop_Acquisition_Type = request.POST.get('acquisition_type_input', '') #acquisition_type_input
        desktop.desktop_Value = request.POST.get('value_desktop_input', '') #value_desktop_input
        desktop.desktop_Datereceived = request.POST.get('date_received_input', '') #date_received_input
        desktop.desktop_Dateinspected= request.POST.get('date_inspected_input', '') #date_inspected_input
        desktop.desktop_Supplier = request.POST.get('supplier_name_input', '') #supplier_name_input
        desktop.desktop_Status = request.POST.get('status_desktop_input', '') #status_desktop_input
        desktop.desktop_Computer_name = request.POST.get('computer_name_input', '')

        # Disposal status
        desktop.is_disposed = request.POST.get('is_disposed_input', desktop.is_disposed)
        desktop.disposal_date = request.POST.get('disposal_date_input', desktop.disposal_date)

        # Handle image file if uploaded
        if 'desktop_image_input' in request.FILES:
            desktop.desktop_Image = request.FILES['desktop_image_input']

        # Validate and save changes
        if desktop.desktop_SerialNo and desktop.desktop_BrandName and desktop.desktop_Model:
            desktop.save()
            messages.success(request, 'Desktop details updated successfully!')
            return redirect('desktop_detailed_view', id=desktop.id)
        else:
            messages.error(request, 'Please fill in all required fields.')

    # Render the template with the current desktop details for editing
    return render(request, 'desktop_detailed_view.html', {'desktops': desktop})







############################

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

