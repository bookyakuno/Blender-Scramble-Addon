# 「3Dビュー」エリア > 「メッシュ編集」モード > 「Ctrl + V」キー
# "3D View" Area > "Mesh Editor" Mode > "Ctrl + V" Key

import bpy
from bpy.props import *

################
# オペレーター #
_STORE_ITEMS = [] #保存用グローバル変数：EnumPropertyの動的なitems作成におけるバグへの対処用
################

class CellMenuSeparateEX(bpy.types.Operator):
	bl_idname = "mesh.cell_menu_separate_ex"
	bl_label = "Separate (Advance)"
	bl_description = "Isolate to another object of call extended menu"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		bpy.ops.wm.call_menu(name=SeparateEXMenu.bl_idname)
		return {'FINISHED'}

class SeparateSelectedEX(bpy.types.Operator):
	bl_idname = "mesh.separate_selected_ex"
	bl_label = "Selected (Activate Isolated-side)"
	bl_description = "After \"in choice of separation\" enters edit mode for separation side"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		objs = [obj.name for obj in context.selectable_objects]
		bpy.ops.mesh.separate(type='SELECTED')
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		for obj in context.selectable_objects:
			if (not obj.name in objs):
				obj.select_set(True)
				bpy.context.view_layer.objects.active = obj
				break
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.select_all(action='SELECT')
		return {'FINISHED'}

class DuplicateNewParts(bpy.types.Operator):
	bl_idname = "mesh.duplicate_new_parts"
	bl_label = "Duplicate Selected parts and to new object"
	bl_description = "Enters edit mode, replication and selection to new object from"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		objs = []
		for obj in context.selectable_objects:
			objs.append(obj.name)
		bpy.ops.mesh.duplicate()
		bpy.ops.mesh.separate(type='SELECTED')
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		for obj in context.selectable_objects:
			if (not obj.name in objs):
				obj.select_set(True)
				bpy.context.view_layer.objects.active = obj
				break
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.select_all(action='SELECT')
		return {'FINISHED'}

class QuickShrinkwrap(bpy.types.Operator):
	bl_idname = "mesh.quick_shrinkwrap"
	bl_label = "Quick Shrinkwrap"
	bl_description = "Another one you mesh selected vertices pettanko!, glue"
	bl_options = {'REGISTER', 'UNDO'}

	items = [
		('NEAREST_SURFACEPOINT', "Closest Surface Point", "", 1),
		('PROJECT', "Projection", "", 2),
		('NEAREST_VERTEX', "Nearest Vertex", "", 3),
		]
	wrap_method : EnumProperty(items=items, name="Mode", default='PROJECT')
	offset : FloatProperty(name="Offset", default=0.0, min=-10, max=10, soft_min=-10, soft_max=10, step=1, precision=5)

	@classmethod
	def poll(cls, context):
		if (len(context.selected_objects) != 2):
			return False
		for obj in context.selected_objects:
			if (obj.type != 'MESH'):
				return False
		return True

	def execute(self, context):
		active_obj = context.active_object
		pre_mode = active_obj.mode
		bpy.ops.object.mode_set(mode='OBJECT')
		for obj in context.selected_objects:
			if (active_obj.name != obj.name):
				target_obj = obj
				break
		new_vg = active_obj.vertex_groups.new(name="TempGroup")
		selected_verts = [v.index for v in active_obj.data.vertices if v.select]
		if (len(selected_verts) <= 0):
			bpy.ops.object.mode_set(mode=pre_mode)
			self.report(type={'ERROR'}, message="One run, select vertex more than")
			return {'CANCELLED'}
		new_vg.add(selected_verts, 1.0, 'REPLACE')
		new_mod = active_obj.modifiers.new("temp", 'SHRINKWRAP')
		for i in range(len(active_obj.modifiers)):
			bpy.ops.object.modifier_move_up(modifier=new_mod.name)
		new_mod.target = target_obj
		new_mod.offset = self.offset
		new_mod.vertex_group = new_vg.name
		new_mod.wrap_method = self.wrap_method
		if (self.wrap_method == 'PROJECT'):
			new_mod.use_negative_direction = True
		bpy.ops.object.modifier_apply(modifier=new_mod.name)
		active_obj.vertex_groups.remove(new_vg)
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

class SeparateMaterialEX(bpy.types.Operator):
	bl_idname = "mesh.separate_material_ex"
	bl_label = "Separate by One Material"
	bl_description = "Separate specific-material-assigned part to another object, and switch to the object's Edit mode"
	bl_options = {'REGISTER', 'UNDO'}

	def item_callback(self, context):
		mat_names = [mat.name for mat in bpy.context.active_object.data.materials]
		if not self.is_stashed:
			_STORE_ITEMS.clear()
			for idx, nam in enumerate(mat_names):
				_STORE_ITEMS.append((nam, nam, "", idx))
				self.is_stashed = True
		#print(_STORE_ITEMS[0])#作成したリストの要素がうまく認識されないバグ?への一応の対処
		return _STORE_ITEMS

	target_mat : EnumProperty(items=item_callback, name="Material to Separate")
	is_stashed : BoolProperty(name="Mats' list exists", default=False, options={'HIDDEN'})

	def execute(self, context):
		target_mat = context.active_object.data.materials[self.target_mat]
		bpy.ops.mesh.separate(type='MATERIAL')
		bpy.ops.object.mode_set(mode='OBJECT')		
		selected_objs = context.selected_objects[:]
		not_targets = [obj for obj in selected_objs if obj.data.materials[0] != target_mat]
		target_obj = list(set(selected_objs) - set(not_targets))[0]
		target_obj.select_set(False)
		context.view_layer.objects.active = not_targets[0]
		bpy.ops.object.join()
		bpy.context.active_object.select_set(False)
		target_obj.select_set(True)
		context.view_layer.objects.active = target_obj
		bpy.ops.object.mode_set(mode='EDIT')
		return {'FINISHED'}

class SeparateLooseEX(bpy.types.Operator):
	bl_idname = "mesh.separate_loose_ex"
	bl_label = "By Non-Selected Loose Parts"
	bl_description = "Separate each not-selected / selected isolated part to another object"
	bl_options = {'REGISTER', 'UNDO'}

	sep_selected : BoolProperty(name="Separate selected", default=False)

	def execute(self, context):
		orig_obj = context.active_object
		bpy.ops.mesh.select_linked()
		if not self.sep_selected:
			bpy.ops.mesh.select_all(action='INVERT')
		bpy.ops.mesh.separate(type='SELECTED')
		bpy.ops.object.mode_set(mode='OBJECT')
		selected_set = set(context.selected_objects)
		separated = list(selected_set - {orig_obj})[0]
		orig_obj.select_set(False)
		bpy.context.view_layer.objects.active = separated
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.separate(type='LOOSE')
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		orig_obj.select_set(True)
		bpy.context.view_layer.objects.active = orig_obj
		bpy.ops.object.mode_set(mode='EDIT')
		return {'FINISHED'}

################
# メニュー追加 #
################

class SeparateMatEXMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_edit_mesh_separate_mat_ex"
	bl_label = "Separate by One Material"
	bl_description = "Separate specific-material-assigned part to another object, and switch to the object's Edit mode"

	def draw(self, context):
		mat_names = [mat.name for mat in context.active_object.data.materials]
		for nam in mat_names:
			self.layout.operator(SeparateMaterialEX.bl_idname, text=nam).target_mat = nam

class SeparateEXMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_edit_mesh_separate_ex"
	bl_label = "Separate (Advance)"
	bl_description = "Isolate to another object of extended menu"

	def draw(self, context):
		self.layout.operator("mesh.separate", text="Selected").type = 'SELECTED'
		self.layout.operator(SeparateSelectedEX.bl_idname, icon="PLUGIN")
		self.layout.operator(DuplicateNewParts.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator("mesh.separate", text="By Material").type = 'MATERIAL'
		self.layout.menu(SeparateMatEXMenu.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator("mesh.separate", text="By Loose Parts").type = 'LOOSE'
		self.layout.operator(SeparateLooseEX.bl_idname).sep_selected = False
		self.layout.operator(SeparateLooseEX.bl_idname, text="By Selected Loose Parts").sep_selected = True

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
		self.layout.operator(QuickShrinkwrap.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(CellMenuSeparateEX.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(DuplicateNewParts.bl_idname, icon="PLUGIN")
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]


################
# クラスの登録 #
################

classes = [
	CellMenuSeparateEX,
	SeparateSelectedEX,
	DuplicateNewParts,
	QuickShrinkwrap,
	SeparateMaterialEX,
	SeparateLooseEX,
	SeparateMatEXMenu,
	SeparateEXMenu
]

def register():
	for cls in classes:
		bpy.utils.register_class(cls)

def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)
