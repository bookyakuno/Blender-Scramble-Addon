# 「プロパティ」エリア > 「オブジェクトデータ」タブ > 「頂点グループ」パネル
# "Propaties" Area > "Object Data" Tab > "Vertex Groups" Panel

import bpy
import re
from bpy.props import *

################
# オペレーター #
################

class RemoveEmptyVertexGroups(bpy.types.Operator):
	bl_idname = "mesh.remove_empty_vertex_groups"
	bl_label = "Remove Empty Vertex Groups"
	bl_description = "Remove vertex groups in which all vertices' assigned weights are zero"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if (ob):
			if (ob.type == 'MESH'):
				if (len(ob.vertex_groups)):
					return True
		return False

	def execute(self, context):
		obj = context.active_object
		if (obj.type == "MESH"):
			for vg in obj.vertex_groups:
				for vert in obj.data.vertices:
					try:
						if (vg.weight(vert.index) > 0.0):
							break
					except RuntimeError:
						pass
				else:
					obj.vertex_groups.remove(vg)
		return {'FINISHED'}

class RemoveSpecifiedStringVertexGroups(bpy.types.Operator):
	bl_idname = "mesh.remove_specified_string_vertex_groups"
	bl_label = "Remove Groups which Contain Specific Texts"
	bl_description = "Remove all vertex groups that contain a designated text"
	bl_options = {'REGISTER', 'UNDO'}

	string : StringProperty(name="Text", default="")

	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if (ob):
			if (ob.type == 'MESH'):
				if (len(ob.vertex_groups)):
					return True
		return False

	def execute(self, context):
		obj = context.active_object
		for vg in obj.vertex_groups[:]:
			if (self.string in vg.name):
				obj.vertex_groups.remove(vg)
		return {'FINISHED'}
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

class SelectActiveGroupOnly(bpy.types.Operator):
	bl_idname = "mesh.select_active_vertex_group_only"
	bl_label = "Active Only"
	bl_description = "Select vertices in the active group only"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if (ob):
			if (ob.type == 'MESH'):
				if (2 <= len(ob.vertex_groups)):
					return True
		return False

	def execute(self, context):
		bpy.ops.mesh.select_all(action='DESELECT')
		bpy.ops.object.vertex_group_select()
		return {'FINISHED'}

class CleanVertexforMenu(bpy.types.Operator):
	bl_idname = "mesh.clean_vaertex_for_panel"
	bl_label = "Remove Low-Weight Vertices"
	bl_description = "Remove vertices which weights are below a limit from the active vertex group"
	bl_options = {'REGISTER', 'UNDO'}

	item = [("ACTIVE", "Active Group", "", 1),("ALL", "All Groups", "", 1)]
	mode : EnumProperty(name="Target", items=item)
	limit : IntProperty(name="Lower Limit", default=0, max=1, min=0, description="Remove vertices which weight is below or equal this limit")
	keep_single : BoolProperty(name="At Least One Weight for Each Vertices", default=False)

	@classmethod
	def poll(cls, context):
		ob = context.active_object
		if (ob):
			if (ob.type == 'MESH'):
				if (len(ob.vertex_groups)):
					return True
		return False
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	def draw(self, context):
		for p in ['mode', 'limit']:
			row = self.layout.row()
			row.use_property_split = True
			row.prop(self, p)
		row = self.layout.split(factor=0.2)
		row.label(text="")
		row.prop(self, 'keep_single')

	def execute(self, context):
		bpy.object.vertex_group_clean(group_select_mode=self.mode, limit=self.limit, keep_single=self.keep_single)
		return {'FINISHED'}

################
# サブメニュー #
################

class RemoveVertexGroupMenu(bpy.types.Menu):
	bl_idname = "DATA_MT_remove_vertex_group"
	bl_label = "Remove Vertex/Group"
	bl_description = "Functions to remove specific vertices or vertex groups"

	def draw(self, context):
		self.layout.operator(RemoveSpecifiedStringVertexGroups.bl_idname, icon='PLUGIN')
		self.layout.operator(RemoveEmptyVertexGroups.bl_idname, icon='PLUGIN')
		self.layout.separator()
		operator = self.layout.operator('object.vertex_group_clean', icon='PLUGIN', text="Remove Zero-Weight Vertices from All Groups")
		operator.group_select_mode = 'ALL'
		operator.limit = 0
		operator.keep_single = False
		operator = self.layout.operator('object.vertex_group_normalize_all', icon='PLUGIN')
		operator.group_select_mode = 'ALL'
		operator.lock_active = False
		self.layout.separator()
		self.layout.operator(CleanVertexforMenu.bl_idname, icon='PLUGIN')

################
# クラスの登録 #
################

classes = [
	RemoveEmptyVertexGroups,
	RemoveSpecifiedStringVertexGroups,
	SelectActiveGroupOnly,
	CleanVertexforMenu,
	RemoveVertexGroupMenu
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
		try:
			ob = context.active_object
			is_active = (len(ob.vertex_groups) > 0)
		except AttributeError as e:
			is_active = False
		row = self.layout.row()
		rowrow = row.row(align=True)
		op = rowrow.operator('object.vertex_group_sort', text="", icon='SORTALPHA')
		op.sort_type = 'NAME'		
		op = rowrow.operator('object.vertex_group_sort', text="", icon='BONE_DATA')
		op.sort_type = 'BONE_HIERARCHY'
		if context.active_object and context.active_object.mode == 'EDIT':
			sp = row.split(factor=0.87)
			spsp = sp.split(factor=0.57)
			spsp.operator('object.vertex_group_assign_new', text="With Selected Vetices", icon='PLUS')
			spsp.operator(SelectActiveGroupOnly.bl_idname, icon='VERTEXSEL')
			spsp = sp.split(factor=1)
			spsp.menu(RemoveVertexGroupMenu.bl_idname, text="", icon='CANCEL')
			spsp.active = is_active
		else:
			sp = row.split(factor=0.6)
			sp.menu(RemoveVertexGroupMenu.bl_idname, icon='CANCEL')
			sp.operator('mesh.copy_mirror_vertex_groups', text="Add Mirrored", icon='MOD_MIRROR')# MESH_MT_group_specials で定義
			sp.active = is_active

	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]