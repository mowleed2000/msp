(function () {
    'use strict';

    function isMobileNav() {
        return window.matchMedia('(max-width: 768px)').matches;
    }

    function setMenuIcon(open) {
        var btn = document.getElementById('mobileMenuBtn');
        if (!btn) return;
        var icon = btn.querySelector('i');
        if (!icon) return;
        icon.classList.toggle('fa-bars', !open);
        icon.classList.toggle('fa-xmark', open);
    }

    function closeMobileNav(navLinks) {
        if (!navLinks) return;
        navLinks.classList.remove('active', 'mobile-active');
        navLinks.style.display = '';
        document.querySelectorAll('.nav-links .dropdown').forEach(function (dropdown) {
            dropdown.classList.remove('active');
        });
        setMenuIcon(false);
    }

    function openMobileNav(navLinks) {
        navLinks.classList.add('active', 'mobile-active');
        navLinks.style.display = 'flex';
        setMenuIcon(true);
    }

    document.addEventListener('DOMContentLoaded', function () {
        var menuBtn = document.getElementById('mobileMenuBtn');
        var navLinks = document.getElementById('navLinks');
        var navbar = document.querySelector('.navbar');

        if (!menuBtn || !navLinks) return;

        menuBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            if (navLinks.classList.contains('active')) {
                closeMobileNav(navLinks);
            } else {
                openMobileNav(navLinks);
            }
        });

        navLinks.querySelectorAll('.dropdown-trigger').forEach(function (trigger) {
            trigger.addEventListener('click', function (e) {
                if (!isMobileNav()) return;

                e.preventDefault();
                e.stopPropagation();

                var parent = trigger.closest('.dropdown');
                if (!parent) return;

                var willOpen = !parent.classList.contains('active');
                navLinks.querySelectorAll('.dropdown').forEach(function (dropdown) {
                    dropdown.classList.remove('active');
                });
                if (willOpen) {
                    parent.classList.add('active');
                }
            });
        });

        navLinks.querySelectorAll('a').forEach(function (link) {
            link.addEventListener('click', function () {
                if (link.classList.contains('dropdown-trigger') && isMobileNav()) {
                    return;
                }
                closeMobileNav(navLinks);
            });
        });

        document.addEventListener('click', function (e) {
            if (!navLinks.classList.contains('active')) return;
            if (navbar && navbar.contains(e.target)) return;
            closeMobileNav(navLinks);
        });

        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                closeMobileNav(navLinks);
            }
        });
    });
})();
