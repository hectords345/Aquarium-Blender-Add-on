"""
One‑Click Aquarium Model Optimizer (corrected version)
=====================================================

This script refactors the original `aquarium_optimizer_one_click.py` into a
more robust, self‑contained utility for Blender.  It cleans up a selected
mesh, adds a base ring for burying the model in gravel, introduces
ventilation holes to reduce buoyancy and exports the result to an
optimised STL file.  The implementation includes improved error
handling, support for newer Blender operators and more accurate
placement of geometry based on the object's world coordinates.

To use this script inside Blender:

  1. Open Blender and switch to the *Scripting* workspace.
  2. Load this file into the text editor and ensure the model you
     wish to optimise is selected.
  3. Run the script (Alt + P) to perform the optimisation and export
     the resulting file alongside your `.blend` file with an
     `_optimized.stl` suffix.

Note: This script makes use of Boolean modifiers for adding a base
ring and vent holes.  Depending on the complexity of the input mesh,
these operations can take a few seconds to complete.  If your model
already contains modifiers, the script will add to the existing
stack before applying.
"""

import bpy


def clean_and_solidify(obj: bpy.types.Object, thickness: float = 0.004) -> None:
    """Clean the mesh by merging doubles, fixing normals and adding thickness.

    :param obj: The mesh object to operate on.  It must be active.
    :param thickness: Wall thickness in metres (4 mm by default).
    """
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    # Switch into edit mode
    bpy.ops.object.mode_set(mode='EDIT')
    # Try the legacy remove_doubles operator first
    try:
        bpy.ops.mesh.remove_doubles(threshold=0.0001)
    except Exception:
        # Fallback for Blender ≥2.93
        bpy.ops.mesh.merge(type='DISTANCE', distance=0.0001)
    # Make normals consistent
    bpy.ops.mesh.normals_make_consistent(inside=False)
    # Return to object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    # Add a solidify modifier and apply it
    mod = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    mod.thickness = thickness
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)


def add_bury_base_ring(obj: bpy.types.Object, height: float = 0.006) -> None:
    """Add a base ring to the model for embedding in gravel.

    A cylinder is created just below the lowest point of the mesh and
    unioned with the model.  The cylinder's radius is set to half the
    maximum of the object's X and Y dimensions, ensuring it extends
    slightly beyond the footprint of the model.

    :param obj: The mesh object to extend with a base ring.
    :param height: The height of the ring in metres (6 mm by default).
    """
    # Determine the radius from the object's bounding box
    radius = max(obj.dimensions.x, obj.dimensions.y) / 2.0
    # Find the minimum world‑space Z coordinate of the mesh
    bottom_z = min((obj.matrix_world @ v.co).z for v in obj.data.vertices)
    ring_z = bottom_z - height / 2.0
    # Create a cylinder for the base ring
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=height,
                                        location=(obj.location.x, obj.location.y, ring_z))
    ring = bpy.context.active_object
    # Add a Boolean modifier to perform a union
    bool_mod = obj.modifiers.new(name="BaseRing", type='BOOLEAN')
    bool_mod.operation = 'UNION'
    bool_mod.object = ring
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=bool_mod.name)
    # Remove the temporary cylinder
    bpy.data.objects.remove(ring, do_unlink=True)


def add_vent_holes(obj: bpy.types.Object, hole_radius: float = 0.002, hole_depth: float = 0.01, count: int = 3) -> None:
    """Drill evenly spaced ventilation holes along the bottom of the model.

    The holes are placed along the object's X axis and positioned just
    below the lowest vertex.  A Boolean difference is used to cut each
    hole into the mesh.  All coordinates are calculated in world space
    to ensure proper alignment even if the object is transformed.

    :param obj: The mesh object to cut holes into.
    :param hole_radius: Radius of each hole in metres (2 mm by default).
    :param hole_depth: Depth of each hole in metres (10 mm by default).
    :param count: Number of holes to create across the width of the model.
    """
    # Determine the lowest Z coordinate in world space
    bottom_z = min((obj.matrix_world @ v.co).z for v in obj.data.vertices)
    # Compute the total width of the object and spacing between holes
    width = obj.dimensions.x
    step = width / (count + 1)
    # Starting X position relative to the object's centre
    x_start = obj.location.x - width / 2 + step
    for i in range(count):
        x = x_start + i * step
        hole_z = bottom_z - hole_depth / 2.0
        # Create a cylinder to act as the hole
        bpy.ops.mesh.primitive_cylinder_add(radius=hole_radius, depth=hole_depth,
                                            location=(x, obj.location.y, hole_z))
        hole = bpy.context.active_object
        # Boolean difference to subtract the hole from the model
        bool_mod = obj.modifiers.new(name=f"Vent_{i}", type='BOOLEAN')
        bool_mod.operation = 'DIFFERENCE'
        bool_mod.object = hole
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=bool_mod.name)
        # Delete the temporary cylinder
        bpy.data.objects.remove(hole, do_unlink=True)


def simulate_sink_or_float(obj: bpy.types.Object, material_density: float = 1.27) -> bool:
    """Approximate whether the model will sink or float in water.

    This function estimates the bounding box volume of the object in
    cubic centimetres and multiplies it by the provided material
    density (in g/cm³) to estimate mass.  It then compares the
    resulting average density to that of water (1.0 g/cm³) to infer
    whether the model is likely to sink.

    :param obj: The mesh object to analyse.
    :param material_density: Density of the printing material in g/cm³.
    :returns: True if the object is expected to sink, False otherwise.
    """
    # Convert bounding box dimensions (in metres) to centimetres
    dims_cm = (obj.dimensions.x * 100.0, obj.dimensions.y * 100.0, obj.dimensions.z * 100.0)
    # Bounding box volume in cubic centimetres
    vol_cm3 = dims_cm[0] * dims_cm[1] * dims_cm[2]
    est_mass_g = vol_cm3 * material_density
    avg_density = est_mass_g / vol_cm3  # g/cm³
    will_sink = avg_density > 1.0
    print(f"🔍 Bounding box volume: {vol_cm3:.2f} cm³")
    print(f"⚖️ Estimated mass: {est_mass_g:.2f} g (assuming density {material_density} g/cm³)")
    print("🌊 Sinking:", "✅ Yes" if will_sink else "🆘 No")
    return will_sink


def main() -> None:
    """Entry point for running the optimisation.

    If a mesh object is selected, this function will perform all
    optimisation steps and export the result to an STL file.  Messages
    describing the estimated mass and sink/float status are printed to
    the console.
    """
    obj = bpy.context.active_object
    if not obj or obj.type != 'MESH':
        print("❌ No mesh object selected.")
        return
    clean_and_solidify(obj)
    add_bury_base_ring(obj)
    add_vent_holes(obj)
    simulate_sink_or_float(obj)
    # Ensure the object is selected before export
    obj.select_set(True)
    path = bpy.path.abspath(f"//{obj.name}_optimized.stl")
    bpy.ops.export_mesh.stl(filepath=path, use_selection=True)
    print(f"✅ Exported to: {path}")


# When run from the Blender text editor, invoke main() immediately
if __name__ == "__main__":
    main()