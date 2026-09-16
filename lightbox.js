(function () {
    'use strict';

    function openLightbox(src, caption) {
        var lb = document.getElementById('lightbox');
        var lbImg = document.getElementById('lightbox-img');
        var lbCap = document.getElementById('lightbox-caption');
        if (!lb || !lbImg || !lbCap) return;

        lbImg.src = src.indexOf('assets/') === 0 || src.indexOf('http') === 0 ? src : 'assets/' + src;
        lbCap.innerText = caption;
        lb.style.display = 'flex';
    }

    function closeLightbox() {
        var lb = document.getElementById('lightbox');
        if (lb) {
            lb.style.display = 'none';
        }
    }

    window.openLightbox = openLightbox;
    window.closeLightbox = closeLightbox;
})();
