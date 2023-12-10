import datetime

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload

from utils.defaults import GOOGLE_CRED, PARENT_FOLDER_ID, SHEET_ID


credentials_sheets = service_account.Credentials.from_service_account_file(
    GOOGLE_CRED, scopes=['https://www.googleapis.com/auth/spreadsheets']
)
google_service = build('drive', 'v3', credentials=service_account.Credentials.from_service_account_file(
    GOOGLE_CRED, scopes=['https://www.googleapis.com/auth/drive.file']
))
google_service_sheets = build('sheets', 'v4', credentials=service_account.Credentials.from_service_account_file(
    GOOGLE_CRED, scopes=['https://www.googleapis.com/auth/spreadsheets']
))


def create_user_folder(user_id):
    try:
        # Check if the user's folder already exists
        folder_query = f"name='{user_id}' and mimeType='application/vnd.google-apps.folder'"
        if PARENT_FOLDER_ID:
            folder_query += f" and '{PARENT_FOLDER_ID}' in parents"

        existing_folders = google_service.files().list(q=folder_query).execute().get('files', [])

        if existing_folders:
            user_folder_id = existing_folders[0]['id']
        else:
            # Create the user's folder
            folder_metadata = {'name': user_id, 'mimeType': 'application/vnd.google-apps.folder'}
            if PARENT_FOLDER_ID:
                folder_metadata['parents'] = [PARENT_FOLDER_ID]

            user_folder = google_service.files().create(body=folder_metadata, fields='id').execute()
            user_folder_id = user_folder['id']

        return user_folder_id

    except HttpError as e:
        print(f"An error occurred: {e.content}")
        return None


def input_data_to_sheet(user_id, data_to_sheet):
    spreadsheet_range = 'Main'
    try:
        values = [[
            user_id,
            data_to_sheet.get('account_id', 'none'),
            data_to_sheet.get('address', 'none'),
            data_to_sheet.get('meter_type', 'none'),
            data_to_sheet.get('photo_url', 'none'),
            data_to_sheet.get('created_at', 'none'),
        ]]

        # Call the Sheets API to update values
        request_body = {'values': values}
        google_service_sheets.spreadsheets().values().append(
            spreadsheetId=SHEET_ID, range=spreadsheet_range, valueInputOption='RAW', body=request_body
        ).execute()

        print(f"Data successfully input into Google Sheet for user {user_id}")
    except HttpError as e:
        print(f"An error occurred while updating Google Sheet: {e.content}")


def upload_file_to_user_folder(photo_stream, user_id, data):
    # Create or get the user's folder
    user_folder_id = create_user_folder(data["account_id"])

    if user_folder_id:
        # Upload the file to the user's folder
        media_body = MediaIoBaseUpload(photo_stream, mimetype='image/jpeg', chunksize=1024 * 1024, resumable=True)
        file_metadata = {'name': f'{data["meter_type"]}-{data["created_at"]}.jpg', 'parents': [user_folder_id]}
        request = google_service.files().create(body=file_metadata, media_body=media_body)

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Uploaded {int(status.progress() * 100)}%")
        photo_url = f"https://drive.google.com/uc?id={response['id']}"

        data["photo_url"] = photo_url

        input_data_to_sheet(user_id, data)
    else:
        return None
