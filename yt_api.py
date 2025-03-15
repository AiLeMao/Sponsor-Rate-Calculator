import os #file browser type beat
import requests #this one is for requesting stuff but i forgot
from datetime import datetime, timedelta #for the age comparison
import re

import isodate  # For parsing ISO 8601 duration format for video duration to second stuff

from dotenv import load_dotenv #make .env files importable and import em
load_dotenv("keys.env")
youtube_api_key = os.getenv("youtube_api_key")

#-----------------------------------------------------------------------------------------------------------------------------

#call for subscriber count from handle. Probably get it from other stuff too later. but handle is fine right now
#no need to bloat the code like crazy for other methods
def yt_get_subscribers_from_handle(yt_channel_handle):
    yt_channel_id = yt_get_channel_id_from_url(yt_channel_handle)
    url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={yt_channel_id}&key={youtube_api_key}"
    subscriber_data = requests.get(url).json()
    return subscriber_data["items"][0]["statistics"]["subscriberCount"]

#----------------------------------------------------------------------------------------------------------------------------

#big ol block to get api calls and stuff to get the id, channel url and handle functions so its not terrible to deal with in main
# Get handle from URL

def yt_get_channel_handle_from_url(yt_channel_url):
    """
    Extracts the YouTube channel handle from a given URL.
    Supports:
    - Standard YouTube URLs (e.g., https://www.youtube.com/@handle, https://www.youtube.com/channel/UCxxx)
    - Mobile YouTube URLs (e.g., https://m.youtube.com/@handle)
    - Handle-only URLs (e.g., https://www.youtube.com/@handle)
    """
    # Regex patterns for different URL formats
    handle_pattern = re.compile(r"(?:https?:\/\/)?(?:www\.|m\.)?youtube\.com\/(?:@|channel\/|c\/)?([^\/\?]+)")
    short_url_pattern = re.compile(r"(?:https?:\/\/)?youtu\.be\/([^\/\?]+)")

    # Handle standard and mobile YouTube URLs (e.g., https://www.youtube.com/@handle, https://m.youtube.com/@handle)
    handle_match = handle_pattern.search(yt_channel_url)
    if handle_match:
        handle = handle_match.group(1)
        if handle.startswith("@"):
            handle = handle[1:]  # Remove "@" for consistency
        return handle

    # If no valid format is found, raise an error
    raise ValueError("Invalid YouTube URL format.")

#Get channel ID from URL
def yt_get_channel_id_from_url(yt_channel_url):
    if "youtube.com" or "youtu.be" in yt_channel_url:
        if "/@" in yt_channel_url:
            handle = yt_channel_url.split("/@")[-1].split("/")[0]
        elif "/channel/" in yt_channel_url:
            return yt_channel_url.split("channel/")[-1].split("/")[0]
        elif "/c/" in yt_channel_url:
            return yt_channel_url.split("channel/")[-1].split("/")[0]
        else:
            raise ValueError("Invalid YouTube URL format.")
    else:
        handle = yt_channel_url.lstrip("@")

    # Get Channel ID from handle
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={handle}&type=channel&key={youtube_api_key}"
    response = requests.get(url).json()

    if "items" not in response or not response["items"]:
        raise ValueError("Channel not found. Check the handle or API key.")

    return response["items"][0]["snippet"]["channelId"]

#Get channel ID from handle:
def yt_get_channel_id_from_handle(yt_channel_handle):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={yt_channel_handle}&type=channel&key={youtube_api_key}"
    response = requests.get(url).json()

    if "items" not in response or not response["items"]:
        raise ValueError("Channel not found. Check the handle or API key.")

    return response["items"][0]["snippet"]["channelId"]

#Get channel url from handle
def yt_get_channel_url_from_handle(yt_channel_handle):
    # Strip leading/trailing spaces and any leading @
    handle = yt_channel_handle.strip().lstrip("@")
    return f"https://www.youtube.com/{handle}"

#Get channel url from channel ID
def yt_get_channel_url_from_id(yt_channel_id):
    url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet&id={yt_channel_id}&key={youtube_api_key}"
    response = requests.get(url).json()

    if "items" not in response or not response["items"]:
        raise ValueError("Channel not found. Check the channel ID or API stuff.")

    # Get customUrl or default to the channel URL
    channel_data = response["items"][0]["snippet"]
    custom_url = channel_data.get("customUrl")

    if custom_url:
        # Strip the @ sign and construct the URL
        handle = custom_url.lstrip("@")
        return f"https://www.youtube.com/{handle}"
    else:
        # Fallback to channel ID
        return f"https://www.youtube.com/channel/{yt_channel_id}"


"""
url -> handle
url -> id

handle -> id
handle -> url

id -> url




"""
#--------------------------------------------------------------------------------------------------------------------------
"""
get last 30 videos if they are recent. otherwise settle for last 10
inputs:
playlist id to get the thing u want.
scan age: default desired age where it'll stop if it goes above min_videos count
min_videos: the amount of videos it'll grab at minimum to get a good sample size regardless of video age. This will override video age
max_videos: just to make sure this bad boy doesn't grab too much info

should output if data is reliable as boolean and a listy boy with the id, views and age

this is way above my head. this is sponsored by deepseek with minor tweaks to ensure its not too ass. 
Lets hope it stays functional and I never have to tweak this
"""

def get_video_stats(yt_playlist_id, scan_age=30, min_videos=3, max_videos=50):
    if not yt_playlist_id.startswith(("UC", "UU", "UUSH", "UULV", "UULF", "UULP", "UUPS", "UUPV", "UUMO", "UUMF", "UUMS", "UUMV")):
        raise ValueError("Invalid playlist ID. Playlist IDs must start with a valid prefix.")

    video_stats = []
    current_date = datetime.utcnow()
    next_page_token = None
    total_fetched = 0

    while True:
        # Fetch video details from the playlist
        url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet,contentDetails&playlistId={yt_playlist_id}&maxResults=50&key={youtube_api_key}"
        if next_page_token:
            url += f"&pageToken={next_page_token}"
        
        try:
            response = requests.get(url).json()
        except requests.RequestException as e:
            raise ValueError(f"API request failed: {e}")

        if "error" in response:
            raise ValueError(f"API Error: {response['error']['message']}")

        if "items" not in response or not response["items"]:
            break

        # Extract video IDs for batch statistics retrieval
        video_ids = [item["contentDetails"]["videoId"] for item in response["items"]]
        stats_url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics,contentDetails&id={','.join(video_ids)}&key={youtube_api_key}"
        stats_response = requests.get(stats_url).json()
        
        # Map video stats by ID
        video_stats_map = {
            item["id"]: {
                "view_count": int(item["statistics"].get("viewCount", 0)),
                "duration": item["contentDetails"].get("duration", "PT0S"),  # Default to 0 seconds
            }
            for item in stats_response.get("items", [])
        }

        # Process video details
        for item in response["items"]:
            video_id = item["contentDetails"]["videoId"]
            view_count = video_stats_map.get(video_id, {}).get("view_count", 0)
            duration = video_stats_map.get(video_id, {}).get("duration", "PT0S")
            upload_date_str = item["snippet"].get("publishedAt", "Unknown")
            upload_date = datetime.strptime(upload_date_str, "%Y-%m-%dT%H:%M:%SZ")
            video_age = (current_date - upload_date).days

            # Parse duration (ISO 8601 format) into seconds and convert to int
            video_length = isodate.parse_duration(duration).total_seconds()

            video_stats.append({
                "video_id": video_id,
                "view_count": view_count,
                "video_age": video_age,
                "video_length": int(video_length),  # Video length in seconds (as int)
            })

            total_fetched += 1
            if total_fetched >= max_videos:
                break

        if total_fetched >= max_videos:
            break

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    # Filter videos within scan_age and ensure min_videos
    filtered_videos = []
    for video in video_stats:
        if video["video_age"] <= scan_age:
            filtered_videos.append(video)
        elif len(filtered_videos) < min_videos:
            filtered_videos.append(video)
        else:
            break
    
    # Sort videos by upload date (newest to oldest)
    video_stats.sort(key=lambda x: x["video_age"], reverse=False)

    reliable_data = len(filtered_videos) >= min_videos

    return {
        "videos": filtered_videos,
        "reliable_data": reliable_data,
    }


#-------------------------------------------------------------------------------------------------------------------------
