import maya.cmds as cmds
from ..base import control
from ..base import module
from ..rigLib import lib

reload(control)
reload(module)
reload(lib)


def createRig(vertexList,
              prefix='L_',
              rigPartName='',
              rigScale=1.0,
              addSliderCtrls=True,
              jointParent=''):

    cmds.select(cl=1)

    # create module
    rigModule = module.Module(prefix=prefix,
                              rigPartName=rigPartName)

    # create joint on each vertex
    jointList = lib.vertex2Joints(vertexList=vertexList,
                                  prefix=prefix,
                                  rigPartName=rigPartName,
                                  addSlaveAttr=True)

    # parent created joint to target joint
    if jointParent:
        for i in jointList:
            cmds.select(cl=1)
            cmds.parent(i, jointParent)
    cmds.select(cl=1)

    # add control for each joint
    jointCtrlList = []
    jointCtrlGrpList = []
    # create controls
    for i in xrange(len(jointList)):
        jointCtrl = control.Control(prefix=jointList[i],
                                    rigPartName='',
                                    scale=rigScale * 0.2,
                                    translateTo=jointList[i],
                                    rotateTo=jointList[i],
                                    shape='circleY')

        cmds.pointConstraint(jointCtrl.C, jointList[i], mo=0)
        cmds.orientConstraint(jointCtrl.C, jointList[i], mo=0)

        jointCtrlList.append(jointCtrl.C)
        jointCtrlGrpList.append(jointCtrl.Off)

    # connect the attribute
    for i in jointList:
        cmds.connectAttr(rigModule.topGrp + '.' + prefix + rigPartName + '_Jnt',
                         i + '.' + prefix + rigPartName, f=1)

    # slider controls
    slideCtrlList = []
    slideCtrlGrpList = []

    if addSliderCtrls:
        for i in xrange(len(jointList)):
            slideCtrl = control.Control(prefix=prefix,
                                        rigPartName=rigPartName + '_Jnt_' + str(i) + '_SLD',
                                        scale=rigScale * 0.5,
                                        shape='planeSliderControl',
                                        lockChannels=['ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])

            slideCtrlList.append(slideCtrl.C)
            slideCtrlGrpList.append(slideCtrl.Off)

    # cleanHierarchy
    for i in jointCtrlGrpList:
        cmds.parent(i, rigModule.topGrp)

    if addSliderCtrls:
        rigModuleSliderGrp = cmds.group(n=prefix + rigPartName + '_SLD_Grp', em=1)
        for i in slideCtrlGrpList:
            cmds.parent(i, rigModuleSliderGrp)

        cmds.parent(rigModuleSliderGrp, rigModule.topGrp)

        # set default keyframe
        cmds.setDrivenKeyframe()

