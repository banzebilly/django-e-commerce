


from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings


from . import views

urlpatterns = [
    #securing admin pane. record login attempts by duplicating the admin panel
    # path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    #we change the admin/ to secured_billy so that can not access admin panel
    path('billy-login/', admin.site.urls),
    #allauth url
    path('account/', include('allauth.urls')),
    #my site urls
    path('', views.home, name= 'home'),
    path('store/', include('store.urls')),
    path('cart/', include('cart.urls')),
    path('accounts/', include('accounts.urls')),
    # ORDERS
    path('orders/', include('orders.urls')),
    
    
    
    
] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
