# Resume Rulebook — ATS, Recruiter, and Naukri

> Source material: public documentation, blog posts, and recruiter surveys from
> **Jobscan**, **Enhancv**, **Resume Worded**, **Workday**, **Greenhouse**,
> **Lever**, **Taleo** community notes, **LinkedIn Talent Solutions**,
> **Naukri Help Center**, **Shine**, **Indeed**, and recruiter forums
> (r/recruiting, r/resumes, Blind). The rules below are the *consensus* used
> by this tool's scorer. They are not official specifications — ATS vendors
> do not publish exact scoring algorithms.

---

## Why this exists

A resume has to clear **three** filters before a human reads it:

1. **ATS parser** — can it extract clean text?
2. **ATS scorer / search match** — do your keywords match the Job Description?
3. **Recruiter 7-second scan** — can they spot the right signals fast?

A fourth filter exists in India for jobs applied via Naukri:

4. **Naukri profile search** — recruiters search the Naukri database first,
   not your resume file. Your *profile fields* decide if they ever see you.

This runbook codifies all four.

---

## 1. ATS parsing rules (format must survive the parser)

| # | Rule | Why | Automated check |
|---|---|---|---|
| 1.1 | Use `.docx` or **text-based** `.pdf` | Scanned PDFs are images → zero keywords | `parseability.text_extractable` |
| 1.2 | Fonts: Calibri, Arial, Helvetica, Times, Georgia, Cambria, Garamond, Verdana, Tahoma, Palatino, Roboto, Open Sans, Lato, Source Sans Pro, Noto Sans | Unusual fonts break glyph extraction | (manual) |
| 1.3 | Body size 10–12 pt, name 14–22 pt | <9 pt may be skipped by parser | (manual) |
| 1.4 | **Single-column** layout | Multi-column PDFs often parse as scrambled text | (manual) |
| 1.5 | Contact info in the **body**, not Word header/footer | Many ATS skip header/footer text | `contact.contact` |
| 1.6 | No photos, no logos, no icon graphics | Parsers ignore images; text near them can be lost | `parseability.no_images` |
| 1.7 | Avoid complex / nested tables | Cells get reordered during extraction | (flagged) |
| 1.8 | Bullets: `•`, `-`, or numbered | Emojis / Wingdings don't register as bullets | `metrics.metrics` |
| 1.9 | Section titles in standard English: **Summary, Skills, Experience, Education, Certifications, Projects** | ATS section detectors match these literals | `structure.sections` |
| 1.10 | Dates as `MMM YYYY – MMM YYYY` (e.g. `Jul 2023 – Present`) | Recruiter search filters parse this format | `dates_format.dates_fmt` |
| 1.11 | Spell URLs fully (`linkedin.com/in/foo`) alongside the link | Some ATS lose the href | `contact.contact` |
| 1.12 | Length: 1 page (0–3 yrs), 2 pages (3–10 yrs), ≤3 (10+ yrs) | Recruiter preference + ATS truncation risk | `parseability.page_count` |
| 1.13 | File name: `FirstName_LastName_Resume.docx` | Appears in ATS candidate list; aids search | (manual) |
| 1.14 | File size ≤ 2 MB | Some portals cap uploads at 2 MB | `parseability.file_size` |
| 1.15 | No photos, DOB, marital status, religion (for global/US/EU roles) | Legal/bias filters remove such resumes | (manual) |

---

## 2. ATS keyword / scoring rules (content must match the JD)

Modern ATS scoring (and AI matchers like **LinkedIn Recruiter**, **Naukri AI
Match**, **Greenhouse match score**, **Workday autoscore**) rank candidates
by **keyword overlap with the JD**, weighted by:

1. **Exact job title** in your current / most recent role → biggest single lift.
2. **Hard skills** mentioned in the JD, present in **both**:
   - a dedicated **Skills** section (so the parser indexes them), AND
   - at least one **Experience bullet** (so recency/context is credited).
3. **Acronym + expansion both present** — e.g. `AVD (Azure Virtual Desktop)`,
   `RBAC (Role-Based Access Control)`, `CI/CD (Continuous Integration /
   Continuous Delivery)`. ATS keyword dictionaries often index only one form.
4. **Years-of-experience phrasing** — e.g. `"2+ years"`, `"3 years of Azure"` —
   many ATS extract this as a numeric field for filtering.
5. **Location + authorisation** — city/country, "willing to relocate",
   visa status for cross-border roles.
6. **Measurable outcomes** — numbers (%, counts, time saved, SLA, uptime)
   boost both AI-match scores and human reviewer ranking.
7. **No keyword stuffing** — white text, hidden sections, long comma dumps
   are detected and penalised by current parsers.

**Rule of thumb:** aim for **70–80% skill-keyword overlap** with the target
JD. Below ~60%, most ATS put you below the fold.

Automated check: `keywords.keywords` (uses a 60% threshold for pass).

---

## 3. Recruiter 7-second scan rules (human reviewer)

Studies by TheLadders, Ladders Eye-Tracking (2018, 2024 update), and Jobscan
consistently show recruiters spend ~6–8 seconds on the first pass, scanning
in an F-pattern. They look for, in order:

1. **Name + current title** at the very top.
2. **Years of experience + domain** in one line (e.g.,
   *"2+ years in Azure Cloud Operations & NOC Automation"*).
3. **Current / last employer + duration**.
4. **Education + any premier-institute signal**.
5. **Top 3–5 skills** visible without scrolling.
6. **Numbers / outcomes** in bullets (eye snaps to digits).
7. **Location** — deal-breaker if mismatched.

If any of these aren't in the **top third of page 1**, your resume gets
de-prioritised, even if the rest is good.

Automated checks: `structure.sections`, `contact.contact`, `metrics.metrics`.

---

## 4. Naukri-specific rules (India)

Naukri recruiters use the **Naukri Resume Database Access (RDA / eSearch)**.
They search the database first — your resume *file* is opened only after you
clear their field filters. So on Naukri, **your profile fields matter more
than the file**.

| Naukri field | Why it matters | Rule |
|---|---|---|
| **Resume Headline** (250 chars) | Primary text shown in search results | Pack it with role + top skills + years. Example: *"System Support Engineer \| 2+ yrs \| Azure, Terraform, GitHub Actions, PagerDuty, PowerShell, NOC Ops"* |
| **Key Skills** (up to 50) | Direct boolean match for recruiter queries | List every tool / skill individually: `Azure`, `Azure VM`, `AVD`, `Terraform`, `GitHub Actions`, `PagerDuty`, `PowerShell`, `Selenium`, `Playwright`, `Jira`, … |
| **Current / Previous Designation** | Recruiters filter by title | Use a standard industry title (`System Support Engineer`, `Cloud Support Engineer`, `DevOps Engineer – L1`), not an internal one |
| **Total Experience** (yrs/months) | Hard filter in every search | Keep exact; must match resume |
| **Current CTC / Expected CTC** | Hard filter | Fill both; empty = many searches skip you |
| **Notice Period** | Hard filter | Fill (`Immediate`, `15 days`, `30 days`, …) |
| **Current Location / Preferred Location** | Hard filter | Add 2–3 preferred cities including the metro you're open to |
| **Industry + Functional Area + Role Category** | Facet filters | Pick the standard taxonomy choice closest to your target role |
| **Education** | Many jobs filter by UG/PG + specialization | Fill both; include institute |
| **Attached Resume** | Only opened after you clear filters | Mirror the same keywords inside the file |
| **Profile Completeness** | Profiles >90% complete rank higher | Fill every optional section (languages, projects, certifications, work samples) |
| **Profile Freshness** | Profiles updated in last 15 days rank higher | Edit *something* every 2 weeks to stay fresh |

**Naukri meta-rule:** your *profile text* carries the keywords, not just the
attached file.

---

## 5. The checker's scoring model (100 points)

| Category | Max | What it rewards |
|---|---:|---|
| **Parseability** | 25 | Extractable text, 1–2 pages, no images, ≤2 MB |
| **Structure** | 20 | Standard sections (Summary, Experience, Education, Skills, Projects/Certs) |
| **Contact** | 10 | Email + phone + LinkedIn + GitHub |
| **Dates / formatting** | 10 | `MMM YYYY` dates and `Present` marker on current role |
| **Keyword overlap vs JD** | 20 | % of JD skills found inside the resume |
| **Metrics / outcomes** | 10 | ≥50% of bullets contain a number or measurable result |
| **Acronyms** | 5 | Common acronyms (AVD, RBAC, CI/CD, …) spelled out at least once |
| **Total** | **100** | |

Grade:

| Score | Grade | Verdict |
|---:|---|---|
| 90–100 | A+ | Excellent — highly likely to clear ATS and recruiter screens |
| 80–89 | A | Strong — should clear most ATS and recruiter screens |
| 70–79 | B | Good — likely to pass, a few tweaks will boost ranking |
| 60–69 | C | Borderline — fix flagged issues before applying |
| 40–59 | D | Weak — ATS will likely rank you below the fold |
| 0–39 | F | Will not pass ATS reliably — significant rework needed |

---

## 6. Manual checklist (printable, 20 items)

Score ≥ 17/20 before you apply anywhere.

- [ ] Single-column, no text boxes, no images
- [ ] Contact details inside the body (not Word header/footer)
- [ ] File name is `FirstName_LastName_Resume.docx`
- [ ] Standard section titles only
- [ ] Dates in `MMM YYYY` format
- [ ] 1 page (≤3 yrs) or 2 pages (3–10 yrs)
- [ ] Current job title matches the title you're applying for (or very close)
- [ ] "Years of experience" written explicitly in Summary (`"2+ years"`)
- [ ] Hard skills appear in **both** Skills section **and** at least one Experience bullet
- [ ] Each acronym spelled out at least once (`AVD (Azure Virtual Desktop)`)
- [ ] At least 60–70% of the target JD keywords present
- [ ] Each role has 3–6 bullets, each starting with a strong verb
- [ ] At least **50%** of bullets contain a number, %, or outcome
- [ ] No keyword stuffing, no white text, no hidden sections
- [ ] No photo, no DOB, no marital status (bad for global ATS)
- [ ] Location + notice period visible
- [ ] Education, Certifications, and Projects sections present
- [ ] Spelling/grammar clean (parsers use this as a signal too)
- [ ] LinkedIn and GitHub links present *and* spelled out
- [ ] (If posting to Naukri) Resume Headline + Key Skills fields fully filled

---

## 7. AI JD-tailoring — how the tool uses this rulebook

When you click **✨ Tailor to JD** in the UI (or POST to `/api/tailor`),
the server:

1. Parses the resume into structured sections (name, contact, summary,
   skills, experience, education, certifications).
2. Extracts up to 50 keywords from the JD, finds which are missing.
3. Calls the active AI provider (`rule_based` / `ollama` / `openai`) with
   a prompt that **enforces** these rules:
   - Never fabricate employers, titles, or dates.
   - Preserve current employer, title, dates exactly.
   - Insert missing JD keywords naturally in **Summary** + **Skills** (and
     plausible **Experience bullets**).
   - Rewrite bullets to be outcome-oriented with numbers.
   - If a metric is unknown, use a bracketed placeholder like `[N]` or
     `[NN%]` instead of inventing one.
4. Returns a structured `TailoredResume` payload, which is rendered twice:
   - `.docx` via `python-docx`
   - `.pdf` via `fpdf2`

Both files follow the formatting rules in Section 1 (single-column,
Calibri/Helvetica, standard section titles, `MMM YYYY` dates, no images),
so the AI output is still ATS-safe.

If the AI provider is unreachable, the tool silently falls back to
`rule_based` so you always get a usable tailored file.

---

## 8. References

- **Jobscan** — "How ATS systems read your resume" (resume formatting guides)
- **Enhancv** — ATS keyword matching deep-dives
- **Resume Worded** — scoring heuristics for recruiter screens
- **Greenhouse** — hiring platform docs on candidate ranking
- **Workday** — Recruiting module admin docs (job requisition keyword scoring)
- **Lever** — recruiter search features
- **LinkedIn Talent Solutions** — Recruiter search field weights
- **Naukri Help Center** — profile completeness and search ranking
- **TheLadders** (2012, re-run 2018, 2024) — eye-tracking studies on recruiter scanning
- **Reddit** r/recruiting, r/resumes, Blind — anecdotal rules consistent across cohorts

This rulebook will drift as ATS vendors evolve. Refresh it against newer
Jobscan / Enhancv / vendor blog posts every ~6 months.
