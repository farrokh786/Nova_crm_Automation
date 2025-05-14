# Nova_crm_Automation

Title: Nova Media - Cloud Automation for Asset Collection

Description: A fully automated solution for scraping business assets (logos, PDFs, images, etc.) from client websites using Python, BeautifulSoup, and uploading them to Google Drive, powered by Azure automation workflows.

⸻

Sections to Include 1. Project Overview 2. Tech Stack 3. Features 4. How It Works (Architecture) 5. Getting Started (Setup Instructions) 6. Folder Structure 7. Screenshots (optional) 8. Contact Info / About Me Example Starting Snippet:

Nova Media - Cloud Asset Automation
This project automates the collection of logos, product images, and documents from client websites and stores them directly into structured Google Drive folders. Built for Nova Media as part of a 12-week DevOps internship.

🔧 Tech Stack

Python (BeautifulSoup)
Google Drive API
Azure Logic Apps (planned)
VS Code
GitHub
⚙️ Key Features

Scrapes logos, PDFs, and images from any valid business website URL
Automatically creates timestamped folders for each client
Uploads all assets to a shared Google Drive workspace
Designed for reuse and scalable automation
📁 Folder Structure

project/ │ ├── scraper.py ├── drive_upload.py ├── credentials.json ├── token.json └── /output_assets
