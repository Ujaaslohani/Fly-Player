from PyQt5.QtWidgets import QApplication,QWidget,QPushButton,QHBoxLayout,QVBoxLayout,\
    QStyle,QSlider,QFileDialog,QLabel,QDesktopWidget,QSpacerItem,QSizePolicy
from PyQt5.QtGui import QIcon,QPalette,QBrush,QPixmap
from PyQt5.QtCore import Qt,QUrl,QEvent,QTimer
from PyQt5.QtMultimedia import QMediaPlayer,QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
import sys

class Window(QWidget):
    def __init__(self): 
        super().__init__()
        self.setWindowIcon(QIcon("icon.ico"))
        self.setWindowTitle("FlyPlayer")

        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(QPixmap("background.jpeg")))
        self.setAutoFillBackground(True)
        self.setPalette(palette)
        self.create_player()

        self.initUI()
        
        self.app = QApplication.instance()
        self.app.installEventFilter(self)

    def initUI(self):
        
        desktop = QDesktopWidget()
        screenRect = desktop.screen().geometry()

        self.resize(screenRect.width(), screenRect.height())
        self.move(0, 0)

        self.show()


    def create_player(self):
        self.mediaPlayer=QMediaPlayer(None,QMediaPlayer.VideoSurface)
        videowidget=QVideoWidget()
        self.openbtn=QPushButton('Open Video')
        self.openbtn.clicked.connect(self.open_file)

        self.playbtn=QPushButton()
        self.playbtn.setEnabled(False)
        self.playbtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playbtn.clicked.connect(self.play_video)

        self.stopbtn=QPushButton()
        self.stopbtn.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stopbtn.clicked.connect(self.stop_video)

        self.fullscreenbtn=QPushButton()
        self.fullscreenbtn.setIcon(QIcon("fullscreen.png"))
        self.fullscreenbtn.clicked.connect(self.fullscreen_video)

        self.slider=QSlider(Qt.Horizontal)
        self.slider.setRange(0,0)
        self.slider.sliderMoved.connect(self.set_position)
        self.slider.setFixedWidth(1250)

        self.volume_slider=QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0,100)
        self.volume_slider.setValue(50)
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.sliderMoved.connect(self.set_volume)

        self.position_label=QLabel("00:00:00")
        self.duration_label=QLabel("00:00:00")

        hbox=QHBoxLayout()
        hbox.setContentsMargins(0,0,0,0)
        hbox.addWidget(self.openbtn)
        hbox.addWidget(self.playbtn)
        hbox.addWidget(self.stopbtn)
        hbox.addWidget(self.fullscreenbtn)
        hbox.addWidget(self.slider)
        hbox.addWidget(self.position_label)
        hbox.addWidget(self.duration_label)
        hbox.addWidget(self.volume_slider)

        vbox=QVBoxLayout()
        vbox.addWidget(videowidget)
        vbox.addLayout(hbox)
        self.mediaPlayer.setVideoOutput(videowidget)
        self.setLayout(vbox)
        
        self.mediaPlayer.stateChanged.connect(self.mediastate_changed)
        self.mediaPlayer.positionChanged.connect(self.position_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)

    def open_file(self):
        filename,_=QFileDialog.getOpenFileName(self,"Open Video")
        if filename!='':
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))
            self.playbtn.setEnabled(True)
            self.play_video()

    def play_video(self):
        if self.mediaPlayer.state()==QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def stop_video(self):
        self.mediaPlayer.stop()

    def fullscreen_video(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def mediastate_changed(self,state):
        if self.mediaPlayer.state()==QMediaPlayer.PlayingState:
            self.playbtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

        else:
            self.playbtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def position_changed(self,position):
        self.slider.setValue(position)
        seconds = position // 1000
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        self.position_label.setText(f"{hours:02}:{minutes:02}:{seconds:02}")

    def duration_changed(self,duration):
        self.slider.setRange(0,duration)
        seconds = duration // 1000
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        self.duration_label.setText(f"{hours:02}:{minutes:02}:{seconds:02}")

    def set_position(self,position):
        self.mediaPlayer.setPosition(position)

    def set_volume(self,value):
        self.mediaPlayer.setVolume(value)



    def seek_backward(self):
        current_position = self.mediaPlayer.position()
        new_position = max(0, current_position - 5000)  
        self.mediaPlayer.setPosition(new_position)

    def seek_forward(self):
        current_position = self.mediaPlayer.position()
        duration = self.mediaPlayer.duration()
        new_position = min(duration, current_position + 5000) 
        self.mediaPlayer.setPosition(new_position)


    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyRelease:
            if event.key() == Qt.Key_Left:
                self.seek_backward()
            elif event.key() == Qt.Key_Right:
                self.seek_forward()
            elif event.key() == Qt.Key_Up:
                self.volume_up()
            elif event.key() == Qt.Key_Down:
                self.volume_down()
            elif event.key() == Qt.Key_M:
                self.mute_unmute()
            elif event.key() == Qt.Key_Space:
                self.toggle_playback()
            elif event.key() == Qt.Key_F:
                if self.isFullScreen():
                    self.showNormal()
                else:
                    self.showFullScreen()
            return True
        return super().eventFilter(obj, event)
    
    def toggle_playback(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()
        
    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.volume_up()
        else:
            self.volume_down()

    def volume_up(self):
        current_volume = self.mediaPlayer.volume()
        if current_volume < 100:
            self.mediaPlayer.setVolume(current_volume + 10)

    def volume_down(self):
        current_volume = self.mediaPlayer.volume()
        if current_volume > 0:
            self.mediaPlayer.setVolume(current_volume - 10)

    def mute_unmute(self):
        if self.mediaPlayer.isMuted():
            self.mediaPlayer.setMuted(False)
        else:
            self.mediaPlayer.setMuted(True)
        
app=QApplication(sys.argv)
w=Window()
w.showMaximized()
sys.exit(app.exec_())