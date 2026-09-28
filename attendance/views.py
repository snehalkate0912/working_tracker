from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.utils import timezone
from django.contrib import messages

from .models import Employee, Visit


# =========================================================
# DASHBOARD
# =========================================================

def dashboard(request):

    employees = Employee.objects.all()

    visits = Visit.objects.select_related(
        'employee'
    ).order_by(
        '-visit_date',
        '-visit_number'
    )

    # Currently working visits
    active_visits = Visit.objects.filter(
        check_out__isnull=True
    ).select_related(
        'employee'
    ).order_by(
        '-check_in'
    )

    # Employee IDs who are currently working
    active_employee_ids = [
        visit.employee_id
        for visit in active_visits
    ]

    # Latest visit for every employee
    employee_data = []

    for employee in employees:

        latest_visit = Visit.objects.filter(
            employee=employee
        ).order_by(
            '-visit_date',
            '-visit_number'
        ).first()

        employee_data.append({
            'employee': employee,
            'latest_visit': latest_visit,
            'is_working': employee.id in active_employee_ids
        })

    return render(
        request,
        'attendance/dashboard.html',
        {
            'employees': employees,
            'visits': visits,
            'active_visits': active_visits,
            'active_employee_ids': active_employee_ids,
            'employee_data': employee_data,
        }
    )


# =========================================================
# CHECK IN
# =========================================================

def check_in(request, employee_id):

    employee = get_object_or_404(
        Employee,
        id=employee_id
    )

    today = timezone.localdate()

    # Check if employee is already working
    active_visit = Visit.objects.filter(
        employee=employee,
        check_out__isnull=True
    ).order_by(
        '-check_in'
    ).first()

    if active_visit:

        messages.warning(
            request,
            f'{employee.name} is already checked in.'
        )

        return redirect('dashboard')

    # Count today's visits
    visit_count = Visit.objects.filter(
        employee=employee,
        visit_date=today
    ).count()

    # Current date and time
    current_time = timezone.now()

    # Create new visit
    Visit.objects.create(
        employee=employee,
        visit_date=today,
        visit_number=visit_count + 1,
        check_in=current_time
    )

    # No success message after check-in
    return redirect('dashboard')


# =========================================================
# CHECK OUT
# =========================================================

def check_out(request, employee_id):

    employee = get_object_or_404(
        Employee,
        id=employee_id
    )

    # Find active visit
    visit = Visit.objects.filter(
        employee=employee,
        check_out__isnull=True
    ).order_by(
        '-check_in'
    ).first()

    if visit:

        # Save checkout time
        visit.check_out = timezone.now()
        visit.save()

    else:

        messages.warning(
            request,
            f'{employee.name} has no active visit.'
        )

    return redirect('dashboard')


# =========================================================
# VISIT HISTORY
# =========================================================

def visit_history(request):

    # Get all visits
    visits = Visit.objects.select_related(
        'employee'
    ).order_by(
        '-visit_date',
        '-visit_number'
    )

    # Number of employees currently working
    working_now = Visit.objects.filter(
        check_out__isnull=True
    ).values(
        'employee'
    ).distinct().count()

    # Total employees
    employee_count = Employee.objects.count()

    return render(
        request,
        'attendance/visit_history.html',
        {
            'visits': visits,
            'working_now': working_now,
            'employee_count': employee_count,
        }
    )
from calendar import monthrange
from datetime import date
from django.db.models import Q


def attendance(request):

    employees = Employee.objects.all()

    today = timezone.localdate()

    # Selected month and year
    selected_month = int(
        request.GET.get('month', today.month)
    )

    selected_year = int(
        request.GET.get('year', today.year)
    )

    # Number of days in selected month
    total_days = monthrange(
        selected_year,
        selected_month
    )[1]

    # Monday to Saturday = Working Day
    working_days = 0

    for day in range(1, total_days + 1):

        current_date = date(
            selected_year,
            selected_month,
            day
        )

        # Sunday = 6
        if current_date.weekday() != 6:
            working_days += 1

    employee_data = []

    for employee in employees:

        # Visits of this employee in selected month
        visits = Visit.objects.filter(
            employee=employee,
            visit_date__year=selected_year,
            visit_date__month=selected_month
        )

        # Unique dates on which employee was present
        present_dates = visits.values_list(
            'visit_date',
            flat=True
        ).distinct()

        present_days = len(present_dates)

        absent_days = working_days - present_days

        if working_days > 0:

            attendance_percentage = round(
                (present_days / working_days) * 100
            )

        else:

            attendance_percentage = 0

        employee_data.append({
            'employee': employee,
            'present_days': present_days,
            'absent_days': absent_days,
            'working_days': working_days,
            'attendance_percentage': attendance_percentage,
        })

    return render(
        request,
        'attendance/attendance.html',
        {
            'employee_data': employee_data,
            'working_days': working_days,
            'selected_month': selected_month,
            'selected_year': selected_year,
        }
    )