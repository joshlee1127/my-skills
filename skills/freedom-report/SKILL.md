---
name: freedom-report
description: Build a branded PowerPoint deck for Freedom Systems (自由系統) using the company's own 自由系統簡報模板_2021.pptx template — its color theme, fonts, cover slide, footer/page numbers, and a large reusable IT/network icon library plus two pre-built network-topology diagram examples. Use this whenever the user asks to make a "自由報告", "自由系統簡報", client-facing 交付簡報/健檢報告簡報, an internal PPTX deck, or any presentation that should carry Freedom Systems branding — even if they just say "做一份簡報" or "output this as a deck" in a project that is clearly a Freedom Systems client engagement. Also use it when the user wants to draw a network/architecture topology diagram in PowerPoint and mentions reusing existing icons rather than drawing shapes from scratch.
---

# Freedom Report (自由系統簡報)

Builds decks on top of `assets/自由系統簡報模板_2021.pptx` — the company's real branded
PowerPoint file, not a generic template. It ships two kinds of reusable material that are
easy to miss if you only skim it as a "6-slide deck":

1. A full Office theme with ~38 slide layouts (cover, section header, content, two-content,
   comparison, blank, picture layouts…) already carrying Freedom Systems' color palette, fonts,
   footer (`© Freedom Systems Inc.`) and auto page numbers.
2. Six pre-built slides that are themselves assets: a cover, a company-intro/closing slide, a
   large IT/network icon library (servers, firewalls, switches, NAS, AD servers, wireless APs,
   data centers…), and two full network-topology diagram examples.

Read `references/template_map.md` before touching the file — it maps exactly which slide index
is which, and which layout names exist, so you don't have to re-discover this by hand each time.

## Why script it instead of hand-editing

python-pptx can't merge two `.pptx` files or copy a layout across presentations. The only way to
get Freedom Systems branding onto new content is to start from a **copy of the template file
itself** and add/edit/delete slides inside that one file — never build a blank deck and try to
import the theme in afterward, and never edit the template's own copy under this skill's
`assets/` folder (copy it into the working directory first).

## Workflow

1. **Copy the template** into the project's output location (e.g. `doc/07-交付報告/`) under a
   name that reflects this deliverable — don't overwrite the master copy in `assets/`.
2. **Inspect before building.** Run `deck_utils.list_layouts()` and `deck_utils.list_slides()`
   (see docstrings in `scripts/deck_utils.py`) against your working copy, or just read
   `references/template_map.md` if you already know which layout/slide you need.
3. **New content slides** — use `prs.slides.add_slide(find_layout(prs, "標題及內容"))` (or
   whichever layout fits the content shape — comparison, two-content, section header, etc.),
   then `set_placeholder_text()` / `add_bullets()` to fill it in. Match the layout to the content
   the way you'd pick a Markdown heading level: a section-header layout for a new topic, a
   two-content layout when you're genuinely presenting two parallel things, not by habit.
4. **Cover slide** — edit slide 0's title/subtitle placeholders directly rather than adding a new
   one; it's already positioned and styled.
5. **Architecture/topology diagrams** — never hand-draw shapes for servers, firewalls, switches,
   etc. Duplicate one of the two example topology slides (`duplicate_slide()`) if the layout is
   close to what you need, or start from a blank slide and pull individual icons across with
   `copy_shape(source_slide, dest_slide, shape_id=...)`, matching by `shape_id` from
   `list_slides()` output since many icons share the generic name `Shape NNN`.
6. **Company intro / closing slide** — if the report should end with Freedom Systems'
   introduction slide, `duplicate_slide()` slide 2 rather than rebuilding it.
7. **Clean up before delivery** — delete any slide you didn't end up needing (especially the icon
   library and whichever example topology slide you didn't use) with `delete_slide()`. A
   client-facing deck should never ship with the icon-library scratch slide still in it.
8. **Content itself is the user's** — this skill only handles branding/layout mechanics. Pull the
   actual findings/narrative from whatever source the user points at (a health-check report under
   `doc/`, notes they paste in, etc.) — never invent figures or findings to fill a slide.

## Reference

- `scripts/deck_utils.py` — `list_layouts`, `list_slides`, `find_layout`,
  `set_placeholder_text`, `add_bullets`, `duplicate_slide`, `delete_slide`, `copy_shape`. Import
  it directly (`from deck_utils import ...`) from a script placed alongside it, or add its folder
  to `sys.path`.
- `references/template_map.md` — which of the 6 shipped slides is which, and the most useful
  layout names.
- `assets/自由系統簡報模板_2021.pptx` — the master copy. Copy it; never edit it in place.

If a task needs generic PPTX manipulation beyond what's here (tables, charts, transitions), the
project's `document-skills:pptx` skill covers python-pptx mechanics in more depth — use both
together rather than duplicating that knowledge here.
