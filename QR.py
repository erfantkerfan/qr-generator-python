import qrcode
from PIL import Image
from datetime import datetime
import time
import psutil
import hashlib
import os
from reportlab.pdfgen import canvas
from PyPDF2 import PdfFileWriter, PdfFileReader


def config():
    global size, pdf_on, alaa_logo_on, alaa_logo_ratio, base_url
    base_url = 'https://alaatv.com/c/'
    size = int(input("output size [5 to 500 default is 20] ? : ") or 20)
    pdf_on = int(input("pdf wil be generated [0 or 1 default is 0][input file is input.pdf] ? : ") or 1)
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
        for line in file:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=size,
                border=1,
            )
            link = base_url + line.split(",")[0].rstrip('\n')
            print()
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
            name = str(os.path.join(now, os.path.basename(link))) + '.png'
            img.save(name)


def pdf():
    with open('QR_list.txt') as file:
        output_file = PdfFileWriter()
        with open("input.pdf", "rb") as inpt:
            input_file = PdfFileReader(inpt)
            # page_count = input_file.getNumPages()
            # print(file.readlines())
            # page_list = [x.split(",")[1].rstrip('\n') for x in file.readlines()]
            # print(page_list)
            # exit()
            # for page_number in range(page_count):
            for line in file:
                # temp_name = hashlib.md5(line.encode()).hexdigest() + '.pdf'
                link = base_url + line.split(",")[0].rstrip('\n')
                file_name = "water.pdf"
                c = canvas.Canvas(file_name)
                c.drawImage(str(os.path.join(now, line.split(",")[0].rstrip('\n'))) + ".png", 525, 772, 70, 70)
                c.linkURL(link, [525, 772, 525 + 70, 772 + 70], )
                c.save()
                with open("water.pdf", "rb") as water:
                    watermark = PdfFileReader(water)

                    page_number = int(line.split(",")[1].rstrip('\n')) +1
                    input_page = input_file.getPage(page_number)
                    input_page.mergePage(watermark.getPage(0))
                    output_file.addPage(input_page)
                os.remove("water.pdf")

            # finally, write "output" to output.pdf
            with open("output.pdf", "wb") as outputStream:
                output_file.write(outputStream)

        # os.remove("temp.pdf")
    # temp.close()


if __name__ == "__main__":
    config()
    generate_qr()
    if pdf_on:
        pdf()
        # proc = psutil.Process()
        # print(proc.open_files())
