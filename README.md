[![codecov](https://codecov.io/gh/Tauffer-Consulting/default_domino_pieces/graph/badge.svg?token=DLCDR2S3B6)](https://codecov.io/gh/Tauffer-Consulting/default_domino_pieces)

# Default Domino Pieces
Default Domino Pieces that comes pre-installed in every Domino workspace:

- **CustomPythonPiece** - A Piece that executes a user-defined Python function.
- **GetDateTimePiece** - A Piece that returns the current date and time.
- **GetItemFromArrayPiece** - A Piece that returns an item from an array.
- **HttpRequestPiece** - A Piece that makes HTTP requests to a list of URLs and returns base64-encoded responses.
- **ImageFilterPiece** - A Piece that applies image filters to a list of images (paths or base64 strings).
- **LogPiece** - A simple logging Piece.
- **LoremIpsumPiece** - A Piece that returns a random Lorem Ipsum text.
- **PageScrapperPiece** - A Piece that scrapes text from a web page, given a URL and a list of HTML tags.
- **SleepPiece** - A Piece that sleeps for a given number of seconds.
- **ToStringPiece** - A Piece that converts any input to string.
- **StringOperationsPiece** - A Piece that performs string operations.
- **StringConditionChecksPiece** - A Piece that checks conditions on a string.

## HTTP Request → Image Filter workflow

The **Image Filter** workflow fetches images over HTTP and applies filters to them. Both pieces support **multiple URLs/images** in a single run:

1. **HttpRequestPiece** — set one or more URLs in the `urls` field. Saves each response to shared storage as `image_file_paths` (wire this to Image Filter). `base64_bytes_data` is only populated for non-image responses.
2. **ImageFilterPiece** — connect upstream `image_file_paths` to `input_images`. Outputs `image_base64_strings` and `image_file_paths` as lists (`modified_image_0.png`, `modified_image_1.png`, …).

In the Domino canvas, list fields render as add/remove rows (same pattern as `LogPiece` `input_array` or `PageScrapperPiece` `search_items`).
