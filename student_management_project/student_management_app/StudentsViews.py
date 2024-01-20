from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
import datetime
from .models import CustomerUser,Staffs,Courses,Subjects,Students,Attendance,AttendanceReport,LeaveReportStudent,FeedBackStudent,StudentResult

def student_home(request):
    student_obj = Students.objects.get(admin = request.user.id)
    total_attendance = AttendanceReport.objects.filter(student_id = student_obj).count()
    attendance_present = AttendanceReport.objects.filter(student_id=student_obj, status=True).count()
    attendance_absent = AttendanceReport.objects.filter(student_id=student_obj,status=True).count()
    course_obj = Courses.objects.get(id = student_obj.course_id.id)
    total_subjects = Students.objects.filter(course_id=course_obj).count()
    subject_name = []
    data_present =[]
    data_absent =[]
    subject_data = Subjects.objects.filter(course_id=student_obj.course_id)
    
    for subject in subject_data:
        attendance = Attendance.objects.filter(subject_id = subject.id)
        attendance_present_count = Attendance.objects.filter(attendance_id_in=attendance,status=True,student_id=student_obj.id).count()
        attendance_absent_count = Attendance.objects.filter(attendance_id_in=attendance,status =False,student_id=student_obj.id).count()
        subject_name.append(subject.subject_name)
        data_present.append(attendance_present_count)
        data_absent.append(attendance_absent_count)

        context ={
            "total_attendance": total_attendance,
            "attendance_present": attendance_present,
            "attendance_absent": attendance_absent,
            "total_subjects": total_subjects,
            "subject_name": subject_name,
            "data_present":data_present,
            "data_absent": data_absent
        }
        return render(request,"student_template/student_home_template.html")
    
def student_view_attendance(request):
    student = Students.objects.get(admin=request.user.id)
    course = student.course_id
    subjects = Subjects.objects.filter(course_id=course)
    context={
        "subjects":subjects,
    }
    return render(request,"student_template/student_view_attendance.html")

def student_view_attendace_post(request):
    if request.method !='POST':
        messages.error(request,'Invalid Method')
        return redirect('student_view_attendance')
    
    else:
        subject_id = request.POST.get('subject')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        start_date_parse = datetime.datetime.strptime(start_date,'%Y-%m-%d').date()
        end_date_parse = datetime.datetime.strptime(end_date,'%Y-%m-%d').date()

        subject_obj = Students.objects.get(id=subject_id)

        user_obj = CustomerUser.objects.get(id=request.user.id)

        stud_obj = Students.objects.get(admin = user_obj)

        attendance = Attendance.objects.filter(attendance_date__range=(start_date_parse,end_date_parse),subject_id=subject_obj)

        attendance_reports = AttendanceReport.objects.filter(attendance_id_in = attendance,subject_id= subject_id)

        context={
            "subject_obj" : subject_obj,
            "attendance_reports": attendance_reports
        }
        return render(request,'student_template/student_apply_leave.html',context)
    

def student_apply_leave(request):
    student_obj = Students.objects.get(admin=request.user.id)
    leave_data = LeaveReportStudent.objects.filter(student_id =student_obj)
    context ={
        "leave_data": leave_data
    }
    return render(request,'student_template/student_apply_leave.html',context)

def student_apply_leave_save(request):
    if request.method != 'POST':
        messages.error(request,'Invalid Method')
        return redirect('student_apply_leave')
    
    else:
        leave_date = request.POST.get('leave_date')
        leave_message = request.POST.get('leave_message')

        student_obj = Students.objects.get(admin=request.user.id)
        try:
            leave_report = LeaveReportStudent(student_id = student_obj,leave_date=leave_date,leave_message=leave_message,leave_status=0)
            leave_report.save()
            messages.success(request,'Applied for leave')
            return redirect('student_apply_leave')
        except:
            messages.error(request,'failed to apply leave')
            return redirect('student_apply_leave')
        