import asyncio
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from ..ckpool import eusolo
from ..ckpool.eusolo.model.pool import Pool


# Charger les clés du bot
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']  # Accès uniquement à Google Sheets
SERVICE_ACCOUNT_FILE = 'data/keys.json'

# Authentification
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Construire le service Sheets
service = build('sheets', 'v4', credentials=credentials)

# ID du document Google Sheets (extrait de l'URL)
SPREADSHEET_ID = '1Jr4vRDWOmFtelWUQ9cdvNXJSxq9qNDC76wU6t8tWIak'
MODEL_SHEET_ID = 0

def clone_sheet_0():
    # Création de la requête pour dupliquer la feuille
    request_body = {
        "requests": [
            {
                "duplicateSheet": {
                    "sourceSheetId": MODEL_SHEET_ID,  # ID de la feuille modèle
                    "insertSheetIndex": 1,  # Position où insérer la nouvelle feuille
                    "newSheetName": datetime.now().strftime("%d/%m")  # Nom de la nouvelle feuille (ex: Copie_01)
                }
            }
        ]
    }

    response = service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body=request_body
    ).execute()

    print("Feuille dupliquée avec succès :", response)

def add_chart(size: int):
    request_body = {
        "requests": [
            {
                "addChart": {
                    "chart": {
                        "spec": {
                            "title": "Répartition des valeurs",
                            "pieChart": {  # Type de graphique : PIE
                                "threeDimensional": False,  # True pour un effet 3D
                                "domain": {  # Les labels (catégories)
                                    "sourceRange": {
                                        "sources": [
                                            {
                                                "sheetId": MODEL_SHEET_ID,
                                                "startRowIndex": 0,
                                                "endRowIndex": size,
                                                "startColumnIndex": 0,
                                                "endColumnIndex": 1,
                                            }
                                        ]
                                    }
                                },
                                "series": {  # Les valeurs associées aux labels
                                    "sourceRange": {
                                        "sources": [
                                            {
                                                "sheetId": MODEL_SHEET_ID,
                                                "startRowIndex": 0,
                                                "endRowIndex": size,
                                                "startColumnIndex": 1,
                                                "endColumnIndex": 2,
                                            }
                                        ]
                                    }
                                }
                            }
                        },
                        "position": {
                            "overlayPosition": {
                                "anchorCell": {
                                    "sheetId": MODEL_SHEET_ID,
                                    "rowIndex": 0,
                                    "columnIndex": 2
                                }
                            }
                        }
                    }
                }
            }
        ]
    }

    # Exécution de la requête

    response = service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body=request_body
    ).execute()

    print(response)

def add_values(values: list, feuille: str):
    print("adding", values)
    body = {
        'values': values
    }

    # Appeler l'API pour ajouter les données
    result = service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range = feuille,  # Nom de la feuille
        valueInputOption="RAW",  # RAW ou USER_ENTERED
        body=body
    ).execute()

    print(result)

def write_stats(pool: Pool):
    data = []
    for worker in pool.workers:
        data.append([worker.name, worker.shares])
    
    add_values(data, "Feuille 1")
    add_chart(len(data))


async def main():
    write_stats(await eusolo.get_user(eusolo.POOL_ID))
    

asyncio.run(main())