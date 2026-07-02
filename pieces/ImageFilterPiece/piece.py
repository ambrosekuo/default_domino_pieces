from domino.base_piece import BasePiece
from .models import InputModel, OutputModel
from pathlib import Path
from PIL import Image
from io import BytesIO
import numpy as np
import base64
import os


filter_masks = {
    'sepia': ((0.393, 0.769, 0.189), (0.349, 0.686, 0.168), (0.272, 0.534, 0.131)),
    'black_and_white': ((0.333, 0.333, 0.333), (0.333, 0.333, 0.333), (0.333, 0.333, 0.333)),
    'brightness': ((1.4, 0, 0), (0, 1.4, 0), (0, 0, 1.4)),
    'darkness': ((0.6, 0, 0), (0, 0.6, 0), (0, 0, 0.6)),
    'contrast': ((1.2, 0.6, 0.6), (0.6, 1.2, 0.6), (0.6, 0.6, 1.2)),
    'red': ((1.6, 0, 0), (0, 1, 0), (0, 0, 1)),
    'green': ((1, 0, 0), (0, 1.6, 0), (0, 0, 1)),
    'blue': ((1, 0, 0), (0, 1, 0), (0, 0, 1.6)),
    'cool': ((0.9, 0, 0), (0, 1.1, 0), (0, 0, 1.3)),
    'warm': ((1.2, 0, 0), (0, 0.9, 0), (0, 0, 0.8)),
}


class ImageFilterPiece(BasePiece):

    def _load_image(self, input_image):
        max_path_size = int(os.pathconf('/', 'PC_PATH_MAX'))
        if len(input_image) < max_path_size and Path(input_image).exists() and Path(input_image).is_file():
            return Image.open(input_image)

        self.logger.info("Input image is not a file path, trying to decode as base64 string")
        try:
            decoded_data = base64.b64decode(input_image)
            image_stream = BytesIO(decoded_data)
            image = Image.open(image_stream)
            image.verify()
            image_stream.seek(0)
            return Image.open(image_stream)
        except Exception:
            raise ValueError("Input image is not a file path or a base64 encoded string")

    def _apply_filters(self, image, all_filters):
        np_image = np.array(image, dtype=float)

        self.logger.info(f"Applying filters: {', '.join(all_filters)}")
        for filter_name in all_filters:
            np_mask = np.array(filter_masks[filter_name], dtype=float)
            for y in range(np_image.shape[0]):
                for x in range(np_image.shape[1]):
                    rgb = np_image[y, x, :3]
                    new_rgb = np.dot(np_mask, rgb)
                    np_image[y, x, :3] = new_rgb
            np_image = np.clip(np_image, 0, 255)

        return Image.fromarray(np_image.astype(np.uint8))

    def piece_function(self, input_data: InputModel):
        all_filters = []
        if input_data.sepia:
            all_filters.append('sepia')
        if input_data.black_and_white:
            all_filters.append('black_and_white')
        if input_data.brightness:
            all_filters.append('brightness')
        if input_data.darkness:
            all_filters.append('darkness')
        if input_data.contrast:
            all_filters.append('contrast')
        if input_data.red:
            all_filters.append('red')
        if input_data.green:
            all_filters.append('green')
        if input_data.blue:
            all_filters.append('blue')
        if input_data.cool:
            all_filters.append('cool')
        if input_data.warm:
            all_filters.append('warm')

        image_base64_strings = []
        image_file_paths = []

        for index, input_image in enumerate(input_data.input_images):
            image = self._load_image(input_image)
            modified_image = self._apply_filters(image, all_filters)

            image_file_path = ""
            if input_data.output_type == "file" or input_data.output_type == "both":
                image_file_path = f"{self.results_path}/modified_image_{index}.png"
                modified_image.save(image_file_path)
                image_file_paths.append(image_file_path)

            image_base64_string = ""
            if input_data.output_type == "base64_string" or input_data.output_type == "both":
                buffered = BytesIO()
                modified_image.save(buffered, format="PNG")
                image_base64_string = base64.b64encode(buffered.getvalue()).decode('utf-8')
                image_base64_strings.append(image_base64_string)

        if image_base64_strings or image_file_paths:
            self.display_result = {
                "file_type": "png",
                "base64_content": image_base64_strings[0] if image_base64_strings else "",
                "file_path": image_file_paths[0] if image_file_paths else "",
            }

        return OutputModel(
            image_base64_strings=image_base64_strings,
            image_file_paths=image_file_paths,
        )
