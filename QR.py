import os
import subprocess
import sys
import threading
import time
import tkinter as tk
import tkinter.ttk as ttk
from datetime import datetime

import qrcode
from PIL import Image
from PyPDF4 import PdfFileWriter, PdfFileReader
from dotenv import load_dotenv
from pick import pick
from progress.bar import Bar
from reportlab.pdfgen import canvas

VERSION = '2.1.0'
PLACEMENT_OPTIONS = [
    {'name': 'Abrisham', 'dimension': 70, 'width': 0, 'height': 0},
    {'name': 'Fadaee Fard', 'dimension': 70, 'width': 0, 'height': 772},
    {'name': 'Free', 'dimension': 70, 'width': 0, 'height': 0},
    {'name': 'Letter', 'dimension': 70, 'width': 525, 'height': 772},
    {'name': 'Arash', 'dimension': 65, 'width': 528, 'height': 741},
]
UTM_OPTIONS = [
    {'name': 'None', 'utm_link': ''},
    {'name': 'abrisham', 'utm_link': '?utm_source=alaatv&utm_medium=qrCode&utm_campaign=pdf&utm_term=abrisham'},
    {'name': 'nooshdaru', 'utm_link': '?utm_source=alaatv&utm_medium=qrCode&utm_campaign=pdf&utm_term=nooshdaru'},
    {'name': 'arash', 'utm_link': '?utm_source=alaatv&utm_medium=qrCode&utm_campaign=pdf&utm_term=arash'},
]
SIZE_OPTIONS = [20, 5, 50, 100, 200, 300, 400]
PERCENT_OPTIONS = [35, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]


# get initialising values from user via console
def config():
    global size, pdf_on, alaa_logo_on, alaa_logo_ratio, placement, utm_link

    # size of the image (represents quality)
    title = 'Please your QUALITY of image output :'
    size, index = pick(SIZE_OPTIONS, title)

    # select utm link
    title = 'Please choose your UTM term:'
    _, index = pick([option['name'] for option in UTM_OPTIONS], title)
    utm_link = UTM_OPTIONS[index]['utm_link']

    # logo is printed on qr-code or not
    title = 'Do you want AlaaTv LOGO ?'
    alaa_logo_on, index = pick([1, 0], title)

    # percent used by logo on qr-code
    if alaa_logo_on:
        title = 'Please space used by LOGO in image in percent(%) :'
        alaa_logo_ratio, index = pick(PERCENT_OPTIONS, title)

    # pdf will be generated or not
    title = 'Do you want PDF version ?'
    pdf_on, index = pick([1, 0], title)

    if pdf_on:
        title = 'Please choose your type of PAMPHLET :'
        _, index = pick([option['name'] for option in PLACEMENT_OPTIONS], title)
        placement = PLACEMENT_OPTIONS[index]


def generate_qr():
    global now
    # used for naming folders
    now = datetime.now()
    now = str(now).replace(':', '-')
    now = str(now).replace('.', '-')
    os.mkdir(now)
    with open(QR_CODE_LIST_FILE) as file:
        bar = Bar('Processing', max=len(file.readlines()))
        file.seek(0)
        for i, line in enumerate(file):
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=size,
                border=1,
            )
            link = line.split(',')[0].rstrip('\n').split('?')[0]
            qr.add_data(link + utm_link)
            qr.make(fit=True)
            img = qr.make_image(fill_color='#202952', back_color='#FFFFFF').convert('RGB')

            if alaa_logo_on:
                logo = Image.open('logo.png')
                ratio = alaa_logo_ratio / 100
                out = tuple([int(ratio * s) for s in img.size])
                logo = logo.resize(out, Image.ANTIALIAS)
                pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
                img.paste(logo, pos, logo)
            name = str(os.path.join(now, os.path.basename(link))) + '.png'
            img.save(name)
            bar.next()
        bar.finish()


def pdf():
    with open(QR_CODE_LIST_FILE) as file:
        txt = [x.rstrip('\n') for x in file.readlines()]
    # generate empty pdf file
    output_file = PdfFileWriter()
    with open(INPUT_PDF_FILE, 'rb') as inpt:
        input_file = PdfFileReader(inpt)
        page_count = input_file.getNumPages()
        page_list = [str(int(x.split(',')[1]) - 1) for x in txt]
        url_list = [x.split(',')[0] for x in txt]
        # temp pdf file for processing single page (deleted afterward)
        file_name = 'water.pdf'
        bar = Bar('Processing', max=page_count)
        for i, page_number in enumerate(range(page_count)):
            if str(page_number) in page_list:
                link = url_list[page_list.index(str(page_number))].split('?')[0]
                c = canvas.Canvas(file_name)
                dimension = placement['dimension']
                width = placement['width']
                height = placement['height']
                c.drawImage(str(os.path.join(now, os.path.basename(link))) + '.png', width, height,
                            dimension, dimension)
                c.linkURL(link + utm_link, [width, height, width + dimension, height + dimension], )
                c.save()
                with open(file_name, 'rb') as water:
                    watermark = PdfFileReader(water)
                    input_page = input_file.getPage(page_number)
                    input_page.mergePage(watermark.getPage(0))
                    output_file.addPage(input_page)
                    with open(OUTPUT_PDF_FILE, 'wb') as outputStream:
                        output_file.write(outputStream)
            else:
                input_page = input_file.getPage(page_number)
                output_file.addPage(input_page)
                with open(OUTPUT_PDF_FILE, 'wb') as outputStream:
                    output_file.write(outputStream)
            bar.next()
        bar.finish()
    os.remove(file_name)


# update the code with github
def update():
    command0 = 'git remote set-url production https://github.com/erfantkerfan/qr-generator-python'
    process0 = subprocess.Popen(command0, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    status0 = process0.wait()

    command = 'git fetch --all'
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    status = process.wait()

    if status == 0:
        update_text = tk.StringVar()
        update_text.set('✔')
        update_label = tk.Label(root, textvariable=update_text, fg='green')
        update_label.pack(pady=5)
        command = 'git reset --hard ' + GIT_REMOTE + '/' + GIT_BRANCH
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        status = process.wait()
        if status == 0:
            update_text.set('✔ ✔')
            command = 'pip install -r requirements.txt'
            process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, shell=True)
            status = process.wait()
            if status == 0:
                update_text.set('✔ ✔ ✔')
                reload(updated=True)


# show update progress bar
def waiting():
    global root

    def progress():
        while progress:
            if progress_bar['value'] > 100:
                progress_bar['value'] = 0
            progress_bar['value'] += 1
            time.sleep(0.01)

    root = tk.Tk()
    root.geometry("250x150")
    root.resizable(height=None, width=None)
    root.iconbitmap(default=os.path.join(os.getcwd(), 'alaa.ico'))
    # root.protocol('WM_DELETE_WINDOW', root.iconify)
    root.title('Alaa QR-code app')
    update_title = tk.Label(root, text='در حال بروزرسانی از اینترنت')
    update_title.pack(pady=20)
    progress_bar = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=200, mode='determinate')
    progress_bar.pack(pady=10)
    t = threading.Thread(target=progress)
    progress = 1
    t.start()
    root.mainloop()


# reload the app with needed sys arguments
def reload(updated=False):
    if updated:
        os.execv(sys.executable, ['python ' + str(__file__) + ' updated'])
    else:
        os.execv(sys.executable, ['python ' + str(__file__)])


if __name__ == '__main__':
    # set up initial variables
    QR_CODE_LIST_FILE = 'QR_list.txt'
    OUTPUT_PDF_FILE = 'output.pdf'
    INPUT_PDF_FILE = 'input.pdf'
    load_dotenv()
    DEBUG = bool(os.getenv("DEBUG"))
    GIT_REMOTE = 'production'
    GIT_BRANCH = 'master'

    # answer if is update needed?
    if DEBUG or (len(sys.argv) > 1 and sys.argv[1] == 'updated'):
        config()
        generate_qr()
        if pdf_on:
            pdf()
    else:
        tt = threading.Thread(target=waiting)
        tt.start()
        update()
        root.quit()
        os._exit(0)
