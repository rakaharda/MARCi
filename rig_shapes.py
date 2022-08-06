import bpy
from bone_names import *
from rig_utils import *

# Relies on having boneWidget! https://github.com/waylow/boneWidget

def shape_finger_bones(context: bpy.types.Context):
    """Creates circular shapes for finger bones"""
    posemode()
    deselect_all()
    arm = context.active_object.data
    for side in SIDES:
        for finger in FINGERS:
            for i in range(1, 4):
                select_bone(arm, f"{finger}{i}{side()}", True)
    context.scene.widget_list = 'Circle'
    bpy.ops.bonewidget.create_widget(global_size=0.3, slide=1, rotation=(0, 0, 0))

def colorize_finger_bones(context: bpy.types.Context):
    """Assigns finger bones to different groups for improved readability"""
    groups = [BoneGroups.ctrl, BoneGroups.fk_wo_ik, BoneGroups.sk_ctrl, BoneGroups.fk, BoneGroups.poles]
    arm = context.active_object.data
    for side in SIDES:
        for j, finger in enumerate(FINGERS):
            for i in range(1, 4):
                deselect_all()
                select_bone(arm, f"{finger}{i}{side()}", True)
                assign_selected_to_bone_group(context, groups[j])

def shape_leg_bones(context: bpy.types.Context):
    """Creates shapes for leg and foot bones"""
    posemode()
    deselect_all()
    arm = context.active_object.data
    for side in SIDES:
        select_bone(arm, side(LEG_BONES[0]))
        select_bone(arm, side(LEG_BONES[2]), True)
        select_bone(arm, side(FOOT_BONES[1]), True)
        context.scene.widget_list = 'FK Limb 2'
        bpy.ops.bonewidget.create_widget(global_size=1, slide=0, rotation=(0, 0, 0))
        select_bone(arm, side(LEG_BONES[1]))
        context.scene.widget_list = 'Roll 1'
        bpy.ops.bonewidget.create_widget(global_size=0.3, slide=0.5, rotation=(0, 0, math.radians(90)))
        deselect_all()
        for toe in TOES:
            select_bone(arm, side(toe), True)
            select_bone(arm, side(toe + '_2'), True)
        context.scene.widget_list = 'Circle'
        bpy.ops.bonewidget.create_widget(global_size=0.3, slide=1, rotation=(0, 0, 0))
        select_bone(arm, side(FOOT_BONES[0]))
        context.scene.widget_list = 'Sphere'
        bpy.ops.bonewidget.create_widget(global_size=4, slide=0, rotation=(0, 0, 0))
        select_bone(arm, side(FOOT_BONES[2]))

def colorize_toe_bones(context: bpy.types.Context):
    """Assigns finger bones to different groups for improved readability"""
    groups = [BoneGroups.ctrl, BoneGroups.fk_wo_ik, BoneGroups.sk_ctrl, BoneGroups.fk, BoneGroups.poles]
    arm = context.active_object.data
    for side in SIDES:
        for j, toe in enumerate(TOES):
            select_bone(arm, side(toe))
            select_bone(arm, side(toe + '_2'), True)
            assign_selected_to_bone_group(context, groups[j])

def shape_leg_ik_bones(context: bpy.types.Context):
    """Creates shapes for leg IK bones"""
    posemode()
    arm = context.active_object.data
    for side in SIDES:
        select_bone(arm, side(LEG_CONTROLLER))
        context.scene.widget_list = 'Cube'
        bpy.ops.bonewidget.create_widget(global_size=1, slide=0, rotation=(0, 0, 0))
        select_bone(arm, side(LEG_POLE))
        context.scene.widget_list = 'Rhomboid'
        bpy.ops.bonewidget.create_widget(global_size=4, slide=0, rotation=(math.radians(90), 0, 0))

def shape_foot_rocker(context: bpy.types.Context):
    """Creates shapes for foot rocker bones"""
    posemode()
    arm = context.active_object.data
    for side in SIDES:
        select_bone(arm, side(FOOT_ROCKER))
        context.scene.widget_list = 'Chest'
        bpy.ops.bonewidget.create_widget(global_size=1, slide=1.5, rotation=(0, 0, 0))
        select_bone(arm, side(mch_bone(TOE)))
        context.scene.widget_list = 'Chest'
        bpy.ops.bonewidget.create_widget(global_size=1, slide=1, rotation=(0, 0, 0))

def shape_arm_bones(context: bpy.types.Context):
    """Creates shapes for arm bones"""
    posemode()
    arm = context.active_object.data
    for side in SIDES:
        select_bone(arm, side(ARM_BONES[0]))
        select_bone(arm, side(ARM_BONES[2]), True)
        context.scene.widget_list = 'FK Limb 2'
        bpy.ops.bonewidget.create_widget(global_size=1, slide=0, rotation=(0, 0, 0))
        select_bone(arm, side(ARM_BONES[1]))
        select_bone(arm, side(ARM_BONES[3]), True)
        context.scene.widget_list = 'Roll 1'
        bpy.ops.bonewidget.create_widget(global_size=0.3, slide=0.5, rotation=(0, 0, math.radians(90)))
        select_bone(arm, side(HAND))
        context.scene.widget_list = 'Sphere'
        bpy.ops.bonewidget.create_widget(global_size=1, slide=0, rotation=(0, 0, 0))
        select_bone(arm, side(COLLAR))
        context.scene.widget_list = 'Clavicle'
        bpy.ops.bonewidget.create_widget(global_size=1, slide=0.6, rotation=(0, 0, 0))

def shape_arm_ik_bones(context: bpy.types.Context):
    """Creates shapes for arm IK bones"""
    posemode()
    arm = context.active_object.data
    for side in SIDES:
        select_bone(arm, side(HAND_CTRL))
        context.scene.widget_list = 'Cube'
        bpy.ops.bonewidget.create_widget(global_size=1, slide=0, rotation=(0, 0, 0))
        select_bone(arm, side(ARM_POLE))
        context.scene.widget_list = 'Pyramid'
        bpy.ops.bonewidget.create_widget(global_size=4, slide=0, rotation=(0, 0, 0))


def shape_spine_bones(context: bpy.types.Context):
    """Creates shapes for spine and root bones"""
    posemode()
    arm = context.active_object.data
    select_bone(arm, "Root")
    bpy.context.scene.widget_list = 'Root 1'
    bpy.ops.bonewidget.create_widget(global_size=2, rotation=(math.radians(90), 0, 0))
    select_bone(arm, SPINE_BONES[0])
    assign_selected_to_bone_group(context, BoneGroups.ctrl)
    bpy.context.scene.widget_list = 'Cube'
    bpy.ops.bonewidget.create_widget(global_size=0.7, slide=0.5, rotation=(0, 0, 0))
    select_bone(arm, SPINE_BONES[1])
    assign_selected_to_bone_group(context, BoneGroups.fk_wo_ik)
    bpy.context.scene.widget_list = 'FK Limb 1'
    bpy.ops.bonewidget.create_widget(global_size=0.7, slide=0.5, rotation=(0, 0, 0))
    select_bone(arm, SPINE_BONES[2])
    assign_selected_to_bone_group(context, BoneGroups.fk_wo_ik)
    bpy.context.scene.widget_list = 'Torso'
    bpy.ops.bonewidget.create_widget(global_size=1.7, slide=0, rotation=(1.5708, 0, 0))
    select_bone(arm, SPINE_BONES[3])
    assign_selected_to_bone_group(context, BoneGroups.fk_wo_ik)
    bpy.context.scene.widget_list = 'Plane'
    bpy.ops.bonewidget.create_widget(global_size=1.5, slide=0, rotation=(0, 0, 0))
    select_bone(arm, SPINE_BONES[4])
    assign_selected_to_bone_group(context, BoneGroups.fk_wo_ik)
    bpy.context.scene.widget_list = 'Circle'
    bpy.ops.bonewidget.create_widget(global_size=0.7, slide=0, rotation=(0, 0, 0))
    select_bone(arm, SPINE_BONES[5])
    assign_selected_to_bone_group(context, BoneGroups.fk_wo_ik)
    bpy.context.scene.widget_list = 'Chest'
    bpy.ops.bonewidget.create_widget(global_size=1.5, slide=-0.3, rotation=(0, 0, 0))
    select_bone(arm, SPINE_BONES[6])
    select_bone(arm, SPINE_BONES[7], True)
    select_bone(arm, SPINE_BONES[8], True)
    assign_selected_to_bone_group(context, BoneGroups.fk_wo_ik)
    bpy.context.scene.widget_list = 'FK Limb 1'
    bpy.ops.bonewidget.create_widget(global_size=1, slide=0, rotation=(0, 0, 0))
    for side in SIDES:
        select_bone(arm, side(PECTORAL))
        assign_selected_to_bone_group(context, BoneGroups.fk)
        bpy.context.scene.widget_list = 'Paddle (rounded)'
        bpy.ops.bonewidget.create_widget(global_size=1, slide=0, rotation=(0, 0, 0))



class ShapeFingerBones(bpy.types.Operator):
    """Creates circular shapes for finger bones and assigns colors"""
    bl_label = "Shape finger bones"
    bl_idname = "view3d.shape_finger_bones"
    def execute(self, context: bpy.types.Context):
        shape_finger_bones(context)
        colorize_finger_bones(context)
        return {'FINISHED'}

class ShapeLegBones(bpy.types.Operator):
    """Creates shapes for leg bones"""
    bl_label = "Shape leg bones"
    bl_idname = "view3d.shape_leg_bones"
    def execute(self, context: bpy.types.Context):
        shape_leg_bones(context)
        colorize_toe_bones(context)
        try:
            shape_leg_ik_bones(context)
        except Exception:
            pass
        try:
            shape_foot_rocker(context)
        except Exception:
            pass
        return {'FINISHED'}

class ShapeArmBones(bpy.types.Operator):
    """Creates shapes for arm bones"""
    bl_label = "Shape arm bones"
    bl_idname = "view3d.shape_arm_bones"
    def execute(self, context: bpy.types.Context):
        shape_arm_bones(context)
        try:
            shape_arm_ik_bones(context)
        except Exception:
            pass
        return {'FINISHED'}

class ShapeSpineBones(bpy.types.Operator):
    """Creates shapes for spine bones"""
    bl_label = "Shape spine bones"
    bl_idname = "view3d.shape_spine_bones"
    def execute(self, context: bpy.types.Context):
        shape_spine_bones(context)
        return {'FINISHED'}

classes = [ShapeFingerBones, ShapeLegBones, ShapeArmBones, ShapeSpineBones]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.register_class(cls)