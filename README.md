# Flashcards Generator

Web application for generating flashcards from text and PDF files.

## Features

- Text to flashcards conversion
- PDF file parsing
- Light/dark theme
- Keyboard navigation
- Card flip animation

## Tech Stack

Frontend: HTML, CSS, JavaScript
Backend: Python, FastAPI, PyPDF2

## Setup

Clone the repository:
```bash
git clone https://github.com/abduss011/flashcards-generator.git
cd flashcards-generator
```

Install dependencies:
```bash
cd backptos
pip install -r requirements.txt
```

Optional - Add Google Gemini API key:
```bash
# Create .env file in backptos/
GEMINI_API_KEY=your_key_here
```

Get a free key at https://makersuite.google.com/app/apikey

## Running

Start backend:
```bash
cd backptos
python3 app.py
```

Start frontend (in new terminal):
```bash
cd frontptos
python3 -m http.server 3000
```

Open http://localhost:3000

## Usage

1. Choose Text or PDF tab
2. Enter text or upload PDF file
3. Click Generate Flashcards
4. Study your cards

Navigation:
- Click card to flip
- Arrow keys for next/previous
- Space to flip

## API Endpoints

POST /generate/text - Generate cards from text
POST /generate/pdf - Generate cards from PDF
GET /health - Health check

## Development

The app uses a simple algorithm by default. For better quality cards, configure Gemini API in the .env file.

## Deployment

Backend works on Render, Railway, or similar platforms.
Frontend can be hosted on Vercel, Netlify, or GitHub Pages.

## Known Issues

- SSL certificate errors with Python 3.9 on macOS
- Simple algorithm produces basic questions
- Large PDF files may take time to process

## Future Improvements

- Better card generation algorithm
- Card saving functionality
- Spaced repetition system
- Multiple language support
- Anki export

## License

MIT

## Author

Abdussattar