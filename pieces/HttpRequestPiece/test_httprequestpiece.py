from domino.testing import piece_dry_run
from domino.logger import get_configured_logger
import base64
import json
import importlib
import sys
from pathlib import Path


FLOWERS_IMAGE_URL = (
    "https://images.pexels.com/photos/4055758/pexels-photo-4055758.jpeg"
    "?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
)


def _run_piece(input_data, results_path):
    pieces_folder_path = str(Path('.').resolve() / "pieces")
    if pieces_folder_path not in sys.path:
        sys.path.append(pieces_folder_path)

    piece_module = importlib.import_module("HttpRequestPiece.piece")
    models_module = importlib.import_module("HttpRequestPiece.models")
    piece = piece_module.HttpRequestPiece.__new__(piece_module.HttpRequestPiece)
    piece.results_path = str(results_path)
    piece.logger = get_configured_logger("test")
    output = piece.piece_function(models_module.InputModel(**input_data))
    return output


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


def test_httprequest_image_file_paths(tmp_path):
    output = _run_piece(
        {
            'urls': [FLOWERS_IMAGE_URL, FLOWERS_IMAGE_URL],
            'method': 'GET',
        },
        tmp_path,
    )

    assert len(output.image_file_paths) == 2
    assert output.base64_bytes_data == ["", ""]
    for file_path in output.image_file_paths:
        assert Path(file_path).exists()
        assert Path(file_path).stat().st_size > 0
        assert file_path.endswith('.jpg')


def test_httprequest_image_file_paths_integration(tmp_path):
    sys.path.insert(0, str(Path('.').resolve() / "pieces"))

    filter_module = importlib.import_module("ImageFilterPiece.piece")
    filter_models = importlib.import_module("ImageFilterPiece.models")

    http_output = _run_piece(
        {
            'urls': [FLOWERS_IMAGE_URL, FLOWERS_IMAGE_URL],
            'method': 'GET',
        },
        tmp_path,
    )

    filter_path = tmp_path / "filter"
    filter_path.mkdir()
    filter_piece = filter_module.ImageFilterPiece.__new__(filter_module.ImageFilterPiece)
    filter_piece.results_path = str(filter_path)
    filter_piece.logger = get_configured_logger("test")

    filter_output = filter_piece.piece_function(filter_models.InputModel(
        input_images=http_output.image_file_paths,
        sepia=True,
        output_type="both",
    ))

    assert len(filter_output.image_file_paths) == 2
