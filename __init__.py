import sys
import importlib

bl_info = {
    'name': 'My Awesome Rig Script',
    'Category': 'Rigging',
    'version': '0.0.1'
}

modules_names = ['rigging', 'rename_bones', 'transfer_drivers', 'rig_shapes', 'bone_names', 'rig_utils']

modules_full_names = {}

for current_module_name in modules_names:
    if 'DEBUG_MODE' in sys.argv:
        modules_full_names[current_module_name] = ('{}'.format(current_module_name))
    else:
        modules_full_names[current_module_name] = ('{}.{}'.format(__name__, current_module_name))

for current_module_name in modules_full_names.values():
    if current_module_name in sys.modules:
        importlib.reload(sys.modules[current_module_name])
    else:
        globals()[current_module_name] = importlib.import_module(current_module_name)
        setattr(globals()[current_module_name], 'modules_names', current_module_name)

def register():
    for current_module_name in modules_full_names.values():
        if current_module_name in sys.modules:
            if hasattr(sys.modules[current_module_name], 'register'):
                sys.modules[current_module_name].register()

def unregister():
    for current_module_name in modules_full_names.values():
        if current_module_name in sys.modules:
            if hasattr(sys.modules[current_module_name], 'unregister'):
                sys.modules[current_module_name].unregister()

if __name__ == "__main__":
    register()