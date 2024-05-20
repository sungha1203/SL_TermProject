import tkinter as tk

class FC_GG_App:
    def __init__(self, root):
        self.root = root
        self.root.title("FC.GG")
        self.root.geometry("1000x700")  # 윈도우 크기 설정

        self.header_frame = tk.Frame(self.root, bg='lightgrey')
        self.header_frame.pack(side="top", fill="x")

        self.logo_label = tk.Label(self.header_frame, text="FC.GG", font=("Helvetica", 24), bg='lightgrey')
        self.logo_label.pack(side="left", padx=10, pady=10)

        self.favorites_button = tk.Button(self.header_frame, text="즐겨찾기", command=self.show_favorites_screen)
        self.favorites_button.pack(side="right", padx=50, pady=10)

        self.search_button = tk.Button(self.header_frame, text="검색", command=self.create_search_screen)
        self.search_button.pack(side="right", padx=50, pady=10)

        self.content_frame = tk.Frame(self.root, bg='white')
        self.content_frame.pack(fill="both", expand=True)

        self.create_search_screen()

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
        search_result_frame = tk.Frame(right_frame, bg='lightgrey')
        search_result_frame.pack(fill="x")

        tk.Label(search_result_frame, text="검색 결과", font=("Helvetica", 16, "bold"), bg='lightgrey').pack(
            anchor="center", pady=10)
        # 여기에 검색 결과 내용을 추가하세요.

    def show_search_results(self):
        self.create_search_screen()
        # 실제 검색 결과를 표시하는 코드를 여기에 추가합니다.

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

if __name__ == "__main__":
    root = tk.Tk()
    app = FC_GG_App(root)
    root.mainloop()
