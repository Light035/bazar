from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Category, Product, Review
from .serializers import CategorySerializer, ProductListSerializer, ProductDetailSerializer, ReviewSerializer
from orders.models import OrderItem


class ProductPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images')
    pagination_class = ProductPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__slug']
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at', 'average_rating']
    ordering = ['-created_at']
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer

    @swagger_auto_schema(
        responses={200: ReviewSerializer(many=True)},
        operation_description="Get all reviews for a product"
    )
    @action(detail=True, methods=['get'], url_path='reviews')
    def reviews(self, request, slug=None):
        product = self.get_object()
        reviews = product.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=ReviewSerializer,
        responses={
            201: ReviewSerializer,
            400: "Validation error",
            403: "Must purchase product first"
        },
        operation_description="Add a review for a product (must have ordered it)",
        security=[{'Bearer': []}]
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], url_path='reviews/create')
    def create_review(self, request, slug=None):
        product = self.get_object()

        # Check if user has ordered this product
        has_ordered = OrderItem.objects.filter(
            order__user=request.user,
            product=product
        ).exists()

        if not has_ordered:
            return Response(
                {'error': 'You must purchase this product before reviewing it'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if user already reviewed this product
        if Review.objects.filter(user=request.user, product=product).exists():
            return Response(
                {'error': 'You have already reviewed this product'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.action == 'destroy':
            return Review.objects.filter(user=self.request.user)
        return Review.objects.all()

    @swagger_auto_schema(
        responses={204: "Review deleted"},
        operation_description="Delete your own review",
        security=[{'Bearer': []}]
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
