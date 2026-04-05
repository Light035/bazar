from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Cart, CartItem, Order, OrderItem
from .serializers import (
    CartSerializer, CartItemSerializer, OrderSerializer,
    CreateOrderSerializer
)


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: CartSerializer},
        operation_description="Get current user's cart",
        security=[{'Bearer': []}]
    )
    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=CartItemSerializer,
        responses={
            201: CartItemSerializer,
            400: "Validation error"
        },
        operation_description="Add item to cart",
        security=[{'Bearer': []}]
    )
    def post(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)

        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        if not product_id:
            return Response({'error': 'product_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_id=product_id,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        responses={204: "Cart cleared"},
        operation_description="Clear all items from cart",
        security=[{'Bearer': []}]
    )
    def delete(self, request):
        try:
            cart = request.user.cart
            cart.items.all().delete()
            return Response({'message': 'Cart cleared'}, status=status.HTTP_204_NO_CONTENT)
        except Cart.DoesNotExist:
            return Response({'message': 'Cart is already empty'}, status=status.HTTP_204_NO_CONTENT)


class CartItemView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='New quantity')
            }
        ),
        responses={
            200: CartItemSerializer,
            404: "Item not found"
        },
        operation_description="Update cart item quantity",
        security=[{'Bearer': []}]
    )
    def patch(self, request, pk):
        try:
            cart = request.user.cart
            cart_item = cart.items.get(pk=pk)

            quantity = request.data.get('quantity')
            if quantity is not None:
                if quantity <= 0:
                    return Response({'error': 'Quantity must be greater than 0'}, status=status.HTTP_400_BAD_REQUEST)
                cart_item.quantity = quantity
                cart_item.save()

            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        responses={204: "Item removed"},
        operation_description="Remove item from cart",
        security=[{'Bearer': []}]
    )
    def delete(self, request, pk):
        try:
            cart = request.user.cart
            cart_item = cart.items.get(pk=pk)
            cart_item.delete()
            return Response({'message': 'Item removed from cart'}, status=status.HTTP_204_NO_CONTENT)
        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product')

    @swagger_auto_schema(
        responses={200: OrderSerializer(many=True)},
        operation_description="Get list of user's orders",
        security=[{'Bearer': []}]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=CreateOrderSerializer,
        responses={
            201: OrderSerializer,
            400: "Validation error"
        },
        operation_description="Create order from current cart (cart will be cleared)",
        security=[{'Bearer': []}]
    )
    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        try:
            cart = request.user.cart
            if not cart.items.exists():
                return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    total_price=cart.total_price,
                    address=serializer.validated_data['address'],
                    phone=serializer.validated_data['phone']
                )

                for cart_item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        price=cart_item.product.price
                    )

                cart.items.all().delete()

            order_serializer = OrderSerializer(order)
            return Response(order_serializer.data, status=status.HTTP_201_CREATED)

        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        responses={200: OrderSerializer},
        operation_description="Get order details",
        security=[{'Bearer': []}]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['cancelled'], description='Only "cancelled" is allowed')
            }
        ),
        responses={
            200: OrderSerializer,
            400: "Cannot cancel order"
        },
        operation_description="Cancel order (only if status is pending)",
        security=[{'Bearer': []}]
    )
    def partial_update(self, request, *args, **kwargs):
        order = self.get_object()

        if order.status != 'pending':
            return Response(
                {'error': 'Only pending orders can be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )

        new_status = request.data.get('status')
        if new_status != 'cancelled':
            return Response(
                {'error': 'You can only cancel orders'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = 'cancelled'
        order.save()

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

