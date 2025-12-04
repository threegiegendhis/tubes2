import pygame, sys
pygame.init()

# Window
WIDTH, HEIGHT = 800, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("KAI Access")

# Colors
WHITE = (255,255,255)
BLACK = (0,0,0)
BLUE = (0,112,224)
HOVER = (0,90,190)
ORANGE = (255,140,0)
GREY = (210,210,210)
RED = (240,80,80)

# Fonts
title_font = pygame.font.Font(None, 90)
text_font = pygame.font.Font(None, 50)
small_font = pygame.font.Font(None, 35)
input_font = pygame.font.Font(None, 40)

# Button class
class Button:
    def __init__(self, text, x, y, w, h, color=BLUE):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.default = color
        self.color = color

    def draw(self, win):
        pygame.draw.rect(win, self.color, self.rect, border_radius=12)
        if self.text:
            txt = text_font.render(self.text, True, WHITE)
            win.blit(txt, txt.get_rect(center=self.rect.center))

    def hover(self, mouse):
        self.color = HOVER if self.rect.collidepoint(mouse) else self.default
        return self.rect.collidepoint(mouse)

# InputBox class
class InputBox:
    def __init__(self, x, y, w, h, password=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.active = False
        self.password = password

    def event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                pass
            else:
                self.text += event.unicode

    def draw(self, win):
        pygame.draw.rect(win, WHITE, self.rect, border_radius=8)
        pygame.draw.rect(win, BLACK, self.rect, 2, border_radius=8)
        display_text = "*" * len(self.text) if self.password else self.text
        txt = input_font.render(display_text, True, BLACK)
        win.blit(txt, (self.rect.x + 10, self.rect.y + 10))

# Dropdown class
class Dropdown:
    def __init__(self, x, y, w, h, options):
        self.rect = pygame.Rect(x, y, w, h)
        self.options = options
        self.selected = ""
        self.open = False

    def draw(self, win):
        pygame.draw.rect(win, WHITE, self.rect, border_radius=8)
        pygame.draw.rect(win, BLACK, self.rect, 2, border_radius=8)
        txt = input_font.render(self.selected if self.selected else "Pilih Gender...", True, BLACK)
        win.blit(txt, (self.rect.x + 10, self.rect.y + 10))
        # Arrow
        pygame.draw.polygon(win, BLACK, [
            (self.rect.right - 25, self.rect.y + 20),
            (self.rect.right - 10, self.rect.y + 20),
            (self.rect.right - 17, self.rect.y + 30)
        ])
        if self.open:
            for i, option in enumerate(self.options):
                r = pygame.Rect(self.rect.x, self.rect.y + (i+1)*self.rect.height, self.rect.width, self.rect.height)
                pygame.draw.rect(win, WHITE, r)
                pygame.draw.rect(win, BLACK, r, 2)
                t = input_font.render(option, True, BLACK)
                win.blit(t, (r.x + 10, r.y + 10))

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

# Back button tanpa teks (panah kiri)
class BackButton:
    def __init__(self, x, y, w=40, h=40, color=GREY):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color

    def draw(self, win):
        pygame.draw.rect(win, self.color, self.rect, border_radius=6)
        pygame.draw.polygon(win, BLACK, [
            (self.rect.x + 10, self.rect.y + self.rect.h//2),
            (self.rect.x + self.rect.w - 10, self.rect.y + 10),
            (self.rect.x + self.rect.w - 10, self.rect.y + self.rect.h - 10)
        ])

    def hover(self, mouse):
        return self.rect.collidepoint(mouse)

# Fake login
REAL_EMAIL = "user@gmail.com"
REAL_PASS = "12345"

# Buttons
masuk_btn = Button("MASUK", WIDTH//2 - 120, 260, 240, 70)
login_next = Button("LOGIN", WIDTH//2 - 120, 240, 240, 60, ORANGE)
login_submit = Button("LOGIN!", WIDTH//2 - 120, 340, 240, 60, BLUE)
regis_btn = Button("REGISTRASI", WIDTH//2 - 120, 350, 240, 60, BLUE)
next_reg_btn = Button("NEXT", WIDTH//2 - 120, 420, 240, 60, ORANGE)
finish_btn = Button("SELESAI", WIDTH//2 - 120, 350, 240, 60, ORANGE)
menu_pesan_btn = Button("PESAN TIKET", WIDTH//2 - 150, 230, 300, 70, ORANGE)
menu_keluar_btn = Button("KELUAR", WIDTH//2 - 150, 320, 300, 70, BLUE)
popup_x_btn = Button("X", 600, 130, 40, 40, RED)
back_btn = BackButton(20, 20)

# Input boxes
email_box = InputBox(WIDTH//2 - 150, 180, 300, 50)
pass_box = InputBox(WIDTH//2 - 150, 260, 300, 50, password=True)

# Register page 1
nama_box = InputBox(WIDTH//2 - 150, 160, 300, 50)
nik_box = InputBox(WIDTH//2 - 150, 230, 300, 50)
hp_box = InputBox(WIDTH//2 - 150, 300, 300, 50)
gender_dropdown = Dropdown(WIDTH//2 - 150, 340, 300, 50, ["Laki-laki", "Perempuan"])

# Register page 2
reg_email = InputBox(WIDTH//2 - 150, 200, 300, 50)
reg_pass = InputBox(WIDTH//2 - 150, 270, 300, 50, password=True)

# Page state
page = "menu"
popup = False
popup_regis = False
prev_page = "menu"  # untuk tombol back

# MAIN LOOP
while True:
    WIN.fill(WHITE)
    mouse = pygame.mouse.get_pos()

    # POPUP LOGIN GAGAL
    if popup:
        pygame.draw.rect(WIN, WHITE, (150, 120, 500, 260), border_radius=12)
        pygame.draw.rect(WIN, RED, (150, 120, 500, 260), 4, border_radius=12)
        lines = [
            "Login Gagal.",
            "Silakan login kembali.",
            "Jika belum memiliki akun,",
            "silakan registrasi akun."
        ]
        y = 150
        for line in lines:
            txt = small_font.render(line, True, BLACK)
            WIN.blit(txt, (WIDTH//2 - txt.get_width()//2, y))
            y += 40
        popup_x_btn.draw(WIN)
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if popup_x_btn.hover(mouse):
                    popup = False
        continue

    # POPUP REGISTRASI BERHASIL
    if popup_regis:
        pygame.draw.rect(WIN, WHITE, (150, 120, 500, 260), border_radius=12)
        pygame.draw.rect(WIN, BLUE, (150, 120, 500, 260), 4, border_radius=12)
        lines = [
            "Registrasi Berhasil!",
            "Silakan login / masuk ke akun Anda."
        ]
        y = 180
        for line in lines:
            txt = small_font.render(line, True, BLACK)
            WIN.blit(txt, (WIDTH//2 - txt.get_width()//2, y))
            y += 50
        popup_x_btn.draw(WIN)
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if popup_x_btn.hover(mouse):
                    popup_regis = False
                    page = "login_menu"
        continue

    # MENU PAGE
    if page == "menu":
        title = title_font.render("KAI ACCESS", True, BLACK)
        WIN.blit(title, title.get_rect(center=(WIDTH//2, 150)))
        masuk_btn.hover(mouse)
        masuk_btn.draw(WIN)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if masuk_btn.hover(mouse):
                    page = "login_menu"
                    prev_page = "menu"

    # LOGIN MENU
    elif page == "login_menu":
        t = text_font.render("Silakan login ke akun Anda", True, BLACK)
        WIN.blit(t, (WIDTH//2 - t.get_width()//2, 120))
        s = small_font.render("Jika belum silakan registrasi", True, BLACK)
        WIN.blit(s, (WIDTH//2 - s.get_width()//2, 315))
        login_next.hover(mouse)
        login_next.draw(WIN)
        regis_btn.hover(mouse)
        regis_btn.draw(WIN)
        back_btn.draw(WIN)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if login_next.hover(mouse):
                    page = "login_form"
                    prev_page = "login_menu"
                if regis_btn.hover(mouse):
                    page = "register1"
                    prev_page = "login_menu"
                if back_btn.hover(mouse):
                    page = prev_page

    # LOGIN FORM
    elif page == "login_form":
        label1 = text_font.render("Login Akun", True, BLACK)
        WIN.blit(label1, (WIDTH//2 - label1.get_width()//2, 100))
        WIN.blit(small_font.render("Email:", True, BLACK), (email_box.rect.x, 150))
        WIN.blit(small_font.render("Password:", True, BLACK), (pass_box.rect.x, 230))
        email_box.draw(WIN)
        pass_box.draw(WIN)
        login_submit.hover(mouse)
        login_submit.draw(WIN)
        back_btn.draw(WIN)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            email_box.event(e)
            pass_box.event(e)
            if e.type == pygame.MOUSEBUTTONDOWN:
                if login_submit.hover(mouse):
                    if email_box.text == REAL_EMAIL and pass_box.text == REAL_PASS:
                        page = "main_menu"
                    else:
                        popup = True
                if back_btn.hover(mouse):
                    page = prev_page

    # REGISTER PAGE 1
    elif page == "register1":
        title1 = small_font.render("Silakan lengkapi data berikut untuk membuat akun.", True, BLACK)
        WIN.blit(title1, (WIDTH//2 - title1.get_width()//2, 70))
        subtitle = small_font.render("Bagian 1 dari 2", True, BLACK)
        WIN.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 100))
        WIN.blit(small_font.render("Nama:", True, BLACK), (nama_box.rect.x, 135))
        WIN.blit(small_font.render("NIK:", True, BLACK), (nik_box.rect.x, 205))
        WIN.blit(small_font.render("Nomor Handphone:", True, BLACK), (hp_box.rect.x, 275))
        WIN.blit(small_font.render("Gender:", True, BLACK), (gender_dropdown.rect.x, 315))
        nama_box.draw(WIN)
        nik_box.draw(WIN)
        hp_box.draw(WIN)
        gender_dropdown.draw(WIN)
        next_reg_btn.hover(mouse)
        next_reg_btn.draw(WIN)
        back_btn.draw(WIN)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            nama_box.event(e)
            nik_box.event(e)
            hp_box.event(e)
            gender_dropdown.event(e)
            if e.type == pygame.MOUSEBUTTONDOWN:
                if next_reg_btn.hover(mouse):
                    if nama_box.text and nik_box.text and hp_box.text and gender_dropdown.selected:
                        page = "register2"
                        prev_page = "register1"
                if back_btn.hover(mouse):
                    page = prev_page

    # REGISTER PAGE 2
    elif page == "register2":
        title2 = small_font.render("Bagian 2 dari 2", True, BLACK)
        WIN.blit(title2, (WIDTH//2 - title2.get_width()//2, 70))
        WIN.blit(small_font.render("Email:", True, BLACK), (reg_email.rect.x, 170))
        WIN.blit(small_font.render("Password:", True, BLACK), (reg_pass.rect.x, 240))
        reg_email.draw(WIN)
        reg_pass.draw(WIN)
        finish_btn.hover(mouse)
        finish_btn.draw(WIN)
        back_btn.draw(WIN)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            reg_email.event(e)
            reg_pass.event(e)
            if e.type == pygame.MOUSEBUTTONDOWN:
                if finish_btn.hover(mouse):
                    popup_regis = True
                if back_btn.hover(mouse):
                    page = prev_page

    # MAIN MENU AFTER LOGIN
    elif page == "main_menu":
        title = text_font.render("MENU UTAMA", True, BLACK)
        WIN.blit(title, title.get_rect(center=(WIDTH//2, 120)))
        menu_pesan_btn.hover(mouse)
        menu_pesan_btn.draw(WIN)
        menu_keluar_btn.hover(mouse)
        menu_keluar_btn.draw(WIN)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if menu_pesan_btn.hover(mouse):
                    page = "pesan_tiket"
                    prev_page = "main_menu"
                if menu_keluar_btn.hover(mouse):
                    page = "menu"

    # PESAN TIKET PAGE
    elif page == "pesan_tiket":
        title = text_font.render("MENU PESAN TIKET", True, BLACK)
        WIN.blit(title, title.get_rect(center=(WIDTH//2, 120)))
        info = small_font.render("Halaman ini masih kosong.", True, BLACK)
        WIN.blit(info, info.get_rect(center=(WIDTH//2, 220)))
        back_btn.draw(WIN)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.hover(mouse):
                    page = prev_page

    pygame.display.update()
