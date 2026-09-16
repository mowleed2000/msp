(function () {
    'use strict';

    var GA_ID = 'G-F5LJHL499N';
    var CLARITY_ID = 'yjc8udg3eu';

    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () {
        window.dataLayer.push(arguments);
    };

    var gaScript = document.createElement('script');
    gaScript.async = true;
    gaScript.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
    document.head.appendChild(gaScript);

    window.gtag('js', new Date());
    window.gtag('config', GA_ID, { anonymize_ip: true });

    (function (c, l, a, r, i, t, y) {
        c[a] = c[a] || function () { (c[a].q = c[a].q || []).push(arguments); };
        t = l.createElement(r);
        t.async = 1;
        t.src = 'https://www.clarity.ms/tag/' + i;
        y = l.getElementsByTagName(r)[0];
        y.parentNode.insertBefore(t, y);
    })(window, document, 'clarity', 'script', CLARITY_ID);

    function track(name, params) {
        try {
            window.gtag('event', name, params || {});
        } catch (e) { /* ignore */ }
        try {
            if (typeof window.clarity === 'function') {
                window.clarity('event', name);
            }
        } catch (e) { /* ignore */ }
    }

    function onReady(fn) {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', fn);
        } else {
            fn();
        }
    }

    onReady(function () {
        document.addEventListener('click', function (event) {
            var link = event.target && event.target.closest ? event.target.closest('a') : null;
            if (!link) return;

            var href = (link.getAttribute('href') || '').trim();
            var abs = link.href || href;

            if (href.indexOf('tel:') === 0 || abs.indexOf('tel:') === 0) {
                track('tel_click', {
                    event_category: 'contact',
                    event_label: abs,
                    value: 1
                });
                return;
            }

            if (href.indexOf('mailto:') === 0 || abs.indexOf('mailto:') === 0) {
                track('email_click', {
                    event_category: 'contact',
                    event_label: abs
                });
                return;
            }

            if (abs.indexOf('instagram.com') !== -1) {
                track('instagram_click', {
                    event_category: 'outbound',
                    event_label: abs
                });
                return;
            }

            if (abs.indexOf('deliveroo.co.uk') !== -1) {
                track('deliveroo_click', {
                    event_category: 'outbound',
                    event_label: abs
                });
                return;
            }

            if (abs.indexOf('/catalogue') !== -1) {
                track('catalogue_view', {
                    event_category: 'engagement',
                    event_label: abs
                });
            }
        }, true);

        document.addEventListener('submit', function (event) {
            var form = event.target;
            if (!form || form.tagName !== 'FORM') return;
            track('generate_lead', {
                event_category: 'lead',
                event_label: window.location.pathname
            });
            track('form_submit', {
                event_category: 'lead',
                event_label: window.location.pathname
            });
        }, true);
    });
})();
