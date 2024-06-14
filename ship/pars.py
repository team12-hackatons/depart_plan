import pandas as pd
import json
import sys
from datetime import datetime

def ports_to_json():
    df = pd.read_excel('../data/ports.xlsx')

    data = df.to_dict(orient='records')

    # def convert_datetime(obj):
    #     if isinstance(obj, datetime):
    #         return obj.strftime('%Y-%m-%d %H:%M:%S')
    #     raise TypeError("Type not serializable")

    # Запись JSON данных в файл с обработкой datetime объектов
    with open('ports1.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def xlsx_to_json( ):
    # Чтение xlsx файла
    df = pd.read_excel('../data/ships.xlsx')

    data = df.to_dict(orient='records')
    # Функция для преобразования объектов datetime в строки
    def convert_datetime(obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        raise TypeError("Type not serializable")

    # Запись JSON данных в файл с обработкой datetime объектов
    with open('ships1.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4, default=convert_datetime)

xlsx_to_json()
ports_to_json()