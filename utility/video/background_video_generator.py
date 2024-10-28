import os
import requests
from utility.utils import log_response, LOG_TYPE_PEXEL

PEXELS_API_KEY = os.environ.get('PEXELS_KEY')

def search_videos(query_string, orientation_landscape=True):
    url = "https://api.pexels.com/videos/search"
    headers = {
        "Authorization": PEXELS_API_KEY,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    params = {
        "query": query_string,
        "orientation": "portrait" if not orientation_landscape else "landscape",
        "per_page": 15
    }

    response = requests.get(url, headers=headers, params=params)
    json_data = response.json()
    log_response(LOG_TYPE_PEXEL, query_string, response.json())

    return json_data


def getBestVideo(query_string, orientation_landscape=True, used_vids=[]):
    vids = search_videos(query_string, orientation_landscape)
    videos = vids['videos']  # Extract the videos list from JSON

    # Only accept videos with EXACT 9:16 aspect ratio and resolution of 1080x1920
    # Filter videos for portrait orientation with exact 1080x1920 resolution (aspect ratio 9:16)
    if not orientation_landscape:
        filtered_videos = [video for video in videos
                           if video['width'] == 1080 and video['height'] == 1920
                           and abs((video['height'] / video['width']) - (16/9)) < 0.001]  # Strict ratio check
                           and abs(video['height'] / video['width'] - 16/9) < 0.01]  # Allowing for floating-point precision
    else:
        filtered_videos = [video for video in videos
                           if video['width'] == 1920 and video['height'] == 1080
                           and abs((video['width'] / video['height']) - (16/9)) < 0.001]
                           and abs(video['width'] / video['height'] - 16/9) < 0.01]

    # Sort the filtered videos by duration in ascending order (closest to 15 seconds)
    sorted_videos = sorted(filtered_videos, key=lambda x: abs(15 - int(x['duration'])))

    # Extract the top available video's URL
    for video in sorted_videos:
        for video_file in video['video_files']:
            if not orientation_landscape:
                # For portrait videos (1080x1920)
                if video_file['width'] == 1080 and video_file['height'] == 1920:
                    if not (video_file['link'].split('.hd')[0] in used_vids):
                        return video_file['link']
            else:
                # For landscape videos (1920x1080)
                if video_file['width'] == 1920 and video_file['height'] == 1080:
                    if not (video_file['link'].split('.hd')[0] in used_vids):
                        return video_file['link']

    print("No full-size portrait videos found for this search query:", query_string)
    return None


def generate_video_url(timed_video_searches, video_server):
    timed_video_urls = []
    if video_server == "pexel":
        used_links = []
        for (t1, t2), search_terms in timed_video_searches:
            url = ""
            for query in search_terms:
                # Search for portrait-oriented videos
                url = getBestVideo(query, orientation_landscape=False, used_vids=used_links)
                if url:
                    used_links.append(url.split('.hd')[0])
                    break
            timed_video_urls.append([[t1, t2], url])
    elif video_server == "stable_diffusion":
        timed_video_urls = get_images_for_video(timed_video_searches)

    return timed_video_urls
