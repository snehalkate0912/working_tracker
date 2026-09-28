from django.contrib import admin
from .models import Employee, Visit


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'mobile',
        'designation',
        'joining_date',
    )


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'employee',
        'visit_date',
        'visit_number',
        'check_in',
        'check_out',
    )