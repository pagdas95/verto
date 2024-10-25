from django.contrib import admin
from .models import Category, NFCProduct, ProductImage, Review, Tag, Brand
from django import forms
from django.core.serializers.json import DjangoJSONEncoder
import json
from ckeditor.widgets import CKEditorWidget


class NFCProductAdminForm(forms.ModelForm):
    long_description = forms.CharField(widget=CKEditorWidget())
    
    class Meta:
        model = NFCProduct
        fields = '__all__'
        widgets = {
            'specs': forms.Textarea(attrs={'rows': 10, 'cols': 80}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.specs:
            self.initial['specs'] = json.dumps(self.instance.specs, cls=DjangoJSONEncoder, indent=2)

    def clean_specs(self):
        specs = self.cleaned_data.get('specs')
        if specs:
            if isinstance(specs, str):
                try:
                    return json.loads(specs)
                except json.JSONDecodeError:
                    raise forms.ValidationError("Invalid JSON format for specs")
            elif isinstance(specs, dict):
                return specs
            else:
                raise forms.ValidationError("Specs must be a JSON string or a dictionary")
        return specs


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ('name', 'email', 'content', 'rating', 'created_at')
    can_delete = False

    def has_add_permission(self, request, obj):
        return False

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'image')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(NFCProduct)
class NFCProductAdmin(admin.ModelAdmin):
    form = NFCProductAdminForm
    list_display = ('name', 'category', 'price', 'discounted_price', 'is_featured', 'is_new', 'average_rating')
    list_filter = ('category', 'is_featured', 'is_new', 'is_promo', 'tags')
    search_fields = ('name', 'description', 'long_description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ReviewInline]
    filter_horizontal = ('tags',)

    fieldsets = (
        (None, {
            'fields': ('category', 'name', 'slug', 'description', 'long_description', 'specs', 'price', 'image')
        }),
        ('Product Status', {
            'fields': ('is_featured', 'is_new','is_promo', 'discount_percentage')
        }),
        ('Tags', {
            'fields': ('tags',)
        }),
    )

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'rating', 'is_approved', 'is_featured', 'created_at')
    list_filter = ('is_approved', 'is_featured', 'rating')
    search_fields = ('product__name', 'name', 'content')
    list_editable = ('is_approved', 'is_featured')
    readonly_fields = ('created_at',)

    fieldsets = (
        (None, {
            'fields': ('product', 'name', 'email', 'content', 'rating')
        }),
        ('Review Status', {
            'fields': ('is_approved', 'is_featured', 'created_at')
        }),
    )

admin.site.register(Brand)