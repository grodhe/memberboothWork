#import usb.core

#dev = usb.core.find(idVendor=0x04f9, idProduct=0x2042)
#print(dev)

from PIL import Image, ImageDraw

from brother_ql.raster import BrotherQLRaster
from brother_ql.conversion import convert
from brother_ql.backends.helpers import send

#img = Image.new("RGB", (696, 150), "white")
#draw = ImageDraw.Draw(img)
#draw.text((30,30), "QL700 TEST", fill="black")

#img = Image.new("1", (696, 150), 1)
img = Image.new("RGB", (696, 696), "white")
draw = ImageDraw.Draw(img)
draw.text((30,30), "QL700 TEST", fill=0)

qlr = BrotherQLRaster("QL-700")

instructions = convert(
    qlr,
    [img],
    label="62",
    red=False
)

status = send(
    instructions=instructions,
    printer_identifier="usb://0x04f9:0x2042",
    backend_identifier="pyusb",
    blocking=False
)

print(status)
