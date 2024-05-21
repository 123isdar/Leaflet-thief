import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
from googleapiclient import discovery
from bs4 import BeautifulSoup
import requests
import googleapiclient
import time

# Start the OAuth flow to retrieve credentials
def authorize_credentials():
    #Watch the video to learn more about client_secret.json file
    CLIENT_SECRET = 'client_secret.json'
    SCOPE = 'https://www.googleapis.com/auth/blogger'
    STORAGE = Storage('credentials.storage')
    # Fetch credentials from storage
    credentials = STORAGE.get()
    # If the credentials don't exist in the storage location, then run the flow
    if credentials is None or credentials.invalid:
        flow = flow_from_clientsecrets(CLIENT_SECRET, scope=SCOPE)
        http = httplib2.Http()
        credentials = run_flow(flow, STORAGE, http=http)
    return credentials

def getBloggerService():
    credentials = authorize_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://blogger.googleapis.com/$discovery/rest?version=v3')
    service = discovery.build('blogger', 'v3', http=http, discoveryServiceUrl=discoveryUrl)
    return service

def postToBlogger(payload):
    service = getBloggerService()
    post = service.posts()

    # Implement a basic backoff mechanism
    retries = 3  # You can adjust the number of retries
    for _ in range(retries):
        try:
            insert = post.insert(blogId='blogger id', body=payload).execute()
            print("Done post!")
            return insert
        except googleapiclient.errors.HttpError as err:
            if 'rateLimitExceeded' in str(err):
                print("Rate limit exceeded. Retrying after a short delay.")
                time.sleep(5)  # Adjust the delay as needed
            else:
                raise

def extract_info_from_link(link):
    if not link:
        print("Empty link. Skipping.")
        return "No title found", "No video content found", None

    if not link.startswith(('http://', 'https://')):
        print("Invalid URL format. Skipping.")
        return "No title found", "No video content found", None

    try:
        response = requests.get(link)
        response.raise_for_status()  # Raise an HTTPError for bad responses
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return "No title found", "No video content found", None

    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract title
    title = soup.title.text.replace("", "") if soup.title else "No title found"

    # Extract video content
    video_tag = soup.find('video')
    video_content = str(video_tag.find_all('source')) if video_tag else "No video content found"

    data_setup = video_tag.get('data-setup')
    poster_url = None
    if data_setup:
        import json
        data_setup_dict = json.loads(data_setup)
        poster_url = data_setup_dict.get('poster')
    # Extract poster URL
    return title, video_content, poster_url

with open('sorted_unique_links.txt', 'r') as file:
    for line in file:
        # Remove newline character at the end
        line = line.strip()

        # Assuming each line in the text file is a link
        link = line

        # Extract information from the link
        title_from_link, video_from_link, poster_url = extract_info_from_link(link)

        customMetaData = "This is meta data"
        style = """<style>
            #myImage{
                display:none;
            }
        </style>"""
        payload = {
            "content": style + f'<video width="800" height="500" controls>' + str(video_from_link) + f'</video> <img src="{poster_url}" id="myImage"/>',
            "title": title_from_link,
            'labels': ['label1', 'label2'],
            'customMetaData': customMetaData,
        }
        postToBlogger(payload)
