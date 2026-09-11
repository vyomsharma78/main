# Mini URL Shortener

A beginner-friendly command-line URL shortener built with **Python 3 standard library only**.

It satisfies the 1st-year CLI track requirements:

- Convert a long URL into a short code
- Persist mappings across runs using SQLite
- Resolve a short code back to the original URL
- List all stored mappings
- Validate invalid URLs
- Handle duplicate/missing codes gracefully
- Optional custom aliases
- Optional click-count tracking
- Optional browser opening on resolve
- No external URL-shortening APIs

## Requirements

- Python 3.10+ recommended
- No third-party packages are required

Python's built-in `sqlite3` module provides a lightweight disk-backed database, so the data persists between program runs.

## Run

Open a terminal in this folder:

```bash
python main.py --help
```

### 1. Shorten a URL

```bash
python main.py shorten https://www.google.com
```

Example:

```text
Short code: aB7kP2
Short URL:  urlshort://aB7kP2
```

The mapping is saved in `urls.db`.

### 2. Resolve a code

```bash
python main.py resolve aB7kP2
```

Example:

```text
Original URL: https://www.google.com
Click count: 1
```

Every successful resolve increments the click count.

To open the URL in your default browser:

```bash
python main.py resolve aB7kP2 --open
```

### 3. List all mappings

```bash
python main.py list
```

Example:

```text
CODE           CLICKS   ORIGINAL URL
------------------------------------------------------------------------------------------
aB7kP2         2        https://www.google.com
x91LmQ         0        https://github.com/
```

### 4. Custom alias (bonus)

```bash
python main.py shorten https://github.com/ --alias github
```

Then:

```bash
python main.py resolve github
```

Aliases are limited to 1-32 letters/numbers.

## Project structure

```text
mini-url-shortener/
├── main.py
├── README.md
├── .gitignore
└── tests/
    └── test_main.py
```

`urls.db` is generated automatically when the application first runs and is ignored by Git.

## Design

The application uses:

- `argparse` for the CLI
- `sqlite3` for persistent storage
- `urllib.parse` for URL validation
- `secrets` for random short-code generation
- `webbrowser` for the optional `--open` feature

Database table:

```text
urls
├── id
├── code
├── original_url
├── clicks
└── created_at
```

## Testing

Run:

```bash
python -m unittest discover -s tests -v
```

The tests use a temporary SQLite database and do not modify your normal `urls.db`.

## GitHub submission

Create a GitHub repository named something like:

`mini-url-shortener`

Then:

```bash
git init
git add .
git commit -m "Build mini URL shortener"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/mini-url-shortener.git
git push -u origin main
```

Do **not** commit `urls.db`; it is already in `.gitignore`.

## Extra-credit ideas

If you want to make the submission stronger, possible extensions are:

1. Add an HTTP Flask version for the 2nd-year track.
2. Add expiration dates.
3. Add a delete command.
4. Add URL statistics.
5. Add a QR-code feature (would require a third-party package, so keep it separate from the standard-library version).
