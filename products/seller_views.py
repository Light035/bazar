from rest_framework import viewsets, status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from products.models import Product, Category, ProductImage
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


class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_url', 'thumbnail', 'thumbnail_url', 'is_main', 'order', 'created_at']
        read_only_fields = ['id', 'thumbnail', 'created_at']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def get_thumbnail_url(self, obj):
        if obj.thumbnail:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url
        return None


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

    @swagger_auto_schema(
        method='post',
        manual_parameters=[
            openapi.Parameter('image', openapi.IN_FORM, type=openapi.TYPE_FILE, required=True, description='Image file (JPEG, PNG, WebP, max 5MB)'),
            openapi.Parameter('is_main', openapi.IN_FORM, type=openapi.TYPE_BOOLEAN, required=False, description='Set as main image'),
            openapi.Parameter('order', openapi.IN_FORM, type=openapi.TYPE_INTEGER, required=False, description='Display order'),
        ],
        responses={
            201: ProductImageSerializer,
            400: "Validation error (max 10 images, invalid format, file too large)"
        },
        operation_description="Upload product image (max 10 images per product, max 5MB, JPEG/PNG/WebP)",
        security=[{'Bearer': []}]
    )
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_image(self, request, pk=None):
        product = self.get_object()

        # Check max images limit
        if product.images.count() >= 10:
            return Response({
                'error': 'Maximum 10 images per product'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate file
        image_file = request.FILES.get('image')
        if not image_file:
            return Response({
                'error': 'No image file provided'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check file size (5MB)
        if image_file.size > 5 * 1024 * 1024:
            return Response({
                'error': 'Image file too large. Maximum size is 5MB'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check file format
        allowed_formats = ['image/jpeg', 'image/png', 'image/webp']
        if image_file.content_type not in allowed_formats:
            return Response({
                'error': 'Invalid image format. Allowed: JPEG, PNG, WebP'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create image
        is_main = request.data.get('is_main', 'false').lower() == 'true'
        order = request.data.get('order', 0)

        # If setting as main, unset other main images
        if is_main:
            product.images.update(is_main=False)

        product_image = ProductImage.objects.create(
            product=product,
            image=image_file,
            is_main=is_main,
            order=int(order) if order else 0
        )

        serializer = ProductImageSerializer(product_image, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        method='delete',
        responses={
            204: "Image deleted",
            404: "Image not found"
        },
        operation_description="Delete product image",
        security=[{'Bearer': []}]
    )
    @action(detail=True, methods=['delete'], url_path='images/(?P<image_id>[^/.]+)')
    def delete_image(self, request, pk=None, image_id=None):
        product = self.get_object()

        try:
            image = product.images.get(id=image_id)
            image.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProductImage.DoesNotExist:
            return Response({
                'error': 'Image not found'
            }, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        method='patch',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'is_main': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Set as main image'),
                'order': openapi.Schema(type=openapi.TYPE_INTEGER, description='Display order'),
            }
        ),
        responses={
            200: ProductImageSerializer,
            404: "Image not found"
        },
        operation_description="Update product image (set as main or change order)",
        security=[{'Bearer': []}]
    )
    @action(detail=True, methods=['patch'], url_path='images/(?P<image_id>[^/.]+)')
    def update_image(self, request, pk=None, image_id=None):
        product = self.get_object()

        try:
            image = product.images.get(id=image_id)

            # Update is_main
            if 'is_main' in request.data:
                is_main = request.data['is_main']
                if is_main:
                    # Unset other main images
                    product.images.update(is_main=False)
                image.is_main = is_main

            # Update order
            if 'order' in request.data:
                image.order = request.data['order']

            image.save()

            serializer = ProductImageSerializer(image, context={'request': request})
            return Response(serializer.data)

        except ProductImage.DoesNotExist:
            return Response({
                'error': 'Image not found'
            }, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        method='get',
        responses={200: ProductImageSerializer(many=True)},
        operation_description="Get all product images",
        security=[{'Bearer': []}]
    )
    @action(detail=True, methods=['get'])
    def images(self, request, pk=None):
        product = self.get_object()
        images = product.images.all()
        serializer = ProductImageSerializer(images, many=True, context={'request': request})
        return Response(serializer.data)


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
