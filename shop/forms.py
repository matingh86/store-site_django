from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from .models import MyUser,Order,ticket,Coupon
class registerform(UserCreationForm):
    email=forms.EmailField(required=True,label="email")
    class Meta:
        model=MyUser
        fields = ('phone', 'email')
class loginform(AuthenticationForm):
    username=forms.CharField(label='شماره همراه',
        widget=forms.TextInput(attrs={'placeholder': 'شماره همراه خود را وارد کنید', 'class': 'form-control'}))
    password=forms.PasswordInput(attrs={'placeholder': 'رمز عبور را وارد کنید', 'class': 'form-control'})
class orderform(forms.ModelForm):
    class Meta:
     model=Order
     fields=['address','postal_code','city','email']
     widgets = {
 
            'email': forms.EmailInput( attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.Select(attrs={'class': 'form-select'}),
        }
class ticket(forms.ModelForm):
    
    class Meta:
        model = ticket
        fields = ("fullname","email","subject","message")
        widgets = {
            'fullname': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نام و نام خانوادگی خود را وارد کنید'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@gmail.com'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'موضوع پیام را بنویسید'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'پیام خود را اینجا بنویسید...'
            }),
        }
        
        labels = {
            'fullname': 'نام و نام خانوادگی',
            'email': 'ایمیل',
            'subject': 'موضوع',
            'message': 'متن پیام',
        }

class updateprofileForm(forms.ModelForm):
    class Meta:
        model = MyUser
        fields = ("email", "fullname")
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ایمیل خود را وارد کنید'}),
            'fullname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام و نام خانوادگی'}),
        }
        labels = {
            'email': 'آدرس ایمیل',
            'fullname': 'نام و نام خانوادگی',
        }

class couponform(forms.Form):
    code=forms.CharField(widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'کد تخفیف را وارد کنید'
        }),
        label='کد تخفیف')
        