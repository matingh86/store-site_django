from django.shortcuts import render ,redirect,get_object_or_404
from django.views.generic import CreateView
from . import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from.models import Product , Category,Otp,MyUser,orderitem,Order,Coupon
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import ListView,DetailView,FormView,CreateView,UpdateView,DeleteView,View,TemplateView
import random
from django.utils import timezone
import json
from django.urls import reverse
import requests
from .cart import Cart
from django.contrib.auth import get_user_model, login
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
def home(request):
    return render (request,"shop/home.html")

class registerview(CreateView):
    form_class=forms.registerform
    template_name="shop/register.html"

    success_url="/"
    def form_valid(self, form):
        # ذخیره کاربر جدید
        response = super().form_valid(form)
        user = self.object

        # ورود خودکار کاربر
        login(self.request, user)

        # ارسال پیام خوش‌آمدگویی
        messages.success(
            self.request,
            f"{user.phone} عزیز، حساب کاربری شما با موفقیت ایجاد شد و وارد شدید!",
        )
        return response
class loginview(LoginView):
    template_name="shop/login.html"
    redirect_authenticated_user=True
    authentication_form=forms.loginform

    def get_success_url(self):
        next_page=self.request.GET.get("next")
        if next_page:
            return next_page
        return reverse_lazy("shop:home")
class logoutview(LogoutView):
    next_page=reverse_lazy("shop:home")
    

class productlist(ListView):
    model=Product
    template_name="shop/product_list.html"
    context_object_name="products"
    paginate_by=6
    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            self.category = get_object_or_404(Category, slug=category_slug)
            
            subcategories = self.category.subs.all()
            categories = [self.category] + list(subcategories)
            queryset = queryset.filter(category__in=categories)

        else:
            self.category = None
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['category'] = getattr(self, 'category', None)
        return context
class productdetail(DetailView):
    model=Product
    template_name="shop/product_detail.html"
    context_object_name="product"
    slug_field="slug"
    slug_url_kwarg="slug"

class search(ListView):
    model=Product
    template_name="shop/search.html"
    context_object_name=("products")
    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            return Product.objects.filter(Q(title__icontains=query )|Q(description__icontains=query))
        else:
            return Product.objects.none()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "")
        return context
class sendotp(View):
    def get(self,request):
        return render(request,"shop/send_otp.html")
    def post(self,request):
        phone=request.POST.get("phone_number")
        if len(phone)==11:
            code=str(random.randint(10000,999999))
            print(code)

            Otp.objects.filter(phone_number=phone).delete()
            Otp.objects.create(phone_number=phone,code=code)
            request.session["otp_phone"]=phone
            return redirect("shop:checkotp")
        return render(request,"send_otp.html")




class checkotp(View):
    def get(self,request):
        if "otp_phone" not in request.session:
            return redirect("shop:send_otp")
        return render( request,"shop/checkotp.html",{"phone": request.session.get("otp_phone")},)
    def post(self,request):
        phone=request.session.get("otp_phone")
        user_code=request.POST.get("code")
        otp_che=Otp.objects.filter(phone_number=phone,code=user_code).first()
        if otp_che:
            otp_che.delete()
            del request.session["otp_phone"]
            user,_=MyUser.objects.get_or_create(phone=phone)
            login(request,user)
            return redirect("shop:home")
        return render(request,"shop/checkotp.html",{"phone":phone})
@require_POST
def cart_add(request,product_id):
    cart=Cart(request)
    product=get_object_or_404(Product,id=product_id)
    quantity=int(request.POST.get("quantity","1"))
    override=request.POST.get("override","false").lower()=="true"
    cart.add(
        product=product,
        quantity=quantity,
        override_quantity=override
    )
    return redirect("shop:cart_detail")
@require_POST
def cart_remove(request,product_id):
    cart=Cart(request)
    product=get_object_or_404(Product,id=product_id)
    cart.remove(product)
    return redirect("shop:cart_detail")
def cart_detail(request):
    cart = Cart(request)
    return render(
        request,
        "shop/cart_detail.html",
        {
            "cart": cart,
            "coupon_form": forms.couponform(),
        }
    )
@login_required(login_url='shop:login')  # 👈 برای محدود کردن تابع به کاربران لاگین شده 
def order_create(request):
    cart=Cart(request)
    if len(cart)==0:
        return redirect("shop:product_list")
    if request.method=="POST":
        form=forms.orderform(request.POST)
        if form.is_valid():
            order=form.save(commit=False)
            order.username=request.user
            if cart.coupon: 
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount # درصد یا مبلغ تخفیف
            
            order.save()
            if request.user.is_authenticated:
                
                order.username=request.user
            order.save()
            for item in cart:
                orderitem.objects.create(order=order,price=item['price'],product=item['product'],quantity=item['quantity'])
            cart.clear()
            return redirect("shop:payment_process",order_id=order.id)
    else:
        form=forms.orderform()
    return render(request,"shop/order_create.html",{"cart":cart,"form":form})

def order_detail(request,order_id):
    order=get_object_or_404(Order,id=order_id)
    return render(request,"shop/order_detail.html",{"order":order})
MERCHANT = '00000000-0000-0000-0000-000000000000'

ZP_API_REQUEST = "https://sandbox.zarinpal.com/pg/v4/payment/request.json"
ZP_API_STARTPAY = "https://sandbox.zarinpal.com/pg/StartPay/{}"
ZP_API_VERIFY = "https://sandbox.zarinpal.com/pg/v4/payment/verify.json" 

def payment_process(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    request.session['order_pay_id'] = order.id
    
    amount = order.get_cost()
    amount_in_rial = int(amount * 10)

    callback_url = request.build_absolute_uri(reverse('shop:payment_verify'))

    req_data = {
        "merchant_id": MERCHANT,
        "amount": amount_in_rial,
        "callback_url": callback_url,
        "description": f"Order #{order.id}",
    }

    req_headers = {
        "accept": "application/json", 
        "content-type": "application/json"
    }
    
    try:
        response = requests.post(url=ZP_API_REQUEST, data=json.dumps(req_data), headers=req_headers, timeout=10)
        
        print("--- ZARINPAL RESPONSE ---")
        print("Status Code:", response.status_code)
        print("Response Text:", response.text)
        print("-------------------------")

        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('data') and response_data['data'].get('code') == 100:
                authority = response_data['data']['authority']
                return redirect(ZP_API_STARTPAY.format(authority))
            else:
                errors = response_data.get('errors', {})
                return render(request, 'shop/payment_failed.html', {'error': f'خطای زرین‌پال: {errors}'})
        else:
            try:
                err_detail = response.json().get('errors')
            except:
                err_detail = response.text
                
            return render(request, 'shop/payment_failed.html', {'error': f'خطای ۴۲۲: {err_detail}'})

    except requests.exceptions.RequestException as e:
        return render(request, 'shop/payment_failed.html', {'error': f'خطای شبکه: {e}'})
def payment_verify(request):
    order_id = request.session.get('order_pay_id')
    order = get_object_or_404(Order, id=order_id)

    payment_status = request.GET.get('Status')
    authority = request.GET.get('Authority')

    if payment_status == 'OK':
        amount_in_rial = int(order.get_cost() * 10)
        req_data = {
            "merchant_id": MERCHANT,
            "amount": amount_in_rial,
            "authority": authority
        }
        req_headers = {"accept": "application/json", "content-type": "application/json"}
        
        response = requests.post(url=ZP_API_VERIFY, data=json.dumps(req_data), headers=req_headers)
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('data') and response_data['data'].get('code') in [100, 101]:
                order.paid = True
                order.save()
                
                ref_id = response_data['data']['ref_id'] 
                return render(request, 'shop/payment_success.html', {'order': order, 'ref_id': ref_id})
            else:
                return render(request, 'shop/payment_failed.html', {'error': 'تراکنش ناموفق بود یا قبلا تایید شده.'})
        else:
            return render(request, 'shop/payment_failed.html', {'error': 'خطا در تایید تراکنش'})
    else:
        return render(request, 'shop/payment_failed.html', {'error': 'پرداخت توسط کاربر لغو شد.'})
def about_us(request):
    return render(request,"shop/about_us.html")
    


def ticket(request):
    if request.method=="POST":
        form=forms.ticket(request.POST)
        if form.is_valid():
            x=form.save(commit=False)
            if request.user.is_authenticated:
                 x.user = request.user
            x.save()
            return redirect("shop:home")
    else:
        form=forms.ticket()
    
    return render (request,"shop/call_us.html",{"form":form})

def faq(request):
    return render(request,"shop/faq.html")

def profile(request):
    user=request.user
    orders=Order.objects.filter(username=request.user).order_by('-created_at')
    return render(request,"shop/profile.html",{"orders":orders,"user":user})

def update_prfile(request):
    if request.method=="POST":
       form=forms.updateprofileForm(request.POST,instance=request.user)
       if form.is_valid():
           form.save()
           return redirect("shop:profile")
    else:
           form=forms.updateprofileForm(instance=request.user)
    return render(request, 'shop/profile.html', {'form': form})
@require_POST  # فقط درخواست‌های POST را می‌پذیرد
def copounview(request):
    now=timezone.now()
    form=forms.couponform(request.POST)
    if form.is_valid():
        code=form.cleaned_data['code']
        try:
            coupon=Coupon.objects.get(code__iexact=code,valid_from__lte=now,
                valid_to__gte=now,
                active=True)
            request.session['coupon_id'] = coupon.id
            messages.success(request, "کد تخفیف با موفقیت اعمال شد.")
        except:
            request.session['coupon_id'] = None
            messages.error(request, "کد تخفیف معتبر نیست یا منقضی شده است.")
    return redirect('shop:cart_detail')  # یا آدرس صفحه سبد خرید شما
