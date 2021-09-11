class FoundAdvert:
    def __init__(self, username, type, sex, features, date, place, photo):
        self.username = username
        self.type = type
        self.sex = sex
        self.features = features
        self.date = date
        self.place = place
        self.photo = photo
    
    def get_message(self):
        message = f'''Тварина: {self.type}
Стать: {self.sex}
Особливості: {self.features}
Дата знайдення: {self.date}
Місце знайдення: {self.place}
Контакти: @{self.username} 
'''
        return message
