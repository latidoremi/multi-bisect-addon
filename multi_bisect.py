import bpy, bmesh
from mathutils import Vector

bl_info = {
    "name": "Multi Bisect",
    "author": "Latidoremi",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "Mesh > Multi Bisect",
    "description": "Bisect selected faces with multiple planes",
    "category": "Mesh",
}

class MESH_OT_multi_bisect(bpy.types.Operator):
    """Bisect selected faces with multiple planes"""
    bl_idname = "mesh.multi_bisect"
    bl_label = "Multi Bisect"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'
    
    items=[
    ('End Points', 'End Points', '', 0),
    ('Offset', 'Offset', '', 1),
    ('Direction End Points', 'Direction End Points', '', 2),
    ('Direction Offset', 'Direction Offset', '', 3)
    ]
    method:bpy.props.EnumProperty(items = items, name = 'Method')
    
    count: bpy.props.IntProperty(name='Count', default=1, min=0)
    
    start: bpy.props.FloatVectorProperty(name='Start')
    end: bpy.props.FloatVectorProperty(name='End', default = (0,0,1))
    offset: bpy.props.FloatVectorProperty(name='Offset', default = (0,0,1))
    direction: bpy.props.FloatVectorProperty(name='Direction', default = (0,0,1))
    length: bpy.props.FloatProperty(name='Length')
    step: bpy.props.FloatProperty(name='Step')
    
    def execute(self, context):
        start = Vector(self.start)
        if self.method =='End Points':
            vec = Vector(self.end) - Vector(self.start)
            no = vec.normalized()
            step = (vec.length/(self.count-1) if self.count>1 else 0)
            
        elif self.method=='Offset':
            no = Vector(self.offset).normalized()
            step = Vector(self.offset).length
            
        elif self.method == 'Direction End Points':
            no = Vector(self.direction).normalized()
            step = (self.length/(self.count-1) if self.count>1 else 0)
            
        elif self.method == 'Direction Offset':
            no = Vector(self.direction).normalized()
            step = self.step
            
        
        me = context.object.data
        
        bm = bmesh.from_edit_mesh(me)
        bm.faces.ensure_lookup_table()
        faces = [f for f in bm.faces if f.select]
        edges = []
        for f in faces:
            for e in f.edges:
                if not e in edges:
                    edges.append(e)
        geom = faces + edges
        
        for i in range(self.count):
            co = start + i*no*step
            r = bmesh.ops.bisect_plane(bm, geom=geom, plane_co=co, plane_no=no)
            
            for ele in r['geom']:
                ele.select_set(True)
            geom = r['geom']
        
        bmesh.update_edit_mesh(me, loop_triangles=True)
        
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, 'method', text='')
        col.prop(self, 'count')
        col.prop(self, 'start')
        
        if self.method =='End Points':
            col.prop(self, 'end')
            
        elif self.method=='Offset':
            col.prop(self, 'offset')
            
        elif self.method == 'Direction End Points':
            col.prop(self, 'direction')
            col.prop(self, 'length')
            
        elif self.method == 'Direction Offset':
            col.prop(self, 'direction')
            col.prop(self, 'step')

         
def add_multi_bisect_button(self, context):
    self.layout.operator("mesh.multi_bisect", text="Multi Bisect")

def register():
    bpy.utils.register_class(MESH_OT_multi_bisect)
    bpy.types.VIEW3D_MT_edit_mesh.append(add_multi_bisect_button)

def unregister():
    bpy.utils.unregister_class(MESH_OT_multi_bisect)
    bpy.types.VIEW3D_MT_edit_mesh.remove(add_multi_bisect_button)


if __name__ == "__main__":
    register()
