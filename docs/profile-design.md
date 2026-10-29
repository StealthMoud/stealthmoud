# Profile design

The profile's job is to introduce Mahmoud and help visitors understand his public
security and backend projects. Selected work comes before activity statistics.

## Visual direction

A hacker research console: phosphor typography, clipped terminal corners, a custom
SM monogram, and a radar that inspects identity, input, and state. The header is
explicitly labeled a local lab simulation; its graphics are not live telemetry.

- Dark: near-black `#070d0a`, phosphor `#b6f45a`, cyan `#6ae5f1`, text `#e3f0e5`.
- Light: pale green `#f0f5ec`, ink `#183721`, green `#3e6c08`, cyan `#086d80`.
- System monospace throughout the artwork; no font downloads.
- A 12-second loop types a local-scope command, highlights the three inspection
  stages in sequence, and rotates the radar. A small wordmark glitch appears once
  per loop. A separate research-flow strip highlights scope, inspection,
  reproduction, and documentation in order.
- Desktop and mobile compositions have dedicated SVGs. The picture elements select
  static assets under `prefers-reduced-motion: reduce`, leaving complete, readable
  content even when the host browser does not pass that preference into SVG images.
- Native Markdown and HTML keep the biography, project descriptions, and contact
  links selectable. No external badges, trackers, image services, or SVG scripts.

Rebuild the eight animated and eight static header and research-flow images with
`python3 scripts/render_brand.py`.

## References reviewed

Reviewed on 29 October 2026; used as design references, not copied assets or templates:

- [thewhiteh4t](https://github.com/thewhiteh4t/thewhiteh4t): a security profile with
  one strong visual identity.
- [BrunnerLivio](https://github.com/BrunnerLivio/BrunnerLivio): a coherent retro
  concept and custom visual assets.
- [DenverCoder1](https://github.com/DenverCoder1/DenverCoder1): explicit project
  navigation and readable grouping.
- [Awesome GitHub Profile README](https://github.com/abhisheknaiidu/awesome-github-profile-readme):
  compared the image-led, retro, code, and minimal approaches.
- [GitHub profile README documentation](https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme).

Project descriptions were checked against each linked public repository. The old
certification and ranking claims were omitted because this review did not establish
supporting evidence. Public professional contact links were preserved.

## Activity updater

`python3 sync_profile.py` records one maintenance update per Europe/Rome calendar
day. GitHub Actions checks at **01:23, 07:23, 13:23, and 19:23 Europe/Rome**, allowing
later checks to retry after a missed or failed run. Successful same-day checks are
no-ops and do not create additional commits.

The script fetches only GitHub's unauthenticated public contribution calendar and
writes `assets/activity-dark.svg` and `assets/activity-light.svg`. It updates only
the marked `PROFILE_REFRESH` block in README.md, preserving the authored content.
It never reads a token, private events, repository lists, or commit messages.
The calendar may include anonymized private contributions if the owner enables them.

If the calendar is unavailable or malformed, the last successful images stay in
place and the README honestly records that the old snapshot was retained. Missing,
duplicated, or reversed README markers fail without editing the profile. Dates are
the actual current day; the script does not backdate commits or fabricate metrics.

At the owner's request, automated commits use author
`StealthMoud <152169815+StealthMoud@users.noreply.github.com>`, with
`github-actions[bot]` as committer and an explicit automated-maintenance commit
message. The workflow pushes only README.md and the two calendar assets to main.

These commits are intended to qualify under GitHub's
[contribution criteria](https://docs.github.com/en/account-and-profile/reference/profile-contributions-reference).
They do not establish manual coding activity. GitHub
[may delay or drop scheduled jobs](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule),
so an uninterrupted streak cannot be guaranteed. The repository must remain active,
the workflow enabled, and the author email associated with the account.

Legacy metrics modules in `src/` are no longer called by the updater.
Validate with `python3 -m unittest discover -s tests -v`.
