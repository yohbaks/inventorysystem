from django.shortcuts import render, redirect
from django.contrib import messages
from inventory.models import Equipment
from inventory.models import DESKTOPPACKAGE




# Create your views here.

# code for the list in the homepage
def equipment_list(request):

    # Get all equipment
    equipments = Equipment.objects.all()

    # Count the total number of equipment
    equipment_count = equipments.count()

    # Render the list of equipment and the count to the template
    return render(request, 'base.html', {'equipments': equipments, 'equipment_count': equipment_count})


# code for the full list in datatablescopy.html
def equipment_full_list(request):

    # Get all equipment
    equipments = Equipment.objects.all()

    # Count the total number of equipment
    equipment_count = equipments.count()

    # Render the list of equipment and the count to the template
    return render(request, 'tables/datatablescopy.html', {'equipments': equipments, 'equipment_count': equipment_count})


# code for the adding item with using forms: 
# def add_equipment(request):
#     if request.method == 'POST':
#         form = EquipmentForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Equipment added successfully!")
#             return redirect('equipment_list')  # Redirect to the list of equipment or another page
#     else:
#         form = EquipmentForm()
#     return render(request, 'add_equipment.html', {'form': form})

##############################################################################

def add_equipment_func(request):
    if request.method == 'POST':
        nameany = request.POST['name_input']
        serialany = request.POST['desktop_serial_input']
        brandnameany = request.POST['desktop_brand_input']
        
        if len(nameany) < 2 or len(serialany)< 1 or len(brandnameany)< 2:
            messages.error(request, "Please fill the following forms")

        else:   
            additemany = DESKTOPPACKAGE(name=nameany, desktop_SerialNo=serialany, desktop_BrandName=brandnameany)
            additemany.save()
            messages.success(request, 'Your Desktop Package was succesfully add')
            print(nameany, serialany, brandnameany)

            # Redirect to another page to prevent form resubmission on refresh
            return redirect('success_add_page')  # Replace 'success_page' with the name of the page you want to redirect to

    #render the request
    return render(request, 'add_equipment.html')

def success_page(request):
    return render(request, 'success_add.html')  # Render the success page template








##################################################################################



#code for the one list and slug
def equipment_detailed_slug(request, slug):
    post = get_object_or_404(add_equipment_func, slug=slug)
    return render(request, 'base.html', {'post': post})



    # # Ensure this view returns the correct template
    # return render(request, 'tables/datatablescopy.html')  # Make sure this path is correct
    

# def contact_function(request):
#     if request.method == 'POST':
#         nameANY = request.POST['name_input']
#         phoneANY = request.POST['phone_input']
#         emailANY = request.POST['email_input']
#         contentANY = request.POST['content_input']
#         if len(nameANY) < 2 or len(phoneANY)<5 or len(emailANY)<2 or len(contentANY)<10:
#             messages.error(request, "Please fill the following forms")

#         else:
#             contactANY = Contactnamedb(name=nameANY, phone=phoneANY, email=emailANY, content=contentANY)
#             contactANY.save()
#             messages.success(request, 'Your messages was successful')
#         # print(nameANY, phoneANY, emailANY, contentANY)
#     return render(request, 'contact.html')
