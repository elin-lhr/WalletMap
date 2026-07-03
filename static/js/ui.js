/* ============================================================
   WalletMap — UI enhancements
   Sostituisce i <select> e gli <input type="date"> nativi con
   widget custom coerenti col design system brutalista.

   Principio: PROGRESSIVE ENHANCEMENT.
   Il controllo nativo resta nel DOM (nascosto) e continua a essere
   la "fonte dei dati" del form: ogni scelta dell'utente viene scritta
   sul controllo nativo, così l'invio del form, la validazione WTForms
   e il CSRF funzionano esattamente come prima. Se il JS non parte,
   l'utente vede i controlli nativi (già stilizzati via CSS).
   ============================================================ */
(function () {
    'use strict';

    // Freccia a triangolo nero (stessa del CSS dei select).
    var ARROW =
        "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' " +
        "width='24' height='24' viewBox='0 0 24 24'>" +
        "<polygon points='4,7 20,7 12,19' fill='%230A0A0A'/></svg>";

    var MESI = ['Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno',
                'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre'];
    var GIORNI = ['Lu', 'Ma', 'Me', 'Gi', 'Ve', 'Sa', 'Do'];

    // Chiude tutti i widget aperti tranne quello passato.
    function closeAll(except) {
        var open = document.querySelectorAll('.cs.cs-open');
        for (var i = 0; i < open.length; i++) {
            if (open[i] !== except) open[i].classList.remove('cs-open');
        }
    }

    function pad(n) { return (n < 10 ? '0' : '') + n; }

    /* ---------- SELECT custom ---------- */
    function initSelect(select) {
        if (select.dataset.csDone) return;
        select.dataset.csDone = '1';

        var wrap = document.createElement('div');
        wrap.className = 'cs cs-select';
        select.parentNode.insertBefore(wrap, select);
        wrap.appendChild(select);
        select.classList.add('cs-native');
        select.tabIndex = -1;

        var trigger = document.createElement('button');
        trigger.type = 'button';
        trigger.className = 'cs-trigger input-field';
        trigger.setAttribute('aria-haspopup', 'listbox');
        trigger.setAttribute('aria-expanded', 'false');
        wrap.appendChild(trigger);

        var label = document.createElement('span');
        label.className = 'cs-value';
        trigger.appendChild(label);

        var arrow = document.createElement('span');
        arrow.className = 'cs-arrow';
        arrow.style.backgroundImage = 'url("' + ARROW + '")';
        trigger.appendChild(arrow);

        var panel = document.createElement('div');
        panel.className = 'cs-panel';
        panel.setAttribute('role', 'listbox');
        wrap.appendChild(panel);

        var options = Array.prototype.slice.call(select.options);
        var active = -1;

        options.forEach(function (opt, i) {
            var item = document.createElement('div');
            item.className = 'cs-option';
            item.setAttribute('role', 'option');
            item.textContent = opt.textContent;
            item.addEventListener('click', function () {
                choose(i);
                close();
                trigger.focus();
            });
            panel.appendChild(item);
        });

        function sync() {
            var opt = select.options[select.selectedIndex];
            label.textContent = opt ? opt.textContent : '';
            var items = panel.children;
            for (var i = 0; i < items.length; i++) {
                items[i].classList.toggle('is-selected', i === select.selectedIndex);
            }
        }

        function choose(i) {
            select.selectedIndex = i;
            select.dispatchEvent(new Event('change', { bubbles: true }));
            sync();
        }

        function paintActive() {
            var items = panel.children;
            for (var i = 0; i < items.length; i++) {
                items[i].classList.toggle('is-active', i === active);
            }
        }

        function open() {
            closeAll(wrap);
            wrap.classList.add('cs-open');
            trigger.setAttribute('aria-expanded', 'true');
            active = select.selectedIndex >= 0 ? select.selectedIndex : 0;
            paintActive();
        }
        function close() {
            wrap.classList.remove('cs-open');
            trigger.setAttribute('aria-expanded', 'false');
        }

        trigger.addEventListener('click', function () {
            wrap.classList.contains('cs-open') ? close() : open();
        });

        trigger.addEventListener('keydown', function (e) {
            if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                e.preventDefault();
                if (!wrap.classList.contains('cs-open')) { open(); return; }
                active += (e.key === 'ArrowDown' ? 1 : -1);
                active = Math.max(0, Math.min(options.length - 1, active));
                paintActive();
            } else if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                if (wrap.classList.contains('cs-open')) {
                    if (active >= 0) choose(active);
                    close();
                } else {
                    open();
                }
            } else if (e.key === 'Escape') {
                close();
            }
        });

        sync();
    }

    /* ---------- DATE custom ---------- */
    function initDate(input) {
        if (input.dataset.csDone) return;
        input.dataset.csDone = '1';

        var wrap = document.createElement('div');
        wrap.className = 'cs cs-date';
        input.parentNode.insertBefore(wrap, input);
        wrap.appendChild(input);
        input.classList.add('cs-native');
        input.tabIndex = -1;

        var trigger = document.createElement('button');
        trigger.type = 'button';
        trigger.className = 'cs-trigger input-field';
        wrap.appendChild(trigger);

        var label = document.createElement('span');
        label.className = 'cs-value';
        trigger.appendChild(label);

        var chip = document.createElement('span');
        chip.className = 'cs-cal-icon';
        chip.textContent = '📅';
        trigger.appendChild(chip);

        var panel = document.createElement('div');
        panel.className = 'cs-panel cs-cal';
        wrap.appendChild(panel);

        var view; // primo giorno del mese visualizzato

        function parse() {
            if (!input.value) return null;
            var p = input.value.split('-');
            return new Date(+p[0], +p[1] - 1, +p[2]);
        }
        function iso(d) {
            return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
        }
        function human(d) {
            return pad(d.getDate()) + '/' + pad(d.getMonth() + 1) + '/' + d.getFullYear();
        }

        function sync() {
            var d = parse();
            label.textContent = d ? human(d) : 'gg/mm/aaaa';
            trigger.classList.toggle('is-placeholder', !d);
        }

        function render() {
            panel.innerHTML = '';

            var head = document.createElement('div');
            head.className = 'cs-cal-head';

            var prev = document.createElement('button');
            prev.type = 'button';
            prev.className = 'cs-cal-nav';
            prev.textContent = '‹';
            prev.addEventListener('click', function (e) {
                e.stopPropagation();
                view.setMonth(view.getMonth() - 1);
                render();
            });

            var title = document.createElement('span');
            title.className = 'cs-cal-title';
            title.textContent = MESI[view.getMonth()] + ' ' + view.getFullYear();

            var next = document.createElement('button');
            next.type = 'button';
            next.className = 'cs-cal-nav';
            next.textContent = '›';
            next.addEventListener('click', function (e) {
                e.stopPropagation();
                view.setMonth(view.getMonth() + 1);
                render();
            });

            head.appendChild(prev);
            head.appendChild(title);
            head.appendChild(next);
            panel.appendChild(head);

            var grid = document.createElement('div');
            grid.className = 'cs-cal-grid';

            GIORNI.forEach(function (g) {
                var c = document.createElement('div');
                c.className = 'cs-cal-dow';
                c.textContent = g;
                grid.appendChild(c);
            });

            var first = new Date(view.getFullYear(), view.getMonth(), 1);
            var offset = (first.getDay() + 6) % 7; // lunedì = 0
            var days = new Date(view.getFullYear(), view.getMonth() + 1, 0).getDate();

            var selected = parse();
            var today = new Date();
            today.setHours(0, 0, 0, 0);

            for (var b = 0; b < offset; b++) {
                var blank = document.createElement('div');
                blank.className = 'cs-cal-day is-empty';
                grid.appendChild(blank);
            }

            for (var day = 1; day <= days; day++) {
                var cell = document.createElement('button');
                cell.type = 'button';
                cell.className = 'cs-cal-day';
                cell.textContent = day;
                var cellDate = new Date(view.getFullYear(), view.getMonth(), day);

                if (selected &&
                    cellDate.getTime() === new Date(selected.getFullYear(),
                        selected.getMonth(), selected.getDate()).getTime()) {
                    cell.classList.add('is-selected');
                }
                if (cellDate.getTime() === today.getTime()) {
                    cell.classList.add('is-today');
                }

                (function (d) {
                    cell.addEventListener('click', function (e) {
                        e.stopPropagation();
                        input.value = iso(d);
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                        sync();
                        close();
                    });
                })(cellDate);

                grid.appendChild(cell);
            }

            panel.appendChild(grid);
        }

        function open() {
            closeAll(wrap);
            var base = parse() || new Date();
            view = new Date(base.getFullYear(), base.getMonth(), 1);
            render();
            wrap.classList.add('cs-open');
        }
        function close() {
            wrap.classList.remove('cs-open');
        }

        trigger.addEventListener('click', function () {
            wrap.classList.contains('cs-open') ? close() : open();
        });
        trigger.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                wrap.classList.contains('cs-open') ? close() : open();
            } else if (e.key === 'Escape') {
                close();
            }
        });

        sync();
    }

    /* ---------- MODALI (pop-up dettaglio) ---------- */
    function openModal(overlay) {
        overlay.classList.add('is-open');
        overlay.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
    }
    function closeModal(overlay) {
        overlay.classList.remove('is-open');
        overlay.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    }

    function initModals() {
        // Trigger: qualsiasi elemento con data-modal="id-di-un-overlay"
        var triggers = document.querySelectorAll('[data-modal]');
        for (var i = 0; i < triggers.length; i++) {
            (function (trigger) {
                var overlay = document.getElementById(trigger.getAttribute('data-modal'));
                if (!overlay) return;
                trigger.addEventListener('click', function () { openModal(overlay); });
                trigger.addEventListener('keydown', function (e) {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        openModal(overlay);
                    }
                });
            })(triggers[i]);
        }

        // Chiusura: click sullo sfondo o sul pulsante ✕
        var overlays = document.querySelectorAll('.detail-overlay');
        for (var j = 0; j < overlays.length; j++) {
            (function (overlay) {
                overlay.addEventListener('click', function (e) {
                    if (e.target === overlay) closeModal(overlay);
                });
                var closers = overlay.querySelectorAll('[data-close]');
                for (var k = 0; k < closers.length; k++) {
                    closers[k].addEventListener('click', function () { closeModal(overlay); });
                }
            })(overlays[j]);
        }

        // Esc chiude qualsiasi modale aperta
        document.addEventListener('keydown', function (e) {
            if (e.key !== 'Escape') return;
            var open = document.querySelectorAll('.detail-overlay.is-open');
            for (var m = 0; m < open.length; m++) closeModal(open[m]);
        });
    }

    /* ---------- MODIFICA LISTA SPESA (righe dinamiche) ---------- */
    function initListaEdit() {
        // Aggiungi una riga prodotto vuota
        var adders = document.querySelectorAll('.lista-add-row');
        for (var i = 0; i < adders.length; i++) {
            (function (btn) {
                btn.addEventListener('click', function () {
                    var form = btn.closest('.lista-edit-form');
                    if (!form) return;
                    var rows = form.querySelector('.lista-rows');
                    var row = document.createElement('div');
                    row.className = 'lista-row';
                    row.innerHTML =
                        '<input type="text" name="nome_prodotto" class="lista-input lista-name" placeholder="Prodotto">' +
                        '<input type="text" name="prezzo_prodotto" class="lista-input lista-price" placeholder="0.00" inputmode="decimal">' +
                        '<button type="button" class="lista-row-del" aria-label="Rimuovi prodotto">✕</button>';
                    rows.appendChild(row);
                    row.querySelector('.lista-name').focus();
                });
            })(adders[i]);
        }

        // Rimuovi riga (delegazione: vale anche per le righe aggiunte dopo)
        var containers = document.querySelectorAll('.lista-rows');
        for (var c = 0; c < containers.length; c++) {
            containers[c].addEventListener('click', function (e) {
                var del = e.target.closest('.lista-row-del');
                if (del) del.closest('.lista-row').remove();
            });
        }

        // Feedback durante la ristima AI (senza disabilitare: il value resta inviato)
        var reest = document.querySelectorAll('.lista-reestimate');
        for (var r = 0; r < reest.length; r++) {
            (function (btn) {
                btn.addEventListener('click', function () {
                    btn.textContent = 'Stima in corso…';
                });
            })(reest[r]);
        }
    }

    /* ---------- MOSTRA/NASCONDI PASSWORD ---------- */
    function initPasswordToggle() {
        var toggles = document.querySelectorAll('[data-password-toggle]');
        for (var i = 0; i < toggles.length; i++) {
            (function (btn) {
                btn.addEventListener('click', function () {
                    var wrap = btn.closest('.password-wrap');
                    var input = wrap ? wrap.querySelector('input') : null;
                    if (!input) return;
                    var mostra = input.type === 'password';
                    input.type = mostra ? 'text' : 'password';
                    btn.classList.toggle('is-on', mostra);   // is-on = password visibile → occhio barrato
                    btn.setAttribute('aria-label', mostra ? 'Nascondi password' : 'Mostra password');
                });
            })(toggles[i]);
        }
    }

    /* ---------- MENU HAMBURGER (mobile) ---------- */
    function initNavToggle() {
        var btn = document.querySelector('[data-nav-toggle]');
        if (!btn) return;
        var navbar = btn.closest('.navbar');
        if (!navbar) return;
        btn.addEventListener('click', function (e) {
            e.stopPropagation();
            var open = navbar.classList.toggle('nav-open');
            btn.setAttribute('aria-expanded', open ? 'true' : 'false');
        });
        // Tap fuori dalla navbar: chiude il menu
        document.addEventListener('click', function (e) {
            if (navbar.classList.contains('nav-open') && !navbar.contains(e.target)) {
                navbar.classList.remove('nav-open');
                btn.setAttribute('aria-expanded', 'false');
            }
        });
    }

    function init() {
        initNavToggle();
        var selects = document.querySelectorAll('select.input-field');
        for (var i = 0; i < selects.length; i++) initSelect(selects[i]);

        var dates = document.querySelectorAll('input[type="date"].input-field');
        for (var j = 0; j < dates.length; j++) initDate(dates[j]);

        initModals();
        initListaEdit();
        initPasswordToggle();

        // Un click fuori da qualsiasi widget li chiude tutti.
        document.addEventListener('click', function (e) {
            if (!e.target.closest('.cs')) closeAll(null);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
