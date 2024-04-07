from django.contrib import admin
from .models import Pilot, Group, Mouse, TumorVolume, IvisData

admin.site.register(Pilot)
admin.site.register(Group)
admin.site.register(Mouse)
admin.site.register(TumorVolume)
admin.site.register(IvisData)
