from django.db import models
from django.utils.text import slugify
from django.db.models import Avg
from ckeditor.fields import RichTextField

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)  # New field

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Brand(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='brand_logos/')
    url = models.URLField(blank=True)

    def __str__(self):
        return self.name
        
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class NFCProduct(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, related_name='products', blank=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    long_description = RichTextField(blank=True, null=True)
    specs = models.JSONField(blank=True, null=True)  # This will store product details/specs as JSON
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='product_images/')
    is_featured = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    is_promo = models.BooleanField(default=False)
    discount_percentage = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    average_rating = models.FloatField(default=0)    

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def discounted_price(self):
        if self.discount_percentage:
            return self.price * (100 - self.discount_percentage) / 100
        return self.price

    def update_average_rating(self):
        avg_rating = self.reviews.filter(is_approved=True).aggregate(Avg('rating'))['rating__avg']
        self.average_rating = avg_rating if avg_rating else 0
        self.save()

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(NFCProduct, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.product.name}"

class Review(models.Model):
    product = models.ForeignKey(NFCProduct, related_name='reviews', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    content = models.TextField()
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)  # New field
    is_approved = models.BooleanField(default=False)  # New field

    def __str__(self):
        return f"Review for {self.product.name} by {self.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product.update_average_rating()