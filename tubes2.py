import pygame
import sys
import random

try:
    import databases.databases as databases
    databases.init_login_db()
    databases.init_data_diri_db()
    databases.init_kereta_db()
    USE_DATABASE = True
except Exception as e:
    print("Warning: databases module not found or failed init. Running without DB. Error:", e)
    USE_DATABASE = False

pygame.init()

# ============================================================
#                         WINDOW
# ============================================================
WIDTH, HEIGHT = 800, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("KAI Access - Sistem Tiket KRL")
CLOCK = pygame.time.Clock()
FPS = 60

# ============================================================
#                         FONTS & COLORS
# ============================================================
TITLE_FONT = pygame.font.Font(None, 90)
TEXT_FONT = pygame.font.Font(None, 50)
SMALL_FONT = pygame.font.Font(None, 35)
INPUT_FONT = pygame.font.Font(None, 40)

FONT_BIG = pygame.font.SysFont("Arial", 26, True)
FONT_MED = pygame.font.SysFont("Arial", 20)
FONT_SMALL = pygame.font.SysFont("Arial", 16)
FONT_DEFAULT = pygame.font.SysFont("Times New Roman", 26)

WHITE = (255,255,255)
BLACK = (0,0,0)
BLUE = (0,112,224)
HOVER = (0,90,190)
ORANGE = (255,140,0)
GREY = (210,210,210)
RED = (240,80,80)
LIGHT_BG = (250, 250, 255)
VA_BLUE = (80, 70, 230)

# ============================================================
#                         DATA
# ============================================================
stations = ["Padalarang", "Cimahi", "Bandung", "Kiaracondong", "Rancaekek"]
times = ["05.00 - 07.30", "07.30 - 10.00", "10.00 - 12.30",
         "12.30 - 15.00", "15.00 - 17.30"]

# Fake login fallback (if no DB)
REAL_EMAIL = "user@gmail.com"
REAL_PASS = "12345"

# ============================================================
#                         UI CLASSES
# ============================================================
class Button:
    def __init__(self, text, x, y, w, h, color=BLUE, txt_font=TEXT_FONT):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.default = color
        self.color = color
        self.txt_font = txt_font

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, self.rect, border_radius=12)
        if self.text:
            txt = self.txt_font.render(self.text, True, WHITE)
            surf.blit(txt, txt.get_rect(center=self.rect.center))

    def hover(self, mouse):
        self.color = HOVER if self.rect.collidepoint(mouse) else self.default
        return self.rect.collidepoint(mouse)

class InputBox:
    def __init__(self, x, y, w, h, password=False, font=INPUT_FONT):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.active = False
        self.password = password
        self.font = font

    def event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                pass
            else:
                # Limit length a bit
                if len(self.text) < 80:
                    self.text += event.unicode

    def draw(self, surf):
        pygame.draw.rect(surf, WHITE, self.rect, border_radius=8)
        pygame.draw.rect(surf, BLACK, self.rect, 2, border_radius=8)
        display_text = "*" * len(self.text) if self.password else self.text
        txt = self.font.render(display_text, True, BLACK)
        surf.blit(txt, (self.rect.x + 10, self.rect.y + (self.rect.h - txt.get_height()) // 2))

class Dropdown:
    def __init__(self, x, y, w, h, options, font=INPUT_FONT, placeholder="Pilih..."):
        self.rect = pygame.Rect(x, y, w, h)
        self.options = options
        self.selected = ""
        self.open = False
        self.font = font
        self.placeholder = placeholder

    def draw(self, surf):
        pygame.draw.rect(surf, WHITE, self.rect, border_radius=8)
        pygame.draw.rect(surf, BLACK, self.rect, 2, border_radius=8)
        txt = self.font.render(self.selected if self.selected else self.placeholder, True, BLACK)
        surf.blit(txt, (self.rect.x + 10, self.rect.y + (self.rect.h - txt.get_height()) // 2))
        # Arrow
        pygame.draw.polygon(surf, BLACK, [
            (self.rect.right - 25, self.rect.y + 20),
            (self.rect.right - 10, self.rect.y + 20),
            (self.rect.right - 17, self.rect.y + 30)
        ])
        if self.open:
            for i, option in enumerate(self.options):
                r = pygame.Rect(self.rect.x, self.rect.y + (i+1)*self.rect.height, self.rect.width, self.rect.height)
                pygame.draw.rect(surf, WHITE, r)
                pygame.draw.rect(surf, BLACK, r, 2)
                t = self.font.render(option, True, BLACK)
                surf.blit(t, (r.x + 10, r.y + (r.h - t.get_height()) // 2))

    def event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.open = not self.open
            else:
                if self.open:
                    for i, option in enumerate(self.options):
                        r = pygame.Rect(self.rect.x, self.rect.y + (i+1)*self.rect.height, self.rect.width, self.rect.height)
                        if r.collidepoint(event.pos):
                            self.selected = option
                    self.open = False

class BackButton:
    def __init__(self, x, y, w=40, h=40, color=GREY):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, self.rect, border_radius=6)
        pygame.draw.polygon(surf, BLACK, [
            (self.rect.x + 10, self.rect.y + self.rect.h//2),
            (self.rect.x + self.rect.w - 10, self.rect.y + 10),
            (self.rect.x + self.rect.w - 10, self.rect.y + self.rect.h - 10)
        ])

    def hover(self, mouse):
        return self.rect.collidepoint(mouse)

# ============================================================
#                   SHARED UI HELPERS
# ============================================================
def draw_text_center(surf, text, y, font=FONT_DEFAULT, color=BLACK):
    label = font.render(text, True, color)
    x = (WIDTH - label.get_width()) // 2
    surf.blit(label, (x, y))

def draw_button_center(surf, y, color, text, radius=12):
    rect = pygame.Rect(0, y, 360, 55)
    rect.centerx = WIDTH // 2
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    pygame.draw.rect(surf, (0, 0, 0), rect, border_radius=radius, width=2)
    label = FONT_DEFAULT.render(text, True, (0, 0, 0))
    label_x = rect.centerx - label.get_width() // 2
    label_y = rect.y + (55 - label.get_height()) // 2
    surf.blit(label, (label_x, label_y))
    return rect

# ============================================================
#                       PAGES / STATES
# ============================================================
page = "menu"
prev_page = "menu"

# Login / register inputs
email_box = InputBox(WIDTH//2 - 150, 180, 300, 50)
pass_box = InputBox(WIDTH//2 - 150, 260, 300, 50, password=True)

nama_box = InputBox(WIDTH//2 - 150, 160, 300, 50)
nik_box = InputBox(WIDTH//2 - 150, 230, 300, 50)
hp_box = InputBox(WIDTH//2 - 150, 300, 300, 50)
gender_dropdown = Dropdown(WIDTH//2 - 150, 340, 300, 50, ["Laki-laki", "Perempuan"], placeholder="Pilih Gender...")

reg_email = InputBox(WIDTH//2 - 150, 200, 300, 50)
reg_pass = InputBox(WIDTH//2 - 150, 270, 300, 50, password=True)

# Buttons
masuk_btn = Button("MASUK", WIDTH//2 - 120, 260, 240, 70)
login_next = Button("LOGIN", WIDTH//2 - 120, 240, 240, 60, ORANGE)
login_submit = Button("LOGIN!", WIDTH//2 - 120, 340, 240, 60, BLUE)
regis_btn = Button("REGISTRASI", WIDTH//2 - 120, 350, 240, 60, BLUE)
next_reg_btn = Button("NEXT", WIDTH//2 - 120, 420, 240, 60, ORANGE)
finish_btn = Button("SELESAI", WIDTH//2 - 120, 350, 240, 60, ORANGE)
menu_pesan_btn = Button("PESAN TIKET", WIDTH//2 - 150, 230, 300, 70, ORANGE)
menu_keluar_btn = Button("KELUAR", WIDTH//2 - 150, 320, 300, 70, BLUE)
popup_x_btn = Button("X", 600, 130, 40, 40, RED, txt_font=SMALL_FONT)
back_btn = BackButton(20, 20)

# Ticket flow variables
start_selected = None
end_selected = None
time_selected = None

# For layer-like UI (station/time selection lists)
start_buttons = []
end_buttons = []
time_buttons = []

# Payment / popup
error_popup = False
error_message = ""
shake_offset = 0
shake_timer = 0

popup = False
popup_regis = False

# Payment button (created when drawing payment screen)
pay_btn = None

# ============================================================
#                  DRAWING SCREENS (PAGE HANDLERS)
# ============================================================
def draw_menu():
    screen.fill(WHITE)
    title = TITLE_FONT.render("KAI ACCESS", True, BLACK)
    screen.blit(title, title.get_rect(center=(WIDTH//2, 150)))
    masuk_btn.hover(mouse)
    masuk_btn.draw(screen)

def draw_login_menu():
    screen.fill(WHITE)
    t = TEXT_FONT.render("Silakan login ke akun Anda", True, BLACK)
    screen.blit(t, (WIDTH//2 - t.get_width()//2, 120))
    s = SMALL_FONT.render("Jika belum silakan registrasi", True, BLACK)
    screen.blit(s, (WIDTH//2 - s.get_width()//2, 315))
    login_next.hover(mouse)
    login_next.draw(screen)
    regis_btn.hover(mouse)
    regis_btn.draw(screen)
    back_btn.draw(screen)

def draw_login_form():
    screen.fill(WHITE)
    label1 = TEXT_FONT.render("Login Akun", True, BLACK)
    screen.blit(label1, (WIDTH//2 - label1.get_width()//2, 100))
    screen.blit(SMALL_FONT.render("Email:", True, BLACK), (email_box.rect.x, 150))
    screen.blit(SMALL_FONT.render("Password:", True, BLACK), (pass_box.rect.x, 230))
    email_box.draw(screen)
    pass_box.draw(screen)
    login_submit.hover(mouse)
    login_submit.draw(screen)
    back_btn.draw(screen)

def draw_register1():
    screen.fill(WHITE)
    title1 = SMALL_FONT.render("Silakan lengkapi data berikut untuk membuat akun.", True, BLACK)
    screen.blit(title1, (WIDTH//2 - title1.get_width()//2, 70))
    subtitle = SMALL_FONT.render("Bagian 1 dari 2", True, BLACK)
    screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 100))
    screen.blit(SMALL_FONT.render("Nama:", True, BLACK), (nama_box.rect.x, 135))
    screen.blit(SMALL_FONT.render("NIK:", True, BLACK), (nik_box.rect.x, 205))
    screen.blit(SMALL_FONT.render("Nomor Handphone:", True, BLACK), (hp_box.rect.x, 275))
    screen.blit(SMALL_FONT.render("Gender:", True, BLACK), (gender_dropdown.rect.x, 315))
    nama_box.draw(screen)
    nik_box.draw(screen)
    hp_box.draw(screen)
    gender_dropdown.draw(screen)
    next_reg_btn.hover(mouse)
    next_reg_btn.draw(screen)
    back_btn.draw(screen)

def draw_register2():
    screen.fill(WHITE)
    title2 = SMALL_FONT.render("Bagian 2 dari 2", True, BLACK)
    screen.blit(title2, (WIDTH//2 - title2.get_width()//2, 70))
    screen.blit(SMALL_FONT.render("Email:", True, BLACK), (reg_email.rect.x, 170))
    screen.blit(SMALL_FONT.render("Password:", True, BLACK), (reg_pass.rect.x, 240))
    reg_email.draw(screen)
    reg_pass.draw(screen)
    finish_btn.hover(mouse)
    finish_btn.draw(screen)
    back_btn.draw(screen)

def draw_main_menu():
    screen.fill(WHITE)
    title = TEXT_FONT.render("MENU UTAMA", True, BLACK)
    screen.blit(title, title.get_rect(center=(WIDTH//2, 120)))
    menu_pesan_btn.hover(mouse)
    menu_pesan_btn.draw(screen)
    menu_keluar_btn.hover(mouse)
    menu_keluar_btn.draw(screen)

def draw_pesan_tiket():
    screen.fill(WHITE)
    title = TEXT_FONT.render("PILIHAN PEMESANAN TIKET", True, BLACK)
    screen.blit(title, title.get_rect(center=(WIDTH//2, 120)))

    info = SMALL_FONT.render("Pilih Stasiun Awal untuk memulai pemesanan.", True, BLACK)
    screen.blit(info, info.get_rect(center=(WIDTH//2, 180)))

    # Button to go to start station selection
    btn = Button("Pilih Stasiun Awal", WIDTH//2 - 160, 240, 320, 60, ORANGE)
    btn.hover(mouse)
    btn.draw(screen)
    back_btn.draw(screen)
    return btn

def draw_stations_start(offset=0):
    screen.fill(LIGHT_BG)
    draw_text_center(screen, "STASIUN AWAL", 24 + offset, font=FONT_DEFAULT)
    y = 100 + offset
    rects = []
    for st in stations:
        rect = draw_button_center(screen, y, (170, 185, 255), st)
        rects.append((rect, st))
        y += 70
    return rects

def draw_stations_end():
    screen.fill(WHITE)
    draw_text_center(screen, "STASIUN TUJUAN", 24, font=FONT_DEFAULT)
    y = 100
    rects = []
    for st in stations:
        rect = draw_button_center(screen, y, (255, 190, 120), st)
        rects.append((rect, st))
        y += 70
    if start_selected:
        draw_text_center(screen, f"Stasiun awal: {start_selected}", 560, font=FONT_DEFAULT)
    return rects

def draw_times():
    screen.fill(WHITE)
    draw_text_center(screen, "JAM KEBERANGKATAN", 24, font=FONT_DEFAULT)
    y = 120
    rects = []
    for t in times:
        rect = draw_button_center(screen, y, (255, 150, 150), t)
        rects.append((rect, t))
        y += 70
    if start_selected:
        draw_text_center(screen, f"Awal: {start_selected}", 560, font=FONT_DEFAULT)
    if end_selected:
        draw_text_center(screen, f"Tujuan: {end_selected}", 600, font=FONT_DEFAULT)
    return rects

def draw_payment_screen():
    screen.fill(WHITE)
    screen.blit(FONT_BIG.render("Pembayaran", True, BLACK), (20, 20))
    screen.blit(FONT_MED.render("Metode Pembayaran:", True, BLACK), (20, 110))
    pygame.draw.rect(screen, GREY, (20,150,760,40), border_radius=10)
    screen.blit(FONT_SMALL.render("Bank Transfer (Virtual Account)", True, BLACK), (30, 162))
    screen.blit(FONT_MED.render("Virtual Account:", True, BLACK), (20, 240))
    screen.blit(FONT_BIG.render("123 456 7890", True, VA_BLUE), (20, 280))
    # Pay button
    pay = Button("Bayar Sekarang", 20, 520, 760, 60, VA_BLUE, txt_font=FONT_MED)
    pay.draw(screen)
    return pay

def draw_ticket_screen():
    screen.fill(WHITE)
    screen.blit(FONT_BIG.render("🎟 Tiket KRL Anda", True, BLACK), (110, 40))
    screen.blit(FONT_MED.render(f"Stasiun Awal   : {start_selected}", True, BLACK), (50,140))
    screen.blit(FONT_MED.render(f"Stasiun Tujuan : {end_selected}", True, BLACK), (50,180))
    screen.blit(FONT_MED.render(f"Jam Berangkat  : {time_selected}", True, BLACK), (50,220))
    screen.blit(FONT_SMALL.render("Pembayaran Berhasil ✔", True, VA_BLUE), (130, 300))
    screen.blit(FONT_SMALL.render("Tunjukkan tiket ini saat masuk stasiun.", True, BLACK), (80, 330))
    btn = Button("Selesai", WIDTH//2 - 120, 420, 240, 60, ORANGE)
    btn.draw(screen)
    return btn

# ============================================================
#                       ERROR POPUP + SHAKE
# ============================================================
def draw_error_popup():
    # background blur mask
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(120)
    overlay.fill((0,0,0))
    screen.blit(overlay, (0,0))

    popup_w, popup_h = 360, 200
    popup_x = (WIDTH - popup_w) // 2
    popup_y = (HEIGHT - popup_h) // 2

    # dialog box
    pygame.draw.rect(screen, (255,255,255), (popup_x, popup_y, popup_w, popup_h), border_radius=12)
    pygame.draw.rect(screen, (255,0,0), (popup_x, popup_y, popup_w, popup_h), width=4, border_radius=12)

    label = FONT_MED.render("Terjadi Kesalahan!", True, (200,0,0))
    screen.blit(label, (popup_x + popup_w//2 - label.get_width()//2, popup_y + 20))

    msg = FONT_SMALL.render(error_message, True, (0,0,0))
    screen.blit(msg, (popup_x + popup_w//2 - msg.get_width()//2, popup_y + 80))

    ok_btn = Button("OK", popup_x + 110, popup_y + 135, 140, 40, (200,0,0), txt_font=FONT_MED)
    ok_btn.draw(screen)
    return ok_btn

# ============================================================
#                          MAIN LOOP
# ============================================================
running = True
while running:
    CLOCK.tick(FPS)
    mx, my = pygame.mouse.get_pos()
    mouse = (mx, my)

    # SHAKE offset
    offset = shake_offset if shake_timer > 0 else 0

    # --- draw current page
    current_clickable = None  # store a returned button/rect for click handling
    if page == "menu":
        draw_menu()
    elif page == "login_menu":
        draw_login_menu()
    elif page == "login_form":
        draw_login_form()
    elif page == "register1":
        draw_register1()
    elif page == "register2":
        draw_register2()
    elif page == "main_menu":
        draw_main_menu()
    elif page == "pesan_tiket":
        btn = draw_pesan_tiket()
        current_clickable = btn
    elif page == "p_stasiun_awal":
        start_buttons = draw_stations_start(offset=offset)
    elif page == "p_stasiun_tujuan":
        end_buttons = draw_stations_end()
    elif page == "p_jam":
        time_buttons = draw_times()
    elif page == "p_pembayaran":
        pay_btn = draw_payment_screen()
    elif page == "p_tiket":
        done_btn = draw_ticket_screen()
        current_clickable = done_btn

    # Show popups if set
    if popup:
        # login failed popup
        pygame.draw.rect(screen, WHITE, (150, 120, 500, 260), border_radius=12)
        pygame.draw.rect(screen, RED, (150, 120, 500, 260), 4, border_radius=12)
        lines = [
            "Login Gagal.",
            "Silakan login kembali.",
            "Jika belum memiliki akun,",
            "silakan registrasi akun."
        ]
        y = 150
        for line in lines:
            txt = SMALL_FONT.render(line, True, BLACK)
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, y))
            y += 40
        popup_x_btn.draw(screen)

    if popup_regis:
        pygame.draw.rect(screen, WHITE, (150, 120, 500, 260), border_radius=12)
        pygame.draw.rect(screen, BLUE, (150, 120, 500, 260), 4, border_radius=12)
        lines = [
            "Registrasi Berhasil!",
            "Silakan login / masuk ke akun Anda."
        ]
        y = 180
        for line in lines:
            txt = SMALL_FONT.render(line, True, BLACK)
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, y))
            y += 50
        popup_x_btn.draw(screen)

    if error_popup:
        ok_btn = draw_error_popup()

    # EVENT HANDLING
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

        # If popup (generic) open, handle only popup events
        if popup:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if popup_x_btn.hover(mouse):
                    popup = False
            if event.type == pygame.QUIT:
                running = False
            continue

        if popup_regis:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if popup_x_btn.hover(mouse):
                    popup_regis = False
                    page = "login_menu"
            continue

        if error_popup:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if ok_btn and ok_btn.rect.collidepoint(event.pos):
                    error_popup = False
            continue

        # Normal events per page
        # -- Inputs need to receive key events as well
        if page in ("login_form",):
            email_box.event(event)
            pass_box.event(event)
        if page == "register1":
            nama_box.event(event)
            nik_box.event(event)
            hp_box.event(event)
            gender_dropdown.event(event)
        if page == "register2":
            reg_email.event(event)
            reg_pass.event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            # BUTTONS on most pages
            if page == "menu":
                if masuk_btn.hover(mouse):
                    page = "login_menu"
                    prev_page = "menu"

            elif page == "login_menu":
                if login_next.hover(mouse):
                    page = "login_form"
                    prev_page = "login_menu"
                if regis_btn.hover(mouse):
                    page = "register1"
                    prev_page = "login_menu"
                if back_btn.hover(mouse):
                    page = prev_page

            elif page == "login_form":
                if login_submit.hover(mouse):
                    # Try DB login if available, else fake match
                    if USE_DATABASE:
                        ok = databases.login_user(email_box.text, pass_box.text)
                    else:
                        ok = (email_box.text == REAL_EMAIL and pass_box.text == REAL_PASS)
                    if ok:
                        page = "main_menu"
                    else:
                        popup = True
                if back_btn.hover(mouse):
                    page = prev_page

            elif page == "register1":
                if next_reg_btn.hover(mouse):
                    if nama_box.text and nik_box.text and hp_box.text and gender_dropdown.selected:
                        if USE_DATABASE:
                            databases.add_user(nama_box.text, hp_box.text, nik_box.text, gender_dropdown.selected)
                        page = "register2"
                        prev_page = "register1"
                if back_btn.hover(mouse):
                    page = prev_page

            elif page == "register2":
                if finish_btn.hover(mouse):
                    # register user
                    if USE_DATABASE:
                        databases.register_user(reg_email.text, reg_pass.text)
                    popup_regis = True
                if back_btn.hover(mouse):
                    page = prev_page

            elif page == "main_menu":
                if menu_pesan_btn.hover(mouse):
                    page = "pesan_tiket"
                    prev_page = "main_menu"
                if menu_keluar_btn.hover(mouse):
                    page = "menu"

            elif page == "pesan_tiket":
                if current_clickable and current_clickable.rect.collidepoint(event.pos):
                    page = "p_stasiun_awal"
                    prev_page = "pesan_tiket"

            elif page == "p_stasiun_awal":
                # station buttons (list of rects)
                for rect, st in start_buttons:
                    if rect.collidepoint(event.pos):
                        start_selected = st
                        # continue flow to choose destination
                        page = "p_stasiun_tujuan"
                        prev_page = "p_stasiun_awal"
                        break

            elif page == "p_stasiun_tujuan":
                for rect, st in end_buttons:
                    if rect.collidepoint(event.pos):
                        if st == start_selected:
                            # trigger error popup + shake
                            error_popup = True
                            error_message = "Stasiun awal dan tujuan tidak boleh sama!"
                            shake_timer = 20
                        else:
                            end_selected = st
                            page = "p_jam"
                            prev_page = "p_stasiun_tujuan"
                        break

            elif page == "p_jam":
                for rect, t in time_buttons:
                    if rect.collidepoint(event.pos):
                        time_selected = t
                        page = "p_pembayaran"
                        prev_page = "p_jam"
                        break

            elif page == "p_pembayaran":
                if pay_btn and pay_btn.rect.collidepoint(event.pos):
                    # In a real app: trigger payment logic. Here: go to ticket
                    page = "p_tiket"
                    prev_page = "p_pembayaran"

            elif page == "p_tiket":
                if current_clickable and current_clickable.rect.collidepoint(event.pos):
                    # reset selections and back to main menu
                    start_selected = None
                    end_selected = None
                    time_selected = None
                    page = "main_menu"

        # Provide dropdown toggles for click handling separate
        if event.type == pygame.MOUSEBUTTONDOWN:
            # dropdown on register1 already handled in gender_dropdown.event
            pass

    # SHAKE update
    if 'shake_timer' in globals() and shake_timer > 0:
        shake_offset = random.randint(-6, 6)
        shake_timer -= 1
    else:
        shake_offset = 0

    pygame.display.update()

pygame.quit()
sys.exit()
