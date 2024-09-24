import os
import pandas as pd
from dotenv import load_dotenv
from googleapiclient.discovery import build
import string

# Load environment variables from a .env file
load_dotenv()

# Get YouTube API key from environment variable
API_KEY = os.getenv("YOUTUBE_API_KEY")
API_VERSION = 'v3'

# Initialize the YouTube API client
youtube = build('youtube', API_VERSION, developerKey=API_KEY)

def get_channel_stats(youtube, channel_id):
    """
    Retrieve statistics for a YouTube channel given its ID.

    Args:
    youtube (Resource): YouTube API resource object.
    channel_id (str): The ID of the YouTube channel.

    Returns:
    dict: A dictionary containing the channel's name, total subscribers, views, and videos.
          Returns None if the channel is not found.
    """
    # Request channel statistics from YouTube API
    request = youtube.channels().list(
        part='snippet, statistics',
        id=channel_id
    )
    response = request.execute()

    # Check if the response contains channel information
    if response['items']:
        # Extract relevant data from the API response
        data = {
            'channel_name': response['items'][0]['snippet']['title'],
            'total_subscribers': response['items'][0]['statistics']['subscriberCount'],
            'total_views': response['items'][0]['statistics']['viewCount'],
            'total_videos': response['items'][0]['statistics']['videoCount'],
        }
        return data
    else:
        return None  # Return None if channel is not found

def get_channel_id(api_key, channel_name):
    """
    Get the Channel ID from the YouTube Channel name using YouTube Data API.

    Args:
    api_key (str): Your YouTube Data API v3 key.
    channel_name (str): The display name of the YouTube channel.

    Returns:
    str: The Channel ID of the YouTube channel, or None if not found.
    """
    # Create a resource object for interacting with the YouTube API
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    # Search for the channel by name
    request = youtube.search().list(
        part='snippet',
        q=channel_name,  # The channel name to search for
        type='channel',  # Limit search results to channels
        maxResults=1     # Only get one result
    )
    
    # Execute the request and get the response
    response = request.execute()
    
    # Check if the response contains any channels
    if 'items' in response and len(response['items']) > 0:
        channel_id = response['items'][0]['snippet']['channelId']
        return channel_id
    else:
        return None  # Return None if no channel is found

def check_string(s):
    """
    Check if the string contains only letters or only numbers,
    or if the length of the string is not 24 characters.

    Args:
    s (str): The string to check.

    Returns:
    bool: True if the string contains only letters or only numbers,
          or if its length is not 24 characters. False otherwise.
    """
    # Check if the length is not 24 characters
    if len(s) != 24:
        return True

    # Check for letters and numbers in the string
    has_letters = any(c in string.ascii_letters for c in s)
    has_numbers = any(c in string.digits for c in s)
    
    # Return True if the string contains only letters or only numbers, False otherwise
    return (has_letters and not has_numbers) or (has_numbers and not has_letters)


# Extract unique channel IDs from the 'NOMBRE' column by splitting on '@'
channel_ids = df['NOMBRE'].str.split('@').str[-1].unique()

# Initialize a list to keep track of channel stats
channel_stats = []

# Loop over the channel IDs and get stats for each
for channel_id in channel_ids:
    # Check if the channel ID is valid (not just letters or numbers)
    if check_string(channel_id):
        # If invalid, retrieve the actual channel ID using the YouTube API
        channel_id = get_channel_id(API_KEY, channel_id)
    
    # Fetch the channel statistics
    stats = get_channel_stats(youtube, channel_id)
    
    # If stats are found, append to the stats list
    if stats is not None:
        channel_stats.append(stats)

# Convert the list of channel statistics to a DataFrame
stats_df = pd.DataFrame(channel_stats)

# Reset the index of the original and stats DataFrames to prepare for concatenation
df.reset_index(drop=True, inplace=True)
stats_df.reset_index(drop=True, inplace=True)

# Concatenate the original DataFrame and the stats DataFrame horizontally
combined_df = pd.concat([df, stats_df], axis=1)

# Optionally, you can drop the 'channel_name' column if it's redundant
# combined_df.drop('channel_name', axis=1, inplace=True)

# Save the merged DataFrame to a CSV file
combined_df.to_csv('updated_youtube_data_uk.csv', index=False)


