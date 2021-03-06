import datetime

def read_file_line(file):
    return file.readline().strip()

class Advert:
    def __init__(self, username):
        self.username = username


class FoundAdvert(Advert):
    def __init__(self, username):
        super().__init__(username)
    
    def get_message(self):
        message = "ЗНАЙШЛАСЬ ТВАРИНА!\n"
        message += f"Тип: {self.type}\n"
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
        message = f'''ЗАГУБИЛАСЬ ТВАРИНА!
Тип: {self.type}
Стать: {self.sex}
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
            adv.coord = tuple(map(float, read_file_line(file).split(", ")))
            adv.features = read_file_line(file)
        return adv

