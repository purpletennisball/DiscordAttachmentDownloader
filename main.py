# Imports
import json, os, requests, ffmpeg, datetime, sys, threading
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QLineEdit, QVBoxLayout, QWidget, QPushButton, QProgressBar, QHBoxLayout, QFileDialog
from PyQt5.QtGui import QFont

titleFont = QFont("Arial", 22)

class FolderSelect(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.path = QLineEdit()
        self.selectorButton = QPushButton("Select Folder")
        self.selectorButton.clicked.connect(self.fileDialog)
        self.layout.addWidget(self.path)
        self.layout.addWidget(self.selectorButton)
        self.layout.setContentsMargins(0,0,0,0)

    def fileDialog(self):
        folderPath = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folderPath:
            self.path.setText(folderPath)

    def text(self):
        return self.path.text()

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.UI()

    def UI(self):
        self.setWindowTitle("DiscordAttachementDownloader")
        self.layout = QVBoxLayout()
        self.title = QLabel("DiscordAttachementDownloader")
        self.title.setFont(titleFont)
        self.messagesFolderText = QLabel("Package Messages Folder")
        self.messagesFolder = FolderSelect()
        self.exportFolderText = QLabel("Found Attachments Folder")
        self.exportFolder = FolderSelect()
        self.startButton = QPushButton("Start")
        self.bar = QProgressBar()
        self.startButton.clicked.connect(self.__download)
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.messagesFolderText)
        self.layout.addWidget(self.messagesFolder)
        self.layout.addWidget(self.exportFolderText)
        self.layout.addWidget(self.exportFolder)
        self.layout.addWidget(self.startButton)
        self.layout.addWidget(self.bar)
        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

    def __download(self):
        threading.Thread(target=self._download, daemon=False).start()

    def _download(self):
        self.download(self.messagesFolder.text(), self.exportFolder.text())
    
    def download(self, folder, exportFolder):
        self.bar.setValue(0)
        print("Checking messages for attachments...")
        attachmentList = []
        channelFolders = os.listdir(folder)
        m4aConvert = False
        audioTypes = ["ogg", "m4a", "mp3", "wav", "aac"]
        for channelFolder in channelFolders:
            if channelFolder != "index.json" or channelFolder != ".DS_Store":
                messageFileLocation = folder + "/" + channelFolder + "/messages.json"
                if os.path.exists(messageFileLocation):
                    with open(messageFileLocation, "r", encoding="utf-8") as file:
                        messages = json.load(file)
                        for message in messages:
                            if message["Attachments"]:
                                for attachment in message["Attachments"].split(" "):
                                    originalName = attachment.split("/")[-1].split("?")[0]
                                    attachmentList.append(
                                        {
                                            "url": attachment,
                                            "date": message["Timestamp"],
                                            "channel": channelFolder,
                                            "originalName": originalName, 
                                            "id": message["ID"]
                                        }
                                    )
        print("Finished")

        attachmentCount = len(attachmentList)
        attachmentsDownloaded = 0
        print(f"Downloading {attachmentCount} Attachements")

        for attachment in attachmentList:
            percent = int(attachmentsDownloaded/attachmentCount*100)
            self.bar.setValue(percent)
            fileName = f"{exportFolder}/discord {attachment["channel"]} m{attachment["id"]} {attachment["originalName"]}"
            newFileName = f"{fileName}.m4a"
            with open(fileName, "wb") as file:
                fail = False
                if not (os.path.exists(newFileName)):
                    # Download file
                    attachmentContents = requests.get(attachment["url"])
                    file.write(attachmentContents.content)
                    # Convert to m4a
                    if m4aConvert:
                        try:
                            if not fileName.endswith("m4a"):
                                ffmpeg.input(fileName).output(newFileName).run()
                            else:
                                with open(newFileName, "wb") as file2:
                                    file2.write(attachmentContents.content)
                        except:
                            fail = True
                if not fail:
                    # Remove Original File
                    if m4aConvert: os.remove(fileName)
                    # Set time of file to message timestamp
                    date, time = attachment["date"].split(" ")
                    year, month, day = date.split("-")
                    hour, minute, second = time.split(":")
                    time = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
                    timestamp = time.timestamp()
                    if m4aConvert: 
                        os.utime(newFileName, (timestamp, timestamp))
                    else:
                        os.utime(fileName, (timestamp, timestamp))
            attachmentsDownloaded = attachmentsDownloaded + 1
        self.bar.setValue(100)


app = QApplication(sys.argv)
window = App()
window.show()
app.exec()