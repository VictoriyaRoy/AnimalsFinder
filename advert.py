import datetime

def read_file_line(file):
    return file.readline().strip()

class Advert:
    def __init__(self, username, photo):
        self.username = username
        self.photo = photo
    
    def get_message(self):
        message = f"Тварина: {self.type}\n"
        return message
    
    def get_info_tuple(self):
        return (self.get_message(), self.photo)



class FoundAdvert(Advert):
    def __init__(self, username, photo):
        super().__init__(username, photo)
    
    def get_message(self):
        message = super().get_message()
        if (self.sex):
            message += f"Стать: {self.sex}"
        message += f'''
Особливості: {self.features}
Дата: {self.date}
Місце: {self.place}
Контакти: @{self.username} 
'''
        return message
    
    @staticmethod
    def create_from_file(username, text_file, photo):
        adv = FoundAdvert(username, photo)
        with open(text_file, 'r', encoding='utf-8') as file:
            adv.type = read_file_line(file)
            adv.sex = read_file_line(file)
            adv.place = read_file_line(file)
            adv.features = read_file_line(file)
        adv.date = datetime.date.today()
        return adv




class LostAdvert(Advert):
    def __init__(self, username, photo):
        super().__init__(username, photo)
    
    def get_message(self):
        message = super().get_message()
        message += f'''
Стать: {self.sex}
Кличка: {self.name}
Особливі прикмети: {self.features}
Дата: {self.date}
Контакти: @{self.username} 
'''
        return message
    
    @staticmethod
    def create_from_file(username, text_file, photo):
        adv = FoundAdvert(username, photo)
        with open(text_file, 'r', encoding='utf-8') as file:
            adv.type = read_file_line(file)
            adv.sex = read_file_line(file)
            adv.date = read_file_line(file)
            adv.name = read_file_line(file)
            adv.place = read_file_line(file)
            adv.features = read_file_line(file)
        return adv

