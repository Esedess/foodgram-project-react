def get_cart_items(recipes):
    """
    Возвращает готовый к отправке список покупок.
    Принимает список рецептов.
    Возвращает список уникальных значений:
    {Название ингредиента}, {формовка}: {суммарное количество}
    """
    data = {}
    for recipe in recipes:
        for ingredient in recipe.ingredientsamount_set.all():
            goods, amount, measurement_unit = (
                ingredient.ingredients.name,
                ingredient.amount,
                ingredient.ingredients.measurement_unit,
            )
            name = (f'{goods} ({measurement_unit})')
            if name in data:
                data.update({name: amount + data.pop(name)})
            else:
                data.update({name: amount})

    return '\n'.join(
        f'{key} - {str(value)}' for key, value in data.items()
    )
