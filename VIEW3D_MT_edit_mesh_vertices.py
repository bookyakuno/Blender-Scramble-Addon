# 「3Dビュー」エリア > メッシュの「編集」モード > 「頂点」メニュー
# "3D View" Area > "Edit" Mode with Mesh > "Vertex" Menu

import bpy
from bpy.props import *

################
# オペレーター #
_STORE_ITEMS = [] #保存用グローバル変数：EnumPropertyの動的なitems作成におけるバグへの対処用
################

class CellMenuSeparateEX(bpy.types.Operator):
	bl_idname = "mesh.cell_menu_separate_ex"
	bl_label = "Separate (Extra)"
	bl_description = "Separate menu with extra functions"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		bpy.ops.wm.call_menu(name=SeparateEXMenu.bl_idname)
		return {'FINISHED'}

class SeparateSelectedEX(bpy.types.Operator):
	bl_idname = "mesh.separate_selected_ex"
	bl_label = "Separate Selection => Edit Separated"
	bl_description = "Separate selected part to another object, and switch to the object's Edit mode"
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
	bl_label = "Duplicate Selection => Edit Duplicated"
	bl_description = "Duplicate selected part as another object, and switch to its Edit mode"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		objs = [obj.name for obj in context.selectable_objects]
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
	bl_label = "Apply Shrinkwrap to Selection"
	bl_description = "Apply to selected vertices Shrinkwrap modifier for the other selected object"
	bl_options = {'REGISTER', 'UNDO'}

	items = [
		('NEAREST_SURFACEPOINT', "Nearest Surface Point", "Shrink the mesh to the nearest target surface", 1),
		('PROJECT', "Project", "Shrink the mesh to the nearest target surface along a given axis", 2),
		('NEAREST_VERTEX', "Nearest Vertex", "Shrink the mesh to the nearest target vertex", 3),
		('TARGET_PROJECT', "Target Normal Project", "Shrink the mesh to the nearest target surface along the interpolated vertex normals of the target", 4),
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
			self.report(type={'ERROR'}, message="Need to select at least one vertex")
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
	bl_label = "By One Material"
	bl_description = "Separate specific-material-assigned part to another object, and switch to the object's Edit mode"
	bl_options = {'REGISTER', 'UNDO'}

	def item_callback(self, context):
		mats = bpy.context.active_object.data.materials
		if not self.is_stashed:
			_STORE_ITEMS.clear()
			for idx, mat in enumerate(mats):
				_STORE_ITEMS.append((str(idx), mat.name, "", idx))
				self.is_stashed = True
		#print(_STORE_ITEMS[0])#作成したリストの要素がうまく認識されないバグ?への一応の対処
		return _STORE_ITEMS

	target_matidx : EnumProperty(items=item_callback, name="Material to Separate")
	is_dupli : BoolProperty(name="Duplicate and Separate", default=False)
	is_stashed : BoolProperty(name="Mats' list exists", default=False, options={'HIDDEN'})

	def execute(self, context):
		orig_obj = context.active_object
		bpy.ops.mesh.select_all(action='DESELECT')
		context.active_object.active_material_index = int(self.target_matidx)
		bpy.ops.object.material_slot_select()
		if self.is_dupli:
			bpy.ops.mesh.duplicate()
		bpy.ops.mesh.separate(type='SELECTED')
		bpy.ops.object.mode_set(mode='OBJECT')
		selected_set = set(context.selected_objects)
		separated = list(selected_set - {orig_obj})[0]
		orig_obj.select_set(False)
		bpy.context.view_layer.objects.active = separated
		bpy.ops.object.mode_set(mode='EDIT')
		return {'FINISHED'}

class SeparateLooseEX(bpy.types.Operator):
	bl_idname = "mesh.separate_loose_ex"
	bl_label = "By Loose Parts (Non-Selected)"
	bl_description = "Separate each not-selected / selected isolated part to another object"
	bl_options = {'REGISTER', 'UNDO'}

	sep_selected : BoolProperty(name="Separate selected", default=False, options={'HIDDEN'})
	is_dupli : BoolProperty(name="Duplicate and Separate", default=False)
	end_method : EnumProperty(name="Mode", items=[
		("EDIT","Edit: Original","",1),
		("OBJECT_ORIG","Object: Original Selected","",2),
		("OBJECT_SEPA","Object: Separated Selected","",3),
		])

	def draw(self, context):
		row = self.layout.row()
		row.use_property_split = True
		row.prop(self, 'is_dupli')
		row = self.layout.split(factor=0.15)
		row.label(text="Mode")
		row.prop(self, 'end_method', text="")

	def execute(self, context):
		orig_obj = context.active_object
		bpy.ops.mesh.select_linked()
		if not self.sep_selected:
			bpy.ops.mesh.select_all(action='INVERT')
		if self.is_dupli:
			bpy.ops.mesh.duplicate()
		bpy.ops.mesh.separate(type='SELECTED')
		bpy.ops.object.mode_set(mode='OBJECT')
		selected_set = set(context.selected_objects)
		separated = list(selected_set - {orig_obj})[0]
		orig_obj.select_set(False)
		bpy.context.view_layer.objects.active = separated
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.separate(type='LOOSE')
		bpy.ops.object.mode_set(mode='OBJECT')
		if not self.end_method == 'OBJECT_SEPA':
			bpy.ops.object.select_all(action='DESELECT')
			orig_obj.select_set(True)
			bpy.context.view_layer.objects.active = orig_obj
			if self.end_method == 'EDIT':
				bpy.ops.object.mode_set(mode='EDIT')
		return {'FINISHED'}

################
# メニュー追加 #
################

class SeparateMatEXMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_edit_mesh_separate_mat_ex"
	bl_label = "By One Material"
	bl_description = "Separate specific-material-assigned part to another object, and switch to the object's Edit mode"

	def draw(self, context):
		mats = context.active_object.data.materials
		for idx, mat in enumerate(mats):
			self.layout.operator(SeparateMaterialEX.bl_idname, text=mat.name).target_matidx = str(idx)

class SeparateEXMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_edit_mesh_separate_ex"
	bl_label = "Separate (Extra)"
	bl_description = "Separate menu with extra functions"

	def draw(self, context):
		self.layout.operator("mesh.separate", text="Selection").type = 'SELECTED'
		self.layout.operator(SeparateSelectedEX.bl_idname, icon="PLUGIN")
		self.layout.operator(DuplicateNewParts.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator("mesh.separate", text="By Material").type = 'MATERIAL'
		self.layout.menu(SeparateMatEXMenu.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator("mesh.separate", text="By Loose Parts").type = 'LOOSE'
		self.layout.operator(SeparateLooseEX.bl_idname, icon="PLUGIN").sep_selected = False
		self.layout.operator(SeparateLooseEX.bl_idname, text="By Loose Parts (Selected)", icon="PLUGIN").sep_selected = True

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
