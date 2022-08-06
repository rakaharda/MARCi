import bpy

class RenameBones(bpy.types.Operator):
    """Changes from prefix to suffix"""
    bl_label = "DAZ to Blender"
    bl_idname = "view3d.rename_bones"
    
    def execute(self, context):
        if(context.mode not in ["EDIT_ARMATURE", "OBJECT"]):
            return ('CANCELED')
        
        if(context.mode == "EDIT_ARMATURE"):
            self.rename_bones(context.visible_bones)
        elif(context.mode == "OBJECT"):
            bones = context.active_object.data.bones
            self.rename_bones(bones)
        return {'FINISHED'}
    
    
    def rename_bones(self, bones):
        for bone in bones:
            if(bone.name[0] == 'l' and bone.name[1].isupper()):
                bone.name = bone.name[1:] + ".L"
            elif(bone.name[0] == 'r' and bone.name[1].isupper()):
                bone.name = bone.name[1:] + ".R"

class RenameBonesToDaz(bpy.types.Operator):
    """Changes from suffix to prefix"""
    bl_label = "Blender to DAZ"
    bl_idname = "view3d.rename_bones_to_daz"
    
    def execute(self, context):
        if(bpy.context.mode not in ["EDIT_ARMATURE", "OBJECT"]):
            return ('CANCELED')
        
        if(bpy.context.mode == "EDIT_ARMATURE"):
            self.rename_bones(context.visible_bones)
        elif(bpy.context.mode == "OBJECT"):
            for armature in bpy.data.armatures:
                bones = armature.bones
                self.rename_bones(bones)
        return {'FINISHED'}
    
    
    def rename_bones(self, bones):
        for bone in bones:
            if(bone.name[-2] == '.'):
                if(bone.name[-1] == 'L'):
                    bone.name = 'l' + bone.name[:-2]
                elif(bone.name[-1] == 'R'):
                    bone.name = 'r' + bone.name[:-2]

def register():
    bpy.utils.register_class(RenameBones)
    bpy.utils.register_class(RenameBonesToDaz)

def unregister():
    bpy.utils.unregister_class(RenameBones)
    bpy.utils.unregister_class(RenameBonesToDaz)