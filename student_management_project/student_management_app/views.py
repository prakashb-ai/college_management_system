from django.shortcuts import render,HttpResponse,redirect,HttpResponseRedirect
from django.contrib.auth import logout,authenticate,login
from .models import CustomerUser,Staffs,Students,AdminHOD
from django.contrib import messages

# Create your views here.

def home(request):
    return render(request,'home.html')

def contact(request):
    return render(request,'contact.html')

def loginUser(request):
    return render(request,'login_page.html')

def doLogin(request):
    print("here")
    email_id = request.GET.get('email')
    password = request.GET.get('password')
    print(email_id)
    print(password)
    print(request.user)
    if not (email_id and password):
        messages.error(request,'Please provide all the details !!')
        return render(request,'login_page.html')
    user = CustomerUser.objects.filter(email= email_id,password=password)

    if not user:
        messages.error(request,'Invalid Login Credentials')
        return render(request,'login_page.html')
    login(request,user)
    print(request.user)

    if user.user_type == CustomerUser.STUDENT:
        return redirect('student_home/')
    elif user.user_type == CustomerUser.STAFF:
        return redirect('staff_home/')
    elif user.user_type == CustomerUser.HOD:
        return redirect('admin_home/')
    return render(request,'home.html')

def registration(request):
    return render(request,'registration.html')

def doRegistration(request):
    first_name = request.GET.get('first_name')
    last_name = request.GET.get('last_name')
    email_id = request.GET.get('email')
    password = request.GET.get('password')
    confirm_password = request.GET.get('confirmPassword')

    print(email_id)
    print(password)
    print(confirm_password)
    print(first_name)
    print(last_name)
    if not email_id and password and confirm_password:
        messages.error(request,'Please provide all the details!!')
        return render(request,'registration.html')
    
    if password!=confirm_password:
        messages.error(request,'Both passwords should match')
        return render(request,'registration.html')
    
    is_user_exists = CustomerUser.objects.filter(email = email_id).exists()

    if is_user_exists:
        messages.error(request,'User with this email id already exists,Please proceed to login !')
        return render(request,'registation.html')
    
    user_type = get_user_type_email(email_id)

    if user_type is None:
        messages.error(request,"Please use valid format for the email id: '<username>.<staffs|student|hod>@college_domain'")
        return render(request,'registration.html')
    
    username = email_id.split('@')[0].split('.')[0]

    if CustomerUser.objects.filter(username = username).exists():
        messages.error(request,'User with this username already exists .please use different username')
        return render(request,'registation.html')
    
    user = CustomerUser()
    user.username =username
    user.email = email_id
    user.password = password
    user.user_type = user_type
    user.first_name = first_name
    user.last_name = last_name

    user.save()

    if user_type == CustomerUser.STAFF:
        Staffs.objects.create(admin = user)
    elif user_type == CustomerUser.STUDENT:
        Students.objects.create(admin = user)
    elif user_type == CustomerUser.HOD:
        AdminHOD.objects.create(admin=user)
    return render(request,'login_page.html')

def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/')

def get_user_type_email(email_id):
    try:
        email_id = email_id.split('@')[0]
        email_user_type  = email_id.split('.')[1]
        return CustomerUser.EMAIL_TO_USER_TYPE_MAP[email_user_type]
    except:
        return None


    
    