from flask import Flask, request, send_file, jsonify
import os
import uuid
from generate_cloud import create_cloud

app = Flask(__name__, static_folder='web', static_url_path='')

# Directories for uploads and results
UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# Default font path (update this to point to a valid font on your system if needed)
# Using the one from the environment we saw earlier
DEFAULT_FONT_PATH = "venv/lib/python3.13/site-packages/matplotlib/mpl-data/fonts/ttf/DejaVuSans.ttf"

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    uploaded_font_path = None
    text_path = None
    mask_path = None

    try:
        # Check for mask file (mandatory)
        if 'mask_file' not in request.files:
            return jsonify({'error': 'Arquivo de máscara é obrigatório'}), 400

        mask_file = request.files['mask_file']
        
        # Handle text input (text_input string OR text_file upload)
        text_input = request.form.get('text_input', '').strip()
        text_file = request.files.get('text_file')
        
        if not text_input and not text_file:
             return jsonify({'error': 'Texto ou arquivo de texto é obrigatório'}), 400

        color_code = request.form.get('color_code', 'hsl(0, 0%, 0%)')

        # Get settings with validation
        try:
            max_words = int(request.form.get('max_words', 400))
        except ValueError:
            max_words = 400

        try:
            min_font_size = int(request.form.get('min_font_size', 10))
        except ValueError:
            min_font_size = 10

        try:
            max_font_size_val = request.form.get('max_font_size', '')
            max_font_size = int(max_font_size_val) if max_font_size_val else None
        except ValueError:
            max_font_size = None

        try:
            min_word_length = int(request.form.get('min_word_length', 0))
        except ValueError:
            min_word_length = 0

        try:
            vertical_ratio = int(request.form.get('vertical_ratio', 40))
        except ValueError:
            vertical_ratio = 40

        # Calculate prefer_horizontal (inverse of vertical ratio)
        prefer_horizontal = 1.0 - (vertical_ratio / 100.0)

        # Save uploaded files temporarily
        request_id = str(uuid.uuid4())
        
        mask_path = os.path.join(UPLOAD_FOLDER, f"{request_id}_{mask_file.filename}")
        mask_file.save(mask_path)
        
        text_path = os.path.join(UPLOAD_FOLDER, f"{request_id}_text.txt")
        if text_input:
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(text_input)
        else:
            text_file.save(text_path)

        # Handle font file
        font_path = DEFAULT_FONT_PATH
        if 'font_file' in request.files and request.files['font_file'].filename != '':
            font_file = request.files['font_file']
            uploaded_font_path = os.path.join(UPLOAD_FOLDER, f"{request_id}_{font_file.filename}")
            font_file.save(uploaded_font_path)
            font_path = uploaded_font_path

        # Generate cloud
        try:
            wc = create_cloud(
                text_path,
                mask_path,
                color_code,
                font_path,
                max_words=max_words,
                min_font_size=min_font_size,
                max_font_size=max_font_size,
                min_word_length=min_word_length,
                prefer_horizontal=prefer_horizontal
            )

            # Save result
            result_filename = f"{request_id}_result.png"
            result_path = os.path.join(RESULTS_FOLDER, result_filename)
            wc.to_file(result_path)

            # Clean up uploaded files (Success case)
            if os.path.exists(text_path): os.remove(text_path)
            if os.path.exists(mask_path): os.remove(mask_path)
            if uploaded_font_path and os.path.exists(uploaded_font_path):
                os.remove(uploaded_font_path)

            return jsonify({'image_url': f'/results/{result_filename}'})

        except Exception as e:
            # Clean up uploaded files (Generation Error case)
            if text_path and os.path.exists(text_path): os.remove(text_path)
            if mask_path and os.path.exists(mask_path): os.remove(mask_path)
            if uploaded_font_path and os.path.exists(uploaded_font_path):
                os.remove(uploaded_font_path)
            raise e # Re-raise to be caught by outer block

    except Exception as e:
        # General Error fallback
        if text_path and os.path.exists(text_path): os.remove(text_path)
        if mask_path and os.path.exists(mask_path): os.remove(mask_path)
        if uploaded_font_path and os.path.exists(uploaded_font_path):
            os.remove(uploaded_font_path)
        return jsonify({'error': str(e)}), 500

@app.route('/results/<filename>')
def get_result(filename):
    return send_file(os.path.join(RESULTS_FOLDER, filename))

if __name__ == '__main__':
    print("Starting server at http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)
