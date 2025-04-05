import flet as ft
import requests
import json

url_on_dropdown = str("")

with open("stations.json", "r") as f:
    data = json.load(f)
    first_station = data['stations'][0]
    url_from_first_station = first_station['url']
    url_on_dropdown = url_from_first_station

with open("stations.json", "r") as f:
    stations = json.load(f)


class Player:
    def __init__(self, page: ft.Page):
        self.audio = ft.Audio(src=url_on_dropdown, autoplay=False)
        # Устанавливаем громкость по умолчанию (0.5 соответствует 50%)
        self.audio.volume = 0.5
        self.is_playing = False
        self.is_paused = True
        # Добавляем аудио-виджет на страницу
        page.add(self.audio)



    def play(self, url):
        self.audio.src = url        
        self.audio.resume()

        self.is_playing = True
        self.is_paused = False


    def pause(self):
        self.audio.pause()
        self.is_playing = False
        self.is_paused = True

    def release(self):
        # Отчищает остаток аудио в буфере, пригодится при смене станций
        self.audio.release()
        self.is_playing = False
        self.is_paused = True


    def is_playing(self):
        # Возращает True если радио играет и False если нет
        return self.is_playing
    
    def is_paused(self):
        # Нужно для икноки паузы, чтобы при смене радиостанции программа понимала что воспроизведение на паузе
        return self.is_paused


# Для отладки списка станций
# with open("stations.json", "r") as f:
#     stations = json.load(f)
#     print(stations['stations'][1]['url'])
#     for station in stations['stations']:
#         print(station['name'])
#         print(station['url'])



def main(page: ft.Page):
    page.title = "Internet Radio"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER



    # Инициализируем плеер и добавляем его на страницу
    player = Player(page)

    img = ft.Image(
        src="radio.png",
        width=250,
        height=250,
        fit=ft.ImageFit.CONTAIN,
    )

    def playbutton_func(e):
        if player.is_playing:
            e.control.icon = ft.Icons.PLAY_ARROW
            player.pause()
        else:
            e.control.icon = ft.Icons.PAUSE
            # Воспроизводим выбранную станцию
            player.play(url_on_dropdown)
        page.update()

    playbutton = ft.IconButton(ft.Icons.PLAY_ARROW, on_click=playbutton_func)

    def dropdown_changed(e):
        if player.is_playing or player.is_paused:
            player.release()
            playbutton.icon = ft.Icons.PLAY_ARROW
        with open("stations.json", "r") as f:
            stations_data = json.load(f)
        for station in stations_data['stations']:
            dropdown.options = [ft.dropdown.Option(text=station['name'], key=station['url']) for station in stations_data['stations']]
            if station['url'] == dropdown.value:
                if station['image_url'] != "":
                    print(f"Загружаем изображение: {station['image_url']}")
                    img.src = station['image_url']
                else:
                    print("Используем дефолтную иконку")
                    img.src = "https://img.icons8.com/?size=100&id=89402&format=png&color=000000"
                
                img.update()  # Обновляем изображение
                global url_on_dropdown
                url_on_dropdown = station['url']
                print(url_on_dropdown)
                # player.play(station['url'])
                page.update()
                break


    def close_banner(e):
        page.close(banner)



    dropdown = ft.Dropdown(
        options=[ft.dropdown.Option(text=station['name'], key=station['url']) for station in stations['stations']],
        on_change=dropdown_changed,
        value=stations['stations'][0]['url']  # задаем начальное значение для выпадающего списка
    )



    error_text1 = ft.Text("Станция не доступна, так как сервер не отвечает")
    error_text1.visible = False
    error_text2 = ft.Text("Станция уже есть в списке")
    error_text2.visible = False



    action_button_style = ft.ButtonStyle(color=ft.Colors.BLUE)
    banner = ft.Banner(
        bgcolor=ft.Colors.AMBER_100,
        leading=ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.AMBER, size=40),
        content=ft.Text(
            value="Станция не доступна, так как сервер не отвечает",
            color=ft.Colors.BLACK,
        ),
        actions=[
            ft.TextButton(text="Понятно", style=action_button_style, on_click=close_banner)
        ],
    )


    def slider_changed(e):
        # Приводим громкость из диапазона 0-100 к диапазону 0.0-1.0
        player.audio.volume = int(e.control.value) / 100.0
        page.update()



    namefield = ft.TextField(label="Название станции")
    urlfield = ft.TextField(label="URL станции")
    imageurlfield = ft.TextField(label="URL лого станции, может и не быть")

    def save_station(e):
        name = namefield.value
        url = urlfield.value
        image_url = imageurlfield.value  # Получаем URL изображения из нового поля

        # Проверяем, существует ли станция с таким URL
        with open("stations.json", "r") as f:
            check_stations = json.load(f)
        for station in check_stations["stations"]:
            if station["url"] == url:
                error_text2.visible = True
                page.update()
                return
        
        # Проверяем доступность URL
        try:
            response = requests.get(url, stream=True, timeout=5)
            if response.status_code != 200:
                print(response.status_code)
                error_text1.visible = True
                page.open(banner)
                page.update()
                return
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при проверке URL: {e}")
            error_text1.visible = True
            page.open(banner)
            page.update()
            return

        # Проверяем доступность URL изображения, если он указан
        if image_url:
            try:
                img_response = requests.get(image_url, timeout=5)
                if img_response.status_code != 200:
                    error_text1.visible = True
                    page.open(banner)
                    page.update()
                    return
            except requests.exceptions.RequestException:
                error_text1.visible = True
                page.open(banner)
                page.update()
                return

        # Загружаем текущие станции
        with open("stations.json", "r") as f:
            stations_data = json.load(f)
        
        # Добавляем новую станцию
        stations_data["stations"].append({
            "name": name,
            "url": url,
            "image_url": image_url if image_url else ""
        })
        # Сохраняем обновленные данные
        with open("stations.json", "w") as f:
            json.dump(stations_data, f, indent=4)
        
        page.close(addstationdialog)
        page.update()



    addstationdialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Добавить станцию"),
        content=ft.Column(
            controls=[
                namefield,
                urlfield,
                imageurlfield,  # Добавляем поле для URL изображения
                error_text1,
                error_text2
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        content_padding=10,
        actions_padding=10,
        adaptive=True,
        actions=[
            ft.TextButton("Отмена", on_click=lambda e: page.close(addstationdialog)),
            ft.TextButton("Добавить", on_click=save_station),
        ],
        )



    slider = ft.Slider(
        min=0,
        max=100,
        divisions=20,
        value=player.audio.volume * 100,

        label="{value}%",
        on_change=slider_changed
    )



    deletestationdialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Удалить станцию"),
        content=ft.Column(
            controls=[
                ft.Text("Выберите станцию для удаления:"),
                ft.ListView(
                    controls=[
                        ft.TextButton(
                            station["name"],
                            data=station["name"],
                            on_click=lambda e: delete_station(e.control.data)
                        ) for station in stations["stations"]
                    ],
                    height=200,
                    spacing=10
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        content_padding=10,
        actions_padding=10,
        adaptive=True,
        actions=[
            ft.TextButton("Закрыть", on_click=lambda e: page.close(deletestationdialog)),
        ],
    )



    aboutdialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("О программе"),
        content=ft.Column(
            controls=[
                ft.Text("GoldRadio Player", size=20, weight=ft.FontWeight.BOLD),
                ft.Text("Версия 1.1"),
                ft.Text(""),
                ft.Text("Разработано с использованием:"),
                ft.Text("• Python"),
                ft.Text("• Flet Framework"),
                ft.Text(""),
                ft.Text("© 2025 GoldRadio Player")
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        actions=[
            ft.TextButton("Закрыть", on_click=lambda e: page.close(aboutdialog)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )



    def delete_station(station_name):
        # Загружаем текущие данные
        with open("stations.json", "r") as f:
            stations_data = json.load(f)
        
        # Удаляем выбранную станцию
        stations_data["stations"] = [
            station for station in stations_data["stations"] 
            if station["name"] != station_name
        ]
        
        # Сохраняем обновленные данные
        with open("stations.json", "w") as f:
            json.dump(stations_data, f, indent=4)
            
        # Обновляем dropdown со списком станций
        dropdown.options = [
            ft.dropdown.Option(station["name"]) 
            for station in stations_data["stations"]
        ]
        
        page.close(deletestationdialog)
        page.update()

    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.Icons.RADIO),
        leading_width=48,
        title=ft.Text(
            "GoldRadio Player",
            weight=ft.FontWeight.W_900,
            size=24,
            style=ft.TextStyle(
                letter_spacing=2,
                foreground=ft.Paint(
                    gradient=ft.PaintLinearGradient(
                        (0, 20),
                        (150, 20),
                        [ft.Colors.RED, ft.Colors.YELLOW]
                    )
                )
            )
        ),
        actions=[
            ft.IconButton(ft.Icons.ADD, on_click=lambda e: page.open(addstationdialog), width=48, height=48, padding=0),
            ft.PopupMenuButton(
                items=[
                    ft.PopupMenuItem(text="Удалить станцию", on_click=lambda e: page.open(deletestationdialog)),
                    ft.PopupMenuItem(),
                    ft.PopupMenuItem(text="О нас", on_click=lambda e: page.open(aboutdialog)),
                ]

            )
        ],
    )



    page.add(
        ft.Stack(
            controls=[
                # Контейнер с иконкой радиостанции. Выравнивание по оси Y = -0.8 (ближе к верху).
                ft.Container(
                    content=img,
                    alignment=ft.Alignment(0, -0.8),
                ),
                # Контейнер с панелью управления, выровненной по центру.
                ft.Container(
                    content=ft.Row(
                        controls=[
                            playbutton,
                            slider,
                            dropdown,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    alignment=ft.Alignment(0, 0),
                ),
            ],
            width=page.width,
            height=page.height,
        ),
    )


ft.app(main)