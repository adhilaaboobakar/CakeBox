import razorpay

from django.shortcuts import render,redirect
from django.views.generic import View,TemplateView
from django.contrib.auth import authenticate,login,logout
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache


from store.forms import RegistrationForm,LoginForm
from store.models import Cake,CakeVarient,BasketItem,Flavour,Order,OrderItems,Shape,Basket,Occasion
from store.decorators import signin_required,owner_permission_required
from django.views.decorators.csrf import csrf_exempt




KEY_ID="rzp_test_FQXYAbDEq72ZN2"
KEY_SECRET="7pdoOLI7fpupomGLJc7NthUi"


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


@method_decorator([signin_required,never_cache],name="dispatch")  
class CakeDetailView(View):

    def get(self, request, *args, **kwargs):
        cake_id = kwargs.get("pk")
        cake = Cake.objects.get(id=cake_id)
        qs = CakeVarient.objects.filter(cake_object=cake)
        return render(request, "cakebox_chatgptdetail.html", {"cake": cake, "data": qs})
    
class HomeView(TemplateView):

    template_name="base.html"



@method_decorator([signin_required,never_cache],name="dispatch")
class AddToBasketView(View):

    def post(self,request,*args,**kwargs):
       id=kwargs.get("pk")
       cake_varient_object=CakeVarient.objects.get(id=id)
       qty=request.POST.get("qty")
       note=request.POST.get("note")
       basket=Basket.objects.get(owner=request.user)
       shape_name=request.POST.get("shape")
       shape_object=Shape.objects.get(name=shape_name)

       BasketItem.objects.create(
           cake_varient_object=cake_varient_object,
           qty=qty,
           note=note,
           basket_object=basket,
           shape_object=shape_object,
       )
       return redirect("index")
    
    

@method_decorator([signin_required,never_cache],name="dispatch")    
class BasketItemListView(View):

    def get(self,request,*args,**kwargs):
        qs=request.user.cart.cartitem.filter(is_order_placed=False)
        return render(request,"cart_list.html",{"data":qs})
    

@method_decorator([signin_required,owner_permission_required,never_cache],name="dispatch")    
class BasketItemRemoveView(View):

    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        basket_item_object=BasketItem.objects.get(id=id)
        basket_item_object.delete()
        return redirect("basket-items")
    

@method_decorator([signin_required,owner_permission_required,never_cache],name="dispatch")    
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


@method_decorator([signin_required,never_cache],name="dispatch")       
class FilterByFlavourView(View):
    
    def get(self,request,*args,**kwargs):
        flavour=kwargs.get("flavour")
        cakes=Cake.objects.filter(flavour_object__name=flavour)
        return render(request,"flavour_cakes.html",{"cakes":cakes,"flavour":flavour})
    
      


    

    

@method_decorator([signin_required,never_cache],name="dispatch")       
class CheckOutView(View):

    def get(self,request,*args,**kwargs):
        return render(request,"checkout.html")
    
    def post(self,request,*args,**kwargs):
        email=request.POST.get("email")
        phone=request.POST.get("phone")
        address=request.POST.get("address")
        payment_method=request.POST.get("payment")


        # create order instance
        order_obj=Order.objects.create(
            user_object=request.user,
            delivery_address=address,
            phone=phone,
            email=email,
            total=request.user.cart.basket_total,
            payment=payment_method
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
            if payment_method=="online" and order_obj:
                client=razorpay.Client(auth=(KEY_ID,KEY_SECRET))
                data = { "amount": int(order_obj.get_order_total*100), "currency": "INR", "receipt": "order_rcptid_11" }
                payment = client.order.create(data=data)
                print(",,,,,,,",payment)
                
                context={
                            "key":KEY_ID,
                            "order_id":payment.get("id"),
                            "amount":payment.get("amount")
                        }
                return render(request,"payment.html",{"context":context})

            return redirect("index")

@method_decorator(csrf_exempt,name="dispatch")
class PaymentVerificationView(View):
    def post(self,request,*args, **kwargs):
        print("=====",request.POST)
        client=razorpay.Client(auth=(KEY_ID,KEY_SECRET))
        data=request.POST
        
        try:
            client.utility.verify_payment_signature(data)
            print(data)
            order_obj=Order.objects.get(order_id=data.get("razorpay_order_id"))
            order_obj.is_paid=True
            order_obj.save()
            print("***Trasaction Completed***")
            
        except:
            print("!!!Transaction Failed!!!")
        return render (request,"success.html")
        

@method_decorator([signin_required,never_cache],name="dispatch")    
class SignOutView(View):

    def get(self,request,*args,**kwargs):
        logout(request)
        return redirect("signin")
 
    
class OrderSummaryView(View):

    def get(self,request,*args,**kwargs):
        qs=Order.objects.filter(user_object=request.user).exclude(status="cancelled")
        return render(request,"order_summary.html",{"data":qs})



class OrderItemRemoveView(View):
    def get(self,request,*args, **kwargs):
        id=kwargs.get("pk")
        OrderItems.objects.get(id=id).delete()
        return redirect("order-summary")
    



    




# {'id': 'order_O74fmvTHPwq3b8', 
#  'entity': 'order',
#    'amount': 120000, 
#    'amount_paid': 0, 
#    'amount_due': 120000, 
#    'currency': 'INR',
#      'receipt': 'order_rcptid_11',
#        'offer_id': None, 
#        'status': 'created',
#          'attempts': 0, 
#          'notes': [], 
#          'created_at': 1714969318}