async function downloadImage() {
    const target = document.getElementById('capture-target');
    const btn = document.querySelector('button');

    btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Generando...';
    btn.disabled = true;

    try {
        // Preload images as Base64 to avoid CORS issues
        await preloadImages(target);

        const canvas = await html2canvas(target, {
            backgroundColor: '#0f172a',
            scale: 2, // High resolution
            useCORS: true,
            allowTaint: true
        });

        const link = document.createElement('a');
        link.download = `reporte-${window.leagueName}.png`;
        link.href = canvas.toDataURL();
        link.click();

        btn.innerHTML = '<i class="fas fa-download mr-2"></i>Descargar Imagen';
        btn.disabled = false;

    } catch (err) {
        console.error(err);
        alert('Error al generar la imagen: ' + err.message);
        btn.innerHTML = '<i class="fas fa-exclamation-triangle mr-2"></i>Error';
        btn.disabled = false;
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
