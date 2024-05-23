import requests
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import ttk, messagebox
import tkintermapview

# API 정보
api_url = "https://openapi.gg.go.kr/GameSoftwaresFacilityProvis"
api_key = "9c52941f1f09418cb908e5388454c307"  # 여기에 자신의 API 키를 입력하세요.


def fetch_data(sigun_nm):
    # 요청 파라미터
    params = {
        "KEY": api_key,
        "Type": "xml",  # 응답 형식: xml
        "pIndex": 1,  # 페이지 위치
        "pSize": 1000,  # 페이지당 요청 수
        "SIGUN_NM": sigun_nm,  # 시군명
    }

    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        # XML 파싱
        root = ET.fromstring(response.content)
        items = root.findall(".//row")
        result = []
        for item in items:
            if item.findtext("BSN_STATE_NM") == "운영중":
                name = item.findtext("BIZPLC_NM")  # 업체명
                address = item.findtext("REFINE_ROADNM_ADDR")  # 도로명 주소
                lat = item.findtext("REFINE_WGS84_LAT")  # 위도
                lng = item.findtext("REFINE_WGS84_LOGT")  # 경도
                result.append((name, address, lat, lng))
        return result
    else:
        messagebox.showerror("Error", f"API request failed: {response.status_code}")
        return []


def show_pc_rooms():
    sigun_nm = city_combobox.get()
    if not sigun_nm:
        messagebox.showwarning("Warning", "Please select a city.")
        return

    pc_rooms = fetch_data(sigun_nm)
    if not pc_rooms:
        messagebox.showinfo("Info", "No operational PC rooms found in the selected city.")
        return

    # Find the first PC room to set the map position to that city
    if pc_rooms:
        first_pc_room = pc_rooms[0]
        lat = float(first_pc_room[2])
        lng = float(first_pc_room[3])
        map_widget.set_position(lat, lng)
        map_widget.set_zoom(18)  # Set default zoom level

    map_widget.delete_all_marker()

    for room in pc_rooms:
        try:
            lat = float(room[2])
            lng = float(room[3])
            map_widget.set_marker(lat, lng, text=room[0])
        except (ValueError, TypeError):
            continue


def open_address_window():
    address_window = tk.Toplevel(root)
    address_window.title("PC Room Addresses")
    address_window.geometry("800x500")

    top_frame = tk.Frame(address_window)
    top_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

    search_label = tk.Label(top_frame, text="PC Room Name:")
    search_label.pack(side=tk.LEFT, padx=5)

    search_entry = tk.Entry(top_frame)
    search_entry.pack(side=tk.LEFT, padx=5)

    address_tree = ttk.Treeview(address_window, columns=("Name", "Address", "Latitude", "Longitude"), show="headings")
    address_tree.heading("Name", text="Name")
    address_tree.heading("Address", text="Address")
    address_tree.heading("Latitude", text="Latitude")
    address_tree.heading("Longitude", text="Longitude")
    address_tree.pack(expand=True, fill="both")

    def on_treeview_double_click(event):
        item = address_tree.selection()[0]
        values = address_tree.item(item, "values")
        lat, lng = float(values[2]), float(values[3])
        map_widget.set_position(lat, lng)
        map_widget.set_zoom(18)  # Set default zoom level after double-click

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
        messagebox.showwarning("Warning", "Please select a city.")
        return

    pc_rooms = fetch_data(sigun_nm)
    if not pc_rooms:
        messagebox.showinfo("Info", "No operational PC rooms found in the selected city.")
        return

    for room in pc_rooms:
        address_tree.insert("", "end", values=room)

    search_button = tk.Button(top_frame, text="Search", command=filter_pc_rooms)
    search_button.pack(side=tk.LEFT, padx=5)


# GUI 설정
root = tk.Tk()
root.title("Gyeonggi Province PC Rooms")
root.geometry("1200x800")

# 상단 프레임
top_frame = tk.Frame(root)
top_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

# 도시 선택 콤보박스
tk.Label(top_frame, text="Select City:").pack(side=tk.LEFT, padx=10)
city_combobox = ttk.Combobox(top_frame, values=[
    "시흥시", "안산시", "수원시", "고양시", "성남시", "부천시", "광명시", "과천시", "광주시",
    "구리시", "군포시", "김포시", "남양주시", "동두천시", "문경시", "목포시", "양주시",
    "여주시", "연천군", "오산시", "용인시", "의왕시", "의정부시", "이천시", "파주시",
    "평택시", "포천시", "하남시", "화성시"
])
city_combobox.pack(side=tk.LEFT, padx=10)

# 조회 버튼
search_button = tk.Button(top_frame, text="Search", command=show_pc_rooms)
search_button.pack(side=tk.LEFT, padx=10)

# 지도 보기 버튼
address_button = tk.Button(top_frame, text="Show Addresses", command=open_address_window)
address_button.pack(side=tk.LEFT, padx=10)

# 지도 위젯
map_widget = tkintermapview.TkinterMapView(root, width=1200, height=700, corner_radius=0)
map_widget.set_position(37.339496586083, 126.73287520461)  # 초기 위치 설정
map_widget.set_zoom(18)  # 초기 줌 레벨 설정
map_widget.pack(expand=True, fill="both")

root.mainloop()