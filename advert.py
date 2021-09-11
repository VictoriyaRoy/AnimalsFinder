import datetime

def read_file_line(file):
    return file.readline().strip()

class Advert:
    def __init__(self, username):
        self.username = username
    
    def get_message(self):
        message = f"Тварина: {self.type}\n"
        return message


class FoundAdvert(Advert):
    def __init__(self, username):
        super().__init__(username)
    
    def get_message(self):
        message = super().get_message()
        if (self.sex != 'Н'):
            message += f"Стать: {self.sex}\n"
        message += f'''Особливості: {self.features}
Дата: {self.date}
Місце: {self.place}
Контакти: @{self.username} 
'''
        return message
    
    @staticmethod
    def create_from_file(username, text_file):
        adv = FoundAdvert(username)
        with open(text_file, 'r', encoding='utf-8') as file:
            adv.type = read_file_line(file)
            adv.sex = read_file_line(file)
            adv.place = read_file_line(file)
            adv.features = read_file_line(file)
        adv.date = datetime.date.today()
        return adv




class LostAdvert(Advert):
    def __init__(self, username):
        super().__init__(username)
    
    def get_message(self):
        message = super().get_message()
        message += f'''Стать: {self.sex}
Кличка: {self.name}
Особливі прикмети: {self.features}
Дата: {self.date}
Контакти: @{self.username} 
'''
        return message
    
    @staticmethod
    def create_from_file(username, text_file):
        adv = LostAdvert(username)
        with open(text_file, 'r', encoding='utf-8') as file:
            adv.type = read_file_line(file)
            adv.sex = read_file_line(file)
            adv.date = read_file_line(file)
            adv.name = read_file_line(file)
            adv.place = read_file_line(file)
            adv.features = read_file_line(file)
        return adv

