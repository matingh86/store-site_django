from .models import Product , Category,orderitem,Order
from .cart import Cart


def cart_processor(request):
    return{
        "cart":Cart(request)
    }


def category_processor(request):
    return{
        "categories":Category.objects.all()

    }
def product_processor(request):
    return{
        "product":Product.objects.all()
    }
def order_processor(request):
    return{
        "orders":Order.objects.all()
    }