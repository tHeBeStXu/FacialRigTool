import maya.cmds as cmds
from ..rigLib import lib
from ..utils import name
from ..base import control
from ..base import module

reload(lib)
reload(name)
reload(control)
reload(module)


def createRig(upperVertexList,
              lowerVertexList,
              prefix='L_',
              rigPartName='EyeLid',
              rigScale=1.0,
              eyeJoint='',
              numCtrl=5,
              ):

    if numCtrl < 3:
        cmds.error('numCtrl must bigger than 3!')
        return
    cmds.select(cl=1)
    # create eyeLid Module
    eyeLidRigModule = module.Module(prefix=prefix, rigPartName=rigPartName)

    # create upper eyelid Module
    upperLidRigModule = module.Module(prefix=prefix, rigPartName='upper_' + rigPartName)

    #####################
    # Upper Eyelid Part #
    #####################

    # create eyelid joint for each vertex
    upperEyeLidJointList = lib.vertex2Joints(vertexList=upperVertexList, prefix=prefix,
                                             rigPartName='upper_' + rigPartName, radius=0.05)

    # connect attr
    for joint in upperEyeLidJointList:
        if cmds.attributeQuery('slaveJoint', node=joint, exists=1):
            cmds.connectAttr(upperLidRigModule.topGrp + '.slaveJoint', joint + '.slaveJoint', f=1)

    # create eyelid parent joint for each eyelid joint
    upperEyeLidParentJntList = []
    for i in upperEyeLidJointList:
        cmds.select(cl=1)

        parentJoint = cmds.joint(n=i + '_Parent', radius=0.05)

        cmds.delete(cmds.pointConstraint(eyeJoint, parentJoint, mo=0))

        cmds.delete(cmds.aimConstraint(i, parentJoint, aimVector=(1, 0, 0), upVector=(0, -1, 0),
                                       worldUpType='scene', weight=1, offset=(0, 0, 0), mo=0))
        cmds.parent(i, parentJoint)

        cmds.joint(i, e=1, oj='none', ch=1, zso=1)

        cmds.makeIdentity(parentJoint, apply=1, t=1, r=1, s=1)

        upperEyeLidParentJntList.append(parentJoint)

    cmds.select(cl=1)

    upperEyelidLocList = []
    # create locator for each eyelid joint
    for i in upperEyeLidParentJntList:

        cmds.select(cl=1)

        eyelidJoint = cmds.listRelatives(i, c=1, type='joint', shapes=0)[0]

        ikHandle = cmds.ikHandle(n=eyelidJoint + '_IK', sj=i, ee=eyelidJoint, sol='ikSCsolver')

        eyelidLoc = cmds.spaceLocator(n=eyelidJoint + '_LOC')[0]

        cmds.delete(cmds.parentConstraint(eyelidJoint, eyelidLoc, mo=0))

        cmds.select(cl=1)

        cmds.setAttr(ikHandle[0] + '.v', 0)
        LOCShape = cmds.listRelatives(eyelidLoc, p=0, c=1, s=1)[0]
        cmds.setAttr(LOCShape + '.localScaleX', 0.1)
        cmds.setAttr(LOCShape + '.localScaleY', 0.1)
        cmds.setAttr(LOCShape + '.localScaleZ', 0.1)

        cmds.parent(ikHandle[0], eyelidLoc)

        upperEyelidLocList.append(eyelidLoc)

    cmds.select(cl=1)

    # create high definition curve
    lowerPosList = []
    for i in upperEyelidLocList:
        pos = cmds.xform(i, q=1, ws=1, t=1)
        lowerPosList.append(tuple(pos))

    upperKList = []
    for i in xrange(len(lowerPosList)):
        upperKList.append(i)

    upperHighDefCurve = cmds.curve(n=prefix + 'upper_' +rigPartName + '_HD_Crv', p=lowerPosList, k=upperKList, d=1)
    upperLowDefCurve = cmds.duplicate(upperHighDefCurve, n=prefix + 'lower_' + rigPartName + '_LD_Crv')

    upperHighDefCurveShape = cmds.listRelatives(upperHighDefCurve, p=0, c=0, s=1, path=1)[0]
    cmds.select(cl=1)

    # make each locator attach to the curve

    for i in upperEyelidLocList:
        pos = cmds.xform(i, q=1, ws=1, t=1)
        uParam = lib.getUParam(pos, upperHighDefCurveShape)

        PCI = cmds.createNode('pointOnCurveInfo', n=name.removeSuffix(i) + '_PCI')

        cmds.connectAttr(upperHighDefCurveShape + '.worldSpace', PCI + '.inputCurve', f=1)

        cmds.setAttr(PCI + '.parameter', uParam)

        cmds.connectAttr(PCI + '.position', i + '.t')

        cmds.select(cl=1)

    # make HD curve deformed by LD curve
    upperLowDefCurve = cmds.rebuildCurve(upperLowDefCurve, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=3, d=3)
    cmds.select(cl=1)

    upperWireDefomer = cmds.wire(upperHighDefCurve, gw=0, en=1, ce=0, li=0, w=upperLowDefCurve)
    upperWireTransNode = cmds.listConnections(upperWireDefomer[0] + '.baseWire[0]', source=1, destination=0)

    cmds.select(cl=1)

    # create control joint and controls for the LD curve
    upperControlJointList = []

    eachADD = 1.0 / (numCtrl - 1)

    for i in xrange(numCtrl):
        newJnt = cmds.joint(n=prefix + 'upper_' + rigPartName + '_CtrlJnt_' + str(i), radius=0.1)
        cmds.select(cl=1)
        motionPath = cmds.pathAnimation(upperLowDefCurve, newJnt, n=prefix + rigPartName + '_MP_' + str(i), fractionMode=1,
                                        follow=1, followAxis='x', upAxis='z', worldUpType='scene',
                                        inverseUp=0, inverseFront=0, bank=0)

        cmds.cutKey(motionPath + '.u', time=())

        cmds.setAttr(motionPath + '.uValue', eachADD * float(i))

        for attr in ['t', 'r']:
            for axis in ['x', 'y', 'z']:
                cmds.delete(newJnt + '.%s%s' % (attr, axis), icn=1)

        cmds.delete(motionPath)
        cmds.select(cl=1)

        upperControlJointList.append(newJnt)

        cmds.setAttr(newJnt + '.r', 0, 0, 0)
        cmds.select(cl=1)

    # bind LD curve by control joint
    cmds.skinCluster(upperControlJointList[:], upperLowDefCurve)
    cmds.select(cl=1)

    upperJntCtrlGrpList = []
    for i in xrange(len(upperControlJointList)):
        ctrl = control.Control(prefix=upperControlJointList[i],
                               rigPartName='',
                               scale=rigScale,
                               shape='circleY',
                               translateTo=upperControlJointList[i],
                               rotateTo=upperControlJointList[i])

        cmds.pointConstraint(ctrl.C, upperControlJointList[i], mo=0)
        cmds.orientConstraint(ctrl.C, upperControlJointList[i], mo=0)

        upperJntCtrlGrpList.append(ctrl.Off)

    cmds.select(cl=1)

    # clean hierarchy
    upperParentJntGrp = cmds.group(n=prefix + 'upper_' + rigPartName + '_skinJnt_Grp', em=1)
    upperLocGrp = cmds.group(n=prefix + 'upper_' + rigPartName + '_LOC_Grp', em=1)
    upperCurveGrp = cmds.group(n=prefix + 'upper_' + rigPartName + '_Crv_Grp', em=1)
    upperCtrlJntGrp = cmds.group(n=prefix + 'upper_' + rigPartName + '_ctrlJnt_Grp', em=1)
    upperCtrlGrp = cmds.group(n=prefix + 'upper_' + rigPartName + '_CtrlGrp', em=1)

    for i in upperEyeLidParentJntList:
        cmds.parent(i, upperParentJntGrp)

    for i in upperEyelidLocList:
        cmds.parent(i, upperLocGrp)

    cmds.parent(upperLowDefCurve, upperCurveGrp)
    cmds.parent(upperHighDefCurve, upperCurveGrp)
    cmds.parent(upperWireTransNode, upperCurveGrp)

    for i in upperControlJointList:
        cmds.parent(i, upperCtrlJntGrp)

    for i in upperJntCtrlGrpList:
        cmds.parent(i, upperCtrlGrp)

    cmds.setAttr(upperLocGrp + '.v', 0)
    cmds.setAttr(upperCurveGrp + '.v', 0)
    cmds.setAttr(upperCtrlJntGrp + '.v', 0)

    cmds.parent(upperParentJntGrp, upperLidRigModule.topGrp)
    cmds.parent(upperLocGrp, upperLidRigModule.topGrp)
    cmds.parent(upperCurveGrp, upperLidRigModule.topGrp)
    cmds.parent(upperCtrlJntGrp, upperLidRigModule.topGrp)
    cmds.parent(upperCtrlGrp, upperLidRigModule.topGrp)

###################################################################################################################

    #####################
    # Lower Eyelid Part #
    #####################
    
    # create lower eyelid Module
    lowerLidRigModule = module.Module(prefix=prefix, rigPartName='lower_' + rigPartName)

    # create eyelid joint for each vertex
    lowerEyeLidJointList = lib.vertex2Joints(vertexList=lowerVertexList, prefix=prefix,
                                             rigPartName='lower_' + rigPartName, radius=0.05)

    # connect attr
    for joint in lowerEyeLidJointList:
        if cmds.attributeQuery('slaveJoint', node=joint, exists=1):
            cmds.connectAttr(lowerLidRigModule.topGrp + '.slaveJoint', joint + '.slaveJoint', f=1)

    # create eyelid parent joint for each eyelid joint
    lowerEyeLidParentJntList = []
    for i in lowerEyeLidJointList:
        cmds.select(cl=1)

        parentJoint = cmds.joint(n=i + '_Parent', radius=0.05)

        cmds.delete(cmds.pointConstraint(eyeJoint, parentJoint, mo=0))

        cmds.delete(cmds.aimConstraint(i, parentJoint, aimVector=(1, 0, 0), upVector=(0, -1, 0),
                                       worldUpType='scene', weight=1, offset=(0, 0, 0), mo=0))
        cmds.parent(i, parentJoint)

        cmds.joint(i, e=1, oj='none', ch=1, zso=1)

        cmds.makeIdentity(parentJoint, apply=1, t=1, r=1, s=1)

        lowerEyeLidParentJntList.append(parentJoint)

    cmds.select(cl=1)

    lowerEyelidLocList = []
    # create locator for each eyelid joint
    for i in lowerEyeLidParentJntList:
        cmds.select(cl=1)

        eyelidJoint = cmds.listRelatives(i, c=1, type='joint', shapes=0)[0]

        ikHandle = cmds.ikHandle(n=eyelidJoint + '_IK', sj=i, ee=eyelidJoint, sol='ikSCsolver')

        eyelidLoc = cmds.spaceLocator(n=eyelidJoint + '_LOC')[0]

        cmds.delete(cmds.parentConstraint(eyelidJoint, eyelidLoc, mo=0))

        cmds.select(cl=1)

        cmds.setAttr(ikHandle[0] + '.v', 0)
        LOCShape = cmds.listRelatives(eyelidLoc, p=0, c=1, s=1)[0]
        cmds.setAttr(LOCShape + '.localScaleX', 0.1)
        cmds.setAttr(LOCShape + '.localScaleY', 0.1)
        cmds.setAttr(LOCShape + '.localScaleZ', 0.1)

        cmds.parent(ikHandle[0], eyelidLoc)

        lowerEyelidLocList.append(eyelidLoc)

    cmds.select(cl=1)

    # create high definition curve
    lowerPosList = []
    for i in lowerEyelidLocList:
        pos = cmds.xform(i, q=1, ws=1, t=1)
        lowerPosList.append(tuple(pos))

    lowerKList = []
    for i in xrange(len(lowerPosList)):
        lowerKList.append(i)

    lowerHighDefCurve = cmds.curve(n=prefix + 'lower_' + rigPartName + '_HD_Crv', p=lowerPosList, k=lowerKList, d=1)
    lowerLowDefCurve = cmds.duplicate(lowerHighDefCurve, n=prefix + 'lower_' + rigPartName + '_LD_Crv')

    lowerHighDefCurveShape = cmds.listRelatives(lowerHighDefCurve, p=0, c=0, s=1, path=1)[0]
    cmds.select(cl=1)

    # make each locator attach to the curve

    for i in lowerEyelidLocList:
        pos = cmds.xform(i, q=1, ws=1, t=1)
        uParam = lib.getUParam(pos, lowerHighDefCurveShape)

        PCI = cmds.createNode('pointOnCurveInfo', n=name.removeSuffix(i) + '_PCI')

        cmds.connectAttr(lowerHighDefCurveShape + '.worldSpace', PCI + '.inputCurve', f=1)

        cmds.setAttr(PCI + '.parameter', uParam)

        cmds.connectAttr(PCI + '.position', i + '.t')

        cmds.select(cl=1)

    # make HD curve deformed by LD curve
    lowerLowDefCurve = cmds.rebuildCurve(lowerLowDefCurve, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=3, d=3)
    cmds.select(cl=1)

    lowerWireDefomer = cmds.wire(lowerHighDefCurve, gw=0, en=1, ce=0, li=0, w=lowerLowDefCurve)
    lowerWireTransNode = cmds.listConnections(lowerWireDefomer[0] + '.baseWire[0]', source=1, destination=0)

    cmds.select(cl=1)

    # create control joint and controls for the LD curve
    lowerControlJointList = []

    eachADD = 1.0 / (numCtrl - 1)

    for i in xrange(numCtrl - 2):
        newJnt = cmds.joint(n=prefix + 'lower_' + rigPartName + '_CtrlJnt_' + str(i + 1), radius=0.1)
        cmds.select(cl=1)
        motionPath = cmds.pathAnimation(lowerLowDefCurve, newJnt, n=prefix + rigPartName + '_MP_' + str(i + 1),
                                        fractionMode=1,
                                        follow=1, followAxis='x', upAxis='z', worldUpType='scene',
                                        inverseUp=0, inverseFront=0, bank=0)

        cmds.cutKey(motionPath + '.u', time=())

        cmds.setAttr(motionPath + '.uValue', eachADD * float(i + 1))

        for attr in ['t', 'r']:
            for axis in ['x', 'y', 'z']:
                cmds.delete(newJnt + '.%s%s' % (attr, axis), icn=1)

        cmds.delete(motionPath)
        cmds.select(cl=1)

        lowerControlJointList.append(newJnt)

        cmds.setAttr(newJnt + '.r', 0, 0, 0)
        cmds.select(cl=1)

    lowerControlJointList.insert(0, upperControlJointList[0])
    lowerControlJointList.append(upperControlJointList[-1])

    # bind LD curve by control joint
    cmds.skinCluster(lowerControlJointList[:], lowerLowDefCurve)
    cmds.select(cl=1)

    lowerJntCtrlGrpList = []
    for i in xrange(len(lowerControlJointList[1:-1])):
        ctrl = control.Control(prefix=lowerControlJointList[i+1],
                               rigPartName='',
                               scale=rigScale,
                               shape='circleY',
                               translateTo=lowerControlJointList[i+1],
                               rotateTo=lowerControlJointList[i+1])

        cmds.pointConstraint(ctrl.C, lowerControlJointList[i+1], mo=0)
        cmds.orientConstraint(ctrl.C, lowerControlJointList[i+1], mo=0)

        lowerJntCtrlGrpList.append(ctrl.Off)

    cmds.select(cl=1)

    # clean hierarchy
    lowerParentJntGrp = cmds.group(n=prefix + 'lower_' + rigPartName + '_skinJnt_Grp', em=1)
    lowerLocGrp = cmds.group(n=prefix + 'lower_' + rigPartName + '_LOC_Grp', em=1)
    lowerCurveGrp = cmds.group(n=prefix + 'lower_' + rigPartName + '_Crv_Grp', em=1)
    lowerCtrlJntGrp = cmds.group(n=prefix + 'lower_' + rigPartName + '_ctrlJnt_Grp', em=1)
    lowerCtrlGrp = cmds.group(n=prefix + 'lower_' + rigPartName + '_CtrlGrp', em=1)

    for i in lowerEyeLidParentJntList:
        cmds.parent(i, lowerParentJntGrp)

    for i in lowerEyelidLocList:
        cmds.parent(i, lowerLocGrp)

    cmds.parent(lowerLowDefCurve, lowerCurveGrp)
    cmds.parent(lowerHighDefCurve, lowerCurveGrp)
    cmds.parent(lowerWireTransNode, lowerCurveGrp)

    for i in lowerControlJointList:
        cmds.parent(i, lowerCtrlJntGrp)

    for i in lowerJntCtrlGrpList:
        cmds.parent(i, lowerCtrlGrp)

    cmds.setAttr(lowerLocGrp + '.v', 0)
    cmds.setAttr(lowerCurveGrp + '.v', 0)
    cmds.setAttr(lowerCtrlJntGrp + '.v', 0)

    cmds.parent(lowerParentJntGrp, lowerLidRigModule.topGrp)
    cmds.parent(lowerLocGrp, lowerLidRigModule.topGrp)
    cmds.parent(lowerCurveGrp, lowerLidRigModule.topGrp)
    cmds.parent(lowerCtrlJntGrp, lowerLidRigModule.topGrp)
    cmds.parent(lowerCtrlGrp, lowerLidRigModule.topGrp)

    # final
    cmds.parent(upperLidRigModule.topGrp, eyeLidRigModule.topGrp)
    cmds.parent(lowerLidRigModule.topGrp, eyeLidRigModule.topGrp)
