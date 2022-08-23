from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from .models import Subscribe, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'show_count',
    )
    list_display_links = ('pk', 'username', 'email')
    search_fields = ('username', 'email')
    search_help_text = 'Поиск по username и email'
    empty_value_display = '-пусто-'
    save_on_top = True
    actions = ['Delete', ]

    @admin.display(description='Подписки')
    def show_count(self, obj):
        count = Subscribe.objects.filter(user=obj).count()
        url = (
            reverse('admin:users_subscribe_changelist')
            + '?'
            + urlencode({'user__id__exact': f'{obj.id}'})
        )
        return format_html(
            'Подписан на {}. <a href="{}">Показать </a>', count, url)


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user', 'author')
    empty_value_display = '-пусто-'
    save_on_top = True
    actions = ['Delete', ]
