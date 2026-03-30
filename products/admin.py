from django.contrib import admin
from .models import Category, Product, ProductImage


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
    list_display = ("title", "category", "price", "stock", "is_active", "created_at")
    list_filter = ("is_active", "category", "created_at", "updated_at")
    search_fields = ("title", "description", "category__name")
    list_editable = ("price", "stock", "is_active")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProductImageInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "is_main")
    list_filter = ("is_main",)
    search_fields = ("product__title",)
