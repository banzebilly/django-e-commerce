
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from cart.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, Payment, OrderProduct
import json
from store.models import Product
#redering the message to the user
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

def place_order(request, total=0, quantity=0,):
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside Order table
            data = Order()#instance
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR') # to  get the current IP
            data.save()
            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #20210305
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')

#=================================payment view===============================================
import json
def payments(request):

    body = json.loads(request.body)

    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])
    
    #store transaction detail inside payment models
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        #in order to get the amout paid is inside the order model ,you should make a query
        amount_paid = order.order_total,
        status = body['status'],

    )
    payment.save()
    order.payment = payment
    #done with the payment
    order.is_ordered=True
    order.save()
    #move the cart items to order product table
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered= True
        orderproduct.save()
        #=========for saving variation is manytomanyfield need to save the objects and then asign the value====================
        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()
        #this part is done 

        #========reduce the quantity of the sold product=========================
        product = Product.objects.get(id=item.product_id)
        product.stock  -= item.quantity
        product.save()

#====================clear the cart item this clear cart it should be outside of the forloop add to cart icon==========================================
    CartItem.objects.filter(user=request.user).delete()

    #send order received to email to customer
    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/order_received_email.html', {
        'user': request.user,
        'order': order,
             
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()


    #send order number and transanction id back to  sen data vai  jsonResponse
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,

    }
    

    return JsonResponse(data)


def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    # Debug output for URL parameters
    print(f"Received order_number: {order_number}")
    print(f"Received transID: {transID}")

    try:
        # Fetch the order with the given order number and is_ordered=True
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        print(f"Order found: {order}")  # Debug output for the order

        # Fetch the products related to this order
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        print(f"Ordered products: {ordered_products.count()}")  # Debug output for ordered products

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        # Fetch the payment details
        payment = Payment.objects.get(payment_id=transID)
        print(f"Payment found: {payment}")  # Debug output for the payment

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)

    except Order.DoesNotExist:
        print("Order does not exist or is not marked as ordered.")  # Debug output for order error
        return redirect('home')
    except Payment.DoesNotExist:
        print("Payment does not exist.")  # Debug output for payment error
        return redirect('home')

