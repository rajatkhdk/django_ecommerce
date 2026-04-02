from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from .models import Product, Category, Review
from .forms import CategoryForm, ProductForm, ReviewForm
# Create your views here.
def home(request):
    return render(request, 'store/index.html')

def contact(request):
    context = {
        'mapbox_token' : settings.MAPBOX_ACCESS_TOKEN,
    }
    return render(request, 'store/contact.html', context)

def about(request):
    return render(request, 'store/about.html')

def shop(request):
    return render(request, 'store/shop.html')

def shop_single(request):
    return render(request, 'store/shop-single.html')

def admin_dashboard(request):
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    total_reviews = Review.objects.count()

    # Example chart data
    sales_data = [10, 25, 15, 30, 20]  # you can replace with actual DB query
    orders_data = [5, 15, 8, 12, 20]

    context = {
        'total_products': total_products,
        'total_categories': total_categories,
        'total_reviews': total_reviews,
        'sales_data': sales_data,
        'orders_data': orders_data,
    }

    return render(request, 'admin/index.html', context)

# views.py
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'admin/category_list.html', {'categories': categories})

def category_add(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('category_list')
    return render(request, 'admin/category_form.html', {'form': form})

def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        return redirect('category_list')
    return render(request, 'admin/category_form.html', {'form': form})

def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    return redirect('category_list')

def product_list(request):
    products = Product.objects.all()
    return render(request, 'admin/product_list.html', {'products': products})

def product_add(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('product_list')
    return render(request, 'admin/product_form.html', {'form': form})

def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if form.is_valid():
        form.save()
        return redirect('product_list')
    return render(request, 'admin/product_form.html', {'form': form})

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect('product_list')

# List all reviews
def review_list(request):
    reviews = Review.objects.select_related('product').all()
    return render(request, 'admin/review_list.html', {'reviews': reviews})

# Add a new review
def review_add(request):
    form = ReviewForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('review_list')
    return render(request, 'admin/review_form.html', {'form': form})

# Edit an existing review
def review_edit(request, pk):
    review = get_object_or_404(Review, pk=pk)
    form = ReviewForm(request.POST or None, instance=review)
    if form.is_valid():
        form.save()
        return redirect('review_list')
    return render(request, 'admin/review_form.html', {'form': form})

# Delete a review
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    review.delete()
    return redirect('review_list')