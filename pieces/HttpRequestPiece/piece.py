from domino.base_piece import BasePiece
from .models import InputModel, OutputModel
from pathlib import Path
import requests
import base64
import json


CONTENT_TYPE_TO_DISPLAY_FILE_TYPE = {
    "image/png": "png",
    "image/jpeg": "jpeg",
    "image/jpg": "jpeg",
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

    def _get_display_file_type(self, content_type):
        normalized = self._normalize_content_type(content_type)
        return CONTENT_TYPE_TO_DISPLAY_FILE_TYPE.get(normalized, "txt")

    def _build_display_result(self, url_responses, base64_results):
        results_path = Path(self.results_path)

        for index, (_, response) in enumerate(url_responses):
            content_type = response.headers.get("Content-Type", "")
            if not self._normalize_content_type(content_type).startswith("image/"):
                continue

            file_type = self._get_display_file_type(content_type)
            extension = "jpg" if file_type == "jpeg" else file_type
            file_path = results_path / f"response_{index}.{extension}"
            with open(file_path, "wb") as f:
                f.write(response.content)

            return {
                "file_type": file_type,
                "base64_content": base64_results[index],
                "file_path": str(file_path),
            }

        index = 0
        _, response = url_responses[0]
        content_type = response.headers.get("Content-Type", "")
        file_type = self._get_display_file_type(content_type)
        extension = "jpg" if file_type == "jpeg" else file_type
        file_path = results_path / f"response_{index}.{extension}"

        if file_type in ("json", "html", "txt", "md"):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(response.text)
        else:
            with open(file_path, "wb") as f:
                f.write(response.content)

        return {
            "file_type": file_type,
            "file_path": str(file_path),
        }

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

        base64_results = []
        url_responses = []
        try:
            for url in urls:
                response = self._make_request(url, method, headers, body_data)
                url_responses.append((url, response))
                base64_results.append(
                    base64.b64encode(response.content).decode('utf-8')
                )
        except requests.RequestException as e:
            raise Exception(f"HTTP request error: {e}")

        if url_responses:
            self.display_result = self._build_display_result(url_responses, base64_results)

        return OutputModel(base64_bytes_data=base64_results)
