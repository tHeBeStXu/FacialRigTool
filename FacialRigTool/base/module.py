"""
module for making top rig structure and rig module
"""

import maya.cmds as cmds
import control
reload(control)

sceneObjectType = 'rig'


class Base():
    """
    class for building top rig structure
    """

    def __init__(self,
                 characterName='new',
                 scale=1.0,
                 mainCtrlAttachObj=''
                 ):
        """
        :param characterName: str, character name
        :param scale: float, general scale of the rig
        :return None
        """

        self.topGrp = cmds.group(n=characterName, em=1)
        # self.rigGrp = cmds.group(n=characterName + 'rig_grp', em=1, p=self.topGrp)
        # self.modelGrp = cmds.group(n=characterName + 'model_grp', em=1, p=self.topGrp)

        characterNameAttr = 'characterName'
        sceneObjectTypeAttr = 'sceneObjectType'

        for attr in [characterNameAttr, sceneObjectTypeAttr]:

            cmds.addAttr(self.topGrp, ln=attr, dt='string')

        cmds.setAttr(self.topGrp + '.' + characterNameAttr,
                     characterName, type='string', l=1)
        cmds.setAttr(self.topGrp + '.' + sceneObjectTypeAttr,
                     sceneObjectType, type='string', l=1)

        # make global control

        self.Master_Ctrl = control.Control(prefix='C_',
                                           rigPartName='Master',
                                           shape='crownCurve',
                                           scale=scale * 10.0,
                                           parent=self.topGrp,
                                           axis='z',
                                           lockChannels=['v'])

        self.Move_Ctrl = control.Control(prefix='C_',
                                         rigPartName='Move',
                                         shape='moveControl',
                                         scale=scale * 15.0,
                                         parent=self.Master_Ctrl.C,
                                         axis='z',
                                         lockChannels=['s', 'v'])
        # Z axis up rotate set
        # self._flattenGlobalCtrlShape(self.Master_Ctrl.C)
        # self._flattenGlobalCtrlShape(self.Move_Ctrl.C)

        for axis in ['y', 'z']:

            cmds.connectAttr(self.Master_Ctrl.C + '.sx', self.Master_Ctrl.C + '.s' + axis)
            cmds.setAttr(self.Master_Ctrl.C + '.s' + axis, k=0)

        cmds.aliasAttr('Global_Scale', self.Master_Ctrl.C + '.sx')

        # make more groups

        # self.jointGrp = cmds.group(n='joint_grp', em=1, p=Move_Ctrl.C)
        # self.modulesGrp = cmds.group(n='modules_grp', em=1, p=Move_Ctrl.C)

        # create a grp for objects are not influenced by rig moving
        # not moving
        self.dontTouchGrp = cmds.group(n='Dont_Touch_Grp', em=1, p=self.topGrp)
        # lock the inherits Transform attr
        cmds.setAttr(self.dontTouchGrp + '.it', 0, l=1)

        cmds.select(cl=1)

        # make main control
        # mainCtrl = control.Control(prefix='main', scale=scale*1, parent=Move_Ctrl.C, translateTo=mainCtrlAttachObj, lockChannels=['t', 'r', 's', 'v'])

        # self._adjustMainCtrlShape(mainCtrl, scale)

        #if cmds.objExists(mainCtrlAttachObj):
        #    cmds.parentConstraint(mainCtrlAttachObj, mainCtrl.Off, mo=1)

        #mainVisAts = ['modelVis', 'jointsVis']
        #mainDispAts = ['modelDisp', 'jointDisp']
        #mainObjList = [self.modelGrp, self.jointGrp]
        #mainObjVisDvList = [1, 0]

        # add rig visibility connections

        #for at, obj, dfVal in zip(mainVisAts, mainObjList, mainObjVisDvList):
        #    cmds.addAttr(mainCtrl.C, ln=at, at='enum', enumName='off:on', k=1, defaultValue=dfVal)
        #    cmds.setAttr(mainCtrl.C + '.' + at, channelBox=1)
        #    cmds.connectAttr(mainCtrl.C + '.' + at, obj + '.v')

        # add rig display type connections
        #for at, obj in zip(mainDispAts, mainObjList):
        #    cmds.addAttr(mainCtrl.C, ln=at, at='enum', enumName='normal:template:reference', k=1, defaultValue=2)
        #    cmds.setAttr(obj + '.ove', 1)
        #    cmds.connectAttr(mainCtrl.C + '.' + at, obj + '.ovdt')

    """
    def _adjustMainCtrlShape(self, ctrl, scale):

        # adjust shape of main control

        ctrlShapes = cmds.listRelatives(ctrl.C, s=1, type='nurbsCurve')

        # cluster()[1] will return the cluster handle name
        cls = cmds.cluster(ctrlShapes)[1]
        cmds.setAttr(cls + '.ry', 90)
        cmds.delete(ctrlShapes, ch=1)

        cmds.move(5 * scale, ctrl.Off, moveY=1, relative=True)
    """

    def _flattenGlobalCtrlShape(self, ctrlObject):

        # flatten ctrl object shape

        ctrlShapes = cmds.listRelatives(ctrlObject, s=1,
                                        type='nurbsCurve')

        cls = cmds.cluster(ctrlShapes)[1]
        cmds.setAttr(cls + '.rx', 90)
        cmds.delete(ctrlShapes, ch=1)


class Module():

    """class for building module rig structure"""

    def __init__(self,
                 prefix='L_',
                 rigPartName='',
                 baseObject=None
                 ):

        """
        :param prefix:str, prefix to name new objects
        :param baseObject:instance of base.module.Base() class
        :return None
        """
        self.topGrp = cmds.group(n=prefix + rigPartName + 'Module_Grp', em=1)
        self.dontTouchGrp = cmds.group(n=prefix + rigPartName + 'Dont_Touch_Grp',
                                       em=1, p=self.topGrp)

        cmds.hide(self.dontTouchGrp)

        cmds.setAttr(self.dontTouchGrp + '.it', 0, l=1)

        # query and add attribute
        if not cmds.attributeQuery('slaveJoint', node=self.topGrp, exists=1):
            cmds.addAttr(self.topGrp, longName='slaveJoint', at='message')

        if not cmds.attributeQuery(prefix + rigPartName + '_Jnt', node=self.topGrp, exists=1):
            cmds.addAttr(self.topGrp, longName=prefix + rigPartName + '_Jnt', at='message')

        # parent module
        if baseObject:

            cmds.parent(self.topGrp, baseObject.Master_Ctrl.C)

        cmds.select(cl=1)
