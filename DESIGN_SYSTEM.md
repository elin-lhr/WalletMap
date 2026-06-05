# Design System — myWeather

Documentazione completa del sistema di design dell'applicazione, ricavata da
[static/css/style.css](static/css/style.css) e dai template in [templates/](templates/).
Pensata per essere riutilizzata: nuovi componenti dovrebbero attingere ai token e ai
pattern qui descritti invece di introdurre valori arbitrari.

> **Stile dichiarato nel file:** `NEO-BRUTALISM × DYNAMIC CHAOS × MAXIMALIST`
> ([style.css:1-3](static/css/style.css#L1-L3)).

---

## 1. Filosofia di design

Estetica **neo-brutalista massimalista**, volutamente "caotica":

- **Bordi spessi e neri** ovunque (4px / 8px), nessun angolo arrotondato — tutto squadrato.
- **Hard shadow** (ombre piene nere/colorate senza blur, offsettate).
- **Colori saturi e accesi** a blocchi pieni (giallo, rosa, ciano, lime su carta bianca).
- **Rotazioni casuali** degli elementi (`transform: rotate(-3deg…3deg)`) per look "appiccicato a mano".
- **Tipografia urlata:** font display pesantissimi, MAIUSCOLO, letter-spacing negativo, scale enormi.
- **Texture & rumore:** overlay di grana (noise SVG) + righe diagonali sullo sfondo.
- **Animazioni glitch / scatto:** transizioni a `steps()` (scattose, non fluide), glitch del titolo,
  marquee scorrevole, jitter della temperatura, blink dei badge.
- **Cursori custom** SVG (freccia gialla / freccia rosa per gli elementi interattivi).
- **Etichette angolari** sui box (badge `::before` ruotati tipo "◆ METEO", "◤ NOW ◢", "◆ CONFERMA").
- **Interazione hover "fisica":** gli elementi si spostano (`translate(-Npx,-Npx)`) e l'ombra cresce,
  come se si sollevassero dalla pagina.

> ⚠️ **Incoerenza nota:** [templates/meteo.html](templates/meteo.html) e
> [templates/index.html (card)](templates/index.html) NON usano questo design system: sono pagine
> standalone con CSS inline in stile *glassmorphism* viola (vecchio stile, gradiente `#667eea→#764ba2`,
> blur, angoli arrotondati). Vanno considerate **legacy**; il design system ufficiale è quello
> brutalista di `style.css`. Da migrare per coerenza.

---

## 2. Design Tokens (CSS Custom Properties)

Definiti in `:root` ([style.css:7](static/css/style.css#L7)). Usare **sempre** le variabili.

### 2.1 Colori (palette fissa — nessun tema dark)

| Token | Valore | Ruolo |
|---|---|---|
| `--black` | `#0A0A0A` | Testo, bordi, ombre, sfondi navbar/footer |
| `--white` | `#FFFAEB` | Sfondo pagina (bianco "carta", leggermente caldo) |
| `--yellow` | `#FFE500` | Accento primario / highlight / badge |
| `--pink` | `#FF2E93` | Accento / azioni distruttive / alert |
| `--cyan` | `#2EC4FF` | Superfici card (info) |
| `--lime` | `#C7F500` | Superfici card alternate / successo |

I colori si usano a **blocchi pieni**, mai sfumati. Le card alternano i colori con
`:nth-child` (odd/even) per il look "patchwork".

### 2.2 Bordi

| Token | Valore | Uso |
|---|---|---|
| `--border-thick` | `4px solid var(--black)` | bordo standard di card/bottoni/input |
| `--border-extra` | `8px solid var(--black)` | bordo forte: hero, box principali, navbar bottom |

Bordi minori espliciti: `2px` / `3px solid var(--black)` per micro-elementi (badge, chip).

### 2.3 Ombre (hard shadow, senza blur)

| Token | Valore |
|---|---|
| `--shadow-brutal` | `12px 12px 0 var(--black)` |
| `--shadow-brutal-lg` | `20px 20px 0 var(--black)` |
| `--shadow-pink` | `12px 12px 0 var(--pink)` |
| `--shadow-yellow` | `12px 12px 0 var(--yellow)` |

**Pattern hover:** l'elemento fa `translate(-3…-8px, -3…-8px)` e l'ombra cresce
(es. da `6px 6px` a `12px 12px`, o cambia colore). **Pattern active:** `translate(2px,2px)` +
ombra che si riduce (effetto "premuto").

### 2.4 Transizioni

| Token | Valore | Uso |
|---|---|---|
| `--transition-hard` | `all 0.001s steps(1, end)` | cambi istantanei (nav link) — niente easing |
| `--transition-snap` | `all 0.15s cubic-bezier(0.95,0.05,0.795,0.035)` | scatto rapido su hover di card/bottoni |

Filosofia: **niente transizioni morbide**. Tutto è istantaneo o a scatto.

### 2.5 Cursori custom

`--cursor-default` (freccia gialla bordata di nero) e `--cursor-pointer` (freccia rosa,
per `a, button, .navbar-links a, .forecast-card, .detail`). SVG inline in
[style.css:23-27](static/css/style.css#L23-L27).

---

## 3. Tipografia

Tre font da Google Fonts ([style.css:5](static/css/style.css#L5)):

| Font | Ruolo | Caratteristiche d'uso |
|---|---|---|
| **Archivo Black** | Display / titoli / valori | `font-weight: 900`, MAIUSCOLO, `letter-spacing` negativo (-1…-6px), `line-height` ~0.85-0.9 |
| **Bebas Neue** | Sotto-titoli, label, nav, badge | condensato, MAIUSCOLO, `letter-spacing` positivo (2-4px) |
| **Space Grotesk** | Corpo del testo / input | pesi 500/700, è il `font-family` del `body` |

**Regole globali** ([style.css:1040](static/css/style.css#L1040)):
- `h1–h6` → Archivo Black, 900, uppercase.
- `a` → Archivo Black, 900, uppercase, niente underline; hover: sfondo nero + testo giallo.
- `body` → Space Grotesk, `font-weight: 700`, `line-height: 1`.

**Scala display** (responsive con `clamp()`):
- Hero `h1`: `clamp(52px, 9vw, 112px)` · temperatura hero: `clamp(96px, 16vw, 184px)`.
- Titoli sezione forecast: `clamp(48px, 9vw, 120px)`.
- Titoli pagina (search/history): `clamp(40px, 7vw, 84px)`.
- Valore meteo card: `clamp(56px, 14vw, 104px)`.

Trucchi tipografici ricorrenti: `transform: scaleY(1.15)` (lettere allungate),
`-webkit-text-stroke: 1px var(--black)` (contorno), `transform: skewX(-3/-4deg)` (titoli inclinati).

---

## 4. Layout

- **`.content`** — wrapper principale: `max-width: 1400px`, centrato, `padding: 60px 40px`
  (→ `30px 16px` su mobile), `z-index: 1` sopra lo sfondo.
- **`.navbar`** — sticky in alto, sfondo nero, testo bianco, `border-bottom: var(--border-extra)`;
  contiene `.navbar-brand` (con glitch animato) e `.navbar-links`. Subito sotto, un
  **marquee giallo** scorrevole (`.navbar::after`, animazione `nav-marquee`).
- **`.footer`** — sfondo nero, Archivo Black, `border-top: var(--border-extra)`, decorazione `////`.
- **Sfondo `body`** — bianco + due overlay fissi: `::before` grana/rumore (`mix-blend-mode: multiply`,
  opacity 0.18) e `::after` righe diagonali a 45°.

### Griglie

- `.city-grid` / `.profile-stats` → `grid` con `repeat(auto-fill|auto-fit, minmax(…, 1fr))`.
- `.forecast-cards` → flex orizzontale con scroll (`overflow-x: auto`) e scrollbar custom.
- `.weather-result` → flex con `flex: 2 1 380px` (card meteo) + `flex: 1 1 260px` (mini-forecast).

### Breakpoint responsive

| Larghezza | Comportamento |
|---|---|
| `≤ 768px` | navbar in colonna; `.content` padding ridotto; `.search-row` in colonna; hero temp-row in colonna; griglie/card rimpicciolite; decorazioni nascoste |
| `≤ 640px` | profilo: head in colonna, `.info-row` in colonna |

---

## 5. Componenti

### Navigazione
- `.navbar-brand` — logo bordato bianco, `skewX(-6deg)`, animazione `glitchBrand` (glitch ogni 6s).
- `.navbar-links a` — link uppercase separati da bordo; hover: sfondo giallo + `scale(1.05) skewX(-4deg)`.
- `.nav-user` — chip giallo per l'username loggato; hover rosa.
- **Marquee** — banner giallo scorrevole sotto la navbar (testo ripetuto "MYWEATHER ★ FORECAST ★ …").

### Bottoni (pattern condiviso: Archivo Black, uppercase, bordo spesso, hard shadow, hover che solleva)
- `.btn-primary` — nero/testo bianco, ombra rosa; hover → giallo/nero.
- `.btn-danger` — rosa; hover → nero/rosa. (rimozione città)
- `.btn-save` — lime; hover → giallo. ("★ Salva città")
- `.btn-logout` — nero, ombra rosa, ruotato 1°.
- `.btn-modal-cancel` (bianco→ciano) / `.btn-modal-confirm` (rosa→nero).

### Card / Box (pattern: colore pieno + `--border-thick/extra` + hard shadow + `rotate()` + hover-lift)
- `.hero` — box principale dashboard; badge `◤ NOW ◢` lampeggiante, stella rotante, titolo glitch.
- `.forecast-card` — card previsione "a caos intenzionale": ogni `:nth-child` ha rotazione,
  colore, `margin-top` e ombra hover diversi; numerate con CSS counter (`#01`, `#02`…).
- `.city-card` — scheda città salvata (ciano/lime alternati, ruotate).
- `.city-chip` — pill città (ciano → rosa su hover).
- `.weather-card` — risultato ricerca (ciano, badge `◆ METEO`).
- `.forecast-mini` / `.forecast-mini-item` — pannello "prossime ore" (righe yellow/lime alternate).
- `.stat-card` — statistiche profilo (ciano/giallo/lime).
- `.profile-card` — box account con badge `ACCOUNT` e `.profile-avatar` (iniziale, rosa, ruotato).
- `.history-item` — riga storico (ciano/lime alternati).
- `.auth-card` — box login/registrazione con finta **title-bar** stile finestra OS
  (`.win-titlebar` + `.traffic-lights` rosa/giallo/lime).

### Form & Input
- `.input-field` / `.field input` — Space Grotesk bold, bordo spesso, hard shadow;
  focus: sfondo **giallo** + `translate(-3px,-3px)` + ombra rosa.
- `.field input:invalid:not(:placeholder-shown)` — sfondo rosa (errore inline).
- `.search-form` / `.search-row` — modulo ricerca (riga input+bottone, va in colonna su mobile).
- `.error` — messaggio di validazione (badge rosa).

### Feedback & Overlay
- `.welcome` — banner saluto (lime, ruotato, con `<strong>` evidenziato nero/giallo).
- `.rain-warning` — alert pioggia: rosa, doppia ombra, animazioni `shakeAlert` + `slideInChaos`,
  badge "!" giallo, marquee "/// ALERT ///", icona lampeggiante.
- `.flash` / `.flash-error` (rosa) / `.flash-success` (lime) — messaggi flash Flask.
- `.no-result` / `.cities-empty` — stati vuoti (rosa / giallo).
- `.modal-overlay` + `.modal-box` — modale conferma: overlay scuro, box che "salta" dentro
  (`modalPop` con rimbalzo), badge `◆ CONFERMA`. Gestito via JS inline in dashboard.html
  (intercetta i `.delete-city-form`, chiude con Annulla / click-fuori / Esc).

---

## 6. Animazioni (keyframes)

| Nome | Effetto | Dove |
|---|---|---|
| `glitchBrand` / `glitchTitle` | glitch testuale periodico | brand navbar, titolo hero |
| `nav-marquee` / `marquee` | scorrimento orizzontale | banner navbar, alert |
| `heroEntry` / `titleSlide` / `cardDrop` | entrate a `steps()` | hero, titoli, forecast card |
| `starSpin` | rotazione continua | stelle decorative ★ |
| `blink` / `iconFlash` | lampeggio | badge "NOW", icona alert |
| `tempJitter` | micro-vibrazione | temperatura hero |
| `shakeAlert` / `slideInChaos` | scossa + entrata | rain-warning |
| `modalFade` / `modalPop` | dissolvenza + rimbalzo | modale conferma |

Caratteristica chiave: molte usano **`steps()`** invece di easing fluido → resa volutamente "a scatti".

> ⚠️ Non c'è `prefers-reduced-motion`: le animazioni sono sempre attive. Da valutare per
> l'accessibilità se si estende il sistema.

---

## 7. Decorazioni ricorrenti (pattern riusabili)

- **Badge angolare** via pseudo-elemento: `::before` con `content` testuale (es. `'◆ METEO'`),
  posizionato `top: -18px`, colore pieno, bordo 3px, `transform: rotate(-2deg)`.
  → usato su saved-cities, weather-card, forecast-mini, profile-card, modal-box.
- **Numerazione** con `counter-increment` / `counter-reset` (forecast card).
- **Alternanza colori** con `:nth-child(odd/even)` (city-card, info-row, history-item, forecast-mini).
- **Rotazione decorativa** leggera (`rotate(-1.5deg…1deg)`) per dare il look "incollato".

---

## 8. Stato del codice / pulizia

- `style.css` ha contenuto reale fino a ~riga 1990; alcune regole (es. blocchi AUTH e SEARCH)
  risultano **duplicate** all'interno del file. Da bonificare se si rifattorizza.
- Non esistono file JS in `static/js/` (il JS è inline in dashboard.html); il `manifest.json`
  e l'eventuale PWA citati altrove non si applicano a questo progetto.
- Pagine fuori dal design system: `meteo.html`, card di `index.html` (vedi nota §1).

---

## 9. Come estendere (linee guida)

1. **Riusa i token** (`var(--black/white/yellow/pink/cyan/lime)`, `--border-*`, `--shadow-*`,
   `--transition-*`). Niente colori o ombre hardcoded fuori palette.
2. **Ogni superficie nuova** = colore pieno + bordo nero spesso + hard shadow + leggera rotazione.
3. **Hover coerente:** `translate(-Npx,-Npx)` + ombra più grande/colorata; **active:** `translate(2px,2px)` + ombra ridotta.
4. **Testo:** titoli/valori in Archivo Black uppercase; label in Bebas Neue; corpo in Space Grotesk.
5. **Badge angolare** per etichettare i box (pattern `::before` ruotato, §7).
6. **Niente blur, niente gradienti, niente angoli arrotondati** — è l'opposto della filosofia.
7. **Responsive:** rispetta il breakpoint 768px (colonne che collassano, decorazioni nascoste).
8. ⚠️ **Non ristrutturare la dashboard** — mantenere il layout ricco esistente (hero, città salvate,
   forecast, modale); preferire modifiche additive.
