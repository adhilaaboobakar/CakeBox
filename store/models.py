from django.db import models

from django.contrib.auth.models import User
from django.db.models.signals import post_save

# Create your models here.

class Category(models.Model):

    name=models.CharField(max_length=200,unique=True)
    created_date=models.DateTimeField(auto_now_add=True)
    updated_date=models.DateTimeField(auto_now=True)
    is_active=models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Flavour(models.Model):

    name=models.CharField(max_length=200,unique=True)
    created_date=models.DateTimeField(auto_now_add=True)
    updated_date=models.DateTimeField(auto_now=True)
    is_active=models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
class Occasion(models.Model):

    name=models.CharField(max_length=200,unique=True)
    created_date=models.DateTimeField(auto_now_add=True)
    updated_date=models.DateTimeField(auto_now=True)
    is_active=models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
class Cake(models.Model):

    title=models.CharField(max_length=200,unique=True)
    description=models.TextField(null=True)
    image=models.ImageField(upload_to="cake_images",default="default.jpg",null=True,blank=True)
    category_object=models.ForeignKey(Category,on_delete=models.CASCADE)
    flavour_object=models.ManyToManyField(Flavour)
    occasion_object=models.ManyToManyField(Occasion)
    created_date=models.DateTimeField(auto_now_add=True)
    updated_date=models.DateTimeField(auto_now=True)
    is_active=models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
class CakeVarient(models.Model):

    cake_object=models.ForeignKey(Cake,on_delete=models.CASCADE,related_name="cakeproduct")
    shape_options=[
        ("round","round"),
        ("square","square"),
        ("rectangle","reactangle"),
        ("heart","heart"),
        ("custom","custom")
    ]
    shape=models.CharField(max_length=200,choices=shape_options,default="round")
    weight_options=[
        (0.5,"0.5kg"),
        (1,"1kg"),
        (2,"2kg"),
        (3,"3kg"),
        (4,"4kg"),
        (5,"5kg")
    ]
    weight=models.DecimalField(max_digits=10,decimal_places=2,choices=weight_options,default=1)
    price=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    created_date=models.DateTimeField(auto_now_add=True)
    updated_date=models.DateTimeField(auto_now=True)
    is_active=models.BooleanField(default=True)


class Basket(models.Model):

    owner=models.OneToOneField(User,on_delete=models.CASCADE,related_name="cart")
    created_date=models.DateTimeField(auto_now_add=True)
    updated_date=models.DateTimeField(auto_now=True)
    is_active=models.BooleanField(default=True)

class BasketItem(models.Model):

    cake_varient_object=models.ForeignKey(CakeVarient,on_delete=models.CASCADE)
    qty=models.PositiveIntegerField(default=1)
    basket_object=models.ForeignKey(Basket,on_delete=models.CASCADE,related_name="cartitem")
    note=models.TextField(blank=True,null=True)
    created_date=models.DateTimeField(auto_now_add=True)
    updated_date=models.DateTimeField(auto_now=True)
    is_active=models.BooleanField(default=True)



def create_basket(sender,instance,created,**kwargs):
    if created:
        Basket.objects.create(owner=instance)

post_save.connect(create_basket,sender=User)



