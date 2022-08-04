from django.contrib import admin

from .models import Favorite, Ingredients, IngredientsAmount, Recipe, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'color',
        'slug',
    )
    list_display_links = ('name',)
    list_filter = ('name', 'color', 'slug',)
    search_fields = ('name', 'color', 'slug',)
    empty_value_display = '-пусто-'
    save_on_top = True
    actions = ['Delete', ]


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'
    save_on_top = True
    actions = ['Delete', ]


@admin.register(IngredientsAmount)
class IngredientsAmounttsAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredients', 'amount')
    list_filter = ('recipe',)
    search_fields = ('recipe',)
    empty_value_display = '-пусто-'
    save_on_top = True
    actions = ['Delete', ]


class IngredientsAmountInline(admin.TabularInline):
    model = IngredientsAmount
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'get_tags',
        'author',
        'get_ingredients',
        'is_favorited',
        'is_in_shopping_cart',
        'name',
        'image',
        'text',
        'cooking_time',
    )
    inlines = (
        IngredientsAmountInline,
    )
    list_display_links = ('name',)
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'
    save_on_top = True
    actions = ['Delete', ]

    def get_tags(self, obj):
        return "\n".join([tag.name for tag in obj.tags.all()])

    def get_ingredients(self, obj):
        return "\n".join([ingr.name for ingr in obj.ingredients.all()])


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user',)
    empty_value_display = '-пусто-'
