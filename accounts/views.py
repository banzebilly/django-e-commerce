from django.shortcuts import render

from django.shortcuts import redirect, render
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from django.http import HttpResponse
from cart.models import Cart, CartItem
from cart.views import _cart_id

from django.contrib.auth.decorators import login_required
#verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
#request library 
import requests
# for sending email fast
from threading import Thread
from .utils import EmailThread




# from .forms import RegistrationForm

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()
            #this code here help us for a password recovey
            #user activation
            current_site = get_current_site(request)
            mail_subject = 'please activate your  account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request, 'Thanks for registering with us. we have sent you  a verification email to your email adress.')
            return redirect('/accounts/login/?command=verification&email='+email)
            # Redirect to success page, login page, or any other desired page
        # No need for an else block here
    else:
        form = RegistrationForm()

    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)

#=====================login function=================================================
def login(request):
    if request.method == 'POST':
        email  = request.POST['email']
        password  = request.POST['password']
        user = auth.authenticate(email=email, password=password)
        
        if user is not None:
            #this try and except block help us to check if there is  a item in the cart before we login
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                
                is_cart_item_exists = CartItem.objects.filter( cart=cart).exists() #if there is something
                #make a condition cart exist
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    
                    #getting product variation by cart id
                    product_variation = []
                    for item in cart_item:
                        variation = item.variation.all()
                        product_variation.append(list(variation))
                        
                    #get cart items from the user to access his product variation
                    
                    cart_item = CartItem.objects.filter( user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variation.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)
                    
                
                    # product_variation = [1, 2, 3, 4, 6]
                    # ex_var_list = [4, 6, 3, 5]
                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                                       
                            for item in cart_item:
                                item.user = user  #we re assigning it to the user we have alreadyf
                                item.save()
                            
                 
                
            except:
                pass
            auth.login(request, user)
            
            messages.success(request, 'you re now logged in.')
            #in order to redirect the user to the proper page when the login we need to install the request library to haddle the sitiution
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                
                #next = /cart/checkout/
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextpage = params['next']
                    return redirect(nextpage)
              
                    
                
            except:
                return redirect('dashboard')
        else:
            messages.error(request, 'invalid login credentials ')
            return redirect('login')
    return render(request, 'accounts/login.html')

#=============================logout function=================================
@login_required(login_url = 'login')
def logout(request):
    
    auth.logout(request)
    messages.success(request, 'you re logged out ')
    
    return redirect('login')

#=============activativation functions==========================
def activate(request, uidb64, token):
    try:
        
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
        
        
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'congrations! your account is activated')
        return redirect('login')
    else:
        messages.error(request, 'invalid activation link')
        return redirect('register')
    
    
    
#======================dashboard+++++++++++++++function=================
@login_required(login_url='login')
def dashboard(request):
    return render(request,  'accounts/dashboard.html')




#==================forgot password function here=======================

def forgot_password(request):
    
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            
             # resert password  through email activation
            current_site = get_current_site(request)
            mail_subject = 'please Reset your password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email 
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            EmailThread(send_email).start()
            messages.success(request, 'Password reset email has been sent to your email address')

            return redirect('login')
        
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgot_password')
            
           
    return render(request, 'accounts/forgot_password.html')

#============reset password validations=========================================
def reset_password_validate(request, uidb64, token):
    
    try:
        
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your Password')
        return redirect('reset_password')
    
    else:
        messages.error(request, 'This link has been expired ')
        return redirect('login')

#============reset password=========================================
def reset_password(request):
    
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'passsword reset succesfully')
            return redirect('login')
            
        else:
            messages.error(request, 'Password do not match!')
            return redirect('reset_password')
    else:
        
        return render(request, 'accounts/reset_password.html')