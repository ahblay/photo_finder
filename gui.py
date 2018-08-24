import sys
from PyQt5.QtWidgets import QApplication, QPushButton, QGroupBox, QDialog, QVBoxLayout, \
    QGridLayout, QLabel, QLineEdit, QFileDialog, QMessageBox, QProgressBar, QScrollArea
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, pyqtSlot, QSize, QThread
import photo_finder as finder
from pprint import pprint as pp
import build_index
from os import path
from time import sleep

'''
class ProgressThread(QThread):
    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
'''




class App(QDialog):
    def __init__(self):
        super().__init__()
        self.title = 'Photo Finder'
        self.left = 10
        self.top = 10
        self.width = 780
        self.height = 800
        self.scroll = QScrollArea()
        self.horizontalGroupBox = QGroupBox()
        self.layout = QGridLayout()
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        windowLayout = QVBoxLayout()
        button_layout = QGridLayout()

        # Create textbox
        self.textbox = QLineEdit(self)
        self.textbox.setEnabled(True)

        # Create a button in the window
        self.open = QPushButton('Open', self)
        self.open.clicked.connect(self.open_file)

        # Create a button in the window
        self.update = QPushButton('Update Index', self)
        self.update.setEnabled(False)
        self.update.clicked.connect(self.update_index)

        self.update_progress = QProgressBar(self)
        self.update_progress.setGeometry(200, 80, 250, 20)

        # Create a button in the window
        self.search = QPushButton('Search', self)
        self.search.setEnabled(True)
        self.search.clicked.connect(self.on_search)

        self.search_progress = QProgressBar(self)
        self.search_progress.setGeometry(200, 80, 250, 20)

        # Create a button in the window
        self.clear = QPushButton('Clear Results', self)
        self.clear.setEnabled(True)
        self.clear.clicked.connect(self.clear_results)

        button_layout.addWidget(self.open, 0, 0)
        button_layout.addWidget(self.update, 0, 1)
        button_layout.addWidget(self.update_progress, 1, 0)
        button_layout.addWidget(self.textbox, 2, 0)
        button_layout.addWidget(self.search, 2, 1)
        button_layout.addWidget(self.search_progress, 3, 0)

        windowLayout.addLayout(button_layout)
        #windowLayout.addWidget(self.horizontalGroupBox)
        windowLayout.addWidget(self.scroll)
        windowLayout.addWidget(self.clear)

        self.setLayout(windowLayout)

        self.show()

    def clear_results(self):
        finder.clear_results()
        self.delete_group_box(self.horizontalGroupBox)

    def delete_group_box(self, group_box):
        group_box.deleteLater()
        self.horizontalGroupBox = QGroupBox()
        self.layout = QGridLayout()

    def open_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name = QFileDialog.getExistingDirectory(self, "Select Directory")
        if file_name:
            self.location = file_name
            self.update.setEnabled(True)
            print(file_name)

    def update_index(self):
        if self.location:
            # THIS LINE DELETES OLD INDEX
            #finder.create_trie("master_index_trie")
            print("Trie created.")
            #finder.build_index(self.location)
            build_index.get_photos(self.location)
            self.search.setEnabled(True)
            self.textbox.setEnabled(True)
        else:
            print("Location does not exist.")

    @pyqtSlot()
    def on_search(self):
        textboxValue = self.textbox.text().split(", ")
        results = finder.get_photos(textboxValue)
        pp(results)
        pixmap = []

        operations = len(results)
        completion = 0

        if not results:
            print("Query not found.")
            self.show_warning_modal(textboxValue)
        else:
            for photo in results.keys():
                finder.save_to_results(photo)
                pixmap.append(
                    (QPixmap("results/" + path.basename(photo)),
                     photo,
                     results[photo])
                )

                completion += (100 / operations)
                self.search_progress.setValue(int(completion))
                print(self.search_progress.value())

            self.addGridWidget(pixmap)
            self.clear.setEnabled(True)

    def addGridWidget(self, pictures):
        row = 0
        column = 0

        for item in pictures:
            picture = item[0]
            path = item[1]
            keywords = item[2]
            button = QPushButton('', self)
            button.setIcon(QIcon(picture))
            button.setIconSize(QSize(128, 128))
            button.clicked.connect(self.make_open_thumbnail(picture))

            desc = "\n".join([str(x) for x in keywords])

            lbl = QLabel(desc)

            self.layout.addWidget(button, row, column)
            column += 1
            self.layout.addWidget(lbl, row, column)
            column += 1

            if column > 3:
                column = 0
                row += 1

        self.horizontalGroupBox.setLayout(self.layout)
        self.scroll.setWidget(self.horizontalGroupBox)

    def clearLayout(self, layout):
        while layout.count() > 0:
            item = layout.takeAt(0)
            if not item:
                continue
            w = item.widget()
            if w:
                w.deleteLater()
                w.widget_name = None

    def show_warning_modal(self, query):
        modal = QMessageBox.question(self,
                                     'Error',
                                     "No photos of '" + str(query) + "' exist.",
                                     QMessageBox.Ok,
                                     QMessageBox.Ok)

    def make_open_thumbnail(self, photo):
        def open_thumbnail():
            print(photo)
            self.buildExamplePopup("blah", photo)
        return open_thumbnail

    @pyqtSlot()
    def buildExamplePopup(self, name, photo):
        exPopup = ExamplePopup(name, photo, self)
        exPopup.show()


class ExamplePopup(QDialog):
    def __init__(self, name, photo, parent=None):
        super().__init__(parent)
        self.name = name
        self.label = QLabel(self.name, self)
        self.photo = photo.scaled(800, 800, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.label.setPixmap(self.photo)
        self.width = self.photo.width()
        self.height = self.photo.height()
        self.setGeometry(50, 50, self.width, self.height)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())