import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pygame
import requests
import io
import json
import time

# API 키와 헤더 설정
headers = {
    "x-nxopen-api-key": "test_1afb40fe1643062715cabee53b8c4aa9d7a211cfa2612f3d86f8a0f56af4eafbefe8d04e6d233bd35cf2fabdeb93fb0d"
}

def get_ouid(character_name):
    userouidURL = "https://open.api.nexon.com/fconline/v1/id?nickname=" + character_name
    response = requests.get(userouidURL, headers=headers)
    response_json = response.json()
    return response_json.get('ouid')

def get_user_info(ouid):
    userinfoURL = 'https://open.api.nexon.com/fconline/v1/user/basic?ouid=' + ouid
    response = requests.get(userinfoURL, headers=headers)
    response_json = response.json()
    return response_json.get('nickname'), response_json.get('level')

def get_match_ids(ouid, matchtype='50', offset='0', limit='20'):
    usermatchURL = ('https://open.api.nexon.com/fconline/v1/user/match?ouid=' + ouid +
                    '&matchtype=' + matchtype + '&offset=' + offset + '&limit=' + limit)
    response = requests.get(usermatchURL, headers=headers)
    return response.json()

def get_match_details(match_ids):
    match_details = []
    for matchid in match_ids:
        userdetailinfoURL = 'https://open.api.nexon.com/fconline/v1/match-detail?matchid=' + matchid
        response = requests.get(userdetailinfoURL, headers=headers)
        match_detail = response.json()
        match_details.append(match_detail)
    return match_details

def get_maxdivision(ouid):
    MaxDivisionURL = 'https://open.api.nexon.com/fconline/v1/user/maxdivision?ouid=' + ouid
    response = requests.get(MaxDivisionURL, headers=headers)
    response_json = response.json()

    if isinstance(response_json, list) and len(response_json) > 0:
        return response_json[0].get('division')
    else:
        return None

def get_spid_metadata():
    url = "https://open.api.nexon.com/static/fconline/meta/spid.json"
    response = requests.get(url)
    return response.json()

def print_other_player_nicknames(match_details, main_nickname):
    for match_detail in match_details:
        for match_info in match_detail.get('matchInfo', []):
            if match_info.get('nickname') != main_nickname:
                player_nickname = match_info.get('nickname')
            print(f"Match ID: {match_detail['matchId']}, Player Nickname: {player_nickname}")

def get_division_data():
    url = "https://open.api.nexon.com/static/fconline/meta/division.json"
    response = requests.get(url)
    return response.json()

def get_season_metadata():
    url = "https://open.api.nexon.com/static/fconline/meta/seasonid.json"
    response = requests.get(url)
    return response.json()

class FC_GG_App:
    def __init__(self, root):
        self.root = root
        self.root.title("FC.GG")
        self.root.geometry("1000x700")  # 윈도우 크기 설정
        self.season_data = get_season_metadata()

        self.favorites = []

        # Initialize pygame mixer
        pygame.mixer.init()
        self.bgm_file = "FIFASOUND.mp3"  # Replace with your actual BGM file
        pygame.mixer.music.load(self.bgm_file)
        pygame.mixer.music.set_volume(0.5)  # Set the volume to 50%
        pygame.mixer.music.play(-1)  # Play the BGM in a loop

        self.header_frame = tk.Frame(self.root, bg='light yellow')
        self.header_frame.pack(side="top", fill="x")

        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=1)
        self.header_frame.grid_columnconfigure(2, weight=1)
        self.header_frame.grid_columnconfigure(3, weight=1)
        self.header_frame.grid_columnconfigure(4, weight=1)

        # 로고 이미지 로드
        self.logo_image = Image.open("FCGG.png")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)

        # 로고 라벨 추가+
        self.logo_button = tk.Button(self.header_frame, image=self.logo_photo, command=self.open_logo_window, bg='light yellow')
        self.logo_button.grid(row=0, column=0, padx=0, pady=1)


        # Create sound toggle button
        self.sound_on_image = Image.open("1.png").convert("RGBA")
        self.sound_off_image = Image.open("2.png").convert("RGBA")

        self.sound_on_image = ImageTk.PhotoImage(self.sound_on_image)
        self.sound_off_image = ImageTk.PhotoImage(self.sound_off_image)

        self.sound_button = tk.Button(self.header_frame, image=self.sound_on_image, command=self.toggle_sound,
                                      bg='light yellow')
        self.sound_button.grid(row=0, column=1, padx=10, pady=10)

        self.is_sound_on = True

        # Load map button image
        self.map_icon = Image.open("map.png").convert("RGBA")
        self.map_icon = ImageTk.PhotoImage(self.map_icon)

        # Create map button
        self.map_button = tk.Button(self.header_frame, image=self.map_icon, command=self.open_map_window,
                                    bg='light yellow')
        self.map_button.grid(row=0, column=2, padx=10, pady=10)
        # 시간 라벨 추가
        self.time_label = tk.Label(self.header_frame, font=("Helvetica", 16), bg='light yellow')
        self.time_label.grid(row=0, column=3, padx=10, pady=10)

        # Load images for buttons
        self.search_icon = Image.open("돋보기.png").convert("RGBA")
        self.favorite_icon = Image.open("별.png").convert("RGBA")
        self.no_check_icon = Image.open("노체크.png").convert("RGBA")  # 기본 노체크 이미지
        self.checked_icon = Image.open("체크.png").convert("RGBA")  # 체크된 이미지

        self.search_icon = ImageTk.PhotoImage(self.search_icon)
        self.favorite_icon = ImageTk.PhotoImage(self.favorite_icon)
        self.no_check_icon = ImageTk.PhotoImage(self.no_check_icon)
        self.checked_icon = ImageTk.PhotoImage(self.checked_icon)

        self.search_button = tk.Button(self.header_frame, text="검색  ", image=self.search_icon, compound="left",
                                       command=self.create_search_screen)
        self.search_button.grid(row=0, column=4, padx=20, pady=20)

        self.favorites_button = tk.Button(self.header_frame, text="즐겨찾기  ", image=self.favorite_icon, compound="left",
                                          command=self.show_favorites_screen)
        self.favorites_button.grid(row=0, column=5, padx=20, pady=20)

        self.content_frame = tk.Frame(self.root, bg='white')
        self.content_frame.pack(fill="both", expand=True)

        # Load SPID data
        self.spid_data = get_spid_metadata()

        self.check_button = None  # Initialize check_button here

        self.create_search_screen()

        self.update_time()

    def toggle_sound(self):
        if self.is_sound_on:
            pygame.mixer.music.pause()
            self.sound_button.config(image=self.sound_off_image)
        else:
            pygame.mixer.music.unpause()
            self.sound_button.config(image=self.sound_on_image)
        self.is_sound_on = not self.is_sound_on

    def update_button_colors(self, active_button):
        inactive_color = "lightgrey"
        active_color = "lightpink"

        if active_button == "search":
            self.search_button.config(bg=active_color)
            self.favorites_button.config(bg=inactive_color)
        elif active_button == "favorites":
            self.search_button.config(bg=inactive_color)
            self.favorites_button.config(bg=active_color)

    def create_search_screen(self):
        self.clear_screen()
        self.update_button_colors("search")

        frame_height = 500

        left_frame = tk.Frame(self.content_frame, bg='white', bd=2, relief="groove", width=300, height=frame_height)
        left_frame.pack(side="left", fill="y", padx=20, pady=20)

        right_frame = tk.Frame(self.content_frame, bg='white', bd=2, relief="groove", width=600, height=frame_height)
        right_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        left_frame.grid_propagate(False)  # 프레임 크기 고정
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure([0, 1, 2, 3], weight=1)

        tk.Label(left_frame, text="닉네임 검색", bg='white').grid(row=1, column=0, padx=5, pady=5, sticky="n")
        self.nickname_entry = tk.Entry(left_frame, width=20)
        self.nickname_entry.grid(row=1, column=1, padx=5, pady=5, sticky="n")
        self.nickname_search_button = tk.Button(left_frame, text="검색", command=self.show_search_results)
        self.nickname_search_button.grid(row=1, column=2, padx=5, pady=5, sticky="n")

        tk.Label(left_frame, text="선수 검색", bg='white').grid(row=2, column=0, padx=5, pady=5, sticky="s")
        self.player_entry = tk.Entry(left_frame, width=20)
        self.player_entry.grid(row=2, column=1, padx=5, pady=5, sticky="s")
        self.player_search_button = tk.Button(left_frame, text="검색", command=self.show_player_results)
        self.player_search_button.grid(row=2, column=2, padx=5, pady=5, sticky="s")

        # 오른쪽 프레임: 검색 결과
        self.search_result_frame = tk.Frame(right_frame, bg='light blue', height=40)  # Height fixed for consistency
        self.search_result_frame.pack(fill="x")

        self.search_result_label = tk.Label(self.search_result_frame, text="검색 결과", font=("Helvetica", 16, "bold"),
                                            bg='light blue')
        self.search_result_label.pack(anchor="center", pady=10)

        # 검색 결과를 표시할 캔버스와 스크롤바
        self.results_canvas = tk.Canvas(right_frame, bg='white')
        self.results_scrollbar = tk.Scrollbar(right_frame, orient="vertical", command=self.results_canvas.yview)
        self.results_canvas.pack(side="left", fill="both", expand=True)
        self.results_canvas.configure(yscrollcommand=self.results_scrollbar.set)

        self.results_frame = tk.Frame(self.results_canvas, bg='white')
        self.results_canvas.create_window((0, 0), window=self.results_frame, anchor="center")
        self.results_frame.bind("<Configure>", self.on_frame_configure)

        # 스크롤바를 기본적으로 숨김
        self.results_scrollbar.pack_forget()

    def on_frame_configure(self, event):
        self.results_canvas.configure(scrollregion=self.results_canvas.bbox("all"))

    def show_search_results(self):
        nickname = self.nickname_entry.get()
        if nickname:
            ouid = get_ouid(nickname)
            if ouid:
                user_nickname, user_level = get_user_info(ouid)
                match_ids = get_match_ids(ouid)
                match_details = get_match_details(match_ids)
                max_division_id = get_maxdivision(ouid)

                division_data = get_division_data()
                division_name = next(
                    (item['divisionName'] for item in division_data if item['divisionId'] == max_division_id),
                    "Unknown Division")

                # 검색 결과 화면 업데이트
                self.clear_search_results()
                self.search_result_label.pack(anchor="center", pady=10)

                # 결과값들을 표시하는 라벨
                result_text = f"닉네임: {user_nickname}\n\nLevel: {user_level}\n\n최고 등급: {division_name}"
                result_label = tk.Label(self.results_frame, text=result_text, bg='white', font=("Helvetica", 30))

                # 중앙 정렬을 위해 라벨을 패킹할 때 anchor 옵션 사용
                result_label.pack(anchor="center", padx=150, pady=20)

                is_favorite = user_nickname in self.favorites
                check_icon = self.checked_icon if is_favorite else self.no_check_icon

                if not self.check_button:
                    self.check_button = tk.Button(self.search_result_frame, image=check_icon,
                                                  command=lambda: self.toggle_favorite(user_nickname), bg='light blue')
                    self.check_button.pack(side="right", padx=10)
                else:
                    self.check_button.config(image=check_icon, command=lambda: self.toggle_favorite(user_nickname))

                # 닉네임 검색 시에는 스크롤바를 숨김
                self.results_scrollbar.pack_forget()

    def toggle_favorite(self, nickname):
        if nickname in self.favorites:
            self.favorites.remove(nickname)
            self.check_button.config(image=self.no_check_icon)
            messagebox.showinfo("즐겨찾기", f"{nickname} 닉네임이 즐겨찾기에서 제거되었습니다.")
        else:
            self.favorites.append(nickname)
            self.check_button.config(image=self.checked_icon)
            messagebox.showinfo("즐겨찾기", f"{nickname} 닉네임이 즐겨찾기에 추가되었습니다.")

    def show_favorites_screen(self):
        self.clear_screen()
        self.update_button_colors("favorites")

        frame_height = 500

        left_frame = tk.Frame(self.content_frame, bg='white', bd=2, relief="groove", width=300, height=frame_height)
        left_frame.pack(side="left", fill="y", padx=20, pady=20)

        self.right_frame = tk.Frame(self.content_frame, bg='white', bd=2, relief="groove", width=600,
                                    height=frame_height)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        left_frame.grid_propagate(False)
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure([0, 1, 2, 3], weight=1)

        favorites_frame = tk.Frame(left_frame, bg='light blue')
        favorites_frame.pack(fill="x")
        tk.Label(favorites_frame, text="즐겨찾기 목록", font=("Helvetica", 16, "bold"), bg='light blue').pack(anchor="center",
                                                                                                        pady=10)

        self.favorites_listbox = tk.Listbox(favorites_frame, height=15)  # Height adjusted for larger entries
        self.favorites_listbox.pack(fill="both", expand=True)

        for favorite in self.favorites:
            self.favorites_listbox.insert(tk.END, favorite)

        self.favorites_listbox.bind('<Double-1>', self.show_favorite_info)

    def show_favorite_info(self, event):
        selected_favorite = self.favorites_listbox.get(self.favorites_listbox.curselection())
        self.show_search_results_for_favorite(selected_favorite)

    def show_search_results_for_favorite(self, nickname):
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        result_text = f"닉네임: {nickname}"
        result_label = tk.Label(self.right_frame, text=result_text, bg='white', font=("Helvetica", 30))
        result_label.pack(anchor="center", pady=5)

        # Add buttons for user match history and transaction history
        match_history_button = tk.Button(self.right_frame, text="유저의 매치 기록 조회", command=self.show_match_history, font=("Helvetica", 20))
        match_history_button.pack(anchor="center", pady=10)

        transaction_history_button = tk.Button(self.right_frame, text="유저의 거래 기록 조회",
                                               command=self.show_transaction_history, font=("Helvetica", 20))
        transaction_history_button.pack(anchor="center", pady=10)

        button_frame = tk.Frame(self.right_frame, bg='white')
        button_frame.pack(anchor="center", pady=10)

        self.telegram_image = Image.open("텔레그램.png")
        self.telegram_photo = ImageTk.PhotoImage(self.telegram_image)
        telegram_button = tk.Button(button_frame, image=self.telegram_photo, command=self.show_match_history,
                                    bg='white')
        telegram_button.pack(side="left", padx=20)

        self.mail_image = Image.open("메일.png")
        self.mail_photo = ImageTk.PhotoImage(self.mail_image)
        mail_button = tk.Button(button_frame, image=self.mail_photo, command=self.send_email, bg='white')
        mail_button.pack(side="left", padx=20)

    def send_email(self):
        email_window = tk.Toplevel(self.root)
        email_window.title("이메일 보내기")
        email_window.geometry("400x200")

        # Calculate the position to center the new window on the screen
        self.root.update_idletasks()  # Update "requested size" from geometry manager

        # Get the size and position of the main window
        main_width = self.root.winfo_width()
        main_height = self.root.winfo_height()
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()

        # Calculate the position of the new window
        window_width = 400
        window_height = 150
        x = main_x + (main_width // 2) - (window_width // 2)
        y = main_y + (main_height // 2) - (window_height // 2)

        # Set the geometry of the new window
        email_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        tk.Label(email_window, text="수신자 메일 주소를 입력해주세요", font=("Helvetica", 12)).pack(pady=5)
        recipient_entry = tk.Entry(email_window, font=("Helvetica", 12))
        recipient_entry.pack(fill="x", padx=10, pady=5)

        send_button = tk.Button(email_window, text="전송", font=("Helvetica", 12),
                                command=lambda: self.send_email_action(recipient_entry))
        send_button.pack(pady=10)

    def send_email_action(self, recipient_entry):
        recipient = recipient_entry.get()
        messagebox.showinfo("이메일 전송", f"메일 주소: {recipient}\n이메일이 전송 되었습니다!")
        # 여기에 실제 이메일 전송 코드를 추가할 수 있습니다.

    def show_match_history(self):
        messagebox.showinfo("기능 미구현", "유저의 매치 기록 조회 기능은 아직 구현되지 않았습니다.")

    def show_transaction_history(self):
        messagebox.showinfo("기능 미구현", "유저의 거래 기록 조회 기능은 아직 구현되지 않았습니다.")

    def show_player_results(self):
        player_name = self.player_entry.get().lower()
        if player_name:
            # 선수 이름 검색
            matching_players = [player for player in self.spid_data if player_name in player['name'].lower()]

            # 검색 결과 화면 업데이트
            self.clear_search_results()
            self.search_result_label.pack(anchor="center", pady=10)

            if matching_players:
                for player in matching_players:
                    # Extract the season ID from the SPID
                    season_id = str(player['id'])[:3]
                    # Find the season image URL
                    season_image_url = next(
                        (season['seasonImg'] for season in self.season_data if season['seasonId'] == int(season_id)),
                        None)

                    player_image_url = f"https://fco.dn.nexoncdn.co.kr/live/externalAssets/common/playersAction/p{player['id']}.png"
                    response = requests.get(player_image_url)
                    if response.status_code == 200:
                        image_data = response.content
                        image = Image.open(io.BytesIO(image_data))
                        photo = ImageTk.PhotoImage(image)
                        frame = tk.Frame(self.results_frame, bg='white')
                        frame.pack(anchor="center", pady=5)
                        image_label = tk.Label(frame, image=photo, bg='white')
                        image_label.image = photo  # Keep a reference to the image to avoid garbage collection
                        image_label.pack(side="left", padx=10)

                        # Add season icon if available
                        if season_image_url:
                            season_response = requests.get(season_image_url)
                            if season_response.status_code == 200:
                                season_image_data = season_response.content
                                season_image = Image.open(io.BytesIO(season_image_data))
                                season_photo = ImageTk.PhotoImage(season_image)
                                season_image_label = tk.Label(frame, image=season_photo, bg='white')
                                season_image_label.image = season_photo  # Keep a reference to the image to avoid garbage collection
                                season_image_label.pack(side="left", padx=10)

                        text_label = tk.Label(frame, text=f"Player Name: {player['name']}", bg='white',
                                              font=("Helvetica", 12))
                        text_label.pack(side="left")
            else:
                result_label = tk.Label(self.results_frame, text="No matching players found.", bg='white',
                                        font=("Helvetica", 12))
                result_label.pack(anchor="center", pady=5)

            # 선수 검색 시에는 스크롤바를 보임
            self.results_scrollbar.pack(side="right", fill="y")


    def clear_screen(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def clear_search_results(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        if self.check_button:
            self.check_button.pack_forget()
            self.check_button = None

    def update_time(self):
        now = time.strftime("%Y년 %m월 %d일\n%H시  %M분  %S초", time.localtime(time.time() + 0 * 3600))
        self.time_label.config(text=now)
        self.root.after(1000, self.update_time)

    def open_map_window(self):
        map_window = tk.Toplevel(self.root)
        map_window.title("구글 맵")
        map_window.geometry("800x800")  # Set window size to 800x800

    def open_logo_window(self):
        logo_window = tk.Toplevel(self.root)
        logo_window.title("만든 사람")

        self.root.update_idletasks()
        main_width = self.root.winfo_width()
        main_height = self.root.winfo_height()
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()

        window_width = 500
        window_height = 200
        x = main_x + (main_width // 2) - (window_width // 2)
        y = main_y + (main_height // 2) - (window_height // 2)
        logo_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        info_label = tk.Label(logo_window, text="한국공학대학교\n\n2020180002 곽정민\n2020184038 황성하", font=("Helvetica", 18))
        info_label.pack(expand=True, fill="both", padx=10, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = FC_GG_App(root)
    root.mainloop()