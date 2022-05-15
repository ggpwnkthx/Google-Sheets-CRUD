# Google Sheets CRUD
 CRUD interface for Google Spreadsheets

Instantiation takes at minimum 3 arguments: the credentials needed to access the data, the name of the spreadsheet, and the name of the worksheet. There are 2 optional arguments: has_headers (which will used the first row for dynamic column naming) and headers (which will statically set the column names). The most complicated part to this is getting the credentials set up properly.
```
GS_CRUD = GoogleSpreadsheetCRUD(
    credential={
        "type": "service_account",
        "project_id": os.environ['google_credentials_project_id'],
        "private_key_id": os.environ['google_credentials_private_key_id'],
        "private_key": os.environ['google_credentials_private_key'].replace("\\n", "\n"),
        "client_email": os.environ['google_credentials_client_email'],
        "client_id": os.environ['google_credentials_client_id'],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{urllib.parse.quote_plus(os.environ['google_credentials_client_email'])}",
        "scopes": [
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/spreadsheets"
        ]
    },
    spreadsheet="Name of the Sheet",
    worksheet="Sheet1",
    has_headers=True
)
```
## Create
Create will automatically determine the the next appropriate row to put data into. It will also automatically figure out which cells should have what values when a dynamic header is used.
```
GS_CRUD.create([{
  "ID":"123",
  "Site":"ABCD",
  ...
  "Ready":"TRUE"
}])
```
## Read
Read will either pull all of the data or return rows (with their proper index keys) based on key filters.
```
GS_CRUD.read(Site="ABCD", Ready="TRUE")
```
## Update
Update will only write data to the cells of a given row that need to be changed - also dynamically. The code sample below gets all rows where the "Site" column is "ABCD" and the "Ready" column is "FALSE". It changes the "Ready" column value for all the rows to "TRUE". Then does a single bulk update where only the changed values are actually updated. What changes are made can be a lot more sophisticated than just updating an entire column. I just wanted to showcase how simple bulk operations are.
```
rows = GS_CRUD.read(Site="ABCD", Ready="FALSE")
rows["Ready"] = "TRUE"
GS_CRUD.update(rows)
```
# Delete
Delete is pretty self-explanatory. It will remove an entire row, given the index key for that row.
```
GS_CRUD.delete(99)
```