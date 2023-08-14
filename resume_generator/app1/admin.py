from django.contrib import admin
from app1.models import Student

# Register your models here.



class StudentAdmin(admin.ModelAdmin):
    list_display = ['id','name','address','phone_number','email','location','tech_skills']


admin.site.register(Student,StudentAdmin)