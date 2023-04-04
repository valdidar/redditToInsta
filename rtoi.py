import shutil
from instabot import Bot
import os
import requests
import glob
import time
from tqdm import tqdm

# Define the subreddit and API endpoint
subreddit = "memes"
api_endpoint = "https://www.reddit.com/r/{}/top/.json?count=10".format(subreddit)

# Set the user-agent for the API request (required by Reddit API)
headers = {"User-Agent": "Top 10 Memes Downloader"}

# Make the API request to get the top 10 memes
response = requests.get(api_endpoint, headers=headers)

# Parse the JSON response and extract the image URLs and titles of the top 10 memes
top_memes = response.json()["data"]["children"]
image_urls = [meme["data"]["url_overridden_by_dest"] for meme in top_memes]
titles = [meme["data"]["title"] for meme in top_memes]

# Create the 'memes' directory if it doesn't exist
if not os.path.exists("memes"):
    os.makedirs("memes")

# Download and save the top 10 memes in the 'memes' directory
count = 0
for i, url in enumerate(image_urls):
    if count == 10:
        break
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    file_size = total_size/1048576 # Convert to MB
    if file_size <= 20:
        block_size = 1024
        t = tqdm(total=total_size, unit='iB', unit_scale=True)
        with open("memes/{}.jpg".format(titles[i].replace(" ", "_").replace("/", "_").replace("?", "_").replace(";", "_").replace(":", "_").replace("'", "_").replace(".", "_").replace(",", "_").replace("=", "_")), "wb") as f:
            for data in response.iter_content(block_size):
                t.update(len(data))
                f.write(data)
        t.close()
        count += 1

# Login to Instagram account
bot = Bot()
bot.login(username="**********", password="****************")

# Get the list of image files in the 'memes' directory
image_files = glob.glob("memes/*.jpg")[:10]

# Loop through the image files and post them to Instagram
for image_file in image_files:
    # Extract the title of the meme from the filename
    title = os.path.splitext(os.path.basename(image_file))[0].replace("_", " ")

    # Generate the list of hashtags based on the title of the meme
    hashtags = [f"#{tag}" for tag in title.lower().split()]
    hashtags += ["#funny", "#memes", "#lol"]

    # Set the caption for the post
    caption = f"{title}\n\n" + " ".join(hashtags)

    # Post the image with the caption and hashtags
    bot.upload_photo(image_file, caption=caption)

    # Wait for some time before posting the next image
    time.sleep(30)
