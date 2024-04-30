from django.shortcuts import render,redirect
from django.views.generic import View,TemplateView
from django.contrib.auth import authenticate,login
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from store.forms import RegistrationForm,LoginForm
from store.models import Cake,CakeVarient,BasketItem,Flavour,Order,OrderItems
from store.decorators import signin_required,owner_permission_required



class SignUpView(View):

    def get(self,request,*args,**kwargs):
        form=RegistrationForm()
        return render(request,"register.html",{"form":form})
    
    def post(self,request,*args,**kwargs):
        form=RegistrationForm(request.POST)
        print("test block1")
        if form.is_valid():
            form.save()
            return redirect("signin")
        
        return render(request,"login.html",{"form":form})


class SignInView(View):

    def get(self,request,*args,**kwargs):
        form=LoginForm()
        return render(request,"login.html",{"form":form})
    
    def post(self,request,*args,**kwargs):
        form=LoginForm(request.POST)
        if form.is_valid():
            u_name=form.cleaned_data.get("username")
            pwd=form.cleaned_data.get("password")
            user_object=authenticate(username=u_name,password=pwd)
            if user_object:
                login(request,user_object)
                return redirect("index")
        return render(request,"login.html",{"form":form})
    
class IndexView(View):
    
    def get(self,request,*args,**kwargs):
        qs=Cake.objects.all()
        return render(request,"index.html",{"data":qs})
    
class CakeDetailView(View):

    def get(self, request, *args, **kwargs):
        cake_id = kwargs.get("pk")
        cake = Cake.objects.get(id=cake_id)
        cake_variants = CakeVarient.objects.filter(cake_object=cake)
        return render(request, "cakebox_chatgptdetail.html", {"cake": cake, "cake_variants": cake_variants})
    
class HomeView(TemplateView):

    template_name="base.html"


class AddToBasketView(View):

    def post(self,request,*args,**kwargs):
       id=kwargs.get("pk")
       cake_varient_object=CakeVarient.objects.get(id=id)
       qty=request.POST.get("qty")
       note=request.POST.get("note")
       basket=request.user.cart

       BasketItem.objects.create(
           cake_varient_object=cake_varient_object,
           qty=qty,
           note=note,
           basket_object=basket
       )

       return redirect("index")
    
class BasketItemListView(View):

    def get(self,request,*args,**kwargs):
        qs=request.user.cart.cartitem.filter(is_order_placed=False)
        return render(request,"cart_list.html",{"data":qs})
    

class BasketItemRemoveView(View):

    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        basket_item_object=BasketItem.objects.get(id=id)
        basket_item_object.delete()
        return redirect("basket-items")
    

class CartItemUpdateQuantityView(View):
    
    def post(self,request,*args,**kwargs):
        action=request.POST.get("counterButton")
        print(action)
        id=kwargs.get("pk")
        basket_item_object=BasketItem.objects.get(id=id)
        if action=="+":
            basket_item_object.qty+=1
        else:
            basket_item_object.qty-=1
        basket_item_object.save()
        return redirect("basket-items")
    
class FilterByFlavourView(View):
    
    def get(self,request,*args,**kwargs):
        flavour=kwargs.get("flavour")
        cakes=Cake.objects.filter(flavour_object__name=flavour)
        return render(request,"flavour_cakes.html",{"cakes":cakes,"flavour":flavour})
    
class CheckOutView(View):

    def get(self,request,*args,**kwargs):
        return render(request,"checkout.html")
    
    def post(self,request,*args,**kwargs):
        email=request.POST.get("email")
        phone=request.POST.get("phone")
        address=request.POST.get("address")


        # create order instance
        order_obj=Order.objects.create(
            user_object=request.user,
            delivery_address=address,
            phone=phone,
            email=email,
            total=request.user.cart.basket_total
        )
        # creating order item instance
        try:

            basket_items=request.user.cart.cart_items
            for bi in basket_items:
                 OrderItems.objects.create(
                order_object=order_obj,
                basket_item_object=bi
            )
            bi.is_order_placed=True
            bi.save()
        except:

            order_obj.delete()
        finally:
            return redirect("index")


