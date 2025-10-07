from django.contrib import admin
from .models import * 

# Register your models here.
admin.site.register(User)
admin.site.register(Property)
admin.site.register(RentalApplication)
admin.site.register(Student_profile)
admin.site.register(Degrees)
admin.site.register(Universities)
admin.site.register(Lister_type)
admin.site.register(PropertyView)