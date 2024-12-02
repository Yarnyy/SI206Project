import requests
import json

API_KEY = 'AIzaSyAjHvWlEotJy5MVqi4WBX6iPRzQYivcY44'
SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'
VIDEOS_URL = 'https://www.googleapis.com/youtube/v3/videos'

def search_music_videos(api_key, query, region_code='US'):
    search_params = {
        'part': 'snippet',
        'q': 'music',
        'type': 'video',
        'videoCategoryId': '10',
        'regionCode': region_code,
        'key': api_key,
        'maxResults': 5  
    }

    try:
        response = requests.get(SEARCH_URL, params=search_params).json()
    except:
        return 'GET Response Error'
    
    return response

def get_video_details(api_key, video_ids):
    video_params = {
        'part': 'snippet,statistics',
        'id': ','.join(video_ids),
        'key': api_key
    }  

    try:
        response = requests.get(VIDEOS_URL, params=video_params).json()
    except:
        return 'GET Response Error'

    return response

def main():
    query = 'poker face'
    region_code = 'US'

    search_response = search_music_videos(API_KEY, query, region_code)
    video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]

    video_details = get_video_details(API_KEY, video_ids)

    # Write output to JSON
    with open('output.json', 'w') as f:
        json.dump(video_details, f, indent=2)

    # TODO: Convert JSON to SQL database file

if __name__ == "__main__":
    main()