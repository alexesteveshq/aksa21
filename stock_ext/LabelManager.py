import zpl


class LabelManager:

    @staticmethod
    def generate_label_data(code):
        label = zpl.Label(100, 100)
        height = 5
        label.origin(5, height)
        label.write_barcode(height=80, barcode_type='C', check_digit='Y', orientation='I')
        label.write_text(f'{code}')
        label.endorigin()
        return label
