from django.contrib import admin
from .models import MyUser , Product , Category,Order,orderitem,ticket,Coupon
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

class UserCreationForm(forms.ModelForm):
    """فرم ایجاد کاربر جدید (برای استفاده در ادمین)"""
    password1 = forms.CharField(label='گذرواژه', widget=forms.PasswordInput)
    password2 = forms.CharField(label='تایید گذرواژه', widget=forms.PasswordInput)

    class Meta:
        model = MyUser
        fields = ('phone','email','fullname')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """فرم ویرایش کاربر (برای استفاده در ادمین)"""
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = MyUser
        fields = ('phone', 'password',  'is_active', 'is_admin','email','fullname')

    def clean_password(self):
        return self.initial["password"]

@admin.register(MyUser)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('phone',  'is_admin','email','fullname')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        
        ('Permissions', {'fields': ('is_admin',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'password1', 'password2','email','fullname'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

class OrderItemInline(admin.TabularInline): 
    model = orderitem
    raw_id_fields = ['product']  
    extra = 0
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(ticket)
admin.site.register(Coupon)
@admin.register(Order)
class order(admin.ModelAdmin):
    list_display=["username",'paid','created_at']
    list_filter = ['paid', 'created_at']
    inlines=[OrderItemInline]
    
