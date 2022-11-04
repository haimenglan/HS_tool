from django.db import models

# Create your models here.
class Wallpaper(models.Model):
    name = models.CharField(max_length=100)
    path = models.CharField(max_length=100, default="")
    img_format = models.CharField(max_length=10, default="")
    img_type = models.CharField(max_length=10, default="")
    order_id = models.IntegerField(null=True, blank=True)
    is_secret = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    def __str__(self):
        # 打印对象的时候，返回名字？
        return self.name


