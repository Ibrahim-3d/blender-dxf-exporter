# Licensing — 2026-09-30

The current add-on is **GPL-3.0-or-later**, matching its existing Blender
manifest and third-party notice's whole-add-on grant. The README and root
LICENSE have been reconciled to that policy. The explicit grant and complete
GPL text are included inside the installable `dxf_dwg_exporter` directory as
`LICENSE.txt` and `COPYING`.

The former root AGPL-3.0 text from commit
`c42351d23e7513340f89479958066395eb6e0295` is preserved verbatim in
`LICENSES/AGPL-3.0-historical.txt`. Historical grants remain intact; this
change does not rewrite tags or previously distributed archives.

## Optional converters

The tracked `bin/` directory contains a placement instruction, not a bundled
LibreDWG binary. The third-party notice identifies components that may be
present in a separately obtained or future bundled converter distribution.
Do not interpret that notice as a complete inventory of every release.

If distributing LibreDWG or its DLLs, verify exact versions and include their
required notices, complete license texts, and corresponding source or other
compliant source-delivery mechanism. GNU libiconv and other libraries can
have different obligations from the add-on. A link to a project's homepage
alone is not a completed compliance check.

Preserve the Python source, `LICENSE.txt`, `COPYING`, and
`THIRD_PARTY_NOTICES.md` in add-on ZIPs. A paid official download or support
service must not remove recipients' GPL rights. No Python behavior, converter
binaries, dependency versions or existing release assets were changed here.
