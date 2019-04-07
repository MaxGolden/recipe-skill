from mycroft import MycroftSkill, intent_file_handler


class Recipe(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('recipe.intent')
    def handle_recipe(self, message):
        self.speak_dialog('recipe')


def create_skill():
    return Recipe()

