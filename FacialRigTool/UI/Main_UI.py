from PySide2 import QtWidgets, QtCore
import maya.OpenMayaUI as omui
import os
import time
import json
import Splitter_UI
import Rig_UI
from shiboken2 import wrapInstance
import maya.cmds as cmds
from ..skinLib import skinLib

from ..rig import *

import logging

reload(Splitter_UI)
reload(Rig_UI)
reload(cartoonEyeLidRig)
reload(singleLineRig)
reload(vertex2Rig)

reload(skinLib)

logging.basicConfig()
logger = logging.getLogger('FacialRiggingTool')
logger.setLevel(logging.INFO)


def getMayaMainWindow():
    """
    get maya main window
    :return: ptr of maya main window as QMainWindow
    """
    win = omui.MQtUtil.mainWindow()
    ptr = wrapInstance(long(win), QtWidgets.QMainWindow)
    return ptr


def deleteDock(name='FacialRiggingTool'):
    """
    delete the Dock
    :param name: Dock name
    :return: None
    """
    if cmds.workspaceControl(name, query=1, exists=1):
        cmds.deleteUI(name)


def getDock(name='FacialRiggingTool'):
    """
    Delete existing Dock and create a Dock Ctrl, finally return the ptr of the new Dock ctrl
    :param name: Dock name
    :return: ptr of the new create Dock as QWidget
    """
    deleteDock(name)

    ctrl = cmds.workspaceControl(name, dockToMainWindow=('right', 1), label='FacialRiggingTool')

    qtCtrl = omui.MQtUtil.findControl(ctrl)
    ptr = wrapInstance(long(qtCtrl), QtWidgets.QWidget)

    return ptr


class RiggingMainUI(QtWidgets.QWidget):

    rigTypes = {'vertex2Rig': '',
                'singleLineRig': '',
                'cartoonEyeLidRig': ''}

    def __init__(self, dock=1):

        if dock:
            parent = getDock()
        else:
            deleteDock()
            try:
                cmds.deleteUI('FacialRiggingTool')
            except:
                logger.info('No prefious UI exists!')

            parent = QtWidgets.QDialog(parent=getMayaMainWindow())
            parent.setObjectName('FacialRiggingTool')
            parent.setWindowTitle('Facial Rigging Tool')
            parent.setFixedSize(270, 780)
            layout = QtWidgets.QVBoxLayout(parent)

        super(RiggingMainUI, self).__init__(parent=parent)

        self.build()

        self.parent().layout().addWidget(self)

        if not dock:
            self.parent().show()

    def build(self):
        self.setFixedWidth(250)
        self.setFixedHeight(750)
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)

        # tabWidget
        self.mainWidget = QtWidgets.QTabWidget()

        self.mainWidget.setFixedSize(250, 680)
        self.layout().addWidget(self.mainWidget)

        # rig tab
        self.rigTabWidget = QtWidgets.QWidget()

        self.mainWidget.addTab(self.rigTabWidget, 'Rig')

        self.rigTabLayout = QtWidgets.QGridLayout()
        self.rigTabWidget.setLayout(self.rigTabLayout)

        self.layout().setContentsMargins(0, 0, 0, 0)

        # Rig File Name
        self.rigProSplitter = Splitter_UI.Splitter(text='Facial Rigging Tool')
        self.rigTabLayout.addWidget(self.rigProSplitter, 0, 0, 1, 3)

        rigProLabel = QtWidgets.QLabel('Rig Project Name:')
        rigProLabel.setAlignment(QtCore.Qt.AlignCenter)

        self.rigProNameLineEdit = QtWidgets.QLineEdit('')
        self.rigProNameLineEdit.setPlaceholderText('Enter Facial Rig Name')

        self.rigTabLayout.addWidget(rigProLabel, 1, 0)
        self.rigTabLayout.addWidget(self.rigProNameLineEdit, 1, 1, 1, 2)

        # combo splitter
        self.rigCBSpllter = Splitter_UI.Splitter(text='Select & Add')
        self.rigTabLayout.addWidget(self.rigCBSpllter, 2, 0, 1, 3)

        # rig combo and add
        self.rigTypeCB = QtWidgets.QComboBox()

        self.rigTypeCB.clear()
        for rigType in sorted(self.rigTypes.keys()):
            self.rigTypeCB.addItem(rigType)

        self.rigTabLayout.addWidget(self.rigTypeCB, 3, 0, 1, 2)

        self.rigAddBtn = QtWidgets.QPushButton('Add')
        self.rigAddBtn.clicked.connect(self.addRigWidget)
        self.rigTabLayout.addWidget(self.rigAddBtn, 3, 2, 1, 1)

        # scroll widget
        self.rigScrollWidget = QtWidgets.QWidget()
        self.scrollLayout = QtWidgets.QVBoxLayout()
        self.scrollLayout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.rigScrollWidget.setLayout(self.scrollLayout)

        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setFixedWidth(230)
        self.scrollArea.setFixedHeight(390)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.rigScrollWidget)
        self.scrollArea.setFocusPolicy(QtCore.Qt.NoFocus)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.rigTabLayout.addWidget(self.scrollArea, 4, 0, 1, 3)

        # utils splitter
        self.rigUtilsSplitter = Splitter_UI.Splitter(text='Rig Utils')
        self.rigTabLayout.addWidget(self.rigUtilsSplitter, 5, 0, 1, 3)

        # action widget
        self.actionWidget = QtWidgets.QWidget()
        self.actionLayout = QtWidgets.QHBoxLayout()

        self.actionWidget.setLayout(self.actionLayout)

        self.rigTabLayout.addWidget(self.actionWidget, 6, 0, 1, 3)

        # save button
        self.saveBtn = QtWidgets.QPushButton('Save Rig')
        self.saveBtn.clicked.connect(self.saveRig)
        self.actionLayout.addWidget(self.saveBtn)

        # import button
        self.importBtn = QtWidgets.QPushButton('ImportRig')
        self.importBtn.clicked.connect(self.importRig)
        self.actionLayout.addWidget(self.importBtn)

        # clear button
        self.clearBtn = QtWidgets.QPushButton('Clear Rig')
        self.clearBtn.clicked.connect(self.clearRig)
        self.actionLayout.addWidget(self.clearBtn)

        # rig splitter
        self.rigSplitter = Splitter_UI.Splitter(text='Rig Action')
        self.rigTabLayout.addWidget(self.rigSplitter, 7, 0, 1, 3)

        # rig widget
        self.rigWidget = QtWidgets.QWidget()
        self.rigLayout = QtWidgets.QHBoxLayout()

        self.rigWidget.setLayout(self.rigLayout)

        self.rigLayout.setAlignment(QtCore.Qt.AlignCenter)

        self.rigCreateBtn = QtWidgets.QPushButton('Create RIG')
        self.rigCreateBtn.setFixedWidth(120)
        self.rigCreateBtn.clicked.connect(self.createRig)
        self.rigLayout.addWidget(self.rigCreateBtn)

        self.rigTabLayout.addWidget(self.rigWidget, 8, 0, 1, 3)

        # helper joints widget
        self.secondWidget = QtWidgets.QWidget()
        self.mainWidget.addTab(self.secondWidget, 'Helper')

        #####################################################################################
        # skin splitter
        self.skinSplitter = Splitter_UI.Splitter(text='Skin Action')
        self.layout().addWidget(self.skinSplitter)
        self.skinWidget = QtWidgets.QWidget()
        self.layout().addWidget(self.skinWidget)
        self.skinLayout = QtWidgets.QHBoxLayout()
        self.skinWidget.setLayout(self.skinLayout)

        # import Skin
        self.importSkinBtn = QtWidgets.QPushButton('Import Skin')
        self.exportSkinBtn = QtWidgets.QPushButton('Export Skin')

        self.skinLayout.addWidget(self.importSkinBtn)
        self.skinLayout.addWidget(self.exportSkinBtn)

        self.importSkinBtn.clicked.connect(skinLib.SkinCluster.createAndImport)
        self.exportSkinBtn.clicked.connect(skinLib.SkinCluster.export)

    def addRigWidget(self, rigType=None):
        """
        Add rig widget to the scroll Layout with specified rigType
        :param rigType: rigType of the rig widget
        :return: None
        """
        if not rigType:
            rigType = self.rigTypeCB.currentText()

        self.widget = Rig_UI.RigWidget(rigTypeName=rigType)
        self.scrollLayout.addWidget(self.widget)

        logger.info('Add a %s Rig Part' % rigType)

    def importRig(self):
        """
        Get the rigLog file from the specified directory and set the rig
        :return: None
        """
        directory = self.getDirectory()

        fileName = QtWidgets.QFileDialog.getOpenFileName(self, 'Rig File Browser', directory)

        if not fileName[0]:
            logger.info('You have selected a null file, please check and select again.')
            return
        else:
            with open(fileName[0], 'r') as f:
                properties = json.load(f)

                if not properties:
                    raise RuntimeError('Rig Part name not enter, please check the rig file')
                else:
                    # Set the rig project name first
                    self.rigProNameLineEdit.setText(str(properties['Procedural Rig Name']))
                    del properties['Procedural Rig Name']

                # set the info
                for key in properties.keys():
                    # Set the rig project name first
                    self.addRigWidget(properties[key]['rigType'])
                    self.widget.rigArgs = properties[key]['rigArgs']
                    self.widget.rigPartLineEdit.setText(str(key))
                    # Be sural to set the rig Part Name of each widget
                    self.widget.setRigPartName()

            logger.info('import %s rig log file.' % fileName[0])

    def saveRig(self):
        """
        Save the rig info to a .json file at the specified directory
        :return: None
        """
        properties = {}
        properties['Procedural Rig Name'] = self.rigProNameLineEdit.text()

        for rig in self.findChildren(Rig_UI.RigWidget):
            if str(rig.rigPartLineEdit.text()) in properties.keys():
                logger.info('Rig file save FAILED, you have already had the same name of rig part!!!')
                break

            properties[str(rig.rigPartLineEdit.text())] = {}
            properties[str(rig.rigPartLineEdit.text())]['rigType'] = rig.rigTypeName
            properties[str(rig.rigPartLineEdit.text())]['rigArgs'] = rig.rigArgs

        if len(properties.keys()) == len(self.findChildren(Rig_UI.RigWidget)) + 1:

            rigLogDir = self.getDirectory()
            rigLogFile = os.path.join(rigLogDir,
                                      self.rigProNameLineEdit.text() + '_rigLogFile_%s.json' % time.strftime('%m%d_%H_%M'))

            with open(rigLogFile, 'w') as f:
                json.dump(properties, f, indent=4)

            logger.info('Saving rig file to %s' % rigLogFile)

    def clearRig(self):
        for rig in self.findChildren(Rig_UI.RigWidget):
            rig.deleteWidget()

    def createRig(self):
        """
        Use the info to create the Rig
        :return:
        """
        if not self.rigProNameLineEdit.text():
            logger.error('No Facial Rig Name Found, Please Input A Facial Rig Name!!!')
            return None
        # Before create the rig, save the rig first!
        self.saveRig()

        for rig in self.findChildren(Rig_UI.RigWidget):
            if rig.rigTypeName == 'vertex2Rig' and rig.rigArgs:
                vertex2Rig.createRig(vertexList=eval(rig.rigArgs['vertexList']),
                                     prefix=rig.rigArgs['prefix'],
                                     rigPartName=rig.rigArgs['rigPartName'],
                                     rigScale=eval(rig.rigArgs['rigScale']),
                                     addSliderCtrls=eval(rig.rigArgs['addSliderCtrls']),
                                     jointParent=rig.rigArgs['jointParent'])
                logger.info('Type:vertex2Rig, %s build complete!' % rig.rigPartLineEdit.text())
                continue

            elif rig.rigTypeName == 'singleLineRig' and rig.rigArgs:
                singleLineRig.createRig(selectedLines=eval(rig.rigArgs['selectedLines']),
                                        prefix=rig.rigArgs['prefix'],
                                        rigScale=eval(rig.rigArgs['rigScale']),
                                        rigPartName=rig.rigArgs['rigPartName'],
                                        numJnt=eval(rig.rigArgs['numJnt']),
                                        addSliderCtrls=eval(rig.rigArgs['addSliderCtrls']),
                                        jointParent=rig.rigArgs['jointParent'])
                logger.info('Type:singleLineRig, %s build complete!' % rig.rigPartLineEdit.text())
                continue

            elif rig.rigTypeName == 'cartoonEyeLidRig' and rig.rigArgs:
                cartoonEyeLidRig.createRig(upperVertexList=eval(rig.rigArgs['upperVertexList']),
                                           lowerVertexList=eval(rig.rigArgs['lowerVertexList']),
                                           prefix=rig.rigArgs['prefix'],
                                           rigPartName=rig.rigArgs['rigPartName'],
                                           rigScale=eval(rig.rigArgs['rigScale']),
                                           eyeJoint=rig.rigArgs['eyeJoint'],
                                           numCtrl=eval(rig.rigArgs['numCtrl']))
                logger.info('Type:cartoonEyeLidRig, %s build complete!' % rig.rigPartLineEdit.text())
                continue

            else:
                logger.info('Can not find the Type: %s rig part, please check again!' % str(rig.rigTypeName))

        logger.info('Project: %s create rig complete!' % str(self.rigProNameLineEdit.text()))

    def getDirectory(self):
        """
        set and get the rig Log directory
        :return: rig log directory
        """
        rigLogDir = os.path.join(cmds.internalVar(userAppDir=1), 'FacialRigLogFiles')

        if not os.path.exists(rigLogDir):
            os.mkdir(rigLogDir)

        return rigLogDir
