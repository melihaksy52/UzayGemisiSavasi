import pygame
import sys
import random
import os

# Pygame başlatma
pygame.init()

# Ekran ayarları
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Uzay Gemisi Oyunu")
clock = pygame.time.Clock()

# Renkler
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DARK_BLUE = (0, 0, 50)  # Koyu uzay mavisi
GOLD = (255, 223, 0)  # Altın rengi

# Ses efektleri kontrolü - DÜZELTİLMİŞ HALİ
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sound_dir = os.path.join(script_dir, "sesler")  # Sesler klasörünü belirle

    # Ses dosyalarını yükle
    shoot_sound = pygame.mixer.Sound(os.path.join(sound_dir, "ates.wav"))
    explosion_sound = pygame.mixer.Sound(os.path.join(sound_dir, "patlama.wav"))
    game_over_sound = pygame.mixer.Sound(os.path.join(sound_dir, "son.wav"))

    sound_enabled = True
except Exception as e:
    print(f"Ses dosyaları yüklenemedi! Hata: {e}")
    sound_enabled = False

# Oyun durumları
MENU, GAME, GAME_OVER = 0, 1, 2
state = MENU

# YILDIZ SİSTEMİ (3 katmanlı)
stars_far = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(0.1, 0.3), 0.2) 
             for _ in range(100)]  # x, y, boyut, hız
stars_mid = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(0.3, 0.6), 0.5) 
             for _ in range(150)]
stars_near = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(0.6, 1.0), 0.8) 
              for _ in range(100)]

# Oyna butonu
button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 30, 200, 60)
font_large = pygame.font.SysFont('Arial', 64)
font_medium = pygame.font.SysFont('Arial', 36)
font_small = pygame.font.SysFont('Arial', 24)
font_dev = pygame.font.SysFont('Arial', 16)
font_coin = pygame.font.SysFont('Arial', 28, bold=True)

# Görsel yükleme fonksiyonu
def load_image(folder, filename, size, color=None):
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, folder, filename)
        image = pygame.image.load(image_path).convert_alpha()
        return pygame.transform.scale(image, size)
    except Exception as e:
        print(f"Görsel yüklenemedi: {folder}/{filename} - {e}")
        surface = pygame.Surface(size, pygame.SRCALPHA)
        if "dushman" in filename.lower():
            pygame.draw.polygon(surface, RED, [(size[0]//2, 0), (0, size[1]), (size[0], size[1])])
        else:
            pygame.draw.polygon(surface, GREEN, [(size[0]//2, 0), (0, size[1]), (size[0], size[1])])
        return surface

# Oyuncu sınıfı
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image('karakter', 'uzaygemisi.png', (80, 80))
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT-50))
        self.speed = 8
        self.health = 3
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.moving_left = False
        self.moving_right = False
        self.moving_up = False
        self.moving_down = False

    def update(self):
        if self.moving_left and self.rect.left > 0:
            self.rect.x -= self.speed
        if self.moving_right and self.rect.right < WIDTH:
            self.rect.x += self.speed
        if self.moving_up and self.rect.top > 0:
            self.rect.y -= self.speed
        if self.moving_down and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if sound_enabled:
                shoot_sound.play()
            bullet = Bullet(self.rect.centerx, self.rect.top)
            return bullet
        return None

# Mermi sınıfı (Animasyonlu)
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 20))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -10
        self.animation_frame = 0

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

# Düşman sınıfı
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image('karakter', 'dushman_gemisi.png', (60, 60))
        self.rect = self.image.get_rect(midtop=(random.randint(30, WIDTH-30), -50))
        self.speed = random.randint(2, 5)
        self.health = 1

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

# Patlama efekti (Pixel tarzı)
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size=50):
        super().__init__()
        self.size = size
        self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center)
        self.frame = 0
        self.max_frames = 5
        if sound_enabled:
            explosion_sound.play()

    def update(self):
        self.frame += 1
        if self.frame >= self.max_frames:
            self.kill()
        else:
            self.image.fill((0, 0, 0, 0))
            radius = int(self.size * (self.frame / self.max_frames))
            pygame.draw.circle(self.image, RED, (self.size, self.size), radius)
            pygame.draw.circle(self.image, WHITE, (self.size, self.size), radius-5)

# Arka plan görselini yükleme fonksiyonu
def load_background_image():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, "arkaplan", "uzaybosluk.png")
        bg_image = pygame.image.load(image_path).convert()
        bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))  # Ekrana uygun boyuta getir
        return bg_image
    except Exception as e:
        print(f"Arka plan görseli yüklenemedi! Hata: {e}")
        return None

# Oyun başlangıç fonksiyonu
def init_game():
    global all_sprites, enemy_group, bullet_group, explosion_group, player, score, level, enemy_spawn_rate, last_enemy_spawn, coins
    
    all_sprites = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    bullet_group = pygame.sprite.Group()
    explosion_group = pygame.sprite.Group()
    
    player = Player()
    all_sprites.add(player)
    
    score = 0
    coins = 0
    level = 1
    enemy_spawn_rate = 1000
    last_enemy_spawn = pygame.time.get_ticks()

def spawn_enemy():
    enemy = Enemy()
    enemy_group.add(enemy)
    all_sprites.add(enemy)

# Arka plan görseli
bg_image = load_background_image()

# Oyunu başlat
init_game()

# Oyun döngüsü
running = True
while running:
    clock.tick(60)
    
    # Olay yönetimi
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if state == MENU:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    state = GAME
                    init_game()
        
        elif state == GAME:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullet = player.shoot()
                    if bullet:
                        bullet_group.add(bullet)
                        all_sprites.add(bullet)
                
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    player.moving_left = True
                if event.key in (pygame.K_RIGHT, pygame.K_d):
                    player.moving_right = True
                if event.key in (pygame.K_UP, pygame.K_w):
                    player.moving_up = True
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    player.moving_down = True
            
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    player.moving_left = False
                if event.key in (pygame.K_RIGHT, pygame.K_d):
                    player.moving_right = False
                if event.key in (pygame.K_UP, pygame.K_w):
                    player.moving_up = False
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    player.moving_down = False

    if state == GAME:
        # Arka planı ekrana çiz
        screen.blit(bg_image, (0, 0))
        
        # Yıldızları çizme
        for star in stars_far:
            pygame.draw.circle(screen, WHITE, (int(star[0]), int(star[1])), int(star[2]))
        for star in stars_mid:
            pygame.draw.circle(screen, WHITE, (int(star[0]), int(star[1])), int(star[2]))
        for star in stars_near:
            pygame.draw.circle(screen, WHITE, (int(star[0]), int(star[1])), int(star[2]))

        all_sprites.update()
        all_sprites.draw(screen)

        # Düşmanlarla mermi çarpışması kontrolü
        for bullet in bullet_group:
            for enemy in enemy_group:
                if bullet.rect.colliderect(enemy.rect):
                    enemy.kill()
                    bullet.kill()
                    score += 1
                    coins += 5
                    explosion = Explosion(enemy.rect.center)
                    explosion_group.add(explosion)
                    all_sprites.add(explosion)

        # Düşmanlar ekleniyor
        now = pygame.time.get_ticks()
        if now - last_enemy_spawn > enemy_spawn_rate:
            spawn_enemy()
            last_enemy_spawn = now
        
        # Coin sayısını göster
        coin_text = font_coin.render(f"COIN: {coins}", True, GOLD)
        screen.blit(coin_text, (10, 10))
        
        # Game Over kontrolü
        if pygame.sprite.spritecollideany(player, enemy_group):
            state = GAME_OVER
            if sound_enabled:
                game_over_sound.play()
    
    # Menü Ekranı
    elif state == MENU:
        screen.fill(BLACK)
        title_text = font_large.render("UZAY SAVAŞI", True, WHITE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 180))
        
        pygame.draw.rect(screen, WHITE, button_rect)  # Mavi yeri beyaz yap
        button_text = font_medium.render("OYNA", True, BLACK)
        screen.blit(button_text, (WIDTH // 2 - button_text.get_width() // 2, HEIGHT // 2 - 30))

        # "Geliştirici Mozzers" yazısı en sağ altta
        developer_text = font_dev.render("Geliştirici: Mozzers", True, WHITE)
        screen.blit(developer_text, (WIDTH - developer_text.get_width() - 10, HEIGHT - developer_text.get_height() - 10))
    
    # Game Over ekranı
    elif state == GAME_OVER:
        screen.fill(BLACK)
        game_over_text = font_large.render("GAME OVER", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))
        score_text = font_medium.render(f"Skor: {score}", True, WHITE)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
        
        pygame.display.flip()
        pygame.time.wait(2000)  # 2 saniye bekleyip yeniden başlat
        
        # Yeniden başlatmak için
        state = MENU
        init_game()

    pygame.display.flip()

pygame.quit()
sys.exit()
