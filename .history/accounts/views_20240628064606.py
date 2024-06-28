

from django.shortcuts import redirect, render, get_object_or_404
from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account
from django.contrib import messages, auth
from django.http import HttpResponse
from cart.models import Cart, CartItem, Variation
from cart.views import _cart_id
from orders.models import Order
from .models import UserProfile
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
            
            #create user profile when they re registering automatically
            profile = UserProfile()
            profile.user_id = user.id
            profile.profile_picture = 'default/default-user.png'
            profile.save() #the user profile is created but does not have  any other value except the default one
            #this code here help us for a password recovery
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
        email = request.POST['email']
        password = request.POST['password']
        
        # Authenticate user
        user = auth.authenticate(email=email, password=password)
        
        if user is not None:
            try:
                # Retrieve the session-based cart
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()

                if is_cart_item_exists:
                    cart_items = CartItem.objects.filter(cart=cart)

                    product_variation = []
                    for item in cart_items:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    # Get the user's cart items to access their product variations
                    user_cart_items = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id_list = []
                    for item in user_cart_items:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id_list.append(item.id)
                        item.user = user

                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id_list[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            for item in cart_items:
                                item.user = user
                                item.save()
            except Cart.DoesNotExist:
                pass  # If no session cart exists, continue to login

            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
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
                pass
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

#=============activation functions==========================
def activate(request, uidb64, token):
    try:
        
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
        
        
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'congrats! your account is activated')
        return redirect('login')
    else:
        messages.error(request, 'invalid activation link')
        return redirect('register')
    
    
    
#======================dashboard+++++++++++++++function=================
@login_required(login_url='login')
def dashboard(request):

    #take the number of product this person has ordered
    orders = Order.objects.order_by('created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()
    context = {
        'orders_count': orders_count,
    }
    return render(request,  'accounts/dashboard.html', context)




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





#=================my orders functions view-===============================
@login_required (login_url='login')
def my_orders(request):

    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/my_orders.html', context)


#================edit profile view========================================
@login_required (login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)

    user_form = UserForm(request.POST, instance=request.user) #passs instance for updating the profile, because we re editing the 
    profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile) #don't ve the instance need to get it
    
    if user_form.is_valid() and profile_form.is_valid():
        user_form.save()
        profile_form.save()
        messages.success(request, 'your profile has been updated')
        return redirect('edit_profile')

    else:
        # it will show all the data as we use instance in the get request
        user_form = UserForm(instance=request.user)
        profile_form= UserProfileForm(instance=userprofile)

        context = {
            'user_form': user_form,
            'profile_form': profile_form,
            'userprofile': userprofile, #this will give you the path for the profile image
        }

    return render(request, 'accounts/edit_profile.html', context)



#====================change-password===============================view
@login_required (login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        #get the object
        user = Account.objects.get(username__exact=request.user.username)
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                #auth.loggout(request)
                messages.success(request, 'password updated successfully')
                return redirect('change_password')
            else:
                messages.error(request, 'Enter the valid current password')    
                return redirect('change_password')
        else:
            message.error(request, 'password do not match')
    else:
        render(request, 'accounts/change_password')               

    return  render(request, 'accounts/change_password.html')