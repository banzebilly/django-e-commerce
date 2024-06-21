
from django.contrib import admin
from .models import PCategory, Product, Variation , ProductGallary, ReviewRating

import admin_thumbnails

# Register your models here.

#install django-admin-thumbnails
@admin_thumbnails.thumbnail('image') #this image come from the galery model
class ProductGallaryInline(admin.TabularInline):
    model = ProductGallary
    extra = 1


#this function here helds when you typing as well as slug automatically
class PCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    
    list_display = ('category_name', 'slug')
admin.site.register(PCategory, PCategoryAdmin)



#product 
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('product_name',)}
    list_display = ('product_name', 'price', 'stock', 'category', 'is_available')

    inlines = [ProductGallaryInline] #for product to be inline in the admin panel product gallary
    
class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    #do not to put a comma because is turple
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value')
    




admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin )
admin.site.register(ProductGallary)
admin.site.register(ReviewRating)
# 