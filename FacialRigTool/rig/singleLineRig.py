import maya.cmds as cmds
from ..base import module
from ..base import control
from ..rigLib import lib

reload(lib)
reload(module)
reload(control)


def createRig(selectedLines,
              prefix='L_',
              rigPartName='',
              numJnt = 3,
              rigScale=1.0,
              addSliderCtrls=True,
              jointParent=''):

    cmds.select(cl=1)

    # create module
    rigModule = module.Module(prefix=prefix,
                              rigPartName=rigPartName)

    # create line
    targetLine = lib.createCurve(edgeList=selectedLines)
    cmds.xform(targetLine, cp=1)

    # create joint along the curve
    jointList = lib.joint2Curve(prefix=prefix,
                                partName=rigPartName,
                                curve=targetLine,
                                numJnt=numJnt)
    # parent created joint to target joint
    if jointParent:
        for i in jointList:
            cmds.select(cl=1)
            cmds.parent(i, jointParent)

    cmds.select(cl=1)

    # create controller for each joint
    jointCtrlList = []
    jointCtrlGrpList = []
    for i in jointList:
        jointCtrl = control.Control(prefix=i,
                                    rigPartName='',
                                    scale=rigScale * 0.2,
                                    translateTo=i,
                                    rotateTo=i,
                                    shape='circleY')

        cmds.pointConstraint(jointCtrl.C, i, mo=0)
        cmds.orientConstraint(jointCtrl.C, i, mo=0)

        jointCtrlList.append(jointCtrl.C)
        jointCtrlGrpList.append(jointCtrl.Off)

    # create module main control
    mainCtrl = control.Control(prefix=prefix,
                               rigPartName=rigPartName,
                               scale=rigScale,
                               translateTo=targetLine[0],
                               rotateTo=jointList[0],
                               shape='circleY')

    # connect the attribute
    for i in jointList:
        cmds.connectAttr(rigModule.topGrp + '.' + prefix + rigPartName + '_Jnt',
                         i + '.' + prefix + rigPartName, f=1)

    # for each joint create the slide control
    slideCtrlList = []
    slideCtrlGrpList = []
    if addSliderCtrls:
        for i in xrange(len(jointList)):
            sliderCtrl = control.Control(prefix=prefix,
                                         rigPartName=rigPartName + '_Jnt_' + str(i) + '_SLD',
                                         scale=rigScale * 0.5,
                                         shape='verticalSliderControl',
                                         lockChannels=['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])

            slideCtrlList.append(sliderCtrl.C)
            slideCtrlGrpList.append(sliderCtrl.Off)

        # add main slider control
        mainSliderCtrl = control.Control(prefix=prefix,
                                         rigPartName=rigPartName + '_Jnt_Main_SLD',
                                         scale=rigScale,
                                         shape='verticalSliderControl',
                                         lockChannels=['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])

    # clean hierarchy
    cmds.parent(targetLine, rigModule.dontTouchGrp)

    for i in jointCtrlGrpList:
        cmds.parent(i, mainCtrl.C)

    cmds.parent(mainCtrl.Off, rigModule.topGrp)

    if addSliderCtrls:
        rigModuleSliderGrp = cmds.group(n=prefix + rigPartName + '_SLD_Grp', em=1)
        for i in slideCtrlGrpList:
            cmds.parent(i, rigModuleSliderGrp)

        cmds.parent(mainSliderCtrl.Off, rigModuleSliderGrp)

        cmds.parent(rigModuleSliderGrp, rigModule.topGrp)

        # set default keyframe

        cmds.setDrivenKeyframe(mainCtrl.C + '.translateZ', cd=mainSliderCtrl.C + '.translateZ')

        for i in xrange(len(jointList)):
            cmds.setDrivenKeyframe(jointCtrlList[i] + '.translateZ', cd=slideCtrlList[i] + '.translateZ')

    cmds.select(cl=1)



