
from datetime import date
from calendar import monthrange

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.db import transaction

from .models import Employee, Visit


def dashboard(request):
    employees = Employee.objects.all().order_by("name")

    visits = Visit.objects.select_related(
        "employee"
    ).order_by("-visit_date", "-visit_number")

    active_visits = Visit.objects.filter(
        check_out__isnull=True
    ).select_related("employee").order_by("-check_in")

    active_employee_ids = set(
        active_visits.values_list("employee_id", flat=True)
    )

    latest_visits = {}

    for visit in visits:
        if visit.employee_id not in latest_visits:
            latest_visits[visit.employee_id] = visit

    context = {
        "employees": employees,
        "visits": visits,
        "active_visits": active_visits,
        "active_employee_ids": active_employee_ids,
        "latest_visits": latest_visits,
        "total_employees": employees.count(),
        "currently_working": active_employee_ids.__len__(),
        "total_visits": visits.count(),
    }

    return render(request, "attendance/dashboard.html", context)


def check_in(request, employee_id):
    if request.method != "POST":
        return redirect("dashboard")

    employee = get_object_or_404(Employee, id=employee_id)

    active_visit = Visit.objects.filter(
        employee=employee,
        check_out__isnull=True
    ).exists()

    if active_visit:
        messages.warning(request, "Employee is already checked in.")
        return redirect("dashboard")

    today = timezone.localdate()

    last_visit = Visit.objects.filter(
        employee=employee,
        visit_date=today
    ).order_by("-visit_number").first()

    next_visit_number = (
        last_visit.visit_number + 1 if last_visit else 1
    )

    Visit.objects.create(
        employee=employee,
        visit_date=today,
        visit_number=next_visit_number,
        check_in=timezone.now()
    )

    return redirect("dashboard")


def check_out(request, visit_id):
    if request.method != "POST":
        return redirect("dashboard")

    visit = get_object_or_404(Visit, id=visit_id)

    if visit.check_out is None:
        visit.check_out = timezone.now()
        visit.save(update_fields=["check_out"])

    return redirect("dashboard")
