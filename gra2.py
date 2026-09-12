import sys
import pygame
import random

# 1. Start gry i okno
pygame.init()
pygame.mixer.init()  # Inicjalizacja miksera dźwięków
ekran = pygame.display.set_mode((800, 600), pygame.DOUBLEBUF | pygame.HWSURFACE, vsync=1)

# Gracz (zmiana z Nicola.png na julka.png)
grafika_sprita = pygame.image.load("julka.png").convert_alpha()
grafika_lewo = pygame.transform.flip(grafika_sprita, True, False)
aktualna_grafika = grafika_sprita

# Przeciwnik (Pająk)
grafika_pajaka = pygame.image.load("spider.png").convert_alpha()

# Tworzenie maski dla pająka (tylko widoczne piksele)
maska_pajaka = pygame.mask.from_surface(grafika_pajaka)

# Inicjalizacja czcionki do wyświetlania napisu o kolizji
czcionka = pygame.font.SysFont("Arial", 60, bold=True)

# --- ŁADOWANIE DŹWIĘKÓW (zabezpieczone przed brakiem plików) ---
dzwiek_skoku = None
dzwiek_kolizji = None

try:
    dzwiek_skoku = pygame.mixer.Sound("skok.wav")
except pygame.error:
    print("Ostrzeżenie: Nie znaleziono pliku skok.wav. Gra uruchomi się bez dźwięku skoku.")

try:
    dzwiek_kolizji = pygame.mixer.Sound("kolizja.wav")
except pygame.error:
    print("Ostrzeżenie: Nie znaleziono pliku kolizja.wav. Gra uruchomi się bez dźwięku kolizji.")

# 2. Pozycja i prędkość naszego kwadratu
x = 400
y = 300
predkosc = 5
zegar = pygame.time.Clock()

# Pozycja i ruch pająka (losowy kierunek i prędkość)
pajak_x = random.randint(100, 700)
pajak_y = random.randint(100, 400)
pajak_dx = random.choice([-4, -3, 3, 4])
pajak_dy = random.choice([-4, -3, 3, 4])

# Zmienne do skakania
grawitacja = 0.8
predkosc_y = 0
czy_skacze = False
podloga_y = 450  # Wysokość na której zatrzymuje się postać

# Zmienna określająca czy w danym momencie trwa kolizja
jest_kolizja = False

# 3. Główna pętla gry
while True:
    # Wyłączenie gry krzyżykiem
    for zdarzenie in pygame.event.get():
        if zdarzenie.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 4. Sterowanie strzałkami
    klawisze = pygame.key.get_pressed()
    if klawisze[pygame.K_LEFT]:
        x -= predkosc
        aktualna_grafika = grafika_lewo
    if klawisze[pygame.K_RIGHT]:
        x += predkosc
        aktualna_grafika = grafika_sprita
    
    # Skok (strzałka w górę lub spacja)
    if (klawisze[pygame.K_UP] or klawisze[pygame.K_SPACE]) and not czy_skacze:
        predkosc_y = -14
        czy_skacze = True
        if dzwiek_skoku:
            dzwiek_skoku.play()

    # Zastosowanie fizyki pionowej gracza
    predkosc_y += grawitacja
    y += predkosc_y

    # Kolizja gracza z ziemią
    if y >= podloga_y:
        y = podloga_y
        predkosc_y = 0
        czy_skacze = False

    # --- RUCH PAJĄKA (odbijanie od krawędzi) ---
    pajak_x += pajak_dx
    pajak_y += pajak_dy

    # Odbicie od lewej/prawej krawędzi ekranu
    if pajak_x <= 0 or pajak_x >= 800 - grafika_pajaka.get_width():
        pajak_dx *= -1
    
    # Odbicie od górnej/dolnej krawędzi ekranu
    if pajak_y <= 0 or pajak_y >= 600 - grafika_pajaka.get_height():
        pajak_dy *= -1

    # --- PRECYZYJNE WYKRYWANIE KOLIZJI (PIXEL-PERFECT) ---
    # Tworzymy maskę dla aktualnego sprita gracza (musi być tworzona na bieżąco, bo postać się obraca)
    maska_gracza = pygame.mask.from_surface(aktualna_grafika)

    # Obliczamy przesunięcie (offset) między lewym górnym rogiem gracza a pająka
    offset_x = pajak_x - x
    offset_y = pajak_y - y

    # Sprawdzamy kolizję
    kolizja_teraz = maska_gracza.overlap(maska_pajaka, (offset_x, offset_y)) is not None

    if kolizja_teraz:
        # Jeśli to pierwsza klatka zderzenia, odtwórz dźwięk
        if not jest_kolizja:
            if dzwiek_kolizji:
                dzwiek_kolizji.play()
        jest_kolizja = True
    else:
        jest_kolizja = False

    # 5. Rysowanie
    ekran.fill((226, 226, 226))  # Szary ekran
    
    # Rysowanie pająka
    ekran.blit(grafika_pajaka, (pajak_x, pajak_y))
    
    # Rysowanie gracza
    ekran.blit(aktualna_grafika, (x, y))

    # Jeśli wykryto kolizję, rysujemy czerwony napis na środku ekranu
    if jest_kolizja:
        tekst_kolizji = czcionka.render("KOLIZJA!", True, (220, 20, 60))  # Kolor szkarłatny/czerwony
        # Wyśrodkowanie tekstu w poziomie na górze ekranu
        pozycja_tekstu = (400 - tekst_kolizji.get_width() // 2, 80)
        ekran.blit(tekst_kolizji, pozycja_tekstu)

    pygame.display.flip()  # Odświeżenie ekranu
    zegar.tick(60)
