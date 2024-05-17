from django.contrib import admin

from store.models import Category,Flavour,Occasion,Cake,CakeVarient,Shape,OrderItems,Order

admin.site.register(Category)
admin.site.register(Flavour)
admin.site.register(Occasion)
admin.site.register(Cake)
admin.site.register(CakeVarient)
admin.site.register(Shape)
admin.site.register(OrderItems)
admin.site.register(Order)
