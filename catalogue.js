(function () {
    'use strict';

    var currentCategory = 'All Products';
    var imageObserver = null;
    var sentinelObserver = null;
    var visibleCount = 24;
    var PAGE_SIZE = 24;
    var renderedUntil = 0;
    var indexMap = null;
    var searchTimer = null;

    function encodeImagePath(path) {
        if (!path) return path;
        if (/^https?:\/\//i.test(path)) return path;
        return path.split('/').map(function (part) {
            return encodeURIComponent(part);
        }).join('/');
    }

    function escapeHtml(value) {
        return String(value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function getIndexMap() {
        if (indexMap || typeof productsData === 'undefined') return indexMap;
        indexMap = {};
        for (var i = 0; i < productsData.length; i++) {
            indexMap[productsData[i].name + '|' + productsData[i].category + '|' + productsData[i].image] = i;
        }
        return indexMap;
    }

    function buildProductSummary(product) {
        if (product.flavors && product.flavors.length) {
            return '<span class="flavour-label">' + product.flavors.length + ' flavours in store</span>';
        }
        if (product.variants && product.variants.length) {
            return escapeHtml(product.variants.slice(0, 3).join(' • '));
        }
        return 'Call store for price &amp; stock at 128 King St, London W6 0QU';
    }

    function buildActionHtml(product, index) {
        var html = '<a href="tel:02080011639" class="btn-call-shop"><i class="fa-solid fa-phone"></i> CALL STORE FOR PRICE & STOCK</a>';
        if (product.flavors && product.flavors.length) {
            html += '<button type="button" onclick="openFlavorModal(' + index + ')" class="btn-view-flavors"><i class="fa-solid fa-eye"></i> VIEW AVAILABLE FLAVORS</button>';
        }
        return html;
    }

    function getFilteredProducts(query) {
        if (typeof productsData === 'undefined') return [];
        var q = (query || '').toLowerCase().trim();
        return productsData.filter(function (product) {
            if (q) {
                var nameMatch = (product.name || '').toLowerCase().indexOf(q) !== -1;
                var flavorMatch = (product.flavors || []).some(function (flavor) {
                    return String(flavor).toLowerCase().indexOf(q) !== -1;
                });
                var variantMatch = (product.variants || []).some(function (variant) {
                    return String(variant).toLowerCase().indexOf(q) !== -1;
                });
                return nameMatch || flavorMatch || variantMatch;
            }
            return currentCategory === 'All Products' || product.category === currentCategory;
        });
    }

    function observeNewImages(root) {
        var images = root.querySelectorAll('img[data-src]');
        if (!images.length) return;

        function loadImg(img) {
            var src = img.getAttribute('data-src');
            if (!src) return;
            img.setAttribute('src', src);
            img.removeAttribute('data-src');
        }

        if (!('IntersectionObserver' in window)) {
            images.forEach(loadImg);
            return;
        }

        if (!imageObserver) {
            imageObserver = new IntersectionObserver(function (entries) {
                entries.forEach(function (entry) {
                    if (!entry.isIntersecting) return;
                    loadImg(entry.target);
                    imageObserver.unobserve(entry.target);
                });
            }, { rootMargin: '1600px 0px', threshold: 0.01 });
        }

        images.forEach(function (img) {
            imageObserver.observe(img);
        });
    }

    function updateCategoryCounts() {
        if (typeof productsData === 'undefined') return;
        var counts = { 'All Products': productsData.length };
        productsData.forEach(function (product) {
            counts[product.category] = (counts[product.category] || 0) + 1;
        });
        document.querySelectorAll('.sidebar-nav-item').forEach(function (item) {
            var label = (item.textContent || '').replace(/\s+/g, ' ').trim();
            var pill = item.querySelector('.item-count-pill');
            if (!pill) return;
            Object.keys(counts).forEach(function (cat) {
                if (label.indexOf(cat) !== -1) {
                    pill.textContent = String(counts[cat]);
                }
            });
        });
    }

    function makeCard(product, index, position) {
        var card = document.createElement('div');
        card.className = 'catalogue-card';
        card.setAttribute('data-category', product.category);
        var src = encodeImagePath(product.image);
        var img;
        if (position < 4) {
            img = '<img src="' + src + '" alt="' + escapeHtml(product.name) + '" width="400" height="400" decoding="async" fetchpriority="high">';
        } else if (position < 12) {
            img = '<img src="' + src + '" alt="' + escapeHtml(product.name) + '" width="400" height="400" decoding="async">';
        } else {
            img = '<img data-src="' + src + '" alt="' + escapeHtml(product.name) + '" width="400" height="400" decoding="async" loading="lazy">';
        }
        card.innerHTML =
            '<div class="catalogue-card-image">' +
                '<span class="category-tag-badge">' + escapeHtml(product.category) + '</span>' +
                img +
            '</div>' +
            '<div class="catalogue-card-content">' +
                '<h3>' + escapeHtml(product.name) + '</h3>' +
                '<div class="product-summary-text">' + buildProductSummary(product) + '</div>' +
                buildActionHtml(product, index) +
                '<span class="in-stock-badge">In stock</span>' +
            '</div>';
        return card;
    }

    function clearSentinel() {
        var grid = document.getElementById('catalogueGrid');
        if (!grid) return;
        var old = grid.querySelector('#catalogue-sentinel');
        if (old) old.remove();
        var note = grid.querySelector('.catalogue-more-note');
        if (note) note.remove();
        var empty = grid.querySelector('.catalogue-empty');
        if (empty) empty.remove();
    }

    function renderCatalogue(append) {
        var grid = document.getElementById('catalogueGrid');
        if (!grid || typeof productsData === 'undefined') return;

        var searchInput = document.getElementById('catalogueSearch');
        var query = searchInput ? searchInput.value : '';
        var list = getFilteredProducts(query);
        var total = list.length;
        var map = getIndexMap();

        if (!append) {
            renderedUntil = 0;
            visibleCount = PAGE_SIZE;
            grid.innerHTML = '';
            if (imageObserver) {
                imageObserver.disconnect();
                imageObserver = null;
            }
        } else {
            clearSentinel();
        }

        var start = renderedUntil;
        var end = Math.min(visibleCount, list.length);
        var fragment = document.createDocumentFragment();
        var newCards = document.createDocumentFragment();

        for (var i = start; i < end; i++) {
            var product = list[i];
            var key = product.name + '|' + product.category + '|' + product.image;
            var index = map[key];
            if (typeof index === 'undefined') index = productsData.indexOf(product);
            newCards.appendChild(makeCard(product, index, i));
        }

        renderedUntil = end;
        grid.appendChild(newCards);

        if (end < total) {
            var sentinel = document.createElement('div');
            sentinel.id = 'catalogue-sentinel';
            sentinel.style.cssText = 'grid-column:1/-1;height:1px;';
            fragment.appendChild(sentinel);
            var note = document.createElement('p');
            note.className = 'catalogue-more-note';
            note.style.cssText = 'grid-column:1/-1;text-align:center;color:#94a3b8;margin:8px 0 0;font-size:0.92rem;';
            note.textContent = 'Showing ' + end + ' of ' + total + ' — keep scrolling to load more.';
            fragment.appendChild(note);
            grid.appendChild(fragment);
        }

        if (!total) {
            var empty = document.createElement('p');
            empty.className = 'catalogue-empty';
            empty.style.cssText = 'grid-column:1/-1;text-align:center;color:#94a3b8;margin:24px 0;';
            empty.textContent = 'No products match this filter.';
            grid.appendChild(empty);
        }

        observeNewImages(grid);
        observeSentinel();
    }

    function observeSentinel() {
        if (sentinelObserver) {
            sentinelObserver.disconnect();
            sentinelObserver = null;
        }
        var sentinel = document.getElementById('catalogue-sentinel');
        if (!sentinel) return;
        sentinelObserver = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                visibleCount += PAGE_SIZE;
                renderCatalogue(true);
            });
        }, { rootMargin: '900px 0px' });
        sentinelObserver.observe(sentinel);
    }

    function selectCategory(cat, el) {
        currentCategory = cat;
        document.querySelectorAll('.sidebar-nav-item').forEach(function (item) {
            item.classList.remove('active');
        });
        if (el) {
            el.classList.add('active');
        }
        renderCatalogue(false);
    }

    function filterProducts() {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(function () {
            renderCatalogue(false);
        }, 120);
    }

    function openFlavorModal(index) {
        if (typeof productsData === 'undefined') return;
        var product = productsData[index];
        if (!product) return;

        var modalImg = document.getElementById('modalImg');
        var modalCat = document.getElementById('modalCat');
        var modalTitle = document.getElementById('modalTitle');
        var chipsWrap = document.getElementById('modalChips');
        var modal = document.getElementById('flavorModal');

        if (!modalImg || !modalCat || !modalTitle || !chipsWrap || !modal) return;

        modalImg.src = encodeImagePath(product.image);
        modalCat.innerText = product.category;
        modalTitle.innerText = product.name;

        chipsWrap.innerHTML = '';
        var flavors = product.flavors && product.flavors.length ? product.flavors : ['Popular In-Store Flavor Selection'];
        var frag = document.createDocumentFragment();
        flavors.forEach(function (flavor) {
            var chip = document.createElement('span');
            chip.className = 'flavor-chip-tag';
            chip.innerText = flavor;
            frag.appendChild(chip);
        });
        chipsWrap.appendChild(frag);

        modal.style.display = 'flex';
    }

    function closeFlavorModal() {
        var modal = document.getElementById('flavorModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    window.selectCategory = selectCategory;
    window.filterProducts = filterProducts;
    window.openFlavorModal = openFlavorModal;
    window.closeFlavorModal = closeFlavorModal;

    window.addEventListener('click', function (e) {
        var modal = document.getElementById('flavorModal');
        if (modal && e.target === modal) {
            closeFlavorModal();
        }
    });

    window.addEventListener('pagehide', function () {
        if (imageObserver) {
            imageObserver.disconnect();
            imageObserver = null;
        }
        if (sentinelObserver) {
            sentinelObserver.disconnect();
            sentinelObserver = null;
        }
    });

    document.addEventListener('DOMContentLoaded', function () {
        if (!document.getElementById('catalogueGrid')) return;

        function boot() {
            updateCategoryCounts();
            var params = new URLSearchParams(window.location.search);
            var category = params.get('category');
            if (category) {
                var targetCategory = category;
                if (category === 'Laptops' || category === 'Tablets & Laptops') targetCategory = 'Laptops';
                if (category === 'Vapes' || category === 'Vapes & Pod Systems') targetCategory = 'Vape Kits';
                if (category === 'Accessories') targetCategory = 'Tech Accessories';
                if (category === 'Smartphones') targetCategory = 'Smartphones';
                if (category === 'Nicotine Pouches') targetCategory = 'Nicotine Pouches';

                var foundItem = null;
                document.querySelectorAll('.sidebar-nav-item').forEach(function (item) {
                    var label = (item.textContent || '').replace(/\s+/g, ' ').trim();
                    if (label.indexOf(targetCategory) !== -1) {
                        foundItem = item;
                    }
                });

                if (foundItem) {
                    selectCategory(targetCategory, foundItem);
                    return;
                }
            }

            renderCatalogue(false);
        }

        window.requestAnimationFrame(function () {
            window.requestAnimationFrame(boot);
        });
    });
})();
