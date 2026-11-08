from typing import Any
import usb.core

from brother_ql.backends.helpers import send
from brother_ql.conversion import convert
from brother_ql.raster import BrotherQLRaster
from brother_ql.devicedependent import label_type_specs
from PIL import Image

from src.util.logger import get_logger

PRINTER_BACKEND = "pyusb"
LABEL_TYPE = "62"

logger = get_logger()


class PrinterNotFoundError(RuntimeError):
    pass


def get_printer():
    printers = [
        ("QL-810W", 0x209e),
        ("QL-800",  0x209b),
        ("QL-700",  0x2042),
    ]

    for model, pid in printers:
        dev = usb.core.find(idVendor=0x04F9, idProduct=pid)
        if dev:
            logger.info(f"Found {model}")
            return model, dev

    raise PrinterNotFoundError("Brother printer not found")


def print_label(label: Image.Image) -> dict[str, Any]:

    printer_model, printer = get_printer()

    qlr = BrotherQLRaster(printer_model)

    dots_printable = label_type_specs[LABEL_TYPE]["dots_printable"]

    if label.size[0] != dots_printable[0]:
        hsize = int((dots_printable[0] / label.size[0]) * label.size[1])
        label = label.resize((dots_printable[0], hsize), Image.LANCZOS)

    label = label.convert("1")

    supports_red = printer_model in ("QL-800", "QL-810W")

    instructions = convert(
        qlr,
        [label],
        label=LABEL_TYPE,
        red=supports_red,
    )

    result = send(
        instructions=instructions,
        printer_identifier=printer,
        backend_identifier=PRINTER_BACKEND,
        blocking=False,
    )

    if result is None:
        return {
            "printer_state": {
                "errors": []
            }
        }

    return result


