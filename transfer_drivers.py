import bpy

from typing import NamedTuple

class Params(NamedTuple):
    transfer_only_existing: bool

class  TransferDrivers(bpy.types.Operator):
    """Transfer drivers from active object to selected"""
    bl_label = "Transfer drivers from active"
    bl_idname = "view3d.transfer_drivers"

    def execute(self, context: bpy.types.Context):
        if len(context.selected_objects) != 2:
            return {'CANCELLED'}
        params = Params(context.scene.transfer_only_existing)
        srckey = context.active_object.data.shape_keys
        dstkey = context.selected_objects[0].data.shape_keys
        if dstkey == srckey:
            dstkey = context.selected_objects[1].data.shape_keys
        dstrig = dstkey.parent
        transfer_drivers(srckey, dstkey, dstrig, params)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(TransferDrivers)

def unregister():
    bpy.utils.unregister_class(TransferDrivers)

def transfer_drivers(srckey: bpy.types.Key, dstkey: bpy.types.Key, dstrig: bpy.types.Object, params: Params):
    fcurves = srckey.animation_data.drivers
    dest_fcurves = None
    try:
        dest_fcurves = dstkey.animation_data.drivers
    except AttributeError:
        dstkey.animation_data_create()
        dest_fcurves = dstkey.animation_data.drivers
    for fcurve in fcurves:
        try:
            new_fcurve = None
            if params.transfer_only_existing:
                for f in dstkey.key_blocks:
                    if fcurve.data_path[12:-8] == f.name:
                        new_fcurve = dest_fcurves.new(fcurve.data_path)
            else:
                new_fcurve = dest_fcurves.new(fcurve.data_path)
        except RuntimeError as e:
            print(e)
            print(fcurve.data_path)
            continue
        if new_fcurve == None:
            continue
        print(fcurve.data_path)
        while len(new_fcurve.keyframe_points) > 0:
            new_fcurve.keyframe_points.remove(new_fcurve.keyframe_points[0])
        new_fcurve.keyframe_points.add(len(fcurve.keyframe_points))
        if len(new_fcurve.keyframe_points) > 0:
            for i, kf in new_fcurve.keyframe_points.items():
                kf.interpolation = fcurve.keyframe_points[i].interpolation
                kf.co = fcurve.keyframe_points[i].co
                kf.easing = fcurve.keyframe_points[i].easing
                kf.handle_left = fcurve.keyframe_points[i].handle_left
                kf.handle_left_type = fcurve.keyframe_points[i].handle_left_type
                kf.handle_right = fcurve.keyframe_points[i].handle_right
                kf.handle_right_type = fcurve.keyframe_points[i].handle_right_type
        new_fcurve.driver.type = fcurve.driver.type 
        new_fcurve.driver.expression = fcurve.driver.expression
        for var in fcurve.driver.variables:
            v = new_fcurve.driver.variables.new()
            v.name = var.name
            v.type = var.type
            if v.type == 'SINGLE_PROP':
                v.targets[0].id_type = var.targets[0].id_type
                if v.targets[0].id_type == 'KEY':
                    v.targets[0].id = dstkey
                elif v.targets[0].id_type == 'ARMATURE':
                    v.targets[0].id = dstrig.data
                else:
                    v.targets[0].id = var.targets[0].id
                v.targets[0].data_path = var.targets[0].data_path
            else:
                v.targets[0].id = dstrig
                v.targets[0].bone_target = fcurve.driver.variables[0].targets[0].bone_target
                v.targets[0].transform_space = fcurve.driver.variables[0].targets[0].transform_space
                v.targets[0].transform_type = fcurve.driver.variables[0].targets[0].transform_type