import sqlite3

class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    @staticmethod
    def get_user_by_username(username, db):
        cursor = db.cursor()
        cursor.execute("SELECT * FROM user WHERE username = ?", (username,))
        user_data = cursor.fetchone()
        if user_data:
            return User(user_data[0], user_data[1], user_data[2])
        return None

    def check_password(self, password):
        return self.password == password


class WeatherData:
    def __init__(self, id, temperature, humidity, record_time):
        self.id = id
        self.temperature = temperature
        self.humidity = humidity
        self.record_time = record_time

    @staticmethod
    def get_weather_data_by_time(start_time, end_time, db):
        cursor = db.cursor()
        cursor.execute("SELECT * FROM weather_data WHERE record_time >= ? AND record_time < ?", (start_time, end_time))
        data = cursor.fetchall()
        return [WeatherData(row[0], row[1], row[2], row[3]) for row in data]