from django.shortcuts import render, redirect
from django.contrib import messages

from inventory.models import Desktop_Package, DesktopDetails, KeyboardDetails, DisposedKeyboard, MouseDetails, MonitorDetails, UPSDetails, DisposedMouse, DisposedMonitor, UserDetails, DisposedUPS, Employee, DocumentsDetails, EndUserChangeHistory, AssetOwnerChangeHistory, DisposedDesktopDetail
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse # sa disposing ni sya sa desktop
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from django.utils import timezone
from django.db import transaction
from django.views.decorators.http import require_POST
from django.urls import reverse



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

 #####################################   
def success_page(request):
    return render(request, 'success_add.html')  # Render the success page template


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
    enduser_history = EndUserChangeHistory.objects.filter(desktop_package=desktop_details.desktop_package)
    assetowner_history = AssetOwnerChangeHistory.objects.filter(desktop_package=desktop_details.desktop_package)
    employees = Employee.objects.all()
    
    # Get all active keyboards,mouse, monitor in desktop_details_view related to the desktop package (for displaying or further processing)

    keyboard_detailsx = KeyboardDetails.objects.filter(desktop_package=desktop_package, is_disposed=False)
    mouse_details = MouseDetails.objects.filter(desktop_package=desktop_package, is_disposed=False)
    monitor_detailsx = MonitorDetails.objects.filter(desktop_package_db=desktop_package, is_disposed=False)
    ups_details = UPSDetails.objects.filter(desktop_package=desktop_package, is_disposed=False)
    user_details = UserDetails.objects.filter(desktop_package_db=desktop_package).first()
    

    # Get disposed keyboards,mouse, monitor in desktop_details_view
    disposed_desktop = DisposedDesktopDetail.objects.filter(desktop__desktop_package=desktop_package)
    disposed_keyboards = DisposedKeyboard.objects.filter(keyboard_dispose_db__desktop_package=desktop_package)
    disposed_mouse = DisposedMouse.objects.filter(mouse_db__desktop_package=desktop_package)
    disposed_monitor = DisposedMonitor.objects.filter(monitor_disposed_db__desktop_package_db=desktop_package)
    disposed_ups = DisposedUPS.objects.filter(ups_db__desktop_package=desktop_package)


    # just checks if any active exist (for conditional logic)
    has_active_desktop = DesktopDetails.objects.filter(id=desktop_id, is_disposed=False).exists()
    has_active_keyboards = keyboard_detailsx.exists()
    has_active_mouse = MouseDetails.objects.filter(desktop_package=desktop_package, is_disposed=False).exists()
    has_active_monitor = MonitorDetails.objects.filter(desktop_package_db=desktop_package, is_disposed=False).exists()
    has_active_ups = UPSDetails.objects.filter(desktop_package=desktop_package, is_disposed=False).exists()
    desktops_disposed_filter = DesktopDetails.objects.filter(desktop_package=desktop_package, is_disposed=False)
    

    #ownership
    # transfer_history = OwnershipTransfer.objects.filter(desktop_package=desktop_package).order_by('-transfer_date')

    return render(request, 'desktop_details_view.html', {
        'desktop_detailsx': desktop_details,

        'keyboard_detailse': keyboard_detailsx.first(),  # Assuming you only need one related keyboard detail
        'disposed_desktop': disposed_desktop,
        'disposed_keyboards': disposed_keyboards,
        'disposed_mouse' : disposed_mouse,
        'disposed_monitor' : disposed_monitor,
        'disposed_ups' : disposed_ups,
        'has_active_desktop': has_active_desktop,
        'has_active_keyboards': has_active_keyboards,
        'has_active_mouse': has_active_mouse,
        'has_active_monitor': has_active_monitor,
        'has_active_ups' : has_active_ups, 
        'monitor_detailse': monitor_detailsx.first(),
        'mouse_detailse': mouse_details.first(),
        'ups_detailse': ups_details.first(),
        'user_details' : user_details,
        'employees': employees,  # Pass the list of employees to the template
        'enduser_history': enduser_history,
        'assetowner_history': assetowner_history,
        'desktop_package': desktop_package,  # Pass desktop_package to the template for URL resolution

       
        'desktops_disposed_filter': desktops_disposed_filter,  # Added this line

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

def keyboard_update(request, keyboard_id):
    keyboard = get_object_or_404(KeyboardDetails, id=keyboard_id)
    


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
            desktop_package=keyboard.desktop_package,
            disposal_date=timezone.now()
        )
        disposed_keyboard.save()

        # Get the package ID to redirect to the same page
        desktop_package_id = keyboard.desktop_package.id
        
        # Redirect back to the desktop details view with the Keyboard tab active
        return redirect(f'/desktop_details_view/{desktop_package_id}/#pills-keyboard')

    # Fallback in case the request method is not POST
    return redirect('desktop_details_view', package_id=keyboard.desktop_package.id)



#MONITORS
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

#update desktop details
@require_POST
def update_desktop(request, pk):
    desktop = get_object_or_404(DesktopDetails, pk=pk)
    desktop.serial_no = request.POST.get('desktop_sn_form')
    desktop.brand_name = request.POST.get('desktop_brand_form')
    desktop.model = request.POST.get('desktop_model_form')
    desktop.processor = request.POST.get('desktop_proccessor_form')
    desktop.memory = request.POST.get('desktop_memory_form')
    desktop.drive = request.POST.get('desktop_drive_form')
    
    desktop.save()

    base_url = reverse('desktop_details_view', kwargs={'desktop_id': desktop.desktop_package.pk})
    return redirect(f'{base_url}#pills-desktop')

#update monitor details
@require_POST
def update_monitor(request, pk):
    monitor                     = get_object_or_404(MonitorDetails, pk=pk)
    monitor.monitor_sn_db       = request.POST.get('monitor_sn_db')
    monitor.monitor_brand_db    = request.POST.get('monitor_brand_db')
    monitor.monitor_model_db    = request.POST.get('monitor_model_db')
    monitor.monitor_size_db     = request.POST.get('monitor_size_db')
    
    monitor.save()

    base_url = reverse('desktop_details_view', kwargs={'desktop_id': monitor.desktop_package_db.pk})
    return redirect(f'{base_url}#pills-monitor')

#update keyboard details
@require_POST
def update_keyboard(request, pk):
    keyboard                    = get_object_or_404(KeyboardDetails, pk=pk)
    keyboard.keyboard_sn_db     = request.POST.get('keyboard_sn_db')
    keyboard.keyboard_brand_db  = request.POST.get('keyboard_brand_db')
    keyboard.keyboard_model_db  = request.POST.get('keyboard_model_db')
    
    keyboard.save()

    base_url = reverse('desktop_details_view', kwargs={'desktop_id': keyboard.desktop_package.pk})
    return redirect(f'{base_url}#pills-keyboard')

@require_POST
def update_mouse(request, pk):
    mouse = get_object_or_404(MouseDetails, pk=pk)
    mouse.mouse_sn_db       = request.POST.get('mouse_sn_db')
    mouse.mouse_brand_db    = request.POST.get('mouse_brand_db')
    mouse.mouse_model_db    = request.POST.get('mouse_model_db')

    mouse.save()
    base_url = reverse('desktop_details_view', kwargs={'desktop_id': mouse.desktop_package.pk})
    return redirect(f'{base_url}#pills-mouse')

@require_POST
def update_ups(request, pk):
    ups = get_object_or_404(UPSDetails, pk=pk)
    ups.ups_sn_db       = request.POST.get('ups_sn_db')
    ups.ups_brand_db    = request.POST.get('ups_brand_db')
    ups.ups_model_db    = request.POST.get('ups_model_db')
    ups.ups_capacity_db = request.POST.get('ups_capacity_db')

    ups.save()
    base_url = reverse('desktop_details_view', kwargs={'desktop_id': ups.desktop_package.pk})
    return redirect(f'{base_url}#pills-ups')


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
        ups_capacity = request.POST.get('ups_capacity')
        
        # Create a new mouse associated with the desktop package
        UPSDetails.objects.create(
            desktop_package=desktop_package,
            ups_sn_db=ups_sn,
            ups_brand_db=ups_brand,
            ups_model_db=ups_model,
            ups_capacity_db=ups_capacity
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




def add_desktop_package_with_details(request):
    employees = Employee.objects.all()  # Fetch all employees

    if request.method == 'POST':
        with transaction.atomic():  # Ensure all or nothing for database changes
            # Create Desktop Package
            desktop_package = Desktop_Package.objects.create(is_disposed=False)

            # Fetch the selected employee as end user
            enduser_id = request.POST.get('enduser_input')  
            enduser = get_object_or_404(Employee, id=enduser_id) if enduser_id else None  

             # Fetch the selected employee as asset owner
            assetowner_id = request.POST.get('assetowner_input')
            assetowner = get_object_or_404(Employee, id=assetowner_id) if assetowner_id else None

            # Create Desktop Details
            DesktopDetails.objects.create(
                desktop_package=desktop_package,
                serial_no=request.POST.get('desktop_serial_no'),
                computer_name=request.POST.get('computer_name'),
                brand_name=request.POST.get('desktop_brand_name'),
                model=request.POST.get('desktop_model'),
                processor=request.POST.get('desktop_processor'),
                memory=request.POST.get('desktop_memory'),
                drive=request.POST.get('desktop_drive'),
                desktop_Graphics=request.POST.get('desktop_Graphics'),
                desktop_Graphics_Size=request.POST.get('desktop_Graphics_Size'),
                desktop_OS=request.POST.get('desktop_OS'),
                desktop_Office=request.POST.get('desktop_Office'),
                desktop_OS_keys=request.POST.get('desktop_OS_keys'),
                desktop_Office_keys=request.POST.get('desktop_Office_keys')
            )

            MonitorDetails.objects.create(
                desktop_package_db=desktop_package,
                monitor_sn_db=request.POST.get('monitor_sn'),
                monitor_brand_db=request.POST.get('monitor_brand'),
                monitor_model_db=request.POST.get('monitor_model'),
                monitor_size_db=request.POST.get('monitor_size')    
            )

            KeyboardDetails.objects.create(
                desktop_package=desktop_package,
                keyboard_sn_db=request.POST.get('keyboard_sn'),
                keyboard_brand_db=request.POST.get('keyboard_brand'),
                keyboard_model_db=request.POST.get('monitor_model'),
                keyboard_size_db=request.POST.get('monitor_size')
            )

            MouseDetails.objects.create(
                desktop_package=desktop_package,
                mouse_sn_db=request.POST.get('mouse_sn'),
                mouse_brand_db=request.POST.get('mouse_brand'),
                mouse_model_db=request.POST.get('mouse_model')
            )

            UPSDetails.objects.create(
                desktop_package=desktop_package,
                ups_sn_db=request.POST.get('ups_sn'),
                ups_brand_db=request.POST.get('ups_brand'),
                ups_model_db=request.POST.get('ups_model'),
                ups_capacity_db=request.POST.get('ups_capacity')
            )

            DocumentsDetails.objects.create(
                desktop_package=desktop_package,
                docs_PAR=request.POST.get('par_number_input'),
                docs_Propertyno=request.POST.get('property_number_input'),
                docs_Acquisition_Type=request.POST.get('acquisition_type_input'),    
                docs_Value=request.POST.get('value_desktop_input'),
                docs_Datereceived=request.POST.get('date_received_input'),
                docs_Dateinspected=request.POST.get('date_inspected_input'),
                docs_Supplier=request.POST.get('supplier_name_input'),
                docs_Status=request.POST.get('status_desktop_input')
            )

            UserDetails.objects.create(
                desktop_package_db=desktop_package,
                user_Enduser=enduser,  # Save Employee instance, not string
                 user_Assetowner=assetowner,  # Save Employee instance, not string
            )

        return redirect('success_add_page')

    return render(request, 'add_desktop_package_with_details.html', {'employees': employees})





############### (RECENT at BASE)

def recent_it_equipment_base(request):
    recent_desktops = DesktopDetails.objects.filter(is_disposed=False).order_by('-created_at')[:10]


    return render(request, 'base.html', {
        'recent_desktops': recent_desktops,
        # 'recent_keyboards': recent_keyboards,
    })

#employees

def employee_list(request):
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('firstName')
        middle_initial = request.POST.get('middleInitial', '')
        last_name = request.POST.get('lastName')
        position = request.POST.get('position', 'Unknown')  # Default if missing
        office = request.POST.get('office', 'Unknown')  # Default if missing
        status = request.POST.get('status')

        # Create new employee
        new_employee = Employee.objects.create(
            employee_fname=first_name,
            employee_mname=middle_initial,
            employee_lname=last_name,
            employee_position=position,
            employee_office=office,
            employee_status=status
        )

        # Store the newly added employee in Django messages
        messages.success(request, f"✅ {first_name} {last_name} has been added successfully!")

        return redirect('employee_list')  # Reload the page

    employees = Employee.objects.all()
    return render(request, 'employees.html', {'employees': employees})

def update_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    
    if request.method == 'POST':
        employee.employee_fname = request.POST.get('firstName')
        employee.employee_mname = request.POST.get('middleInitial')
        employee.employee_lname = request.POST.get('lastName')
        employee.employee_position = request.POST.get('position')
        employee.employee_office = request.POST.get('office')
        employee.employee_status = request.POST.get('status')

        employee.save()
        messages.success(request, f"✅ {employee.employee_fname} {employee.employee_lname} has been added updated!")
        return redirect('employee_list')

    return render(request, 'edit_employee.html', {'employee': employee})

def delete_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    
    if request.method == 'POST':
        employee.delete()
        messages.success(request, f"✅ {employee.employee_fname} {employee.employee_lname} has been Deleted!")
        return redirect('employee_list')
    
    the_messages = get_messages(request)  # Get all messages
    return render(request, 'delete_employee.html', {'employee': employee, 'the_messages': the_messages } )

##update asset owner

def update_asset_owner(request, desktop_id):
    if request.method == 'POST':
        try:
            new_assetowner_id = request.POST.get('assetowner_input')
            new_assetowner = get_object_or_404(Employee, id=new_assetowner_id)

            # Get UserDetails instead of DesktopDetails
            user_details = get_object_or_404(UserDetails, desktop_package_db__id=desktop_id)
            old_assetowner = user_details.user_Assetowner  # Store old asset owner

            # Debugging prints
            print(f"Old Asset Owner: {old_assetowner}")  
            print(f"New Asset Owner: {new_assetowner}")  
            print(f"User Making Change: {request.user}")  

            # Update asset owner
            user_details.user_Assetowner = new_assetowner
            user_details.save()

            # Save history record
            history_entry = AssetOwnerChangeHistory(
                desktop_package=user_details.desktop_package_db,
                old_assetowner=old_assetowner if old_assetowner else None,  # Prevent NoneType errors
                new_assetowner=new_assetowner,
                changed_by=request.user,
                changed_at=timezone.now()
            )
            history_entry.save()
            print("History entry saved successfully!")  # Debugging

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': f"Error updating Asset Owner: {e}"})

    
def update_end_user(request, desktop_id):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                new_enduser_id = request.POST.get('enduser_input')
                if not new_enduser_id:
                    return JsonResponse({'success': False, 'error': 'Please select an end user'})

                new_enduser = get_object_or_404(Employee, id=new_enduser_id)
                user_details = get_object_or_404(UserDetails, desktop_package_db__id=desktop_id)
                old_enduser = user_details.user_Enduser

                # Update end user
                user_details.user_Enduser = new_enduser
                user_details.save()

                # Save history record
                EndUserChangeHistory.objects.create(
                    desktop_package=user_details.desktop_package_db,
                    old_enduser=old_enduser,
                    new_enduser=new_enduser,
                    changed_by=request.user,
                    changed_at=timezone.now()
                )

                return JsonResponse({'success': True})
                
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': f"Error updating End User: {str(e)}"
            }, status=400)
    
    return JsonResponse({
        'success': False, 
        'error': 'Invalid request method.'
    }, status=405)

# sa kadaghanan na dispose katung naay checkbox sa monitor, mouse, keyboard, ups, etc.
def dispose_desktop(request, desktop_id):
    if request.method == 'POST':
        desktop = get_object_or_404(DesktopDetails, id=desktop_id)
        reason = request.POST.get('reason')

        # Create disposal record for the desktop (without package code)
        disposal_record = DisposedDesktopDetail.objects.create(
            desktop=desktop,
            reason=reason,
            serial_no=desktop.serial_no,
            brand_name=desktop.brand_name,
            model=desktop.model,
            asset_owner=desktop.asset_owner,
            date_disposed=timezone.now()
        )

        # Handle attached monitors if checkbox was selected
        if request.POST.get('monitor'):
            monitors = MonitorDetails.objects.filter(
                desktop_package_db=desktop.desktop_package,
                is_disposed=False
            )
            for m in monitors:
                DisposedMonitor.objects.create(
                    monitor_disposed_db=m,
                    desktop_package_db=desktop.desktop_package,
                    disposed_under=disposal_record,
                    monitor_sn=m.monitor_sn_db,
                    monitor_brand=m.monitor_brand_db,
                    monitor_model=m.monitor_model_db,
                    monitor_size=m.monitor_size_db,
                    disposal_date=timezone.now()
                )
                m.is_disposed = True
                m.save()

        # Mark the desktop itself as disposed
        desktop.is_disposed = True
        desktop.save()

        # Redirect back to the desktop detail view
        return redirect('desktop_details_view', desktop_id=desktop.id)

    return redirect('desktop_list')



#THIS IS WORKING
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
            desktop_package_db=monitor.desktop_package_db,
            disposal_date=timezone.now()
        )
        disposed_monitor.save()

        # Get the package ID to redirect to the same page
        desktop_package_id = monitor.desktop_package_db.id
        
        # Redirect back to the desktop details view with the Keyboard tab active
        return redirect(f'/desktop_details_view/{desktop_package_id}/#pills-monitor')

    # Fallback in case the request method is not POST
    return redirect('desktop_details_view', package_id=monitor_id)
