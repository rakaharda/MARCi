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
# Finger bones enumerate like 'Mid1.L', 'Mid2.L', 'Mid3.L'
FINGERS = ["Thumb", "Index", "Mid", "Ring", "Pinky"]
# Toe bones enumerate like 'SmallToe1', 'SmallToe1_2'
TOES = ["BigToe", "SmallToe1", "SmallToe2", "SmallToe3", "SmallToe4"]
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
FOOT_ROCKER = "Foot.Rocker"
FOOT_BONES = [FOOT, METATARSALS, TOE]
SPINE_BONES = ["hip", "pelvis", "abdomenLower", "abdomenUpper", 
               "chestLower", "chestUpper", "neckLower", "neckUpper", "head"]
PECTORAL = "Pectoral"
COLLAR = "Collar"