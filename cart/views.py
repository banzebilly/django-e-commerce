from django.shortcuts import redirect, render, get_object_or_404
from store.models import Product
from .models import Cart, CartItem

# Create your views here.
'''
Django sessions allow you to store and retrieve arbitrary data on a per-site-visitor basis.
Each visitor gets a unique session key stored as a cookie in their browser.
The session data itself is stored on the server (database, cache, or file system).

'''
from django.shortcuts import redirect, get_object_or_404
from .models import Product, Cart, CartItem

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

#=================functions to ==================add cart ======================
def add_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)  # Ensure the product exists
    
    cart_id = _cart_id(request)  # Get the cart session ID
    
    # Ensure a cart exists
    cart, created = Cart.objects.get_or_create(cart_id=cart_id)
    
    # Add or update the cart item
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart,
        )
        cart_item.save()
    # Redirect to the cart page
    return redirect('cart')
#=================functions to ==================remove cart======================
def _cart_id(request):
    """
    Retrieve or create a unique session ID for the cart.
    """
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def remove_cart(request, product_id):
    """
    Remove an item from the cart or reduce its quantity by one.
    """
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    
    # Get the specific cart item for the product in the cart
    cart_item = CartItem.objects.get(product=product, cart=cart)
    
    # Reduce the quantity or remove the cart item
    if cart_item.quantity > 1:
        cart_item.quantity -= 1  # Decrease the quantity by 1
        cart_item.save()         # Save the updated cart item
    else:
        cart_item.delete()       # Remove the cart item if the quantity is 1

    # Redirect to the cart view to reflect changes
    return redirect('cart')

def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    # Get the specific cart item for the product in the cart
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return  redirect('cart')

#=================functions to ==================cart page======================
def cart(request, total=0, quantity=0, cart_items=None):
    try:
        # Get the cart using the session cart_id
        cart = Cart.objects.get(cart_id=_cart_id(request))
        # Get all active cart items for this cart
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        # Loop through each cart item to calculate the total and quantity
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax

    except Cart.DoesNotExist:
        # If the cart does not exist, initialize with default empty values
        cart_items = []
        total = 0
        quantity = 0

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total
    }

    return render(request, 'cart/cart.html', context)
