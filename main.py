import tkinter as tk
from PIL import Image, ImageTk  # You'll need to install pillow library
import pygame  # You'll need to install pygame library
import requests
import json

# API 키와 헤더 설정
headers = {
    "x-nxopen-api-key": "test_1afb40fe1643062715cabee53b8c4aa9876c94ce1f82999c2f4ad21e3937c6deefe8d04e6d233bd35cf2fabdeb93fb0d"
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

def print_other_player_nicknames(match_details, main_nickname):
    for match_detail in match_details:
        for match_info in match_detail.get('matchInfo', []):
            if match_info.get('nickname') != main_nickname:
                player_nickname = match_info.get('nickname')
                print(f"Match ID: {match_detail['matchId']}, Player Nickname: {player_nickname}")

class FC_GG_App:
    def __init__(self, root):
        self.root = root
        self.root.title("FC.GG")
        self.root.geometry("1000x700")  # 윈도우 크기 설정

        # Initialize pygame mixer
        pygame.mixer.init()
        self.bgm_file = "FIFASOUND.mp3"  # Replace with your actual BGM file
        pygame.mixer.music.load(self.bgm_file)
        pygame.mixer.music.set_volume(0.5)  # Set the volume to 50%
        pygame.mixer.music.play(-1)  # Play the BGM in a loop

        self.header_frame = tk.Frame(self.root, bg='lightgrey')
        self.header_frame.pack(side="top", fill="x")

        self.logo_label = tk.Label(self.header_frame, text="FC.GG", font=("Helvetica", 24), bg='lightgrey')
        self.logo_label.pack(side="left", padx=10, pady=10)

        # Load images for sound toggle
        self.sound_on_image = Image.open("1.png").convert("RGBA")
        self.sound_off_image = Image.open("2.png").convert("RGBA")

        self.sound_on_image = ImageTk.PhotoImage(self.sound_on_image)
        self.sound_off_image = ImageTk.PhotoImage(self.sound_off_image)

        # Load images for buttons
        self.search_icon = Image.open("돋보기.png").convert("RGBA")
        self.favorite_icon = Image.open("별.png").convert("RGBA")

        self.search_icon = ImageTk.PhotoImage(self.search_icon)
        self.favorite_icon = ImageTk.PhotoImage(self.favorite_icon)

        # Create sound toggle button
        self.sound_button = tk.Button(self.header_frame, image=self.sound_on_image, command=self.toggle_sound, bg='lightgrey')
        self.sound_button.pack(side="left", padx=10, pady=10)

        self.is_sound_on = True

        self.favorites_button = tk.Button(self.header_frame, text="즐겨찾기  ", image=self.favorite_icon, compound="left", command=self.show_favorites_screen)
        self.favorites_button.pack(side="right", padx=20, pady=20)

        self.search_button = tk.Button(self.header_frame, text="검색  ", image=self.search_icon, compound="left", command=self.create_search_screen)
        self.search_button.pack(side="right", padx=20, pady=20)

        self.content_frame = tk.Frame(self.root, bg='white')
        self.content_frame.pack(fill="both", expand=True)

        self.create_search_screen()

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

        # 두 프레임의 높이를 동일하게 설정
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
        self.player_search_button = tk.Button(left_frame, text="검색", command=self.show_search_results)
        self.player_search_button.grid(row=2, column=2, padx=5, pady=5, sticky="s")

        # 오른쪽 프레임: 검색 결과
        self.search_result_frame = tk.Frame(right_frame, bg='lightgrey')
        self.search_result_frame.pack(fill="x")

        self.search_result_label = tk.Label(self.search_result_frame, text="검색 결과", font=("Helvetica", 16, "bold"), bg='lightgrey')
        self.search_result_label.pack(anchor="center", pady=10)

        self.results_frame = tk.Frame(right_frame, bg='white')
        self.results_frame.pack(fill="both", expand=True, pady=(0, 20))  # 위쪽 여백은 0, 아래쪽 여백은 20으로 설정

    def show_search_results(self):
        nickname = self.nickname_entry.get()
        if nickname:
            ouid = get_ouid(nickname)
            if ouid:
                user_nickname, user_level = get_user_info(ouid)
                match_ids = get_match_ids(ouid)
                match_details = get_match_details(match_ids)

                # 검색 결과 화면 업데이트
                self.clear_search_results()
                self.search_result_label.pack(anchor="center", pady=10)
                # 결과값들을 표시하는 라벨
                result_text = f"Nickname: {user_nickname}\nLevel: {user_level}"
                result_label = tk.Label(self.results_frame, text=result_text, bg='white', font=("Helvetica", 30))
                result_label.pack(anchor="center", pady=5)

    def show_favorites_screen(self):
        self.clear_screen()
        self.update_button_colors("favorites")

        # 두 프레임의 높이를 동일하게 설정
        frame_height = 500

        left_frame = tk.Frame(self.content_frame, bg='white', bd=2, relief="groove", width=300, height=frame_height)
        left_frame.pack(side="left", fill="y", padx=20, pady=20)

        right_frame = tk.Frame(self.content_frame, bg='white', bd=2, relief="groove", width=600, height=frame_height)
        right_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        left_frame.grid_propagate(False)  # 프레임 크기 고정
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure([0, 1, 2, 3], weight=1)

        favorites_frame = tk.Frame(left_frame, bg='lightgrey')
        favorites_frame.pack(fill="x")
        tk.Label(favorites_frame, text="즐겨찾기 목록", font=("Helvetica", 16, "bold"), bg='lightgrey').pack(anchor="center",
                                                                                                       pady=10)
        # 여기에 즐겨찾기 목록 내용을 추가하세요.

        # 오른쪽 프레임: 즐겨찾기 상세 내용
        tk.Label(right_frame, text="", bg='white').pack(anchor="w", pady=5)
        # 여기에 즐겨찾기 상세 내용을 추가하세요.

    def clear_screen(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def clear_search_results(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = FC_GG_App(root)
    root.mainloop()