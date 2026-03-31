# Mastermind — Pure CSS

A complete two-player [Mastermind](https://en.wikipedia.org/wiki/Mastermind_(board_game)) board game implemented entirely in HTML and CSS. No JavaScript. All game logic — color matching, feedback computation, duplicate handling, win/loss detection — runs through CSS selectors.

## How to Play

1. Open `index.html` in a modern browser
2. **Player 1** picks a secret code (4 pegs from 6 colors) and clicks "Lock In Code"
3. Hand the screen to **Player 2**
4. Player 2 guesses the code row by row, getting feedback after each guess
5. Crack the code in 10 guesses or fewer to win

### Feedback

After each guess, feedback pegs appear:

- **● (filled circle)** — correct color in the correct position ("black peg")
- **○ (hollow circle)** — correct color but wrong position ("white peg")
- Feedback is non-positional: you know *how many* are right, not *which ones*

Duplicate colors are handled correctly. If the secret has one red and you guess two reds, only one gets feedback.

## How It Works

### The Checkbox Hack

The entire game is a CSS state machine built on hidden `<input>` elements:

- **Radio buttons** for color selection (grouped by `name` attribute so each slot picks exactly one color)
- **Checkboxes** for state transitions (lock-in, submit guess)
- **Labels** provide the visual clickable interface; the actual inputs are invisible

All 275 inputs are direct children of `<body>`. This is a structural requirement — CSS sibling combinators (`~`) can only select elements that come *after* the source in the DOM and share the same parent. By placing inputs at the body level, selectors like `#s1-red:checked ~ #g1-1-red:checked` can check if both the secret and guess have the same color at position 1.

### State Machine

Three game states, toggled by checkbox `:checked` states:

```
[Setup] --lock-in checkbox--> [Playing] --submit/win/loss--> [Game Over]
```

CSS hides and shows the appropriate screen:

```css
#lock-in:checked ~ .game .setup { display: none; }
#lock-in:checked ~ .game .play  { display: block; }
```

### Black Peg Detection

For each of the 10 guess rows, CSS evaluates all 2⁴ = 16 combinations of "which positions match." A position matches if the secret and guess have the same color there. The selector uses `:has()` with a comma-separated list of all 6 possible color matches:

```css
body:has(#s1-red:checked ~ #g1-1-red:checked,
         #s1-orange:checked ~ #g1-1-orange:checked,
         #s1-yellow:checked ~ #g1-1-yellow:checked,
         #s1-green:checked ~ #g1-1-green:checked,
         #s1-blue:checked ~ #g1-1-blue:checked,
         #s1-purple:checked ~ #g1-1-purple:checked)
```

Each of the 16 match/no-match masks maps to a black peg count (0–4). The CSS shows the corresponding number of filled feedback circles. That's 160 selector groups across all 10 rows.

### White Peg Detection (the hard part)

White pegs are where this project gets interesting. The classic Mastermind formula:

```
For each color C:
  white(C) = min(count_in_secret(C), count_in_guess(C)) - black_matches(C)

total_white = sum of white(C) across all colors
```

CSS can't do arithmetic. It can't count, compare, or sum. So how do we compute this?

**Hidden helper elements + CSS counters.**

For each of the 6 colors and 4 possible contribution levels (white ≥ 1, ≥ 2, ≥ 3, ≥ 4), we place a hidden `<span>` element in the HTML. CSS rules show the helper when its condition is met. For example, `white(red) ≥ 1` means:

> At least one secret position has red and is NOT a black match,
> AND at least one guess position has red and is NOT a black match.

"Secret position 2 is red and not a black match" translates to:

```css
body:has(#s2-red:checked):not(:has(#g1-2-red:checked))
```

(Secret slot 2 is red, but guess slot 2 is NOT red — so it's not an exact position match.)

For level 1, we enumerate all pairs of (secret position, guess position) that could witness the match — 12 pairs per color (4×4 minus the 4 diagonal i=j cases which are contradictions). For level 2, we need 2 non-black positions on each side: C(4,2)² = 36 combinations. And so on.

Each visible helper element has `counter-increment: wp`, and hidden ones (display: none) don't participate in CSS counters. The total counter value equals the total white peg count. We render it using `@counter-style symbolic`, which repeats a symbol N times for counter value N:

```css
@counter-style wdots {
  system: symbolic;
  symbols: '○';
  suffix: '';
}

.wrapper::after {
  content: counter(wp, wdots);
}
```

Counter value 3 renders as `○○○`. Counter value 0 falls through to an empty fallback. This gives us the correct number of white peg indicators without any JavaScript.

Total: 3,900 white peg selectors across all 10 rows — the bulk of the 1.5MB CSS file.

### Win/Loss Detection

**Win** checks if all 4 positions match simultaneously (4 `:has()` clauses ANDed together, each containing 6 color alternatives):

```css
body:has(#submit-1:checked)
    :has(/* position 1 matches any color */)
    :has(/* position 2 matches any color */)
    :has(/* position 3 matches any color */)
    :has(/* position 4 matches any color */)
    .game .gameover { display: block; }
```

**Loss** triggers when row 10 is submitted and is NOT a win:

```css
body:has(#submit-10:checked):not(/* all 4 match */) .game .gameover { display: block; }
```

## Build

The HTML and CSS are generated by a Python script since the combinatorial selectors are far too repetitive to write by hand:

```bash
python3 generate.py
```

This produces:
- `index.html` — ~67KB, containing 275 hidden inputs and the visual layout
- `style.css` — ~1.5MB, containing ~1,280 CSS rules

No build tools, no dependencies, no npm. Just Python 3 and a browser.

## Constraints and Tradeoffs

### Why is the CSS file so large?

CSS has no variables that participate in selector logic, no loops, and no arithmetic. Every possible game state that requires a visual change needs its own selector. The white peg logic alone generates 3,900 selectors because we're exhaustively enumerating position/color combinations.

This is the fundamental tradeoff of "logic in CSS" — you're compiling a truth table into selector rules.

### Why are all inputs at the body level?

CSS's general sibling combinator (`~`) only works between siblings. If the secret radio buttons were nested inside a `<div class="secret-code">` and the guess radios inside `<div class="board">`, they couldn't reference each other with `~`. Flattening everything to the body level makes every input a sibling of every other input and of the visual layout containers.

The visual structure is maintained through `<label for="...">` elements inside styled containers. The labels reference the body-level inputs by ID, so clicking a label inside a nicely styled card still toggles the right hidden input at the body level.

### Why two-player instead of random?

CSS cannot generate random numbers. The secret code must exist in the HTML/CSS at page load. A single-player version would require either:

- Hardcoded puzzles (boring after one play)
- A tiny bit of JavaScript just for randomization
- The new CSS `random()` function (not yet widely supported)

The two-player approach sidesteps this entirely and is actually more faithful to the [original 1970 board game](https://en.wikipedia.org/wiki/Mastermind_(board_game)), which was designed for two players — a codemaker and a codebreaker.

### Can you cheat?

Yes. The secret code is in the DOM as checked radio buttons. Open DevTools, inspect the inputs, and you can see which `secret-*` radio is checked. This is inherent to any pure-CSS approach — there's no way to have client-side state that CSS can read but a human can't inspect.

The honor system applies, just like the physical board game where you could peek behind the shield.

### Why `:has()`?

`:has()` is the key CSS feature that makes this possible. Before `:has()` (which shipped in browsers in 2022–2023), CSS selectors could only style elements based on their ancestors and preceding siblings. `:has()` lets you style an element based on *any* element in the document:

```css
/* "If body contains a checked #s1-red somewhere, then style this descendant" */
body:has(#s1-red:checked) .some-descendant { ... }
```

This is what allows the feedback area (deep in the DOM) to react to the state of inputs (at the body level) without requiring those inputs to be direct siblings.

### Browser Support

Requires CSS `:has()` support:
- Chrome 105+ (Sep 2022)
- Safari 15.4+ (Mar 2022)
- Firefox 121+ (Dec 2023)

### What about performance?

The 1.5MB CSS file with 1,280 rules and extensive `:has()` usage is a stress test for browser CSS engines. In testing, modern browsers handle it fine — selector matching is fast because the selectors are highly specific (checking exact input IDs) rather than broad patterns. The page loads and responds to clicks without noticeable delay.

That said, this is firmly in "because we can" territory, not "because we should."

## Interesting CSS Techniques Used

- **Checkbox hack** — checkboxes as boolean state, radio buttons as enum state
- **`:has()` with comma-separated selectors** — OR logic (`any of these conditions`)
- **Chained `:has():has():not(:has())` on body** — AND/NOT logic
- **`@counter-style symbolic`** — renders counter value N as N repetitions of a symbol
- **CSS counters on conditionally displayed elements** — `display:none` elements don't increment counters, giving us a way to "sum" boolean conditions
- **General sibling combinator (`~`)** — forwards-only state propagation between body-level inputs

## Credits

Built at the [Recurse Center](https://www.recurse.com/), 2026.
