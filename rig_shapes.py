import bpy
from bone_names import *
from rig_utils import *
from rigging import assign_selected_to_bone_group

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
    bpy.ops.bonewidget.create_widget(global_size=0.3, slide=1)

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
        

class ShapeFingerBones(bpy.types.Operator):
    """Creates circular shapes for finger bones and assigns colors"""
    bl_label = "Shape finger bones"
    bl_idname = "view3d.shape_finger_bones"
    def execute(self, context: bpy.types.Context):
        shape_finger_bones(context)
        colorize_finger_bones(context)
        return {'FINISHED'}


classes = [ShapeFingerBones]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.register_class(cls)