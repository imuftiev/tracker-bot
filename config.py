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
                    "1. Добавьте меня в нужную группу",
                    "2. Добавьте мне все разрешения в группе",
                    "3. Создавайте ивенты в личных сообщениях с ботом и прикрепляйте ID группы куда нужно отправить уведомление"

                ],
                "note": "⚠️ Примечание \n1. Убедитесь, что я уже добавлен в группу перед использованием\n2. В группе недоступна команда \t/add"
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
