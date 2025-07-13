# Recruitment OSIS Web Application

A Flask-based web application for OSIS recruitment with automatic progress saving functionality.

## Features

### Progress Saving
- **Automatic Progress Saving**: User progress is automatically saved as they fill out the form
- **Session Persistence**: Progress persists even when users close and reopen the browser
- **Form Pre-filling**: When users return, all previously entered data is automatically loaded
- **Progress Indicators**: Visual indicators show users their saved progress
- **Manual Progress Clear**: Users can clear their progress and start fresh
- **Anti-Double Submission**: Prevents users from submitting the same form multiple times

### Form Features
- **Two-Step Process**: 
  - Step 1: Basic information (email, name, class)
  - Step 2: Detailed information (selections, essays, file uploads)
- **File Upload**: Support for certificate/prestige document uploads
- **Validation**: Comprehensive form validation with user-friendly error messages
- **Google Sheets Integration**: All submissions are automatically categorized and saved to separate sheets based on selected sekbid

## Technical Implementation

### Progress Storage
- **File-based Storage**: Progress is stored in JSON files in the `progress_data/` directory
- **Unique Session IDs**: Each user gets a unique session ID for progress tracking
- **Auto-save**: Progress is automatically saved after 1 second of inactivity
- **AJAX Integration**: Real-time progress saving without page reloads

### Google Sheets Categorization
- **Dynamic Sheet Creation**: Sheets are automatically created for each sekbid if they don't exist
- **Multi-Sheet Support**: If user selects multiple sekbid, data is saved to all corresponding sheets
- **Automatic Headers**: New sheets are created with proper column headers
- **Error Handling**: Comprehensive error handling with detailed logging

### Security Features
- **Session-based Protection**: Uses session flags to prevent double submissions
- **Button Disable**: Submit button is disabled during form submission
- **Visual Feedback**: Loading spinner and disabled state provide clear user feedback
- **Graceful Handling**: Users receive informative messages if they attempt to resubmit

### File Structure
```
Recruitment/
├── main.py                 # Main Flask application
├── credensials.json       # Google Sheets API credentials
├── progress_data/         # User progress storage (auto-created)
├── static/
│   └── uploads/          # File uploads directory
└── templates/
    ├── base.html         # Base template with styling
    ├── form_step1.html   # Step 1 form
    ├── form_step2.html   # Step 2 form
    └── success.html      # Success page
```

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install flask gspread oauth2client werkzeug
   ```

2. **Google Sheets Setup**:
   - Create a Google Service Account
   - Download the credentials JSON file
   - Place it as `credensials.json` in the project root
   - Update `SPREADSHEET_ID` in `main.py` with your Google Sheets ID

3. **Run the Application**:
   ```bash
   python main.py
   ```

4. **Access the Application**:
   - Open `http://localhost:5000` in your browser

## Progress Saving Details

### How It Works
1. **Session Management**: Each user gets a unique session ID stored in browser cookies
2. **File Storage**: Progress data is stored in JSON files named with the session ID
3. **Auto-save**: JavaScript monitors form changes and sends data to `/auto_save` endpoint
4. **Data Loading**: When users return, the application loads their saved progress
5. **Form Pre-filling**: All form fields are automatically populated with saved data

### Progress Data Structure
```json
{
  "email": "user@example.com",
  "nama_lengkap": "John Doe",
  "kelas": "XI-IPA-A",
  "sekbid": ["Ketua OSIS", "Sekretaris"],
  "gdrive_link": "https://drive.google.com/...",
  "visi_misi": "User's vision and mission...",
  "motivasi": "User's motivation...",
  "kelebihan": "User's strengths...",
  "kekurangan": "User's weaknesses...",
  "pengalaman_organisasi": "User's experience...",
  "skala_prioritas": "User's priorities...",
  "yakin_peraturan": "Ya, saya yakin",
  "step": 2,
  "last_updated": "2024-01-01T12:00:00"
}
```

### Google Sheets Structure
When a user submits the form, the data is automatically categorized:

**Example 1: Single Sekbid Selection**
- User selects: "Sekretaris"
- Data saved to: Sheet named "Sekretaris"

**Example 2: Multiple Sekbid Selection**
- User selects: ["Ketua OSIS", "Sekretaris"]
- Data saved to: Both "Ketua OSIS" and "Sekretaris" sheets

**Sheet Headers (automatically created)**
```
Timestamp | Email | Nama Lengkap | Kelas | Sekbid Pilihan | Link Google Drive | Visi-Misi OSIS | Motivasi | Kelebihan | Kekurangan | Pengalaman Berorganisasi | Sertifikat/Prestasi | Skala Prioritas | Yakin Menjalankan Peraturan
```

### API Endpoints
- `GET /` - Main form page with progress loading
- `POST /step1` - Save step 1 data
- `GET /step2` - Step 2 form with progress loading
- `POST /submit_form` - Final form submission
- `POST /auto_save` - Auto-save progress via AJAX
- `GET /get_progress` - Get current progress via AJAX
- `GET /clear_progress` - Clear user progress
- `GET /debug_sheets` - Debug endpoint to list all sheets

## Security Considerations

- **Session Security**: Session IDs are randomly generated UUIDs
- **File Permissions**: Progress files are stored locally with appropriate permissions
- **Data Privacy**: Progress data is stored locally and cleared after successful submission
- **Input Validation**: All form inputs are validated server-side

## Browser Compatibility

- **Modern Browsers**: Chrome, Firefox, Safari, Edge
- **JavaScript Required**: Auto-save functionality requires JavaScript
- **Local Storage**: Progress is stored locally on the server, not in browser storage

## Troubleshooting

### Common Issues
1. **Progress Not Saving**: Check browser console for JavaScript errors
2. **File Upload Issues**: Ensure `static/uploads/` directory has write permissions
3. **Google Sheets Errors**: Verify credentials and spreadsheet permissions
4. **Session Issues**: Clear browser cookies if session problems occur
5. **Sheet Creation Errors**: Ensure the Google Service Account has permission to create sheets in the spreadsheet
6. **Multiple Sekbid Issues**: Check console logs for detailed error messages about sheet operations
7. **Double Submission**: If users report form not submitting, check if session flag is stuck - use `/clear_progress` to reset

### Debug Mode
The application runs in debug mode by default. Check the console for detailed error messages. # Recruitment
# Recruitment
