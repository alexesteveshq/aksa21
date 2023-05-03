import zpl


class LabelManager:

    @staticmethod
    def generate_label_data(data):
        label = zpl.Label(100, 100)
        label.origin(1, 5)
        label.write_barcode(height=60, barcode_type='C', check_digit='Y', orientation='I')
        label.write_text(f'{data["code"]}')
        label.endorigin()
        label.origin(3, 13)
        label.write_text(f'{data["product"].upper()}', char_height=2.5, char_width=2.5)
        label.endorigin()
        label.origin(9, 16)
        label.write_text(f'{data["weight"]}', char_height=1.5, char_width=1.5)
        label.endorigin()
        label.origin(2, 19)
        label.write_text(f'{"USD " + data["price_usd"]}', char_height=2.5, char_width=2.5)
        label.endorigin()
        label.origin(14, 19)
        label.write_text(f'{"MXN " + data["price_mxn"]}', char_height=2.5, char_width=2.5)
        label.endorigin()
        return label
