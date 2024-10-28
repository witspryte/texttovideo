import time
import os
import tempfile
import platform
import subprocess
from moviepy.editor import (AudioFileClip, CompositeVideoClip, CompositeAudioClip, TextClip, VideoFileClip)
import requests

def download_file(url, filename):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded {url} to {filename}")
    except requests.RequestException as e:
        print(f"Failed to download {url}: {e}")

def search_program(program_name):
    try:
        search_cmd = "where" if platform.system() == "Windows" else "which"
        return subprocess.check_output([search_cmd, program_name]).decode().strip()
    except subprocess.CalledProcessError:
        return None

def get_program_path(program_name):
    program_path = search_program(program_name)
    return program_path

def get_output_media(audio_file_path, timed_captions, background_video_data, video_server):
    OUTPUT_FILE_NAME = "rendered_video.mp4"
    magick_path = get_program_path("magick")
    print(magick_path)
    
    if magick_path:
        os.environ['IMAGEMAGICK_BINARY'] = magick_path
    else:
        os.environ['IMAGEMAGICK_BINARY'] = '/usr/bin/convert'
    
    visual_clips = []
    for (t1, t2), video_url in background_video_data:
        video_filename = tempfile.NamedTemporaryFile(delete=False).name
        download_file(video_url, video_filename)
        
        print(f"Trying to load video from {video_filename} (URL: {video_url})")
        
        # Check if the file exists and has a valid size
        if os.path.exists(video_filename) and os.path.getsize(video_filename) > 1000:  # Assuming a minimum size
            try:
                video_clip = VideoFileClip(video_filename).subclip(t1, t2)  # Set the desired subclip
                visual_clips.append(video_clip)
                print(f"Successfully loaded video: {video_filename}")
            except Exception as e:
                print(f"Error loading video {video_filename}: {e}")
        else:
            print(f"Downloaded file {video_filename} is invalid or too small.")
    
    audio_clips = []
    try:
        audio_file_clip = AudioFileClip(audio_file_path)
        audio_clips.append(audio_file_clip)
    except Exception as e:
        print(f"Error loading audio file {audio_file_path}: {e}")

    for (t1, t2), text in timed_captions:
        text_clip = TextClip(txt=text, fontsize=100, color="white", stroke_width=3, stroke_color="black", method="label")
        text_clip = text_clip.set_start(t1)
        text_clip = text_clip.set_end(t2)
        text_clip = text_clip.set_position(["center", 800])
        visual_clips.append(text_clip)

    video = CompositeVideoClip(visual_clips)
    
    if audio_clips:
        audio = CompositeAudioClip(audio_clips)
        video.duration = audio.duration
        video.audio = audio

    video.write_videofile(OUTPUT_FILE_NAME, codec='libx264', audio_codec='aac', fps=25, preset='veryfast')
    
    # Clean up downloaded files
    for (t1, t2), video_url in background_video_data:
        try:
            os.remove(video_filename)
        except Exception as e:
            print(f"Error removing file {video_filename}: {e}")

    return OUTPUT_FILE_NAME

# Sample data for testing
SAMPLE_FILE_NAME = "path_to_your_audio_file.mp3"  # Replace with your audio file path
timed_captions = [((0, 1), "Hello"), ((1, 2), "World")]
background_video_urls = [
    ((0, 0.52), 'https://videos.pexels.com/video-files/6266892/6266892-hd_1920_1080_30fps.mp4'),
    ((0.52, 0.94), 'https://videos.pexels.com/video-files/8439478/8439478-hd_1920_1080_25fps.mp4'),
    # Add more tuples as needed
]

VIDEO_SERVER = "your_video_server"  # Replace with your video server info if needed

# Call the function to generate output media
get_output_media(SAMPLE_FILE_NAME, timed_captions, background_video_urls, VIDEO_SERVER)

