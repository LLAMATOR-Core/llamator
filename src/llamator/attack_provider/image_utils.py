import base64
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pymupdf as fitz
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


def imgpath2base64(image_path: Union[str, Path]):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string


def create_vision_messages(
    image_base64: str, vision_prompt: str = "What do you see?", system_prompt: Optional[str] = None
) -> List[Dict[str, Any]]:
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": vision_prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{image_base64}"},
                },
            ],
        }
    ]
    if system_prompt:
        messages.insert(0, {"role": "system", "content": system_prompt})
    return messages


def txt2image(
    text: str,
    img_size: Tuple[int, int] = (600, 400),
    max_words_per_line: int = 3,
) -> Image.Image:
    """Creates an image with text, wrapping lines by max_words_per_line words."""
    img = Image.new("RGB", img_size, color="white")
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default(size=50)

    # Split text into lines
    words = text.split()
    lines = [" ".join(words[i : i + max_words_per_line]) for i in range(0, len(words), max_words_per_line)]
    text_width = max([draw.textbbox((0, 0), line, font=font)[2] for line in lines])

    # Calculate text height
    line_height = draw.textbbox((0, 0), "Ay", font=font)[3]
    total_text_height = line_height * len(lines)

    # Create image with required size
    img = Image.new("RGB", (img_size[0], img_size[1]), color="white")
    draw = ImageDraw.Draw(img)

    # Draw text
    y_offset = img_size[1] // 2 - total_text_height // 2
    for line in lines:
        x_position = (img_size[0] - text_width) // 2
        draw.text((x_position, y_offset), line, font=font, fill="black")
        y_offset += line_height

    return img


def lines2images(
    words_file: Path,
    out_dir: Path,
    crop_text: Optional[int] = None,
) -> None:
    """Creates images for all words in the input file."""
    save_dir = out_dir / words_file.stem
    save_dir.mkdir(parents=True, exist_ok=True)

    words = words_file.read_text().splitlines()
    for word in words:
        img = txt2image(word)
        fname_str = word.replace(" ", "_")
        if crop_text is not None:
            fname_str = fname_str[:crop_text]
        fname = save_dir / f"{fname_str}.png"
        img.save(fname)
        logger.info(f"Saved image '{fname.name}'")
    logger.info(f"Created {len(words)} images for '{words_file.stem}'")


def page2image(page: fitz.Page, rescale: float = 1.0, default_dpi: int = 72) -> Image.Image:
    # Convert page to pixmap
    new_dpi = int(default_dpi * rescale)
    pix = page.get_pixmap(dpi=new_dpi)  # pyright: ignore

    # Convert pixmap to PIL Image
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

    # Resize image to original size
    img = img.resize((int(pix.width / rescale), int(pix.height / rescale)))
    return img


def pdf2images(
    path: Path, is_long_flag: bool = False, rescale: float = 1.0, idxs: Optional[List[int]] = None
) -> List[Image.Image]:
    doc = fitz.open(path)
    images = []
    range_len = min(10, doc.page_count) if is_long_flag else doc.page_count
    for idx in idxs or range(range_len):
        page = doc.load_page(idx)
        img = page2image(page, rescale=rescale)
        images.append(img)
    return images
