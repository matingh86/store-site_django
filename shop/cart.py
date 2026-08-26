from decimal import Decimal
from django.conf import settings
from .models import Product,Coupon


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart_key = getattr(settings, 'CART_SESSION_ID', 'cart')
        cart = self.session.get(cart_key)
        if not cart:
            cart = self.session[cart_key] = {}
        self.cart = cart
        self.coupon_id = self.session.get('coupon_id')

    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)
        
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price)
            }
        
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
            
        self.save()

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        product_ids = self.cart.keys()
        cart = self.cart.copy()
        products = Product.objects.filter(id__in=product_ids)
        
        for product in products:
            cart[str(product.id)]['product'] = product
            
        for item in cart.values():
            item['price'] = int(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def total_price(self):
        return sum(int(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        cart_key = getattr(settings, 'CART_SESSION_ID', 'cart')
        if cart_key in self.session:
            del self.session[cart_key]
            self.save()
    @property
    def coupon(self):
        """دریافت شیء کوپن در صورت وجود"""
        if self.coupon_id:
            try:
                return Coupon.objects.get(id=self.coupon_id)
            except Coupon.DoesNotExist:
                pass
        return None
    def get_discount(self):
        """محاسبه مقدار تخفیف"""
        if self.coupon:
            return (self.total_price() * Decimal(self.coupon.discount)) / Decimal(100)
        return Decimal(0)

    def get_total_price_after_discount(self):
        """محاسبه مبلغ نهایی پس از کسر تخفیف"""
        return self.total_price() - self.get_discount()