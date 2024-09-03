from django.shortcuts import render
from django.contrib import messages
from inventory.models import Equipment



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


#code for the add equipment
def add_equipment_func(request):
    if request.method == 'POST':
        nameany = request.POST['name_input']
        serialany = request.POST['serial_input']
        brandnameany = request.POST['brandname_input']
        
        if len(nameany) < 2 or len(serialany)<5 or len(brandnameany)<2:
            messages.error(request, "Please fill the following forms")

        else:   
            additemany = Equipment(name=nameany, serialE=serialany, brandname=brandnameany)
            additemany.save()
            messages.success(request, 'Your messages was successful')
            print(nameany, serialany, brandnameany)
    #render the request
    return render(request, 'add_equipment.html')



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
