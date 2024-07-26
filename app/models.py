from django.db import models

# Create your models here.
class Vulnerabilities(models.Model):

    id = models.AutoField(primary_key=True)
    cve_id = models.CharField(max_length=20, unique=True, blank=False, null=False)
    name = models.CharField(max_length=50, blank=False, null=False)
    criticality = models.CharField(max_length=20, blank=False, null=False)
    status = models.CharField(max_length=20, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_update_at = models.DateTimeField(auto_now=True)
    description_vulnerabilitie = models.TextField(max_length=500, null=True)
    solution_date = models.DateTimeField(blank=False, null=False)
    description_solution = models.TextField(max_length=500, null=True)

    class Meta:
        ordering = ['-solution_date']