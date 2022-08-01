import os
import sys
import bpy

FILES_DIR = "C:/Saves/my thingies/blender files/blender/Addons/My shit/MARCi"
 
INIT_FILE = "__init__.py"
 
if FILES_DIR not in sys.path:
    sys.path.append(FILES_DIR)
 
file = os.path.join(FILES_DIR, INIT_FILE)
 
if 'DEBUG_MODE' not in sys.argv:
    sys.argv.append('DEBUG_MODE')
 
exec(compile(open(file).read(), INIT_FILE, 'exec'))
 
if 'DEBUG_MODE' in sys.argv:
    sys.argv.remove('DEBUG_MODE')

PROPS = [
    ('transfer_only_existing', bpy.props.BoolProperty(name='Transfer only existing', default=True))
]

class VIEW3D_MARCi:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Rig Tools"
    bl_options = {"DEFAULT_CLOSED"}

class VIEW3D_PT_MARCi(VIEW3D_MARCi, bpy.types.Panel):
    bl_label = "MARCi"
    bl_idname = "marci_panel"

    def draw(self, context):
        self.layout.operator("view3d.constraint_bone_to_empty", text="Constraint bone to empty")

class VIEW3D_PT_MARCi_RENAME_BONES(VIEW3D_MARCi, bpy.types.Panel):
    bl_parent_id = "marci_panel"
    bl_label = "Rename bones"

    def draw(self, context):
        self.layout.operator("view3d.rename_bones", text="Rename Daz to Blender")
        self.layout.operator("view3d.rename_bones_to_daz", text="Rename Blender to Daz")

class VIEW3D_PT_MARCi_RIGGING(VIEW3D_MARCi, bpy.types.Panel):
    bl_parent_id = "marci_panel"
    bl_label = "Rigging"
    
    def draw(self, context):
        self.layout.operator("view3d.create_bone_groups", text="Create bone groups")
        self.layout.operator("view3d.add_root_bone", text="Add root bone")
        self.layout.operator("view3d.rig_arm", text="Rig arm")
        self.layout.operator("view3d.rig_leg", text="Rig leg")
        self.layout.operator("view3d.add_foot_rocker", text="Add foot rocker")
        


class VIEW3D_PT_MARCi_FIXES(VIEW3D_MARCi, bpy.types.Panel):
    bl_parent_id = "marci_panel"
    bl_label = "Fixes"

    def draw(self, context):
        self.layout.operator("view3d.fix_foot_driver", text="Fix Foot driver")
        self.layout.operator("view3d.fix_hand_driver", text="Fix hand driver")
        self.layout.operator("view3d.fix_shldr_driver", text="Fix shoulder driver")

class VIEW3D_PT_MARCi_TRANSFER_DRIVERS(VIEW3D_MARCi, bpy.types.Panel):
    bl_parent_id = "marci_panel"
    bl_label = "Transfer Drivers"

    def draw(self, context):
        self.layout.operator("view3d.transfer_drivers", text="Transfer drivers")
        self.layout.prop(context.scene, PROPS[0][0])


classes = [VIEW3D_PT_MARCi, 
           VIEW3D_PT_MARCi_RENAME_BONES, 
           VIEW3D_PT_MARCi_RIGGING, 
           VIEW3D_PT_MARCi_TRANSFER_DRIVERS,
           VIEW3D_PT_MARCi_FIXES]

def register():
    for (prop_name, prop_value) in PROPS:
        setattr(bpy.types.Scene, prop_name, prop_value)

    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for (prop_name, _) in PROPS:
        delattr(bpy.types.Scene, prop_name)

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()