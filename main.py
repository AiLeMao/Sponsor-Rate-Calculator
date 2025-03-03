#init all the packages for basic function
from dotenv import load_dotenv
import os
import requests
#init all the scripts i've made
import yt_api
import yt_func
import tw_api

#loading api keys
load_dotenv("keys.env")
youtube_api_key = os.getenv("youtube_api_key")

#loading static values
load_dotenv("static_values.env")
#import all the static values from the static_values.env
yt_get_video_stats_scan_age = int(os.getenv("scan_age"))
yt_get_video_stats_min_videos = int(os.getenv("min_videos"))
yt_get_video_stats_max_videos = int(os.getenv("max_videos"))

yt_non_mid_roll_ads = float(os.getenv("non_mid_roll_ads"))
yt_mid_roll_threshold = float(os.getenv("mid_roll_threshold"))
yt_sec_per_midroll_ad = float(os.getenv("seconds_per_midroll_ad"))

yt_fresh_age = int(os.getenv("fresh_age"))
yt_fresh_threshold = float(os.getenv("fresh_threshold"))
yt_fresh_outlier_multiplier = float(os.getenv("fresh_outlier_multiplier"))

yt_sponsor_multiplier_integrated = float(os.getenv("yt_sponsor_multiplier_integrated"))
yt_sponsor_multiplier_dedicated = float(os.getenv("yt_sponsor_multiplier_dedicated"))
yt_outlier_range = float(os.getenv("yt_outlier_range"))


#dummy input master sections
#check what platform the info is for and run the corresponding platform functions
content_type = "twitch" 



#YOUTUBE LONGFORM INPUT GANG HERE
match content_type:
    case "videos":  # YouTube long-form videos

        #DUMMY INPUTS. FRONT END SHOULD HOOK UP HERE AT SOME POINT
        #DUMMY INPUTS. FRONT END SHOULD HOOK UP HERE AT SOME POINT

        yt_channel_rpm = 4.00 #temp value. replace later with ppls rpm in float[2]
        yt_identifier_input = os.getenv("test_input")#replace this with web input. for some reason this input is rly finicky on urls. Fix later
        #should be a checkbox input on website or something for content types

        #DUMMY INPUTS. FRONT END SHOULD HOOK UP HERE AT SOME POINT
        #DUMMY INPUTS. FRONT END SHOULD HOOK UP HERE AT SOME POINT


        #convert the input to get the full identifiers: 
        #THIS HAS A PROBLEM. NOT ALL URL TYPES CONVERT AND CLASSIFY PROPERLY. ONLY SPECIFIC ONES. FIX IT LATER!!!!!
        yt_identifier_array = yt_func.classify_youtube_input(yt_identifier_input)
        #THIS HAS A PROBLEM. NOT ALL URL TYPES CONVERT AND CLASSIFY PROPERLY. ONLY SPECIFIC ONES. FIX IT LATER!!!!!

        #use id from that to get id of playlists so we can call upon the right one later:
        yt_playlists = yt_func.get_playlists(yt_identifier_array["id"])

        #yt_api.get_video_stats(yt_playlist_id, scan_age=30, min_videos=10, max_videos=50)
        #get the list of the last relevant videos:
        recalled_videos = yt_api.get_video_stats(yt_playlists[content_type], yt_get_video_stats_scan_age, yt_get_video_stats_min_videos, yt_get_video_stats_max_videos)

        #video list, rpm given by user, avr ads pre/post roll combined, avr amt of seconds it takes to get a mid roll for videos longer than
        normalized_rpm = yt_func.normalize_rpm(recalled_videos, yt_channel_rpm, yt_non_mid_roll_ads, yt_mid_roll_threshold ,yt_sec_per_midroll_ad)

        #delet newest upload if it's not near peak views yet. This is after normalize rpm so it has a bit more data to work with
        updated_recalled_videos = yt_func.fresh_upload_killer(recalled_videos, yt_fresh_age, yt_fresh_threshold, yt_fresh_outlier_multiplier)

        #get the average views to prep for brand deal calc
        average_views = int(yt_func.get_avr_views(updated_recalled_videos))

        #take normalized rpm and get static value multiplier to convert to a real life sponsor cpm
        base_cpm_integrated = normalized_rpm * float(yt_sponsor_multiplier_integrated)
        base_cpm_dedicated = normalized_rpm * float(yt_sponsor_multiplier_dedicated)

        #convert sponsor cpm to amount it should sponsor for
        yt_integration = round(base_cpm_integrated * (average_views/1000), 2)
        yt_integration_min = round(yt_integration - (yt_integration * yt_outlier_range), 2)
        yt_integration_max = round(yt_integration + (yt_integration * yt_outlier_range), 2)
        
        yt_dedicated = round(base_cpm_dedicated * (average_views / 1000), 2)
        yt_dedicated_min = round(yt_dedicated - (yt_dedicated * yt_outlier_range), 2)
        yt_dedicated_max = round(yt_dedicated + (yt_dedicated * yt_outlier_range), 2)

        print(f"Integration: {yt_integration}\n Min: {yt_integration_min}\n Max: {yt_integration_max}\n Dedicated: {yt_dedicated}\n Min: {yt_dedicated_min}\n Max: {yt_dedicated_max}")

        #collect all the data for outputting into a single dict so it is easy to get out later... i hope
        yt_sponsor_rate_output = {
        "integration": yt_integration,
        "integration_min": yt_integration_min,
        "integration_max": yt_integration_max,
        "dedicated": yt_dedicated,
        "dedicated_min": yt_dedicated_min,
        "dedicated_max": yt_dedicated_max,
    }
        #debug chunk
        """
        for key, value in yt_sponsor_rate_output.items():
            print(f"{key}: {value}")
        """
   
    case "shorts":  # YouTube shorts
        pass

    case "streams":  # YouTube streams
        pass

    case "instagram":  # Instagram posts
        pass

    case "twitch":  # Twitch
        # DUMMY INPUTS
        tw_username = os.getenv("twitch_test_input")
        sponsor_margin = 0  # 0-1 how crazy a sponsor is. gambling and crypto is 1, low margin goods are 0

        # Set the values so I can use them in calcs later
        tw_ccv30 = tw_api.get_ccv_30(tw_username)
        
        # Check if tw_ccv30 is None
        if tw_ccv30 is None:
            print("Failed to retrieve average viewers. Going on with a fat ol 0. Do fix that habibi")
            tw_ccv30 = 0  

        tw_static_multi = float(os.getenv("tw_static_multiplier")) 
        tw_outlier_range = float(os.getenv("tw_outlier_range"))

        # Convert to sponsor rate/hr
        tw_sponsor_hourly = round(((1 + sponsor_margin) * tw_ccv30) * tw_static_multi, 2)
        tw_sponsor_hourly_min = round(tw_sponsor_hourly - (tw_sponsor_hourly * tw_outlier_range), 2)
        tw_sponsor_hourly_max = round(tw_sponsor_hourly + (tw_sponsor_hourly * tw_outlier_range), 2)

        tw_sponsor_hourly_output = {
            "sponsor_hourly": tw_sponsor_hourly,
            "sponsor_hourly_min": tw_sponsor_hourly_min,
            "sponsor_hourly_max": tw_sponsor_hourly_max,
        }

        #debug chunk
        """
        for key, value in tw_sponsor_hourly_output.items():
            print(f"{key}: {value}")
        """

    case "tiktok":  # TikTok videos
        pass

    case _:
        raise Exception("No valid content type found!")
    
