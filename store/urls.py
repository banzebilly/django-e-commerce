



from django.urls import path



from . import views

urlpatterns = [
  
    path('', views.store, name='store'),
    #desplay products by category
    path('category/<slug:category_slug>/', views.store, name='products_by_category'),
    #this the way we can access the single product, 
    path('category/<slug:category_slug>/<product_slug>/', views.product_detail, name='product_detail'),
    path('submit_review/<int:product_id>/', views.submit_review, name="submit_review"),
    path('search/', views.search, name='search'),
]