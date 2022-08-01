from ftplib import all_errors
import bpy

class ArmatureLayers:
    all_layers = [True for x in range(32)]
    none_layers = [False for x in range(32)]
    current_layers: list[bool]

    def show_all(self, armature: bpy.types.Armature):
        self.current_layers = [*armature.layers]
        armature.layers = self.all_layers.copy()

    def restore_layers(self, armature: bpy.types.Armature):
        armature.layers = self.current_layers

    def single_layer(self, layer: int) -> list[bool]:
        layers = self.none_layers.copy()
        layers[layer] = True
        return layers
        
armature_layers = ArmatureLayers()