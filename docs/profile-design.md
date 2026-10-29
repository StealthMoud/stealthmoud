# Profile design

The profile's job is to introduce Mahmoud and help visitors understand his public
security and backend projects. Selected work comes before activity statistics.

## Visual direction

An application-security workbench: a request crosses a trust boundary, then branches
into identity, input, and access checks. This is an illustration, not live telemetry.
The diagram is original SVG artwork. A single 4.5-second packet animation stops
automatically and respects reduced-motion preferences.

- Deep blue `#0c1b25`, off-white `#edf5f4`, teal `#69d6cd`, copper `#f1b184`.
- Light variant: pale blue `#f1f6f6`, ink `#153543`, teal `#087e80`, copper `#a85226`.
- Trebuchet / Segoe UI for the wordmark and headline; system monospace for labels.
- Separate mobile compositions keep the main text readable at small widths.
- Native Markdown and HTML keep the biography, project descriptions, and contact
  links selectable and accessible. No external fonts, badges, trackers, or image services.

Rebuild the four header images with `python3 scripts/render_brand.py`.

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

`python3 sync_profile.py` fetches only GitHub's unauthenticated public contribution
calendar. It writes stable `assets/activity-dark.svg` and `assets/activity-light.svg`
paths. It never reads a token, private events, repository lists, or commit messages,
and it never rewrites README.md. The calendar may include anonymized private
contributions if the owner chooses to show them on GitHub.

The daily workflow commits only changed calendar assets. A missing or malformed
calendar fails the run and preserves the last successful assets; no fallback counts
are invented. Legacy metrics modules in `src/` are no longer called by the updater.

Validate with `python3 -m unittest discover -s tests -v`.
