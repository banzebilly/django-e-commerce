


from django.db import models
from django.forms import ValidationError
from django.urls import reverse
from accounts.models import Account
from django.db.models import Avg, Count


class PCategory(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug          = models.SlugField(max_length=100, unique=True)
    description   = models.TextField(max_length=225)
    image         = models.ImageField(upload_to='categories', blank=True)
    
    #in order to fix the way category wil appear in admin panel will be Categorys that is not what you want . to fix u can use meta
    class Meta:
        verbose_name = 'pcategory'
        verbose_name_plural = 'pcategories'
        
    def get_url(self):
        return reverse('products_by_category', args=[self.slug])
        
        
    def __str__(self):
        return self.category_name


#second model is Product


# Create your models here.

#this category is  foreign key for Caterory model ,when we
#what should happen when we delete the category, for that whe shold say on_delete, 
# whenever we delete the category the product atach to that category will be deleted
class Product(models.Model):
    product_name       = models.CharField(max_length=200, unique=True)
    slug               = models.SlugField(max_length=200, unique=True)
    description        = models.TextField(max_length=500, blank=True)
    price              = models.IntegerField()
    image              = models.ImageField(upload_to='products', blank=True)
    stock              = models.IntegerField()
    is_available       = models.BooleanField(default=True) 
    category           = models.ForeignKey(PCategory, on_delete=models.CASCADE)

    created_date       = models.DateTimeField(auto_now_add=True)
    modefied_date      = models.DateTimeField(auto_now=True)
    
    def clean(self):
        if not self.image:
            raise ValidationError('Each product must have an associated image.')

   
    def get_url(self):
        # this url will help us to get single product url, if you click any product or name it takes you to that  product detail by using refering product name
        return reverse('product_detail', args=[self.category.slug, self.slug]) #this one takes 2 argument the first one is category slug and the second is the product slug
    
    def __str__(self):
        return self.product_name

    #===========calculating the rating average=========================
    def averageReview(self):
            reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
            return reviews['average'] or 0.0

       
    #===========calculating count review=========================
    def countReview(self):
            reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
            return reviews['count'] or 0
    
    

from django.db import models

variation_category_choice = (
    ('color', 'color'),
    ('size', 'size'),
)

class VariationManager(models.Manager):
    def colors(self):
        return self.filter(variation_category='color', is_active=True)
    
    def sizes(self):
        return self.filter(variation_category='size', is_active=True)
    
class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=variation_category_choice)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    createe_date = models.DateTimeField(auto_now=True)
    
    objects = VariationManager()
    
    def __str__(self):
        return self.variation_value


    
    
# #revieew and rating system we need the models
# #after creating the models you need to create a review form.py file in store app
class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank = True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.subject

#==============product gallary======================================start here
class ProductGallary(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    image = models.ImageField(upload_to="store/products", max_length=255)

    def __str__(self):

        return self. product.product_name


    class Meta:

        verbose_name_plural = 'product gallary'