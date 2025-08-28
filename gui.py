import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
from player import MusicPlayer
import os
import yt_dlp

class MusicPlayerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Player")
        
        # Estados
        self.is_playing = False
        self.is_paused = False
        self.music_length = 0
        self.current_time = 0
        
        # Inicializar o player
        self.player = MusicPlayer()

        # Interface
        self.status_label = tk.Label(root, text="Nenhuma música carregada.", width=50)
        self.status_label.pack(pady=10)

        # Barra de progresso (ttk.Progressbar) - com atualização de tempo e posição
        self.progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(padx=20, pady=10, fill=tk.X)
        self.progress_bar.bind("<Button-1>", self.jump_to_position)  # Atualizar posição ao clicar

        self.time_label = tk.Label(root, text="00:00 / 00:00", font=("Helvetica", 10))
        self.time_label.pack(pady=5)

        # Botões
        self.load_button = tk.Button(root, text="Carregar Música", command=self.load_music)
        self.load_button.pack(side=tk.LEFT, padx=10)

        self.youtube_button = tk.Button(root, text="Baixar do YouTube", command=self.download_youtube_music)
        self.youtube_button.pack(side=tk.LEFT, padx=10)

        self.play_button = tk.Button(root, text="▶", command=self.play_music)
        self.play_button.pack(side=tk.LEFT, padx=10)

        self.pause_button = tk.Button(root, text="⏸", command=self.pause_music)
        self.pause_button.pack(side=tk.LEFT, padx=10)

        self.stop_button = tk.Button(root, text="⏹", command=self.stop_music)
        self.stop_button.pack(side=tk.LEFT, padx=10)

        # Volume
        self.volume_slider = tk.Scale(root, from_=0, to=100, orient="horizontal", label="Volume")
        self.volume_slider.set(50)
        self.volume_slider.pack(side=tk.RIGHT, padx=10)
        self.volume_slider.bind("<Motion>", self.adjust_volume)

    def load_music(self):
        music_file = filedialog.askopenfilename(filetypes=(("Arquivos MP3", "*.mp3"),))
        if music_file:
            self.player.load_music(music_file)
            self.music_length = self.player.get_music_length()
            self.status_label.config(text=f"Música carregada: {os.path.basename(music_file)}")
            self.play_music()

    def download_youtube_music(self):
        search_query = simpledialog.askstring("Buscar Música", "Digite o nome ou link da música no YouTube:")
        if search_query:
            music_file = self.player.download_music_from_youtube(search_query)
            if music_file:
                self.status_label.config(text=f"Música baixada: {os.path.basename(music_file)}")
                self.music_length = self.player.get_music_length()
                self.play_music()

    def play_music(self):
        if self.player.current_music is None:
            self.status_label.config(text="Nenhuma música carregada.")
            return
        
        if not self.is_playing and not self.is_paused:
            self.player.play_music(start_time=self.current_time)
            self.is_playing = True
            self.is_paused = False
            self.update_progress()
        elif self.is_paused:
            self.player.resume_music()
            self.is_playing = True
            self.is_paused = False
            self.update_progress()

    def pause_music(self):
        if self.is_playing:
            self.is_paused = True
            self.player.pause_music()
            self.current_time = self.player.get_current_time()
            self.status_label.config(text="Música pausada.")

    def stop_music(self):
        self.is_playing = False
        self.is_paused = False
        self.player.stop_music()
        self.current_time = 0
        self.progress_bar["value"] = 0
        self.update_time_label(0)
        self.status_label.config(text="Música parada.")

    def jump_to_position(self, event):
        """Permite ao usuário saltar para um ponto na música clicando na barra."""
        if self.music_length > 0:
            width = self.progress_bar.winfo_width()
            click_x = event.x
            new_position = max(0, (click_x / width) * self.music_length)  # Posição na música em segundos
            self.player.set_position(new_position)  # Atualiza a posição da música no player
            
            # Atualiza o tempo local de reprodução (current_time)
            self.current_time = new_position  
            self.update_time_label(new_position)  # Atualiza o rótulo de tempo
            print(f"JUMP ACIONADO - NOVA POSIÇÃO: {new_position}")

            # Se a música estava pausada, resume a música a partir da nova posição
            if self.is_paused:
                self.player.resume_music()
                self.is_playing = True
                self.is_paused = False
                self.update_progress()
            elif not self.is_paused:  # Se estava tocando, apenas atualiza a barra de progresso
                self.update_progress()


    def update_progress(self):
        """Atualiza o progresso da barra e o rótulo de tempo."""
        if self.is_playing and not self.is_paused:
            # Atualizar o tempo atual
            self.current_time = self.player.get_current_time()

            # Evitar valores negativos de tempo
            self.current_time = max(0, self.current_time)

            # Atualizar a barra de progresso
            if self.music_length > 0:
                progress = (self.current_time / self.music_length) * 100
                self.progress_bar["value"] = progress

            # Atualizar rótulo de tempo
            self.update_time_label(self.current_time)
            print(f"TEMPO DECORRIDO: {self.current_time}")

            # Verificar se a música terminou
            if self.current_time >= self.music_length:
                self.stop_music()
            else:
                # Atualiza a cada 1000ms (1 segundo)
                self.root.after(1000, self.update_progress)


    def update_time_label(self, current_time):
        """Atualiza o rótulo de tempo com o formato MM:SS."""
        elapsed = self.format_time(current_time)
        total = self.format_time(self.music_length)
        self.time_label.config(text=f"{elapsed} / {total}")

    def format_time(self, seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02}:{seconds:02}"

    def adjust_volume(self, event):
        volume = self.volume_slider.get() / 100
        self.player.set_volume(volume)
