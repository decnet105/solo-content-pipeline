---
name: free-study-companion-drive
description: Standardized pipeline for generating unencrypted 300 DPI A4 study companion workbooks (PDF) for TokyoFlow masterclasses and uploading to Google Drive with public access.
---

# Free Study Companion & Google Drive Synchronization Skill

## 1. When to Use
Use this skill whenever:
- Generating study companion PDFs for any episode, weekly compilation, or specialized series.
- Uploading educational PDFs to Google Drive under `Weekly_Master_Workbooks_PDF`.
- Syncing Google Drive download links into YouTube descriptions and pinned comments.

## 2. Key Requirements
1. **Unencrypted PDF (Zero Passcode)**:
   - Do NOT use `PdfWriter.encrypt()`.
   - Direct opening and print-friendly for learners.
2. **300 DPI A4 Dimensions**:
   - 2480 x 3508 px per page.
   - Clean light/white executive layout with high contrast.
3. **Google Drive Integration**:
   - Target Folder: `Weekly_Master_Workbooks_PDF`
   - Sharing Permission: `role='reader', type='anyone'`
   - Validation: Must check HTTP 200 on returned view URL.
4. **YouTube Embedding**:
   - Embed verified link into video `metadata.md` / description.
   - Post comment via YouTube Data API containing the link.

## 3. Reference Implementation Pattern
```python
from PIL import Image, ImageDraw, ImageFont
from googleapiclient.discovery import build
from drive_manager import get_drive_credentials, get_or_create_folder, upload_and_share_file

def generate_companion_pdf(data, out_path: Path) -> Path:
    W, H = 2480, 3508
    img = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    # Render header, title card, vocabulary table, grammar breakdown, routine guide, footer
    img.save(out_path, "PDF", resolution=300.0)
    return out_path

def upload_companion_to_drive(pdf_path: Path) -> str:
    creds = get_drive_credentials()
    service = build("drive", "v3", credentials=creds)
    folder_id = get_or_create_folder(service, "Weekly_Master_Workbooks_PDF")
    res = upload_and_share_file(service, str(pdf_path), folder_id, pdf_path.name)
    return res.get("view_link", "")
```
