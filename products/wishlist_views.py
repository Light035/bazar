from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Wishlist, Product
from .serializers import ProductListSerializer


class WishlistViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: ProductListSerializer(many=True)},
        operation_description="Get user's wishlist with full product details",
        security=[{'Bearer': []}]
    )
    def list(self, request):
        """Get my wishlist with full product details"""
        wishlist_items = Wishlist.objects.filter(user=request.user).select_related(
            'product__category', 'product__seller'
        ).prefetch_related('product__images')

        products = [item.product for item in wishlist_items]
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['product_id'],
            properties={
                'product_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Product ID to add')
            }
        ),
        responses={
            201: openapi.Response(description="Product added to wishlist"),
            400: "Product not found or already in wishlist"
        },
        operation_description="Add product to wishlist",
        security=[{'Bearer': []}]
    )
    def create(self, request):
        """Add product to wishlist"""
        product_id = request.data.get('product_id')

        if not product_id:
            return Response(
                {'error': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if already in wishlist
        if Wishlist.objects.filter(user=request.user, product=product).exists():
            return Response(
                {'error': 'Product already in wishlist'},
                status=status.HTTP_400_BAD_REQUEST
            )

        Wishlist.objects.create(user=request.user, product=product)
        return Response(
            {'message': 'Product added to wishlist'},
            status=status.HTTP_201_CREATED
        )

    @swagger_auto_schema(
        responses={
            204: "Product removed from wishlist",
            404: "Product not in wishlist"
        },
        operation_description="Remove product from wishlist",
        security=[{'Bearer': []}]
    )
    def destroy(self, request, pk=None):
        """Remove product from wishlist"""
        try:
            wishlist_item = Wishlist.objects.get(user=request.user, product_id=pk)
            wishlist_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Wishlist.DoesNotExist:
            return Response(
                {'error': 'Product not in wishlist'},
                status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="Check if product is in wishlist",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'in_wishlist': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                    }
                )
            )
        },
        operation_description="Check if product is in user's wishlist",
        security=[{'Bearer': []}]
    )
    @action(detail=True, methods=['get'], url_path='check')
    def check(self, request, pk=None):
        """Check if product is in wishlist"""
        in_wishlist = Wishlist.objects.filter(user=request.user, product_id=pk).exists()
        return Response({'in_wishlist': in_wishlist})
