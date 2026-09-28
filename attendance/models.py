from django.db import models
from django.utils import timezone


class Employee(models.Model):
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    designation = models.CharField(
        max_length=100,
        default='Field Worker'
    )
    joining_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class Visit(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE
    )

    visit_date = models.DateField(
        default=timezone.localdate
    )

    visit_number = models.PositiveIntegerField(
        default=1
    )

    check_in = models.DateTimeField(
        null=True,
        blank=True
    )

    check_out = models.DateTimeField(
        null=True,
        blank=True
    )

    def working_hours(self):
        if self.check_in and self.check_out:
            duration = self.check_out - self.check_in

            total_seconds = int(duration.total_seconds())

            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60

            return f"{hours} hours {minutes} minutes"

        return "Still working"

    def __str__(self):
        return f"{self.employee.name} - Visit {self.visit_number}"