import os
import re
import threading
import subprocess
import telebot
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import googleapiclient.http
from google.oauth2.credentials import Credentials
from flask import Flask, request

# Telegram bot token
API_TOKEN = '7461482650:AAF0dme5l8NQX4W0wHXk172o29JqBnTVE0I'

# YouTube API scopes and token file
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_FILE = 'token.json'

# Use the client file you uploaded
CLIENT_SECRETS_FILE = "client.json"

# Create a TeleBot instance
bot = telebot.TeleBot(API_TOKEN)

# Flask app setup
app = Flask(__name__)

# Authenticate YouTube
def authenticate_youtube():
    if os.path.exists(TOKEN_FILE):
        credentials = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    else:
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, SCOPES)
        
        # Set the redirect URI to your VPS domain
        flow.redirect_uri = "http://freegiftgamed.in/oauth2callback"
        
        auth_url, _ = flow.authorization_url(prompt='consent')
        print(f"Please go to this URL and authorize the application: {auth_url}")
        
        # This assumes you're able to handle the callback on your server
        code = input("Enter the authorization code: ")
        flow.fetch_token(code=code)
        
        credentials = flow.credentials

        with open(TOKEN_FILE, 'w') as token:
            token.write(credentials.to_json())

    youtube = googleapiclient.discovery.build(
        "youtube", "v3", credentials=credentials)

    return youtube

# Telegram bot commands
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Use /link to authorize the bot with your YouTube account.")

@bot.message_handler(commands=['link'])
def send_auth_link(message):
    if os.path.exists(TOKEN_FILE):
        bot.reply_to(message, "You have already authorized the bot. You can now upload videos by sending them here.")
    else:
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, SCOPES)
        flow.redirect_uri = "http://freegiftgamed.in/oauth2callback"
        auth_url, _ = flow.authorization_url(prompt='consent')
        
        bot.reply_to(message, f"Authorize this application by visiting this link: {auth_url}")



@bot.message_handler(content_types=['video'])
def handle_video(message):
    if not os.path.exists(TOKEN_FILE):
        bot.reply_to(message, "Please authorize the bot first using /link.")
        return

    youtube = authenticate_youtube()

    # Download the video
    video_file_info = bot.get_file(message.video.file_id)
    video_file_path = bot.download_file(video_file_info.file_path)
    original_video_name = "uploaded_video.mp4"

    with open(original_video_name, 'wb') as video_file:
        video_file.write(video_file_path)

    # Check the video's resolution and aspect ratio
    probe = subprocess.run(
        ['ffmpeg', '-i', original_video_name],
        capture_output=True,
        text=True
    )

    # Extract video width and height from ffmpeg output
    resolution = None
    for line in probe.stderr.split('\n'):
        if 'Video:' in line:
            resolution_match = re.search(r'(\d+)x(\d+)', line)
            if resolution_match:
                width, height = map(int, resolution_match.groups())
                aspect_ratio = width / height
                break

    # If the video is not vertical, re-encode it
    reencoded_file_name = "reencoded_video.mp4"
    
    if resolution is None or aspect_ratio != 9 / 16:
        # Delete the existing file if it exists
        if os.path.exists(reencoded_file_name):
            os.remove(reencoded_file_name)

        command = [
            'ffmpeg',
            '-i', original_video_name,
            '-c:v', 'libx264',
            '-preset', 'slow',
            '-crf', '18',  # Adjust this for desired quality
            '-vf', 'scale=1080:1920',  # Ensure it's in the correct resolution for Shorts
            '-c:a', 'aac',
            '-b:a', '128k',
            reencoded_file_name
        ]
        subprocess.run(command, check=True)
    
    video_file_to_upload = reencoded_file_name if os.path.exists(reencoded_file_name) else original_video_name

    # Upload the video as a YouTube Short
    request_body = {
        "snippet": {
            "categoryId": "22",
            "title": "Top Trending 🔥 Instagram Reels Videos | All Famous Tik Tok Star💞Today Viral Insta Reels |nsta Reels",
            "description": """New Tik tok video 
            
Inst Reel Video 
Trending reels hot Videos
Couple Videos" "Tiktok Romantic Cute Couple Goals "Videos 2022 | Cute Romantic Bf Gf Goalsgg

#couplegoals #relationshipgoals #coupledialouge

Cute & Romantic Tik Tok Videos  Sad Tik Tok Videos  "Tik Tok Videos" || TikTok viral video #couplegoals #relationshipgoals #coupledialouge

Today New Latest Heart Broken Romantic Shayari, Love Shayaril #Bewafaishayari #Loveshayari #Attitudeshayari

Sad Shayari,

New Trending Instagram Reels Videos | All Famous TikTok Star | Today Viral Insta Reels | Insta Reels #instareels #ViralReels

#newtrendinginstagramreelsvideos #newinstareels #instagramreels

Raataan Lambiyan - Official Video | Shershaah |

Sidharth - Kiara | Tanishk B| Jubin Nautiyal | Asees

Breakup Tik Tok Videos  Sad Tik Tok Videos  "Tik Tok Videos" || TikTok viral video #couplegoals #relationshipgoals #coupledialouge

New Tiktok Funny &amp; Attitude Videos Of Jannat Zubair, Mr. Faisu, Riyaz Aly, Arishfa Khan, Beauty Khan #kdattitudeking #kd #attitude

Girls Dhamal Tiktok Videos Best Trending Videos

viral Girls Full Videos #MrSwagxx #faishumusically #awejmusically

Filhaal2 Mohabbat | Akshay Kumar Ft Nupur Sanon | Ammy Virk | B Praak | Jaani | Arvindr Khaira #newsong #ankitdancer #shentertainment #latestsongs

#pushpa #ooantavaooantava

Tags Star :- #cuty_beauty_khan #tanujsindhwani #dancewithalishaa #mukulgain #ashwinishinde #muskan_kalra01 #muskankalra #sonadey #beautykhan #praven1921 #ammye1921 #anjali #anialicnoba #JannatZubair #cunainathakur #Alia

#Kareenakapoor #Taimur Ali Khan #SohaAlikhan #KarismaKapoor #Anushka Sharma #Virat Kohli #Sharukh Khan #Twin Melody #Avneet Kaur #GimaAshi #MrFaisu #AwezDarbar #NagmaMirajkar #VitastaBhat #Fizuliyat

#DishaMadan #UnnathiMalharkar #anushkasen

#shravankumar #princekumar #udayandarun

#arishfakhan #india

new dance video,new song,new song 2022,new hindi song,hindi song,new punjabi song,new punjabi song 2022,hindi dj

song,new,dance,video,song,hindi,punjabi,2022,t series,t series new song,new Song dance video,tik tok,tik tok video,romantic tik tok,romantic,tik tok dance,tik tok dance video,dance video tik tok,best Dancer, Dancer, Viral Dance Video,set india,india's best dancer,#dance,#video ,#dancevideo,#india,jannat zubair,jannat,jannat zubair new song,

#tiktok #tseries #zeemusiccompany #zeemusicindia #set #setindia #badshah #yoyohoneysingh #dancevideo #saregamamusic #dm #dmdesimelodies #adityamusic #sony #sonymusic #sonymusicindia

#surajpalsingh #heroindori #divyakhoslakumar #faizelsiddiqui #aashikabhatia #khusipanjaban #restykamboj #dreamgirl #amitbachi #nitashilimkar #iamgajraj #bhavin #vishalpanday #surbhirathor #deepikapilli #shivamsingh #premvats #abrazkhan #khansufiyan #anjaliarora #ayushyadav #aamir #mohaknarang #neetubisht #himachalwalibeauty #lastminute #sofiaansari #khusipanjaban #Rjkevar #nawajorigankevar #hkadmoy arishfakhan #arishfakhantiktok #tiktokcouplegoals #musicallycouplegoals #couplegoals #cutecouples #tiktokcouples #relationshipgoals #Awez #musically #bestduets #famoustiktokers #tiktokindia #tiktok #tiktokfamoussong #BeautyHighlightsPlus cutestcouple #bae goals #mostpopularvideosontiktok #vigovideo #vigovideocomedy #musically #Tiktoktrending #faiusnewtoday #comedykingmillionscreation #chimkandi""",
            "tags": ["reel", "new reels", "instagram reels", "reels videos", "reels", "Anushkan sen", "Anushkan sen Instagram Reels", "Anushkan sen top Video", "Anushkan sen new reels", "Anushkan sen hot video", "Anushkan inst live video", "Anushkan Short reels", "Anushkan Sen top trending video", "Anushkan Sen viral", "YouTube Tag", "YouTube Tag Extractor", "YouTube Tag", "YouTube", "Video", "Video Tag Extractor"],
            "shorts": True  # Indicates that this is a YouTube Short
        },
        "status": {
            "privacyStatus": "public"  # Set the video to public
        }
    }

    media_file = googleapiclient.http.MediaFileUpload(video_file_to_upload, chunksize=10 * 1024 * 1024, resumable=True)

    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media_file
    )

    response = None

    while response is None:
        status, response = request.next_chunk()
        if status:
            bot.reply_to(message, f"Upload {int(status.progress() * 100)}% complete")

    bot.reply_to(message, f"Video uploaded successfully as a YouTube Short with ID: {response['id']}")


# Flask routes
@app.route('/')
def index():
    return "Welcome to the OAuth2 Callback Test!"

@app.route('/oauth2callback')
def oauth2callback():
    code = request.args.get('code')
    if code:
        # Exchange the authorization code for credentials
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, SCOPES)
        flow.redirect_uri = "http://freegiftgamed.in/oauth2callback"
        flow.fetch_token(code=code)

        credentials = flow.credentials

        with open(TOKEN_FILE, 'w') as token:
            token.write(credentials.to_json())

        return "Authorization complete! You can now use the bot to upload videos."
    else:
        return "No authorization code found."

# Function to run the bot
def run_bot():
    bot.polling()

if __name__ == "__main__":
    # Start the bot in a separate thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    # Start the Flask app
    app.run(host='0.0.0.0', port=80)








