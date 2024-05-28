import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import smtplib
from email.mime.text import MIMEText
import pygame
import requests
import io
import json
import time
import os
from PIL import ImageGrab
from api_utils import get_ouid, get_user_info, get_match_ids, get_match_details, get_maxdivision, get_spid_metadata, get_division_data, get_season_metadata
import map_utils
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# 한글 폰트 설정
font_path = 'C:/Windows/Fonts/malgun.ttf'  # 시스템에 설치된 한글 폰트 경로로 변경 필요
font_name = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font_name)

class FC_GG_App:
    def __init__(self, root):
        self.root = root
        self.root.title("FC.GG")
        self.root.geometry("1000x700")
        self.season_data = get_season_metadata()

        self.favorites = []

        pygame.mixer.init()
        self.bgm_file = "FIFASOUND.mp3"
        pygame.mixer.music.load(self.bgm_file)
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)

        self.header_frame = tk.Frame(self.root, bg='light yellow')
        self.header_frame.pack(side="top", fill="x")

        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=1)
        self.header_frame.grid_columnconfigure(2, weight=1)
        self.header_frame.grid_columnconfigure(3, weight=1)
        self.header_frame.grid_columnconfigure(4, weight=1)

        self.logo_image = Image.open("photo/FCGG.png")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)

        self.logo_button = tk.Button(self.header_frame, image=self.logo_photo, command=self.open_logo_window,
                                     bg='light yellow')
        self.logo_button.grid(row=0, column=0, padx=0, pady=1)

        self.sound_on_image = Image.open("photo/1.png").convert("RGBA")
        self.sound_off_image = Image.open("photo/2.png").convert("RGBA")

        self.sound_on_image = ImageTk.PhotoImage(self.sound_on_image)
        self.sound_off_image = ImageTk.PhotoImage(self.sound_off_image)

        self.sound_button = tk.Button(self.header_frame, image=self.sound_on_image, command=self.toggle_sound,
                                      bg='light yellow')
        self.sound_button.grid(row=0, column=1, padx=10, pady=10)

        self.is_sound_on = True

        self.map_icon = Image.open("photo/map.png").convert("RGBA")
        self.map_icon = ImageTk.PhotoImage(self.map_icon)

        self.map_button = tk.Button(self.header_frame, image=self.map_icon, command=self.open_map_window,
                                    bg='light yellow')
        self.map_button.grid(row=0, column=2, padx=10, pady=10)

        self.squad_icon = Image.open("photo/스쿼드메이커.png").convert("RGBA")
        self.squad_icon = ImageTk.PhotoImage(self.squad_icon)

        self.squad_button = tk.Button(self.header_frame, image=self.squad_icon, command=self.open_squad_window,
                                      bg='light yellow')
        self.squad_button.grid(row=0, column=3, padx=10, pady=10)

        self.time_label = tk.Label(self.header_frame, font=("Helvetica", 16), bg='light yellow')
        self.time_label.grid(row=0, column=4, padx=10, pady=10)

        self.search_icon = Image.open("photo/돋보기.png").convert("RGBA")
        self.favorite_icon = Image.open("photo/별.png").convert("RGBA")
        self.no_check_icon = Image.open("photo/노체크.png").convert("RGBA")
        self.checked_icon = Image.open("photo/체크.png").convert("RGBA")

        self.search_icon = ImageTk.PhotoImage(self.search_icon)
        self.favorite_icon = ImageTk.PhotoImage(self.favorite_icon)
        self.no_check_icon = ImageTk.PhotoImage(self.no_check_icon)
        self.checked_icon = ImageTk.PhotoImage(self.checked_icon)

        self.search_button = tk.Button(self.header_frame, text="검색  ", image=self.search_icon, compound="left",
                                       command=self.create_search_screen)
        self.search_button.grid(row=0, column=5, padx=20, pady=20)

        self.favorites_button = tk.Button(self.header_frame, text="즐겨찾기  ", image=self.favorite_icon, compound="left",
                                          command=self.show_favorites_screen)
        self.favorites_button.grid(row=0, column=6, padx=20, pady=20)

        self.content_frame = tk.Frame(self.root, bg='white')
        self.content_frame.pack(fill="both", expand=True)

        self.spid_data = get_spid_metadata()

        self.check_button = None

        self.create_search_screen()

        self.after_id = None
        self.update_time()

        # Bind the close event to stop the timer and music
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
        pygame.mixer.music.stop()  # Stop the music
        pygame.mixer.quit()  # Quit pygame mixer
        self.root.destroy()

    def toggle_sound(self):
        if self.is_sound_on:
            pygame.mixer.music.pause()
            self.sound_button.config(image=self.sound_off_image)
        else:
            pygame.mixer.music.unpause()
            self.sound_button.config(image=self.sound_on_image)
        self.is_sound_on = not self.is_sound_on

    def update_time(self):
        if not self.root.winfo_exists():  # Check if the root window exists
            return
        now = time.strftime("%Y년 %m월 %d일\n%H시  %M분  %S초", time.localtime(time.time() + 0 * 3600))
        self.time_label.config(text=now)
        self.after_id = self.root.after(1000, self.update_time)
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

        self.search_result_frame = tk.Frame(right_frame, bg='light blue', height=40)
        self.search_result_frame.pack(fill="x")

        self.search_result_label = tk.Label(self.search_result_frame, text="검색 결과", font=("Helvetica", 16, "bold"),
                                            bg='light blue')
        self.search_result_label.pack(anchor="center", pady=10)

        self.results_canvas = tk.Canvas(right_frame, bg='white')
        self.results_scrollbar = tk.Scrollbar(right_frame, orient="vertical", command=self.results_canvas.yview)
        self.results_canvas.pack(side="left", fill="both", expand=True)
        self.results_canvas.configure(yscrollcommand=self.results_scrollbar.set)

        self.results_frame = tk.Frame(self.results_canvas, bg='white')
        self.results_canvas.create_window((0, 0), window=self.results_frame, anchor="center")
        self.results_frame.bind("<Configure>", self.on_frame_configure)

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

                self.clear_search_results()
                self.search_result_label.pack(anchor="center", pady=10)

                result_text = f"닉네임: {user_nickname}\n\nLevel: {user_level}\n\n최고 등급: {division_name}"
                result_label = tk.Label(self.results_frame, text=result_text, bg='white', font=("Helvetica", 30))

                result_label.pack(anchor="center", padx=150, pady=20)

                is_favorite = user_nickname in self.favorites
                check_icon = self.checked_icon if is_favorite else self.no_check_icon

                if not self.check_button:
                    self.check_button = tk.Button(self.search_result_frame, image=check_icon,
                                                  command=lambda: self.toggle_favorite(user_nickname), bg='light blue')
                    self.check_button.pack(side="right", padx=10)
                else:
                    self.check_button.config(image=check_icon, command=lambda: self.toggle_favorite(user_nickname))

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

        self.favorites_listbox = tk.Listbox(favorites_frame, height=15)
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
            max_division_id = get_maxdivision(ouid)

            division_data = get_division_data()
            division_name = next(
                (item['divisionName'] for item in division_data if item['divisionId'] == max_division_id),
                "Unknown Division")

            self.current_user_info = {
                "nickname": user_nickname,
                "level": user_level,
                "division": division_name
            }
            for widget in self.right_frame.winfo_children():
                widget.destroy()

            result_text = f"닉네임: {nickname}"
            result_label = tk.Label(self.right_frame, text=result_text, bg='white', font=("Helvetica", 30))
            result_label.pack(anchor="center", pady=5)

            match_history_button = tk.Button(self.right_frame, text="유저의 매치 기록 조회", command=self.show_match_history, font=("Helvetica", 20))
            match_history_button.pack(anchor="center", pady=10)

            transaction_history_button = tk.Button(self.right_frame, text="유저의 거래 기록 조회",
                                                   command=self.show_transaction_history, font=("Helvetica", 20))
            transaction_history_button.pack(anchor="center", pady=10)

            button_frame = tk.Frame(self.right_frame, bg='white')
            button_frame.pack(anchor="center", pady=10)

            self.telegram_image = Image.open("photo/텔레그램.png")
            self.telegram_photo = ImageTk.PhotoImage(self.telegram_image)
            telegram_button = tk.Button(button_frame, image=self.telegram_photo, command=self.telegram_bot,
                                        bg='white')
            telegram_button.pack(side="left", padx=20)

            self.mail_image = Image.open("photo/메일.png")
            self.mail_photo = ImageTk.PhotoImage(self.mail_image)
            mail_button = tk.Button(button_frame, image=self.mail_photo, command=self.send_email, bg='white')
            mail_button.pack(side="left", padx=20)

    def send_email(self):
        email_window = tk.Frame(self.content_frame, bg='white')
        email_window.pack(fill="both", expand=True)

        tk.Label(email_window, text="수신자 메일 주소를 입력해주세요", font=("Helvetica", 12)).pack(pady=5)
        recipient_entry = tk.Entry(email_window, font=("Helvetica", 12))
        recipient_entry.pack(fill="x", padx=10, pady=5)

        send_button = tk.Button(email_window, text="전송", font=("Helvetica", 12),
                                command=lambda: self.send_email_action(recipient_entry, email_window))
        send_button.pack(pady=10)

    def send_email_action(self, recipient_entry, email_window):
        recipient = recipient_entry.get()
        sender = "hih20553@gmail.com"
        subject = "이메일 전송 완료"

        if self.current_user_info:
            body = (f"닉네임: {self.current_user_info['nickname']}\n"
                    f"레벨: {self.current_user_info['level']}\n"
                    f"최고 등급: {self.current_user_info['division']}\n\n")

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipient

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender, "zbqf ctvk ktku rfes")
                server.sendmail(sender, recipient, msg.as_string())
            messagebox.showinfo("이메일 전송", f"메일 주소: {recipient}\n이메일이 전송 되었습니다!")
            email_window.destroy()
        except Exception as e:
            messagebox.showerror("이메일 전송 실패", str(e))

    def show_match_history(self):
        ouid = get_ouid(self.current_user_info['nickname'])
        match_ids = get_match_ids(ouid)
        match_details = get_match_details(match_ids)

        match_window = tk.Toplevel(self.root)
        match_window.title("매치 기록 조회")
        match_window.geometry("600x400")

        match_listbox = tk.Listbox(match_window, width=80, height=20)
        match_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(match_window, orient="vertical", command=match_listbox.yview)
        scrollbar.pack(side="right", fill="y")

        match_listbox.config(yscrollcommand=scrollbar.set)

        for match in match_details:
            myInfo = next(info for info in match['matchInfo'] if info['ouid'] == ouid)
            enemyInfo = next(info for info in match['matchInfo'] if info['ouid'] != ouid)

            # Get enemy user info
            enemy_ouid = enemyInfo['ouid']
            enemyname, enemylevel = get_user_info(enemy_ouid)

            matchtime = match['matchDate']
            result = myInfo['matchDetail']['matchResult']
            total_pass = myInfo['pass']['passTry']
            pass_success = myInfo['pass']['passSuccess']
            effective_shoot_total = myInfo['shoot']['effectiveShootTotal']
            pass_success_rate = (pass_success / total_pass) * 100 if total_pass > 0 else 0
            match_summary = f"시간: {matchtime}, 상대 닉네임: {enemyname}, 결과: {result}, 패스 성공률: {pass_success_rate:.2f}%, 유효 슈팅: {effective_shoot_total}\n\n+"
            match_listbox.insert(tk.END, match_summary)

        match_listbox.bind('<Double-1>',
                           lambda event: self.show_match_detail(event, match_details, match_listbox, ouid))

    def show_match_detail(self, event, match_details, match_listbox, ouid):
        selected_index = match_listbox.curselection()[0]
        selected_match = match_details[selected_index]
        match_detail = next(info for info in selected_match['matchInfo'] if info['ouid'] == ouid)
        opponent_detail = next(info for info in selected_match['matchInfo'] if info['ouid'] != ouid)

        detail_window = tk.Toplevel(self.root)
        detail_window.title("매치 상세 정보")
        detail_window.geometry("1200x800")

        canvas = tk.Canvas(detail_window)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(detail_window, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        match_time = selected_match['matchDate']
        result = match_detail['matchDetail']['matchResult']
        pass_success = match_detail['pass']['passSuccess']
        total_pass = match_detail['pass']['passTry']
        effective_shoot_total = match_detail['shoot']['effectiveShootTotal']
        shoot_total = match_detail['shoot']['shootTotal']
        pass_success_rate = (pass_success / total_pass) * 100 if total_pass > 0 else 0
        shoot_success_rate = (effective_shoot_total / shoot_total) * 100 if shoot_total > 0 else 0
        fouls = match_detail['matchDetail']['foul']

        opponent_pass_success = opponent_detail['pass']['passSuccess']
        opponent_total_pass = opponent_detail['pass']['passTry']
        opponent_effective_shoot_total = opponent_detail['shoot']['effectiveShootTotal']
        opponent_shoot_total = opponent_detail['shoot']['shootTotal']
        opponent_pass_success_rate = (
                                             opponent_pass_success / opponent_total_pass) * 100 if opponent_total_pass > 0 else 0
        opponent_shoot_success_rate = (
                                              opponent_effective_shoot_total / opponent_shoot_total) * 100 if opponent_shoot_total > 0 else 0
        opponent_fouls = opponent_detail['matchDetail']['foul']

        labels = ["슛", "유효슛", "슛 성공률", "패스 성공률", "파울"]
        my_values = [shoot_total, effective_shoot_total, shoot_success_rate, pass_success_rate, fouls]
        opponent_values = [opponent_shoot_total, opponent_effective_shoot_total, opponent_shoot_success_rate,
                           opponent_pass_success_rate, opponent_fouls]

        time_label = tk.Label(frame, text=f"시간: {match_time}")
        time_label.pack(pady=10)

        result_label = tk.Label(frame, text=f"Result: {result}")
        result_label.pack(pady=10)

        my_team_label = tk.Label(frame, text=f"우리팀: {match_detail['nickname']}", font=("Helvetica", 16))
        my_team_label.pack(side="left", padx=10, pady=10)

        opponent_team_label = tk.Label(frame, text=f"상대팀: {opponent_detail['nickname']}", font=("Helvetica", 16))
        opponent_team_label.pack(side="right", padx=10, pady=10)

        table_frame = tk.Frame(frame)
        table_frame.pack()

        fig, axs = plt.subplots(len(labels), 2, figsize=(8, 10))
        bar_width = 0.1  # 막대그래프 두께 조절

        for i, label in enumerate(labels):
            axs[i, 0].barh([label], [my_values[i]], color='#4CAF50', height=bar_width)
            axs[i, 0].set_xlim(0, max(max(my_values), max(opponent_values)) + 1)
            axs[i, 0].set_yticks([])  # Remove y-axis labels for left bars
            axs[i, 0].text(my_values[i] + 0.5, 0, f"{my_values[i]:.1f}", va='center')

            axs[i, 1].barh([label], [opponent_values[i]], color='#FF5733', height=bar_width)
            axs[i, 1].set_xlim(0, max(max(my_values), max(opponent_values)) + 1)
            axs[i, 1].set_yticks([])  # Remove y-axis labels for right bars
            axs[i, 1].text(opponent_values[i] + 0.5, 0, f"{opponent_values[i]:.1f}", va='center')
            axs[i, 1].invert_xaxis()

        for ax, label in zip(axs[:, 0], labels):
            ax.set_ylabel(label, labelpad=15)  # Add the label in the middle

        fig.tight_layout()

        canvas_agg = FigureCanvasTkAgg(fig, master=frame)
        canvas_agg.draw()
        canvas_agg.get_tk_widget().pack(pady=20)

    def telegram_bot(self):
        messagebox.showinfo("기능 미구현", "텔레그램 기능은 아직 구현되지 않았습니다.")

    def show_transaction_history(self):
        messagebox.showinfo("기능 미구현", "유저의 거래 기록 조회 기능은 아직 구현되지 않았습니다.")

    def show_player_results(self):
        player_name = self.player_entry.get().lower()
        if player_name:
            matching_players = [player for player in self.spid_data if player_name in player['name'].lower()]

            self.clear_search_results()
            self.search_result_label.pack(anchor="center", pady=10)

            if matching_players:
                for player in matching_players:
                    season_id = str(player['id'])[:3]
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
                        image_label.image = photo
                        image_label.pack(side="left", padx=10)

                        if season_image_url:
                            season_response = requests.get(season_image_url)
                            if season_response.status_code == 200:
                                season_image_data = season_response.content
                                season_image = Image.open(io.BytesIO(season_image_data))
                                season_photo = ImageTk.PhotoImage(season_image)
                                season_image_label = tk.Label(frame, image=season_photo, bg='white')
                                season_image_label.image = season_photo
                                season_image_label.pack(side="left", padx=10)

                        text_label = tk.Label(frame, text=f"Player Name: {player['name']}", bg='white',
                                              font=("Helvetica", 12))
                        text_label.pack(side="left")
            else:
                result_label = tk.Label(self.results_frame, text="No matching players found.", bg='white',
                                        font=("Helvetica", 12))
                result_label.pack(anchor="center", pady=5)

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
        map_utils.initialize_map(self.root, self)

    def open_squad_window(self):
        # Clear the main content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        top_frame = tk.Frame(self.content_frame)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        label = tk.Label(top_frame, text="포메이션 선택", font=("Helvetica", 20))
        label.pack(pady=10)

        self.squad_combobox = ttk.Combobox(top_frame, values=["4-2-3-1", "4-4-2", "4-3-3"])
        self.squad_combobox.pack(side=tk.TOP, padx=10)
        self.squad_combobox.bind("<<ComboboxSelected>>", self.display_formation)

        self.large_frame = tk.Frame(self.content_frame, bg='light gray')
        self.large_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        save_button = tk.Button(self.content_frame, text="저장", command=self.save_squad_image)
        save_button.place(relx=0.95, rely=0.05, anchor="ne")

        self.root.after(100, self.load_and_display_image, self.large_frame, "photo/축구장.png")

        self.plus_image = Image.open("photo/플러스.png")
        self.plus_photo = ImageTk.PhotoImage(self.plus_image)
        self.player_buttons = []

    def save_squad_image(self):
        x = self.large_frame.winfo_rootx()
        y = self.large_frame.winfo_rooty()
        width = self.large_frame.winfo_width()
        height = self.large_frame.winfo_height()

        image = ImageGrab.grab().crop((x, y, x + width, y + height))

        base_filename = "squad_image"
        file_extension = ".png"
        file_number = 1

        while os.path.exists(f"{base_filename}{file_number}{file_extension}"):
            file_number += 1

        file_name = f"{base_filename}{file_number}{file_extension}"
        image.save(file_name)
        messagebox.showinfo("저장 완료", f"스쿼드 이미지가 {file_name}으로 저장되었습니다!")

    def load_and_display_image(self, frame, image_path):
        frame.update_idletasks()
        frame_width = frame.winfo_width()
        frame_height = frame.winfo_height()

        image = Image.open(image_path)
        image = image.resize((frame_width, frame_height), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)

        image_label = tk.Label(frame, image=photo, bg='white')
        image_label.image = photo
        image_label.pack(fill=tk.BOTH, expand=True)

    def open_player_search_window(self, pos_index):
        search_window = tk.Toplevel(self.root)
        search_window.title("선수 검색")
        search_window.geometry("500x700")

        tk.Label(search_window, text="선수 이름 검색:", font=("Helvetica", 12)).pack(pady=10)
        search_entry = tk.Entry(search_window, font=("Helvetica", 12))
        search_entry.pack(fill="x", padx=10, pady=5)

        search_button = tk.Button(search_window, text="검색", font=("Helvetica", 12),
                                  command=lambda: self.search_players(search_entry.get(), search_window, pos_index))
        search_button.pack(pady=10)

        self.search_result_frame = tk.Frame(search_window, bg='white')
        self.search_result_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.search_result_canvas = tk.Canvas(self.search_result_frame, bg='white')
        self.search_result_scrollbar = tk.Scrollbar(self.search_result_frame, orient="vertical",
                                                    command=self.search_result_canvas.yview)
        self.search_result_canvas.configure(yscrollcommand=self.search_result_scrollbar.set)

        self.search_result_inner_frame = tk.Frame(self.search_result_canvas, bg='white')

        self.search_result_canvas.create_window((0, 0), window=self.search_result_inner_frame, anchor="nw")
        self.search_result_inner_frame.bind("<Configure>", lambda e: self.search_result_canvas.configure(
            scrollregion=self.search_result_canvas.bbox("all")))

        self.search_result_canvas.pack(side="left", fill="both", expand=True)
        self.search_result_scrollbar.pack(side="right", fill="y")

    def search_players(self, player_name, window, position):
        if player_name:
            matching_players = [player for player in self.spid_data if player_name.lower() in player['name'].lower()]

            for widget in self.search_result_inner_frame.winfo_children():
                widget.destroy()

            if matching_players:
                for player in matching_players:
                    season_id = str(player['id'])[:3]
                    season_image_url = next(
                        (season['seasonImg'] for season in self.season_data if season['seasonId'] == int(season_id)),
                        None)

                    if season_image_url:
                        response = requests.get(season_image_url)
                        if response.status_code == 200:
                            image_data = response.content
                            image = Image.open(io.BytesIO(image_data))
                            photo = ImageTk.PhotoImage(image)
                            player_button = tk.Button(self.search_result_inner_frame, image=photo,
                                                      command=lambda p=player: self.select_season(p, position, window),
                                                      bg='white')
                            player_button.image = photo
                            player_button.pack(side="top", padx=10, pady=5)
            else:
                result_label = tk.Label(self.search_result_inner_frame, text="X", bg='white',
                                        font=("Helvetica", 12))
                result_label.pack(anchor="center", pady=5)
        else:
            messagebox.showwarning("경고", "선수 이름을 입력해주세요.")

    def select_season(self, player, position, window):
        player_image_url = f"https://fco.dn.nexoncdn.co.kr/live/externalAssets/common/playersAction/p{player['id']}.png"
        response = requests.get(player_image_url)
        if response.status_code == 200:
            image_data = response.content
            image = Image.open(io.BytesIO(image_data))
            image = image.resize((100, 100), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)

            button = self.player_buttons[position]
            button.config(image=photo, command=lambda: self.open_player_search_window(position))
            button.image = photo
            window.destroy()
        else:
            messagebox.showerror("오류", "NEXON API에 등록된 이미지가 없어요ㅠㅠ.")

    def select_player(self, player, position, window):
        self.player_buttons[position].config(text=player['name'], image='', compound='center')
        window.destroy()

    def display_formation(self, event):
        selected_formation = self.squad_combobox.get()

        if selected_formation == "4-2-3-1":
            positions = [
                (0.5, 0.2),
                (0.5, 0.4),
                (0.3, 0.4),
                (0.7, 0.4),
                (0.4, 0.6),
                (0.6, 0.6),
                (0.2, 0.8),
                (0.8, 0.8),
                (0.35, 0.8),
                (0.65, 0.8),
                (0.5, 0.9)
            ]
        elif selected_formation == "4-4-2":
            positions = [
                (0.3, 0.2),
                (0.7, 0.2),
                (0.2, 0.4),
                (0.8, 0.4),
                (0.4, 0.4),
                (0.6, 0.4),
                (0.2, 0.8),
                (0.8, 0.8),
                (0.35, 0.8),
                (0.65, 0.8),
                (0.5, 0.9)
            ]
        elif selected_formation == "4-3-3":
            positions = [
                (0.2, 0.2),
                (0.5, 0.2),
                (0.8, 0.2),
                (0.35, 0.4),
                (0.65, 0.4),
                (0.5, 0.6),
                (0.2, 0.8),
                (0.8, 0.8),
                (0.35, 0.8),
                (0.65, 0.8),
                (0.5, 0.9)
            ]

        for button in self.player_buttons:
            button.destroy()

        self.player_buttons = []
        for i, (x, y) in enumerate(positions):
            button = tk.Button(self.large_frame, image=self.plus_photo, bg='white',
                               command=lambda pos=i: self.open_player_search_window(pos))
            button.place(relx=x, rely=y, anchor="center")
            self.player_buttons.append(button)

    def open_logo_window(self):
        logo_window = tk.Frame(self.content_frame, bg='white')
        logo_window.pack(fill="both", expand=True)

        info_label = tk.Label(logo_window, text="한국공학대학교\n\n2020180002 곽정민\n2020184038 황성하", font=("Helvetica", 18))
        info_label.pack(expand=True, fill="both", padx=10, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = FC_GG_App(root)
    root.mainloop()
