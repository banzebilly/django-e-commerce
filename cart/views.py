from django.shortcuts import redirect, render, get_object_or_404
from store.models import Product, Variation,  variation_category_choice
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
    product_variation = []
    
    if request.method == "POST":
        for key, value in request.POST.items():
            # Check if the key is in the variation_category_choice
            if key in dict(variation_category_choice):
                print(f"Processing variation category: {key}, value: {value}")
                try:
                    # Fetch the variation based on category and value
                    variation = Variation.objects.get(
                        product=product,
                        variation_category__iexact=key,
                        variation_value__iexact=value
                    )
                    product_variation.append(variation)
                    print(f"Added variation: {variation}")
                except Variation.DoesNotExist:
                    print(f"No variation found for {key}: {value}")
                    pass
    
    cart_id = _cart_id(request)  # Get the cart session ID
    
    # Ensure a cart exists
    cart, created = Cart.objects.get_or_create(cart_id=cart_id)
    
    # Check if the cart item already exists
    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
    
    if is_cart_item_exists:
        # Get existing cart items
        cart_items = CartItem.objects.filter(product=product, cart=cart)
        
        ex_var_list = []
        id_list = []
        
        for item in cart_items:
            existing_variations = item.variations.all()
            ex_var_list.append(list(existing_variations))
            id_list.append(item.id)
        
        print(f"Existing variations: {ex_var_list}")
        
        if product_variation in ex_var_list:
            # If the variation already exists in the cart, increase the quantity
            index = ex_var_list.index(product_variation)
            item_id = id_list[index]
            cart_item = CartItem.objects.get(product=product, id=item_id)
            cart_item.quantity += 1
            cart_item.save()
        else:
            # Create a new cart item with the given variation
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart
            )
            if product_variation:
                cart_item.variations.add(*product_variation)  # Add the variations
            cart_item.save()
    else:
        # Create a new cart item if it doesn't exist
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart
        )
        if product_variation:
            cart_item.variations.add(*product_variation)  # Add the variations
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

def remove_cart(request, product_id, cart_item_id):
    """
    Remove an item from the cart or reduce its quantity by one.
    """
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    
    # Get the specific cart item for the product in the cart
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        
        # Reduce the quantity or remove the cart item
        if cart_item.quantity > 1:
            cart_item.quantity -= 1  # Decrease the quantity by 1
            cart_item.save()         # Save the updated cart item
        else:
            cart_item.delete()       # Remove the cart item if the quantity is 1
    except CartItem.DoesNotExist:
        pass

    # Redirect to the cart view to reflect changes
    return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id ):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    # Get the specific cart item for the product in the cart
    cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return  redirect('cart')

#=================functions to ==================cart page======================
def cart(request, total=0, quantity=0, cart_items=None):
    tax= 0
    grand_total = 0
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
