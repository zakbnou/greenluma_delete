import aiohttp
import os
import asyncio
import PySimpleGUI as sg


class AppDetails:
    def __init__(self, app_id):
        self.app_id = app_id

    def get_appdetails_url(self):
        return f'https://store.steampowered.com/api/appdetails?appids={self.app_id}'

    async def download_json_data(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f'Faulty response status code = {
                          response.status} for url = {url}')
                    return None

    async def download_app_details(self):
        url = self.get_appdetails_url()
        data = await self.download_json_data(url)
        if data and data[str(self.app_id)]['success']:
            return data[str(self.app_id)]['data']['name']
        else:
            print(f'No data found for appID = {self.app_id}')
            return None


async def main():
    
    sg.theme('Black')
    layout = [[sg.Text('Enter Directory:'), sg.Input(key='-IN-'), sg.FolderBrowse()],
              [sg.Button('Get Details'), sg.Button(
                  'Delete Selected'), sg.Button('Quit')],
              [sg.Listbox(values=[], size=(60, 20), key='-LIST-', select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE)]]

    window = sg.Window('App Details', layout)

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, 'Quit'):
            break
        elif event == 'Get Details':
            directory = values['-IN-']
            if not directory:
                sg.popup('Warning', 'No directory selected.')
                continue
            tasks = []
            for filename in os.listdir(directory):
                # check if the filename is a number followed by ".txt"
                if filename[:-4].isdigit() and filename.endswith('.txt'):
                    with open(os.path.join(directory, filename), 'r') as file:
                        app_id = file.read().strip()
                        app = AppDetails(app_id)
                        tasks.append(asyncio.ensure_future(
                            app.download_app_details()))
            app_details_list = await asyncio.gather(*tasks)
            for app_id, app_name in zip(os.listdir(directory), app_details_list):
                if app_name:
                    current_items = window['-LIST-'].get_list_values()
                    current_items.append(
                        f'Filename: {app_id}, App Name: {app_name}')
                    window['-LIST-'].update(current_items)
                else:
                    current_items = window['-LIST-'].get_list_values()
                    current_items.append(
                        f'No details found for App ID: {app_id}.')
                    window['-LIST-'].update(current_items)     
        elif event == 'Delete Selected':
            directory = values['-IN-']
            if not directory:
                sg.popup('Warning', 'No directory selected.')
                continue
            selected_items = values['-LIST-']
            if sg.popup_yes_no('Are you sure you want to delete these items?') == 'Yes':
                for item in selected_items:
                    app_id = item.split(',')[0].split(':')[1].strip()
                    # print(values['-IN-']+r'/' +f'{app_id}.txt')
                    os.remove(values['-IN-']+r'/' + f'{app_id}')
                # Renaming files
                for i, filename in enumerate(sorted(os.listdir(values['-IN-']))):
                    os.rename(os.path.join(
                        values['-IN-'], filename), os.path.join(values['-IN-'], f'{i}.txt'))
                window['-LIST-'].update(
                    values=[item for item in values['-LIST-'] if item not in selected_items])

    window.close()

if __name__ == "__main__":
    asyncio.run(main())
