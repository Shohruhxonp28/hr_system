/* ============================================
   HRMS — Extra JavaScript utilities
   ============================================ */

// Auto-dismiss alerts after 4 seconds
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.alert').forEach(function (alert) {
        setTimeout(function () {
            var bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 4000);
    });
});

// Confirm delete links
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-confirm]').forEach(function (el) {
        el.addEventListener('click', function (e) {
            if (!confirm(el.dataset.confirm)) e.preventDefault();
        });
    });
});

// Format money inputs with spaces as thousands separator (display only)
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('input[data-money]').forEach(function (el) {
        el.addEventListener('input', function () {
            var raw = el.value.replace(/\D/g, '');
            el.value = raw;
        });
    });
});

// Active nav link highlighter (already handled in base.html via Django url_name)
// This is a fallback for any edge cases
document.addEventListener('DOMContentLoaded', function () {
    var path = window.location.pathname;
    document.querySelectorAll('.sidebar-nav a').forEach(function (link) {
        if (link.getAttribute('href') === path) {
            link.classList.add('active');
        }
    });
});

// Animate stat card numbers on page load
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.stat-value').forEach(function (el) {
        var rawText = el.textContent.trim();
        var num = parseFloat(rawText.replace(/\s/g, '').replace(/,/g, ''));
        if (isNaN(num) || num === 0) return;
        var start = 0;
        var duration = 600;
        var startTime = null;
        var isDecimal = rawText.includes('.');

        function step(timestamp) {
            if (!startTime) startTime = timestamp;
            var progress = Math.min((timestamp - startTime) / duration, 1);
            var current = Math.floor(progress * num);
            el.textContent = isDecimal
                ? current.toFixed(1)
                : current.toLocaleString('ru-RU').replace(/,/g, ' ');
            if (progress < 1) requestAnimationFrame(step);
            else el.textContent = rawText; // restore original
        }
        requestAnimationFrame(step);
    });
});

// Payroll month picker sync
document.addEventListener('DOMContentLoaded', function () {
    var monthSel = document.querySelector('select[name="month"]');
    var yearInp  = document.querySelector('input[name="year"]');
    if (monthSel && yearInp) {
        // Set current date as defaults if empty
        var now = new Date();
        if (!monthSel.value) monthSel.value = now.getMonth() + 1;
        if (!yearInp.value)  yearInp.value  = now.getFullYear();
    }
});

// Bulk attendance: highlight row on status change
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.status-select').forEach(function (sel) {
        sel.addEventListener('change', function () {
            var row = sel.closest('tr');
            row.style.background = '';
            if (sel.value === 'absent') {
                row.style.background = '#FFF5F5';
            } else if (sel.value === 'present' || sel.value === 'overtime') {
                row.style.background = '#F0FDF4';
            } else if (sel.value === 'late') {
                row.style.background = '#FFFBEB';
            } else if (sel.value === 'day_off' || sel.value === 'holiday') {
                row.style.background = '#F5F3FF';
            }
        });
    });
});

// Tooltip init (Bootstrap)
document.addEventListener('DOMContentLoaded', function () {
    var tooltipEls = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipEls.forEach(function (el) {
        new bootstrap.Tooltip(el, { trigger: 'hover' });
    });
});
