from PySide2 import QtWidgets, QtCore, QtGui
import logging
import Edit_UI
from ..rig import *

reload(Edit_UI)

logging.basicConfig()
logger = logging.getLogger('FacialRiggingTool')
logger.setLevel(logging.INFO)


class RigWidget(QtWidgets.QFrame):

    def __init__(self, rigTypeName):
        super(RigWidget, self).__init__()

        self.setFrameStyle(QtWidgets.QFrame.Panel)
        self.setFrameShadow(QtWidgets.QFrame.Raised)

        self.setFixedHeight(100)
        self.setFixedWidth(200)

        self.rigArgs = {}
        self.rigTypeName = rigTypeName

        self.rigPartLineEdit = None
        self.editBtn = None

        self.buildUI()

    def buildUI(self):
        """
        build the Rig UI
        :return: None
        """
        self.editWidgetLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.editWidgetLayout)

        self.editWidgetLayout.setSpacing(2)

        self.closeBtnLayout = QtWidgets.QHBoxLayout()
        self.editLineLayout = QtWidgets.QHBoxLayout()
        self.editBtnLayout = QtWidgets.QHBoxLayout()

        self.editWidgetLayout.addLayout(self.closeBtnLayout)
        self.editWidgetLayout.addLayout(self.editLineLayout)
        self.editWidgetLayout.addLayout(self.editBtnLayout)

        self.closeBtn = QtWidgets.QPushButton('X')
        self.closeBtn.clicked.connect(self.deleteWidget)
        self.closeBtn.setFixedWidth(25)

        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(1)
        self.rigTypeLable = QtWidgets.QLabel('Type: %s' % self.rigTypeName)
        self.rigTypeLable.setFont(font)

        self.closeBtnLayout.addWidget(self.rigTypeLable)
        self.closeBtnLayout.addWidget(self.closeBtn)

        label = QtWidgets.QLabel('Part Name:  ')
        self.rigPartLineEdit = QtWidgets.QLineEdit()
        self.rigPartLineEdit.setPlaceholderText('Enter a name')
        self.editLineLayout.addWidget(label)
        self.editLineLayout.addWidget(self.rigPartLineEdit)

        self.editBtn = QtWidgets.QPushButton('Edit...')
        self.editBtn.setFixedWidth(80)
        self.editBtn.clicked.connect(self.editRigPart)
        self.editBtnLayout.addWidget(self.editBtn)

    def deleteWidget(self):
        self.setParent(None)
        self.setVisible(False)
        self.deleteLater()

    def editRigPart(self):
        """
        Set the rig part info
        :return: None
        """
        if self.rigTypeName == 'vertex2Rig':
            Edit_UI.EditWidget(self, self.rigTypeName, vertex2Rig.createRig)

        elif self.rigTypeName == 'singleLineRig':
            Edit_UI.EditWidget(self, self.rigTypeName, singleLineRig.createRig)

        elif self.rigTypeName == 'cartoonEyeLidRig':
            Edit_UI.EditWidget(self, self.rigTypeName, cartoonEyeLidRig.createRig)

        else:
            logger.info('Unknow rig type: %s' % self.rigTypeName)

        logger.info('Edit %s Rig Part... (Type: %s)' % (self.rigPartLineEdit.text(), self.rigTypeName))
