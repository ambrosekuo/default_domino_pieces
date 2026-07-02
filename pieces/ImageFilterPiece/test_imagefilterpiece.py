from domino.testing import piece_dry_run
from pathlib import Path
import base64
import importlib
import requests
import sys

PIECE_NAME = "ImageFilterPiece"

FLOWERS_IMAGE_URL = (
    "https://images.pexels.com/photos/4055758/pexels-photo-4055758.jpeg"
    "?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
)

flowers_response = requests.get(FLOWERS_IMAGE_URL, timeout=30)
flowers_response.raise_for_status()
flowers_image_bytes = flowers_response.content
base64_image = base64.b64encode(flowers_image_bytes).decode("utf-8")


def _dry_run_locally(input_data, results_path):
    pieces_folder_path = str(Path(".").resolve() / "pieces")
    if pieces_folder_path not in sys.path:
        sys.path.append(pieces_folder_path)

    piece_module = importlib.import_module(f"{PIECE_NAME}.piece")
    models_module = importlib.import_module(f"{PIECE_NAME}.models")
    piece_class = getattr(piece_module, PIECE_NAME)

    return piece_class.dry_run(
        input_data=input_data,
        piece_input_model=models_module.InputModel,
        piece_output_model=models_module.OutputModel,
        results_path=str(results_path),
    )


def test_imagefilterpiece():
    input_data = dict(
        input_images=[base64_image],
        sepia=True,
        blue=True,
        output_type="both"
    )
    piece_output = piece_dry_run(
        piece_name="ImageFilterPiece",
        input_data=input_data
    )
    assert piece_output is not None
    assert piece_output.get('image_file_paths')[0].endswith('.png')


def test_imagefilterpiece_multiple_images():
    input_data = dict(
        input_images=[base64_image, base64_image],
        sepia=True,
        output_type="both"
    )
    piece_output = piece_dry_run(
        piece_name="ImageFilterPiece",
        input_data=input_data
    )
    assert len(piece_output['image_file_paths']) == 2
    assert len(piece_output['image_base64_strings']) == 2


def test_imagefilterpiece_from_file_paths(tmp_path):
    image_paths = []
    for index in range(2):
        file_path = tmp_path / f"flowers_{index}.jpg"
        file_path.write_bytes(flowers_image_bytes)
        image_paths.append(str(file_path))

    results_path = tmp_path / "results"
    results_path.mkdir()

    piece_output = _dry_run_locally(
        input_data=dict(
            input_images=image_paths,
            sepia=True,
            output_type="both",
        ),
        results_path=results_path,
    )
    assert len(piece_output.image_file_paths) == 2
    for file_path in piece_output.image_file_paths:
        assert Path(file_path).exists()
        assert Path(file_path).stat().st_size > 0
