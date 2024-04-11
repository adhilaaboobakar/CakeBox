from django.contrib import admin

from store.models import Category,Flavour,Occasion,Cake,CakeVarient

admin.site.register(Category)
admin.site.register(Flavour)
admin.site.register(Occasion)
admin.site.register(Cake)
admin.site.register(CakeVarient)
