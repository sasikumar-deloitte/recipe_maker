import json
import pandas as pd

"""

CocktailSuggester class to suggest cocktails to make from a list of input ingredients.


inputs: list of ingredients, separated by commas
		optional: ratio - ratio of ingredients it must have
		for example, 0.5 means it must have 50% of recipe ingredients
"""


class CocktailSuggester:
    def __init__(self, ingredients, ratio=0, visualization=False):
        self.ratio = ratio
        self.visualization = visualization
        self.ingredients = self.format_ingredients(ingredients)
        self.cocktails_to_ingredients, self.ingredients_to_cocktails, self.compatible_ingredients, self.recipe_ingredient_quantity = self.get_cocktail_lookups()
        self.matched_recipe, self.partial_recipe = self.make_cocktail()

    def format_ingredients(self, ingredients):
        """format and normalize ingredients for better matching"""
        to_replace = {'cointreau': 'triple sec', '&': 'and'}
        updated_ingredients = []
        for i in ingredients:
            i = i.strip()
            if i in to_replace:
                ingredient = to_replace[i]
            else:
                ingredient = i
            updated_ingredients.append(ingredient)
        return updated_ingredients

    def get_cocktail_lookups(self):
        meals = pd.read_excel("recipes.xlsx", "Ingredients_List")
        ingredients = pd.read_excel("recipes.xlsx", "Shelf_life and Price prediction")[
            ["Ingredients_Id", "Ingredients"]]
        meal_ingred = pd.merge(meals, ingredients, how="left", left_on="Ingredients_id", right_on="Ingredients_Id")[
            ["meal_id", "Ingredients", "Amount(g)"]]

        cocktails_ingredients = {}
        recipe_ingredients = {}
        ingredients_to_cocktails = {}
        # compatible ingredients are any ingredients that are found in a recipe together
        compatible_ingredients = {}
        recipe_ingredient_quantity = {}
        for ind, row in meal_ingred.iterrows():
            cocktail_name = str(row["meal_id"])
            if row['meal_id'] not in recipe_ingredients.keys():
                recipe_ingredients[row['meal_id']] = set([str(row["Ingredients"])])
                recipe_ingredient_quantity[row['meal_id']] = set([str(row["Amount(g)"]) + "g " + row["Ingredients"]])
            else:
                recipe_ingredients[row['meal_id']] = recipe_ingredients[row['meal_id']].union(
                    set([str(row["Ingredients"])]))
                recipe_ingredient_quantity[row['meal_id']] = recipe_ingredient_quantity[row['meal_id']].union(
                    set([str(row["Amount(g)"]) + "g " + row["Ingredients"]]))
        for row in recipe_ingredients.items():
            ingredients = row[1]
            cocktail_name = row[0]
            for count, ingredient in enumerate(ingredients):
                if ingredient not in ingredients_to_cocktails:
                    ingredients_to_cocktails[ingredient] = set([cocktail_name])
                else:
                    ingredients_to_cocktails[ingredient].add(cocktail_name)
                if ingredient not in compatible_ingredients:
                    compatible_ingredients[ingredient] = set(
                        [i for i in ingredients if i != ingredient])
                else:
                    compatible_ingredients[ingredient].update(
                        [i for i in ingredients if i != ingredient])
        return recipe_ingredients, ingredients_to_cocktails, compatible_ingredients, recipe_ingredient_quantity

    def make_cocktail(self):
        """

    depth first search starting with each input ingredient to find cocktail matches
    visualization=True means to stop after a couple of matches are found

    """
        # steps for visualization
        partial_recipe = {}
        matched_recipe = set()
        for i in self.ingredients:
            if i in self.ingredients_to_cocktails.keys():
                for j in self.ingredients_to_cocktails[i]:
                    temp = set()
                    missing = set()
                    match_count = 0
                    for k in self.cocktails_to_ingredients[j]:
                        if k in self.ingredients:
                            match_count += 1
                            temp.add(k)
                        else:
                            missing.add(k)
                    if match_count == len(self.ingredients) or not missing:
                        matched_recipe.add(j)
                    if missing:
                        partial_recipe[j] = missing
            else:
                print(i + " " + "not found in recipe list")
        return matched_recipe, partial_recipe

    def order_possible(self, ingredients, stock, recipes):
        result = {}
        for recipe in recipes:
            max_orders = 999999
            for ingr in self.cocktails_to_ingredients[recipe]:
                if ingr in ingredients:
                    for k in self.recipe_ingredient_quantity[recipe]:
                        if ingr in k:
                            ingredient_quantity = int(stock[ingredients.index(ingr)][:-1]) // int(
                                k.split(" ", 1)[0][:-1])
                            if max_orders > ingredient_quantity:
                                max_orders = ingredient_quantity
                            break
            result[recipe] = max_orders
        print(result)
def stock_left():
    current_stock = pd.read_excel("inventory.xlsx", "current_stock")
    ingredients = pd.read_excel("recipes.xlsx", "Shelf_life and Price prediction")[["Ingredients_Id", "Ingredients"]]
    ingred_stock_left_in_inventory=pd.merge(current_stock,ingredients,how='left',left_on='Items',right_on='Ingredients_Id')[['Ingredients','Amount(g)','Shelf life(days)']]
    ingredients=[]
    stock=[]
    for index,ingred in ingred_stock_left_in_inventory.iterrows():
        if ingred['Shelf life(days)']<=5:
            ingredients.append(ingred['Ingredients'])
            stock.append(str(ingred['Amount(g)'])+'g')
    return ingredients,stock
if __name__ == '__main__':
    input_ingredients,stock = stock_left()
    print(input_ingredients)
    print(stock)
    cocktails = CocktailSuggester(input_ingredients, ratio=0, visualization=True)
    for option in cocktails.matched_recipe:
        print(option)
    cocktails.order_possible(input_ingredients,stock, cocktails.matched_recipe)
    # for item in cocktails.order_possible(input_ingredients,['140g','200g'],cocktails.matched_recipe):
    #     print(item)
    for partial_cocktail, missing_ingredients in cocktails.partial_recipe.items():
        print("if you had {} you could make {}".format(missing_ingredients, partial_cocktail))

