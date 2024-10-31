import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
from moviepy.editor import VideoFileClip, ImageSequenceClip
from pydub import AudioSegment
from pydub.playback import play
import os
import threading
from src.remover import BackgroundRemover

# Set appearance and color theme
ctk.set_appearance_mode("Dark")  # Set to dark mode
ctk.set_default_color_theme("dark-blue")  # Dark blue theme, but you can customize further

class VideoBackgroundRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Backova")
        self.root.geometry("1240x600")

        # Initialize the BackgroundRemover object
        self.obj = BackgroundRemover()

        # UI Elements
        self.label = ctk.CTkLabel(root, text="Video Background Remover", font=("Helvetica", 18))
        self.label.pack(pady=10)

        self.upload_button = ctk.CTkButton(root, text="Upload Video", command=self.upload_video)
        self.upload_button.pack(pady=5)

        self.process_button = ctk.CTkButton(root, text="Process Video", command=self.process_video)
        self.process_button.pack(pady=5)
        self.process_button.configure(state="disabled")

        self.status_label = ctk.CTkLabel(root, text="", font=("Helvetica", 12))
        self.status_label.pack(pady=5)

        # Video display areas
        self.video_frame = ctk.CTkFrame(root)
        self.video_frame.pack(pady=10, fill="both", expand=True)
        
        self.original_video_label = ctk.CTkLabel(self.video_frame, text="")
        self.original_video_label.grid(row=0, column=0, padx=10, pady=10)

        self.processed_video_label = ctk.CTkLabel(self.video_frame, text="")
        self.processed_video_label.grid(row=0, column=1, padx=10, pady=10)
        
        
        self.original_label = ctk.CTkLabel(self.video_frame, text="Original Video")
        self.original_label.grid(row=1, column=0, padx=10, pady=10)

        self.processed_label = ctk.CTkLabel(self.video_frame, text="Processed Video")
        self.processed_label.grid(row=1, column=1, padx=10, pady=10)


        self.video_path = ""
        self.output_path = "./output/results.mp4"
        self.background_path = os.path.join(os.getcwd(), "background/2.png")
        self.images = []

    def upload_video(self):
        self.video_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mov")])
        if self.video_path:
            self.status_label.configure(text=f"Video uploaded: {os.path.basename(self.video_path)}")
            self.process_button.configure(state="normal")
        else:
            messagebox.showerror("Error", "Failed to upload video")

    def process_video(self):
        if not self.video_path:
            messagebox.showwarning("Warning", "Please upload a video first.")
            return

        self.status_label.configure(text="Processing video... Please wait.")
        self.root.update_idletasks()

        # Process video in a new thread to avoid freezing the UI
        threading.Thread(target=self._process_video_task).start()

    def _process_video_task(self):
        cap = cv2.VideoCapture(self.video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        # Clear previous images
        self.images = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            processed_frame = self.obj.process_video(frame, self.background_path)

            # Resize for displaying in the UI
            screen_width = 600
            scaling_factor = screen_width / frame.shape[1]
            new_width = screen_width
            new_height = int(frame.shape[0] * scaling_factor)
            resized_frame = cv2.resize(frame, (new_width, new_height))
            resized_processed_frame = cv2.resize(processed_frame, (new_width, new_height))

            # Convert frames to ImageTk for displaying in labels
            original_img = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)))
            processed_img = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(resized_processed_frame, cv2.COLOR_BGR2RGB)))

            # Update the labels to show frames
            self.original_video_label.configure(image=original_img)
            self.processed_video_label.configure(image=processed_img)
            self.original_video_label.image = original_img
            self.processed_video_label.image = processed_img

            self.images.append(cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB))
            self.root.update_idletasks()

        cap.release()

        # Save processed video with audio
        self.save_processed_video(self.images, fps)
        self.status_label.configure(text="Video processed and saved successfully!")

        # Play both videos in UI
        self.play_videos()

    def save_processed_video(self, frames, fps):
        clip = ImageSequenceClip(frames, fps=fps)
        original_video = VideoFileClip(self.video_path)
        audio = original_video.audio

        final_clip = clip.set_audio(audio)
        final_clip.write_videofile(self.output_path, codec="libx264", audio_codec="aac")

        messagebox.showinfo("Success", f"Video saved to {self.output_path}")

    def play_videos(self):
        self.status_label.configure(text="Playing videos...")

        # Use threading to play audio and video asynchronously
        threading.Thread(target=self._play_video_with_audio, args=(self.video_path, self.original_video_label)).start()
        threading.Thread(target=self._play_video_with_audio, args=(self.output_path, self.processed_video_label)).start()

    def _play_video_with_audio(self, video_path, label):
        video = VideoFileClip(video_path)
        # Calculate frame delay based on the video's frame rate
        fps = video.fps
        delay = int(1000 / fps)  # Convert fps to milliseconds
        
        
        audio = AudioSegment.from_file(video_path)
        
        # Play audio in a separate thread
        threading.Thread(target=play, args=(audio,)).start()
       
        for frame in video.iter_frames(fps=fps, dtype="uint8"):
            # Resize for displaying in the UI
            screen_width = 600
            scaling_factor = screen_width / frame.shape[1]
            new_width = screen_width
            new_height = int(frame.shape[0] * scaling_factor)
            resized_frame = cv2.resize(frame, (new_width, new_height))
            img = ImageTk.PhotoImage(image=Image.fromarray(resized_frame))
            label.configure(image=img)
            label.image = img
            self.root.update()
            self.root.after(12)  # Adjust the delay to match the frame rate

if __name__ == "__main__":
    root = ctk.CTk()
    app = VideoBackgroundRemoverApp(root)
    root.mainloop()
