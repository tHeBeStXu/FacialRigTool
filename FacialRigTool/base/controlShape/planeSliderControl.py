import maya.cmds as cmds
from ...utils import name
reload(name)


def createShape(prefix=''):
    """
    Create a vertical slider control with proper name
    :param prefix: str, prefixName of the control
    :return: list(str), [sliderPath, mainCtrlBox]
    """
    # create slider
    ctrl = cmds.circle(radius=0.15, nr=(0, 1, 0), n=prefix + '_Ctrl')[0]

    cmds.transformLimits(ctrl, tx=(-1, 1), ty=(0, 0), tz=(-1, 1), etx=(1, 1), ety=(1, 1), etz=(1, 1))

    ctrlBox = cmds.curve(d=1, p=[(-1, 0, 1),
                                 (1, 0, 1),
                                 (1, 0, -1),
                                 (-1, 0, -1),
                                 (-1, 0, 1)], k=[0, 1, 2, 3, 4], n=prefix + '_Path')
    parentCrvShape = cmds.listRelatives(ctrlBox, s=1)
    cmds.setAttr(parentCrvShape[0] + '.template', 1)
    cmds.parent(ctrl, ctrlBox)

    cmds.select(cl=1)

    # create text
    textCrv = cmds.textCurves(n=prefix + '_text', font='Times-Roman', t=name.removeSuffix(prefix))[0]

    cmds.setAttr(textCrv + '.overrideEnabled', 1)
    cmds.setAttr(textCrv + '.overrideDisplayType', 2)

    cmds.setAttr(textCrv + '.s', 0.5, 0.5, 0.5)

    cmds.setAttr(textCrv + '.rx', 90)
    cmds.makeIdentity(textCrv, apply=1, t=0, r=1, s=1)

    textHeight = cmds.getAttr(textCrv + '.boundingBoxMaxZ')
    textWidth = cmds.getAttr(textCrv + '.boundingBoxMaxX')

    cmds.setAttr(textCrv + '.tx', (0 - (textWidth/2)))
    cmds.setAttr(textCrv + '.tz', 1.5)

    betterWidth = 1.15
    if textWidth/2 >= 1.15:
        betterWidth = textWidth/2

    # create Main CtrlBox
    mainCtrlBox = cmds.curve(d=1, p=[((0 - (betterWidth + 0.2)), 0, (1.85 + textHeight)),
                                     ((betterWidth + 0.2), 0, (1.85 + textHeight)),
                                     ((betterWidth + 0.2), 0, -1.35),
                                     ((0 - (betterWidth + 0.2)), 0, -1.35),
                                     ((0 - (betterWidth + 0.2)), 0, (1.85 + textHeight))],
                             k=[0, 1, 2, 3, 4], n=prefix + '_ctrlBox')

    parentCrvShape1 = cmds.listRelatives(mainCtrlBox, s=1)
    cmds.setAttr(parentCrvShape1[0] + '.template', 1)

    # clean hierarchy
    cmds.parent(ctrlBox, mainCtrlBox)
    cmds.parent(textCrv, mainCtrlBox)

    cmds.makeIdentity(mainCtrlBox, apply=1, t=0, r=1, s=1)

    cmds.select(cl=1)

    return [ctrlBox, mainCtrlBox]
