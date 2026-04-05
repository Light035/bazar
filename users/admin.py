from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User, EmailVerification, PasswordReset


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email",)


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    ordering = ("-created_at",)
    list_display = ("email", "first_name", "last_name", "phone", "is_seller", "email_verified", "is_staff", "is_active", "created_at")
    list_filter = ("is_staff", "is_superuser", "is_active", "is_seller", "email_verified", "created_at")
    search_fields = ("email", "first_name", "last_name", "phone")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "phone", "avatar")}),
        ("Status", {"fields": ("email_verified", "is_seller")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined", "created_at")}),
    )
    readonly_fields = ("created_at",)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_staff", "is_active"),
            },
        ),
    )


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at', 'is_used', 'is_expired_display')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__email', 'token')
    readonly_fields = ('token', 'created_at')

    def is_expired_display(self, obj):
        return obj.is_expired()
    is_expired_display.short_description = 'Expired'
    is_expired_display.boolean = True


@admin.register(PasswordReset)
class PasswordResetAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at', 'expires_at', 'is_used', 'is_expired_display')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__email', 'token')
    readonly_fields = ('token', 'created_at', 'expires_at')

    def is_expired_display(self, obj):
        return obj.is_expired()
    is_expired_display.short_description = 'Expired'
    is_expired_display.boolean = True

