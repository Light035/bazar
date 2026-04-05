from rest_framework import viewsets, status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from products.models import Product, Category
from products.serializers import ProductDetailSerializer
from orders.models import Order
from orders.serializers import OrderSerializer


class IsSellerPermission(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_seller


class SellerProductSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)
    category = serializers.PrimaryKeyRelatedField(read_only=True)
    images = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'title', 'slug', 'description', 'price', 'stock', 'category', 'category_id', 'seller', 'images', 'average_rating', 'review_count', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'seller', 'slug', 'category', 'average_rating', 'review_count', 'created_at', 'updated_at']

    def create(self, validated_data):
        category_id = validated_data.pop('category_id')
        validated_data['category_id'] = category_id
        validated_data['seller'] = self.context['request'].user
        return Product.objects.create(**validated_data)


class SellerProductViewSet(viewsets.ModelViewSet):
    serializer_class = SellerProductSerializer
    permission_classes = [IsSellerPermission]

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user).select_related('category').prefetch_related('images')

    @swagger_auto_schema(
        responses={200: SellerProductSerializer(many=True)},
        operation_description="Get all products created by the seller",
        security=[{'Bearer': []}]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=SellerProductSerializer,
        responses={
            201: SellerProductSerializer,
            400: "Validation error"
        },
        operation_description="Create a new product (seller only)",
        security=[{'Bearer': []}]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={200: SellerProductSerializer},
        operation_description="Get product details",
        security=[{'Bearer': []}]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=SellerProductSerializer,
        responses={200: SellerProductSerializer},
        operation_description="Update product (full update)",
        security=[{'Bearer': []}]
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=SellerProductSerializer,
        responses={200: SellerProductSerializer},
        operation_description="Partially update product",
        security=[{'Bearer': []}]
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={204: "Product deleted"},
        operation_description="Delete product",
        security=[{'Bearer': []}]
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class SellerOrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsSellerPermission]

    def get_queryset(self):
        # Get orders that contain seller's products
        return Order.objects.filter(
            items__product__seller=self.request.user
        ).distinct().prefetch_related('items__product')

    @swagger_auto_schema(
        responses={200: OrderSerializer(many=True)},
        operation_description="Get all orders containing seller's products",
        security=[{'Bearer': []}]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={200: OrderSerializer},
        operation_description="Get order details",
        security=[{'Bearer': []}]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
