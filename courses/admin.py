from django.contrib import admin

from .models import User, Course, CategoCourse, AddCourse, ReviCourse, DistribCourse, Order, OrderCourse
# Register your models here.

admin.site.register(User)
admin.site.register(DistribCourse)
admin.site.register(Course)
admin.site.register(CategoCourse)
admin.site.register(AddCourse)
admin.site.register(ReviCourse)
admin.site.register(Order)
admin.site.register(OrderCourse)
