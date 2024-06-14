import os
import requests


output_dir = 'map'
os.makedirs(output_dir, exist_ok=True)

base_url = "https://tiles.stadiamaps.com/tiles/stamen_toner"

# for z in range(8):
z = 3

headers = {
    'accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    'accept-language': 'en-US,en;q=0.9',
    'priority': 'i',
    'referer': 'https://maps.stamen.com/',
    'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'image',
    'sec-fetch-mode': 'no-cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
}

for x in range(8):
    for y in range(8):
        # Формируем URL для текущих значений z, x и y
        url = f"{base_url}/{z}/{x}/{y}.png"
        print(f"Fetching {url}")

        # Делаем запрос к URL
        response = requests.get(url, headers=headers)

        # Проверяем успешность запроса
        if response.status_code == 200:
            # Определяем путь для сохранения файла
            file_path = os.path.join(output_dir, f"{z}_{x}_{y}.png")

            # Сохраняем изображение в файл
            with open(file_path, 'wb') as file:
                file.write(response.content)

            print(f"Saved {file_path}")
        else:
            print(f"Failed to fetch {url} with status code {response.status_code}")
