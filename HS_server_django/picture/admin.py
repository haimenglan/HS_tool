from django.contrib import admin
from picture.models import Wallpaper
# Register your models here.

class WallpaperAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'path', "img_format", "img_type"]

admin.site.register(Wallpaper, WallpaperAdmin)