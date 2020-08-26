# 「3Dビュー」エリア > 「オブジェクト」モード > 「選択」メニュー
# "3D View" Area > "Object" Mode > "Select" Menu

import bpy, mathutils
import re

################
# オペレーター #
################

class SelectBoundBoxSize(bpy.types.Operator):
	bl_idname = "object.select_bound_box_size"
	bl_label = "Compare size and select objects"
	bl_description = "Select maximum objects larger or smaller objects"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		('LARGE', "Select Big", "", 1),
		('SMALL', "Select Small", "", 2),
		]
	mode = bpy.props.EnumProperty(items=items, name="Select Mode")
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
	select_type = bpy.props.EnumProperty(items=items, name="Select Type", default='MESH')
	threshold = bpy.props.FloatProperty(name="Selection Range", default=50, min=0, max=100, soft_min=0, soft_max=100, step=100, precision=1, subtype='PERCENTAGE')
	
	@classmethod
	def poll(cls, context):
		for obj in context.selectable_objects:
			return True
		return False
	
	def execute(self, context):
		context.scene.update()
		max_volume = -1
		min_volume = 999999999999999
		min_obj = None
		objs = []
		for obj in context.visible_objects:
			if (self.select_type != 'ALL'):
				if (obj.type != self.select_type):
					continue
			bound_box = obj.bound_box[:]
			bound_box0 = mathutils.Vector(bound_box[0][:])
			x = (bound_box0 - mathutils.Vector(bound_box[4][:])).length * obj.scale.x
			y = (bound_box0 - mathutils.Vector(bound_box[3][:])).length * obj.scale.y
			z = (bound_box0 - mathutils.Vector(bound_box[1][:])).length * obj.scale.z
			volume = x + y + z
			objs.append((obj, volume))
			if (max_volume < volume):
				max_volume = volume
			if (volume < min_volume):
				min_volume = volume
				min_obj = obj
		if (self.mode == 'LARGE'):
			threshold_volume = max_volume * (1.0 - (self.threshold * 0.01))
		elif (self.mode == 'SMALL'):
			threshold_volume = max_volume * (self.threshold * 0.01)
		for obj, volume in objs:
			if (self.mode == 'LARGE'):
				if (threshold_volume <= volume):
					obj.select = True
			elif (self.mode == 'SMALL'):
				if (volume <= threshold_volume):
					obj.select = True
		if (min_obj and self.mode == 'SMALL'):
			min_obj.select = True
		return {'FINISHED'}

class UnselectUnactiveObjects(bpy.types.Operator):
	bl_idname = "object.unselect_unactive_objects"
	bl_label = "Non-active to Non-select"
	bl_description = "Uncheck everything except for active object"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			return True
		return False
	
	def execute(self, context):
		for ob in bpy.data.objects:
			ob.select = False
		context.active_object.select = True
		return {'FINISHED'}

############################
# オペレーター(関係で選択) #
############################

class SelectGroupedName(bpy.types.Operator):
	bl_idname = "object.select_grouped_name"
	bl_label = "Select object same name"
	bl_description = "Select visible object of active object with same name, such as (X.001 X X.002)"
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
		for obj in context.selectable_objects:
			if (re.search('^'+name_base+r'\.\d+$', obj.name) or name_base == obj.name):
				obj.select = True
		return {'FINISHED'}

class SelectGroupedMaterial(bpy.types.Operator):
	bl_idname = "object.select_grouped_material"
	bl_label = "Select objects of same material structure"
	bl_description = "Select active object material structure and same visible objects"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			return True
		return False
	
	def execute(self, context):
		def GetMaterialList(slots):
			list = []
			for slot in slots:
				if (slot.material):
					list.append(slot.material.name)
			return list
		activeMats = GetMaterialList(context.active_object.material_slots)
		if (0 < len(activeMats)):
			for obj in context.selectable_objects:
				if (activeMats == GetMaterialList(obj.material_slots)):
					obj.select = True
		return {'FINISHED'}

class SelectGroupedModifiers(bpy.types.Operator):
	bl_idname = "object.select_grouped_modifiers"
	bl_label = "Select same modifier structure object"
	bl_description = "Select same modifier of active objects visible objects"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			return True
		return False
	
	def execute(self, context):
		def GetModifiersString(obj):
			str = ""
			for mod in obj.modifiers:
				str = str + mod.type
			return str
		active_modifiers = GetModifiersString(context.active_object)
		active_type = context.active_object.type
		for obj in context.selectable_objects:
			if (GetModifiersString(obj) == active_modifiers and active_type == obj.type):
				obj.select= True
		return {'FINISHED'}

class SelectGroupedSubsurfLevel(bpy.types.Operator):
	bl_idname = "object.select_grouped_subsurf_level"
	bl_label = "Select same subsurf level object"
	bl_description = "Select Subsurf levels of active objects have same visible objects"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			return True
		return False
	
	def execute(self, context):
		def GetSubsurfLevel(obj):
			level = 0
			for mod in obj.modifiers:
				if (mod.type == 'SUBSURF'):
					level += mod.levels
			return level
		active_subsurf_level = GetSubsurfLevel(context.active_object)
		active_type = context.active_object.type
		for obj in context.selectable_objects:
			if (GetSubsurfLevel(obj) == active_subsurf_level and active_type == obj.type):
				obj.select= True
		return {'FINISHED'}

class SelectGroupedArmatureTarget(bpy.types.Operator):
	bl_idname = "object.select_grouped_armature_target"
	bl_label = "Select objects that transform in same armature"
	bl_description = "Select visible objects are transformed in an active object with same armature"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			return True
		return False
	
	def execute(self, context):
		def GetArmatureTarget(obj):
			target = []
			for mod in obj.modifiers:
				if (mod.type == 'ARMATURE'):
					if (mod.object):
						target.append(mod.object.name)
					else:
						target.append("")
			return set(target)
		active_armature_targets = GetArmatureTarget(context.active_object)
		if (len(active_armature_targets) == 0):
			self.report(type={"ERROR"}, message="Armtuamodifaia has no active object")
			return {"CANCELLED"}
		active_type = context.active_object.type
		for obj in context.selectable_objects:
			if (len(GetArmatureTarget(obj).intersection(active_armature_targets)) == len(active_armature_targets) and active_type == obj.type):
				obj.select= True
		return {'FINISHED'}

class SelectGroupedSizeThan(bpy.types.Operator):
	bl_idname = "object.select_grouped_size_than"
	bl_label = "Compare size and select objects"
	bl_description = "Greater than active object, or select additional small objects"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		('LARGER', "Select Bigger", "", 1),
		('SMALLER', "Select Smaller", "", 2),
		]
	mode = bpy.props.EnumProperty(items=items, name="Select Mode")
	select_same_size = bpy.props.BoolProperty(name="Select Same Size", default=True)
	items = [
		('MESH', "Mesh", "", 1),
		('CURVE', "Curve", "", 2),
		('SURFACE', "Surface", "", 3),
		('META', "Metaballs", "", 4),
		('FONT', "Text", "", 5),
		('ARMATURE', "Armature", "", 6),
		('LATTICE', "Lattice", "", 7),
		('ALL', "All", "", 8),
		('SAME', "Same Type", "", 9),
		]
	select_type = bpy.props.EnumProperty(items=items, name="Select Type", default='SAME')
	size_multi = bpy.props.FloatProperty(name="Standard Size Offset", default=1.0, min=0, max=10, soft_min=0, soft_max=10, step=10, precision=3)
	
	@classmethod
	def poll(cls, context):
		if context.active_object:
			return True
		return False
	
	def execute(self, context):
		def GetSize(obj):
			bound_box = obj.bound_box[:]
			bound_box0 = mathutils.Vector(bound_box[0][:])
			bound_box0 = mathutils.Vector(bound_box[0][:])
			x = (bound_box0 - mathutils.Vector(bound_box[4][:])).length * obj.scale.x
			y = (bound_box0 - mathutils.Vector(bound_box[3][:])).length * obj.scale.y
			z = (bound_box0 - mathutils.Vector(bound_box[1][:])).length * obj.scale.z
			return x + y + z
		
		active_obj = context.active_object
		if (not active_obj):
			self.report(type={'ERROR'}, message="There is no active object")
			return {'CANCELLED'}
		context.scene.update()
		active_obj_size = GetSize(active_obj) * self.size_multi
		for obj in context.selectable_objects:
			if (self.select_type != 'ALL'):
				if (self.select_type == 'SAME'):
					if (obj.type != active_obj.type):
						continue
				else:
					if (obj.type != self.select_type):
						continue
			size = GetSize(obj)
			if (self.mode == 'LARGER'):
				if (active_obj_size < size):
					obj.select = True
			elif (self.mode == 'SMALLER'):
				if (size < active_obj_size):
					obj.select = True
			if (self.select_same_size):
				if (active_obj_size == size):
					obj.select = True
		return {'FINISHED'}

##########################
# オペレーター(メッシュ) #
##########################

class SelectMeshFaceOnly(bpy.types.Operator):
	bl_idname = "object.select_mesh_face_only"
	bl_label = "Select face exist mesh"
	bl_description = "Select mesh more than one face"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		for obj in context.selectable_objects:
			if (obj.type == 'MESH'):
				return True
		return False
	
	def execute(self, context):
		for obj in context.selectable_objects:
			if (obj.type == 'MESH'):
				me = obj.data
				if (0 < len(me.polygons)):
					obj.select = True
		return {'FINISHED'}

class SelectMeshEdgeOnly(bpy.types.Operator):
	bl_idname = "object.select_mesh_edge_only"
	bl_label = "Select edge only mesh"
	bl_description = "Terms, select only side mesh"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		for obj in context.selectable_objects:
			if (obj.type == 'MESH'):
				return True
		return False
	
	def execute(self, context):
		for obj in context.selectable_objects:
			if (obj.type == 'MESH'):
				me = obj.data
				if (len(me.polygons) == 0 and 0 < len(me.edges)):
					obj.select = True
		return {'FINISHED'}

class SelectMeshVertexOnly(bpy.types.Operator):
	bl_idname = "object.select_mesh_vertex_only"
	bl_label = "Select only vertices of mesh"
	bl_description = "Surfaces and edges, select mesh vertices only"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		for obj in context.selectable_objects:
			if (obj.type == 'MESH'):
				return True
		return False
	
	def execute(self, context):
		for obj in context.selectable_objects:
			if (obj.type == 'MESH'):
				me = obj.data
				if (len(me.polygons) == 0 and len(me.edges) == 0 and 0 < len(me.vertices)):
					obj.select = True
		return {'FINISHED'}

class SelectMeshNone(bpy.types.Operator):
	bl_idname = "object.select_mesh_none"
	bl_label = "Select mesh even non vertex"
	bl_description = "Surface and edge and select mesh object vertex is not empty"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		for obj in context.selectable_objects:
			if (obj.type == 'MESH'):
				return True
		return False
	
	def execute(self, context):
		for obj in context.selectable_objects:
			if (obj.type == 'MESH'):
				me = obj.data
				if (len(me.polygons) == 0 and len(me.edges) == 0 and len(me.vertices) == 0):
					obj.select = True
		return {'FINISHED'}

################
# サブメニュー #
################

class SelectGroupedEX(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_select_object_grouped_ex"
	bl_label = "Select by relation (Extra)"
	bl_description = "Select all visible objects grouped by properties"
	
	def draw(self, context):
		column = self.layout.column()
		column.operator("object.select_grouped", text="Child").type = 'CHILDREN_RECURSIVE'
		column.operator("object.select_grouped", text="Immediate Children").type = 'CHILDREN'
		column.operator("object.select_grouped", text="Parent").type = 'PARENT'
		column.operator("object.select_grouped", text="Brother").type = 'SIBLINGS'
		column.operator("object.select_grouped", text="Type").type = 'TYPE'
		column.operator("object.select_grouped", text="Layer").type = 'LAYER'
		column.operator("object.select_grouped", text="Group").type = 'GROUP'
		column.operator("object.select_grouped", text="Path").type = 'PASS'
		column.operator("object.select_grouped", text="Color").type = 'COLOR'
		column.operator("object.select_grouped", text="Property").type = 'PROPERTIES'
		column.operator("object.select_grouped", text="Keying Set").type = 'KEYINGSET'
		column.operator("object.select_grouped", text="Lamp Type").type = 'LAMP_TYPE'
		column.separator()
		column.operator(SelectGroupedSizeThan.bl_idname, text="Bigger Than", icon='PLUGIN').mode = 'LARGER'
		column.operator(SelectGroupedSizeThan.bl_idname, text="Smaller Than", icon='PLUGIN').mode = 'SMALLER'
		column.separator()
		column.operator(SelectGroupedName.bl_idname, text="Object Name", icon='PLUGIN')
		column.operator(SelectGroupedMaterial.bl_idname, text="Material", icon='PLUGIN')
		column.operator(SelectGroupedModifiers.bl_idname, text="Modifier", icon='PLUGIN')
		column.operator(SelectGroupedSubsurfLevel.bl_idname, text="Subsurf Level", icon='PLUGIN')
		column.operator(SelectGroupedArmatureTarget.bl_idname, text="Same Armature Transform", icon='PLUGIN')
		if (not context.object):
			column.enabled = False

class SelectMesh(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_select_object_mesh"
	bl_label = "Select characteristics of mesh"
	bl_description = "Ability to select mesh object visualization menu"
	
	def draw(self, context):
		self.layout.operator(SelectMeshFaceOnly.bl_idname, text="Face Only", icon='PLUGIN')
		self.layout.operator(SelectMeshEdgeOnly.bl_idname, text="Edge Only", icon='PLUGIN')
		self.layout.operator(SelectMeshVertexOnly.bl_idname, text="Only Vertex", icon='PLUGIN')
		self.layout.operator(SelectMeshNone.bl_idname, text="Without Even Vertex", icon='PLUGIN')

################
# クラスの登録 #
################

classes = [
	SelectBoundBoxSize,
	UnselectUnactiveObjects,
	SelectGroupedName,
	SelectGroupedMaterial,
	SelectGroupedModifiers,
	SelectGroupedSubsurfLevel,
	SelectGroupedArmatureTarget,
	SelectGroupedSizeThan,
	SelectMeshFaceOnly,
	SelectMeshEdgeOnly,
	SelectMeshVertexOnly,
	SelectMeshNone,
	SelectGroupedEX,
	SelectMesh
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
		self.layout.operator(UnselectUnactiveObjects.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(SelectBoundBoxSize.bl_idname, text="Select Small", icon='PLUGIN').mode = 'SMALL'
		self.layout.operator(SelectBoundBoxSize.bl_idname, text="Select Big", icon='PLUGIN').mode = 'LARGE'
		self.layout.separator()
		self.layout.menu(SelectMesh.bl_idname, icon='PLUGIN')
		self.layout.menu(SelectGroupedEX.bl_idname, icon='PLUGIN')
	if (context.preferences.addons["Blender-Scramble-Addon-master"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
