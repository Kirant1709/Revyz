from django.db import models
from django.db.models.signals import post_save

# Create your models here.

class Student(models.Model):
    TECH_SKILLS = [("Python", "Python"),("Java", "Java"),("Ruby", "Ruby"),("Docker","Docker"),("Node","Node"),("JS","JS")]
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    phone_number = models.IntegerField()
    email = models.EmailField()
    location = models.CharField(max_length=50)
    tech_skills = models.CharField(choices=TECH_SKILLS,max_length=10)


    def __str__(self):
        return str(self.name)
    
     
        
    
#django signal to notify whenever we create new entry to db
def create_student(sender, instance, created, **kwargs):
        print("New student added to the database")

post_save.connect(receiver=create_student, sender=Student)            
