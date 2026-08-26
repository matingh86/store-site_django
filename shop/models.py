from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,PermissionsMixin
from django.urls import reverse
from cities_light.models import City
from django.core.validators import MaxValueValidator, MinValueValidator
class MyUserManager(BaseUserManager):
    def create_user(self, phone, password=None):
        """
        ایجاد و ذخیره یک کاربر معمولی با ایمیل، تاریخ تولد و رمز عبور
        """
        if not phone:
            raise ValueError('Users must have an email address')

        user = self.model(
            phone=phone
            
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone,  password=None):
        """
        ایجاد و ذخیره یک سوپر یوزر با ایمیل، تاریخ تولد و رمز عبور
        """
        user = self.create_user(
            phone,
            password=password,
            
        )

        user.is_admin = True
        user.save(using=self._db)
        return user



class MyUser(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(
        verbose_name='ادرس ایمیل',
        max_length=255,
        null=True,
        blank=True,
        unique=True,
    )
    fullname = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='نام و نام خانوادگی',
    )
    is_active = models.BooleanField(default=True)   # در کد شما default=False بود که معمولاً True است
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    phone=models.CharField(max_length=12,unique=True,verbose_name="شماره همراه")

    objects = MyUserManager()

    USERNAME_FIELD = 'phone'
   

    def __str__(self):
        return f"{self.fullname}-{self.phone}"

    def has_perm(self, perm, obj=None):
        "آیا کاربر مجوز خاصی دارد؟"
        return True

    def has_module_perms(self, app_label):
        "آیا کاربر به اپلیکیشن خاصی دسترسی دارد؟"
        return True

    @property
    def is_staff(self):
        "آیا کاربر کارمند (دسترسی به پنل ادمین) است؟"
        return self.is_admin
# Create your models here.
class Category(models.Model):
    parent=models.ForeignKey('self',null=True,blank=True,related_name='subs',on_delete=models.CASCADE)
    name=models.CharField(max_length=12)
    slug=models.SlugField(max_length=15,unique=True,allow_unicode=True)
    def __str__(self):
        return self.name
class Product(models.Model):
    title=models.CharField()
    image=models.ImageField(upload_to="products/%Y/%m/", blank=True,null=True)
    description=models.TextField(max_length=250,blank=True)
    price=models.PositiveIntegerField()
    category=models.ForeignKey(Category,on_delete=models.CASCADE,related_name="products")
    slug=models.SlugField(unique=True,allow_unicode=True)
    created_at=models.DateTimeField(auto_now_add=True)
    quantity=models.CharField()
    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.slug])
    class Meta:
        ordering=['-created_at']
class Otp(models.Model):
    phone_number=models.CharField(max_length=11)
    code=models.CharField(max_length=6)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.phone_number
CITY_CHOICES = [
    ('', '--- انتخاب شهر ---'),  
    ('تهران', 'تهران'),
    ('مشهد', 'مشهد'),
    ('اصفهان', 'اصفهان'),
    ('کرج', 'کرج'),
    ('شیراز', 'شیراز'),
    ('تبریز', 'تبریز'),
    ('قم', 'قم'),
]
class Order(models.Model):
    username=models.ForeignKey(MyUser,on_delete=models.CASCADE,related_name="orders")
    created_at=models.DateField(auto_now_add=True)
    address=models.TextField(max_length=500)
    postal_code=models.IntegerField()
    email=models.EmailField(null=True,blank=True)
    discount=models.IntegerField(default=0)
    city = models.CharField(
        max_length=50,
        choices=CITY_CHOICES,
        default='',
        verbose_name="شهر"
    )
    paid=models.BooleanField(default=False)
    def __str__(self):
        return f"{self.username}-{self.paid}-{self.created_at}"
    def get_total_cost_before_discount(self):
        return sum(item.get_cost() for item in self.items.all())

    def get_discount_amount(self):
        total = self.get_total_cost_before_discount()
        if self.discount:
            return int(total * (self.discount / 100))
        return 0

    def get_cost(self):
        total = self.get_total_cost_before_discount()
        return max(0, total - self.get_discount_amount())
class orderitem(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name="order_item")
    order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name="items")
    price=models.IntegerField()
    quantity=models.PositiveIntegerField(default=1)
    def __str__(self):
        return f"{self.product}-{self.order}"
    def get_cost(self):
        return self.price * self.quantity
class ticket(models.Model):
    user=models.ForeignKey(MyUser,on_delete=models.CASCADE,related_name="ticket",blank=True , null=True)
    fullname=models.CharField()
    email=models.EmailField(null=True,blank=True)
    subject=models.CharField(
        )
    message=models.TextField(max_length=500)
    def __str__(self):
        return f"{self.user}-{self.fullname}"
class Coupon(models.Model):
    code=models.CharField(max_length=12,unique=True)
    valid_from=models.DateTimeField()
    valid_to=models.DateTimeField()
    discount=models.PositiveIntegerField(validators=[MinValueValidator(0),MaxValueValidator(100)])
    active=models.BooleanField(default=True)
    def __str__(self):
        return f"{self.code}-{self.active}"
