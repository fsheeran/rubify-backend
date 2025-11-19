# rubify-backend

A Python/FastAPI service that provides text segmentation and pronunciation annotation for Japanese (and hopefully soon Chinese and Korean) text. For use alongside github.com/fsheeran/rubify

## Installation

### Prerequisites

- Python 3.13+
- pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/fsheeran/rubify-backend
cd rubify-backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download and prepare the furigana dictionary:
```bash
python update_dictionaries.py
```

This will download the latest [JmdictFurigana](github.com/Doublevil/JmdictFurigana/) dictionary and transform it into the required format. The dictionary file `JmdictFurigana.json` will be created in the project root.

## Usage

### Running the Service

just run it like you would any other FastAPI server. For example, to run the dev server, run:

```bash
fastapi dev src/main.py
```

#### Docker

A Dockerfile is provided as well:

```bash
docker build -t rubify-backend .
docker run -p 8000:80 rubify-backend
```

### API

The service exposes only one API route, `/annotate

#### `POST /annotate`

Annotates text with segmentation and pronunciation guides.

**Request Body:**
```json
{
  "base_text": "私はその人を常に先生と呼んでいた",
  "language": "jpn"
}
```

**Parameters:**
- `base_text` (string): The text to annotate
- `language` (string): Language code - `"jpn"` for Japanese, `"zho"` for Chinese

**Response:**
```json
[
  {
    "indices": [0, 1],
    "annotations": [
      {
        "indices": [0, 1],
        "annotation_text": "わたし"
      }
    ]
  },
  {
    "indices": [1, 2]
  },
  {
    "indices": [2, 4]
  },
  {
    "indices": [4, 5],
    "annotations": [
      {
        "indices": [4, 5],
        "annotation_text": "ひと"
      }
    ]
  }
  // ... more segments
]
```

**Response Fields:**
- `indices`: Tuple `[start, end]` indicating the character range in the original text of the text segment
- `annotations`: Optional list of annotation objects (segments that need no pronunciation guides, such as those that contain only hangul, kana, or latin characters, do not have an `annotations` attribute). Each annotation object contains:
  - `indices`: Character range for this specific annotation
  - `annotation_text`: The pronunciation guide (e.g., hiragana for kanji).

### Example Usage

#### Using curl

```bash
curl -X POST "http://localhost:8000/annotate" \
  -H "Content-Type: application/json" \
  -d '{
    "base_text": "私は学生です",
    "language": "jpn"
  }'
```

#### Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/annotate",
    json={
        "base_text": "私は学生です",
        "language": "jpn"
    }
)
result = response.json()
print(result)
```

## License

See `LICENSE` file for details. Third-party licenses are documented in `THIRDPARTYLICENSES`.

## Acknowledgments

- Uses [JmdictFurigana](https://github.com/Doublevil/JmdictFurigana) for Japanese pronunciation data
- Uses [SudachiPy](https://github.com/WorksApplications/sudachi.rs) for Japanese morphological analysis
