import sys
import argparse
import base64
from PyQt4 import QtCore, QtGui


TEMPLATE = """
    QByteArray by = QByteArray::fromBase64("{data}");
    QImage image = QImage::fromData(by, "PNG");
    QLabel label;
    label.setPixmap(QPixmap::fromImage(image));
    label.show();
"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", "-o", default=None)
    parser.add_argument("image")
    args = parser.parse_args()
    with open(args.image, "rb") as fh:
        imdata = fh.read()
    b64data = base64.b64encode(imdata)
    fh = open(args.output, "wb") if args.output else sys.stdout
    fh.write(b64data)
    fh.close()



