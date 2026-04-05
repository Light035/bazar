from django.contrib import admin
from .models import Category, Product, ProductImage, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "price", "stock", "average_rating", "review_count", "is_active", "created_at")
    list_filter = ("is_active", "category", "created_at", "updated_at")
    search_fields = ("title", "description", "category__name")
    list_editable = ("price", "stock", "is_active")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProductImageInline]
    readonly_fields = ("average_rating", "review_count")


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "is_main")
    list_filter = ("is_main",)
    search_fields = ("product__title",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("user__email", "product__title", "comment")
    readonly_fields = ("created_at",)
