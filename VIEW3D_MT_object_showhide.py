# 「3Dビュー」エリア > 「オブジェクト」モード > 「オブジェクト」メニュー > 「表示/隠す」メニュー
# "3D View" Area > "Object" Mode > "Object" Menu > "Show/Hide" Menu

import bpy

################
# オペレーター #
################

class hide_view_clear_unselect(bpy.types.Operator):
	bl_idname = "object.hide_view_clear_unselect"
	bl_label = "Show Hidden (non-select)"
	bl_description = "Does not display objects were hidden again, select"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		pre_selectable_objects = []
		for ob in context.selectable_objects:
			pre_selectable_objects.append(ob.name)
		bpy.ops.object.hide_view_clear()
		for ob in context.selectable_objects:
			if ob.name not in pre_selectable_objects:
				ob.select = False
		return {'FINISHED'}

class InvertHide(bpy.types.Operator):
	bl_idname = "object.invert_hide"
	bl_label = "Invert Show/Hide"
	bl_description = "Flips object\'s view state and non-State"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		objs = []
		for obj in bpy.data.objects:
			for i in range(len(bpy.context.scene.layers)):
				if (bpy.context.scene.layers[i] and obj.layers[i]):
					for obj2 in objs:
						if (obj.name == obj2.name):
							break
					else:
						objs.append(obj)
		for obj in objs:
			obj.hide = not obj.hide
		return {'FINISHED'}

class HideOnlyType(bpy.types.Operator):
	bl_idname = "object.hide_only_mesh"
	bl_label = "Hide only type of objects"
	bl_description = "Hides object of specific type are displayed"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		("MESH", "Mesh", "", 1),
		("CURVE", "Curve", "", 2),
		("SURFACE", "Surface", "", 3),
		("META", "Metaballs", "", 4),
		("FONT", "Text", "", 5),
		("ARMATURE", "Armature", "", 6),
		("LATTICE", "Lattice", "", 7),
		("EMPTY", "Empty", "", 8),
		("CAMERA", "Camera", "", 9),
		("LAMP", "Lamp", "", 10),
		("SPEAKER", "Speaker", "", 11),
		]
	type = bpy.props.EnumProperty(items=items, name="Hide Object Type")
	
	def execute(self, context):
		for obj in context.selectable_objects:
			if (obj.type == self.type):
				obj.hide = True
		return {'FINISHED'}

class HideExceptType(bpy.types.Operator):
	bl_idname = "object.hide_except_mesh"
	bl_label = "Hide except type of objects"
	bl_description = "Hides object non-specific type that is displayed"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		("MESH", "Mesh", "", 1),
		("CURVE", "Curve", "", 2),
		("SURFACE", "Surface", "", 3),
		("META", "Metaballs", "", 4),
		("FONT", "Text", "", 5),
		("ARMATURE", "Armature", "", 6),
		("LATTICE", "Lattice", "", 7),
		("EMPTY", "Empty", "", 8),
		("CAMERA", "Camera", "", 9),
		("LAMP", "Lamp", "", 10),
		("SPEAKER", "Speaker", "", 11),
		]
	type = bpy.props.EnumProperty(items=items, name="Extract Object Type")
	
	def execute(self, context):
		for obj in context.selectable_objects:
			if (obj.type != self.type):
				obj.hide = True
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	hide_view_clear_unselect,
	InvertHide,
	HideOnlyType,
	HideExceptType
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
		self.layout.operator(hide_view_clear_unselect.bl_idname, icon='PLUGIN')
		self.layout.operator(InvertHide.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(HideOnlyType.bl_idname, icon='PLUGIN')
		self.layout.operator(HideExceptType.bl_idname, icon='PLUGIN')
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
