import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ------------- Google Drive Setup -------------
SCOPES = ['https://www.googleapis.com/auth/drive']
PARENT_FOLDER_ID = '1GDACzOkUN09vX8XXgVUk_W_0SrYLnQ7w'  # Manager's shared folder ID

def authenticate_google_drive():
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    return build('drive', 'v3', credentials=creds)

def create_drive_folder(service, folder_name, parent_id):
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    folder = service.files().create(body=file_metadata, fields='id').execute()
    return folder['id']

def upload_to_drive(service, folder_id, file_path):
    file_name = os.path.basename(file_path)
    file_metadata = {'name': file_name, 'parents': [folder_id]}
    media = MediaFileUpload(file_path, resumable=True)
    service.files().create(body=file_metadata, media_body=media, fields='id').execute()

# ------------- Scraping Function -------------
def scrape_and_upload(url, service):
    domain = urlparse(url).netloc.replace('.', '_')
    folder_name = domain
    base_local_folder = f"scraped_assets/{folder_name}"
    os.makedirs(base_local_folder, exist_ok=True)

    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.content, 'html.parser')

        # Create subfolders
        images_folder = os.path.join(base_local_folder, 'images')
        pdfs_folder = os.path.join(base_local_folder, 'pdfs')
        logs_folder = os.path.join(base_local_folder, 'logs')

        os.makedirs(images_folder, exist_ok=True)
        os.makedirs(pdfs_folder, exist_ok=True)
        os.makedirs(logs_folder, exist_ok=True)

        # Download images
        img_tags = soup.find_all('img')
        for idx, img in enumerate(img_tags[:25]):
            img_url = img.get('src')
            if not img_url:
                continue
            if img_url.startswith('//'):
                img_url = 'https:' + img_url
            elif img_url.startswith('/'):
                img_url = url + img_url
            if not img_url.startswith('http'):
                continue
            ext = os.path.splitext(img_url)[-1][:5]
            img_path = os.path.join(images_folder, f'image_{idx}{ext}')
            with open(img_path, 'wb') as f:
                f.write(requests.get(img_url).content)

        # Download PDFs
        for link in soup.find_all('a', href=True):
            if link['href'].endswith('.pdf'):
                pdf_url = link['href']
                if not pdf_url.startswith('http'):
                    pdf_url = url + pdf_url
                pdf_name = os.path.join(pdfs_folder, os.path.basename(pdf_url))
                with open(pdf_name, 'wb') as f:
                    f.write(requests.get(pdf_url).content)

        # Save raw HTML log
        log_path = os.path.join(logs_folder, 'page.html')
        with open(log_path, 'w', encoding='utf-8', errors='ignore') as f:
            f.write(soup.prettify())

        # Upload folders
        drive_folder_id = create_drive_folder(service, folder_name, PARENT_FOLDER_ID)

        for subfolder_name in ['images', 'pdfs', 'logs']:
            local_sub = os.path.join(base_local_folder, subfolder_name)
            drive_sub_id = create_drive_folder(service, subfolder_name, drive_folder_id)
            for file in os.listdir(local_sub):
                upload_to_drive(service, drive_sub_id, os.path.join(local_sub, file))

        print(f"Done: {url}")

    except Exception as e:
        print(f"Failed: {url} - {e}")

# ------------- Main -------------
if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')  # Windows fix for terminal

    drive_service = authenticate_google_drive()

    num_urls = 2  # You can change this number
    for i in range(num_urls):
        url = input(f"Enter business website URL {i+1}/{num_urls}: ").strip()
        if not url.startswith("http"):
            url = "https://" + url
        scrape_and_upload(url, drive_service)

