
from django.contrib import admin
from .models import PCategory, Product #Variation, ReviewRating



# Register your models here.
#this function here helds when you typing as well as slug automatically
class PCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    
    list_display = ('category_name', 'slug')
admin.site.register(PCategory, PCategoryAdmin)



#product 
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('product_name',)}
    list_display = ('product_name', 'price', 'stock', 'category', 'is_available')
    
# class VariationAdmin(admin.ModelAdmin):
#     list_display = ('product', 'variation_category', 'variation_value', 'is_active')
#     #do not to put a comma because is turple
#     list_editable = ('is_active',)
#     list_filter = ('product', 'variation_category', 'variation_value')
    

admin.site.register(Product, ProductAdmin)
# admin.site.register(Variation, VariationAdmin )
# admin.site.register(ReviewRating)
# 