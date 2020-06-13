import qrcode
from PIL import Image
from datetime import datetime
import os

size = int(input("output size [5 to 500 default is 20] ? : ") or 20)
alaa_logo_on = int(input("is Alaa logo on [0 or 1 default is 1] ? : ") or 1)
if alaa_logo_on:
    alaa_logo_ratio = int(input("Alaa logo ratio size [1 to 100 default is 35] ? : ") or 35)

now = datetime.now()
now = str(now).replace(":", "-")
now = str(now).replace(".", "-")
os.mkdir(now)
with open('QR_list.txt') as file:
    for line in file:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=size,
            border=1,
        )
        data = line.rstrip('\n')
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#202952", back_color="#FFFFFF").convert('RGB')

        if alaa_logo_on:
            logo = Image.open('logo.png')
            ratio = alaa_logo_ratio / 100
            out = tuple([int(ratio * s) for s in img.size])
            logo = logo.resize(out, Image.ANTIALIAS)
            pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
            img.paste(logo, pos, logo)
        img.save(str(os.path.join(now, os.path.basename(data))) + '.png')
