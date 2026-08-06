# Hero type size — decided by measurement

The owner asked for the headline size to be set from evidence rather than
taste. These are computed styles read off the live sites at a 1440px viewport,
not design-system documentation.

## The measurements

| site | h1 | body | ratio | weight | line-height |
|---|---|---|---|---|---|
| Cluely | 80px | 12 | 6.7× | 500 | 0.96 |
| Nike | 76px | 12 | 6.3× | 500 | 0.90 |
| Whoop | 60px | 13 | 4.6× | 300 | 1.20 |
| Uber | 52px | 16 | 3.3× | 700 | 1.23 |
| **Sporve** | **52px** | **14.5** | **3.6×** | **700** | **1.05** |
| Airbnb | 22px | 14 | 1.6× | 500 | 1.18 |
| Amboras | — | — | — | — | did not render headless |

## What the numbers actually say

**Size and weight trade against each other.** The two sites running the
largest headlines — Cluely 80px and Nike 76px — both set them at **weight
500**. A 500-weight letter has thin strokes, so it needs size to hold presence
on the page. Whoop goes further: weight **300** at 60px. Uber, at weight
**700**, needs only 52px to carry equal authority, because the strokes are
doing the work the size does elsewhere.

Ranking by size alone is therefore the wrong read. The comparison that holds
is size *at a given weight*:

```
weight 300   Whoop      60px
weight 500   Nike       76px      Cluely 80px
weight 700   Uber       52px      SPORVE 52px
```

**Sporve is already at the correct size for its weight**, and sits exactly on
Uber — which is also the closest business analogue in the set: a two-sided
marketplace whose headline is an instruction to act rather than a brand
statement.

On ratio-to-body Sporve is at 3.6×, marginally *more* dramatic than Uber's
3.3×, because its body copy is 14.5px rather than 16px.

## Verdict: keep 52px. Do not go to 64.

64px at weight 700 would land at a 4.4× ratio — past Whoop, which achieves its
drama with a face 400 units lighter. The result reads as shouting rather than
confidence, and it is the same mistake the uppercase treatment was making
before it was removed: reaching for emphasis that the typeface already
supplies.

`--text-hero` stays `clamp(32px, 3.6vw, 54px)`.

## The one number worth revisiting

Airbnb's 22px "h1" is not a marketing headline — **airbnb.com is a product
surface**, a search result page. That is the same thing Sporve's `explore`
route is, and it is a useful reminder that the hero scale belongs to marketing
pages only. Product surfaces should not inherit it, and currently do not.

## Method note

Measured with headless Chromium at 1440×900: largest visible text in the top
1400px with a non-empty text node, and the most frequent font-size among
`p / li / span / div / a` between 9 and 30px as the body figure. Nike and
Zillow needed a longer settle before their heroes rendered; Zillow never
returned usable numbers and Amboras did not render at all, so neither is in
the table. Absent data is left absent rather than estimated.
