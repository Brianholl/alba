#!/usr/bin/env python3
"""Lanzador de juegos educativos - Taller de Informática"""
import tkinter as tk
import subprocess
import os
try:
    from PIL import Image, ImageTk
    PIL_OK = True
except ImportError:
    PIL_OK = False

GAMES = [
    # ── Pantalla principal · baja exigencia, sin presión de tiempo ──────────────
    {"name": "Tux Paint",     "desc": "Dibujar y pintar",     "cmd": "tuxpaint",
     "color": "#e17055", "dark": "#c25640", "screen": "main",
     "icon": "/usr/share/icons/hicolor/128x128/apps/tuxpaint.png"},
    {"name": "GCompris",      "desc": "Actividades variadas", "cmd": "gcompris-qt",
     "color": "#00b894", "dark": "#008f73", "screen": "main",
     "icon": "/usr/share/icons/hicolor/256x256/apps/gcompris-qt.png"},
    {"name": "Frozen Bubble", "desc": "Puzzle de burbujas",   "cmd": "frozen-bubble",
     "color": "#00cec9", "dark": "#009e9a", "screen": "main",
     "icon": "/usr/share/icons/hicolor/64x64/apps/frozen-bubble.png"},
    # ── Pantalla avanzada · requiere lectura, cálculo o escritura ───────────────
    {"name": "Tux Typing",    "desc": "Mecanografía",         "cmd": "tuxtype",
     "color": "#e84393", "dark": "#b5306f", "screen": "advanced",
     "icon": "/usr/share/tuxtype/images/tux2.png"},
    {"name": "Tux Math",      "desc": "Matemáticas",          "cmd": "tuxmath",
     "color": "#0984e3", "dark": "#0769b4", "screen": "advanced",
     "icon": "/usr/share/tuxmath/images/factoroids/tux.png"},
    {"name": "KTurtle",       "desc": "Programación visual",  "cmd": "kturtle",
     "color": "#6c5ce7", "dark": "#5040c4", "screen": "advanced",
     "icon": "/usr/share/icons/hicolor/128x128/apps/kturtle.png"},
]

BG         = "#12111a"
FG_MAIN    = "#ffffff"
FG_DIM     = "#3d3d5c"
RADIUS     = 18

# ── Configuración de accesibilidad (ajustable por el docente) ──────────────────
COLS         = 3      # juegos por fila; bajalo a 2 para tiles aún más grandes
ICON_SIZE    = 132    # el ícono es el protagonista (admite fotos reales .jpg/.png)
SHOW_DESC    = True   # mostrar la descripción bajo el nombre
SOUND_ON_TAP = True   # sonido suave de confirmación al elegir un juego
EXIT_LOCKED  = True   # ESC NO cierra (evita salidas accidentales del alumno)
EXIT_COMBO   = "<Control-Shift-q>"  # combinación del docente para salir

LOCALE_ENV = {**os.environ,
              "LANG": "es_AR.UTF-8",
              "LANGUAGE": "es_AR:es",
              "LC_ALL": "es_AR.UTF-8"}


def load_icon(path):
    if not PIL_OK:
        return None
    try:
        img = Image.open(path).convert("RGBA")
        img.thumbnail((ICON_SIZE, ICON_SIZE), Image.LANCZOS)
        canvas = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
        offset = ((ICON_SIZE - img.width) // 2, (ICON_SIZE - img.height) // 2)
        canvas.paste(img, offset, img)
        return ImageTk.PhotoImage(canvas)
    except Exception:
        return None


def draw_bg(cv, w, h, r, color):
    cv.delete("bg")
    cv.create_rectangle(r, 0, w-r, h,   fill=color, outline=color, tags="bg")
    cv.create_rectangle(0, r, w,   h-r, fill=color, outline=color, tags="bg")
    for ax, ay, start in [(0, 0, 90), (w-2*r, 0, 0), (0, h-2*r, 180), (w-2*r, h-2*r, 270)]:
        cv.create_arc(ax, ay, ax+2*r, ay+2*r, start=start, extent=90,
                      fill=color, outline=color, style="pieslice", tags="bg")
    cv.tag_raise("fg")


def launch(cmd):
    subprocess.Popen(cmd.split(), start_new_session=True, env=LOCALE_ENV)


def play_confirm(root):
    """Sonido de confirmación suave al elegir un juego."""
    if not SOUND_ON_TAP:
        return
    snd = "/usr/share/sounds/freedesktop/stereo/bell.oga"
    if os.path.exists(snd):
        try:
            subprocess.Popen(["paplay", snd],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
            return
        except Exception:
            pass
    try:
        root.bell()  # respaldo si no hay reproductor/sonido del sistema
    except Exception:
        pass


def show_launching(root, game, icon):
    """Confirmación visual a pantalla completa antes de abrir el juego."""
    overlay = tk.Frame(root, bg=game["color"])
    overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

    inner = tk.Frame(overlay, bg=game["color"])
    inner.place(relx=0.5, rely=0.5, anchor="center")

    if icon:
        lbl = tk.Label(inner, image=icon, bg=game["color"])
        lbl.image = icon  # mantener la referencia viva
        lbl.pack(pady=(0, 28))

    tk.Label(inner, text="Abriendo " + game["name"] + "…",
             font=("DejaVu Sans", 34, "bold"),
             bg=game["color"], fg="white").pack()

    overlay.tkraise()
    # El overlay se quita solo; la ventana del juego aparecerá encima.
    root.after(2500, overlay.destroy)


def nav_button(parent, text, command):
    btn = tk.Button(parent, text=text, command=command,
                    font=("DejaVu Sans", 14, "bold"),
                    bg="#1e1d30", fg="#b0b0d0",
                    activebackground="#2a2940", activeforeground="#ffffff",
                    relief="flat", bd=0, padx=28, pady=12, cursor="hand2")
    btn.pack()
    return btn


def clear(root):
    for w in root.winfo_children():
        w.destroy()


def show_screen(root, screen):
    clear(root)

    W = root.winfo_screenwidth()
    H = root.winfo_screenheight()

    games = [g for g in GAMES if g["screen"] == screen]

    rows   = max((len(games) + COLS - 1) // COLS, 1)
    tile_w = min(360, (W - 140) // COLS)
    tile_h = min(300, (H - 300) // rows)
    pad    = 22

    icons = [load_icon(g["icon"]) for g in games]

    # ── Header ────────────────────────────────────────────────────────────────
    if screen == "main":
        title, subtitle = "Taller de Informática", "Elige un juego para empezar"
    else:
        title, subtitle = "Juegos avanzados", "Lectura, cálculo y programación"

    hdr = tk.Frame(root, bg=BG)
    hdr.pack(fill="x", pady=(44, 6))
    tk.Label(hdr, text=title,
             font=("DejaVu Sans", 42, "bold"), bg=BG, fg=FG_MAIN).pack()
    tk.Label(hdr, text=subtitle,
             font=("DejaVu Sans", 15), bg=BG, fg="#7070a0").pack(pady=7)
    tk.Frame(root, bg="#1e1d30", height=1).pack(fill="x", padx=80, pady=(0, 26))

    # ── Tiles ─────────────────────────────────────────────────────────────────
    grid = tk.Frame(root, bg=BG)
    grid.pack(expand=True)

    _refs = []  # keep PhotoImage references alive

    for i, (game, icon) in enumerate(zip(games, icons)):
        col = i % COLS
        row = i // COLS

        cv = tk.Canvas(grid, width=tile_w, height=tile_h,
                       bg=BG, highlightthickness=0, cursor="hand2")
        cv.grid(row=row, column=col, padx=pad, pady=pad)

        draw_bg(cv, tile_w, tile_h, RADIUS, game["color"])

        cx = tile_w // 2

        if icon:
            _refs.append(icon)
            cv.create_image(cx, int(tile_h * 0.40), anchor="center",
                            image=icon, tags="fg")

        name_y = 0.78 if SHOW_DESC else 0.83
        cv.create_text(cx, int(tile_h * name_y), text=game["name"],
                       font=("DejaVu Sans", 20, "bold"),
                       fill="white", anchor="center", tags="fg")
        if SHOW_DESC:
            cv.create_text(cx, int(tile_h * 0.90), text=game["desc"],
                           font=("DejaVu Sans", 13),
                           fill="white", anchor="center", tags="fg")

        def on_press(e, c=cv, g=game, tw=tile_w, th=tile_h):
            draw_bg(c, tw, th, RADIUS, g["dark"])

        def on_release(e, c=cv, g=game, ic=icon, tw=tile_w, th=tile_h):
            draw_bg(c, tw, th, RADIUS, g["color"])
            if 0 <= e.x <= tw and 0 <= e.y <= th:
                play_confirm(root)
                show_launching(root, g, ic)
                root.after(600, lambda: launch(g["cmd"]))

        def on_enter(e, c=cv, g=game, tw=tile_w, th=tile_h):
            draw_bg(c, tw, th, RADIUS, g["dark"])

        def on_leave(e, c=cv, g=game, tw=tile_w, th=tile_h):
            draw_bg(c, tw, th, RADIUS, g["color"])

        cv.bind("<ButtonPress-1>",   on_press)
        cv.bind("<ButtonRelease-1>", on_release)
        cv.bind("<Enter>",           on_enter)
        cv.bind("<Leave>",           on_leave)

    root._refs = _refs

    # ── Footer ────────────────────────────────────────────────────────────────
    foot = ("Para salir, pedile ayuda al docente" if EXIT_LOCKED
            else "F11 · pantalla completa     ESC · salir")
    tk.Label(root, text=foot,
             font=("DejaVu Sans", 11), bg=BG, fg=FG_DIM, pady=18
             ).pack(side="bottom")

    # ── Navegación entre pantallas ──────────────────────────────────────────────
    nav = tk.Frame(root, bg=BG)
    nav.pack(side="bottom", pady=(0, 6))
    if screen == "main":
        nav_button(nav, "Más juegos  →", lambda: show_screen(root, "advanced"))
    else:
        nav_button(nav, "←  Volver", lambda: show_screen(root, "main"))


def main():
    root = tk.Tk()
    root.title("Taller de Informática")
    root.configure(bg=BG)
    root.attributes("-fullscreen", True)
    if EXIT_LOCKED:
        root.bind("<Escape>", lambda e: "break")          # ESC no cierra
        root.bind(EXIT_COMBO, lambda e: root.destroy())   # salida del docente
    else:
        root.bind("<Escape>", lambda e: root.destroy())
    root.bind("<F11>",    lambda e: root.attributes("-fullscreen",
                                    not root.attributes("-fullscreen")))
    show_screen(root, "main")
    root.mainloop()


if __name__ == "__main__":
    main()
