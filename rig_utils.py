import enum
from logging import exception
from re import A
import this
import bpy
from mathutils import Vector
import mathutils
import math
from armature_layers import armature_layers as al

fingers_names = ["Thumb", "Index", "Mid", "Ring", "Pinky"]
lip_bones = ["lip", "lip.L", "lip.001.L", "lip.002.L", "lip.003.L",
             "lip.004.L", "lip.005.L", "lip.R", "lip.001.R", "lip.002.R",
             "lip.003.R", "lip.004.R", "lip.005.R", "lip.B", "lip.B.001.L",
             "lip.B.001.R", "lip.B.002.L", "lip.B.002.R", "lip.B.003.L", "lip.B.003.R",
             "lip.B.004.L", "lip.B.004.R"]
arm_bones = ["ShldrBend", "ShldrTwist", "ForearmBend", "ForearmTwist"]
leg_bones = ["ThighBend", "ThighTwist", "Shin"]
hand_controller_name = "Hand.controller"
leg_controller_name = "Leg.controller"
arm_pole_name = "Arm.pole"
leg_pole_name = "Leg.pole"
hand_bone_name = "Hand"
foot = "Foot"
metatarsals = "Metatarsals"
toe = "Toe"

class BoneGroups():
    ctrl = 'Controllers'
    poles = 'Poles'
    fk = 'Forward Kinematics'
    sk_ctrl = 'Shapekey Controllers'
    fk_wo_ik = 'Forward Kinematics (w/o IK)'

def deselect_all():
    """Deselects all bones in current mode"""
    
    if bpy.context.mode == 'EDIT_ARMATURE':
        bpy.ops.armature.select_all(action='DESELECT')
    elif bpy.context.mode == 'POSE':
        bpy.ops.pose.select_all(action='DESELECT')

def objectmode():
    """Switches to object mode if not in it"""
    if bpy.context.mode == "POSE":
        bpy.ops.object.posemode_toggle()
    elif bpy.context.mode == "EDIT_ARMATURE":
        bpy.ops.object.editmode_toggle()


def posemode() -> None:
    """Switches to pose mode if not in it"""

    if bpy.context.mode != "POSE":
        bpy.ops.object.posemode_toggle()


def editmode():
    """Switches to edit mode if not in it"""

    if bpy.context.mode != "EDIT_ARMATURE":
        bpy.ops.object.editmode_toggle()


def select_bone(armature, bone_name, multiple=False, head = True, tail = True):
    """Selects given bone"""

    if not multiple:
        deselect_all()
    if bpy.context.mode == "POSE":
        bone = bpy.context.object.pose.bones[bone_name]
        armature.bones.active = bone.bone
    if bpy.context.mode == "EDIT_ARMATURE":
        armature.edit_bones.active = armature.edit_bones[bone_name]
        armature.edit_bones[bone_name].select = True
        armature.edit_bones[bone_name].select_head = head
        armature.edit_bones[bone_name].select_tail = tail


def extrude_bone(armature, from_bone, vec, name, parent="Root", orient_type="GLOBAL", from_head=False):
    """Extrudes bone from selected bone in direction of given vector,
    renames it, turns off deform, disconnects
    and parents to give bone (Root bone by default),
    expecting that there is no bone with name .001 already exist"""

    editmode()
    deselect_all()
    if not from_head:
        armature.edit_bones[from_bone].select_tail = True
    else:
        armature.edit_bones[from_bone].select_head = True
    bpy.ops.armature.extrude_move(ARMATURE_OT_extrude={"forked": False},
                                  TRANSFORM_OT_translate={"value": vec,
                                  "orient_type": orient_type})
    armature.edit_bones[from_bone + ".001"].name = name
    armature.edit_bones[name].use_deform = False
    armature.edit_bones[name].use_connect = False
    if parent is not None:
        armature.edit_bones[name].parent = armature.edit_bones[parent]
    else:
        armature.edit_bones[name].parent = None
    bpy.ops.object.editmode_toggle()


def duplicate_bone(armature, bone_name, name=None, parent=None, length=None):
    editmode()
    print(bone_name)
    select_bone(armature, bone_name)
    bpy.ops.armature.duplicate()
    bone = bpy.context.selected_bones[0]
    
    if parent is not None:
        bone.parent = armature.edit_bones[parent]
    if name is not None:
        bone.name = name
    if length is not None:
        bone.length = length

def add_bone(bone_name):
    editmode()
    bpy.ops.armature.bone_primitive_add(name=bone_name)


def move_bone(armature, name, position):
    """Moves bone in direction of given vector"""

    editmode()
    armature.edit_bones[name].translate(position)
    bpy.ops.object.editmode_toggle()


def move_to_bone(armature, bone_to_move_name, bone_tail_name, src_head = False, dst_head = False):
    """Moves bone head/tail to tail/head of other bone"""

    editmode()
    vector = armature.edit_bones[bone_to_move_name].vector
    if dst_head:
        vector2 = armature.edit_bones[bone_tail_name].head
    else:
        vector2 = armature.edit_bones[bone_tail_name].tail
    if src_head:
        armature.edit_bones[bone_to_move_name].head = vector2
        armature.edit_bones[bone_to_move_name].tail = vector2 - vector
    else:
        armature.edit_bones[bone_to_move_name].tail = vector2 + vector
        armature.edit_bones[bone_to_move_name].head = vector2
        
    bpy.ops.object.editmode_toggle()


def add_ik_modifier(rig, bone_name, chain_length=0,
                    target_name=None, pole_name=None, pole_angle=0):
    """Adds IK modifier to bone"""

    posemode()
    bone = bpy.context.object.pose.bones[bone_name]
    select_bone(rig.data, bone_name)
    bpy.ops.pose.constraint_add(type='IK')
    constraint = bone.constraints[-1]
    constraint.chain_count = chain_length
    if target_name is not None:
        constraint.target = rig
        constraint.subtarget = target_name
    if pole_name is not None:
        constraint.pole_target = rig
        constraint.pole_subtarget = pole_name
    constraint.pole_angle = math.radians(pole_angle)
    bpy.ops.object.posemode_toggle()

def remove_constraint(rig, bone_name, constraint):
    posemode()
    bone = rig.pose.bones[bone_name]
    try:
        bone.constraints.remove(bone.constraints[constraint])
    except KeyError:
        print(f"Constraint {constraint} in bone {bone_name} not found")

def add_limit_loc_constraint(armature, bone_name, 
                             min_x=None, min_y=None, min_z=None,
                             max_x=None, max_y=None, max_z=None):
    """Adds Limit Location Constraint to a bone
    and sets it to local and to affect transform"""

    posemode()
    bone = bpy.context.object.pose.bones[bone_name]
    select_bone(armature, bone_name)
    bpy.ops.pose.constraint_add(type='LIMIT_LOCATION')
    constraint = bone.constraints[-1]
    constraint.owner_space = 'LOCAL'
    constraint.use_transform_limit = True
    if min_x is not None:
        constraint.use_min_x = True
        constraint.min_x = min_x
    if min_y is not None:
        constraint.use_min_y = True
        constraint.min_y = min_y
    if min_z is not None:
        constraint.use_min_z = True
        constraint.min_z = min_z
    if max_x is not None:
        constraint.use_max_x = True
        constraint.max_x = max_x
    if max_y is not None:
        constraint.use_max_y = True
        constraint.max_y = max_y
    if max_z is not None:
        constraint.use_max_z = True
        constraint.max_z = max_z


def add_limit_rotation_constraint(armature, bone_name, axis="xyz",
                                  min_x=0, min_y=0, min_z=0,
                                  max_x=0, max_y=0, max_z=0,
                                  affect_transform=True):
    """Adds Limit Rotation constraint to the bone in local space"""

    posemode()
    bone = bpy.context.object.pose.bones[bone_name]
    select_bone(armature, bone_name)
    bpy.ops.pose.constraint_add(type='LIMIT_ROTATION')
    constraint = bone.constraints[-1]
    constraint.use_limit_x = axis.lower().__contains__("x")
    constraint.min_x = math.radians(min_x)
    constraint.max_x = math.radians(max_x)
    constraint.use_limit_y = axis.lower().__contains__("y")
    constraint.min_y = math.radians(min_y)
    constraint.max_y = math.radians(max_y)
    constraint.use_limit_z = axis.lower().__contains__("z")
    constraint.min_z = math.radians(min_z)
    constraint.max_z = math.radians(max_z)
    constraint.use_transform_limit = affect_transform
    constraint.owner_space = 'LOCAL'
    return constraint


def add_copy_transforms_constraint(rig, bone_name, subtarget, influence=1.0):
    """Adds Copy Transforms modifier to the bone"""

    posemode()
    bone = bpy.context.object.pose.bones[bone_name]
    select_bone(rig.data, bone_name)
    bpy.ops.pose.constraint_add(type='COPY_TRANSFORMS')
    bone.constraints[-1].target = rig
    bone.constraints[-1].subtarget = subtarget
    bone.constraints[-1].influence = influence


def add_damped_track_modifier(rig, bone_name, subtarget):
    """Adds Damped Track modifier to the bone"""

    posemode()
    bone = bpy.context.object.pose.bones[bone_name]
    select_bone(rig.data, bone_name)
    bpy.ops.pose.constraint_add(type='DAMPED_TRACK')
    constraint = bone.constraints[-1]
    constraint.target = rig
    constraint.subtarget = subtarget


def add_locked_track_constraint(rig, bone_name, subtarget, head_tail = 0.0, track_axis = 'TRACK_Y', lock_axis = 'LOCK_Z'):
    """Adds Locked Track constraint to the bone
       Track axes - TRACK_X, TRACK_NEGATIVE_X, TRACK_Y, TRACK_NEGATIVE_Y, TRACK_Z, TRACK_NEGATIVE_Z
       Locked axes - LOCK_X, LOCK_Y, LOCK_Z"""

    posemode()
    bone = bpy.context.object.pose.bones[bone_name]
    select_bone(rig.data, bone_name)
    bpy.ops.pose.constraint_add(type='LOCKED_TRACK')
    constraint = bone.constraints[-1]
    constraint.target = rig
    constraint.subtarget = subtarget
    constraint.head_tail = head_tail
    constraint.track_axis = track_axis
    constraint.lock_axis = lock_axis

def constraint_ik_rotation(armature, bone_name, x_axis = True, y_axis = False, z_axis = True):
    """Constraints rotation of bone"""

    posemode()
    deselect_all()
    bone = bpy.context.object.pose.bones[bone_name]
    select_bone(armature, bone_name)
    bone.lock_ik_x = x_axis
    bone.lock_ik_y = y_axis
    bone.lock_ik_z = z_axis
    bpy.ops.object.posemode_toggle()

def add_copy_rotation_constraint(rig, bone_name, target_name, axis = "xyz", mix_mode = 'ADD', target_space = 'LOCAL_WITH_PARENT', owner_space = 'LOCAL'):
    """Adds Copy Rotation constraint to the bone in local space"""
    
    posemode()
    bone = bpy.context.object.pose.bones[bone_name]
    select_bone(rig.data, bone_name)
    bpy.ops.pose.constraint_add(type='COPY_ROTATION')
    constraint = bone.constraints[-1]
    constraint.target = rig
    constraint.subtarget = target_name
    constraint.use_x = axis.lower().__contains__("x")
    constraint.use_y = axis.lower().__contains__("y")
    constraint.use_z = axis.lower().__contains__("z")
    constraint.mix_mode = mix_mode
    constraint.target_space = target_space
    constraint.owner_space = owner_space

def add_shrinkwrap(armature, bone_name, object):
    """Adds Shrinkwrap Relationship to bone with object as target"""
    posemode()
    bone = bpy.context.object.pose.bones[bone_name]
    select_bone(armature, bone_name)
    bpy.ops.pose.constraint_add(type='SHRINKWRAP')
    constraint = bone.constraints[-1]
    constraint.target = bpy.data.objects[object]
    bpy.ops.constraint.move_to_index(constraint=constraint.name, owner='BONE', index=0)
    constraint.shrinkwrap_type = 'PROJECT'
    constraint.project_axis = 'POS_Y'
    constraint.project_limit = 0.05

def left_bone(bone = ""):
    return bone + ".L"

def right_bone(bone  = ""):
    return bone + ".R"

def mch_bone(bone):
    return bone + ".MCH"

def ctrl_bone(bone):
    return bone + ".Controller"

def add_vertex_subtract(from_group, group, prefix = ""):
    bpy.ops.object.modifier_add(type='VERTEX_WEIGHT_MIX')
    modifier = bpy.context.object.modifiers[-1]
    modifier.name = prefix + modifier.name
    modifier.vertex_group_a = from_group
    modifier.vertex_group_b = group
    modifier.mix_set = 'ALL'
    modifier.mix_mode = 'SUB'
    bpy.ops.object.modifier_move_to_index(modifier=modifier.name, index=0)

def lock_bone_rot(armature, bone_name, axis = 'xyz'):
    """Locks bone rotation along given axis"""

    posemode()
    bone = bpy.context.object.pose.bones[bone_name]
    select_bone(armature, bone_name)
    bone.lock_rotation[0] = axis.lower().__contains__("x")
    bone.lock_rotation[1] = axis.lower().__contains__("y")
    bone.lock_rotation[2] = axis.lower().__contains__("z")

def rig_fingers_ik(arm: bpy.types.Armature):
    """Adds IK, constraints and controllers to each finger"""
   
    for finger in fingers_names:
        extrude_bone(f"{finger}1.R", (0, 0.01, 0), f"{finger}.controller.R", "hand.R", "NORMAL")
        move_to_bone(arm, f"{finger}.controller.R", f"{finger}3.R")
        add_ik_modifier(f"{finger}3.R", 3, f"{finger}.controller.R")
        add_limit_loc_constraint(arm, f"{finger}.controller.R", 
                                 min_x = 0, max_x =0, max_y = 0, max_z = 0)
        constraint_ik_rotation(f"{finger}1.R", False, True, False)
        constraint_ik_rotation(f"{finger}2.R", False, True, False)
        constraint_ik_rotation(f"{finger}3.R", False, True, False)
        

def rig_fingers(arm: bpy.types.Armature):
    """Adds Copy Rotation based rig for fingers"""
    for i in range(4):
        extrude_bone(f"{fingers_names[3]}3.R", (-0.02 + 0.005 * i, 0, 0), f"finger.controller.{i+1}.R", "Hand.R")
        move_bone(arm, f"finger.controller.{i+1}.R", Vector((-0.02, 0, 0)))
        if i > 0:
            add_copy_rotation_constraint(f"finger.controller.{i + 1}.R", "finger.controller.1.R", "x")
        add_limit_rotation_constraint(f"finger.controller.{i+1}.R", "x", min_x=-90)
        lock_bone_rot(f"finger.controller.{i+1}.R", "yz")
    for finger in fingers_names:
        extrude_bone(f"{finger}3.R", (-0.01, 0, 0), f"{finger}.controller.R", "Hand.R")
        extrude_bone(f"{finger}3.R", (-0.0075, 0, 0), f"{finger}.controller.1.R", "Hand.R")
        extrude_bone(f"{finger}3.R", (-0.005, 0, 0), f"{finger}.controller.2.R", "Hand.R")
        extrude_bone(f"{finger}3.R", (-0.0025, 0, 0), f"{finger}.controller.3.R", "Hand.R")
        add_copy_rotation_constraint(f"{finger}1.R", f"{finger}.controller.1.R", "x")
        add_copy_rotation_constraint(f"{finger}2.R", f"{finger}.controller.3.R", "x")
        add_copy_rotation_constraint(f"{finger}3.R", f"{finger}.controller.2.R", "x")
        lock_bone_rot(f"{finger}1.R", "yz")
        lock_bone_rot(f"{finger}2.R", "yz")
        lock_bone_rot(f"{finger}3.R", "yz")
        add_copy_rotation_constraint(f"{finger}.controller.R", "finger.controller.1.R", "x")
        add_limit_rotation_constraint(f"{finger}.controller.R", "x", min_x=-90, affect_transform=False)
        lock_bone_rot(f"{finger}.controller.R", "yz")
        add_copy_rotation_constraint(f"{finger}.controller.1.R", f"{finger}.controller.R", "x")
        add_copy_rotation_constraint(f"{finger}.controller.1.R", "finger.controller.2.R", "x")
        add_limit_rotation_constraint(f"{finger}.controller.1.R", "x", min_x=-90, affect_transform=False)
        lock_bone_rot(f"{finger}.controller.1.R", "yz")
        add_copy_rotation_constraint(f"{finger}.controller.2.R", f"{finger}.controller.R", "x")
        add_copy_rotation_constraint(f"{finger}.controller.2.R", "finger.controller.3.R", "x")
        add_limit_rotation_constraint(f"{finger}.controller.2.R", "x", min_x=-90, affect_transform=False)
        lock_bone_rot(f"{finger}.controller.2.R", "yz")
        add_copy_rotation_constraint(f"{finger}.controller.3.R", f"{finger}.controller.2.R", "x")
        add_copy_rotation_constraint(f"{finger}.controller.3.R", "finger.controller.4.R", "x")
        add_limit_rotation_constraint(f"{finger}.controller.3.R", "x", min_x=-90, affect_transform=False)
        lock_bone_rot(f"{finger}.controller.3.R", "yz")


def create_bone_group(bone_groups, name='Group', color_set='DEFAULT'):
    for group in bone_groups:
        if group.name == name:
            group.color_set = color_set
            return
    bone_groups.new(name=name)
    bone_groups[-1].color_set = color_set


def create_bone_groups(context):
    """Create bone groups for color coding"""
    #TODO: Naming is obsolete
    bone_groups = context.active_object.pose.bone_groups
    create_bone_group(bone_groups, BoneGroups.ctrl, 'THEME03')
    create_bone_group(bone_groups, BoneGroups.poles, 'THEME06')
    create_bone_group(bone_groups, BoneGroups.fk, 'THEME09')
    create_bone_group(bone_groups, BoneGroups.sk_ctrl, 'THEME01')
    create_bone_group(bone_groups, BoneGroups.fk_wo_ik, 'THEME04')


def assign_selected_to_bone_group(context, bone_group):
    i = 1
    for group in context.active_object.pose.bone_groups:
        if group.name == bone_group:
            bpy.ops.pose.group_assign(type=i)
            return
        i += 1
    print(f"Bone group with name {bone_group} not found")

def rig_arm(rig):
    """Adds IK, pole and controller to arm"""
    rig.data.use_mirror_x = False
    sides = [".R",".L"]
    for side in sides:
        print(side)
        duplicate_bone(rig.data, hand_bone_name + side, hand_controller_name + side, "Root", 0.1)
        move_to_bone(rig.data, hand_controller_name + side, arm_bones[3] + side)
        posemode()
        select_bone(rig.data, hand_controller_name + side)
        bpy.context.active_pose_bone.lock_location[0] = False
        bpy.context.active_pose_bone.lock_location[1] = False
        bpy.context.active_pose_bone.lock_location[2] = False
        try:
            bpy.ops.constraint.delete(constraint="Limit Rotation", owner='BONE')
        except Exception:
            pass
        assign_selected_to_bone_group(bpy.context, BoneGroups.ctrl)
        select_bone(rig.data, hand_bone_name + side)
        bpy.context.active_bone.use_inherit_rotation = False
        add_copy_rotation_constraint(rig, hand_bone_name + side, hand_controller_name + side, "xyz")
        extrude_bone(rig.data, arm_bones[1] + side, (0, 0.02, 0), arm_pole_name + side)
        move_bone(rig.data, arm_pole_name + side, Vector((0, 0.2, 0)))
        add_ik_modifier(rig, arm_bones[3] + side, 4, hand_controller_name + side, arm_pole_name + side, -90)
        constraint_ik_rotation(rig.data, arm_bones[1] + side)
        constraint_ik_rotation(rig.data, arm_bones[3] + side)

def rig_leg(rig):
    """Adds IK, pole and controller to arm"""
    rig.data.use_mirror_x = False
    sides = [".R",".L"]
    for side in sides:
        print(side)
        duplicate_bone(rig.data, foot + side, leg_controller_name + side, "Root", 0.1)
        move_to_bone(rig.data, leg_controller_name + side, leg_bones[2] + side)
        posemode()
        select_bone(rig.data, leg_controller_name + side)
        bpy.context.active_pose_bone.lock_location[0] = False
        bpy.context.active_pose_bone.lock_location[1] = False
        bpy.context.active_pose_bone.lock_location[2] = False
        bpy.ops.constraint.delete(constraint="Limit Rotation", owner='BONE')
        assign_selected_to_bone_group(bpy.context, BoneGroups.ctrl)
        select_bone(rig.data, foot + side)
        bpy.context.active_bone.use_inherit_rotation = False
        add_copy_rotation_constraint(rig, foot + side, leg_controller_name + side, "xyz")
        extrude_bone(rig.data, leg_bones[1] + side, (0, 0.02, 0), leg_pole_name + side)
        move_bone(rig.data, leg_pole_name + side, Vector((0, -0.4, 0)))
        add_ik_modifier(rig, leg_bones[2] + side, 3, leg_controller_name + side, leg_pole_name + side, -90)
        constraint_ik_rotation(rig.data, leg_bones[1] + side)

def add_pole_constraint(rig, extrude_vec, first_bone, second_bone, 
                        third_bone, pole, controller, name):
    """Adds bones and constraints
    to avoid IK flipping around pole"""
    sides = [".L"]
    for side in sides:
        extrude_bone(rig.data, first_bone + side, extrude_vec, f"{name}.1{side}", rig.data.bones[first_bone + side].parent.name, from_head=True, orient_type='NORMAL')
        extrude_bone(rig.data, second_bone+ side, extrude_vec, f"{name}.2{side}", None, orient_type='NORMAL')
        extrude_bone(rig.data, third_bone+ side, extrude_vec, f"{name}.3{side}", controller + side, orient_type='NORMAL')
        add_copy_transforms_constraint(rig, f"{name}.2{side}", f"{name}.1{side}", 1)
        add_copy_transforms_constraint(rig, f"{name}.2{side}", f"{name}.3{side}", 0.5)
        add_damped_track_modifier(rig, f"{name}.2{side}", controller + side)
        editmode()
        rig.data.edit_bones[pole + side].parent = rig.data.edit_bones[f"{name}.2{side}"]

def rig_foot_rocker(rig: bpy.types.Object):
    rig.data.use_mirror_x = False
    armature = rig.data
    ground_level = 0.015
    heel_head_position = {
        '.L': (0.2, 0.1, ground_level), 
        '.R': (-0.2, 0.1, ground_level)
        }
    heel_tail_position = {
        '.L': (0.195, 0.13, ground_level), 
        '.R': (-0.195, 0.13, ground_level)
        }
    bone_len  = 0.03
    for side in [left_bone, right_bone]:
        
        deselect_all()
        foot_roll_side_left = side(mch_bone(left_bone(foot + ".Roll.side")))
        editmode()
        bpy.ops.armature.bone_primitive_add(name=foot_roll_side_left)
        select_bone(armature, foot_roll_side_left)
        bpy.context.active_bone.head = heel_head_position[side()]
        bpy.context.active_bone.tail = heel_tail_position[side()]
        bpy.context.active_bone.use_deform = False
        bpy.context.active_bone.parent = armature.edit_bones[side(leg_controller_name)]
        bpy.ops.transform.translate(value=(0.025, 0, 0), orient_type='LOCAL')
        bpy.context.active_bone.roll = 0
        bpy.context.active_bone.layers = al.single_layer(29)

        foot_roll_side_right = side(mch_bone(right_bone(foot + ".Roll.side")))
        duplicate_bone(armature, foot_roll_side_left, foot_roll_side_right, foot_roll_side_left)
        select_bone(armature, foot_roll_side_right)
        bpy.ops.transform.translate(value=(-0.05, 0, 0), orient_type='LOCAL')
        bpy.context.active_bone.roll = 0
        bpy.context.active_bone.layers = al.single_layer(29)

        foot_roll_heel = side(mch_bone(foot + ".Roll.Heel"))
        duplicate_bone(armature, foot_roll_side_left, foot_roll_heel, foot_roll_side_right)
        select_bone(armature, foot_roll_heel)
        bpy.ops.transform.translate(value=(-0.025, 0, 0), orient_type='LOCAL')
        bpy.context.active_bone.roll = 0
        bpy.context.active_bone.layers = al.single_layer(29)

        foot_roll = side(mch_bone(foot + ".Roll"))
        print(foot_roll)
        duplicate_bone(armature, side(toe), foot_roll, foot_roll_heel, 0.03)
        move_to_bone(armature, foot_roll, side(toe), True, True)
        editmode()
        select_bone(armature, foot_roll)
        bpy.context.active_bone.tail[2] = bpy.context.active_bone.head[2]
        bpy.context.active_bone.use_deform = False
        bpy.context.active_bone.roll = 0
        posemode()
        bpy.context.active_pose_bone.custom_shape = None
        bpy.context.active_bone.layers = al.single_layer(29)

        foot_mch = side(mch_bone(foot))
        print(foot_mch)
        duplicate_bone(armature, side(foot), foot_mch, foot_roll)
        move_to_bone(armature, foot_mch, side(leg_bones[2]))
        select_bone(armature, foot_mch)
        bpy.context.active_bone.use_deform = False
        bpy.context.active_bone.use_inherit_rotation = True
        posemode()
        bpy.context.active_pose_bone.custom_shape = None
        remove_constraint(rig, foot_mch, 'Copy Rotation')
        bpy.context.active_bone.layers = al.single_layer(29)

        metatarsals_mch = side(mch_bone(metatarsals))
        print(metatarsals_mch)
        duplicate_bone(armature, side(metatarsals), metatarsals_mch)
        select_bone(armature, metatarsals_mch)
        bpy.context.active_bone.use_deform = False
        posemode()
        bpy.context.active_pose_bone.custom_shape = None
        bpy.context.active_bone.layers = al.single_layer(29)

        toe_mch = side(mch_bone(toe))
        print(toe_mch)
        duplicate_bone(armature, side(toe), toe_mch, foot_roll_heel)
        select_bone(armature, toe_mch)
        bpy.context.active_bone.use_deform = False
        bpy.context.active_bone.layers = al.single_layer(1)

        foot_rocker = side("Foot.Rocker")
        extrude_bone(armature, side(foot), (0, bone_len, 0), foot_rocker, side(leg_controller_name), from_head = True)

        add_copy_rotation_constraint(rig, foot_roll_side_left, foot_rocker, "y", 'REPLACE', 'LOCAL')
        add_limit_rotation_constraint(armature, foot_roll_side_left, "y", min_y = 0, max_y = 180)

        add_copy_rotation_constraint(rig, foot_roll_side_right, foot_rocker, "y", 'REPLACE', 'LOCAL')
        add_limit_rotation_constraint(armature, foot_roll_side_right, "y", min_y = -180, max_y = 0)

        add_copy_rotation_constraint(rig, foot_roll_heel, foot_rocker, "x", 'REPLACE', 'LOCAL')
        add_limit_rotation_constraint(armature, foot_roll_heel, "x", min_x = -180, max_x = 0)

        add_copy_rotation_constraint(rig, foot_roll, foot_rocker, "x", 'REPLACE', 'LOCAL')
        add_limit_rotation_constraint(armature, foot_roll, "x", min_x = 0, max_x = 180)

        add_copy_rotation_constraint(rig, side(toe), toe_mch, "xyz", 'REPLACE', 'WORLD','WORLD')
        add_copy_rotation_constraint(rig, side(metatarsals), metatarsals_mch, "xyz", 'REPLACE', 'WORLD','WORLD')
        add_copy_rotation_constraint(rig, side(foot), foot_mch, "xyz", 'REPLACE', 'WORLD','WORLD')

        posemode()
        shin = side(leg_bones[2])
        bone = bpy.context.object.pose.bones[shin]
        select_bone(rig.data, shin)
        constraint = bone.constraints[-1]
        constraint.subtarget = foot_mch 

def fix_hand_driver(rig):
    """Fixes wrong interaction of hand corrective shapekeys with IK"""
    armature = rig.data
    sides = [left_bone, right_bone]
    for side in sides:
        hand_driver = side("Hand.driver")
        forearm = side(arm_bones[3])
        extrude_bone(armature, forearm, (0, -0.01, 0), hand_driver, forearm, 'NORMAL')
        add_locked_track_constraint(rig, hand_driver, side(hand_bone_name), 1.0, 'TRACK_NEGATIVE_Y')
        add_limit_rotation_constraint(armature, hand_driver, axis = "z", min_z = -90, max_z = 90)
        posemode()
        select_bone(armature, hand_driver)
        bpy.ops.pose.armature_apply(selected=True)
        bpy.ops.pose.bone_layers(layers=al.single_layer(25))
    sides = ['L', 'R']
    for side in sides:
        hand_driver = left_bone("Hand.driver") if side == 'L' else right_bone("Hand.driver")
        for f in armature.animation_data.drivers:
            if f"pJCMHandDwn_70_{side}(fin)" in f.data_path or f"pJCMHandUp_80_{side}(fin)" in f.data_path:
                f.driver.variables[0].targets[0].bone_target = hand_driver


def fix_foot_driver(rig):
    """Fixes wrong interaction of foot corrective shapekeys with IK (kind of)"""
    armature = rig.data
    sides = [left_bone, right_bone]
    for side in sides:
        foot_driver = side("Foot.driver")
        shin = side(leg_bones[2])
        extrude_bone(armature, shin, (0, -0.01, 0), foot_driver, shin, 'NORMAL')
        add_locked_track_constraint(rig, foot_driver, side(foot), 1.0, 'TRACK_NEGATIVE_Z', 'LOCK_X')
        add_limit_rotation_constraint(armature, foot_driver, axis = "x", min_x = -90, max_x = 90)
        posemode()
        select_bone(armature, foot_driver)
        bpy.ops.pose.armature_apply(selected=True)
        bpy.ops.pose.bone_layers(layers=al.single_layer(25))
    sides = ['L', 'R']
    for side in sides:
        foot_driver = left_bone("Foot.driver") if side == 'L' else right_bone("Foot.driver")
        for f in armature.animation_data.drivers:
            if f"pJCMFootDwn_75_{side}(fin)" in f.data_path:
                f.driver.variables[0].targets[0].bone_target = foot_driver
                f.driver.expression = '-1.13*A' # initial down 0.764*A
            elif f"pJCMHDFootUp_40_{side}(fin)" in f.data_path:
                f.driver.variables[0].targets[0].bone_target = foot_driver
                f.driver.expression = '1.45*A' # initial up -1.432*A


def fix_shldr_driver(rig: bpy.types.Object):
    """Fixes wrong interaction of foot corrective shapekeys with IK (kind of)"""
    arm = rig.data

def constraint_bone_to_empty(context: bpy.types.Context):
    bone = context.active_pose_bone
    bone_mat = bone.matrix
    arm_mat = context.object.matrix_world
    matrix = bone_mat @ arm_mat
    vec = tuple(x[3] for x in matrix[:-1])
    objectmode()
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=vec, scale=(1, 1, 1))
    empty = context.active_object
    constraint = bone.constraints.new('COPY_LOCATION')
    constraint.target = empty
    

class FixFootDriver(bpy.types.Operator):
    """Adds bone to fix foot rotation driver with IK"""
    bl_label = "Fix Foot Driver"
    bl_idname = "view3d.fix_foot_driver"
    
    def execute(self, context: bpy.types.Context):
        fix_foot_driver(context.object)
        return {'FINISHED'}


class FixHandDriver(bpy.types.Operator):
    """Adds bone to fix hand rotation driver with IK"""
    bl_label = "Fix Hand Driver"
    bl_idname = "view3d.fix_hand_driver"
    
    def execute(self, context: bpy.types.Context):
        fix_hand_driver(context.object)
        return {'FINISHED'}


class ConstraintBoneToEmpty(bpy.types.Operator):
    """Constraints bone to empty"""
    bl_label = "Constraint bone to empty"
    bl_idname = "view3d.constraint_bone_to_empty"
    def execute(self, context: bpy.types.Context):
        constraint_bone_to_empty(context)
        return {'FINISHED'}


class CreateBoneGroups(bpy.types.Operator):
    """Creates bone groups for color coding"""
    bl_label = "Create bone groups"
    bl_idname = "view3d.create_bone_groups"
    def execute(self, context: bpy.types.Context):
        create_bone_groups(context)
        return {'FINISHED'}


class AddRootBone(bpy.types.Operator):
    """Adds root bone and parents hip to it"""
    bl_label = "Adds root bone"
    bl_idname = "view3d.add_root_bone"
    def execute(self, context: bpy.types.Context):
        current_mode = context.mode
        bpy.ops.view3d.snap_cursor_to_center()
        add_bone('Root')
        editmode()
        context.active_object.data.edit_bones['hip'].parent = context.active_object.data.edit_bones['Root']
        context.active_object.data.edit_bones['Root'].length = 0.3
        posemode()
        select_bone(context.active_object.data, 'Root')
        assign_selected_to_bone_group(context, BoneGroups.ctrl)
        if current_mode == 'OBJECT':
            posemode() 
        else:
            editmode()
        return {'FINISHED'}


class RigArm(bpy.types.Operator):
    """Rigs arm with IK"""
    bl_label = "Rig arm"
    bl_idname = "view3d.rig_arm"
    def execute(self, context: bpy.types.Context):
        al.show_all(context.active_object.data)
        rig_arm(context.active_object)
        al.restore_layers(context.active_object.data)
        return {'FINISHED'}


class RigLeg(bpy.types.Operator):
    """Rigs leg with IK"""
    bl_label = "Rig leg"
    bl_idname = "view3d.rig_leg"
    def execute(self, context: bpy.types.Context):
        al.show_all(context.active_object.data)
        rig_leg(context.active_object)
        al.restore_layers(context.active_object.data)
        return {'FINISHED'}


class AddFootRocker(bpy.types.Operator):
    """Adds controller to rock food around pivot"""
    bl_label = "Add foot rocker"
    bl_idname = "view3d.add_foot_rocker"
    def execute(self, context: bpy.types.Context):
        al.show_all(context.active_object.data)
        rig_foot_rocker(context.active_object)
        al.restore_layers(context.active_object.data)
        return {'FINISHED'}

classes = [FixFootDriver, FixHandDriver, ConstraintBoneToEmpty, CreateBoneGroups, AddRootBone, RigArm, RigLeg, AddFootRocker]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.register_class(cls)

def rig_object():
    rig = bpy.context.active_object
    if rig.type != 'ARMATURE':
        return
    armature = rig.data
    bpy.context.object.data.use_mirror_x = False
    current_layers = armature.layers.copy()
    armature.layers = [True for x in range(32)]
#    add_bone("Root")
#    create_bone_groups(bpy.context)
#    rig_arm(rig)
#    rig_leg(rig)
#    add_pole_constraint(rig, (0, 0.02, 0), leg_bones[0], leg_bones[1], leg_bones[2], leg_pole_name, leg_controller_name, "Leg.pole.constraint")
#    rig_foot_rocker(rig)
    # fix_hand_driver(rig)
#    fix_foot_driver(rig)
    armature.layers = current_layers

if __name__ == "__main__":
    rig_object()
        
