def print_label(path):
    from brother_ql.raster import BrotherQLRaster
    from brother_ql.backends.helpers import send
    from brother_ql.conversion import convert

    qlr = BrotherQLRaster('QL-700')

    instructions = convert(
        qlr=qlr,
        images=label.png,
        label='62',
    )

    send(
        instructions=instructions,
        printer_identifier='usb://0x04f9:0x209b',
        backend_identifier='pyusb'
    )

