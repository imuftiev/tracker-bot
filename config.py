import json

with open('util/text.json', 'r', encoding='UTF-8') as file:
    data = json.load(file)



class BotConfig:
    def __init__(self):
        self.start_text = data['greetings']['user-unknown']
        self.start_text_user = data['greetings']['user-registered']
        self.help_text = data['help']
