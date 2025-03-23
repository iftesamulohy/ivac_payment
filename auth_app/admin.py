from django.contrib import admin

from auth_app.models import IVACLoginInfo, PaymentInfo

# Register your models here.
admin.site.register(IVACLoginInfo)
admin.site.register(PaymentInfo)