"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from store import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('shop/', views.shop, name='shop'),
    path('shop_single/', views.shop_single, name='shop-single'),

    path('admin/', views.admin_dashboard, name='admin_dashboard'),

    # Category URLs
    path('admin/categories/', views.category_list, name='category_list'),
    path('admin/categories/add/', views.category_add, name='category_add'),
    path('admin/categories/edit/<int:pk>/', views.category_edit, name='category_edit'),
    path('admin/categories/delete/<int:pk>/', views.category_delete, name='category_delete'),

    # Product URLs
    path('admin/products/', views.product_list, name='product_list'),
    path('admin/products/add/', views.product_add, name='product_add'),
    path('admin/products/edit/<int:pk>/', views.product_edit, name='product_edit'),
    path('admin/products/delete/<int:pk>/', views.product_delete, name='product_delete'),

    # Review URLs
    path('admin/reviews/', views.review_list, name='review_list'),
    path('admin/reviews/add/', views.review_add, name='review_add'),
    path('admin/reviews/edit/<int:pk>/', views.review_edit, name='review_edit'),
    path('admin/reviews/delete/<int:pk>/', views.review_delete, name='review_delete'),
]
