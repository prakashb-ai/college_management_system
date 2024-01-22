from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json 

from .models import CustomUser,Staffs,Courses,Subjects,Students,SessionYearModel,Attendance,AttendanceReport,LeaveReportStaff,FeedBackStaffs,StudentResult


def staff_home(request):
    print(request.user.id)
    subjects = Subjects.objects.filter(staff_id= request.user.id)
    print(subjects)
    course_id_list =[]
    for subject in subjects:
        course = Courses.objects.get(id=subjects.course_id.id)
        course_id_list.append(course.id)
    
    final_course =[]

    for course_id in course_id_list:
        if course_id not in final_course:
            final_course.append(course_id)
    
    print(final_course)
    students_count = Students.objects.filter(couse_id_in = final_course).count()
    subject_count = subject.count()
    print(subject_count)
    print(students_count)

    attendance_count = Attendance.objects.filter(subject_id_in = subject).count()

    print(request.user.user_type)
    staff = Staffs.objects.get(admin = request.user.id)
    leave_count = LeaveReportStaff.objects.filter(staff_id=staff.id,leave_status=1).count()


    subject_list =[]
    attendance_list =[]
    
    for subject in subjects:
        attendance_count1 = Attendance.objects.filter(subject_id=subject.id).count()
        subject_list.append(subject.subject_name)
        attendance_list.append(attendance_count1)

    students_attendance = Students.objects.filter(course_id_in=final_course)
    student_list =[]
    student_list_attendance_present =[]
    student_list_attendance_absent =[]

    for student in students_attendance:
        attendance_present_count = AttendanceReport.objects.filter(status=True,student_id=student.id).count()
        attendance_absent_count = AttendanceReport.objects.filter(status=False,student_id=student.id).count()
        student_list.append(student.admin.first_name+" "+student.admin.last_name)
        student_list_attendance_present.append(attendance_present_count)
        student_list_attendance_absent.append(attendance_absent_count)

    
    context ={
        "student_count": students_count,
        "attendance_count": attendance_count,
        "leave_count": leave_count,
        "subject_count": subject_count,
        "subject_list": subject_list,
        "attendance_list": attendance_list,
        "student_list": student_list,
        "attendance_present_list": student_list_attendance_present,
        "attendance_absent_list": student_list_attendance_present
    }
    return render(request,"staff_template/staff_home_template.html",context)

def staff_take_attendance(request):
    subjects = Subjects.objects.filter(staff_id = request.user.id)
    session_years = SessionYearModel.objects.all()
    context ={
        "subjects": subjects,
        "session_years": session_years,
    }
    return render(request,"staff_template/take_attendance_template.html",context)

def staff_apply_leave(request):
    print(request.user.id)
    staff_obj = Staffs.objects.get(admin=request.user.id)
    leave_data = LeaveReportStaff.objects.filter(staff_id=staff_obj)
    context = {
        "leave_data": leave_data
    }
    return render(request, "staff_template/staff_apply_leave_template.html", context)


def staff_apply_leave_save(request):
    if request.method !='POST':
        messages.error(request,'Invalid method')
        return redirect('staff_apply_leave')
    else:
        leave_date = request.POST.get('leave_date')
        leave_message = request.POST.get('leave_message')

        staff_obj = Staffs.objects.get(admin = request.user.id)
        try:
            leave_report = LeaveReportStaff(staff_id = staff_obj,leave_date = leave_date,leave_message=leave_message,leave_status=0)
            leave_report.save()
            messages.success(request,'Applied for leave')
            return redirect('staff_apply_leave')
        except:
            messages.error(request,'failed to apply leave')
            return redirect('staff_apply_leave')
        
def staff_feedback(request):
  return render(request, "staff_template/staff_feedback_template.html")

def staff_feedback_save(request):
    if request.method !='POST':
        messages.error(request,'Invalid method')
        return redirect('staff_feedback')
    else:
        feedback = request.POST.get('feedback_message')
        staff_obj = Staffs.objects.get(admin = request.user.id)

        try:
            add_feedback = FeedBackStaffs(staff_id = staff_obj,feedback = feedback,feedback_reply='')
            add_feedback.save()

            messages.success(request,'Feedback sent')
            return redirect('staff_feedback')
        except:
            messages.error(request,'Failed to send feedback')
            return redirect('staff_feedback')

@csrf_exempt
def get_students(request):
    subject_id = request.POST.get('subject')
    session_year = request.POST.get('session_year')

    subject_model = Subjects.objects.get(id=subject_id)
    session_model = SessionYearModel.objects.get(id=session_year)

    students = Students.objects.filter(course_id = subject_model.course_id,session_year_id=session_model)

    list_data =[]
    for student in students:
        data_small ={
            "id":student.admin.id,
            "name": student.admin.first_name+" "+student.admin.last_name
            }
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data),content_type="applicaion/json",safe =False)


@csrf_exempt
def save_attendance_data(request):
    student_ids = request.POST.get('student_ids')
    subject_id = request.POST.get('subject_id')
    attendance_date = request.POST.get('attendance_date')
    session_year_id = request.POST.get('session_year_id')

    subject_model = Subjects.objects.get(id = subject_id)
    session_year_model = SessionYearModel.objects.get(id=session_year_id)

    json_student = json.loads(student_ids)

    try:
        attendance = Attendance(subject_id = subject_model,attendance_date=attendance_date,session_year_id=session_year_id)
        attendance.save()

        for stud in json_student:

            student = Students.objects.get(admin=stud['id'])
            attendance_report = AttendanceReport(student_id = student,attendance_id = attendance,status= stud['status'])

            attendance_report.save()
            return HttpResponse('ok')
    except:
        return HttpResponse('error')


def staff_update_attendance(request):
    subjects = Subjects.objects.filter(staff_id = request.user.id)
    session_years = SessionYearModel.objects.all()

    context ={
        "subjects": subjects,
        "session_years": session_years
    }
    return render(request,'staff_template/update_attendance_template.html',context)


        
@csrf_exempt
def get_attendance_dates(request):
    subject_id = request.POST.get('subject')
    session_year = request.POST.get('session_year_id')

    subject_model = Subjects.objects.get(id = subject_id)
    session_model = SessionYearModel.objects.get(id = session_year)

    attendance = Attendance.objects.filter(subject_id=subject_model,session_year_id= session_model)
    list_data =[]

    for attendance_single in attendance:
        data_small ={
            "id":attendance_single.id,
            "attendance_date":str(attendance_single.attendance_date),
            "session_year_id": attendance_single.session_year_id.id
        }
        list_data.append(data_small)
    
    return JsonResponse(json.dumps(list_data),content_type ="application/json",safe =False)

@csrf_exempt
def get_attendance_student(request):
    attendance_date = request.POST.get('attendance_date')
    attendance = Attendance.objects.get(id=attendance_date)

    attendance_date = AttendanceReport.objects.filter(attendance_id = attendance)

    list_data =[]

    for student in attendance_date:
        data_small={
            "id":student.student_id.admin.id,
            "name": student.student_id.admin.first_name+" "+student.student_id.admin.last_name,"status": student.status
        }
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)

@csrf_exempt
def update_attendance_data(request):
    student_ids = request.POST.get('student_ids')
    attendance_date = request.POST.get('attendance_date')
    attendance = Attendance.objects.get(id=attendance_date)

    json_student = json.loads(student_ids)

    try:
        for stud in json_student:
            student = Students.objects.get(admin = stud['id'])
            attendance_report = AttendanceReport.objects.get(student_id=student,attendance_id=attendance)
            attendance_report.status=stud['status']

            attendance_report.save()

        return HttpResponse('ok')
    except:
        return HttpResponse('error')

def staff_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    staff = Staffs.objects.get(admin = user)

    context ={
        "user": user,
        "staff": staff,
    }

    return render(request,"staff_template/staff_profile.html",context)

def staff_profile_update(request):
    if request.method !='POST':
        messages.error(request,'Invalid method!')
        return redirect('staff_profile')
    
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        address = request.POST.get('address')
    try:
        CustomUser = CustomUser.objects.get(id=request.user.id)
        CustomUser.first_name = first_name
        CustomUser.last_name = last_name
        if password !=None and password !='':
            CustomUser.set_password(password)
        CustomUser.save()

        staff = Staffs.objects.get(admin = CustomUser.id)
        staff.address = address
        staff.save()

        messages.success(request,'profile updated successfully')
        return redirect('staff_profile')
    
    except:
        messages.error(request,'failed to update profile')
        return redirect('staff_profile')

def staff_add_result(request):
    subjects = Subjects.objects.filter(staff_id = request.user.id)
    session_year = SessionYearModel.objects.all()
    context ={
        "subjects": subjects,
        "session_years": session_year,
    }
    return render(request,"staff_template/add_result_template.html",context)


def staff_add_result_save(request):
    if request.method !='POST':
        messages.error(request,'Invalid method')
        return redirect('staff_add_result')
    
    else:
        student_admin_id = request.POST.get('student_list')
        assignment_marks = request.POST.get('assignment_marks')
        exam_marks = request.POST.get('exam_marks')
        subject_id = request.POST.get('subject')

        student_obj = Students.objects.get(admin=student_admin_id)
        subject_obj = Subjects.objects.get(id=subject_id)

        try:
            check_exit = StudentResult.objects.filter(subject_id = subject_obj,student_id = student_obj)

            if check_exit:
                result = StudentResult.objects.get(subject_id=subject_obj,student_id = student_obj)
                result.subject_assignement_marks = assignment_marks
                result.subject_exam_marks = exam_marks
                result.save()
                messages.success(request,'result updated successfully')
                return redirect('staff_add_result')
            else:
                result = StudentResult(student_id = student_obj,
                                       subject_id = subject_obj,
                                       subject_exam_marks = exam_marks,
                                       subject_assignment_marks= assignment_marks)
                result.save()
                messages.success(request,'Result addedd successfully')
                return redirect('staff_add_result')
            
        except:
            messages.error(request,'failed to add result')
            return redirect('staff_add_result')
        




         


