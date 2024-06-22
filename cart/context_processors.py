'''

here will be working with two model one is Cart model. and 
the secont one is CartItem in order to make the Add to cart icon to calculate the total of quantity in the cart

when you done configure this in the setting 
and go the navbar.html  where there is a shoppin icon if you see 0 remove it and pass {{ cart_count }}

'''
from .models import Cart, CartItem
from .views import _cart_id

def counter(request):
    cart_count = 0
    #if we re inside the admin we re going to see anything here
    if 'admin' in request.path:
        return {}
    
    else:
        try:
            cart = Cart.objects.filter(cart_id=_cart_id(request))
            if request.user.is_authenticated:
                cart_items = CartItem.objects.all().filter(user=request.user)
            else:
                    
                cart_items = CartItem.objects.all().filter(cart=cart[:1])
            #we need to access the cart item quantity by looping through
            for cart_item in cart_items:
                cart_count += cart_item.quantity
                
        except Cart.DoesNotExist:  #if the cart icon is empty show 0 in the cart
            cart_count = 0
            return {'cart_count': cart_count}
        return {f'cart_count':cart_count}
            
            
            