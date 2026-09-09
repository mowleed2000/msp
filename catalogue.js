(function () {
    'use strict';

    var currentCategory = 'All Products';
    var imageObserver = null;

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

    function buildProductSummary(product) {
        if (product.flavors && product.flavors.length) {
            var shown = product.flavors.slice(0, 8);
            var extra = product.flavors.length - shown.length;
            var chips = shown.map(function (flavor) {
                return '<span class="flavor-chip-tag flavor-chip-inline">' + escapeHtml(flavor) + '</span>';
            }).join('');
            if (extra > 0) {
                chips += '<span class="flavor-chip-tag flavor-chip-more">+' + extra + ' more</span>';
            }
            return '<span class="flavour-label">Available flavours</span><div class="flavour-chip-row">' + chips + '</div>';
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
            var catMatch = currentCategory === 'All Products' || product.category === currentCategory;
            if (!q) return catMatch;
            var nameMatch = (product.name || '').toLowerCase().indexOf(q) !== -1;
            var flavorMatch = (product.flavors || []).some(function (flavor) {
                return String(flavor).toLowerCase().indexOf(q) !== -1;
            });
            var variantMatch = (product.variants || []).some(function (variant) {
                return String(variant).toLowerCase().indexOf(q) !== -1;
            });
            return catMatch && (nameMatch || flavorMatch || variantMatch);
        });
    }

    function observeImages(grid) {
        if (imageObserver) {
            imageObserver.disconnect();
            imageObserver = null;
        }

        var images = grid.querySelectorAll('img[data-src]');
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

        imageObserver = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                loadImg(entry.target);
                imageObserver.unobserve(entry.target);
            });
        }, { rootMargin: '100px 0px', threshold: 0.01 });

        images.forEach(function (img) { imageObserver.observe(img); });
    }

    function renderCatalogue() {
        var grid = document.getElementById('catalogueGrid');
        if (!grid || typeof productsData === 'undefined') return;

        var searchInput = document.getElementById('catalogueSearch');
        var query = searchInput ? searchInput.value : '';
        var list = getFilteredProducts(query);

        // Cap initial "All Products" paint so entering the page stays snappy
        var MAX_ALL = 36;
        var truncated = false;
        if (currentCategory === 'All Products' && !query && list.length > MAX_ALL) {
            list = list.slice(0, MAX_ALL);
            truncated = true;
        }

        var fragment = document.createDocumentFragment();
        // O(1) index lookup (avoid productsData.indexOf inside the loop)
        var indexMap = {};
        for (var i = 0; i < productsData.length; i++) {
            indexMap[productsData[i].name + '|' + productsData[i].category + '|' + productsData[i].image] = i;
        }

        list.forEach(function (product) {
            var key = product.name + '|' + product.category + '|' + product.image;
            var index = indexMap[key];
            if (typeof index === 'undefined') index = productsData.indexOf(product);
            var card = document.createElement('div');
            card.className = 'catalogue-card';
            card.setAttribute('data-category', product.category);
            card.setAttribute('data-name', product.name.toLowerCase());

            card.innerHTML =
                '<div class="catalogue-card-image">' +
                    '<span class="category-tag-badge">' + product.category + '</span>' +
                    '<img data-src="' + encodeImagePath(product.image) + '" alt="' + product.name.replace(/"/g, '&quot;') + '" width="400" height="400" loading="lazy" decoding="async">' +
                '</div>' +
                '<div class="catalogue-card-content">' +
                    '<h3>' + escapeHtml(product.name) + '</h3>' +
                    '<div class="product-summary-text">' + buildProductSummary(product) + '</div>' +
                    buildActionHtml(product, index) +
                    '<span class="in-stock-badge">In stock</span>' +
                '</div>';

            fragment.appendChild(card);
        });

        if (truncated) {
            var note = document.createElement('p');
            note.className = 'catalogue-more-note';
            note.style.cssText = 'grid-column:1/-1;text-align:center;color:#94a3b8;margin:8px 0 0;font-size:0.92rem;';
            note.textContent = 'Showing first ' + MAX_ALL + ' items — pick a category or search to see the rest.';
            fragment.appendChild(note);
        }

        if (!list.length) {
            var empty = document.createElement('p');
            empty.style.cssText = 'grid-column:1/-1;text-align:center;color:#94a3b8;margin:24px 0;';
            empty.textContent = 'No products match this filter.';
            fragment.appendChild(empty);
        }

        grid.innerHTML = '';
        grid.appendChild(fragment);
        observeImages(grid);
    }

    function selectCategory(cat, el) {
        currentCategory = cat;
        document.querySelectorAll('.sidebar-nav-item').forEach(function (item) {
            item.classList.remove('active');
        });
        if (el) {
            el.classList.add('active');
        }
        renderCatalogue();
    }

    function filterProducts() {
        renderCatalogue();
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
        flavors.forEach(function (flavor) {
            var chip = document.createElement('span');
            chip.className = 'flavor-chip-tag';
            chip.innerText = flavor;
            chipsWrap.appendChild(chip);
        });

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

    // Tear down observers when leaving the page so back-nav stays snappy
    window.addEventListener('pagehide', function () {
        if (imageObserver) {
            imageObserver.disconnect();
            imageObserver = null;
        }
    });

    document.addEventListener('DOMContentLoaded', function () {
        if (!document.getElementById('catalogueGrid')) return;

        function boot() {
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

            renderCatalogue();
        }

        // Yield one frame so the catalogue chrome paints before card work
        window.requestAnimationFrame(function () {
            window.requestAnimationFrame(boot);
        });
    });
})();
