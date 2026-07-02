from domino.base_piece import BasePiece
from .models import InputModel, OutputModel
from pathlib import Path
import requests
import base64
import json


CONTENT_TYPE_TO_EXTENSION = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/gif": "gif",
    "image/bmp": "bmp",
    "image/tiff": "tiff",
    "image/svg+xml": "svg",
    "application/json": "json",
    "text/html": "html",
    "text/plain": "txt",
}


class HttpRequestPiece(BasePiece):
    def _normalize_content_type(self, content_type):
        return content_type.lower().split(";")[0].strip()

    def _is_image_response(self, content_type):
        return self._normalize_content_type(content_type).startswith("image/")

    def _get_response_extension(self, content_type):
        normalized = self._normalize_content_type(content_type)
        return CONTENT_TYPE_TO_EXTENSION.get(normalized, "bin")

    def _save_response_file(self, results_path, index, response):
        content_type = response.headers.get("Content-Type", "")
        extension = self._get_response_extension(content_type)
        file_path = results_path / f"response_{index}.{extension}"

        if extension in ("json", "html", "txt", "md"):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(response.text)
        else:
            with open(file_path, "wb") as f:
                f.write(response.content)

        return str(file_path)

    def _encode_response(self, response):
        content_type = response.headers.get("Content-Type", "")
        if self._is_image_response(content_type):
            return ""
        return base64.b64encode(response.content).decode("utf-8")

    def _make_request(self, url, method, headers, body_data):
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=body_data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=body_data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise Exception(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        return response

    def piece_function(self, input_data: InputModel):
        urls = input_data.urls
        method = input_data.method

        headers = {}
        if input_data.bearer_token:
            headers['Authorization'] = f'Bearer {input_data.bearer_token}'

        body_data = None
        if method in ["POST", "PUT"]:
            try:
                body_data = json.loads(input_data.body_json_data)
            except json.JSONDecodeError:
                raise Exception("Invalid JSON data in the request body.")

        results_path = Path(self.results_path)
        results_path.mkdir(parents=True, exist_ok=True)

        base64_results = []
        response_file_paths = []
        try:
            for url in urls:
                response = self._make_request(url, method, headers, body_data)
                base64_results.append(self._encode_response(response))
                response_file_paths.append(
                    self._save_response_file(results_path, len(response_file_paths), response)
                )
        except requests.RequestException as e:
            raise Exception(f"HTTP request error: {e}")

        return OutputModel(
            base64_bytes_data=base64_results,
            image_file_paths=response_file_paths,
        )
