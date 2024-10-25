from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from .models import Category, NFCProduct, Review, Tag, Brand
from django.db.models import Avg, Q
import logging
from django.contrib import messages
from .forms import ContactForm

def index(request):
    featured_categories = Category.objects.filter(image__isnull=False)[:3]
    featured_products = NFCProduct.objects.filter(is_featured=True)[:4]
    promo_products = NFCProduct.objects.filter(is_promo=True)[:4]
    new_products = NFCProduct.objects.filter(is_new=True)[:4]
    featured_reviews = Review.objects.filter(is_featured=True, is_approved=True)[:4]
    brands = Brand.objects.all()[:6]

    context = {
        'featured_categories': featured_categories,
        'featured_products': featured_products,
        'promo_products': promo_products,
        'new_products': new_products,
        'featured_reviews': featured_reviews,
        'brands': brands,
    }
    return render(request, 'products/index.html', context)


class ProductListView(ListView):
    model = NFCProduct
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 6

    def get_queryset(self):
        queryset = NFCProduct.objects.all()
        ordering = self.request.GET.get('orderby', 'menu_order')
        search_query = self.request.GET.get('q')
        tag_slug = self.request.GET.get('tag')
        
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(tags__name__icontains=search_query)
            ).distinct()

        if ordering == 'popularity':
            queryset = queryset.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
        elif ordering == 'rating':
            queryset = queryset.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
        elif ordering == 'date':
            queryset = queryset.order_by('-created_at')
        elif ordering == 'price':
            queryset = queryset.order_by('price')
        elif ordering == 'price-desc':
            queryset = queryset.order_by('-price')
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['latest_products'] = NFCProduct.objects.order_by('-created_at')[:3]
        context['product_tags'] = Tag.objects.all()
        context['current_ordering'] = self.request.GET.get('orderby', 'menu_order')
        context['search_query'] = self.request.GET.get('q', '') 
        return context

class CategoryProductListView(ListView):
    model = NFCProduct
    template_name = 'products/category_product_list.html'
    context_object_name = 'products'
    paginate_by = 6

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        queryset = NFCProduct.objects.filter(category=self.category)
        ordering = self.request.GET.get('orderby', 'menu_order')
        tag_slug = self.request.GET.get('tag')
        
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        
        if ordering == 'popularity':
            queryset = queryset.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
        elif ordering == 'rating':
            queryset = queryset.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
        elif ordering == 'date':
            queryset = queryset.order_by('-created_at')
        elif ordering == 'price':
            queryset = queryset.order_by('price')
        elif ordering == 'price-desc':
            queryset = queryset.order_by('-price')
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = Category.objects.all()
        context['latest_products'] = NFCProduct.objects.order_by('-created_at')[:3]
        context['product_tags'] = Tag.objects.filter(products__category=self.category).distinct()
        context['current_ordering'] = self.request.GET.get('orderby', 'menu_order')
        context['current_tag'] = self.request.GET.get('tag')
        return context





logger = logging.getLogger(__name__)



# Add a view for handling review submission
from django.views.generic.edit import CreateView
from django.urls import reverse

class ReviewCreateView(CreateView):
    model = Review
    fields = ['name', 'email', 'content', 'rating']
    template_name = 'products/review_form.html'

    def form_valid(self, form):
        form.instance.product = get_object_or_404(NFCProduct, slug=self.kwargs['slug'])
        form.instance.is_approved = True  # Automatically approve the review
        response = super().form_valid(form)
        self.object.product.update_average_rating()  # Update the product's average rating
        return response

    def get_success_url(self):
        return reverse('product_detail', kwargs={'slug': self.object.product.slug})

class ProductDetailView(DetailView):
    model = NFCProduct
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object

        # Get related products (same category or shared tags)
        related_products = NFCProduct.objects.filter(
            Q(category=product.category) | Q(tags__in=product.tags.all())
        ).exclude(id=product.id).distinct()

        context['related_products'] = related_products[:4]  # Limit to 4 related products
        context['reviews'] = self.object.reviews.filter(is_approved=True)
        context['average_rating'] = self.object.reviews.filter(is_approved=True).aggregate(Avg('rating'))['rating__avg']
        return context



class ContactView(TemplateView):
    template_name = 'products/contact.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ContactForm()
        return context

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if form.is_valid():
            # Process the form data (e.g., send email, save to database)
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('products/contact')
        return self.render_to_response(self.get_context_data(form=form))
