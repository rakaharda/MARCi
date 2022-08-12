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
        

def add_finger_controller(context: bpy.types.Context):
    """Adds Copy Rotation based rig for fingers"""
    rig = context.active_object
    arm = rig.data
    for side in SIDES:
        finger_ctrl = side(FINGER_CTRL)
        extrude_bone(arm, side(HAND), (0, 0.1, 0), finger_ctrl, side(HAND), 'NORMAL')
        editmode()
        if side() == '.L':
            rig.data.edit_bones[finger_ctrl].roll = math.radians(-130)
        else:
            rig.data.edit_bones[finger_ctrl].roll = math.radians(130)
        posemode()
        select_bone(arm, finger_ctrl)
        context.active_pose_bone.lock_location[0] = True
        context.active_pose_bone.lock_location[2] = True
        assign_selected_to_bone_group(bpy.context, BoneGroups.sk_ctrl)
        add_limit_rotation_constraint(arm, finger_ctrl, axis='xyz', max_x=110, min_x=-50, max_y=5, min_y=-5, max_z=18, min_z=-18)
        add_limit_loc_constraint(arm, finger_ctrl, min_y = -0.1, max_y = 0)
        for finger in FINGERS[1:]:
            for i in range (1, 4):
                grab_constraint = "MARCi Grab"
                clench_constraint = "MARCi Clench"
                f = side(f"{finger}{i}")
                axis = 'xyz'
                if i > 1:
                    axis = 'x'
                if i < 3:
                    add_copy_rotation_constraint(rig, f, finger_ctrl, axis, target_space='LOCAL', name=grab_constraint)
                add_transformation_constraint(context, f, finger_ctrl,
                                              map_to='ROTATION', map_to_x_from='Y',
                                              from_min_y=-0.1, to_min_x = 90,
                                              name=clench_constraint)
                posemode()
                select_bone(arm, f)
                bpy.ops.constraint.move_to_index(constraint=grab_constraint, owner='BONE', index=0)
                bpy.ops.constraint.move_to_index(constraint=clench_constraint, owner='BONE', index=0)

                
           


def create_bone_groups(context):
    """Create bone groups for color coding"""
    #TODO: Naming is obsolete
    bone_groups = context.active_object.pose.bone_groups
    create_bone_group(bone_groups, BoneGroups.ctrl, 'THEME03')
    create_bone_group(bone_groups, BoneGroups.poles, 'THEME06')
    create_bone_group(bone_groups, BoneGroups.fk, 'THEME09')
    create_bone_group(bone_groups, BoneGroups.sk_ctrl, 'THEME01')
    create_bone_group(bone_groups, BoneGroups.fk_wo_ik, 'THEME04')

def rig_arm(rig):
    """Adds IK, pole and controller to arm"""
    rig.data.use_mirror_x = False
    armature = rig.data
    for side in SIDES:
        hand_ctrl = side(HAND_CTRL)
        duplicate_bone(armature, side(HAND), hand_ctrl, "Root", 0.1)
        move_to_bone(armature, hand_ctrl, side(ARM_BONES[3]))
        posemode()
        select_bone(armature, hand_ctrl)
        bpy.context.active_pose_bone.lock_location[0] = False
        bpy.context.active_pose_bone.lock_location[1] = False
        bpy.context.active_pose_bone.lock_location[2] = False
        try:
            bpy.ops.constraint.delete(constraint="Limit Rotation", owner='BONE')
        except Exception:
            pass
        assign_selected_to_bone_group(bpy.context, BoneGroups.ctrl)
        select_bone(armature, side(HAND))
        bpy.context.active_bone.use_inherit_rotation = False
        assign_selected_to_bone_group(bpy.context, BoneGroups.fk)
        add_copy_rotation_constraint(rig, side(HAND), hand_ctrl, "xyz")
        arm_pole = side(ARM_POLE)
        extrude_bone(armature, side(ARM_BONES[1]), (0, 0.02, 0), arm_pole)
        move_bone(armature, arm_pole, Vector((0, 0.2, 0)))
        posemode()
        select_bone(armature, arm_pole)
        assign_selected_to_bone_group(bpy.context, BoneGroups.poles)
        add_ik_modifier(rig, side(ARM_BONES[3]), 4, hand_ctrl, arm_pole, -90)
        constraint_ik_rotation(armature, side(ARM_BONES[1]))
        constraint_ik_rotation(armature, side(ARM_BONES[3]))
        posemode()
        select_bone(armature, side(ARM_BONES[0]))
        select_bone(armature, side(ARM_BONES[2]), True)
        assign_selected_to_bone_group(bpy.context, BoneGroups.fk)
        select_bone(armature, side(ARM_BONES[1]))
        select_bone(armature, side(ARM_BONES[3]), True)
        select_bone(armature, side(COLLAR), True)
        assign_selected_to_bone_group(bpy.context, BoneGroups.fk_wo_ik)
        


def rig_leg(rig):
    """Adds IK, pole and controller to arm"""
    rig.data.use_mirror_x = False
    for side in SIDES:
        leg_ctrl = side(LEG_CONTROLLER)
        extrude_bone(rig.data, side(LEG_BONES[2]), (0, -0.1, 0), leg_ctrl)
        move_to_bone(rig.data, leg_ctrl, side(LEG_BONES[2]))
        editmode()
        if side() == '.L':
            rig.data.edit_bones[leg_ctrl].roll = math.radians(180)
        else:
            rig.data.edit_bones[leg_ctrl].roll = math.radians(-180)
        posemode()
        select_bone(rig.data, leg_ctrl)
        bpy.ops.constraint.delete(constraint="Limit Rotation", owner='BONE')
        assign_selected_to_bone_group(bpy.context, BoneGroups.ctrl)
        select_bone(rig.data, side(FOOT))
        bpy.context.active_bone.use_inherit_rotation = False
        assign_selected_to_bone_group(bpy.context, BoneGroups.fk)
        leg_pole = side(LEG_POLE)
        add_copy_rotation_constraint(rig, side(FOOT), leg_ctrl, "xyz")
        extrude_bone(rig.data, side(LEG_BONES[1]), (0, 0.02, 0), leg_pole)
        move_bone(rig.data, leg_pole, Vector((0, -0.4, 0)))
        posemode()
        select_bone(rig.data, leg_pole)
        assign_selected_to_bone_group(bpy.context, BoneGroups.poles)
        add_ik_modifier(rig, side(LEG_BONES[2]), 3, leg_ctrl, leg_pole, -90)
        constraint_ik_rotation(rig.data, side(LEG_BONES[1]))
        posemode()
        select_bone(rig.data, side(LEG_BONES[0]))
        select_bone(rig.data, side(LEG_BONES[2]), True)
        assign_selected_to_bone_group(bpy.context, BoneGroups.fk)
        select_bone(rig.data, side(LEG_BONES[1]))
        assign_selected_to_bone_group(bpy.context, BoneGroups.fk_wo_ik)


def add_pole_constraint(rig, extrude_vec, first_bone, second_bone, 
                        third_bone, pole, controller, name):
    """Adds bones and constraints
    to avoid IK flipping around pole"""
    for side in SIDES:
        extrude_bone(rig.data, side(first_bone), extrude_vec, f"{name}.1{side()}", rig.data.bones[side(first_bone)].parent.name, from_head=True, orient_type='NORMAL')
        extrude_bone(rig.data, side(second_bone), extrude_vec, f"{name}.2{side()}", None, orient_type='NORMAL')
        extrude_bone(rig.data, side(third_bone), extrude_vec, f"{name}.3{side()}", side(controller), orient_type='NORMAL')
        add_copy_transforms_constraint(rig, f"{name}.2{side()}", f"{name}.1{side()}", 1)
        add_copy_transforms_constraint(rig, f"{name}.2{side()}", f"{name}.3{side()}", 0.5)
        add_damped_track_modifier(rig, f"{name}.2{side()}", side(controller))
        editmode()
        rig.data.edit_bones[side(pole)].parent = rig.data.edit_bones[f"{name}.2{side()}"]


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
        assign_selected_to_bone_group(bpy.context, BoneGroups.fk_wo_ik)
        remove_constraint(rig, foot_mch, 'Copy Rotation')
        bpy.context.active_bone.layers = al.single_layer(29)

        metatarsals_mch = side(mch_bone(METATARSALS))
        print(metatarsals_mch)
        duplicate_bone(armature, side(METATARSALS), metatarsals_mch)
        select_bone(armature, metatarsals_mch)
        bpy.context.active_bone.use_deform = False
        posemode()
        bpy.context.active_pose_bone.custom_shape = None
        assign_selected_to_bone_group(bpy.context, BoneGroups.fk)
        bpy.context.active_bone.layers = al.single_layer(29)

        toe_mch = side(mch_bone(TOE))
        print(toe_mch)
        duplicate_bone(armature, side(TOE), toe_mch, foot_roll_heel)
        select_bone(armature, toe_mch)
        assign_selected_to_bone_group(bpy.context, BoneGroups.sk_ctrl)
        bpy.context.active_bone.use_deform = False
        bpy.context.active_bone.layers = al.single_layer(1)

        foot_rocker = side(FOOT_ROCKER)
        extrude_bone(armature, side(FOOT), (0, bone_len, 0), foot_rocker, side(LEG_CONTROLLER), from_head = True)
        posemode()
        select_bone(armature, foot_rocker)
        assign_selected_to_bone_group(bpy.context, BoneGroups.sk_ctrl)
        
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


#TODO: Move to animation module
def constraint_bone_to_empty(context: bpy.types.Context):
    bone = context.active_pose_bone
    bone_mat = bone.matrix
    arm_mat = context.object.matrix_world
    matrix = arm_mat @ bone_mat
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


#TODO: Move to animation module
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
    """Adds root bone and parents hip to it, changes rotation mode of all bones to Euler XYZ"""
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
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.rotation_mode_set(type='XYZ')
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


class AddFingerController(bpy.types.Operator):
    """Adds controller to simultaneous finger rotation"""
    bl_label = "Add finger controller"
    bl_idname = "view3d.add_finger_controller"
    def execute(self, context: bpy.types.Context):
        al.show_all(context.active_object.data)
        add_finger_controller(context)
        al.restore_layers(context.active_object.data)
        return {'FINISHED'}

class RigLeg(bpy.types.Operator):
    """Rigs leg with IK"""
    bl_label = "Rig leg"
    bl_idname = "view3d.rig_leg"
    def execute(self, context: bpy.types.Context):
        rig = context.active_object
        al.show_all(rig.data)
        rig_leg(rig)
        add_pole_constraint(rig, (0, 0.02, 0), LEG_BONES[0], LEG_BONES[1], LEG_BONES[2], LEG_POLE, LEG_CONTROLLER, "Leg.pole.constraint")
        al.restore_layers(rig.data)
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
           AddRootBone, RigArm, RigLeg, AddFootRocker, FixShoulderDriver, AddFingerController]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.register_class(cls)
        
