from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin
from .models import Channel, Profile, User


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_subscription_count')
    list_display_links = ('user', )
    list_filter = ('user', 'stripe_customer_id')
    search_fields = ('user', 'email')
    fieldsets = (
        (None, {
            'fields': (
                'user',
                'stripe_customer_id'
            )
        }),
    )


class ChannelAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'subscriber_count')
    list_display_links = ('user', )
    list_filter = ('user', 'name', 'date_joined')
    search_fields = ('user', 'email')
    fieldsets = (
        (None, {
            'fields': (
                'user',
                'name',
                'description',
                'categories',
                'profile_image',
                'background_image',
                'stripe_account_id',
                'stripe_plan_id'
            )
        }),
    )


class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (None, {
            'fields': ('email', 'username', 'password1', 'password2')
        }),
        ('Permissions', {
            'fields': ('is_superuser', 'is_staff')
        })
    )
    fieldsets = (
        (None, {
            'fields': ('email', 'username', 'password')
        }),
        ('Permissions', {
            'fields': ('is_superuser', 'is_staff')
        })
    )
    list_display = ['email', 'username']
    search_fields = ('email', 'username')
    ordering = ('email',)


admin.site.register(Channel, ChannelAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
