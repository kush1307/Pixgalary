from django.contrib import admin
from .models import Pins, Category, SavePin, Board

# Register your models here.

admin.site.register(Pins)
admin.site.register(Category)
admin.site.register(SavePin)
admin.site.register(Board)
