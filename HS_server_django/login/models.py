from django.db import models

class Contact(models.Model):
    account = models.CharField(max_length=50, null=False, blank=False)
    password = models.CharField(max_length=30, null=False, blank=False)
    name = models.CharField(max_length=50, null=True, blank=True)
    ip = models.CharField(max_length=20, null=True, blank=True)
    port = models.SmallIntegerField(null=True, blank=True, default=0)
    is_online = models.BinaryField(null=True, blank=True, default=b"\x00")
    photo = models.CharField(max_length=200, null=True, blank=True)
    sign = models.CharField(max_length=200, null=True, blank=True)
    birthday = models.CharField(max_length=20, null=True, blank=True)
    # gender = 
    address = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=30, null=True, blank=True)
    mail = models.CharField(max_length=50, null=True, blank=True)
    is_delete = models.BinaryField(null=True, blank=True, default=b"\x00")
    # cookie = models.CharField(max_length=100, null=True, blank=True)
    fd_file = models.IntegerField(null=True, blank=True)
    connect_time = models.CharField(max_length=25, null=True, blank=True)


    class Meta:
        db_table='Contact'

