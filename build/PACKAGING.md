# Packaging AI Token Auditor for Windows

## Build the executable

From the project root (the folder containing `main.py`):

```bash
pip install -r requirements.txt
pip install pyinstaller
pyinstaller build/token_auditor.spec --noconfirm
```

Output: `dist/AI Token Auditor/AI Token Auditor.exe` (a folder — see below
for why this is used instead of a single-file exe).

Before building, replace the placeholder `build/app_icon.ico` with a real
icon, and edit `build/version_info.txt` — set `CompanyName` to your real
business/legal name. That's what fills in the exe's Properties → Details
tab, and Windows shows that name in the UAC/SmartScreen prompt.

## About the "Unknown Publisher" prompt — what actually fixes it

Be direct with yourself about this: no packaging trick, spec file, or
folder structure removes the "Unknown Publisher" warning on its own.
That warning is Windows telling the user the exe has no verified digital
signature. There are exactly two ways to make it go away:

1. **Buy a code-signing certificate** from a recognized CA (DigiCert,
   Sectigo, SSL.com, etc.) and sign the exe with `signtool`:
   ```bash
   signtool sign /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 ^
     /f your_cert.pfx /p your_password "dist\AI Token Auditor\AI Token Auditor.exe"
   ```
   A standard (OV) certificate still shows a generic "Unknown Publisher"-
   style warning until the exe has built up enough download reputation
   with Microsoft SmartScreen. An **EV (Extended Validation)** certificate
   is the only option that suppresses the SmartScreen warning immediately,
   because EV certs ship on a hardware token and require a stricter
   identity check.

2. **Build reputation over time** with a signed OV certificate — as more
   users download and run the signed exe without reporting it, SmartScreen
   reputation improves and the warning eventually stops appearing.

There is no third option. Anything claiming to bypass this without a real
certificate is either wrong or a security risk to recommend to your users.

## What this project does to make the rest of the experience trustworthy

Since signing is a business decision (it costs money and requires
registering a legal entity with the CA), the app is structured so
everything *else* about first-run looks professional:

- **Full version metadata** (`build/version_info.txt`) so Explorer's
  Properties dialog shows a real product name, company, and version
  instead of blank fields — blank fields are one of the strongest
  "this looks sketchy" signals to users.
- **Onedir build, not onefile.** A onefile exe self-extracts to a temp
  folder on every launch, which is slower and matches a pattern used by
  some malware droppers. A onedir build (a folder with the exe and its
  dependencies visible) starts faster and is more transparent about what
  it's actually shipping.
- **No UPX compression.** UPX-packed binaries are flagged by a
  disproportionate number of AV heuristics relative to the actual risk.
  Leaving binaries unpacked trades a larger download for fewer false
  positives.
- **`console=False`** in the spec, so no terminal flashes on launch —
  the polished window is the very first thing the user sees.
- **Clean error handling in `main.py`** — a startup failure shows a
  message box with a real explanation instead of the process silently
  vanishing, which is one of the more "untrustworthy-feeling" things an
  app can do.

## Distribution checklist

- [ ] Real `app_icon.ico` in `build/`
- [ ] `CompanyName` / `LegalCopyright` filled in in `version_info.txt`
- [ ] Built with `pyinstaller build/token_auditor.spec --noconfirm`
- [ ] Smoke-tested on a clean Windows VM (not just your dev machine)
- [ ] Zipped or wrapped in a proper installer (Inno Setup / NSIS) rather
      than distributing the raw `dist/` folder — an installer is itself a
      trust signal and lets you add Start Menu shortcuts, an uninstaller,
      and a EULA screen
- [ ] Signed with a code-signing certificate if you have one (see above)
- [ ] SHA-256 checksum published alongside the download so users can
      verify integrity independent of signing
