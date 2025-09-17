import requests
import tkinter
from tkinter import messagebox  # 메시지 박스를 위해 추가
import time as t
import os
import pygame

# --- 변수 설정 ---
# API로부터 받은 실제 환율 값을 저장할 전역 변수
current_rate = 0.0 
earned = 0
grade = 0
money = 0
tm = 0

# Pygame mixer 초기화
pygame.mixer.init()

# --- 효과음 및 배경음악 로드 ---
# 배경음악 로드 및 재생
pygame.mixer.music.load("microchip.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(loops=-1)

# 효과음 로드  <-- 이 부분이 핵심!
click_sound = pygame.mixer.Sound("click_sound.mp3")
upgrade_sound = pygame.mixer.Sound("upgrade_sound.mp3")
fail_sound = pygame.mixer.Sound("fail_sound.mp3") # 실패 효과음 추가

# 효과음 볼륨 설정 (선택사항)
click_sound.set_volume(0.8)
upgrade_sound.set_volume(0.7)
fail_sound.set_volume(0.7)

# --- 함수 정의 ---
def update_exchange_rate():
    click_sound.play()
    "API를 호출하여 환율을 가져오고, 전역 변수와 UI 레이블을 업데이트하는 함수"
    global current_rate
    
    # API 주소 (기준 통화: LAK)
    url = "https://open.er-api.com/v6/latest/LAK"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # 요청 실패 시 예외 발생
        data = response.json()

        if data.get("result") == "success":
            rate = data.get("rates", {}).get("KRW")
            if rate:
                current_rate = rate  # 전역 변수에 숫자 환율 저장
                display_text = f"✅ 현재 환율: 1 LAK = {current_rate:.4f} KRW"
            else:
                display_text = "⚠️ KRW 통화 코드를 찾을 수 없습니다."
        else:
            display_text = "❌ 환율 정보 가져오기 실패"

    except requests.exceptions.RequestException:
        display_text = "❌ 네트워크 오류 발생"
    
    # UI 레이블 업데이트
    label2.config(text=display_text)

def earn():
    click_sound.play()
    "'돈벌기' 버튼 기능. 등급에 따라 돈을 법니다."
    global money
    earnings_per_grade = [1, 1.5, 2, 2.5, 3, 5, 7.5, 10, 20, 50, 100]
    if grade < len(earnings_per_grade):
        money += earnings_per_grade[grade]
    else: # 최대 등급 이상일 경우
        money += earnings_per_grade[-1]
    label1.config(text=f"{money:.1f} LAK")

def upgrade():

    "'업그레이드' 버튼 기능. 등급을 올립니다."
    global grade, money
    upgrade_cost = [50, 150, 200, 250, 300, 500, 750, 1000, 2000, 5000] 
    
    if grade >= len(upgrade_cost):
        messagebox.showinfo("업그레이드", "최고 레벨입니다!")
        return

    need_money = upgrade_cost[grade]
    
    if money >= need_money:
        upgrade_sound.play()
        money -= need_money
        grade += 1
        label1.config(text=f"{money:.1f} LAK")
        messagebox.showinfo("업그레이드 성공", f"등급이 {grade}가 되었습니다!\n다음 업그레이드 비용: {upgrade_cost[grade] if grade < len(upgrade_cost) else '없음'}")
    else:
        fail_sound.play()
        messagebox.showwarning("업그레이드 실패", f"돈이 부족합니다!\n필요한 돈: {need_money} LAK")

def get_money():
    click_sound.play()
    "'기록하기' 버튼 기능. 현재 LAK를 원화로 환산하여 파일에 기록합니다."
    global money, earned, current_rate
    
    if current_rate == 0.0:
        messagebox.showerror("오류", "환율 정보가 없습니다. '환율갱신'을 먼저 눌러주세요.")
        return

    tm = t.localtime(t.time())
    stm = t.strftime('%Y-%m-%d %I:%M:%S %p', tm)
    earned = money * current_rate  # 올바른 숫자 환율로 계산
    
    with open('Earnings.txt', 'a', encoding='utf-8') as file:
        file.write(f'{stm} / 환산 금액 : {earned:.2f} 원 (기준: {money:.1f} LAK)\n')

def quit_app():
    pygame.mixer.music.stop()
    app.destroy()

# --- UI 설정 ---
app = tkinter.Tk()
app.geometry('860x720+530+180')
app.title('Earn Money!')
app.resizable(0, 0)

# 파일 초기화 로직 (최초 실행 시 1회만)
if not os.path.exists('Earnings.txt'):
    with open('Earnings.txt', 'w', encoding='utf-8') as file:
        file.write('주의! / 프로그램으로 자동 작성되는 파일입니다. 건들지 말아주세요!\n\n')
        file.write('프로그램을 껐다 켜도 기록은 계속 누적됩니다.\n\n')

# 위젯 생성
label1 = tkinter.Label(app, text='0.0 LAK', font=('HY견고딕', 36))
label2 = tkinter.Label(app, text='환율 정보를 불러오는 중...', font=('맑은 고딕', 18))
label3 = tkinter.Label(app, text='게임을 꺼도 기록은 저장됩니다.', font=('맑은 고딕', 12))

b1 = tkinter.Button(app, text='돈벌기', command=earn)
b2 = tkinter.Button(app, text='업그레이드', command=upgrade)
b3 = tkinter.Button(app, text='기록하기', command=get_money)
b4 = tkinter.Button(app, text='종료하기', command=quit_app)
b5 = tkinter.Button(app, text='환율갱신', command=update_exchange_rate)

# 위젯 배치
label1.place(x=430, y=370, anchor='center')
label2.place(x=430, y=30, anchor='center')
label3.place(x=430, y=700, anchor='center')

b1.place(relx=0.1, rely=0.8, relwidth=0.15, relheight=0.1)
b2.place(relx=0.3, rely=0.8, relwidth=0.15, relheight=0.1)
b3.place(relx=0.5, rely=0.8, relwidth=0.15, relheight=0.1)
b4.place(relx=0.7, rely=0.8, relwidth=0.15, relheight=0.1)
b5.place(relx=0.3, rely=0.1, relwidth=0.4, relheight=0.05)

# 프로그램 시작 시 환율 자동 갱신
update_exchange_rate()

app.mainloop()
