from django.shortcuts import render
from django.conf import settings

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

def admin_index(request):
    return render(request, 'admin/index.html')
