from django.shortcuts import render, redirect
from django.contrib import messages
from inventory.models import DESKTOPPACKAGE
from django.shortcuts import render, get_object_or_404




# Create your views here.
##############################################################################
# code for the list in the homepage
def desktop_list_func(request):

    # Get all equipment
    desktop_list = DESKTOPPACKAGE.objects.all()

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

        if equipment_type == 'Desktop':
            if len(nameany) < 2 or len(serialany) < 1 or len(brandnameany) < 2 or len(modelany) < 2 or len(processorany) < 2 or len(memoryany)<2:
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
                })
            else:
                additemany = DESKTOPPACKAGE(name=nameany, desktop_SerialNo=serialany, desktop_BrandName=brandnameany, 
                                            desktop_Model=modelany, desktop_Processor=processorany, desktop_Memory=memoryany, 
                                            desktop_Drive=driveany)
                additemany.save()
                messages.success(request, 'Your Desktop Package was successfully added')
                return redirect('success_add_page')  # Redirect to success page

        # Add similar conditions for other equipment types as needed

    # Render the form with default values if not a POST request
    return render(request, 'add_equipment.html', {
        'equipment_type': '',
        'nameany': '',
        'serialany': '',
        'brandnameany': '',
    })
    
def success_page(request):
    return render(request, 'success_add.html')  # Render the success page template


##################################################################################


##################################################################################

# detailed view

# def desktop_detailed_view(request, id):
#     desktop = get_object_or_404(DESKTOPPACKAGE, id=id)
#     return render(request, 'desktop_detailed_view.html', {'desktops': desktop})
# #########################################################################


###########################################################################

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

        # Validate and save changes
        if desktop.desktop_SerialNo and desktop.desktop_BrandName and desktop.desktop_Model:
            desktop.save()
            messages.success(request, 'Desktop details updated successfully!')
            return redirect('desktop_detailed_view', id=desktop.id)
        else:
            messages.error(request, 'Please fill in all required fields.')

    # Render the template with the current desktop details for editing
    return render(request, 'desktop_detailed_view.html', {'desktops': desktop})
