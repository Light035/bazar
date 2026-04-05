from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, ReviewViewSet
from .seller_views import SellerProductViewSet, SellerOrderViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'reviews', ReviewViewSet, basename='review')

seller_router = DefaultRouter()
seller_router.register(r'products', SellerProductViewSet, basename='seller-product')
seller_router.register(r'orders', SellerOrderViewSet, basename='seller-order')

urlpatterns = [
    path('', include(router.urls)),
    path('seller/', include(seller_router.urls)),
]
