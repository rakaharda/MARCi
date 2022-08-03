import math
import bpy
from mathutils import Vector
from armature_layers import armature_layers as al
from bone_names import *
from rig_utils import *

def rig_fingers_ik(arm: bpy.types.Armature):
    """Adds IK, constraints and controllers to each finger"""
   
    for finger in FINGERS:
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
        extrude_bone(f"{FINGERS[3]}3.R", (-0.02 + 0.005 * i, 0, 0), f"finger.controller.{i+1}.R", "Hand.R")
        move_bone(arm, f"finger.controller.{i+1}.R", Vector((-0.02, 0, 0)))
        if i > 0:
            add_copy_rotation_constraint(f"finger.controller.{i + 1}.R", "finger.controller.1.R", "x")
        add_limit_rotation_constraint(f"finger.controller.{i+1}.R", "x", min_x=-90)
        lock_bone_rot(f"finger.controller.{i+1}.R", "yz")
    for finger in FINGERS:
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
        duplicate_bone(rig.data, HAND + side, HAND_CTRL + side, "Root", 0.1)
        move_to_bone(rig.data, HAND_CTRL + side, ARM_BONES[3] + side)
        posemode()
        select_bone(rig.data, HAND_CTRL + side)
        bpy.context.active_pose_bone.lock_location[0] = False
        bpy.context.active_pose_bone.lock_location[1] = False
        bpy.context.active_pose_bone.lock_location[2] = False
        try:
            bpy.ops.constraint.delete(constraint="Limit Rotation", owner='BONE')
        except Exception:
            pass
        assign_selected_to_bone_group(bpy.context, BoneGroups.ctrl)
        select_bone(rig.data, HAND + side)
        bpy.context.active_bone.use_inherit_rotation = False
        add_copy_rotation_constraint(rig, HAND + side, HAND_CTRL + side, "xyz")
        extrude_bone(rig.data, ARM_BONES[1] + side, (0, 0.02, 0), ARM_POLE + side)
        move_bone(rig.data, ARM_POLE + side, Vector((0, 0.2, 0)))
        add_ik_modifier(rig, ARM_BONES[3] + side, 4, HAND_CTRL + side, ARM_POLE + side, -90)
        constraint_ik_rotation(rig.data, ARM_BONES[1] + side)
        constraint_ik_rotation(rig.data, ARM_BONES[3] + side)

def rig_leg(rig):
    """Adds IK, pole and controller to arm"""
    rig.data.use_mirror_x = False
    sides = [".R",".L"]
    for side in sides:
        print(side)
        duplicate_bone(rig.data, FOOT + side, LEG_CONTROLLER + side, "Root", 0.1)
        move_to_bone(rig.data, LEG_CONTROLLER + side, LEG_BONES[2] + side)
        posemode()
        select_bone(rig.data, LEG_CONTROLLER + side)
        bpy.context.active_pose_bone.lock_location[0] = False
        bpy.context.active_pose_bone.lock_location[1] = False
        bpy.context.active_pose_bone.lock_location[2] = False
        bpy.ops.constraint.delete(constraint="Limit Rotation", owner='BONE')
        assign_selected_to_bone_group(bpy.context, BoneGroups.ctrl)
        select_bone(rig.data, FOOT + side)
        bpy.context.active_bone.use_inherit_rotation = False
        add_copy_rotation_constraint(rig, FOOT + side, LEG_CONTROLLER + side, "xyz")
        extrude_bone(rig.data, LEG_BONES[1] + side, (0, 0.02, 0), LEG_POLE + side)
        move_bone(rig.data, LEG_POLE + side, Vector((0, -0.4, 0)))
        add_ik_modifier(rig, LEG_BONES[2] + side, 3, LEG_CONTROLLER + side, LEG_POLE + side, -90)
        constraint_ik_rotation(rig.data, LEG_BONES[1] + side)

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
        foot_roll_side_left = side(mch_bone(left_bone(FOOT + ".Roll.side")))
        editmode()
        bpy.ops.armature.bone_primitive_add(name=foot_roll_side_left)
        select_bone(armature, foot_roll_side_left)
        bpy.context.active_bone.head = heel_head_position[side()]
        bpy.context.active_bone.tail = heel_tail_position[side()]
        bpy.context.active_bone.use_deform = False
        bpy.context.active_bone.parent = armature.edit_bones[side(LEG_CONTROLLER)]
        bpy.ops.transform.translate(value=(0.025, 0, 0), orient_type='LOCAL')
        bpy.context.active_bone.roll = 0
        bpy.context.active_bone.layers = al.single_layer(29)

        foot_roll_side_right = side(mch_bone(right_bone(FOOT + ".Roll.side")))
        duplicate_bone(armature, foot_roll_side_left, foot_roll_side_right, foot_roll_side_left)
        select_bone(armature, foot_roll_side_right)
        bpy.ops.transform.translate(value=(-0.05, 0, 0), orient_type='LOCAL')
        bpy.context.active_bone.roll = 0
        bpy.context.active_bone.layers = al.single_layer(29)

        foot_roll_heel = side(mch_bone(FOOT + ".Roll.Heel"))
        duplicate_bone(armature, foot_roll_side_left, foot_roll_heel, foot_roll_side_right)
        select_bone(armature, foot_roll_heel)
        bpy.ops.transform.translate(value=(-0.025, 0, 0), orient_type='LOCAL')
        bpy.context.active_bone.roll = 0
        bpy.context.active_bone.layers = al.single_layer(29)

        foot_roll = side(mch_bone(FOOT + ".Roll"))
        print(foot_roll)
        duplicate_bone(armature, side(TOE), foot_roll, foot_roll_heel, 0.03)
        move_to_bone(armature, foot_roll, side(TOE), True, True)
        editmode()
        select_bone(armature, foot_roll)
        bpy.context.active_bone.tail[2] = bpy.context.active_bone.head[2]
        bpy.context.active_bone.use_deform = False
        bpy.context.active_bone.roll = 0
        posemode()
        bpy.context.active_pose_bone.custom_shape = None
        bpy.context.active_bone.layers = al.single_layer(29)

        foot_mch = side(mch_bone(FOOT))
        print(foot_mch)
        duplicate_bone(armature, side(FOOT), foot_mch, foot_roll)
        move_to_bone(armature, foot_mch, side(LEG_BONES[2]))
        select_bone(armature, foot_mch)
        bpy.context.active_bone.use_deform = False
        bpy.context.active_bone.use_inherit_rotation = True
        posemode()
        bpy.context.active_pose_bone.custom_shape = None
        remove_constraint(rig, foot_mch, 'Copy Rotation')
        bpy.context.active_bone.layers = al.single_layer(29)

        metatarsals_mch = side(mch_bone(METATARSALS))
        print(metatarsals_mch)
        duplicate_bone(armature, side(METATARSALS), metatarsals_mch)
        select_bone(armature, metatarsals_mch)
        bpy.context.active_bone.use_deform = False
        posemode()
        bpy.context.active_pose_bone.custom_shape = None
        bpy.context.active_bone.layers = al.single_layer(29)

        toe_mch = side(mch_bone(TOE))
        print(toe_mch)
        duplicate_bone(armature, side(TOE), toe_mch, foot_roll_heel)
        select_bone(armature, toe_mch)
        bpy.context.active_bone.use_deform = False
        bpy.context.active_bone.layers = al.single_layer(1)

        foot_rocker = side("Foot.Rocker")
        extrude_bone(armature, side(FOOT), (0, bone_len, 0), foot_rocker, side(LEG_CONTROLLER), from_head = True)

        add_copy_rotation_constraint(rig, foot_roll_side_left, foot_rocker, "y", 'REPLACE', 'LOCAL')
        add_limit_rotation_constraint(armature, foot_roll_side_left, "y", min_y = 0, max_y = 180)

        add_copy_rotation_constraint(rig, foot_roll_side_right, foot_rocker, "y", 'REPLACE', 'LOCAL')
        add_limit_rotation_constraint(armature, foot_roll_side_right, "y", min_y = -180, max_y = 0)

        add_copy_rotation_constraint(rig, foot_roll_heel, foot_rocker, "x", 'REPLACE', 'LOCAL')
        add_limit_rotation_constraint(armature, foot_roll_heel, "x", min_x = -180, max_x = 0)

        add_copy_rotation_constraint(rig, foot_roll, foot_rocker, "x", 'REPLACE', 'LOCAL')
        add_limit_rotation_constraint(armature, foot_roll, "x", min_x = 0, max_x = 180)

        add_copy_rotation_constraint(rig, side(TOE), toe_mch, "xyz", 'REPLACE', 'WORLD','WORLD')
        add_copy_rotation_constraint(rig, side(METATARSALS), metatarsals_mch, "xyz", 'REPLACE', 'WORLD','WORLD')
        add_copy_rotation_constraint(rig, side(FOOT), foot_mch, "xyz", 'REPLACE', 'WORLD','WORLD')

        posemode()
        shin = side(LEG_BONES[2])
        bone = bpy.context.object.pose.bones[shin]
        select_bone(rig.data, shin)
        constraint = bone.constraints[-1]
        constraint.subtarget = foot_mch 

def fix_hand_driver(rig):
    """Fixes wrong interaction of hand corrective shapekeys with IK"""
    armature = rig.data
    rig.data.use_mirror_x = False
    sides = [left_bone, right_bone]
    for side in sides:
        hand_driver = side("Hand.driver")
        forearm = side(ARM_BONES[3])
        extrude_bone(armature, forearm, (0, -0.01, 0), hand_driver, forearm, 'NORMAL')
        add_locked_track_constraint(rig, hand_driver, side(HAND), 1.0, 'TRACK_NEGATIVE_Y')
        add_limit_rotation_constraint(armature, hand_driver, axis = "z", min_z = -90, max_z = 90)
        posemode()
        select_bone(armature, hand_driver)
        bpy.ops.pose.armature_apply(selected=True)
        bpy.ops.pose.bone_layers(layers=al.single_layer(25))
    for side in sides:
        hand_driver = side("Hand.driver")
        suffix = side()[1:2]
        for f in armature.animation_data.drivers:
            if f"pJCMHandDwn_70_{suffix}(fin)" in f.data_path or f"pJCMHandUp_80_{suffix}(fin)" in f.data_path:
                f.driver.variables[0].targets[0].bone_target = hand_driver


def fix_foot_driver(rig):
    """Fixes wrong interaction of foot corrective shapekeys with IK (kind of)"""
    armature = rig.data
    rig.data.use_mirror_x = False
    sides = [left_bone, right_bone]
    for side in sides:
        foot_driver = side("Foot.driver")
        shin = side(LEG_BONES[2])
        extrude_bone(armature, shin, (0, -0.01, 0), foot_driver, shin, 'NORMAL')
        add_locked_track_constraint(rig, foot_driver, side(FOOT), 1.0, 'TRACK_NEGATIVE_Z', 'LOCK_X')
        add_limit_rotation_constraint(armature, foot_driver, axis = "x", min_x = -90, max_x = 90)
        posemode()
        select_bone(armature, foot_driver)
        bpy.ops.pose.armature_apply(selected=True)
        bpy.ops.pose.bone_layers(layers=al.single_layer(27))
    for side in sides:
        foot_driver = side("Foot.driver")
        suffix = side()[1:2]
        for drv in armature.animation_data.drivers:
            if f"pJCMFootDwn_75_{suffix}(fin)" in drv.data_path:
                drv.driver.variables[0].targets[0].bone_target = foot_driver
                drv.driver.expression = '-1.13*A' # initial down 0.764*A
            elif f"pJCMHDFootUp_40_{suffix}(fin)" in drv.data_path:
                drv.driver.variables[0].targets[0].bone_target = foot_driver
                drv.driver.expression = '1.45*A' # initial up -1.432*A


def fix_shldr_driver(rig: bpy.types.Object):
    """Fixes wrong interaction of foot corrective shapekeys with IK (kind of)"""
    arm = rig.data
    rig.data.use_mirror_x = False
    al.show_all(arm)
    for side in SIDES:
        shldr_driver_x = side("Shldr.Drv.X")
        shldr = side(ARM_BONES[0])
        duplicate_bone(arm, shldr, shldr_driver_x, length = 0.03)
        add_locked_track_constraint(rig, shldr_driver_x, shldr, 1.0, 'TRACK_Y', 'LOCK_X')
        add_limit_rotation_constraint(arm, shldr_driver_x, axis = "x", min_x = -40, max_x = 110)
        posemode()
        select_bone(arm, shldr_driver_x)
        bpy.ops.pose.bone_layers(layers=al.single_layer(25))
        
        shldr_driver_z = side("Shldr.Drv.Z")
        duplicate_bone(arm, shldr, shldr_driver_z, length = 0.03)
        add_locked_track_constraint(rig, shldr_driver_z, shldr, 1.0, 'TRACK_Y', 'LOCK_Z')
        add_limit_rotation_constraint(arm, shldr_driver_z, axis = "z", min_z = -40, max_z = 90)
        posemode()
        select_bone(arm, shldr_driver_z)
        bpy.ops.pose.bone_layers(layers=al.single_layer(25))

        ctrl_side = 'n' if side() == '.L' else ''
        suffix = side()[1:2]
        drivers_to_fix_x = [f"CTRLMD_N_YRotate_{ctrl_side}110(fin)", f"pJCMShldrFwd_110_{suffix}(fin)", ]
        drivers_to_fix_z = [f"pJCMShldrDown_40_{suffix}(fin)", f"pJCMShldrUp_90_{suffix}(fin)", 
                            f"CTRLMD_N_ZRotate_{ctrl_side}40(fin)", f"CTRLMD_N_ZRotate_{ctrl_side}90(fin)"]
        for drv in arm.animation_data.drivers:
            if any(drv_name in drv.data_path for drv_name in drivers_to_fix_x):
                print("Driver:", drv.data_path)
                for var in drv.driver.variables:
                    try:
                        # if var.targets[0].bone_target == shldr:
                        var.targets[0].bone_target = shldr_driver_x
                    except AttributeError:
                        pass
            elif any(drv_name in drv.data_path for drv_name in drivers_to_fix_z):
                print("Driver:", drv.data_path)
                for var in drv.driver.variables:
                    try:
                        # if var.targets[0].bone_target == shldr:
                        var.targets[0].bone_target = shldr_driver_z
                    except AttributeError:
                        pass
    al.restore_layers(arm)        

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
    """Adds bone to fix foot corrective driver with IK"""
    bl_label = "Fix Foot Driver"
    bl_idname = "view3d.fix_foot_driver"
    
    def execute(self, context: bpy.types.Context):
        fix_foot_driver(context.object)
        return {'FINISHED'}


class FixShoulderDriver(bpy.types.Operator):
    """Adds bones to fix shoulder corrective driver with IK"""
    bl_label = "Fix Shldr Driver"
    bl_idname = "view3d.fix_shldr_driver"
    
    def execute(self, context: bpy.types.Context):
        fix_shldr_driver(context.object)
        return {'FINISHED'}


class FixHandDriver(bpy.types.Operator):
    """Adds bone to fix hand corrective driver with IK"""
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

classes = [FixFootDriver, FixHandDriver, ConstraintBoneToEmpty, CreateBoneGroups, 
           AddRootBone, RigArm, RigLeg, AddFootRocker, FixShoulderDriver]

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
#    add_pole_constraint(rig, (0, 0.02, 0), LEG_BONES[0], LEG_BONES[1], LEG_BONES[2], LEG_POLE, LEG_CONTROLLER, "Leg.pole.constraint")
#    rig_foot_rocker(rig)
    # fix_hand_driver(rig)
#    fix_foot_driver(rig)
    armature.layers = current_layers

if __name__ == "__main__":
    rig_object()
        
