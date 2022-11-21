from django.contrib import admin

# Register your models here.
from HS_server.models import Book, Python_doc, English_doc, College_doc, Python_module, Health_Sensing_doc, HWTE_Station_doc


class BookInfoAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'author', "path"]

class Python_docAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', "path", "order_id"]
    
class English_docAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', "path", "order_id", "is_secret", "is_delete"]

class College_docAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', "path", "order_id"]

class Python_moduleAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', "path", "order_id"]

class Health_Sensing_docAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', "path", "order_id", "is_secret", "is_delete"]

class HWTE_Station_docAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', "path", "order_id", "is_secret", "is_delete"]


admin.site.register(Book, BookInfoAdmin)
admin.site.register(Python_doc, Python_docAdmin)
admin.site.register(English_doc, English_docAdmin)
admin.site.register(College_doc, College_docAdmin)

admin.site.register(Python_module, Python_moduleAdmin)
admin.site.register(Health_Sensing_doc, Health_Sensing_docAdmin)
admin.site.register(HWTE_Station_doc, HWTE_Station_docAdmin)