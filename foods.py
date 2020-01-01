import re
import copy
import sqlite3
from enum import Enum
from typing import List, Dict

FoodType = Enum('FoodType', 'dolce primo secondo contorno placeholder')
FoodUnit = Enum('FoodUnit', 'item gr ml')


class Food:

    def __init__(self, name: str, food_type: FoodType, unit: FoodUnit, calories_per_unit: float,
                 carbohydrates_per_unit: float, proteins_per_unit: float, fats_per_unit: float):
        self.name = name
        self.food_type = food_type
        self.unit = unit
        self.calories_per_unit = calories_per_unit
        self.carbohydrates_per_unit = carbohydrates_per_unit
        self.proteins_per_unit = proteins_per_unit
        self.fats_per_unit = fats_per_unit
        self.quantity = None

    def calories(self) -> float:
        return self.calories_per_unit * self.quantity

    def carbohydrates(self) -> float:
        return self.carbohydrates_per_unit * self.quantity

    def proteins(self) -> float:
        return self.proteins_per_unit * self.quantity

    def fats(self) -> float:
        return self.fats_per_unit * self.quantity

    def to_dict(self) -> Dict:
        return dict(name=self.name, quantity=self.quantity)


def get_food_from_db(name: str, quantity=None) -> Food:
    connection = sqlite3.connect('foods.db')
    cursor = connection.cursor()
    rows = cursor.execute('SELECT * FROM foods WHERE name = (?)', (name,)).fetchall()
    connection.close()

    if len(rows) == 0:
        derived_matches = [i for i, food in enumerate(derived_foods) if food.name == name]
        assert len(derived_matches) <= 1
        if len(derived_matches) == 1:
            derived_food = derived_foods[derived_matches[0]]
            copied_derived_food = copy.deepcopy(derived_food)
            return copied_derived_food

    assert len(rows) == 1
    row = rows[0]
    food = Food(name=row[0],
                food_type=FoodType[row[1]],
                unit=FoodUnit[row[2]],
                calories_per_unit=row[3],
                carbohydrates_per_unit=row[4],
                proteins_per_unit=row[5],
                fats_per_unit=row[6])

    if quantity is not None:
        food.quantity = quantity
    return food


def get_all_foods_from_db() -> List[Food]:
    connection = sqlite3.connect('foods.db')
    cursor = connection.cursor()
    rows = cursor.execute('SELECT name FROM foods WHERE 1').fetchall()
    connection.close()
    all_foods = [get_food_from_db(x[0]) for x in rows]
    return all_foods


class DerivedFood(Food):

    def __init__(self, name: str, food_type: FoodType, ingredients: List[Food]):
        self.ingredients = ingredients

        total_calories = sum([food.calories() for food in ingredients])
        total_carbohydrates = sum([food.carbohydrates() for food in ingredients])
        total_proteins = sum([food.proteins() for food in ingredients])
        total_fats = sum([food.fats() for food in ingredients])

        super().__init__(name, food_type, FoodUnit.item, total_calories,
                         total_carbohydrates, total_proteins, total_fats)


# example, note the singular: "toast (primo): 2 bread slice, 1 egg, 100 gr egg"
def derived_food_from_string(recipe: str) -> DerivedFood:
    header, rest_of_recipe = recipe.split(':')
    regexp = re.compile(r'([a-zA-Z0-9 ]+) \(([a-z]+)\)')
    groups = re.match(regexp, header).groups()
    assert len(groups) == 2

    derived_food_name = groups[0]
    food_type = FoodType[groups[1]]
    components = rest_of_recipe.split(',')
    components = [component.lstrip(' ') for component in components]

    ingredients: List[Food] = list()
    for component in components:
        quantity = component.split(' ')[0]
        quantity = int(quantity)
        assert quantity != 0

        maybe_unit = component.split(' ')[1]
        if maybe_unit in FoodUnit.__members__ and maybe_unit != 'item':
            unit = FoodUnit[maybe_unit]
            food_name = ' '.join(component.split(' ')[2:])
        else:
            unit = FoodUnit.item
            food_name = ' '.join(component.split(' ')[1:])

        food = get_food_from_db(food_name)
        assert food.unit == unit
        food.quantity = quantity
        ingredients.append(food)

    return DerivedFood(derived_food_name, food_type, ingredients)


derived_foods = list()
def initialize_all_derived_foods():
    global derived_foods
    # use the singual for items in the recipe, they must be valid food names
    # a recipe can't use derived food as ingredients
    with open('recipes.txt') as f:
        recipes = [x.replace('\n', '') for x in f.readlines()]
    derived_foods = [derived_food_from_string(recipe) for recipe in recipes]


initialize_all_derived_foods()

if __name__ == '__main__':
    derived_food = derived_food_from_string('simple rice (primo): 150 gr basmati, 10 gr olive oil, 10 apple')
    foods = get_all_foods_from_db()
