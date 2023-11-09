import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import pandas as pd
import io
import shutil
import os

# Path to your service account key JSON file
credentials_path = 'consolidation/digitizing-alford-4f8cd1b7df85.json'
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/drive.file']
# Authenticate using the service account credentials
credentials = service_account.Credentials.from_service_account_file(
    credentials_path, scopes=scope
)
# Create a Google Drive API service
drive_service = build('drive', 'v3', credentials=credentials)

# Create a Google Docs API service
docs_service = build('docs', 'v1', credentials=credentials)

def get_page_assignments_as_df():
    # Create a gspread client and open the Google Sheet by its title or URL
    gc = gspread.authorize(credentials)
    spreadsheet = gc.open('Page Assignments')  # Replace with your sheet title or URL

    worksheet = spreadsheet.get_worksheet(0)

    # print(worksheet.get_all_cells())

    df = pd.DataFrame(worksheet.get_all_values())

    return df

def download_docx_from_drive(file_id, output_file_path):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%" % int(status.progress() * 100))

    # The file has been downloaded into RAM, now save it in a file
    fh.seek(0)

    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    with open(output_file_path, 'wb') as f:
        shutil.copyfileobj(fh, f, length=131072)


if __name__ == '__main__':
    pass
