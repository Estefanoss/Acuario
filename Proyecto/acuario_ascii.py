import pygame  
import random
import math
from datetime import datetime

# 1. Colores
COLS = 92       # Ancho del acuario en caracteres
ROWS = 32       # Alto del acuario en caracteres
FPS = 60

# Paleta de colores (R, G, B) inspirada en la referencia
COLOR_FONDO = (6, 10, 18)
COLOR_MARCO = (45, 95, 130)
COLOR_OLA_1 = (70, 170, 220)
COLOR_OLA_2 = (35, 100, 150)
COLOR_ARENA = (160, 125, 85)
COLOR_HUD = (80, 185, 225)
COLOR_BURBUJA = (120, 210, 255)
COLOR_COMIDA = (255, 230, 120)

# Colores por capa para simular profundidad (más oscuro = más lejos)
COLORES_ALGAS = {
    0: (25, 75, 50),    # Capa fondo (oscuro)
    2: (60, 195, 110)   # Capa frente (brillante)
}

COLORES_PECES = {
    0: [(60, 85, 110), (75, 95, 105)],                        # Fondo: tonos apagados
    1: [(90, 165, 215), (180, 110, 185), (195, 145, 80)],     # Medio: tonos intermedios
    2: [(255, 115, 75), (90, 235, 145), (255, 85, 100), (255, 215, 80)]  # Frente: neón
}


# 2. CLASES DEL ACUARIO (ENTIDADES)
class Pez:
    def __init__(self, capa):
        self.capa = capa  # 0: Fondo, 1: Medio, 2: Primer plano
        
        # Sprites (izquierda, derecha) según la profundidad
        if capa == 0:
            self.sprite_izq, self.sprite_der = random.choice([("<><", "><>"), ("<°><", "><°>")])
            self.vel_base = random.uniform(3.0, 5.5)
        elif capa == 1:
            self.sprite_izq, self.sprite_der = random.choice([("<===<", ">===>"), ("<°))><", "><((°>")])
            self.vel_base = random.uniform(5.5, 8.5)
        else:
            self.sprite_izq, self.sprite_der = random.choice([("<°)))><", "><(((°>"), ("<*(((><", "><)))*>"), ("<°)))><>", "<><(((°>")])
            self.vel_base = random.uniform(7.5, 11.5)

        self.color = random.choice(COLORES_PECES[capa])
        self.x = random.uniform(5, COLS - 12)
        self.y = random.uniform(5, ROWS - 7)
        
        direccion = random.choice([-1, 1])
        self.vx = self.vel_base * direccion
        self.vy = 0.0
        self.fase = random.uniform(0, math.pi * 2)
        self.mirando_der = direccion > 0

    def actualizar(self, dt, tiempo, objetivo):
        # Si el usuario hizo clic, el pez nada suavemente hacia ese punto
        if objetivo is not None:
            dx = objetivo[0] - self.x
            dy = objetivo[1] - self.y
            dist = math.hypot(dx, dy)

            if dist > 2.0:
                # Velocidad deseada hacia el clic (los del fondo reaccionan un poco más lento)
                factor_profundidad = 0.7 if self.capa == 0 else (1.0 if self.capa == 1 else 1.3)
                vel_deseada_x = (dx / dist) * (self.vel_base * 1.9 * factor_profundidad)
                vel_deseada_y = (dy / dist) * (self.vel_base * 1.4 * factor_profundidad)

                # Interpolación suave (steering) para evitar giros bruscos
                suavizado = 2.8 * dt
                self.vx += (vel_deseada_x - self.vx) * suavizado
                self.vy += (vel_deseada_y - self.vy) * suavizado
            else:
                # Al llegar cerca, frena suavemente y flota alrededor
                self.vx *= (1 - 2.0 * dt)
                self.vy += math.sin(tiempo * 3 + self.fase) * 1.5 * dt
        else:
            # Nado libre natural (crucero horizontal + ligero vaivén vertical)
            dir_actual = 1 if self.mirando_der else -1
            vel_objetivo_x = self.vel_base * dir_actual
            vel_objetivo_y = math.sin(tiempo * 1.5 + self.fase) * 1.2

            self.vx += (vel_objetivo_x - self.vx) * 1.5 * dt
            self.vy += (vel_objetivo_y - self.vy) * 2.0 * dt

        # Aplicar movimiento
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Actualizar dirección visual según la velocidad horizontal
        if self.vx > 0.3:
            self.mirando_der = True
        elif self.vx < -0.3:
            self.mirando_der = False

        # Rebotar suavemente en los bordes del acuario
        largo = len(self.sprite_der)
        if self.x < 2:
            self.x = 2
            self.vx = abs(self.vx)
            self.mirando_der = True
        elif self.x > COLS - largo - 2:
            self.x = COLS - largo - 2
            self.vx = -abs(self.vx)
            self.mirando_der = False

        if self.y < 4:
            self.y = 4
            self.vy = abs(self.vy) * 0.5
        elif self.y > ROWS - 5:
            self.y = ROWS - 5
            self.vy = -abs(self.vy) * 0.5

    def dibujar(self, pantalla, fuente, char_w, char_h):
        sprite = self.sprite_der if self.mirando_der else self.sprite_izq
        dibujar_ascii(pantalla, fuente, int(round(self.x)), int(round(self.y)), sprite, self.color, char_w, char_h)


class Medusa:
    def __init__(self):
        self.x = random.uniform(10, COLS - 10)
        self.y = random.uniform(6, ROWS - 10)
        self.fase = random.uniform(0, math.pi * 2)
        self.color_cabeza = (225, 115, 195)
        self.color_tentaculos = (145, 75, 170)

    def actualizar(self, dt, tiempo):
        # Impulso rítmico hacia arriba y caída suave
        pulso = math.sin(tiempo * 2.2 + self.fase)
        self.y -= pulso * 1.8 * dt
        self.x += math.cos(tiempo * 0.6 + self.fase) * 0.8 * dt

        # Mantener dentro del agua
        self.y = max(5, min(ROWS - 8, self.y))
        self.x = max(4, min(COLS - 8, self.x))

    def dibujar(self, pantalla, fuente, char_w, char_h, tiempo):
        gx, gy = int(round(self.x)), int(round(self.y))
        tentaculos = "|||" if math.sin(tiempo * 4 + self.fase) > 0 else "| |"
        dibujar_ascii(pantalla, fuente, gx, gy, "(^)", self.color_cabeza, char_w, char_h)
        dibujar_ascii(pantalla, fuente, gx, gy + 1, tentaculos, self.color_tentaculos, char_w, char_h)


class Burbuja:
    def __init__(self, x=None, y=None):
        self.reiniciar(x, y)

    def reiniciar(self, x=None, y=None):
        self.x = x if x is not None else random.uniform(3, COLS - 4)
        self.y = y if y is not None else random.uniform(ROWS - 6, ROWS - 3)
        self.vel_y = random.uniform(2.5, 5.5)
        self.fase = random.uniform(0, math.pi * 2)

    def actualizar(self, dt, tiempo):
        self.y -= self.vel_y * dt
        self.x += math.sin(tiempo * 3 + self.fase) * 1.2 * dt
        if self.y < 3.5:
            self.reiniciar()

    def dibujar(self, pantalla, fuente, char_w, char_h):
        # Cambia de tamaño al subir
        if self.y > ROWS - 10:
            simbolo = "."
        elif self.y > 10:
            simbolo = "o"
        else:
            simbolo = "O"
        dibujar_ascii(pantalla, fuente, int(round(self.x)), int(round(self.y)), simbolo, COLOR_BURBUJA, char_w, char_h)


class Alga:
    def __init__(self, x, altura, capa):
        self.x = x
        self.altura = altura
        self.capa = capa
        self.color = COLORES_ALGAS[capa]
        self.fase = random.uniform(0, math.pi * 2)
        self.tipo = random.choice(["hoja", "tallo"])

    def dibujar(self, pantalla, fuente, char_w, char_h, tiempo):
        base_y = ROWS - 3
        for i in range(self.altura):
            y = base_y - i
            # Movimiento ondulante progresivo (más fuerte en la punta)
            onda = math.sin(tiempo * 2.0 + self.fase + i * 0.6)
            desplazamiento = int(round(onda * (i / self.altura) * 1.2))
            
            if i == self.altura - 1:
                simbolo = "T" if self.tipo == "hoja" else "^"
            elif onda > 0.3:
                simbolo = ")"
            elif onda < -0.3:
                simbolo = "("
            else:
                simbolo = "Y" if i % 2 == 0 else "|"

            dibujar_ascii(pantalla, fuente, self.x + desplazamiento, y, simbolo, self.color, char_w, char_h)


class OndaClic:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vida = 1.0  

    def actualizar(self, dt):
        self.vida -= dt * 1.4

    def dibujar(self, pantalla, fuente, char_w, char_h):
        gx, gy = int(round(self.x)), int(round(self.y))
        if self.vida > 0.65:
            dibujar_ascii(pantalla, fuente, gx, gy, "*", COLOR_COMIDA, char_w, char_h)
        elif self.vida > 0.3:
            dibujar_ascii(pantalla, fuente, gx - 1, gy, "(o)", COLOR_BURBUJA, char_w, char_h)
        else:
            dibujar_ascii(pantalla, fuente, gx - 2, gy, "(   )", COLOR_OLA_2, char_w, char_h)


# 3. FUNCIONES AUXILIARES DE DIBUJO
def dibujar_ascii(pantalla, fuente, col, row, texto, color, char_w, char_h):
    if 0 <= row < ROWS:
        superficie = fuente.render(texto, True, color)
        pantalla.blit(superficie, (col * char_w, row * char_h))


def dibujar_escenario(pantalla, fuente, char_w, char_h, tiempo, total_peces):
    # 1. Marco exterior
    dibujar_ascii(pantalla, fuente, 0, 0, "-" * COLS, COLOR_MARCO, char_w, char_h)
    for r in range(1, ROWS - 2):
        dibujar_ascii(pantalla, fuente, 0, r, "|", COLOR_MARCO, char_w, char_h)
        dibujar_ascii(pantalla, fuente, COLS - 1, r, "|", COLOR_MARCO, char_w, char_h)

    # 2. Olas animadas en la superficie (filas 1 y 2)
    ola_sup = ""
    ola_inf = ""
    for c in range(1, COLS - 1):
        val1 = math.sin(c * 0.22 + tiempo * 2.5)
        val2 = math.cos(c * 0.15 - tiempo * 1.8)
        ola_sup += "-" if val1 > 0.3 else ("_" if val1 < -0.5 else " ")
        ola_inf += "_" if val2 > 0.4 else ("-" if val2 < -0.6 else " ")
    dibujar_ascii(pantalla, fuente, 1, 1, ola_sup, COLOR_OLA_1, char_w, char_h)
    dibujar_ascii(pantalla, fuente, 1, 2, ola_inf, COLOR_OLA_2, char_w, char_h)

    # 3. Arena en el fondo (fila ROWS - 2)
    patron_arena = "._.-._..-_."
    arena = (patron_arena * (COLS // len(patron_arena) + 1))[:COLS - 2]
    dibujar_ascii(pantalla, fuente, 1, ROWS - 2, arena, COLOR_ARENA, char_w, char_h)

    # 4. Barra de estado inferior (HUD)
    hora_actual = datetime.now().strftime("%H:%M")
    hud = f" [ AQUARIUM ]   fish:{total_peces}   time:{hora_actual}   temp:24c   depth:3.2m   "
    hud += "-" * max(0, COLS - len(hud))
    dibujar_ascii(pantalla, fuente, 0, ROWS - 1, hud, COLOR_HUD, char_w, char_h)


# 4. BUCLE PRINCIPAL DEL PROGRAMA
def main():
    pygame.init()
    
    # Fuente monoespaciada (esencial para que el arte ASCII quede alineado)
    fuente = pygame.font.SysFont("consolas,couriernew,dejavusansmono,monospace", 18, bold=True)
    char_w, char_h = fuente.size("M")

    pantalla = pygame.display.set_mode((COLS * char_w, ROWS * char_h))
    pygame.display.set_caption("Acuario ASCII Interactivo")
    reloj = pygame.time.Clock()

    # Crear entidades distribuidas por capas
    peces = (
        [Pez(capa=0) for _ in range(4)] +   # 4 peces lejanos
        [Pez(capa=1) for _ in range(4)] +   # 4 peces intermedios
        [Pez(capa=2) for _ in range(4)]     # 4 peces en primer plano
    )
    medusas = [Medusa() for _ in range(2)]
    burbujas = [Burbuja() for _ in range(14)]
    plancton = [(random.randint(3, COLS - 4), random.randint(4, ROWS - 5)) for _ in range(18)]

    algas_fondo = [Alga(x, random.randint(4, 7), capa=0) for x in range(5, COLS - 5, 9)]
    algas_frente = [Alga(x, random.randint(5, 9), capa=2) for x in range(3, COLS - 5, 11)]

    ondas = []
    objetivo_clic = None
    tiempo_objetivo = 0.0
    tiempo_total = 0.0

    ejecutando = True
    while ejecutando:
        dt = min(reloj.tick(FPS) / 1000.0, 0.05)  # Delta time seguro
        tiempo_total += dt

        # --- Eventos (Teclado y Ratón) ---
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                mx, my = evento.pos
                gx = max(3, min(COLS - 4, mx / char_w))
                gy = max(4, min(ROWS - 5, my / char_h))
                objetivo_clic = (gx, gy)
                tiempo_objetivo = 4.5  # Los peces seguirán el clic durante 4.5 segundos
                ondas.append(OndaClic(gx, gy))
                # Generar un par de burbujas en el lugar del clic
                burbujas.append(Burbuja(gx, gy))

        # Reducir temporizador del clic
        if tiempo_objetivo > 0:
            tiempo_objetivo -= dt
            if tiempo_objetivo <= 0:
                objetivo_clic = None

        # --- Actualizar lógica ---
        for pez in peces:
            pez.actualizar(dt, tiempo_total, objetivo_clic)
        for medusa in medusas:
            medusa.actualizar(dt, tiempo_total)
        for burbuja in burbujas:
            burbuja.actualizar(dt, tiempo_total)
        for onda in ondas[:]:
            onda.actualizar(dt)
            if onda.vida <= 0:
                ondas.remove(onda)
        # Mantener un límite sano de burbujas extra
        if len(burbujas) > 22:
            burbujas.pop(0)

        # --- Dibujado por CAPAS (Algoritmo del pintor) ---
        pantalla.fill(COLOR_FONDO)

        # Escenario base (marco, olas, arena, HUD)
        dibujar_escenario(pantalla, fuente, char_w, char_h, tiempo_total, len(peces) + len(medusas))

        # CAPA 0: Fondo (plancton, algas oscuras, peces pequeños/lentos)
        for px, py in plancton:
            dibujar_ascii(pantalla, fuente, px, py, ".", (30, 50, 75), char_w, char_h)
        for alga in algas_fondo:
            alga.dibujar(pantalla, fuente, char_w, char_h, tiempo_total)
        for pez in peces:
            if pez.capa == 0:
                pez.dibujar(pantalla, fuente, char_w, char_h)

        # CAPA 1: Intermedia (burbujas, medusas, ondas de clic, peces medianos)
        for burbuja in burbujas:
            burbuja.dibujar(pantalla, fuente, char_w, char_h)
        for medusa in medusas:
            medusa.dibujar(pantalla, fuente, char_w, char_h, tiempo_total)
        for onda in ondas:
            onda.dibujar(pantalla, fuente, char_w, char_h)
        for pez in peces:
            if pez.capa == 1:
                pez.dibujar(pantalla, fuente, char_w, char_h)

        # CAPA 2: Primer plano (algas brillantes y peces grandes/vivos)
        for alga in algas_frente:
            alga.dibujar(pantalla, fuente, char_w, char_h, tiempo_total)
        for pez in peces:
            if pez.capa == 2:
                pez.dibujar(pantalla, fuente, char_w, char_h)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()