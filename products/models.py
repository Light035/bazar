from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import os
import sys


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="products", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    review_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def update_rating(self):
        from django.db.models import Avg, Count
        result = self.reviews.aggregate(avg_rating=Avg('rating'), count=Count('id'))
        self.average_rating = result['avg_rating'] or 0.00
        self.review_count = result['count'] or 0
        self.save()


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/")
    thumbnail = models.ImageField(upload_to="products/thumbnails/", blank=True, null=True)
    is_main = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ["-is_main", "order", "id"]

    def __str__(self):
        return f"{self.product.title} image"

    def save(self, *args, **kwargs):
        # Generate thumbnail if image exists
        if self.image:
            self.create_thumbnail()

        # Resize main image if too large
        if self.image:
            self.resize_image()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete image files from storage
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)

        if self.thumbnail:
            if os.path.isfile(self.thumbnail.path):
                os.remove(self.thumbnail.path)

        super().delete(*args, **kwargs)

    def resize_image(self):
        """Resize main image to max 1200x1200 keeping aspect ratio"""
        img = Image.open(self.image)

        # Convert RGBA to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background

        # Resize if larger than 1200x1200
        max_size = (1200, 1200)
        if img.width > max_size[0] or img.height > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Save resized image
            output = BytesIO()
            img.save(output, format='JPEG', quality=90, optimize=True)
            output.seek(0)

            # Update the image field
            self.image = InMemoryUploadedFile(
                output, 'ImageField',
                f"{self.image.name.split('.')[0]}.jpg",
                'image/jpeg',
                sys.getsizeof(output), None
            )

    def create_thumbnail(self):
        """Create thumbnail (300x300) from main image"""
        img = Image.open(self.image)

        # Convert RGBA to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background

        # Create thumbnail
        img.thumbnail((300, 300), Image.Resampling.LANCZOS)

        # Save thumbnail
        thumb_io = BytesIO()
        img.save(thumb_io, format='JPEG', quality=85, optimize=True)
        thumb_io.seek(0)

        # Generate thumbnail filename
        thumb_name = f"thumb_{os.path.basename(self.image.name)}"
        thumb_name = f"{thumb_name.split('.')[0]}.jpg"

        # Save thumbnail to field
        self.thumbnail = InMemoryUploadedFile(
            thumb_io, 'ImageField', thumb_name,
            'image/jpeg', sys.getsizeof(thumb_io), None
        )


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.product.title} ({self.rating}/5)"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product.update_rating()

    def delete(self, *args, **kwargs):
        product = self.product
        super().delete(*args, **kwargs)
        product.update_rating()


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlisted_by")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.email} - {self.product.title}"
