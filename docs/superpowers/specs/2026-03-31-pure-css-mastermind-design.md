# Pure CSS Mastermind — Design Spec

## Overview

A two-player Mastermind board game implemented entirely in HTML and CSS (zero JavaScript). Player 1 sets a secret 4-peg code from 6 colors. Player 2 gets 10 guesses with full black/white peg feedback computed by CSS selectors. All game logic uses the checkbox hack, `:checked` selectors, sibling combinators, and `:has()`.

## Rules (Classic Mastermind)

- **Colors**: 6 — Red, Orange, Yellow, Green, Blue, Purple
- **Code length**: 4 pegs
- **Guesses**: 10 attempts
- **Feedback per guess**:
  - **Black peg**: correct color in correct position
  - **White peg**: correct color in wrong position (respecting duplicate counting)
  - **Empty**: no match
- **Feedback is non-positional**: black and white pegs are shown as counts (e.g., 2 black, 1 white) — they do NOT reveal which guess positions are correct. This matches classic Mastermind rules.
- **Win**: Player 2 guesses the exact code (4 black pegs)
- **Loss**: Player 2 exhausts all 10 guesses without an exact match

### Duplicate Counting Rule

Feedback pegs respect duplicate colors. For each color, the number of white pegs equals `min(count_in_secret, count_in_guess) - black_matches_for_that_color`.

Example: secret (Red, Red, Blue, Green), guess (Red, Blue, Blue, Yellow):
- Position 1: Secret=Red, Guess=Red → black peg
- Position 3: Secret=Blue, Guess=Blue → black peg
- Remaining secret: {Red (pos 2), Green (pos 4)}. Remaining guess: {Blue (pos 2), Yellow (pos 4)}.
- No remaining guess color matches a remaining secret color.
- **Result: 2 black, 0 white, 2 empty.**

## Game Flow (CSS State Machine)

Three states driven by checkbox toggles:

### State 1: Setup

- Player 1 sees 4 peg slots, each with 6 color options (radio buttons styled as colored circles).
- Player 1 selects one color per slot to form the secret code.
- The "Lock In Code" button is hidden until all 4 slots have a selection.
- A "Lock In Code" checkbox transitions to the Playing state.
- The guessing board is hidden during setup via CSS.

**Validation selector:**
```css
.lock-in-btn { display: none; }
body:has([name="secret-1"]:checked)
    :has([name="secret-2"]:checked)
    :has([name="secret-3"]:checked)
    :has([name="secret-4"]:checked)
    .lock-in-btn { display: block; }
```

### State 2: Playing

- The secret code section is hidden (CSS `display: none` or overlay).
- Player 2 sees guess rows, revealed one at a time (only row 1 visible initially).
- Each guess row has 4 peg slots with 6 color radio buttons each.
- Each row has a "Submit Guess" checkbox (hidden until all 4 slots filled).
- When submitted, CSS displays feedback and reveals the next row.
- Submitted rows are locked via `pointer-events: none`.
- If all 4 pegs match exactly, transition to Game Over (win).
- If row 10 is submitted without an exact match, transition to Game Over (loss).

**Row progression selectors:**
```css
/* All rows hidden by default except row 1 */
.guess-row { display: none; }
#row-1 { display: flex; }

/* Reveal next row when current is submitted */
#submit-1:checked ~ .board #row-2 { display: flex; }
#submit-2:checked ~ .board #row-3 { display: flex; }
/* ... etc */

/* Lock submitted rows */
#submit-1:checked ~ .board #row-1 { pointer-events: none; }
/* ... etc */

/* Submit button hidden until all 4 slots filled */
.submit-btn { display: none; }
body:has([name="guess-1-1"]:checked)
    :has([name="guess-1-2"]:checked)
    :has([name="guess-1-3"]:checked)
    :has([name="guess-1-4"]:checked)
    #row-1 .submit-btn { display: block; }
```

### State 3: Game Over

- The secret code is revealed.
- A win or loss message is displayed.
- All remaining guess rows are hidden or disabled.

**Win detection:**
```css
/* Win: all 4 positions match. Each :has() checks if ANY of the 6 colors
   match in that position (comma-separated selector list inside :has). */
body:has(#s1-red:checked ~ .board #g1-1-red:checked,
         #s1-orange:checked ~ .board #g1-1-orange:checked,
         #s1-yellow:checked ~ .board #g1-1-yellow:checked,
         #s1-green:checked ~ .board #g1-1-green:checked,
         #s1-blue:checked ~ .board #g1-1-blue:checked,
         #s1-purple:checked ~ .board #g1-1-purple:checked)
    :has(/* same for position 2 */)
    :has(/* same for position 3 */)
    :has(/* same for position 4 */)
    .game-over .win-message { display: block; }
```

This is 4 `:has()` clauses with 6-option comma lists each — 1 selector per row, 10 total.

**Loss detection:**
```css
/* Loss: row 10 submitted, win message not active */
#submit-10:checked ~ .game-over .loss-message { display: block; }
/* Win message overrides loss via higher specificity or later order */
```

## HTML Structure

All inputs (radio buttons and checkboxes) are direct children of `<body>` so that sibling combinators (`~`) can reach any element later in the document. Visual containers hold only `<label>` elements that reference the inputs via `for` attributes.

```html
<body>
  <!-- State checkboxes -->
  <input type="checkbox" id="lock-in">
  <input type="checkbox" id="submit-1">
  <input type="checkbox" id="submit-2">
  ...
  <input type="checkbox" id="submit-10">

  <!-- Secret code radios (4 slots x 6 colors = 24 inputs) -->
  <input type="radio" name="secret-1" id="s1-red" value="red">
  <input type="radio" name="secret-1" id="s1-orange" value="orange">
  <input type="radio" name="secret-1" id="s1-yellow" value="yellow">
  <input type="radio" name="secret-1" id="s1-green" value="green">
  <input type="radio" name="secret-1" id="s1-blue" value="blue">
  <input type="radio" name="secret-1" id="s1-purple" value="purple">
  <!-- ... secret-2, secret-3, secret-4 -->

  <!-- Guess radios (10 rows x 4 slots x 6 colors = 240 inputs) -->
  <input type="radio" name="guess-1-1" id="g1-1-red" value="red">
  <input type="radio" name="guess-1-1" id="g1-1-orange" value="orange">
  <!-- ... all guess inputs for all rows -->

  <!-- Visual layout (labels only) -->
  <div class="secret-code">
    <div class="slot">
      <label for="s1-red" class="color red"></label>
      <label for="s1-orange" class="color orange"></label>
      <!-- ... -->
    </div>
    <!-- ... 3 more slots -->
    <label for="lock-in" class="lock-in-btn">Lock In Code</label>
  </div>

  <div class="board">
    <div class="guess-row" id="row-1">
      <div class="slot">
        <label for="g1-1-red" class="color red"></label>
        <!-- ... -->
      </div>
      <!-- ... 3 more slots -->
      <label for="submit-1" class="submit-btn">Submit</label>
      <div class="feedback">
        <!-- Non-positional: show count of black/white pegs -->
        <!-- Multiple spans, CSS shows correct count configuration -->
        <span class="fb" data-type="black">&#9679;</span>
        <span class="fb" data-type="black">&#9679;</span>
        <span class="fb" data-type="black">&#9679;</span>
        <span class="fb" data-type="black">&#9679;</span>
        <span class="fb" data-type="white">&#9675;</span>
        <span class="fb" data-type="white">&#9675;</span>
        <span class="fb" data-type="white">&#9675;</span>
        <span class="fb" data-type="white">&#9675;</span>
      </div>
    </div>
    <!-- ... 9 more rows -->
  </div>

  <div class="game-over">
    <div class="win-message">You cracked the code!</div>
    <div class="loss-message">Out of guesses!</div>
    <div class="secret-reveal">
      <!-- Labels showing secret code colors -->
    </div>
  </div>
</body>
```

### Feedback Display Strategy

Each feedback area has 4 black peg spans and 4 white peg spans, all hidden by default. CSS rules show/hide the correct number based on the guess-vs-secret comparison:

- 0 black: all black spans hidden
- 1 black: `.fb[data-type="black"]:nth-of-type(1)` shown
- 2 black: first 2 shown
- etc.

Same for white pegs. This avoids positional correlation — the player just sees "2 black, 1 white" without knowing which positions.

## Feedback Logic (CSS Implementation)

### Approach: Lookup Table via Enumeration

CSS cannot dynamically count or do arithmetic. Instead, the build script generates selectors for every possible secret/guess combination that produces each feedback result.

However, enumerating all 6^4 x 6^4 = 1,679,616 pairs is impractical. Instead, we decompose:

### Black Peg Detection

Per-position, per-color. Since all inputs are body-level siblings:

```css
/* Secret slot 1 is red AND guess row 1 slot 1 is red → 1 black match at position 1 */
#s1-red:checked ~ #g1-1-red:checked ~ .board #row-1 .feedback ...
```

But we need black peg COUNTS, not positional feedback. We enumerate the 2^4 = 16 combinations of "which positions match" for each row:

- 0 positions match: no black pegs
- Position 1 only matches: 1 black peg
- Positions 1 and 3 match: 2 black pegs
- etc.

For "position N matches," the selector checks if ANY of the 6 colors match at that position. Using `:has()`:

```css
/* Define: position 1 matches ≡ same color in secret-1 and guess-R-1 */
/* We can test this with: */
body:has(#s1-red:checked ~ #gR-1-red:checked,
         #s1-orange:checked ~ #gR-1-orange:checked,
         #s1-yellow:checked ~ #gR-1-yellow:checked,
         #s1-green:checked ~ #gR-1-green:checked,
         #s1-blue:checked ~ #gR-1-blue:checked,
         #s1-purple:checked ~ #gR-1-purple:checked)
```

To count exactly N black pegs, we combine match/no-match for each position. Example — exactly 2 black (positions 1 and 3):

```css
body:has(/* pos 1 matches */):not(:has(/* pos 2 matches */)):has(/* pos 3 matches */):not(:has(/* pos 4 matches */))
```

16 combinations per row x 10 rows = 160 selectors for black peg counting.

### White Peg Detection

This is the hardest part. After determining black pegs, white pegs are calculated per-color:

For each color C: `white_from_C = min(secret_count_C, guess_count_C) - black_count_C`

Since there are 4 positions and 6 colors, each color appears 0-4 times in the secret and 0-4 times in the guess. We enumerate:

For a given color, the possible (secret_count, guess_count, black_count) triples are constrained: black_count ≤ min(secret_count, guess_count). The white contribution is `min(s, g) - b`.

The build script will:

1. For each row, for each of the 6 colors, enumerate which secret positions have that color and which guess positions have that color.
2. Compute black matches (positions where both have that color).
3. Compute white = min(s_count, g_count) - black_for_color.
4. Sum whites across all 6 colors.
5. Emit a selector that checks the exact configuration and shows the correct total white peg count.

Since we're checking specific color assignments across positions, the selectors use `:has()` with specific `#id:checked` checks. The build script generates these by iterating all configurations.

**Estimated selector count**: The total feedback (black + white count pair) has limited possible values: (0,0), (0,1), (0,2), (0,3), (0,4), (1,0), (1,1), (1,2), (1,3), (2,0), (2,1), (2,2), (3,0), (4,0) — 14 possible outcomes. But each outcome maps to many secret/guess configurations. The build script groups these and generates one selector per (secret-configuration-class, guess-configuration-class) → (black, white) mapping.

A practical simplification: rather than enumerate all 1,679,616 pairs, the script can:
- Compute black count from position matches (16 combos as above)
- For white count, enumerate per-color frequency patterns in the secret and guess
- Since we only have 4 positions and 6 colors, frequency distributions are bounded

The build script will calculate exact selector counts during generation. Expected: thousands to tens of thousands of selectors. The CSS file may be large (hundreds of KB) but browsers can handle it.

## Visual Design

- **Layout**: Centered vertical board, secret code at top (hidden during play), guess rows below.
- **Color pegs**: 30px circles with distinct, accessible colors.
  - Red: `#E74C3C`
  - Orange: `#E67E22`
  - Yellow: `#F1C40F`
  - Green: `#27AE60`
  - Blue: `#2980B9`
  - Purple: `#8E44AD`
- **Feedback pegs**: small circles in a 2x2 grid — black filled, white outlined, empty gray.
- **Board**: Dark background, each row in a lighter card.
- **Radio buttons**: Hidden (`position: absolute; opacity: 0`). Labels styled as colored circles with hover/selected states (ring or scale).
- **Selected peg display**: Each slot shows the selected color as a filled circle (using `:checked` + adjacent label or `:has()` styling).
- **Game state transitions**: CSS transitions on opacity/transform for smooth reveals.

## CSS Techniques Used

- **Checkbox hack**: Checkboxes as boolean state toggles for game flow.
- **`:checked` + `~` (general sibling combinator)**: Core logic for inputs at body level.
- **`:has()`**: Parent-context-aware selectors for feedback logic and validation.
- **`:has()` with comma-separated selector lists**: For "any color matches at position N."
- **`pointer-events: none`**: Disable interaction on submitted rows.
- **`appearance: none`**: Hide native form elements.
- **CSS transitions**: Smooth state changes.
- **Data attributes + `:nth-of-type()`**: For showing correct count of feedback pegs.

## Build Process

A shell script (`generate.sh`) generates both the HTML and CSS:

### Generated HTML
- 11 checkboxes (1 lock-in + 10 submit)
- 264 radio buttons (24 secret + 240 guess)
- Visual layout with labels referencing all inputs
- Feedback spans for each row

### Generated CSS
- Base styles (layout, colors, animations) — hand-written
- State transition rules — hand-written
- Black peg count selectors: ~160 rules (16 combos x 10 rows)
- White peg count selectors: generated by enumerating configurations
- Win detection: 10 selectors (1 per row)
- Loss detection: 1 selector
- Validation selectors: ~20 rules (lock-in + submit visibility)
- Row progression: 10 rules

The generated CSS is committed to the repo (no runtime generation needed).

## Browser Requirements

- CSS `:has()` support: Chrome 105+, Safari 15.4+, Firefox 121+
- `:has()` with comma-separated selector lists (same versions)
- No JavaScript required
- No CSS preprocessor required at runtime

## File Structure

```
mastermind-css/
  index.html          — the game (generated)
  style.css           — base styles (hand-written)
  feedback.css        — generated feedback selectors
  generate.sh         — build script to generate HTML and CSS
  docs/               — specs and documentation
```

## Limitations

- The secret code exists in the DOM — Player 2 could inspect source to cheat. This is inherent to any pure-CSS approach.
- No randomness — this is a two-player game by design.
- Large CSS file due to combinatorial feedback selectors (potentially hundreds of KB).
- Requires modern browser with `:has()` support.
- No "new game" button — reload the page to play again.
