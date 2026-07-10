# MediaNamer

Rename images and videos with auto-generated filenames to meaningful names.

MediaNamer scans a folder, shows only media files whose names look non-descriptive (timestamps, random IDs, downloader names, camera defaults), and lets you preview each file and rename it one at a time.

## Requirements

- Python 3.10+
- Windows, macOS, or Linux

## Quick start

```bash
pip install -r requirements.txt
python main.py
```

## Build executable

```bash
pip install -r requirements-build.txt
pyinstaller --noconfirm --clean MediaNamer.spec
```

Output: `dist/MediaNamer.exe`

## Usage

1. Enter or browse to a folder, then click **Load**
2. Each file with a non-descriptive name is shown with a preview
3. Type a new name (extension is kept automatically)
4. Click **Save & Next** to rename, or **Skip** to leave unchanged

### Video controls

- **Click the video** to play or pause
- **Click the seekbar** to jump to a position
- **Settings → Video autoplay** — start playback when a video loads (default: on)
- **Settings → Video loop** — repeat the current video (default: off)

Settings are saved between sessions.

## What gets flagged?

| Flagged (needs rename) | Skipped (descriptive) |
|------------------------|------------------------|
| `1677436352686185.webm` | `LiftTogetherOrgans.mov` |
| `G88xPUkWAAAYKvk.png` | `my_vacation_photo.jpg` |
| `ssstwitter.com_1677363396448.mp4` | `birthdayParty.mp4` |
| `IMG_1234.jpg` | `I'mCat.mp4` |
| `trim.B62AC75E-….mov` | `ProjectAlpha.mp4` |

Supported media: common image formats (JPG, PNG, GIF, WebP, …) and video formats (MP4, MOV, MKV, WebM, …).

## Project structure

```
MediaNamer/
├── medianamer/
│   ├── app.py           Application entry point
│   ├── main_window.py   Main window (wiring only)
│   ├── media_player.py  Video playback
│   ├── preview.py       Image preview
│   ├── rename.py        Rename queue and validation
│   ├── name_utils.py    Descriptive name detection
│   ├── settings.py      Persisted user settings
│   └── widgets.py       UI widgets
├── tests/
│   ├── test_name_utils.py
│   └── test_rename.py
├── exampleData/         Local test media (gitignored)
├── main.py
├── MediaNamer.spec      PyInstaller build config
├── requirements.txt
└── requirements-build.txt
```

## Development

```bash
pip install -r requirements.txt
python -m pytest tests/
```

Place sample files in `exampleData/` for manual testing.
