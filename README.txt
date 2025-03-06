Take in social media identification input. 
Automatically seach up their content and make a calculation what the value of an ad on their channel is.
Static values not included at the moment 'cause it has a bunch of test inputs that are against github privacy TOS.

Requirements for inputs:
Youtube: RPM + channel identification (url, tag or channel ID)
Twitch: channel identification (url or name)
TikTok: channel identification (url or name) + something to figure out what niche they are in. tracking hashtags in a huge dynamic database will be super out of scope
Insta: channel identification (url or exact tag, maybe search by name?)+ something to figure out what niche they are in. tracking hashtags in a huge dynamic database will be super out of scope


Done:
    -youtube longform
    -twitch

todo list:
    -fix url inputs so all types of urls work, not just the specific 2 for youtube stuff
    -obtain data to get proper multipliers and ad counts so static values are accurate
    
        
    -add youtube short functionality
    -add youtube streams functionality
    -add tiktok functionality? How the heckles do u even api that????
    -add instagram functionality? How dahecc do u even api that

    -Get some sort of front end somehow on some website so people can give inputs
    -unhide static_values.env without breaking TOS once website is done