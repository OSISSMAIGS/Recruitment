from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime
import json
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Directories (absolute paths)
BASE_DIR = app.root_path
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
PROGRESS_FOLDER = os.path.join(BASE_DIR, 'progress_data')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload and progress directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROGRESS_FOLDER, exist_ok=True)

# Google Sheets configuration
SCOPE = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

# You need to create a service account and download the JSON key file
# Place it in your project directory and update the path below
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'credensials.json') 
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

def get_session_id():
    """Generate or retrieve session ID"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']

def get_progress_file_path(session_id):
    """Get the file path for storing progress data"""
    return os.path.join(PROGRESS_FOLDER, f"{session_id}.json")

def save_progress(data):
    """Save user progress to file"""
    try:
        session_id = get_session_id()
        file_path = get_progress_file_path(session_id)
        
        # Load existing data if any
        existing_data = {}
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        
        # Update with new data
        existing_data.update(data)
        existing_data['last_updated'] = datetime.now().isoformat()
        
        # Save to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving progress: {e}")
        return False

def load_progress():
    """Load user progress from file"""
    try:
        session_id = get_session_id()
        file_path = get_progress_file_path(session_id)
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Error loading progress: {e}")
        return {}

def clear_progress():
    """Clear user progress"""
    try:
        session_id = get_session_id()
        file_path = get_progress_file_path(session_id)
        
        if os.path.exists(file_path):
            os.remove(file_path)
        return True
    except Exception as e:
        print(f"Error clearing progress: {e}")
        return False

def init_gsheet():
    """Initialize Google Sheets connection"""
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, SCOPE)
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        return spreadsheet
    except Exception as e:
        print(f"Error initializing Google Sheets: {e}")
        return None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_or_create_sheet(spreadsheet, sheet_name):
    """Get existing sheet or create new one"""
    try:
        # Try to get existing sheet
        sheet = spreadsheet.worksheet(sheet_name)
        return sheet
    except:
        # Create new sheet if it doesn't exist
        try:
            sheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
            # Add headers to new sheet
            headers = [
                'Timestamp', 'Email', 'Nama Lengkap', 'Kelas', 'Sekbid Pilihan',
                'Link Google Drive', 'Visi-Misi OSIS', 'Motivasi', 'Kelebihan',
                'Kekurangan', 'Pengalaman Berorganisasi', 'Sertifikat/Prestasi',
                'Skala Prioritas', 'Yakin Menjalankan Peraturan'
            ]
            sheet.insert_row(headers, 1)
            return sheet
        except Exception as e:
            print(f"Error creating sheet {sheet_name}: {e}")
            return None

def save_to_gsheet(data):
    """Save form data to Google Sheets based on sekbid selection"""
    try:
        spreadsheet = init_gsheet()
        if spreadsheet is None:
            print("Failed to initialize Google Sheets connection")
            return False
        
        # Get selected sekbid
        sekbid_list = data.get('sekbid', [])
        if not sekbid_list:
            print("No sekbid selected")
            return False
        
        print(f"Saving data for sekbid: {sekbid_list}")
        
        # Prepare row data
        row_data = [
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            data.get('email', ''),
            data.get('nama_lengkap', ''),
            data.get('kelas', ''),
            ', '.join(sekbid_list),
            data.get('gdrive_link', ''),
            data.get('visi_misi', ''),
            data.get('motivasi', ''),
            data.get('kelebihan', ''),
            data.get('kekurangan', ''),
            data.get('pengalaman_organisasi', ''),
            data.get('sertifikat_link', ''),
            data.get('skala_prioritas', ''),
            data.get('yakin_peraturan', '')
        ]
        
        # Save to each selected sekbid sheet
        success_count = 0
        saved_sheets = []
        
        for sekbid in sekbid_list:
            try:
                print(f"Processing sheet: {sekbid}")
                sheet = get_or_create_sheet(spreadsheet, sekbid)
                if sheet:
                    sheet.append_row(row_data)
                    success_count += 1
                    saved_sheets.append(sekbid)
                    print(f"✓ Data successfully saved to sheet: {sekbid}")
                else:
                    print(f"✗ Failed to get/create sheet: {sekbid}")
            except Exception as e:
                print(f"✗ Error saving to sheet {sekbid}: {e}")
        
        if success_count > 0:
            print(f"✓ Successfully saved data to {success_count} sheet(s): {', '.join(saved_sheets)}")
        else:
            print("✗ Failed to save data to any sheet")
        
        # Return True if at least one sheet was updated successfully
        return success_count > 0
        
    except Exception as e:
        print(f"✗ Error in save_to_gsheet: {e}")
        return False

@app.route('/')
def index():
    # Load existing progress
    progress = load_progress()
    return render_template('form_step1.html', progress=progress)

@app.route('/step1', methods=['POST'])
def step1():
    email = request.form.get('email')
    nama_lengkap = request.form.get('nama_lengkap')
    kelas = request.form.get('kelas')
    
    # Validation
    if not email or not nama_lengkap or not kelas:
        flash('Semua field harus diisi!', 'error')
        return redirect(url_for('index'))
    
    # Save progress
    progress_data = {
        'email': email,
        'nama_lengkap': nama_lengkap,
        'kelas': kelas,
        'step': 1
    }
    save_progress(progress_data)
    
    return redirect(url_for('step2'))

@app.route('/step2')
def step2():
    # Load existing progress
    progress = load_progress()
    
    # Check if user has completed step 1
    if not progress.get('email') or not progress.get('nama_lengkap') or not progress.get('kelas'):
        flash('Silakan lengkapi informasi dasar terlebih dahulu!', 'error')
        return redirect(url_for('index'))
    
    return render_template('form_step2.html', progress=progress)

@app.route('/submit_form', methods=['POST'])
def submit_form():
    # 1) Cek flag "submitted" di session
    if session.get('submitted'):
        flash('Form sudah pernah dikirim. Terima kasih!', 'info')
        return redirect(url_for('index'))
    
    # Load existing progress
    progress = load_progress()
    
    # Check if user has completed step 1
    if not progress.get('email') or not progress.get('nama_lengkap') or not progress.get('kelas'):
        flash('Silakan lengkapi informasi dasar terlebih dahulu!', 'error')
        return redirect(url_for('index'))
    
    # Get form data
    sekbid = request.form.getlist('sekbid')
    gdrive_link = request.form.get('gdrive_link')
    visi_misi = request.form.get('visi_misi')
    motivasi = request.form.get('motivasi')
    kelebihan = request.form.get('kelebihan')
    kekurangan = request.form.get('kekurangan')
    pengalaman_organisasi = request.form.get('pengalaman_organisasi')
    skala_prioritas = request.form.get('skala_prioritas')
    yakin_peraturan = request.form.get('yakin_peraturan')
    
    # Validation
    if not sekbid or len(sekbid) < 1 or len(sekbid) > 2:
        flash('Pilih minimal 1 dan maksimal 2 sekbid!', 'error')
        return redirect(url_for('step2'))
    
    if not gdrive_link or not visi_misi or not motivasi or not kelebihan or not kekurangan or not skala_prioritas or not yakin_peraturan:
        flash('Semua field yang required harus diisi!', 'error')
        return redirect(url_for('step2'))
    
    # Handle file upload
    sertifikat_link = ''
    if 'sertifikat' in request.files:
        file = request.files['sertifikat']
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to filename to avoid conflicts
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            sertifikat_link = f"https://recruitment.osissmaigs.com/static/uploads/{filename}"
    
    # Save final progress
    final_progress = {
        'sekbid': sekbid,
        'gdrive_link': gdrive_link,
        'visi_misi': visi_misi,
        'motivasi': motivasi,
        'kelebihan': kelebihan,
        'kekurangan': kekurangan,
        'pengalaman_organisasi': pengalaman_organisasi,
        'sertifikat_link': sertifikat_link,
        'skala_prioritas': skala_prioritas,
        'yakin_peraturan': yakin_peraturan,
        'step': 2
    }
    save_progress(final_progress)
    
    # Prepare data for Google Sheets
    form_data = {
        'email': progress['email'],
        'nama_lengkap': progress['nama_lengkap'],
        'kelas': progress['kelas'],
        'sekbid': sekbid,
        'gdrive_link': gdrive_link,
        'visi_misi': visi_misi,
        'motivasi': motivasi,
        'kelebihan': kelebihan,
        'kekurangan': kekurangan,
        'pengalaman_organisasi': pengalaman_organisasi,
        'sertifikat_link': sertifikat_link,
        'skala_prioritas': skala_prioritas,
        'yakin_peraturan': yakin_peraturan
    }
    
    # Save to Google Sheets
    save_result = save_to_gsheet(form_data)
    if save_result:
        # Tandai session agar tidak bisa submit lagi
        session['submitted'] = True
        clear_progress()
        session.clear()
        # Pass sekbid information to success page
        sekbid_list = form_data.get('sekbid', [])
        return render_template('success.html', sekbid_list=sekbid_list)
    else:
        flash('Terjadi kesalahan saat menyimpan data. Silakan coba lagi.', 'error')
        return redirect(url_for('step2'))

@app.route('/clear_progress')
def clear_user_progress():
    """Clear user progress and redirect to start"""
    clear_progress()
    session.clear()
    # Reset submitted flag when user starts fresh
    session.pop('submitted', None)
    flash('Progress telah dihapus. Anda dapat memulai dari awal.', 'info')
    return redirect(url_for('index'))

@app.route('/auto_save', methods=['POST'])
def auto_save():
    """Auto-save progress via AJAX"""
    try:
        data = request.get_json()
        if data:
            save_progress(data)
            return jsonify({'success': True, 'message': 'Progress tersimpan'})
        return jsonify({'success': False, 'message': 'Data tidak valid'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/get_progress')
def get_progress():
    """Get current progress via AJAX"""
    try:
        progress = load_progress()
        return jsonify({'success': True, 'progress': progress})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/debug_sheets')
def debug_sheets():
    """Debug endpoint to list all sheets"""
    try:
        spreadsheet = init_gsheet()
        if spreadsheet:
            sheets = [sheet.title for sheet in spreadsheet.worksheets()]
            return jsonify({'success': True, 'sheets': sheets})
        return jsonify({'success': False, 'message': 'Failed to connect to Google Sheets'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)