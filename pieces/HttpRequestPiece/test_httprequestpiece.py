from domino.testing import piece_dry_run
from domino.logger import get_configured_logger
import base64
import json
import importlib
import sys
from pathlib import Path


def _run_piece(input_data, results_path):
    pieces_folder_path = str(Path('.').resolve() / "pieces")
    if pieces_folder_path not in sys.path:
        sys.path.append(pieces_folder_path)

    piece_module = importlib.import_module("HttpRequestPiece.piece")
    models_module = importlib.import_module("HttpRequestPiece.models")
    piece = piece_module.HttpRequestPiece.__new__(piece_module.HttpRequestPiece)
    piece.results_path = str(results_path)
    piece.logger = get_configured_logger("test")
    piece.display_result = None
    piece.piece_function(models_module.InputModel(**input_data))
    return piece


def test_httprequest_get():
    input_data = {
        'urls': ['https://jsonplaceholder.typicode.com/posts'],
        'method': 'GET'
    }
    piece_output = piece_dry_run(
        piece_name="HttpRequestPiece",
        input_data=input_data
    )
    assert len(piece_output['base64_bytes_data']) == 1
    output_data = base64.decodebytes(piece_output['base64_bytes_data'][0].encode('utf-8'))
    output_data = json.loads(output_data)
    assert isinstance(output_data, list)


def test_httprequest_get_multiple_urls():
    input_data = {
        'urls': [
            'https://jsonplaceholder.typicode.com/posts/1',
            'https://jsonplaceholder.typicode.com/posts/2',
        ],
        'method': 'GET'
    }
    piece_output = piece_dry_run(
        piece_name="HttpRequestPiece",
        input_data=input_data
    )
    assert len(piece_output['base64_bytes_data']) == 2
    for encoded in piece_output['base64_bytes_data']:
        output_data = json.loads(base64.decodebytes(encoded.encode('utf-8')))
        assert 'id' in output_data


def test_httprequest_post():
    input_data = {
        'urls': ['https://httpbin.org/post'],
        'method': 'POST',
        'body_json_data': json.dumps({
            'key_1': 'domino',
            'key_2': 'testing-post'
        })
    }
    piece_output = piece_dry_run(
        piece_name="HttpRequestPiece",
        input_data=input_data
    )
    output_data = base64.decodebytes(piece_output['base64_bytes_data'][0].encode('utf-8'))
    output_data = json.loads(output_data)
    assert output_data['json']['key_1'] == 'domino'
    assert output_data['json']['key_2'] == 'testing-post'


def test_httprequest_put():
    input_data = {
        'urls': ['https://httpbin.org/put'],
        'method': 'PUT',
        'body_json_data': json.dumps({
            'key_1': 'domino',
            'key_2': 'testing-put'
        })
    }
    piece_output = piece_dry_run(
        piece_name="HttpRequestPiece",
        input_data=input_data
    )
    output_data = base64.decodebytes(piece_output['base64_bytes_data'][0].encode('utf-8'))
    output_data = json.loads(output_data)
    assert output_data['json']['key_1'] == 'domino'
    assert output_data['json']['key_2'] == 'testing-put'


def test_httprequest_delete():
    input_data = {
        'urls': ['https://httpbin.org/delete'],
        'method': 'DELETE'
    }
    piece_output = piece_dry_run(
        piece_name="HttpRequestPiece",
        input_data=input_data
    )
    output_data = base64.decodebytes(piece_output['base64_bytes_data'][0].encode('utf-8'))
    output_data = json.loads(output_data)
    assert output_data['url'] == 'https://httpbin.org/delete'


def test_httprequest_display_result_shows_image(tmp_path):
    piece = _run_piece(
        {
            'urls': ['https://httpbin.org/image/png'],
            'method': 'GET',
        },
        tmp_path,
    )

    assert piece.display_result is not None
    assert piece.display_result["file_type"] == "png"
    assert piece.display_result["base64_content"]
    assert Path(piece.display_result["file_path"]).exists()


def test_httprequest_display_result_shows_json_body(tmp_path):
    piece = _run_piece(
        {
            'urls': ['https://jsonplaceholder.typicode.com/posts/1'],
            'method': 'GET',
        },
        tmp_path,
    )

    assert piece.display_result is not None
    assert piece.display_result["file_type"] == "json"
    saved_response = json.loads(Path(piece.display_result["file_path"]).read_text())
    assert saved_response["id"] == 1
