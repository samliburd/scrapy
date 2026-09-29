# scrapy

A lightweight CLI bookmark manager. Save URLs from the command line or clipboard, auto-scrape their page titles, and browse your collection in an interactive dashboard.

---

## Features

- **One-command bookmarking** — `scrapy <url>` or copy a URL and just run `scrapy`
- **Smart title scraping** — fast `pycurl` fetch with automatic Playwright fallback for JS-heavy or bot-protected pages
- **Local SQLite storage** — everything lives in `~/.urls.db`, nothing leaves your machine
- **Streamlit dashboard** — browse, filter, and click bookmarks with `scrapy --read`
- **Auto-backup** — copies the database to `$BOOKMARK_BACKUP_DIR` every 5 inserts

---

## Requirements

- Python 3.14+
- [`uv`](https://docs.astral.sh/uv/) — install with `curl -LsSf https://astral.sh/uv/install.sh | sh`
- `libcurl` with SSL support (required by `pycurl`)

### macOS — install libcurl

```bash
brew install curl
export PYCURL_SSL_LIBRARY=openssl
```

---

## Installation

### As a global `uv tool` (recommended)

Install directly from the project directory:

```bash
git clone https://github.com/your-username/scrapy.git
cd scrapy
uv tool install .
```

Verify it's on your `PATH`:

```bash
scrapy --help
```

> If `scrapy` is not found, ensure the `uv` tools bin directory is on your `PATH`.
> Run `uv tool dir --bin` to find it, then add it to your shell profile.

### Install Playwright browsers (one-time)

After installing the tool, install the Playwright browser binaries:

```bash
uv tool run playwright install chromium
```

Or, if you have `playwright` available in your shell:

```bash
playwright install chromium
```

---

## Usage

### Bookmark a URL

```bash
scrapy https://example.com
```

### Bookmark from clipboard

Copy a URL to your clipboard, then run:

```bash
scrapy
```

### Open the dashboard

```bash
scrapy --read
```

This backfills any missing titles, then launches the Streamlit browser UI.

### Reset a column

Clear all values in a column (e.g. to re-scrape all titles):

```bash
scrapy --drop page_title
```

> **Warning:** This drops and re-adds the column, permanently deleting all existing values in it.

---

## Configuration

### Automatic backups

Set the `BOOKMARK_BACKUP_DIR` environment variable to enable automatic backups every 5 inserts:

```bash
# Add to ~/.zshrc or ~/.bashrc
export BOOKMARK_BACKUP_DIR="$HOME/Backups/scrapy"
```

Backups are timestamped copies of `~/.urls.db`, e.g. `urls_20260929_213000.db`.

### Streamlit theme

Streamlit settings live in [`.streamlit/config.toml`](.streamlit/config.toml). Edit this file to customise the dashboard appearance.

---

## Upgrading

Pull the latest changes and reinstall:

```bash
cd scrapy
git pull
uv tool install . --force
```

---

## Uninstalling

```bash
uv tool uninstall scrapy
```

The database at `~/.urls.db` is **not** removed — delete it manually if needed:

```bash
rm ~/.urls.db
```

---

## Development

### Set up a local environment

```bash
uv sync
```

### Run directly (without installing)

```bash
uv run python main.py https://example.com
uv run python main.py --read
```

### Lint

```bash
uv run ruff check .
uv run ruff check --fix .
```

### Add a dependency

```bash
uv add <package>
```

---

## Project Structure

```
scrapy/
├── main.py              # CLI entry point
├── pyproject.toml       # Package config and build system
├── src/
│   ├── processor.py     # Title scraping (pycurl + Playwright)
│   ├── display.py       # Streamlit dashboard
│   └── utils/
│       ├── config.py    # Constants (paths, thresholds)
│       ├── db_manager.py# SQLite connection and schema
│       ├── backup.py    # Database backup logic
│       └── drop.py      # Column reset helpers
└── .streamlit/
    └── config.toml      # Streamlit configuration
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for a detailed technical breakdown.
