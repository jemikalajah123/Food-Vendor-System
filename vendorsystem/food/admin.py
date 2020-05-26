from django.contrib import admin
from . models import Vendor,Customer,Menu,Status,Order,Notification,Auth,Cart,OrderContent

# Register your models here.
admin.site.register(Vendor)
admin.site.register(Customer)
admin.site.register(Menu)
admin.site.register(Status)
admin.site.register(Order)
admin.site.register(Notification)
admin.site.register(Auth)
admin.site.register(OrderContent)
admin.site.register(Cart)