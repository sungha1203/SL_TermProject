import tkinter as tk
from tkinter import ttk, messagebox
import tkintermapview
from api_utils import fetch_data

def initialize_map(root, app):
    map_window = tk.Toplevel(root)
    map_window.title("지역별 PC방 찾기")
    map_window.geometry("1200x800")

    top_frame = tk.Frame(map_window)
    top_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

    tk.Label(top_frame, text="도시 선택:").pack(side=tk.LEFT, padx=10)
    city_combobox = ttk.Combobox(top_frame, values=[
        "시흥시", "안산시", "수원시", "고양시", "성남시", "부천시", "광명시", "과천시", "광주시",
        "구리시", "군포시", "김포시", "남양주시", "동두천시", "문경시", "목포시", "양주시",
        "여주시", "연천군", "오산시", "용인시", "의왕시", "의정부시", "이천시", "파주시",
        "평택시", "포천시", "하남시", "화성시"
    ])
    city_combobox.pack(side=tk.LEFT, padx=10)

    search_button = tk.Button(top_frame, text="검색",
                              command=lambda: show_pc_rooms(app, map_widget, city_combobox))
    search_button.pack(side=tk.LEFT, padx=10)

    address_button = tk.Button(top_frame, text="피시방 찾기",
                               command=lambda: open_address_window(root, map_widget, city_combobox))
    address_button.pack(side=tk.LEFT, padx=10)

    map_widget = tkintermapview.TkinterMapView(map_window, width=1200, height=700, corner_radius=0)
    map_widget.set_position(37.339496586083, 126.73287520461)
    map_widget.set_zoom(18)
    map_widget.pack(expand=True, fill="both")

def show_pc_rooms(app, map_widget, city_combobox):
    sigun_nm = city_combobox.get()
    if not sigun_nm:
        messagebox.showwarning("Warning", "Please select a city.")
        return

    pc_rooms = fetch_data(sigun_nm)
    if not pc_rooms:
        messagebox.showinfo("Info", "No operational PC rooms found in the selected city.")
        return

    if pc_rooms:
        first_pc_room = pc_rooms[0]
        lat = float(first_pc_room[2])
        lng = float(first_pc_room[3])
        map_widget.set_position(lat, lng)
        map_widget.set_zoom(18)

    map_widget.delete_all_marker()

    for room in pc_rooms:
        try:
            lat = float(room[2])
            lng = float(room[3])
            map_widget.set_marker(lat, lng, text=room[0])
        except (ValueError, TypeError):
            continue

def open_address_window(root, map_widget, city_combobox):
    address_window = tk.Toplevel(root)
    address_window.title("PC Room Addresses")
    address_window.geometry("800x500")

    top_frame = tk.Frame(address_window)
    top_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

    search_label = tk.Label(top_frame, text="PC방 이름 검색:")
    search_label.pack(side=tk.LEFT, padx=5)

    search_entry = tk.Entry(top_frame)
    search_entry.pack(side=tk.LEFT, padx=5)

    address_tree = ttk.Treeview(address_window, columns=("Name", "Address", "Latitude", "Longitude"),
                                show="headings")
    address_tree.heading("Name", text="이름")
    address_tree.heading("Address", text="주소")
    address_tree.heading("Latitude", text="위도")
    address_tree.heading("Longitude", text="경도")
    address_tree.pack(expand=True, fill="both")

    def on_treeview_double_click(event):
        item = address_tree.selection()[0]
        values = address_tree.item(item, "values")
        lat, lng = float(values[2]), float(values[3])
        map_widget.set_position(lat, lng)
        map_widget.set_zoom(18)

    address_tree.bind("<Double-1>", on_treeview_double_click)

    def filter_pc_rooms():
        keyword = search_entry.get()
        for row in address_tree.get_children():
            address_tree.delete(row)

        for room in pc_rooms:
            if keyword.lower() in room[0].lower():
                address_tree.insert("", "end", values=room)

    sigun_nm = city_combobox.get()
    if not sigun_nm:
        messagebox.showwarning("Warning", "Please 도시 선택.")
        return

    pc_rooms = fetch_data(sigun_nm)
    if not pc_rooms:
        messagebox.showinfo("Info", "PC방이 없습니다 ㅠ.")
        return

    for room in pc_rooms:
        address_tree.insert("", "end", values=room)

    search_button = tk.Button(top_frame, text="검색", command=filter_pc_rooms)
    search_button.pack(side=tk.LEFT, padx=5)