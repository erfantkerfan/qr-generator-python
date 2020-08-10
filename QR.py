import os
from datetime import datetime

import qrcode
from PIL import Image
from PyPDF4 import PdfFileWriter, PdfFileReader
from progress.bar import Bar
from reportlab.pdfgen import canvas


def config():
    global size, pdf_on, alaa_logo_on, alaa_logo_ratio, letter
    size = int(input("output size [5 to 500 default is 20] ? : ") or 20)
    pdf_on = int(input("pdf wil be generated [0 or 1 default is 0][input file is input.pdf] ? : ") or 0)
    if pdf_on:
        letter = int(input("pdf is letter size [0 or 1 default is 0] ? : ") or 0)
    alaa_logo_on = int(input("is Alaa logo on [0 or 1 default is 0] ? : ") or 0)
    if alaa_logo_on:
        alaa_logo_ratio = int(input("Alaa logo ratio size [1 to 100 default is 35] ? : ") or 35)


def generate_qr():
    global now
    now = datetime.now()
    now = str(now).replace(":", "-")
    now = str(now).replace(".", "-")
    os.mkdir(now)
    with open('QR_list.txt') as file:
        bar = Bar('Processing', max=len(file.readlines()))
        file.seek(0)
        for i, line in enumerate(file):
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=size,
                border=1,
            )
            link = line.split(",")[0].rstrip('\n')
            qr.add_data(link)
            qr.make(fit=True)
            img = qr.make_image(fill_color="#202952", back_color="#FFFFFF").convert('RGB')

            if alaa_logo_on:
                logo = Image.open('logo.png')
                ratio = alaa_logo_ratio / 100
                out = tuple([int(ratio * s) for s in img.size])
                logo = logo.resize(out, Image.ANTIALIAS)
                pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
                img.paste(logo, pos, logo)
            name = str(os.path.join(now, os.path.basename(link.split("?")[0]))) + '.png'
            img.save(name)
            bar.next()
        bar.finish()


def pdf():
    with open('QR_list.txt') as file:
        txt = [x.rstrip("\n") for x in file.readlines()]
    output_file = PdfFileWriter()
    with open("input.pdf", "rb") as inpt:
        input_file = PdfFileReader(inpt)
        page_count = input_file.getNumPages()
        page_list = [str(int(x.split(",")[1]) - 1) for x in txt]
        url_list = [x.split(",")[0] for x in txt]
        file_name = "water.pdf"
        bar = Bar('Processing', max=page_count)
        for i, page_number in enumerate(range(page_count)):
            if str(page_number) in page_list:
                link = url_list[page_list.index(str(page_number))]
                c = canvas.Canvas(file_name)
                if letter:
                    c.drawImage(str(os.path.join(now, os.path.basename(link.split("?")[0]))) + ".png", 528, 741, 65, 65)
                    c.linkURL(link, [528, 741, 528 + 65, 741 + 65], )
                else:
                    c.drawImage(str(os.path.join(now, os.path.basename(link.split("?")[0]))) + ".png", 525, 772, 70, 70)
                    c.linkURL(link, [525, 772, 525 + 70, 772 + 70], )
                c.save()
                with open(file_name, "rb") as water:
                    watermark = PdfFileReader(water)
                    input_page = input_file.getPage(page_number)
                    input_page.mergePage(watermark.getPage(0))
                    output_file.addPage(input_page)
                    with open("output.pdf", "wb") as outputStream:
                        output_file.write(outputStream)
            else:
                input_page = input_file.getPage(page_number)
                output_file.addPage(input_page)
                with open("output.pdf", "wb") as outputStream:
                    output_file.write(outputStream)
            bar.next()
        bar.finish()
    os.remove(file_name)


if __name__ == "__main__":
    config()
    generate_qr()
    if pdf_on:
        pdf()
