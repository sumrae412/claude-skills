# HTML Entity & Character Reference

## Quick Substitution Table

| If you see | Replace with | Entity | Rule |
|------------|-------------|--------|------|
| "straight double" | "curly double" | `&ldquo;` `&rdquo;` | Always curly |
| 'straight single' | 'curly single' | `&lsquo;` `&rsquo;` | Always curly |
| it's (straight) | it's (curly) | `&rsquo;` | Apostrophe = closing single |
| -- | – | `&ndash;` | En dash for ranges |
| --- | — | `&mdash;` | Em dash for breaks |
| ... | … | `&hellip;` | Single character |
| (c) | © | `&copy;` | Real symbol |
| (TM) | ™ | `&trade;` | Real symbol |
| (R) | ® | `&reg;` | Real symbol |
| 12 x 34 | 12 × 34 | `&times;` | Real multiplication |
| 56 - 12 (math) | 56 − 12 | `&minus;` | Real minus |
| 6' 10" (curly) | 6' 10" (straight) | `&#39;` `&quot;` | Foot/inch MUST be straight |

---

## Quotes and Apostrophes

```
&ldquo;   "   U+201C   opening double quote
&rdquo;   "   U+201D   closing double quote
&lsquo;   '   U+2018   opening single quote
&rsquo;   '   U+2019   closing single quote / apostrophe
&quot;    "   U+0022   straight double (inch mark only)
&#39;     '   U+0027   straight single (foot mark only)
```

## Dashes

```
-              U+002D   hyphen (compound words, line breaks)
&ndash;   –   U+2013   en dash (ranges: 1–10, connections)
&mdash;   —   U+2014   em dash (sentence breaks)
&shy;          U+00AD   soft hyphen (invisible break hint)
```

## Symbols

```
&hellip;  …   U+2026   ellipsis
&times;   ×   U+00D7   multiplication
&minus;   −   U+2212   minus
&divide;  ÷   U+00F7   division
&plusmn;  ±   U+00B1   plus-minus
&copy;    ©   U+00A9   copyright
&trade;   ™   U+2122   trademark
&reg;     ®   U+00AE   registered
&para;    ¶   U+00B6   paragraph (pilcrow)
&sect;    §   U+00A7   section
&deg;     °   U+00B0   degree
```

## Spaces

```
&nbsp;         U+00A0   nonbreaking space
&thinsp;       U+2009   thin space
&ensp;         U+2002   en space (half em)
&emsp;         U+2003   em space (full em)
&hairsp;       U+200A   hair space (thinnest)
```

## Primes (Foot/Inch)

```
&#39;     '   U+0027   foot / minute (straight single)
&quot;    "   U+0022   inch / second (straight double)
&prime;   ′   U+2032   true prime (if font supports)
&Prime;   ″   U+2033   true double prime
```

## Common Accented Characters

```
&eacute;  é    &Eacute;  É    &aacute;  á    &Aacute;  Á
&egrave;  è    &Egrave;  È    &iacute;  í    &Iacute;  Í
&oacute;  ó    &Oacute;  Ó    &uacute;  ú    &Uacute;  Ú
&uuml;    ü    &Uuml;    Ü    &ouml;    ö    &Ouml;    Ö
&ccedil;  ç    &Ccedil;  Ç    &ntilde;  ñ    &Ntilde;  Ñ
```

## Usage Patterns

```html
<!-- Quoted text -->
<p>&ldquo;She said &lsquo;hello&rsquo; to me,&rdquo; he reported.</p>

<!-- Decade abbreviations -->
<p>In the &rsquo;70s, rock &rsquo;n&rsquo; roll dominated.</p>

<!-- Ranges -->
<p>Pages 4&ndash;8</p>

<!-- Sentence breaks -->
<p>The em dash puts a pause in text&mdash;and is underused.</p>

<!-- Legal references -->
<p>Under &sect;&nbsp;1782, the seller may offer a refund.</p>

<!-- Copyright -->
<footer>&copy;&nbsp;2025 MegaCorp&trade;</footer>

<!-- Measurements -->
<p>The room is 12&#39;&nbsp;6&quot; &times; 8&#39;&nbsp;10&quot;.</p>

<!-- Math -->
<p>12 &times; 34 &minus; 56 = 352</p>
```
