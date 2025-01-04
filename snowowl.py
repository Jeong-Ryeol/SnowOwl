import pyautogui
import time
import tkinter as tk
from threading import Thread
import threading
import win32gui
import win32con
import win32api

class AutoClicker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ARK 자동 우클릭")
        self.root.geometry("300x500")
        
        self.is_running = False
        self.click_thread = None
        self.key_thread = None
        self.key_counts = {i: 0 for i in range(1, 9)}  # 1-8까지의 키 사용 횟수
        
        # 숫자 키 체크박스 프레임
        key_frame = tk.LabelFrame(self.root, text="30분마다 누를 키")
        key_frame.pack(pady=10, padx=10, fill="x")
        
        # 체크박스 변수들
        self.key_vars = {}
        for i in range(1, 9):  # 1-8까지만 생성
            self.key_vars[i] = tk.BooleanVar()
            cb = tk.Checkbutton(key_frame, text=str(i), variable=self.key_vars[i])
            cb.grid(row=(i-1)//3, column=(i-1)%3, padx=10, pady=5)
        
        # 시간 설정 프레임
        time_frame = tk.Frame(self.root)
        time_frame.pack(pady=10)
        
        # 클릭 유지 시간 설정
        tk.Label(time_frame, text="클릭 유지 시간(초):").pack(side=tk.LEFT)
        self.hold_time = tk.StringVar(value="40")
        self.hold_entry = tk.Entry(time_frame, textvariable=self.hold_time, width=5)
        self.hold_entry.pack(side=tk.LEFT, padx=5)
        
        # 대기 시간 설정
        wait_frame = tk.Frame(self.root)
        wait_frame.pack(pady=10)
        tk.Label(wait_frame, text="대기 시간(초):").pack(side=tk.LEFT)
        self.wait_time = tk.StringVar(value="15")
        self.wait_entry = tk.Entry(wait_frame, textvariable=self.wait_time, width=5)
        self.wait_entry.pack(side=tk.LEFT, padx=5)
        
        # 임프린트 타이머 프레임 추가
        timer_frame = tk.LabelFrame(self.root, text="임프린트 타이머")
        timer_frame.pack(pady=10, padx=10, fill="x")
        
        # 시간 입력 프레임
        time_input_frame = tk.Frame(timer_frame)
        time_input_frame.pack(pady=5)
        
        # 시간 선택
        tk.Label(time_input_frame, text="시:").pack(side=tk.LEFT)
        self.hours = tk.StringVar(value="0")
        tk.Entry(time_input_frame, textvariable=self.hours, width=3).pack(side=tk.LEFT, padx=2)
        
        tk.Label(time_input_frame, text="분:").pack(side=tk.LEFT)
        self.minutes = tk.StringVar(value="0")
        tk.Entry(time_input_frame, textvariable=self.minutes, width=3).pack(side=tk.LEFT, padx=2)
        
        # 타이머 표시 레이블
        self.timer_label = tk.Label(timer_frame, text="남은 시간: --:--")
        self.timer_label.pack(pady=5)
        
        # 임프린트 알림 레이블
        self.imprint_label = tk.Label(timer_frame, text="", font=("Arial", 12, "bold"))
        self.imprint_label.pack(pady=5)
        
        # 시작/정지 버튼
        self.toggle_button = tk.Button(self.root, text="시작", command=self.toggle_clicking)
        self.toggle_button.pack(pady=10)
        
        # 상태 레이블
        self.status_label = tk.Label(self.root, text="대기 중...")
        self.status_label.pack(pady=10)
        
        # 종료 버튼
        self.quit_button = tk.Button(self.root, text="프로그램 종료", command=self.root.quit)
        self.quit_button.pack(pady=10)

        self.timer_thread = None
        self.end_time = None

    def send_key(self, key):
        hwnd = self.find_ark_window()
        if hwnd:
            win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, ord(str(key)), 0)
            time.sleep(0.1)
            win32gui.PostMessage(hwnd, win32con.WM_KEYUP, ord(str(key)), 0)

    def get_next_available_keys(self):
        checked_keys = [k for k, v in self.key_vars.items() if v.get()]
        # 키를 2개씩 그룹화
        key_groups = [checked_keys[i:i+2] for i in range(0, len(checked_keys), 2)]
        
        for group in key_groups:
            # 그룹의 모든 키가 20번 미만 사용되었는지 확인
            if all(self.key_counts[key] < 20 for key in group):
                return group
        return None

    def key_press_loop(self):
        while self.is_running:
            current_keys = self.get_next_available_keys()
            if current_keys:
                keys_str = ','.join(str(k) for k in current_keys)
                self.status_label.config(text=f"{keys_str}번 키 누르는 중... (사용횟수: {self.key_counts[current_keys[0]] + 1}/20)")
                
                # 그룹의 모든 키 누르기
                for key in current_keys:
                    self.send_key(key)
                    time.sleep(0.5)
                
                # 모든 키의 카운트 증가
                for key in current_keys:
                    self.key_counts[key] += 1
            
            self.status_label.config(text="자동 클릭 진행 중...")
            time.sleep(1800)  # 30분 대기
            
            if not self.is_running:
                break

    def get_hold_time(self):
        try:
            return max(1, int(self.hold_time.get()))
        except ValueError:
            self.hold_time.set("40")
            return 40
    
    def get_wait_time(self):
        try:
            return max(1, int(self.wait_time.get()))
        except ValueError:
            self.wait_time.set("15")
            return 15
    
    def find_ark_window(self):
        return win32gui.FindWindow(None, "ARKAscended")
    
    def background_right_click(self):
        hwnd = self.find_ark_window()
        if hwnd:
            # 창의 크기와 위치 가져오기
            rect = win32gui.GetWindowRect(hwnd)
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]
            
            # 창의 중앙 좌표 계산
            center_x = width // 2
            center_y = height // 2
            
            # 중앙 좌표로 클릭 이벤트 전송
            win32gui.PostMessage(hwnd, win32con.WM_RBUTTONDOWN, 0, center_y << 16 | center_x)
            return True
        return False
    
    def release_right_click(self):
        hwnd = self.find_ark_window()
        if hwnd:
            # 창의 크기와 위치 가져오기
            rect = win32gui.GetWindowRect(hwnd)
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]
            
            # 창의 중앙 좌표 계산
            center_x = width // 2
            center_y = height // 2
            
            # 중앙 좌표로 클릭 해제 이벤트 전송
            win32gui.PostMessage(hwnd, win32con.WM_RBUTTONUP, 0, center_y << 16 | center_x)
    
    def auto_right_click(self):
        while self.is_running:
            self.status_label.config(text="시작합니다...")
            
            if not self.is_running:
                break
                
            self.status_label.config(text="우클릭 누르는 중...")
            if self.background_right_click():
                hold_duration = self.get_hold_time()
                self.status_label.config(text=f"우클릭 {hold_duration}초 유지 중...")
                time.sleep(hold_duration)
                
                if not self.is_running:
                    self.release_right_click()
                    break
                    
                self.status_label.config(text="우클릭 떼는 중...")
                self.release_right_click()
                
                wait_duration = self.get_wait_time()
                self.status_label.config(text=f"{wait_duration}초 후에 다시 시작합니다...")
                time.sleep(wait_duration)
            else:
                self.status_label.config(text="ARK 창을 찾을 수 없습니다!")
                time.sleep(5)
    
    def start_timer(self):
        try:
            hours = int(self.hours.get())
            minutes = int(self.minutes.get())
            total_seconds = hours * 3600 + minutes * 60
            
            if total_seconds > 0:
                self.end_time = time.time() + total_seconds
                if self.timer_thread is None or not self.timer_thread.is_alive():
                    self.timer_thread = Thread(target=self.timer_loop)
                    self.timer_thread.daemon = True
                    self.timer_thread.start()
        except ValueError:
            self.timer_label.config(text="시간을 올바르게 입력하세요")

    def timer_loop(self):
        while self.is_running and self.end_time:
            remaining = max(0, self.end_time - time.time())
            hours = int(remaining // 3600)
            minutes = int((remaining % 3600) // 60)
            seconds = int(remaining % 60)
            
            self.timer_label.config(text=f"남은 시간: {hours:02d}:{minutes:02d}:{seconds:02d}")
            
            if remaining <= 0:
                self.imprint_label.config(text="IMPRINT!", fg="red")
                # 5초 동안 표시 후 초기화
                time.sleep(5)
                self.imprint_label.config(text="")
                self.end_time = None
                break
            
            time.sleep(1)

    def toggle_clicking(self):
        if not self.is_running:
            self.is_running = True
            # 카운트 초기화
            self.key_counts = {i: 0 for i in range(1, 9)}
            self.toggle_button.config(text="정지")
            self.click_thread = Thread(target=self.auto_right_click)
            self.key_thread = Thread(target=self.key_press_loop)
            self.click_thread.daemon = True
            self.key_thread.daemon = True
            self.click_thread.start()
            self.key_thread.start()
            # 타이머 시작
            self.start_timer()
        else:
            self.is_running = False
            self.toggle_button.config(text="시작")
            self.status_label.config(text="대기 중...")
            self.release_right_click()
            self.end_time = None  # 타이머 중지
            self.timer_label.config(text="남은 시간: --:--")
            self.imprint_label.config(text="")
            time.sleep(0.5)
    
    def run(self):
        # 창이 닫힐 때 정리 작업을 수행하는 핸들러 추가
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        """창이 닫힐 때 호출되는 메서드"""
        self.is_running = False
        self.end_time = None  # 타이머 중지
        self.release_right_click()
        time.sleep(0.5)
        self.root.destroy()

if __name__ == "__main__":
    app = AutoClicker()
    app.run()
