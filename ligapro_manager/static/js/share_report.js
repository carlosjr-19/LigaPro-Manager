async function downloadImage() {
    const target = document.getElementById('capture-target');
    const btn = document.querySelector('button[onclick="downloadImage()"]');

    btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Generando...';
    btn.disabled = true;

    try {
        // Preload images as Base64 to avoid CORS issues
        await preloadImages(target);

        const canvas = await html2canvas(target, {
            backgroundColor: null, // Transparent to grab the actual element color
            scale: 2, // High resolution
            useCORS: true,
            allowTaint: true
        });

        const dataUrl = canvas.toDataURL('image/png');
        triggerDownload(dataUrl);

        btn.innerHTML = '<i class="fas fa-download mr-2"></i>Descargar Imagen';
        btn.disabled = false;

    } catch (err) {
        console.error("html2canvas error:", err);
        btn.innerHTML = '<i class="fas fa-exclamation-triangle mr-2"></i>Error';
        btn.disabled = false;
    }
}

function triggerDownload(dataUrl) {
    const fileName = (window.leagueName || 'reporte') + '_rol.png';
    if (window.FlutterDownloader) {
        try {
            window.FlutterDownloader.postMessage(fileName + "|" + dataUrl);
            return;
        } catch (e) {
            console.error("Flutter error:", e);
        }
    }
    
    // Fallback for browser
    try {
        const link = document.createElement('a');
        link.download = fileName;
        link.href = dataUrl;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } catch (e) {
        console.error("Browser download error:", e);
    }
}

async function downloadPDF() {
    const wrapper = document.getElementById('pdf-capture-wrapper');
    const target = document.getElementById('pdf-capture-target');
    const btn = document.querySelector('button[onclick="downloadPDF()"]');

    btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Generando PDF...';
    btn.disabled = true;

    // Show wrapper temporarily but keep it out of view
    wrapper.classList.remove('hidden');
    wrapper.style.position = 'absolute';
    wrapper.style.left = '-9999px';
    wrapper.style.top = '0';

    try {
        // Preload images for PDF as well
        await preloadImages(target);

        const fileName = (window.leagueName || 'reporte') + '_rol.pdf';
        const opt = {
            margin: 0,
            filename: fileName,
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { 
                scale: 2, 
                useCORS: true, 
                letterRendering: true,
                backgroundColor: null
            },
            jsPDF: { unit: 'pt', format: 'a4', orientation: 'landscape' }
        };

        if (window.FlutterDownloader) {
            const pdfBase64 = await html2pdf().set(opt).from(target).outputPdf('datauristring');
            window.FlutterDownloader.postMessage(fileName + "|" + pdfBase64);
        } else {
            await html2pdf().set(opt).from(target).save();
        }

        btn.innerHTML = '<i class="fas fa-file-pdf mr-2"></i>Descargar PDF';
        btn.disabled = false;

    } catch (err) {
        console.error("html2pdf error:", err);
        btn.innerHTML = '<i class="fas fa-exclamation-triangle mr-2"></i>Error';
        btn.disabled = false;
    } finally {
        wrapper.classList.add('hidden');
        wrapper.style.position = '';
        wrapper.style.left = '';
        wrapper.style.top = '';
    }
}

async function preloadImages(element) {
    const images = element.querySelectorAll('img');
    const promises = Array.from(images).map(img => {
        if (img.src.startsWith('data:')) return Promise.resolve();

        let fetchUrl = img.src;
        // Check if image is external and needs proxy
        if (img.src.startsWith('http') && !img.src.includes(window.location.origin)) {
            fetchUrl = window.proxyImageUrl + "?url=" + encodeURIComponent(img.src);
        }

        return fetch(fetchUrl)
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.blob();
            })
            .then(blob => {
                return new Promise((resolve, reject) => {
                    const reader = new FileReader();
                    reader.onloadend = () => {
                        img.dataset.originalSrc = img.src; // Backup original src
                        img.src = reader.result; // Replace with Base64
                        resolve();
                    };
                    reader.onerror = reject;
                    reader.readAsDataURL(blob);
                });
            })
            .catch(err => {
                console.warn('Could not load image as Base64:', img.src, err);
                // If it fails (e.g. CORS block), we leave it as is and hope html2canvas can handle it or just skip it
                return Promise.resolve();
            });
    });
    await Promise.all(promises);
}
