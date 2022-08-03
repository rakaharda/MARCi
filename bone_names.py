class BoneGroups:
    ctrl = 'Controllers'
    poles = 'Poles'
    fk = 'Forward Kinematics'
    sk_ctrl = 'Shapekey Controllers'
    fk_wo_ik = 'Forward Kinematics (w/o IK)'

def left_bone(bone = ""):
    return bone + ".L"

def right_bone(bone  = ""):
    return bone + ".R"

def mch_bone(bone):
    return bone + ".MCH"

def ctrl_bone(bone):
    return bone + ".Controller"


SIDES = [left_bone, right_bone]
FINGERS = ["Thumb", "Index", "Mid", "Ring", "Pinky"]
ARM_BONES = ["ShldrBend", "ShldrTwist", "ForearmBend", "ForearmTwist"]
LEG_BONES = ["ThighBend", "ThighTwist", "Shin"]
HAND_CTRL = "Hand.controller"
LEG_CONTROLLER = "Leg.controller"
ARM_POLE = "Arm.pole"
LEG_POLE = "Leg.pole"
HAND = "Hand"
FOOT = "Foot"
METATARSALS = "Metatarsals"
TOE = "Toe"
