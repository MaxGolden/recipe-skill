from mycroft import MycroftSkill, intent_file_handler, intent_handler, \
                    AdaptIntent
from mycroft.util.log import LOG
import requests
import time

# API_KEY = 'app_id=88c35ddf&app_key=edd358c155b85aabe7299d492112ef31&q'
API_URL = 'https://api.edamam.com/search?&app_id=88c35ddf&app_key=edd358c155b85aabe7299d492112ef31&'


def search_dish(name):
    r = requests.get(API_URL, params={'q': name})
    if (200 <= r.status_code < 300 and 'hits' in r.json() and
            r.json()['hits']):
        return r.json()['hits'][0].recipe.ingredientLines
    else:
        return None

# def ingredients(dish):
#     ret = dish.recipe.ingredientLines
#     return ret


class CocktailSkill(MycroftSkill):
    @intent_file_handler('Recipie.intent')
    def get_recipie(self, message):
        cocktail = search_dish(message.data['dish'])
        if cocktail:
            self.speak_dialog('YouWillNeed', {
                'ingredients': ', '.join(cocktail[:-1]),
                'final_ingredient': cocktail[-1]})
            time.sleep(1)
            self.speak(cocktail['strInstructions'])
            self.set_context('IngredientContext', str(cocktail))
        else:
            self.speak_dialog('NotFound')

    def repeat_ingredients(self, ingredients):
        self.speak(ingredients)

    @intent_handler(AdaptIntent().require('Ingredients').require('What')
                                 .require('IngredientContext'))
    def what_were_ingredients(self, message):
        return self.repeat_ingredients(message.data['IngredientContext'])

    @intent_handler(AdaptIntent().require('Ingredients').require('TellMe')
                                 .require('Again')
                                 .require('IngredientContext'))
    def tell_ingredients_again(self, message):
        return self.repeat_ingredients(message.data['IngredientContext'])


def create_skill():
    return CocktailSkill()
