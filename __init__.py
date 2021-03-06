from mycroft import MycroftSkill, intent_file_handler, intent_handler, \
                    AdaptIntent
from mycroft.util.log import LOG
import requests
import random
import time

API_URL = 'https://api.edamam.com/search?&app_id=88c35ddf&app_key=edd358c155b85aabe7299d492112ef31&'
Food_URL = 'https://api.edamam.com/api/food-database/parser?&app_id=33bf21f9&app_key=f92c5494765750636558c8bf9c68fb93&'


def search_dish(name):
    r = requests.get(API_URL, params={'q': name})
    if (200 <= r.status_code < 300 and 'hits' in r.json() and
            r.json()['hits']):
        return r.json()['hits'][0]['recipe']
    else:
        return None


def dish_recommendation(ingres):
    r = requests.get(API_URL, params={'q': ingres})
    if (200 <= r.status_code < 300 and 'hits' in r.json() and
            r.json()['hits']):
        hits = r.json()['hits']
        randomNum = random.randint(1, 10)
        dish_info = hits[randomNum]['recipe']
        return dish_info
    else:
        return None


def search_nutrients(foodname):
    s = requests.get(Food_URL, params={'ingr': foodname})
    if (200 <= s.status_code < 300 and 'hints' in s.json() and s.json()['hints']):
        # cocktail = r.json()['hits'][0]['recipe']['ingredientLines']
        food = s.json()['hints'][0]['food']
        label = food['label']
        nutrients = food['nutrients']
        names_key = {'ENERC_KCAL': 'Energy', 'PROCNT': 'Protein', 'FAT': 'Fat',
                     'CHOCDF': 'Carbohydrates', 'FIBTG': 'Fiber'}
        nutrients = [nutrients]
        for row in nutrients:
            for k, v in names_key.items():
                for old_name in row:
                    if k == old_name:
                        row[v] = row.pop(old_name)
        unit_nutrients = []
        for row in nutrients:
            for key in row.keys():
                unit_nutrients.append(" ".join((key, str(row[key]), " grams")))
        new_nutrients = ["the nutrition for "+label+' is']
        for idx, word in enumerate(unit_nutrients):
            if idx == 0:
                word = word.replace('grams', 'kilocalories')
            new_nutrients.append(word)
        return new_nutrients
    else:
        return None


class RecipeSkill(MycroftSkill):
    @intent_file_handler('recipe.intent')
    def get_recipe(self, message):
        recipe = search_dish(message.data['dish'])
        if recipe:
            ingredients = recipe['ingredientLines']
            calories = "the total calories is " + str(round(recipe['calories'], 2))
            totalNutr = recipe['totalNutrients']
            totalNutrlist = ["the total nutrients are"]
            for key, value in totalNutr.items():
                totalNutrlist.append(' '.join((value['label'], str(round(value['quantity'], 2)),
                                               value['unit'])))
            self.speak_dialog('YouWillNeed', {
                'ingredients': ', '.join(ingredients[:-1]),
                'final_ingredient': ingredients[-1]})
            time.sleep(1)
            self.speak(calories)

            self.set_context('IngredientContext', str(ingredients))
            self.set_context('caloriesContext', str(calories))
            self.set_context('totalNutrlistContext', str(totalNutrlist))
        else:
            self.speak_dialog('NotFound')

    @intent_file_handler('rec.intent')
    def get_recommendation(self, message):
        duration = self.get_response('askfood')
        if duration is None:
            return  # user cancelled
        print(duration)
        dish_infor = dish_recommendation(duration)
        if dish_infor:

            ingredients = dish_infor['ingredientLines']
            label = dish_infor['label']
            calories = "the total calories is " + str(round(dish_infor['calories'], 2))
            totalNutr = dish_infor['totalNutrients']
            totalNutrlist = ["the total nutrients are"]
            for key, value in totalNutr.items():
                totalNutrlist.append(' '.join((value['label'], str(round(value['quantity'], 2)),
                                               value['unit'])))
            self.speak_dialog('YouCanCook', {
                'label': label})
            self.speak(calories)

            self.set_context('IngredientContext', str(ingredients))
            self.set_context('caloriesContext', str(calories))
            self.set_context('totalNutrlistContext', str(totalNutrlist))
        else:
            self.speak_dialog('NotFound')

    @intent_file_handler('food.intent')
    def get_nutrition(self, message):
        nutrients = search_nutrients(message.data['food'])
        if nutrients:

            speakNu = nutrients
            self.speak_dialog('okay', {
                'nutrition': ', '.join(speakNu[:-1]),
                'final_nutrition': speakNu[-1]})
            time.sleep(1)
            self.set_context('NutrientsContext', str(nutrients))
        else:
            self.speak_dialog('NotFound')

    @intent_handler(AdaptIntent().require('Nutrients').require('TellMe').require('forthismeal')
                                 .require('totalNutrlistContext'))
    def tell_ingredients_again(self, message):
        return self.repeat_context(message.data['totalNutrlistContext'])

    def repeat_context(self, context):
        self.speak(context)

    @intent_handler(AdaptIntent().require('Ingredients').require('What')
                                 .require('IngredientContext'))
    def what_were_ingredients(self, message):
        return self.repeat_context(message.data['IngredientContext'])

    @intent_handler(AdaptIntent().require('Ingredients').require('TellMe')
                                 .require('Again')
                                 .require('IngredientContext'))
    def tell_ingredients_again(self, message):
        return self.repeat_context(message.data['IngredientContext'])

    @intent_handler(AdaptIntent().require('calories').require('What')
                                 .require('caloriesContext'))
    def what_were_calories(self, message):
        return self.repeat_context(message.data['caloriesContext'])

    @intent_handler(AdaptIntent().require('calories').require('TellMe')
                                 .require('Again')
                                 .require('caloriesContext'))
    def tell_calories_again(self, message):
        return self.repeat_context(message.data['caloriesContext'])

    @intent_handler(AdaptIntent().require('nutritionword').require('What')
                    .require('totalNutrlistContext'))
    def what_were_nutrition(self, message):
        return self.repeat_context(message.data['totalNutrlistContext'])

    @intent_handler(AdaptIntent().require('nutritionword').require('TellMe')
                    .require('Again')
                    .require('totalNutrlistContext'))
    def tell_nutrition_again(self, message):
        return self.repeat_context(message.data['totalNutrlistContext'])


def create_skill():
    return RecipeSkill()
