import streamlit as st
from PIL import Image
import sys
print(sys.executable)
from src.remover import BackgroundRemover
import cv2
from moviepy.editor import *
import os




def save_uploaded_file(uploaded_file,filename, save_dir="./static/video"):
    file_path = os.path.join(save_dir, filename)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path


def process_video(input_path, output_path,background_path):

    # Open the video file
    video_capture = cv2.VideoCapture(input_path)
    # Get video properties
    images = []
    fps = int(video_capture.get(cv2.CAP_PROP_FPS))
    # Process each frame in the video
    while True:
        ret, frame = video_capture.read()
        if not ret:
            break
        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        processed_frame = obj.process_video(frame,background_path)
       
        # Get screen width for resizing
        screen_width = 1024  # Set this to your screen width if known (e.g., 800, 1024, etc.)
        scaling_factor = screen_width / frame.shape[1]
        new_width = screen_width
        new_height = int(frame.shape[0] * scaling_factor)

        # Resize to fit screen width
        resized_image = cv2.resize(frame, (new_width, new_height))
        resized_proimage = cv2.resize(processed_frame, (new_width, new_height))
        # Display the result
        cv2.imshow("Real-time Video", resized_image)
        cv2.imshow("Real-time Process", resized_proimage)
        images.append(processed_frame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            break

    cv2.destroyAllWindows()
    video_capture.release()

    # Create a video clip from processed images
    clip = ImageSequenceClip(images, fps=fps)

    # Extract the audio from the original video
    original_video = VideoFileClip(input_path)
    audio = original_video.audio

    # Add the original audio to the processed video
    final_clip = clip.set_audio(audio)

    # Write the result to the output file with audio
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")


st.set_page_config(
    page_title="Video Background Remover",
    page_icon="👋",
)

if __name__ == "__main__":

    obj = BackgroundRemover()

    st.title("DEMO")
    st.write("Upload an Video")

    uploaded_file = st.file_uploader("Choose a file",type=["mp4", "avi", "mov"])
    VIDEO_DIR = "./output"

    if uploaded_file is not None:
        # To read file as bytes:
        bytes_data = uploaded_file.getvalue()
        file_name = "upload.mp4"
        OUT_PATH =  os.path.join(VIDEO_DIR,"results.mp4")
        BACKGROUND_PATH = os.path.join(os.getcwd(),"static/background/2.png")

        col1, col2 = st.columns(2)
         
        with col1:
            st.video(data=uploaded_file)
            video_path = save_uploaded_file(uploaded_file,file_name)
            st.success(f"Video saved as {video_path}")
            flag1 = 1
            process_video(video_path,OUT_PATH,BACKGROUND_PATH)
            flag2 = 1

        with col2:
            if flag1==1 and flag2==1:
                st.video(data=OUT_PATH)
                st.success(f"Removing Background")
            
    else:

        st.write("Failed to upload video")


