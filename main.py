import pygame
import json
import sys
import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

# --- INISIALISASI ---
root = tk.Tk()
root.withdraw()
pygame.init()
pygame.mixer.init()

SCREEN = pygame.display.set_mode((1200, 800))
pygame.display.set_caption("Family 100 - Ultimate Edition")

# --- WARNA & FONT ---
YELLOW = (255, 255, 0)
WHITE  = (255, 255, 255)
RED    = (255, 0, 0)
GRAY   = (50, 50, 50)

def get_font(size):
    try: return pygame.font.Font("font_game.ttf", size)
    except: return pygame.font.SysFont("Arial", size, bold=True)

font_score = get_font(55)
font_main = get_font(28)
font_x = get_font(100)
font_admin = pygame.font.SysFont("Arial", 16)

# --- LOAD SOUNDS ---
def load_s(file):
    try: return pygame.mixer.Sound(file)
    except: return None

s_correct = load_s("correct.mp3")
s_wrong = load_s("wrong.mp3")
s_fm_correct = load_s("fm_correct.wav")
s_reveal = load_s("score_reveal.wav")
s_buzzer = load_s("timer_end.wav")

# --- LOGIKA DATA ---
current_file = "soal.json"
def load_data(path):
    try:
        with open(path, 'r') as f: return json.load(f)
    except: return None

data = load_data(current_file)
if not data: 
    print("Gagal memuat soal. Pastikan soal.json ada."); pygame.quit(); sys.exit()

# --- STATE GAME ---
is_fm = False
idx_n = 0
skor_t1, skor_t2, skor_mid = 0, 0, 0
salah1, salah2 = 0, 0
fm_st = {"b_j1":[False]*5, "b_s1":[False]*5, "b_j2":[False]*5, "b_s2":[False]*5, "timer":20, "s_t":False, "tick":0}

try:
    bg = pygame.image.load("board.png")
    bg = pygame.transform.scale(bg, (1200, 800))
except:
    bg = pygame.Surface((1200, 800))

def draw_t(txt, font, col, x, y, center=True):
    img = font.render(str(txt), True, col)
    rect = img.get_rect(center=(x,y)) if center else img.get_rect(topleft=(x,y))
    SCREEN.blit(img, rect)

# --- MAIN LOOP ---
running = True
while running:
    SCREEN.blit(bg, (0,0))
    
    if not is_fm:
        # MODE NORMAL
        soal = data["normal_mode"][idx_n]
        mult = soal.get("multiplier", 1)
        draw_t(f"RONDE {soal['ronde']} - {mult}X SCORE", font_main, YELLOW, 600, 35)
        draw_t(skor_t1, font_score, YELLOW, 150, 85); draw_t(skor_mid, font_score, YELLOW, 600, 85); draw_t(skor_t2, font_score, YELLOW, 1050, 85)
        for i in range(4):
            draw_t("X", font_x, RED if i < salah1 else GRAY, 100+(i*70), 195)
            draw_t("X", font_x, RED if i < salah2 else GRAY, 880+(i*70), 195)
        draw_t(soal["pertanyaan"], font_main, YELLOW, 600, 220)
        for i in range(8):
            y_p = 340 + (i * 45)
            if i < len(soal["jawaban"]):
                item = soal["jawaban"][i]
                if "buka" in item:
                    draw_t(f"{i+1}. {item['teks']}", font_main, YELLOW, 350, y_p, False)
                    draw_t(item['skor']*mult, font_main, YELLOW, 850, y_p)
                else: draw_t(f"{i+1}. ....................", font_main, (150,150,0), 350, y_p, False)
    else:
        # MODE FAST MONEY
        draw_t("FAST MONEY ROUND", font_score, YELLOW, 600, 45)
        fdb = data["fast_money"]
        for i in range(5):
            y_p = 180 + (i * 85)
            t1 = fdb["P1"]["jwb"][i] if fm_st["b_j1"][i] else "---"
            draw_t(f"{i+1}. {t1}", font_main, YELLOW, 120, y_p, False)
            s1 = fdb["P1"]["skr"][i] if fm_st["b_s1"][i] else "--"
            draw_t(s1, font_main, YELLOW, 520, y_p)
            t2 = fdb["P2"]["jwb"][i] if fm_st["b_j2"][i] else "---"
            draw_t(f"{i+1}. {t2}", font_main, YELLOW, 680, y_p, False)
            s2 = fdb["P2"]["skr"][i] if fm_st["b_s2"][i] else "--"
            draw_t(s2, font_main, YELLOW, 1080, y_p)
        if fm_st["s_t"]:
            draw_t(fm_st["timer"], font_x, WHITE, 600, 650)
            if fm_st["timer"] > 0 and pygame.time.get_ticks() - fm_st["tick"] >= 1000:
                fm_st["timer"] -= 1; fm_st["tick"] = pygame.time.get_ticks()
                if fm_st["timer"] == 0 and s_buzzer: s_buzzer.play()

    draw_t(f"[L] Load | [E] Edit | [R] Reload | [M] Switch | [N/P] Ronde", font_admin, WHITE, 10, 775, False)

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT: running = False
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_m: is_fm = not is_fm
            if ev.key == pygame.K_l:
                p = filedialog.askopenfilename(filetypes=[("JSON","*.json")])
                if p: current_file = p; data = load_data(p); idx_n = 0
            if ev.key == pygame.K_e:
                if sys.platform == "win32": os.startfile(current_file)
                else: subprocess.call(["open", current_file])
            if ev.key == pygame.K_r: data = load_data(current_file)

            if not is_fm:
                if ev.key == pygame.K_z: salah1 = (salah1+1)%5; (s_wrong.play() if s_wrong else None)
                if ev.key == pygame.K_x: salah2 = (salah2+1)%5; (s_wrong.play() if s_wrong else None)
                if pygame.K_1 <= ev.key <= pygame.K_8:
                    idx = ev.key - pygame.K_1
                    if idx < len(data["normal_mode"][idx_n]["jawaban"]):
                        if "buka" not in data["normal_mode"][idx_n]["jawaban"][idx]:
                            data["normal_mode"][idx_n]["jawaban"][idx]["buka"] = True
                            skor_mid += data["normal_mode"][idx_n]["jawaban"][idx]["skor"] * data["normal_mode"][idx_n].get("multiplier", 1)
                            (s_correct.play() if s_correct else None)
                if ev.key == pygame.K_q: skor_t1 += skor_mid; skor_mid = 0
                if ev.key == pygame.K_w: skor_t2 += skor_mid; skor_mid = 0
                if ev.key == pygame.K_n: idx_n = (idx_n+1)%len(data["normal_mode"]); skor_mid=0; salah1=0; salah2=0
            else:
                if pygame.K_1 <= ev.key <= pygame.K_5: 
                    fm_st["b_j1"][ev.key-pygame.K_1] = True; (s_fm_correct.play() if s_fm_correct else None)
                pk1 = [pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_r, pygame.K_t]
                if ev.key in pk1: fm_st["b_s1"][pk1.index(ev.key)] = True; (s_reveal.play() if s_reveal else None)
                if pygame.K_6 <= ev.key <= pygame.K_0: 
                    idx = 4 if ev.key == pygame.K_0 else ev.key-pygame.K_6
                    fm_st["b_j2"][idx] = True; (s_fm_correct.play() if s_fm_correct else None)
                pk2 = [pygame.K_y, pygame.K_u, pygame.K_i, pygame.K_o, pygame.K_p]
                if ev.key in pk2: fm_st["b_s2"][pk2.index(ev.key)] = True; (s_reveal.play() if s_reveal else None)
                if ev.key == pygame.K_v: fm_st["s_t"] = not fm_st["s_t"]; fm_st["tick"] = pygame.time.get_ticks()
                if ev.key == pygame.K_b: fm_st.update({"timer":20, "s_t":False, "b_j1":[False]*5, "b_s1":[False]*5, "b_j2":[False]*5, "b_s2":[False]*5})

    pygame.display.flip()
pygame.quit()
