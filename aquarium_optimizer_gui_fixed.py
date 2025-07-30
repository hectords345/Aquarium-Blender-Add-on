"""
Aquarium Optimizer Add‑on (corrected version)
===========================================

This module contains a refactored version of the `aquarium_optimizer_gui.py`
provided with the project.  The original script performed a few common
mesh clean‑up tasks and added a solidify modifier to add wall thickness,
but it made a few assumptions about Blender's API that could lead to
runtime errors in newer releases.  This corrected version adds
additional error handling, supports newer Blender API conventions and
ensures the target object is properly selected when operations are
performed.

Use this script as a drop‑in replacement for the original add‑on in
Blender ≥3.0.  Installation instructions remain the same: install this
file via the `Edit › Preferences › Add‑ons › Install` dialog and
enable it from the add‑on list.
"""

import bpy

bl_info = {
    "name": "Aquarium Optimizer (Fixed)",
    "blender": (3, 0, 0),
    "category": "Object",
}


class OBJECT_OT_AquariumOptimize(bpy.types.Operator):
    """Optimize the currently selected aquarium model.

    When invoked, this operator merges coincident vertices,
    recalculates face normals and applies a Solidify modifier to give
    the mesh a 4 mm wall thickness.  It attempts to use the legacy
    `remove_doubles` operator if present, otherwise it falls back to
    the newer `mesh.merge` operator (introduced in Blender 2.93+) for
    removing duplicate vertices.  An error is reported if no mesh
    object is active.
    """

    bl_idname = "object.aquarium_optimize"
    bl_label = "Optimize Aquarium Model"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # Grab the active object and verify it's a mesh
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({"ERROR"}, "No mesh object selected")
            return {'CANCELLED'}

        # Ensure the object is both selected and active for operators
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        # Switch to edit mode to perform mesh operations
        bpy.ops.object.mode_set(mode='EDIT')
        try:
            # Blender versions prior to 2.93 expose this operator
            bpy.ops.mesh.remove_doubles(threshold=0.0001)
        except Exception:
            # Blender 2.93+ replaced remove_doubles with merge by distance
            bpy.ops.mesh.merge(type='DISTANCE', distance=0.0001)
        # Make normals face consistently outward
        bpy.ops.mesh.normals_make_consistent(inside=False)
        # Return to object mode so modifiers can be applied
        bpy.ops.object.mode_set(mode='OBJECT')

        # Add a Solidify modifier with a default thickness of 4 mm (0.004 m)
        mod = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
        mod.thickness = 0.004
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=mod.name)

        self.report({"INFO"}, "✅ Optimized and ready to print")
        return {'FINISHED'}


class VIEW3D_PT_AquariumPanel(bpy.types.Panel):
    """UI Panel for the Aquarium Optimizer operator.

    Adds a button under a dedicated 'Aquarium' tab in the 3D Viewport
    sidebar, allowing users to run the optimizer on the selected mesh
    with a single click.
    """

    bl_label = "Aquarium Tools"
    bl_idname = "VIEW3D_PT_aquarium_optimizer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Aquarium'

    def draw(self, context):
        layout = self.layout
        layout.operator(OBJECT_OT_AquariumOptimize.bl_idname)


def register():
    bpy.utils.register_class(OBJECT_OT_AquariumOptimize)
    bpy.utils.register_class(VIEW3D_PT_AquariumPanel)


def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_AquariumPanel)
    bpy.utils.unregister_class(OBJECT_OT_AquariumOptimize)


if __name__ == "__main__":
    register()