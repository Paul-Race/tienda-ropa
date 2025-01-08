# store/views/products.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from ..models import Product, Category, Brand, ProductReview
from ..forms import ProductForm, ProductReviewForm, ProductSearchForm

def index(request):
    """Vista de la página principal"""
    featured_products = Product.objects.filter(featured=True, is_active=True)[:8]
    latest_products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    
    context = {
        'featured_products': featured_products,
        'latest_products': latest_products,
    }
    return render(request, 'store/index.html', context)

def product_list(request):
    """Vista de listado de productos con filtros"""
    form = ProductSearchForm(request.GET)
    products = Product.objects.filter(is_active=True)

    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        brand = form.cleaned_data.get('brand')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        size = form.cleaned_data.get('size')
        order_by = form.cleaned_data.get('order_by')

        if query:
            products = products.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(brand__name__icontains=query)
            )
        
        if category:
            products = products.filter(category=category)
        
        if brand:
            products = products.filter(brand=brand)
        
        if min_price:
            products = products.filter(price__gte=min_price)
        
        if max_price:
            products = products.filter(price__lte=max_price)
        
        if size:
            products = products.filter(size=size)
        
        if order_by:
            if order_by == 'price_asc':
                products = products.order_by('price')
            elif order_by == 'price_desc':
                products = products.order_by('-price')
            elif order_by == 'name':
                products = products.order_by('name')
            elif order_by == 'created_at':
                products = products.order_by('-created_at')

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'form': form,
        'page_obj': page_obj,
    }
    return render(request, 'store/products/list.html', context)

def product_detail(request, slug):
    """Vista de detalle de producto"""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    review_form = ProductReviewForm()
    reviews = product.reviews.all().order_by('-created_at')
    
    if request.method == 'POST' and request.user.is_authenticated:
        review_form = ProductReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, '¡Gracias por tu reseña!')
            return redirect('product_detail', slug=slug)

    similar_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'review_form': review_form,
        'reviews': reviews,
        'similar_products': similar_products,
    }
    return render(request, 'store/products/detail.html', context)

@login_required
def add_review(request, product_id):
    """Vista para añadir reseña a un producto"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, '¡Gracias por tu reseña!')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    
    return redirect('product_detail', slug=product.slug)

def category_products(request, slug):
    """Vista de productos por categoría"""
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, is_active=True)
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'store/products/category.html', context)

def brand_products(request, slug):
    """Vista de productos por marca"""
    brand = get_object_or_404(Brand, slug=slug)
    products = Product.objects.filter(brand=brand, is_active=True)
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'brand': brand,
        'page_obj': page_obj,
    }
    return render(request, 'store/products/brand.html', context)