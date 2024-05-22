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

        self.header_frame = tk.Frame(self.root, bg='lightgrey')
        self.header_frame.pack(side="top", fill="x")

        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=1)
        self.header_frame.grid_columnconfigure(2, weight=1)
        self.header_frame.grid_columnconfigure(3, weight=1)
        self.header_frame.grid_columnconfigure(4, weight=1)

        self.logo_label = tk.Label(self.header_frame, text="FC.GG", font=("Helvetica", 24), bg='lightgrey')
        self.logo_label.grid(row=0, column=0, padx=10, pady=10)

        # Create sound toggle button
        self.sound_on_image = Image.open("1.png").convert("RGBA")
        self.sound_off_image = Image.open("2.png").convert("RGBA")

        self.sound_on_image = ImageTk.PhotoImage(self.sound_on_image)
        self.sound_off_image = ImageTk.PhotoImage(self.sound_off_image)

        self.sound_button = tk.Button(self.header_frame, image=self.sound_on_image, command=self.toggle_sound,
                                      bg='lightgrey')
        self.sound_button.grid(row=0, column=1, padx=10, pady=10)

        self.is_sound_on = True

        # 시간 라벨 추가
        self.time_label = tk.Label(self.header_frame, font=("Helvetica", 16), bg='lightgrey')
        self.time_label.grid(row=0, column=2, padx=10, pady=10)

        # Load images for buttons
        self.search_icon = Image.open("돋보기.png").convert("RGBA")
        self.favorite_icon = Image.open("별.png").convert("RGBA")
        self.check_icon = Image.open("체크.png").convert("RGBA")

        self.search_icon = ImageTk.PhotoImage(self.search_icon)
        self.favorite_icon = ImageTk.PhotoImage(self.favorite_icon)
        self.check_icon = ImageTk.PhotoImage(self.check_icon)

        self.search_button = tk.Button(self.header_frame, text="검색  ", image=self.search_icon, compound="left",
                                       command=self.create_search_screen)
        self.search_button.grid(row=0, column=3, padx=20, pady=20)

        self.favorites_button = tk.Button(self.header_frame, text="즐겨찾기  ", image=self.favorite_icon, compound="left",
                                          command=self.show_favorites_screen)
        self.favorites_button.grid(row=0, column=4, padx=20, pady=20)

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

        left_frame.grid_propagate(False)
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

        self.search_result_frame = tk.Frame(right_frame, bg='lightgrey', height=40)  # Height fixed for consistency
        self.search_result_frame.pack(fill="x")

        self.search_result_label = tk.Label(self.search_result_frame, text="검색 결과", font=("Helvetica", 16, "bold"),
                                            bg='lightgrey')
        self.search_result_label.pack(anchor="center", pady=10)

        self.results_frame = tk.Frame(right_frame, bg='white')
        self.results_frame.pack(fill="both", expand=True, pady=(0, 20))

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

                self.clear_search_results()
                self.search_result_label.pack(anchor="center", pady=10)
                result_text = f"닉네임: {user_nickname}\n\nLevel: {user_level}\n\n최고 등급: {division_name}"
                result_label = tk.Label(self.results_frame, text=result_text, bg='white', font=("Helvetica", 30))
                result_label.pack(anchor="center", pady=5)

                if not self.check_button:
                    self.check_button = tk.Button(self.search_result_frame, image=self.check_icon,
                                                  command=lambda: self.add_to_favorites(user_nickname), bg='lightgrey')
                    self.check_button.pack(side="right", padx=10)

    def add_to_favorites(self, nickname):
        if nickname not in self.favorites:
            self.favorites.append(nickname)
            messagebox.showinfo("즐겨찾기", f"{nickname} 닉네임이 즐겨찾기에 추가되었습니다.")
        else:
            messagebox.showinfo("즐겨찾기", f"{nickname} 닉네임은 이미 즐겨찾기에 있습니다.")

    def show_favorites_screen(self):
        self.clear_screen()
        self.update_button_colors("favorites")

        frame_height = 500

        left_frame = tk.Frame(self.content_frame, bg='white', bd=2, relief="groove", width=300, height=frame_height)
        left_frame.pack(side="left", fill="y", padx=20, pady=20)

        right_frame = tk.Frame(self.content_frame, bg='white', bd=2, relief="groove", width=600, height=frame_height)
        right_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        left_frame.grid_propagate(False)
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure([0, 1, 2, 3], weight=1)

        favorites_frame = tk.Frame(left_frame, bg='lightgrey')
        favorites_frame.pack(fill="x")
        tk.Label(favorites_frame, text="즐겨찾기 목록", font=("Helvetica", 16, "bold"), bg='lightgrey').pack(anchor="center", pady=10)

        self.favorites_listbox = tk.Listbox(favorites_frame, height=15)  # Height adjusted for larger entries
        self.favorites_listbox.pack(fill="both", expand=True)

        for favorite in self.favorites:
            self.favorites_listbox.insert(tk.END, favorite)

        self.favorites_listbox.bind('<Double-1>', self.show_favorite_info)

    def show_favorite_info(self, event):
        selected_favorite = self.favorites_listbox.get(self.favorites_listbox.curselection())
        self.show_search_results_for_favorite(selected_favorite)

    def show_search_results_for_favorite(self, nickname):
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

            self.clear_search_results()
            self.search_result_label.pack(anchor="center", pady=10)
            result_text = f"닉네임: {user_nickname}\n\nLevel: {user_level}\n\n최고 등급: {division_name}"
            result_label = tk.Label(self.results_frame, text=result_text, bg='white', font=("Helvetica", 30))
            result_label.pack(anchor="center", pady=5)

    def show_player_results(self):
        spid_data = get_spid_metadata()
        self.clear_search_results()
        self.search_result_label.pack(anchor="center", pady=10)
        if spid_data:
            result_text = json.dumps(spid_data[0], indent=4, ensure_ascii=False)
            result_label = tk.Label(self.results_frame, text=result_text, bg='white', font=("Helvetica", 12))
            result_label.pack(anchor="center", pady=5)

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
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() + 0 * 3600))
        self.time_label.config(text=now)
        self.root.after(1000, self.update_time)

if __name__ == "__main__":
    root = tk.Tk()
    app = FC_GG_App(root)
    root.mainloop()
