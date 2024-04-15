from django.shortcuts import render,redirect
from django.views.generic import View,TemplateView
from django.contrib.auth import authenticate,login
from store.forms import RegistrationForm,LoginForm
from store.models import Cake,CakeVarient,BasketItem


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


class AddToBasketView( View):

    def post(self,request,*args,**kwargs):
       id=kwargs.get("pk")
       cake_varient_object=CakeVarient.objects.get(id=id)
       qty=request.POST.get("qty")
       flavour_object=request.POST.get("flavour") 
       occasion_object=request.POST.get("occasion")
       note=request.POST.get("note")

       BasketItem.objects.create(
           cake_varient_object=cake_varient_object,
           qty=qty,
           basket_object=request.user.cart,
           flavour_object=flavour_object,
           occasion_object=occasion_object,
           note=note
       )

       return redirect("index")



