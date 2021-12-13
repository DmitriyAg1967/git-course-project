from datetime import datetime
import os
import requests
import time
from tqdm import tqdm
import json

with open('token_vk.txt', 'r') as file_object:
    token_vk = file_object.read().strip()
with open('token_ya.txt', 'r') as file_object:
    token_ya = file_object.read().strip()


class DownloadVK:
    def __init__(self, token):
        self.token = token
        URL = 'https://api.vk.com/method/photos.get'
        params = {
            'owner_id':  user_id,
            'album_id': 'profile',
            'extended': '1',
            'access_token': token,
            'v':'5.131'
        }
        res = requests.get(URL, params=params)
        i = 0
        for res_1 in res.json()['response']['items']:
            picture_resolution = 0
            if i < int(number_of_shots):
                i += 1
                for res_2 in res_1['sizes']:
                    k = int(res_2['height'])*int(res_2['width'])
                    if k > picture_resolution:
                        picture_resolution = k
                        likes = res_1['likes']['count']
                        date = res_1['date']
                        dt = datetime.fromtimestamp(date)
                        str_date_time = dt.strftime("%d-%m-%Y-%H-%M-%S")
                        path = os.path.join(os.getcwd())
                        if str(likes) in path:
                            file_name = str(likes) + '_' + str_date_time + ".jpg"
                        else:
                            file_name = str(likes) + ".jpg"
                        file = requests.get(res_2['url'])
                        out = open(path + "/" + file_name, "wb")
                        out.write(file.content)
                        out.close()
                    else:
                        continue
            else:
                break
            for z in tqdm(file_name):
                time.sleep(0.03)

class YaUploader:
    def __init__(self, token: str):
        self.token = token

    def create_folder(self, path=''):
        URL = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = {'Content-Type': 'application/json',
                   'Accept': 'application/json',
                   'Authorization': f'OAuth {token_ya}'}
        requests.put(f'{URL}?path={path}', headers=headers)

    def upload_file(self, loadfile, savefile, replace=False):
        URL = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = {'Content-Type': 'application/json',
                   'Accept': 'application/json',
                   'Authorization': f'OAuth {token_ya}'}
        res = requests.get(f'{URL}/upload?path={savefile}&overwrite={replace}', headers=headers).json()
        with open(loadfile, 'rb') as f:
            try:
                requests.put(res['href'], files={'file':f})
            except KeyError:
                print(res)
        for i in tqdm(savefile):
            time.sleep(0.03)

    def get_files_list(self):
        files_url = 'https://cloud-api.yandex.net/v1/disk/resources?path=Новая папка'
        headers = {'Content-Type': 'application/json',
                   'Accept': 'application/json',
                   'Authorization': f'OAuth {token_ya}'
                    }
        response = requests.get(files_url, headers=headers)
        return response.json()


if __name__ == '__main__':
    user_id = input('Введите id пользователя: ')
    number_of_shots = input('Введите количество снимков для сохранения: ')
    if number_of_shots == '':
        number_of_shots = 5
    print('Загрузка из VK:')
    vk = DownloadVK (token=token_vk)
    ya = YaUploader(token=token_ya)
    ya.create_folder('Новая папка')
    file_path = os.listdir()
    print('Копирование на яндекс диск:')
    for file_name in file_path:
        if file_name.endswith(".jpg"):
            filename = file_name
            path_to_file = os.path.join(os.getcwd(), filename)
            ya.upload_file(path_to_file, 'Новая папка/' + filename)
    file_options = ya.get_files_list()['_embedded']['items']
    file_properties = {}
    for file_parameters in file_options:
        file_properties['file_name'] = file_parameters['name']
        file_properties['size'] = file_parameters['size']
        print(json.dumps([file_properties]))
        with open("file_properties.json", "a") as write_file:
            json.dump(file_properties,  write_file, indent=0)
