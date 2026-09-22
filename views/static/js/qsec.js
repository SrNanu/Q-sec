/* Q-Sec shared front-end helpers (theme, reveal, charts, glyphs). */
(function () {
    'use strict';

    const SVG_NS = 'http://www.w3.org/2000/svg';
    const QSec = {};

    /* ---------------- Physics helpers ---------------- */
    QSec.THRESHOLD = 0.11;

    QSec.entropy = function (p) {
        if (p <= 0 || p >= 1) return 0;
        return -p * Math.log2(p) - (1 - p) * Math.log2(1 - p);
    };

    QSec.keyRate = function (q) {
        return Math.max(0, 1 - 2 * QSec.entropy(q));
    };

    /**
     * Theoretical QBER for Qiskit's depolarizing_error(eps):
     * rho -> (1 - eps) rho + eps I/2  ==> bit-flip probability p = eps/2 in any basis.
     * With intercept-resend (noise applied before and after Eve):
     *   QBER = 1/2 * [2p(1-p)] + 1/2 * 1/2 = p(1-p) + 1/4
     */
    QSec.expectedQber = function (eps, hasEve) {
        const p = Math.min(Math.max(eps, 0), 1) / 2;
        return hasEve ? p * (1 - p) + 0.25 : p;
    };

    /** Sample size used by the backend for parameter estimation. */
    QSec.sampleSize = function (n) {
        return Math.min(Math.floor((n / 2) / 4), 20);
    };

    /* ---------------- DOM helpers ---------------- */
    function el(tag, attrs, parent) {
        const node = document.createElementNS(SVG_NS, tag);
        for (const k in attrs) node.setAttribute(k, attrs[k]);
        if (parent) parent.appendChild(node);
        return node;
    }
    QSec.svgEl = el;

    /** Polarization glyph: rectilinear basis (0) -> 0/90 deg, diagonal (1) -> 45/135 deg. */
    QSec.polAngle = function (bit, basis) {
        if (basis === 0) return bit === 0 ? 0 : 90;
        return bit === 0 ? 45 : 135;
    };

    QSec.polGlyph = function (bit, basis, color) {
        const a = QSec.polAngle(bit, basis);
        const c = color || 'currentColor';
        return '<svg viewBox="-8 -8 16 16" aria-hidden="true">' +
            '<g transform="rotate(' + (-a) + ')">' +
            '<line x1="-5.5" y1="0" x2="5.5" y2="0" stroke="' + c + '" stroke-width="1.6" stroke-linecap="round"/>' +
            '<path d="M5.5 0 L3.2 -1.8 M5.5 0 L3.2 1.8 M-5.5 0 L-3.2 -1.8 M-5.5 0 L-3.2 1.8" stroke="' + c + '" stroke-width="1.3" stroke-linecap="round" fill="none"/>' +
            '</g></svg>';
    };

    QSec.basisSymbol = function (b) { return b === 1 ? '×' : '+'; };

    /* ---------------- Key-rate chart ---------------- */
    /**
     * Draws R(QBER) = max(0, 1 - 2h(QBER)) with the 11% Shor-Preskill cutoff.
     * Returns an object with setPoint(qber) to move the marker.
     */
    QSec.keyRateChart = function (svg, opts) {
        opts = opts || {};
        const W = 520, H = opts.height || 260;
        const m = { t: 30, r: 18, b: 38, l: 44 };
        const xMax = opts.xMax || 0.30;
        const iw = W - m.l - m.r, ih = H - m.t - m.b;
        svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
        svg.classList.add('q-chart');
        svg.innerHTML = '';

        const uid = 'g' + Math.floor(performance.now() * 1000 % 1e6);
        const defs = el('defs', {}, svg);
        const lg = el('linearGradient', { id: uid, x1: 0, y1: 0, x2: 0, y2: 1 }, defs);
        el('stop', { offset: '0%', 'stop-color': 'var(--q-alice)', 'stop-opacity': 0.28 }, lg);
        el('stop', { offset: '100%', 'stop-color': 'var(--q-alice)', 'stop-opacity': 0 }, lg);

        const x = function (q) { return m.l + (q / xMax) * iw; };
        const y = function (r) { return m.t + (1 - r) * ih; };

        // abort zone
        el('rect', { class: 'abort-zone', x: x(QSec.THRESHOLD), y: m.t, width: x(xMax) - x(QSec.THRESHOLD), height: ih }, svg);

        // grid + ticks
        [0, 0.25, 0.5, 0.75, 1].forEach(function (r) {
            el('line', { class: 'grid', x1: m.l, x2: m.l + iw, y1: y(r), y2: y(r) }, svg);
            const t = el('text', { class: 'tick', x: m.l - 8, y: y(r) + 3, 'text-anchor': 'end' }, svg);
            t.textContent = r.toFixed(2);
        });
        for (let q = 0; q <= xMax + 1e-9; q += 0.05) {
            const t = el('text', { class: 'tick', x: x(q), y: m.t + ih + 16, 'text-anchor': 'middle' }, svg);
            t.textContent = Math.round(q * 100) + '%';
        }
        el('line', { class: 'axis', x1: m.l, x2: m.l + iw, y1: m.t + ih, y2: m.t + ih }, svg);

        const xt = el('text', { class: 'axis-title', x: m.l + iw, y: H - 4, 'text-anchor': 'end' }, svg);
        xt.textContent = 'QBER →';
        const yt = el('text', { class: 'axis-title', x: m.l, y: 10, 'text-anchor': 'start' }, svg);
        yt.textContent = 'SECRET KEY RATE R';

        // curve
        let d = '', area = '';
        const steps = 160;
        for (let i = 0; i <= steps; i++) {
            const q = (i / steps) * xMax;
            const px = x(q), py = y(QSec.keyRate(q));
            d += (i ? 'L' : 'M') + px.toFixed(2) + ' ' + py.toFixed(2);
        }
        area = d + 'L' + x(xMax) + ' ' + y(0) + 'L' + x(0) + ' ' + y(0) + 'Z';
        el('path', { d: area, fill: 'url(#' + uid + ')' }, svg);
        const curve = el('path', { class: 'curve', d: d }, svg);
        if (opts.animate !== false) {
            const len = curve.getTotalLength ? curve.getTotalLength() : 800;
            curve.style.strokeDasharray = len;
            curve.style.strokeDashoffset = len;
            curve.getBoundingClientRect();
            curve.style.transition = 'stroke-dashoffset 1.4s cubic-bezier(.22,1,.36,1)';
            requestAnimationFrame(function () { curve.style.strokeDashoffset = 0; });
        }

        // threshold
        el('line', { class: 'thresh', x1: x(QSec.THRESHOLD), x2: x(QSec.THRESHOLD), y1: m.t, y2: m.t + ih }, svg);
        const tl = el('text', { class: 'thresh-label', x: x(QSec.THRESHOLD) + 6, y: m.t + 14 }, svg);
        tl.textContent = '11% · abort';

        // marker
        const g = el('g', { style: 'transition: transform .6s cubic-bezier(.22,1,.36,1); opacity: 0' }, svg);
        const gx = el('line', { class: 'guide', x1: 0, x2: 0, y1: 0, y2: 0 }, g);
        el('circle', { class: 'pt-ring', r: 11, cx: 0, cy: 0 }, g);
        el('circle', { class: 'pt', r: 5, cx: 0, cy: 0 }, g);
        const lbl = el('text', { class: 'pt-label', x: 12, y: -12 }, g);

        function setPoint(q) {
            if (q === null || q === undefined || isNaN(q)) { g.style.opacity = 0; return; }
            const qc = Math.min(Math.max(q, 0), xMax);
            const r = QSec.keyRate(q);
            const px = x(qc), py = y(r);
            g.style.opacity = 1;
            g.style.transform = 'translate(' + px + 'px,' + py + 'px)';
            gx.setAttribute('y2', (m.t + ih) - py);
            lbl.textContent = 'R = ' + r.toFixed(3);
            const flip = px > m.l + iw - 90;
            lbl.setAttribute('x', flip ? -12 : 12);
            lbl.setAttribute('y', py < m.t + 24 ? 22 : -12);
            lbl.setAttribute('text-anchor', flip ? 'end' : 'start');
        }
        return { setPoint: setPoint };
    };

    /* ---------------- Number animation ---------------- */
    QSec.countUp = function (node, to, opts) {
        opts = opts || {};
        const dec = opts.decimals || 0, dur = opts.duration || 900, suffix = opts.suffix || '';
        const from = opts.from || 0;
        const start = performance.now();
        function tick(now) {
            const t = Math.min((now - start) / dur, 1);
            const e = 1 - Math.pow(1 - t, 3);
            node.textContent = (from + (to - from) * e).toFixed(dec) + suffix;
            if (t < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
    };

    /* ---------------- Theme ---------------- */
    function applyThemeIcon(theme) {
        const icon = document.getElementById('theme-icon');
        if (icon) icon.className = theme === 'dark' ? 'bi bi-sun' : 'bi bi-moon-stars';
    }

    document.addEventListener('DOMContentLoaded', function () {
        const root = document.documentElement;
        applyThemeIcon(root.getAttribute('data-bs-theme') || 'dark');
        const btn = document.getElementById('theme-toggle');
        if (btn) {
            btn.addEventListener('click', function () {
                const next = (root.getAttribute('data-bs-theme') === 'dark') ? 'light' : 'dark';
                root.setAttribute('data-bs-theme', next);
                try { localStorage.setItem('qsec-theme', next); } catch (e) { /* noop */ }
                applyThemeIcon(next);
            });
        }

        // Reveal-on-scroll
        const items = document.querySelectorAll('.q-reveal');
        if ('IntersectionObserver' in window) {
            const io = new IntersectionObserver(function (entries) {
                entries.forEach(function (en) {
                    if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); }
                });
            }, { threshold: 0.12 });
            items.forEach(function (n) { io.observe(n); });
        } else {
            items.forEach(function (n) { n.classList.add('is-in'); });
        }

        // Auto-dismiss flash messages
        document.querySelectorAll('.q-flash').forEach(function (f, i) {
            setTimeout(function () {
                f.style.transition = 'opacity .4s ease, transform .4s ease';
                f.style.opacity = '0';
                f.style.transform = 'translateX(16px)';
                setTimeout(function () { f.remove(); }, 450);
            }, 5000 + i * 400);
        });
    });

    window.QSec = QSec;
})();
