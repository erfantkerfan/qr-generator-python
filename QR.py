import os
from datetime import datetime

import qrcode
from PIL import Image
from PyPDF4 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas


def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r\n%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


def config():
    global size, pdf_on, alaa_logo_on, alaa_logo_ratio
    size = int(input("output size [5 to 500 default is 20] ? : ") or 20)
    pdf_on = int(input("pdf wil be generated [0 or 1 default is 0][input file is input.pdf] ? : ") or 0)
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
        x = len(file.readlines())
        printProgressBar(0, x, prefix='Progress:', suffix='Complete', length=50)
        file.seek(0)
        for i, line in enumerate(file):
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
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
            name = str(os.path.join(now, os.path.basename(link))) + '.png'
            img.save(name)
            printProgressBar(i + 1, x, prefix='Progress:', suffix='Complete', length=50)


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

        printProgressBar(0, page_count, prefix='Progress:', suffix='Complete', length=50)
        for i, page_number in enumerate(range(page_count)):
            if str(page_number) in page_list:
                link = url_list[page_list.index(str(page_number))]

                c = canvas.Canvas(file_name)
                c.drawImage(
                    str(os.path.join(now, os.path.basename(link))) + ".png",
                    525, 772,
                    70, 70)
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
            printProgressBar(i + 1, page_count, prefix='Progress:', suffix='Complete', length=50)

    os.remove(file_name)


if __name__ == "__main__":
    config()
    generate_qr()
    if pdf_on:
        pdf()
