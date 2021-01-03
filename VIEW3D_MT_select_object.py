# 「3Dビュー」エリア > 「オブジェクト」モード > 「選択」メニュー
# "3D View" Area > "Object" Mode > "Select" Menu

import bpy, mathutils
import re
from bpy.props import *

################
# オペレーター #
################

class SelectBoundBoxSize(bpy.types.Operator):
	bl_idname = "object.select_bound_box_size"
	bl_label = "Select (Object Size)"
	bl_description = "Select objects based on their size"
	bl_options = {'REGISTER', 'UNDO'}

	mode : EnumProperty(name="Select Mode", items=[
		('MORE_L', "Larger than Active", "", 1),
		('MORE_S', "Smaller than Active", "", 2),
		('MOST_L', "From Largest", "", 3),
		('MOST_S', "From Smallest", "", 4)])
	items = [
		('MESH', "Mesh", "", 1),
		('CURVE', "Curve", "", 2),
		('SURFACE', "Surface", "", 3),
		('META', "Metaballs", "", 4),
		('FONT', "Text", "", 5),
		('ARMATURE', "Armature", "", 6),
		('LATTICE', "Lattice", "", 7),
		('ALL', "All", "", 8),
		]
	select_type : EnumProperty(items=items, name="Type", default='MESH')
	number : IntProperty(name="Number", default=1, min=1, max=100, soft_min=1, soft_max=100)

	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True
		for p in ['mode', 'select_type', 'number']:
			row = layout.row()
			row.enabled = not (p == 'number' and self.mode not in ['MOST_L', 'MOST_S'])
			row.prop(self, p)

	def get_bbox_size(self, item):
		bb = item.bound_box
		origin = mathutils.Vector(bb[0])
		x = (origin-mathutils.Vector(bb[4])).length * item.scale.x
		y = (origin-mathutils.Vector(bb[3])).length * item.scale.y
		z = (origin-mathutils.Vector(bb[1])).length * item.scale.z
		return x+y+z

	def execute(self, context):
		if self.select_type == 'ALL':
			targets = context.visible_objects
		else:
			targets = [ob for ob in context.visible_objects if ob.type== self.select_type]
		sizes = [[ob, self.get_bbox_size(ob)] for ob in targets]
		sorted_targets = [x[0] for x in sorted(sizes, key=lambda x:x[1])]
		if self.mode in ['MORE_L', 'MORE_S']:
			if not context.active_object:
				return {'CANCELLED'}
			active_idx = sorted_targets.index(context.active_object)
			if self.mode == 'MORE_L':
				results = sorted_targets[active_idx:]
			elif self.mode == 'MORE_S':
				results = sorted_targets[:active_idx]
		elif self.mode in ['MOST_L', 'MOST_S']:
			if self.mode == 'MOST_L':
				results = sorted_targets[self.number*-1:]
				context.active_object.select_set(False)
			elif self.mode == 'MOST_S':
				results = sorted_targets[:self.number]
				context.active_object.select_set(False)
		for ob in results:
			ob.select_set(True)
		return {'FINISHED'}

############################
# オペレーター(関係で選択) #
############################

class SelectGroupedName(bpy.types.Operator):
	bl_idname = "object.select_grouped_name"
	bl_label = "Objects Sharing Same Name"
	bl_description = "Select objects which names are same as active object except dot-number"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if context.active_object:
			return True
		return False

	def execute(self, context):
		name_base = context.active_object.name
		if (re.search(r'\.\d+$', name_base)):
			name_base = re.search(r'^(.*)\.\d+$', name_base).groups()[0]
		for obj in context.visible_objects:
			if (re.search('^'+name_base+r'\.\d+$', obj.name) or name_base == obj.name):
				obj.select_set(True)
		return {'FINISHED'}

class SelectGroupedMaterial(bpy.types.Operator):
	bl_idname = "object.select_grouped_material"
	bl_label = "Objects All Materials are Same"
	bl_description = "Select objects which have exactly the same materials as active object"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if context.active_object:
			return True
		return False

	def execute(self, context):
		activeMats = [s.material for s in context.active_object.material_slots]
		if activeMats:
			for obj in context.visible_objects:
				obj_mats = [s.material for s in obj.material_slots]
				if set(activeMats) == set(obj_mats):
					obj.select_set(True)
		return {'FINISHED'}

class SelectGroupedModifiers(bpy.types.Operator):
	bl_idname = "object.select_grouped_modifiers"
	bl_label = "Objects All Modifiers are Same"
	bl_description = "Select objects which have exactly the same modifiers as active object"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if context.active_object:
			return True
		return False

	def execute(self, context):
		active_modis = [mod.type for mod in context.active_object.modifiers]
		for obj in context.visible_objects:
				obj_modis = [mod.type for mod in obj.modifiers]
				if set(active_modis) == set(obj_modis):
					obj.select_set(True)
		return {'FINISHED'}

class SelectGroupedSubsurfLevel(bpy.types.Operator):
	bl_idname = "object.select_grouped_subsurf_level"
	bl_label = "Objects with Same Number of Subdivisions"
	bl_description = "Select objects which use same number of subdivisions of subdivision surface modifier as active object"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if context.active_object:
			if 'SUBSURF' in [mod.type for mod in context.active_object.modifiers]:
				return True
		return False

	def execute(self, context):
		for mod in context.active_object.modifiers:
			if (mod.type == 'SUBSURF'):
				active_level = mod.levels
		for obj in context.visible_objects:
			mod_types = [mod.type for mod in obj.modifiers]
			try:
				obj_level = obj.modifiers[mod_types.index('SUBSURF')].levels
				if active_level == obj_level:
					obj.select_set(True)
			except ValueError:
				continue
		return {'FINISHED'}

class SelectGroupedArmatureTarget(bpy.types.Operator):
	bl_idname = "object.select_grouped_armature_target"
	bl_label = "Objects Referring Same Armature"
	bl_description = "Select objects which refer the same armature object as active object"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if context.active_object:
			if 'ARMATURE' in [mod.type for mod in context.active_object.modifiers]:
				return True
		return False

	def execute(self, context):
		for mod in context.active_object.modifiers:
			if (mod.type == 'ARMATURE'):
				active_target = mod.object
		for obj in context.visible_objects:
			mod_types = [mod.type for mod in obj.modifiers]
			try:
				obj_target = obj.modifiers[mod_types.index('ARMATURE')].object
				if active_target == obj_target:
					obj.select_set(True)
			except ValueError:
				continue
		return {'FINISHED'}

##########################
# オペレーター(メッシュ) #
##########################

class SelectMeshFaceOnly(bpy.types.Operator):
	bl_idname = "object.select_mesh_face_only"
	bl_label = "Mesh with Face"
	bl_description = "Select mesh more than one face"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		for obj in context.selectable_objects:
			if (obj.type == 'MESH'):
				me = obj.data
				if (0 < len(me.polygons)):
					obj.select_set(True)
		return {'FINISHED'}

class SelectMeshEdgeOnly(bpy.types.Operator):
	bl_idname = "object.select_mesh_edge_only"
	bl_label = "Mesh with Only Edges"
	bl_description = "Select objects which meshes have only edges"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		for obj in context.selectable_objects:
			if (obj.type == 'MESH'):
				me = obj.data
				if (len(me.polygons) == 0 and 0 < len(me.edges)):
					obj.select_set(True)
		return {'FINISHED'}

class SelectMeshVertexOnly(bpy.types.Operator):
	bl_idname = "object.select_mesh_vertex_only"
	bl_label = "Mesh with Only Vertices"
	bl_description = "Select objects which meshes have only vertices"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		for obj in context.selectable_objects:
			if (obj.type == 'MESH'):
				me = obj.data
				if (len(me.polygons) == 0 and len(me.edges) == 0 and 0 < len(me.vertices)):
					obj.select_set(True)
		return {'FINISHED'}

class SelectMeshNone(bpy.types.Operator):
	bl_idname = "object.select_mesh_none"
	bl_label = "Mesh with No Vertex"
	bl_description = "Select objects which meshes have no vertex"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		for obj in context.selectable_objects:
			if (obj.type == 'MESH'):
				me = obj.data
				if (len(me.polygons) == 0 and len(me.edges) == 0 and len(me.vertices) == 0):
					obj.select_set(True)
		return {'FINISHED'}

################
# サブメニュー #
################

class SelectGroupedEX(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_select_object_grouped_ex"
	bl_label = "Select Grouped (Extra)"

	def draw(self, context):
		for item in bpy.ops.object.select_grouped.get_rna_type().properties["type"].enum_items:
			self.layout.operator('object.select_grouped', text=item.name).type = item.identifier
		self.layout.separator()
		self.layout.operator(SelectGroupedName.bl_idname, icon='PLUGIN')
		self.layout.operator(SelectGroupedMaterial.bl_idname, icon='PLUGIN')
		self.layout.operator(SelectGroupedModifiers.bl_idname, icon='PLUGIN')
		self.layout.operator(SelectGroupedSubsurfLevel.bl_idname, icon='PLUGIN')
		self.layout.operator(SelectGroupedArmatureTarget.bl_idname, icon='PLUGIN')

class SelectMesh(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_select_object_mesh"
	bl_label = "Select (Special Mesh)"

	def draw(self, context):
		self.layout.operator(SelectMeshFaceOnly.bl_idname, icon='PLUGIN')
		self.layout.operator(SelectMeshEdgeOnly.bl_idname, icon='PLUGIN')
		self.layout.operator(SelectMeshVertexOnly.bl_idname, icon='PLUGIN')
		self.layout.operator(SelectMeshNone.bl_idname, icon='PLUGIN')

class SelectSizeMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_select_bound_box_size"
	bl_label = "Select (Object Size)"

	def draw(self, context):
		for ps in [
				('MORE_L', "Larger than Active"),
				('MORE_S', "Smaller than Active"),
				('MOST_L', "From Largest"),
				('MOST_S', "From Smallest")]:
			self.layout.operator(SelectBoundBoxSize.bl_idname, icon='PLUGIN', text=ps[1]).mode = ps[0]

################
# クラスの登録 #
################

classes = [
	SelectBoundBoxSize,
	SelectGroupedName,
	SelectGroupedMaterial,
	SelectGroupedModifiers,
	SelectGroupedSubsurfLevel,
	SelectGroupedArmatureTarget,
	SelectMeshFaceOnly,
	SelectMeshEdgeOnly,
	SelectMeshVertexOnly,
	SelectMeshNone,
	SelectGroupedEX,
	SelectMesh,
	SelectSizeMenu
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
	for id in bpy.context.preferences.addons[__name__.partition('.')[0]].preferences.disabled_menu.split(','):
		if (id == self_id):
			return False
	else:
		return True

# メニューを登録する関数
def menu(self, context):
	if (IsMenuEnable(__name__.split('.')[-1])):
		self.layout.separator()
		self.layout.menu(SelectGroupedEX.bl_idname, icon='PLUGIN')
		self.layout.menu(SelectSizeMenu.bl_idname, icon='PLUGIN')
		self.layout.menu(SelectMesh.bl_idname, icon='PLUGIN')
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
