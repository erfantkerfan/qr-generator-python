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
from progress.bar import Bar
from reportlab.pdfgen import canvas


def config():
    global size, pdf_on, alaa_logo_on, alaa_logo_ratio, type
    size = int(input('output size [5 to 500 default is 20] ? : ') or 20)
    pdf_on = int(input('pdf wil be generated [0 or 1 default is 0][input file is input.pdf] ? : ') or 0)
    if pdf_on:
        user_input = input('pdf type [Arash or Letter or Free default is Free] ? : ') or 'free'

        type = [k for k in MAP.keys() if user_input.lower() in MAP[k]][0]
    alaa_logo_on = int(input('is Alaa logo on [0 or 1 default is 0] ? : ') or 0)
    if alaa_logo_on:
        alaa_logo_ratio = int(input('Alaa logo ratio size [1 to 100 default is 35] ? : ') or 35)


def generate_qr():
    global now
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
            link = line.split(',')[0].rstrip('\n')
            qr.add_data(link)
            qr.make(fit=True)
            img = qr.make_image(fill_color='#202952', back_color='#FFFFFF').convert('RGB')

            if alaa_logo_on:
                logo = Image.open('logo.png')
                ratio = alaa_logo_ratio / 100
                out = tuple([int(ratio * s) for s in img.size])
                logo = logo.resize(out, Image.ANTIALIAS)
                pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
                img.paste(logo, pos, logo)
            name = str(os.path.join(now, os.path.basename(link.split('?')[0]))) + '.png'
            img.save(name)
            bar.next()
        bar.finish()


def pdf():
    with open(QR_CODE_LIST_FILE) as file:
        txt = [x.rstrip('\n') for x in file.readlines()]
    output_file = PdfFileWriter()
    with open(INPUT_PDF_FILE, 'rb') as inpt:
        input_file = PdfFileReader(inpt)
        page_count = input_file.getNumPages()
        page_list = [str(int(x.split(',')[1]) - 1) for x in txt]
        url_list = [x.split(',')[0] for x in txt]
        file_name = 'water.pdf'
        bar = Bar('Processing', max=page_count)
        for i, page_number in enumerate(range(page_count)):
            if str(page_number) in page_list:
                link = url_list[page_list.index(str(page_number))]
                c = canvas.Canvas(file_name)
                if type == 'Letter':
                    dimension = 65
                    width = 528
                    height = 741
                elif type == 'Arash':
                    dimension = 70
                    width = 525
                    height = 772
                elif type == 'Free':
                    dimension = 70
                    width = 0
                    height = 0
                c.drawImage(str(os.path.join(now, os.path.basename(link.split('?')[0]))) + '.png', width, height,
                            dimension, dimension)
                c.linkURL(link, [width, height, width + dimension, height + dimension], )
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


def update():
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
    root.title('Alaa studio app')
    update_title = tk.Label(root, text='در حال بروزرسانی از اینترنت')
    update_title.pack(pady=20)
    progress_bar = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=200, mode='determinate')
    progress_bar.pack(pady=10)
    t = threading.Thread(target=progress)
    progress = 1
    t.start()
    root.mainloop()


def reload(updated=False):
    if updated:
        os.execv(sys.executable, ['python ' + str(__file__) + ' updated'])
    else:
        os.execv(sys.executable, ['python ' + str(__file__)])


if __name__ == '__main__':
    MAP = {
        'Arash': ['1', 'arash', 'a', 'ar'],
        'Letter': ['2', 'letter', 'l', 'le'],
        'Free': ['3', 'free', 'fr', 'f']
    }
    QR_CODE_LIST_FILE = 'QR_list.txt'
    OUTPUT_PDF_FILE = 'output.pdf'
    INPUT_PDF_FILE = 'input.pdf'

    VERSION = '2.0.0'
    load_dotenv()
    DEBUG = bool(os.getenv("DEBUG"))
    GIT_REMOTE = os.getenv("GIT_REMOTE")
    GIT_BRANCH = os.getenv("GIT_BRANCH")

    if DEBUG or (len(sys.argv) > 1 and sys.argv[1] == 'updated'):
        config()
        generate_qr()
        if pdf_on:
            pdf()
    else:
        tt = threading.Thread(target=waiting)
        tt.start()

        root.quit()
        os._exit(0)
