# 「3Dビュー」エリア > 「追加」メニュー > 「メッシュ」メニュー
# "3D View" Area > "Add" Menu > "Mesh" Menu

import bpy, bmesh
import math

################
# オペレーター #
################

class AddSphereOnlySquare(bpy.types.Operator):
	bl_idname = "mesh.add_sphere_only_square"
	bl_label = "Square Polygon Sphere"
	bl_description = "Add sphere mesh is composed only of quadrilateral polygon"
	bl_options = {'REGISTER', 'UNDO'}
	
	level = bpy.props.IntProperty(name="Number of Divisions", default=2, step=1, min=1, max=6, soft_min=1, soft_max=6)
	radius = bpy.props.FloatProperty(name="Radius (roughly)", default=1.0, step=10, precision=3, min=0.001, max=100, soft_min=0.001, soft_max=100)
	view_align = bpy.props.BoolProperty(name="Align View", default=False)
	location = bpy.props.FloatVectorProperty(name="Location", default=(0.0, 0.0, 0.0), step=10, precision=3, subtype='XYZ', min=-100, max=100, soft_min=-100, soft_max=100)
	rotation = bpy.props.IntVectorProperty(name="Rotation", default=(0, 0, 0), step=1, subtype='XYZ', min=-360, max=360, soft_min=-360, soft_max=360)
	enter_editmode = False
	
	def execute(self, context):
		isEdited = False
		if (context.mode == 'EDIT_MESH'):
			isEdited = True
			activeObj = context.active_object
		try:
			bpy.ops.object.mode_set(mode="OBJECT")
		except RuntimeError: pass
		if (self.view_align):
			bpy.ops.mesh.primitive_cube_add(radius=self.radius, view_align=True, location=self.location)
		else:
			rotation = self.rotation
			rotation = (math.radians(rotation[0]), math.radians(rotation[1]), math.radians(rotation[2]))
			bpy.ops.mesh.primitive_cube_add(radius=self.radius, location=self.location, rotation=rotation)
		context.active_object.name = "SquarePolySphere"
		subsurf = context.active_object.modifiers.new("temp", "SUBSURF")
		subsurf.levels = self.level
		bpy.ops.object.modifier_apply(apply_as="DATA", modifier=subsurf.name)
		bpy.ops.object.mode_set(mode="EDIT")
		bpy.ops.transform.tosphere(value=1)
		bpy.ops.object.mode_set(mode="OBJECT")
		if (isEdited and False):
			activeObj.select = True
			context.scene.objects.active = activeObj
			bpy.ops.object.join()
			bpy.ops.object.mode_set(mode="EDIT")
		return {'FINISHED'}

class AddVertexOnlyObject(bpy.types.Operator):
	bl_idname = "mesh.add_vertex_only_object"
	bl_label = "Only Vertex"
	bl_description = "Only 1 vertex meshes 3D adds to position of cursor"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		if (context.mode != 'OBJECT'):
			bpy.ops.object.mode_set(mode="OBJECT")
		me = bpy.data.meshes.new("Vertex")
		me.from_pydata([(0, 0, 0)], [], [])
		me.update()
		obj = bpy.data.objects.new("Vertex", me)
		obj.data = me
		bpy.context.scene.objects.link(obj)
		bpy.ops.object.select_all(action='DESELECT')
		obj.select = True
		bpy.context.scene.objects.active = obj
		obj.location = context.space_data.cursor_location[:]
		bpy.ops.object.mode_set(mode="EDIT")
		context.tool_settings.mesh_select_mode = (True, False, False)
		return {'FINISHED'}

class CreateVertexGroupSplits(bpy.types.Operator):
	bl_idname = "mesh.create_vertex_group_splits"
	bl_label = "Isolate by vertex groups"
	bl_description = "Create separate each part of vertex groups applied mesh group"
	bl_options = {'REGISTER', 'UNDO'}
	
	threshold = bpy.props.FloatProperty(name="Enabled Threshold", default=0.5, min=0, max=1, soft_min=0, soft_max=1, step=3, precision=2)
	delete_source = bpy.props.BoolProperty(name="Delete Source", default=False)
	
	@classmethod
	def poll(cls, context):
		if (context.mode == 'OBJECT'):
			for obj in context.selected_objects:
				if (obj.type == 'MESH'):
					if (len(obj.vertex_groups)):
						return True
		return False
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	
	def execute(self, context):
		for obj in context.selected_objects:
			obj.select = False
			if (obj.type != 'MESH'):
				continue
			me = obj.data
			bm = bmesh.new()
			bm.from_mesh(me)
			for vertex_group in obj.vertex_groups:
				new_verts = []
				new_verts_index = []
				new_faces = []
				for index, vert in enumerate(bm.verts):
					for group in me.vertices[index].groups:
						if (obj.vertex_groups[group.group].name == vertex_group.name):
							if (self.threshold <= group.weight):
								new_verts.append(vert.co[:])
								new_verts_index.append(index)
							break
				for face in bm.faces:
					for vert in face.verts:
						if (vert.index not in new_verts_index):
							break
					else:
						faces = []
						for vert in face.verts:
							faces.append(new_verts_index.index(vert.index))
						new_faces.append(faces)
				if (len(new_verts) and len(new_faces)):
					new_me = bpy.data.meshes.new(obj.name +":"+ vertex_group.name)
					new_me.from_pydata(new_verts, [], new_faces)
					new_obj = bpy.data.objects.new(obj.name +":"+ vertex_group.name, new_me)
					context.scene.objects.link(new_obj)
					new_obj.select = True
					context.scene.objects.active = new_obj
					new_obj.location = obj.location[:]
					new_obj.rotation_mode = obj.rotation_mode
					if (obj.rotation_mode == 'QUATERNION'):
						new_obj.rotation_quaternion = obj.rotation_quaternion[:]
					elif (obj.rotation_mode == 'AXIS_ANGLE'):
						new_obj.rotation_axis_angle = obj.rotation_axis_angle[:]
					else:
						new_obj.rotation_euler = obj.rotation_euler[:]
					new_obj.scale = obj.scale[:]
			if (self.delete_source):
				context.scene.objects.unlink(obj)
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	AddSphereOnlySquare,
	AddVertexOnlyObject,
	CreateVertexGroupSplits
]

def register():
	for cls in classes:
		bpy.utils.register_class(cls)

def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)


################
# メニュー追加 #
################

# メニューのオン/オフの判定
def IsMenuEnable(self_id):
	for id in bpy.context.preferences.addons["Blender-Scramble-Addon-master"].preferences.disabled_menu.split(','):
		if (id == self_id):
			return False
	else:
		return True

# メニューを登録する関数
def menu(self, context):
	if (IsMenuEnable(__name__.split('.')[-1])):
		self.layout.separator()
		self.layout.operator(AddVertexOnlyObject.bl_idname, icon='PLUGIN')
		self.layout.operator(AddSphereOnlySquare.bl_idname, icon='PLUGIN').location = context.space_data.cursor_location
		self.layout.separator()
		self.layout.operator(CreateVertexGroupSplits.bl_idname, icon='PLUGIN')
	if (context.preferences.addons["Blender-Scramble-Addon-master"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
