import os
import requests
from utility.utils import log_response, LOG_TYPE_PEXEL

# Fetching Pexels API Key from environment variable
PEXELS_API_KEY = os.environ.get('PEXELS_KEY')
if not PEXELS_API_KEY:
    raise ValueError("PEXELS_KEY environment variable not set.")

def search_videos(query_string, orientation_landscape=True):
    url = "https://api.pexels.com/videos/search"
    headers = {
        "Authorization": PEXELS_API_KEY,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    params = {
        "query": query_string,
        "orientation": "landscape" if orientation_landscape else "portrait",
        "per_page": 15
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Error fetching videos: {response.status_code}, {response.text}")
        return None
    
    json_data = response.json()
    log_response(LOG_TYPE_PEXEL, query_string, json_data)
    return json_data

def getBestVideo(query_string, orientation_landscape=True, used_vids=[]):
    vids = search_videos(query_string, orientation_landscape)
    if vids is None or 'videos' not in vids:
        print("No videos found or error occurred.")
        return None

    videos = vids['videos']

    # Filter and extract videos with specified dimensions
    if orientation_landscape:
        filtered_videos = [
            video for video in videos
            if video['width'] >= 1920 and video['height'] >= 1080 and
            1.77 <= video['width'] / video['height'] <= 1.79
        ]
    else:
        filtered_videos = [
            video for video in videos
            if video['width'] >= 1080 and video['height'] >= 1920 and
            1.77 <= video['height'] / video['width'] <= 1.79
        ]

    # Sort the filtered videos by duration in ascending order
    sorted_videos = sorted(filtered_videos, key=lambda x: abs(15 - int(x['duration'])))

    # Extract the top video URLs
    for video in sorted_videos:
        for video_file in video['video_files']:
            if ((orientation_landscape and video_file['width'] == 1920 and video_file['height'] == 1080) or
                (not orientation_landscape and video_file['width'] == 1080 and video_file['height'] == 1920)):
                link = video_file['link'].split('.hd')[0]
                if link not in used_vids:
                    used_vids.append(link)
                    return video_file['link']
    
    print("NO LINKS found for this round of search with query:", query_string)
    return None

def generate_video_url(timed_video_searches, video_server):
    timed_video_urls = []
    if video_server == "pexel":
        used_links = []
        for (t1, t2), search_terms in timed_video_searches:
            url = ""
            for query in search_terms:
                url = getBestVideo(query, orientation_landscape=True, used_vids=used_links)
                if url:
                    used_links.append(url.split('.hd')[0])
                    break
            timed_video_urls.append([[t1, t2], url])
    elif video_server == "stable_diffusion":
        timed_video_urls = get_images_for_video(timed_video_searches)

    return timed_video_urls

