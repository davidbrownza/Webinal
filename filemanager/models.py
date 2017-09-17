from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save

class FileManagerSettings(models.Model):
    HomeDirectory = models.TextField(default="/")
    AceTheme = models.CharField(max_length=30, default="chrome")
    FontSize = models.IntegerField(default=11)
    AutoCompleteInd = models.BooleanField(default=True)
    
    ServerPass = models.CharField(max_length=1024, null=True, blank=True)    
    User = models.OneToOneField(User)
    
    class Meta:
        db_table = "FileManagerSettings"


class Tab(models.Model):
    User = models.ForeignKey(User)
    FilePath = models.TextField()
    LastSave = models.IntegerField(null=True, blank=True)
    
    class Meta:
        unique_together = ("User", "FilePath")
        db_table = "Tabs"
    
    
def create_settings(sender, instance, created, **kwargs):  
    if created:
       profile, created = FileManagerSettings.objects.get_or_create(User=instance)
	

post_save.connect(create_settings, sender=User) 
