from django.shortcuts import render, get_object_or_404

from cart.models import CartItem, Cart
from .models import Product, PCategory
from cart.views import _cart_id
from django.core.paginator import PageNotAnInteger,EmptyPage, Paginator


def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug:
        categories = get_object_or_404(PCategory, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        #paginator start here
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
    else:
        products = Product.objects.filter(is_available=True)
        #paginator start here
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)

     

    product_count = products.count()
    context = {
        'products': paged_products, #because we want to use paginator instead of products
        'product_count': product_count,
    }

    return render(request, 'store/store.html', context)

#=============================single product start here===========================================================
def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug) #in order to get single product we need to access the category name in the product model and slu name in category models thats why we use category__slug
        #this will check if the product added to cart  or not
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()

    except Exception as e:
        raise e
    
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
    }


    return render(request, 'store/product_detail.html', context)

#================search view functions start here===================================
from django.db.models import Q
def search(request):
    products = []
    product_count = 0  # Initialize product_count
 
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
     
        if keyword:
            # Filter products based on keyword
            products = Product.objects.order_by('-created_date').filter(
                Q(description__icontains=keyword) | Q(product_name__icontains=keyword)
            )
            product_count = products.count()
          
    
    context = {
        'products': products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)


