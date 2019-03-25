from django.contrib import admin

from .models import SignUp


class SignUpModelAdmin(admin.ModelAdmin):
    list_display = ["__str__", "subscribed", "timestamp"]


admin.site.register(SignUp, SignUpModelAdmin)
