from domino.testing import piece_dry_run
import base64
import json


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
