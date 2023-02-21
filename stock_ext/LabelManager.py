import zpl


class LabelManager:

    @staticmethod
    def generate_label_data(data):
        label = zpl.Label(100, 100)
        label.origin(5, 3)
        label.write_barcode(height=80, barcode_type='C', check_digit='Y', orientation='I')
        label.write_text(f'{data["code"]}')
        label.endorigin()
        label.origin(4, 14)
        label.write_text(f'{data["product"].upper()}', char_height=2.5, char_width=2.5)
        label.endorigin()
        label.origin(10, 17)
        label.write_text(f'{data["weight"]}', char_height=1.5, char_width=1.5)
        label.endorigin()
        label.origin(3, 20)
        label.write_text(f'{"USD " + data["price_usd"]}', char_height=2.5, char_width=2.5)
        label.endorigin()
        label.origin(15, 20)
        label.write_text(f'{"MXN " + data["price_mxn"]}', char_height=2.5, char_width=2.5)
        label.endorigin()
        return label
