import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import cv2
import threading
from ffpyplayer.player import MediaPlayer

# Set appearance and color theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class VideoPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Side-by-Side Video Player")
        self.root.geometry("1640x700")

        # UI Elements
        self.label = ctk.CTkLabel(root, text="Video Player", font=("Helvetica", 18))
        self.label.pack(pady=(10, 0))

        # Button frame for horizontal layout
        self.button_frame = ctk.CTkFrame(root)
        self.button_frame.pack(pady=10)

        self.select_original_button = ctk.CTkButton(self.button_frame, text="Select Original Video", command=self.select_original_video)
        self.select_original_button.grid(row=0, column=0, padx=5)

        self.select_processed_button = ctk.CTkButton(self.button_frame, text="Select Processed Video", command=self.select_processed_video)
        self.select_processed_button.grid(row=0, column=1, padx=5)

        self.play_button = ctk.CTkButton(self.button_frame, text="Play Videos Side by Side", command=self.play_videos)
        self.play_button.grid(row=0, column=2, padx=5)
        self.play_button.configure(state="disabled")

        self.status_label = ctk.CTkLabel(root, text="", font=("Helvetica", 12))
        self.status_label.pack(pady=5)

        # Video display areas
        self.video_frame = ctk.CTkFrame(root)
        self.video_frame.pack(pady=10, fill="both", expand=True)

        # Define video labels to dynamically resize with window
        self.original_video_label = ctk.CTkLabel(self.video_frame, text="")
        self.original_video_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.processed_video_label = ctk.CTkLabel(self.video_frame, text="")
        self.processed_video_label.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.video_frame.grid_columnconfigure(0, weight=1)
        self.video_frame.grid_columnconfigure(1, weight=1)
        self.video_frame.grid_rowconfigure(0, weight=1)

        self.original_video_path = ""
        self.processed_video_path = ""

    def select_original_video(self):
        self.original_video_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mov")])
        if self.original_video_path:
            self.status_label.configure(text=f"Original video selected: {self.original_video_path}")
            if self.processed_video_path:
                self.play_button.configure(state="normal")
        else:
            messagebox.showerror("Error", "Failed to select original video")

    def select_processed_video(self):
        self.processed_video_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mov")])
        if self.processed_video_path:
            self.status_label.configure(text=f"Processed video selected: {self.processed_video_path}")
            if self.original_video_path:
                self.play_button.configure(state="normal")
        else:
            messagebox.showerror("Error", "Failed to select processed video")

    def play_videos(self):
        threading.Thread(target=self._play_video_with_audio, args=(self.original_video_path, self.original_video_label)).start()
        threading.Thread(target=self._play_video, args=(self.processed_video_path, self.processed_video_label)).start()

    def _play_video_with_audio(self, video_path, video_label):
        video = cv2.VideoCapture(video_path)
        player = MediaPlayer(video_path)

        while True:
            grabbed, frame = video.read()
            if not grabbed:
                break

            # Calculate new dimensions based on available label size
            label_width = video_label.winfo_width()
            label_height = video_label.winfo_height()
            resized_frame = cv2.resize(frame, (label_width, label_height))

            # Convert to CTkImage for High-DPI scaling
            img = ctk.CTkImage(Image.fromarray(cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)), size=(label_width, label_height))
            video_label.configure(image=img)
            video_label.image = img

            audio_frame, val = player.get_frame()
            if val == 'eof':
                break
            if cv2.waitKey(24) & 0xFF == ord("q"):
                break

        video.release()
        player.close_player()

    def _play_video(self, video_path, video_label):
        video = cv2.VideoCapture(video_path)
        while True:
            grabbed, frame = video.read()
            if not grabbed:
                break

            # Calculate new dimensions based on available label size
            label_width = video_label.winfo_width()
            label_height = video_label.winfo_height()
            resized_frame = cv2.resize(frame, (label_width, label_height))

            # Convert to CTkImage for High-DPI scaling
            img = ctk.CTkImage(Image.fromarray(cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)), size=(label_width, label_height))
            video_label.configure(image=img)
            video_label.image = img
            if cv2.waitKey(24) & 0xFF == ord("q"):
                break

        video.release()

if __name__ == "__main__":
    root = ctk.CTk()
    app = VideoPlayerApp(root)
    root.mainloop()
