import yt_api
import re

#-------------------------------------------------------------------------------------------------------------------------
"""
how do i filter the yt url from tag and id?
url: if contains youtube.com
id: if contains UC and is specific length???

example handles to check for length and characters
    UCQeRaTukNYft1_6AZPACnog
    UC-oYqxpi6TO1J7BjQksSuOA
    UC5hH5NN26s92Qro_ZFWl8cQ
        length 24, a to z, A to Z, 0 to 9, - , _

remove spaces at the end cuz chatgpt is smart and i forgot about that
if contains youtube.com -> url
elif string starting with "@" -> handle
elif starts with UC and is 24 characters long AND does not contain " " -> id
else -> handle
"""
#get input to populate the channel url, id and handle
#output 
# handle, 
# url, 
# id

def classify_youtube_input(yt_identifier_input):
    try:
        # Strip and validate input
        yt_identifier_input = yt_identifier_input.strip()
        if not yt_identifier_input:
            raise ValueError("Input cannot be empty.")

        # Regex patterns for different URL formats
        handle_pattern = r"https?://(?:www\.)?youtube\.com/(?:@|channel/|c/)([^/]+)"
        channel_id_pattern = r"https?://(?:www\.)?youtube\.com/channel/(UC[\w-]{22})"

        # Helper function to construct the return dictionary
        def build_result(handle, url, id):
            return {
                "handle": handle,
                "url": url,
                "id": id
            }

        # Check if input is a URL
        if "youtube.com" in yt_identifier_input or "youtu.be" in yt_identifier_input:
            # Handle-based URLs (e.g., @ying_verse, channel/@ying_verse, c/ying_verse)
            handle_match = re.search(handle_pattern, yt_identifier_input)
            if handle_match:
                handle = handle_match.group(1)
                if handle.startswith("@"):
                    handle = handle[1:]  # Remove "@" for consistency
                return build_result(
                    handle=f"@{handle}",
                    url=yt_identifier_input,
                    id=yt_api.yt_get_channel_id_from_handle(handle)
                )

            # Channel ID-based URLs (e.g., channel/UCdwCJM5ScKKKW7dQmDUIIdA)
            channel_id_match = re.search(channel_id_pattern, yt_identifier_input)
            if channel_id_match:
                channel_id = channel_id_match.group(1)
                return build_result(
                    handle=yt_api.yt_get_channel_handle_from_id(channel_id),
                    url=yt_identifier_input,
                    id=channel_id
                )

        # Handle inputs that are not URLs
        elif yt_identifier_input.startswith("@"):  # Input is a handle
            handle = yt_identifier_input[1:]  # Remove "@"
            return build_result(
                handle=yt_identifier_input,
                url=yt_api.yt_get_channel_url_from_handle(handle),
                id=yt_api.yt_get_channel_id_from_handle(handle)
            )

        elif yt_identifier_input.startswith("UC") and re.fullmatch(r"UC[\w-]{22}", yt_identifier_input):  # Input is a channel ID
            return build_result(
                handle=yt_api.yt_get_channel_handle_from_id(yt_identifier_input),
                url=yt_api.yt_get_channel_url_from_id(yt_identifier_input),
                id=yt_identifier_input
            )

        else:  # Assume input is a handle (without "@")
            return build_result(
                handle=f"@{yt_identifier_input}",
                url=yt_api.yt_get_channel_url_from_handle(yt_identifier_input),
                id=yt_api.yt_get_channel_id_from_handle(yt_identifier_input)
            )

    except Exception as e:
        # Handle any unexpected errors
        print(f"Error processing input: {e}")
        return None

#-------------------------------------------------------------------------------------------------------------------------
#turn channel ID into all the prefix IDs for each type of content:

def get_playlists(yt_channel_id):

    if not yt_channel_id.startswith("UC"):
        raise ValueError("Channel ID did not start with 'UC'. You did something wrong.")

    #yt_videos_id = "UULF" + yt_channel_id[2:]
    #yt_shorts_id = "UUSH" + yt_channel_id[2:]
    #yt_streams_id = "UULV" + yt_channel_id[2:]
    #yt_popular_videos_id = "UULP" + yt_channel_id[2:]
    #yt_popular_shorts_id = "UUPS" + yt_channel_id[2:]
    #yt_popular_streams_id = "UUPV" + yt_channel_id[2:]
    #yt_member_all = "UUMO" + yt_channel_id[2:]
    #yt_member_video = "UUMF" + yt_channel_id[2:]
    #yt_member_shorts = "UUMS" + yt_channel_id[2:]
    #yt_member_streams = "UUMV" + yt_channel_id[2:]

    return {
        "videos": "UULF" + yt_channel_id[2:],
        "shorts": "UUSH" + yt_channel_id[2:],
        "streams": "UULV" + yt_channel_id[2:], 
        "popular_videos": "UULP" + yt_channel_id[2:], 
        "popular_shorts": "UUPS" + yt_channel_id[2:], 
        "popular_streams": "UUPV" + yt_channel_id[2:],
        "members_all": "UUMO" + yt_channel_id[2:],  
        "members_videos": "UUMF" + yt_channel_id[2:], 
        "members_shorts": "UUMS" + yt_channel_id[2:], 
        "members_streams": "UUMV" + yt_channel_id[2:],  
        }




#---------------------------------------------------------------------------------------------------------
#just kill any upload that is below age old and scores threhold amount under median views in the entire measured list of videos
#shoutouts deepseek for figuring out this mental gymnastic puzzle of getting outliers out of the data so it doesnt auto kill stuff that it shouldnt

def fresh_upload_killer(video_data, age=7, threshold=0.7, outlier_multiplier=3):
    # Step 1: Loop to remove all top outliers
    while True:
        # Calculate the current median
        view_counts = [video["view_count"] for video in video_data["videos"]]
        view_counts_sorted = sorted(view_counts)
        median_index = len(view_counts_sorted) // 2
        median_view_count = view_counts_sorted[median_index]

        # Check if the top video is an outlier
        if len(view_counts_sorted) >= 3:  # Only check for outliers if there are at least 3 videos
            top_video = video_data["videos"][0]  # The first video is the youngest
            if top_video["view_count"] > outlier_multiplier * median_view_count:
                # Remove the top video if it's an outlier
                video_data["videos"].pop(0)
                continue  # Recheck for more outliers
            else:
                break  # No more outliers, exit the loop
        else:
            break  # Not enough videos to check for outliers

    # Step 2: Check the youngest video (after removing all outliers)
    youngest_video = video_data["videos"][0]
    is_young = youngest_video["video_age"] < age
    is_low_performing = youngest_video["view_count"] < threshold * median_view_count

    # Step 3: Remove the youngest video if it meets the condition
    if is_young and is_low_performing:
        video_data["videos"].pop(0)  # Remove the first video (youngest)

    # Step 4: Return the modified or unmodified list
    return video_data

#____________________________________________________________________________________________________________
#get those average views bro
def get_avr_views(video_data):
    # Step 1: Extract view counts from the video list
    view_counts = [video["view_count"] for video in video_data["videos"]]

    # Step 2: Calculate the average
    if view_counts:  # Ensure the list is not empty
        average_views = sum(view_counts) / len(view_counts)
    else:
        average_views = 0  # Return 0 if the list is empty

    # Step 3: Return the average
    return average_views



#____________________________________________________________________________________________________________
#function to spit out avr or median views. gotta figure this out what is more consistent. 
#need to cull poor performant videos with less than 7 day upload time but only if they are 30% below median or something



def yt_sponsor_longform(yt_playlist_handle,yt_rpm):
    pass
#reliable_data = True
#get list of videos of last 30 uploads
#if less than 3 uploads:  set reliable_data = False
#repeat over list and kill old videos until you hit 3 videos or get to video age of 45 days
#if more than 4 videos left: check if there's any videos with less than 7 days upload time
#make a temp avr to compare new videos to
#if video age < 7 days AND views are far off median, kill that video from the list
#set new average and median based on remainder videos

#something something rpm

#return  price,reliable_data



#----------------------------------------------------------------------------------------------------------------------------

#Normalizing the rpm based on the estimated ads playing on average
def normalize_rpm(video_data, rpm, non_mid_roll_ads=2.0,midroll_threshold=480, seconds_per_mid_roll_ad=540.0):
    
    # Define the calculate_normalized_rpm function
    def calculate_normalized_rpm(video_length, rpm, non_mid_roll_ads, seconds_per_mid_roll_ad):
        """
        Calculate the normalized RPM for a single video.

        Args:
            video_length (float): Length of the video in seconds.
            rpm (float): Base RPM provided by the user.
            non_mid_roll_ads (float): Average non-mid-roll ads (pre + post).
            seconds_per_mid_roll_ad (float): Average seconds between mid-roll ads.

        Returns:
            float: Normalized RPM for the video.
        """
        if video_length <= midroll_threshold:
            mid_roll_ads = 0.0
        else:  # Videos over threshold
            mid_roll_ads = (video_length - midroll_threshold) / seconds_per_mid_roll_ad

        total_ads = non_mid_roll_ads + mid_roll_ads
        revenue_per_ad = rpm / total_ads
        normalized_rpm = revenue_per_ad * non_mid_roll_ads
        return round(normalized_rpm, 2)

    # Extract videos from video_data
    videos = video_data.get("videos", [])  # Only use the "videos" list
    total_normalized_rpm = 0.0
    num_videos = len(videos)  # Length of the "videos" list (ignores "reliable_data")

    # Calculate normalized RPM for each video
    for video in videos:
        video_length = video.get("video_length", 0)  # Get video length in seconds
        if video_length <= 0:
            continue  # Skip invalid video lengths

        # Calculate normalized RPM for this video
        normalized_rpm = calculate_normalized_rpm(
            video_length, 
            rpm,
            non_mid_roll_ads,
            seconds_per_mid_roll_ad
        )
        total_normalized_rpm += normalized_rpm

    # Calculate average normalized RPM
    if num_videos > 0:
        channel_value_score = total_normalized_rpm / num_videos
    else:
        channel_value_score = 0.0

    return round(channel_value_score, 2)

#----------------------------------------------------------------------------------------------------------------------------