from django.contrib import admin

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
    empty_value_display = '-пусто-'
    save_on_top = True
    actions = ['Delete', ]


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    search_help_text = 'Поиск по названию'
    empty_value_display = '-пусто-'
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
        'publication_date',
    )
    filter_horizontal = ('tags',)
    inlines = (
        IngredientsAmountInline,
    )
    list_display_links = ('name',)
    search_fields = ('name', 'author', 'tags')
    search_help_text = 'Поиск по названию, автору и тегам'
    empty_value_display = '-пусто-'
    save_on_top = True
    actions = ['Delete', ]

    def get_tags(self, obj):
        return "\n".join([tag.name for tag in obj.tags.all()])
    get_tags.short_description = 'Тэги'

    def get_ingredients(self, obj):
        return "\n".join([ingr.name for ingr in obj.ingredients.all()])
    get_ingredients.short_description = 'Ингредиенты'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    filter_horizontal = ('recipes',)
    list_display = ('user', 'get_recipes')
    list_filter = ('user',)
    empty_value_display = '-пусто-'

    def get_recipes(self, obj):
        return "\n".join([recipe.name for recipe in obj.recipes.all()])
    get_recipes.short_description = 'Рецепты'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    filter_horizontal = ('recipes',)
    list_display = (
        'pk',
        'user',
        'get_recipes',
    )
    list_display_links = ('user',)
    list_filter = ('user',)
    search_fields = ('user',)
    empty_value_display = '-пусто-'
    save_on_top = True
    actions = ['Delete', ]
    actions_on_top = True

    def get_recipes(self, obj):
        return "\n".join([recipe.name for recipe in obj.recipes.all()])
    get_recipes.short_description = 'Рецепты'
