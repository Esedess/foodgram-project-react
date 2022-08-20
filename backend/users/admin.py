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
        'is_staff',
        'is_active',
    )
    list_display_links = ('pk', 'username', 'email')
    search_fields = ('username', 'email')
    search_help_text = 'Поиск по username и email'
    empty_value_display = '-пусто-'
    save_on_top = True
    actions = ['Delete', ]


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    filter_horizontal = ('author',)
    list_display = ('user', 'get_author')
    search_fields = ('user__username', 'author__username')
    empty_value_display = '-пусто-'
    save_on_top = True
    actions = ['Delete', ]

    def get_author(self, obj):
        return ", ".join([author.username for author in obj.author.all()])
    get_author.short_description = 'Авторы'
