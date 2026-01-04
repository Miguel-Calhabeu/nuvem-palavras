document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('generator-form');
    const generateBtn = document.getElementById('generate-btn');
    const statusMessage = document.getElementById('status-message');
    const imageContainer = document.getElementById('image-container');
    const downloadLink = document.getElementById('download-link');
    
    // Vertical slider
    const verticalInput = document.getElementById('vertical-ratio');
    const verticalVal = document.getElementById('vertical-val');
    
    verticalInput.addEventListener('input', (e) => {
        verticalVal.textContent = `${e.target.value}%`;
    });

    // Handle File Input UI
    document.querySelectorAll('.file-input').forEach(input => {
        const label = input.nextElementSibling;
        const defaultText = label.textContent;

        input.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                label.textContent = e.target.files[0].name;
                label.classList.add('selected');
            } else {
                label.textContent = defaultText;
                label.classList.remove('selected');
            }
        });
    });

    // --- Color Modal Logic ---
    const modal = document.getElementById('color-modal');
    const openModalBtn = document.getElementById('open-color-modal');
    const closeModalBtn = document.querySelector('.close-modal');
    const confirmColorBtn = document.getElementById('confirm-color');
    const html5Color = document.getElementById('html5-color');
    const presetSwatches = document.querySelectorAll('.color-swatch');
    
    const currentColorDot = document.getElementById('current-color-dot');
    const hiddenColorInput = document.getElementById('selected-color-code');
    
    let tempColor = hiddenColorInput.value;

    // Open Modal
    openModalBtn.addEventListener('click', () => {
        modal.style.display = 'flex';
        // Initialize picker with current value if it's hex, otherwise default
        if (tempColor.startsWith('#')) {
            html5Color.value = tempColor;
        }
    });

    // Close Modal
    function closeModal() {
        modal.style.display = 'none';
    }
    closeModalBtn.addEventListener('click', closeModal);
    window.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    // Handle HTML5 Color Picker
    html5Color.addEventListener('input', (e) => {
        tempColor = e.target.value;
        // Deselect swatches
        presetSwatches.forEach(s => s.classList.remove('selected'));
    });

    // Handle Preset Swatches
    presetSwatches.forEach(swatch => {
        swatch.addEventListener('click', () => {
            tempColor = swatch.getAttribute('data-color');
            presetSwatches.forEach(s => s.classList.remove('selected'));
            swatch.classList.add('selected');
            
            // If it's a hex color, sync the picker
            if (tempColor.startsWith('#')) {
                html5Color.value = tempColor;
            }
        });
    });

    // Confirm Color
    confirmColorBtn.addEventListener('click', () => {
        hiddenColorInput.value = tempColor;
        currentColorDot.style.backgroundColor = tempColor;
        closeModal();
    });

    // Initialize Dot Color
    currentColorDot.style.backgroundColor = hiddenColorInput.value;


    // --- Form Submission ---
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Basic validation
        const textInput = document.getElementById('text-input').value.trim();
        const maskFile = document.getElementById('mask-file').files[0];
        const fontFile = document.getElementById('font-file').files[0];

        if (!textInput || !maskFile) {
            showStatus('Por favor, preencha o texto e escolha uma máscara.', 'error');
            return;
        }

        // Prepare data
        const formData = new FormData();
        formData.append('text_input', textInput);
        formData.append('mask_file', maskFile);
        if (fontFile) {
            formData.append('font_file', fontFile);
        }
        
        formData.append('color_code', hiddenColorInput.value);

        // Add settings
        formData.append('max_words', document.getElementById('max-words').value);
        formData.append('min_font_size', document.getElementById('min-font-size').value);
        formData.append('max_font_size', document.getElementById('max-font-size').value);
        formData.append('min_word_length', document.getElementById('min-word-length').value);
        formData.append('vertical_ratio', verticalInput.value);

        // UI updates
        generateBtn.disabled = true;
        generateBtn.textContent = 'Gerando...';
        showStatus('Processando...', 'normal');
        imageContainer.innerHTML = '<div class="placeholder">Gerando...</div>';
        downloadLink.style.display = 'none';

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                // Try to parse JSON error; fall back to plain text.
                let msg = 'Falha ao gerar nuvem';
                try {
                    const data = await response.json();
                    msg = data.error || msg;
                } catch {
                    try {
                        msg = await response.text();
                    } catch {
                        // ignore
                    }
                }
                throw new Error(msg);
            }

            // Success: API returns the PNG directly
            const blob = await response.blob();
            const objectUrl = URL.createObjectURL(blob);

            // Success
            showStatus('Nuvem de palavras gerada com sucesso!', 'success');
            
            // Display image
            const img = document.createElement('img');
            img.src = objectUrl;
            img.alt = 'Nuvem de Palavras Gerada';
            
            // Wait for image to load before clearing placeholder
            img.onload = () => {
                imageContainer.innerHTML = '';
                imageContainer.appendChild(img);
                
                // Setup download link
                downloadLink.href = objectUrl;
                downloadLink.style.display = 'block';
            };

        } catch (error) {
            console.error(error);
            showStatus(`Erro: ${error.message}`, 'error');
            imageContainer.innerHTML = '<div class="placeholder error">Falha ao gerar imagem</div>';
        } finally {
            generateBtn.disabled = false;
            generateBtn.textContent = 'Gerar Nuvem';
        }
    });

    function showStatus(message, type) {
        statusMessage.textContent = message;
        statusMessage.className = type;
        if (type === 'normal') statusMessage.style.color = '#333';
    }
});