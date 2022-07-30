from django.contrib import admin

from .models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'password',
        'confirmation_code',
        'is_staff',
    )
    list_display_links = ('username',)
    list_filter = ('is_staff',)
    search_fields = ('username', 'email', 'is_staff',)
    empty_value_display = '-пусто-'
    save_on_top = True
    actions = ['Delete', ]


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    list_filter = ('user',)
    empty_value_display = '-пусто-'
