import json

with open('util/text.json', 'r', encoding='UTF-8') as file:
    data = json.load(file)


class BotConfig:
    help_data = {
        "help": {
            "title": "🤖 Что я умею",
            "description": "Я — ваш личный помощник по задачам! Вот что я могу для вас сделать:",
            "features": [
                "🔹 Создание событий — одноразовых и повторяющихся",
                "🔹 Напоминания — автоматически уведомлю вас в нужное время",
                "🔹 Групповая работа — делитесь событиями с участниками чата"
            ],
            "how_to_link": {
                "title": "📌 Как подключить меня к группе",
                "steps": [
                    "1. <u>Добавьте</u> меня в нужную группу",
                    "2. Добавьте мне <u>все разрешения</u> в группе",
                    "3. <u>Прикрепите свою группу</u> командой\n/link. Введите название чата и ID. (ID группы можно узнать командой /id)\n"
                    "4. <u>Создавайте ивенты в личных сообщениях</u> с ботом и прикрепляйте к группе куда нужно отправить уведомление"

                ],
                "note": "⚠️ Примечание \n1. Убедитесь, что я уже добавлен в группу перед использованием\n"
                        "2. В группе недоступны команды\n<code>/add</code>, <code>/groups</code> и <code>/link</code>",
                "author":"<b>creator</b>: @ilyas_mn"
            }
        }
    }

    help_info = help_data["help"]

    assembled_text = (
            f"<b>{help_info['title']}</b>\n\n"
            f"{help_info['description']}\n\n"
            + "\n".join(help_info["features"])
            + f"\n\n<b>{help_info['how_to_link']['title']}</b>\n"
            + "\n".join(help_info["how_to_link"]["steps"])
            + f"\n\n<b>{help_info['how_to_link']['note']}</b>"
            + f"\n\n<b>{help_info['how_to_link']['author']}</b>"
    )

    def __init__(self):
        self.start_text = data['greetings']['start-message']
        self.start_text_user = data['greetings']['start-message']
        self.cancel_title = data['cancel']['title']
        self.cancel_text = data['cancel']['message']
        self.default_text = data['default']
        self.back_text = data['return']
        self.confirm = data['confirm']
        self.success_text = data['success']
        self.error_text = data['error']
        self.delete_all_text = data['delete']['all']
        self.delete_one_text = data['delete']['one']
        self.delete_not_found = data['delete']['not-found']
        self.delete_list_empty = data['delete']['empty']
