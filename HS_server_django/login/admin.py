from django.contrib import admin
from login.models import Contact
# Register your models here.

class ContactAdmin(admin.ModelAdmin):
	list_display = ['account', 'password', 'name', "ip", "photo", "sign", 'is_online']

admin.site.register(Contact, ContactAdmin)

