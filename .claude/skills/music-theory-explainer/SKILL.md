---
name: music-theory-explainer
description: Create a self-contained interactive music theory explainer page for a song. Researches the song and artist, analyzes the music theory (key, scale, chord progression, harmonic character), writes a Strudel live coding program, and builds an index.html explainer using the established template. Use when the user wants to learn music theory through a specific song they love.
origin: local
---

# Music Theory Explainer

Create a "learn music theory through songs you love" explainer page: research the song and artist, analyze the music theory, write a Strudel program, build the interactive index.html.

## When to Activate

- User says "make an explainer for [song]"
- User wants to learn music theory through a specific song
- User has a Strudel program for a song and wants an explainer built around it
- User says "music theory explainer", "song explainer", or "learn [song] on strudel"

## Template Reference

The canonical template is at:
`/Users/jayveeabella/repos/learning/music/20260401_bahala_ka_na_by_zild/index.html`

All new explainers follow this template exactly: same CSS structure, same sidebar/section layout, same card/info/warn box components, amber accent color (`#c9a84c`).

## Output

A directory: `music/YYYYMMDD_<song_slug>_by_<artist_slug>/`
Containing: `index.html` + optional `<song>.txt` (the Strudel program)

---

## Workflow

### Step 1: Gather song info

Collect from the user:
- Song title and artist
- Any existing Strudel program (`.txt` file or pasted code)
- Any known music theory details (key, chords) — skip research if provided

If no Strudel program exists yet, note that one will be written after research.

---

### Step 2: Research (parallel agents)

Launch two agents in parallel:

**Agent A — Song & Artist research**
- Artist background, genre, bands, influences
- Song release (album, year, label)
- Title meaning / lyrical theme
- Published chord charts, tabs, key information (Ultimate-Guitar, Chordify, Songsterr)
- Any existing music theory discussion of this song

**Agent B — Strudel syntax research** (skip if user already has a working program)
- Confirm any Strudel functions needed for this song's style
- Check: `setcpm`, `note()`, `sound()`, `chord().voicing()`, `.scale()`, `gain()`, effects

Synthesize both into a music theory brief before writing any code or HTML.

---

### Step 3: Music theory analysis

From the research, determine:

| Item | What to find |
|------|-------------|
| **Key / scale** | Root + mode (e.g. C# natural minor / Aeolian) |
| **Scale degrees** | All 7 notes with degree numbers (1 2 b3 4 5 b6 b7) |
| **Chord progression** | All chords with roman numerals in key |
| **Harmonic character** | What makes it sound the way it does (leading tone? modal? extended chords?) |
| **Song structure** | Which sections use which chords |
| **Notable details** | Maj7? Borrowed chords? Pedal tones? Polyrhythm? |

Pick **2–3 focused theory concepts** to teach — don't try to teach everything. "Bahala Ka Na" taught: (1) Aeolian / no leading tone, (2) minor v vs. major V, (3) Amaj7 major/minor blur.

---

### Step 4: Write the Strudel program

If the user provided one, annotate it. If not, write one following this structure:

```javascript
setcpm(N)                          // slow tempo: 5–15 CPM

$: sound("[bd sd]*8")              // minimal drum pulse

$: note(`                          // harmonic arpeggiation
  <chord1 notes across a line>     // one cycle per line = one chord
  <chord2 notes>
  <chord3 notes>
`).sound("piano")

$: note(`                          // optional: melody / sustained chords
  <sparse notes with rests>
  -!8
`).sound("piano").gain(N)
```

**Notation reminders:**
- `@2` = note lasts 2× as long
- `-` or `~` = rest; `-!4` = four rest steps
- `[bd sd]*8` = repeat sequence 8× per cycle
- Backtick string: each line = one cycle
- `$:` = simultaneous pattern layer
- Use sharps: `C#4`, `F#3`, `G#4` (not flats, for consistency)

Save the program as `<song_slug>.txt` in the output directory.

---

### Step 5: Build index.html

Copy the structure from the template. The page has **6 sidebar sections**:

| Section | Content |
|---------|---------|
| **0 — The Song** | Artist bio, album, release year, title meaning, what the page teaches |
| **1 — Key & Scale** | Scale name + mode, scale-degree flex-row display, Aeolian vs harmonic minor comparison if relevant |
| **2 — The Chord Loop** | Chord cards (one per chord), roman numeral table, which sections use which chords |
| **3 — [Core theory concept]** | The 1–2 most interesting harmonic ideas. Name this section after the concept (e.g. "Why It Floats", "The Borrowed Chord", "The ii–V–I") |
| **4 — The Strudel Code** | Full code in `<pre><code>`, annotation cards for each logical group |
| **5 — Listen** | Live Strudel embed, things-to-try list |

#### CSS / design rules
- Copy CSS verbatim from template, change only: page title, sidebar logo text, emoji icons on nav buttons
- Accent color stays `#c9a84c` (amber) — consistent across all music explainers
- Scale-degree boxes: `.scale-box` / `.scale-box.root` (root highlighted in amber)
- Chord cards: `.chord-card` with per-chord border color classes
- Annotation cards: `.annotation` grid with `.ann-line` (amber monospace) + `.ann-text`

#### Strudel embed (Section 5)
- Include LZString: `<script src="https://cdn.jsdelivr.net/npm/lz-string@1.5.0/libs/lz-string.min.js"></script>`
- Store code as `STRUDEL_DEFAULT` array joined with `\n`
- Encode: `LZString.compressToEncodedURIComponent(code)`
- Iframe src: `https://strudel.cc/#` + encoded
- Auto-load on `DOMContentLoaded`
- Status bar below iframe: `.editor-status` div
- Stop function clears iframe to `about:blank`

#### Things to Try list (Section 5)
Always include at least 3 experiments that directly demonstrate the theory concepts taught:
- One that reveals the harmonic character (e.g. swap minor v for major V)
- One that removes a key color (e.g. drop the maj7)
- One that changes tempo or texture
- One that uses Strudel's `.scale()` or `chord().voicing()` API

---

### Step 6: Review checklist

Before marking complete:

- [ ] All scale degrees correct (count semitones, don't guess)
- [ ] All chord spellings correct (list notes explicitly)
- [ ] Roman numerals in the right key (check tonic carefully)
- [ ] Strudel code plays the right notes (cross-check note names against chords)
- [ ] `DOMContentLoaded` auto-loads the REPL
- [ ] LZString CDN included
- [ ] Nav wiring: all 6 buttons switch sections correctly
- [ ] No `encodeURIComponent` — must use `LZString.compressToEncodedURIComponent`
- [ ] Theory claims have sources (chord tabs, Wikipedia, published analysis)

---

## Section Templates

### Scale degree row (copy and fill in)
```html
<div class="scale-row">
  <div class="scale-box root"><span class="scale-note">X</span><span class="scale-deg">1 (root)</span></div>
  <div class="scale-box"><span class="scale-note">X</span><span class="scale-deg">2</span></div>
  <!-- repeat for all 7 degrees -->
</div>
```

### Chord card (copy per chord)
```html
<div class="chord-card [vi|iv|v|i|II|etc]">
  <div class="chord-name">Xmaj7</div>
  <div class="chord-roman">VI — description</div>
  <div class="chord-notes">X &nbsp; X &nbsp; X &nbsp; X</div>
  <div class="chord-role">What this chord feels like</div>
</div>
```

### Annotation card (copy per code group)
```html
<div class="annotation">
  <span class="ann-line">code snippet here</span>
  <div class="ann-text">
    <strong>What it does.</strong> Explanation connecting to the theory.
  </div>
</div>
```

### Strudel JS block (copy and fill STRUDEL_DEFAULT)
```javascript
var STRUDEL_DEFAULT = [
  'setcpm(N)',
  '...',
].join('\n');

function setStatus(msg, cls) {
  var el = document.getElementById('editor-status');
  el.textContent = msg;
  el.className = 'editor-status ' + cls;
}
function strudelRun() {
  var encoded = LZString.compressToEncodedURIComponent(STRUDEL_DEFAULT);
  document.getElementById('strudel-iframe').src = 'https://strudel.cc/#' + encoded;
  setStatus('Running — click ▶ in the Strudel frame if audio doesn\'t start automatically', 'running');
}
function strudelStop() {
  document.getElementById('strudel-iframe').src = 'about:blank';
  setStatus('Stopped', 'stopped');
}
function strudelReset() { strudelRun(); }
document.addEventListener('DOMContentLoaded', strudelRun);
```

---

## Example: "Bahala Ka Na" by Zild

The completed reference implementation:
- Directory: `music/20260401_bahala_ka_na_by_zild/`
- Key: C# natural minor (Aeolian)
- Chords: Amaj7 (VI) – F#m (iv) – G#m (v)
- Theory focus: Aeolian mode, minor v vs major V, Amaj7 major/minor blur
- Strudel program: `bahala_ka_na.txt`

---

## Common Theory Patterns to Watch For

| Pattern | What to teach |
|---------|--------------|
| Natural minor / Aeolian | No leading tone = no resolution pull; minor v not major V |
| Harmonic minor | Raised 7th creates major V with strong cadential pull |
| Dorian mode | Minor scale with raised 6th — brighter minor; common in jazz/folk |
| Mixolydian | Major scale with flat 7th — major key without strong cadence; common in rock |
| I–V–vi–IV | Pop loop; teach why it works in any starting rotation |
| ii–V–I | Jazz fundamental; dominance, tension, resolution |
| Borrowed chords | Chords from parallel minor/major; bVII in major keys is common in rock |
| Pedal tone | Sustained bass note while chords change above |
| Maj7 / min7 color | Extended chord tones; major 7th = shimmer; minor 7th = mellow |
| Chromatic passing tones | Notes outside the scale used as transitions |
