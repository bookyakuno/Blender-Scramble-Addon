# 「3Dビュー」エリア > 「オブジェクト」モード > 「オブジェクト」メニュー > 「表示/隠す」メニュー
# "3D View" Area > "Object" Mode > "Object" Menu > "Show/Hide" Menu

import bpy
from bpy.props import *
import bpy.ops

################
# オペレーター #
################

class HideViewClearUnselect(bpy.types.Operator):
	bl_idname = "object.hide_view_clear_unselect"
	bl_label = "Show Hidden (non-select)"
	bl_description = "Does not display objects were hidden again, select"
	bl_options = {'REGISTER', 'UNDO'}

	show_col : BoolProperty(name="show hided collections", default=False)

	def flatten(self, layer_collection):
		flat_hide = []
		for coll in layer_collection.children:
			if not coll.exclude and not coll.hide_viewport:
				if len(coll.children) > 0:
					flat_hide += self.flatten(coll)
			elif not coll.exclude and coll.hide_viewport:
				flat_hide.append(coll)
		return flat_hide

	def execute(self, context):
		master_col = context.view_layer.layer_collection
		if self.show_col:
			views = [c for c in master_col.children if not c.exclude and not c.hide_viewport]
			hides = [c for c in master_col.children if not c.exclude and c.hide_viewport]
			for col in views:
				if len(col.children) > 0:
					hides += self.flatten(col)
			for col in hides:
				col.hide_viewport = False
		pre_selectable_objects = []
		for ob in context.selectable_objects:
			pre_selectable_objects.append(ob.name)
		bpy.ops.object.hide_view_clear()
		for ob in context.selectable_objects:
			if ob.name not in pre_selectable_objects:
				ob.select_set(False)
		return {'FINISHED'}

class InvertHide(bpy.types.Operator):
	bl_idname = "object.invert_hide"
	bl_label = "Invert Show/Hide"
	bl_description = "Flips object\'s view state and non-State"
	bl_options = {'REGISTER', 'UNDO'}

	method : EnumProperty(name="Collections", items=[
		("IGNORE","Not Invert","Only Objects are changed",1),
		("CHILD","Invert Nested","Collections in collection are changed",2),
		("PARENT","Invert Parent","Collections in 'Scene Collection' are changed",3)])
	
	def flatten(self, layer_collection):
		flat_view = []
		for coll in layer_collection.children:
			if not coll.exclude and not coll.hide_viewport:
				if len(coll.children) > 0:
					flat_view.append(coll)
					flat_view += self.flatten(coll)
				else:
					flat_view.append(coll)
		return flat_view

	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True
		layout.prop(self, 'method', expand=True)

	def execute(self, context):
		objs = []
		master_col = context.view_layer.layer_collection
		for obj in master_col.collection.objects:
			obj.hide_set(not obj.hide_get())
		if self.method == 'IGNORE':
			views = self.flatten(master_col)
			for col in views:
				for obj in col.collection.objects:
					obj.hide_set(not obj.hide_get())
		else: 
			for col in master_col.children:
				if self.method == 'PARENT':
					col.hide_viewport = not col.hide_viewport
				elif self.method == 'CHILD':
					if not col.exclude and not col.hide_viewport:
						for obj in col.collection.objects:
							 obj.hide_set(not obj.hide_get())
						for child in col.children:
							if not child.exclude:
								child.hide_viewport = not child.hide_viewport
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
	type : EnumProperty(items=items, name="Hide Object Type")
	is_except : BoolProperty(name="Except designated", default=False, options={'HIDDEN'})

	def execute(self, context):
		for obj in context.selectable_objects:
			if not self.is_except and (obj.type == self.type):
				obj.hide_set(True)
			elif self.is_except and (not obj.type == self.type):
				obj.hide_set(True)
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	HideViewClearUnselect,
	InvertHide,
	HideOnlyType
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
		self.layout.operator(HideViewClearUnselect.bl_idname, icon='PLUGIN')
		self.layout.operator(InvertHide.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(HideOnlyType.bl_idname, icon='PLUGIN').is_except = False
		self.layout.operator(HideOnlyType.bl_idname, text="Hide Objects (Except Specific Type)", icon='PLUGIN').is_except = True
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
