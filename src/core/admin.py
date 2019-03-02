from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin
from .models import Channel, Profile, User, Subscription, Payout, Charge


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
                'connected'
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


class SubscriptionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'channel',
                'profile',
                'stripe_subscription_id',
                'active'
            )
        }),
    )
    list_display = ['channel', 'profile', 'active']
    list_display_links = ('channel', 'profile')
    list_filter = ('active', )
    search_fields = ('channel', 'profile', 'stripe_subscription_id')
    ordering = ('created_at',)


class PayoutAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'channel',
                'amount',
                'success',
                'stripe_transfer_id'
            )
        }),
    )
    list_display = ['channel', 'amount', 'success']
    list_display_links = ('channel', )
    search_fields = ('channel', )
    ordering = ('created_at',)


class ChargeAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'profile',
                'amount',
                'success',
                'stripe_charge_id'
            )
        }),
    )
    list_display = ['profile', 'amount']
    list_display_links = ('profile', )
    search_fields = ('profile', )
    ordering = ('created_at',)


admin.site.register(Channel, ChannelAdmin)
admin.site.register(Charge, ChargeAdmin)
admin.site.register(Payout, PayoutAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(User, UserAdmin)

admin.site.unregister(Group)
