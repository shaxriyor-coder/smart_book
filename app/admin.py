from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(User)
admin.site.register(Janr)
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    pass
admin.site.register(Ijaradagi_kitob_infosi)