from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin
from .models import Channel, Profile, User


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_subscription_count')
    list_display_links = ('user', )
    list_filter = ('user', 'phone', 'payment_details')
    search_fields = ('user', 'email', 'phone')
    fieldsets = (
        (None, {
            'fields': (
                'user',
                'middle_names',
                'phone',
                'date_of_birth',
                'payment_details'
            )
        }),
    )


class ChannelAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'subscriber_count')
    list_display_links = ('user', )
    list_filter = ('user', 'name', 'date_joined', 'rating')
    search_fields = ('user', 'email', 'phone')
    fieldsets = (
        (None, {
            'fields': (
                'user',
                'name',
                'description',
                'categories',
                'profile_image',
                'background_image',
                'rating',
                'payment_details'
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
