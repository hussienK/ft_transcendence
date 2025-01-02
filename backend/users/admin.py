from django.contrib import admin
from .models import TranscendenceUser, FriendRequest

@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    # Show ID in the list view
    list_display = ('id', 'sender', 'receiver', 'accepted', 'created_at')

    # Make ID read-only in the detail view
    readonly_fields = ('id', 'sender', 'receiver', 'created_at')

# Register your models here.
admin.site.register(TranscendenceUser)