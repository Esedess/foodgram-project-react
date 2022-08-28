from django.conf import settings
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from .models import Cart, Favorite, Ingredients, IngredientsAmount, Recipe, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'color',
        'slug',
    )
    list_display_links = ('name',)
    search_fields = ('name', 'color', 'slug',)
    empty_value_display = settings.ADMIN_EMPTY_VALUE_DISPLAY
    save_on_top = True
    actions = ['Delete', ]


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    search_help_text = 'Поиск по названию'
    empty_value_display = settings.ADMIN_EMPTY_VALUE_DISPLAY
    save_on_top = True
    actions = ['Delete', ]


class IngredientsAmountInline(admin.StackedInline):
    model = IngredientsAmount
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'get_tags',
        'author',
        'get_ingredients',
        'name',
        'image',
        'text',
        'cooking_time',
        'show_count',
        'publication_date',
    )
    filter_horizontal = ('tags',)
    inlines = (
        IngredientsAmountInline,
    )
    list_display_links = ('name',)
    search_fields = ('name', 'author', 'tags')
    search_help_text = 'Поиск по названию, автору и тегам'
    empty_value_display = settings.ADMIN_EMPTY_VALUE_DISPLAY
    save_on_top = True
    actions = ['Delete', ]

    @admin.display(description='Тэги')
    def get_tags(self, obj):
        return "\n".join([tag.name for tag in obj.tags.all()])

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        return "\n".join([ingr.name for ingr in obj.ingredients.all()])

    @admin.display(description='Добавлений в избранное')
    def show_count(self, obj):
        count = Favorite.objects.filter(recipes__exact=obj).count()
        url = (
            reverse("admin:recipes_favorite_changelist")
            + '?'
            + urlencode({"recipes__id__exact": f"{obj.id}"})
        )
        return format_html(
            'В избранном у {}. <a href="{}">Показать </a>', count, url)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    filter_horizontal = ('recipes',)
    list_display = ('user', 'get_recipes')
    list_filter = ('user', 'recipes')
    empty_value_display = settings.ADMIN_EMPTY_VALUE_DISPLAY

    @admin.display(description='Рецепты')
    def get_recipes(self, obj):
        return '\n'.join([recipe.name for recipe in obj.recipes.all()])


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    filter_horizontal = ('recipes',)
    list_display = (
        'pk',
        'user',
        'get_recipes',
    )
    list_display_links = ('user',)
    list_filter = ('user', 'recipes')
    search_fields = ('user',)
    empty_value_display = settings.ADMIN_EMPTY_VALUE_DISPLAY
    save_on_top = True
    actions = ['Delete', ]
    actions_on_top = True

    @admin.display(description='Рецепты')
    def get_recipes(self, obj):
        return '\n'.join([recipe.name for recipe in obj.recipes.all()])
