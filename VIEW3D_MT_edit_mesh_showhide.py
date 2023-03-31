# 「3Dビュー」エリア > メッシュの「編集」モード > 「メッシュ」メニュー > 「表示/隠す」メニュー
# "3D View" Area > "Edit" Mode with Mesh > "Mesh" Menu > "Show/Hide" Menu

import bpy
import bmesh
from bpy.props import *

################
# オペレーター #
################

class InvertHide(bpy.types.Operator):
	bl_idname = "mesh.invert_hide"
	bl_label = "Invert Show / Hide"
	bl_description = "Invert display states of each vertices / edges / faces"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if bpy.context.active_object:
			if (bpy.context.active_object.type == 'MESH'):
				return True
		return False

	def execute(self, context):
		obj = context.active_object
		bpy.ops.object.mode_set(mode="OBJECT")
		me = obj.data
		for v in me.vertices:
			v.hide = not v.hide
		for e in me.edges:
			for i in e.vertices:
				if (me.vertices[i].hide == True):
					e.hide = True
					break
			else:
				e.hide = False
		for f in me.polygons:
			for i in f.vertices:
				if (me.vertices[i].hide == True):
					f.hide = True
					break
			else:
				f.hide = False
		bpy.ops.object.mode_set(mode="EDIT")
		return {'FINISHED'}

class HideVertexOnly(bpy.types.Operator):
	bl_idname = "mesh.hide_vertex_only"
	bl_label = "Hide Only Vertex"
	bl_description = "Hide selected vertices to prevent them from changing"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if bpy.context.active_object:
			if (bpy.context.active_object.type == 'MESH'):
				return True
		return False

	def execute(self, context):
		obj = context.active_object
		bpy.ops.object.mode_set(mode="OBJECT")
		me = obj.data
		for vert in me.vertices:
			if (vert.select):
				vert.hide = True
		bpy.ops.object.mode_set(mode="EDIT")
		return {'FINISHED'}

class HidePartlySelected(bpy.types.Operator):
	bl_idname = "mesh.hide_partly_selected"
	bl_label = "Hide Partly-Selected Parts"
	bl_description = "Hide all of isolated meshes at least one of which vertices is selected"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		for bol, mode in zip(context.tool_settings.mesh_select_mode, ["VERT","EDGE","FACE"]):
			if bol:
				mode_type = mode
		mesh = bmesh.from_edit_mesh(context.active_object.data)
		isSelecteds = [v for v in mesh.verts]
		bpy.ops.mesh.select_linked()
		bpy.ops.mesh.hide()
		bpy.ops.mesh.select_all(action='DESELECT')
		bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
		bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type=mode_type)
		return {'FINISHED'}

class HideNotSelected(bpy.types.Operator):
	bl_idname = "mesh.hide_not_selected"
	bl_label = "Hide Not-Selected Parts"
	bl_description = "Hide all of isolated meshes which vertices are not selected"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		for bol, mode in zip(context.tool_settings.mesh_select_mode, ["VERT","EDGE","FACE"]):
			if bol:
				mode_type = mode
		mesh = bmesh.from_edit_mesh(context.active_object.data)
		isSelecteds = [v for v in mesh.verts]
		bpy.ops.mesh.select_linked()
		bpy.ops.mesh.hide(unselected=True)
		bpy.ops.mesh.select_all(action='DESELECT')
		for idx, vert in enumerate(mesh.verts):
			vert.select = isSelecteds[idx]
		bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
		bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type=mode_type)
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	InvertHide,
	HideVertexOnly,
	HidePartlySelected,
	HideNotSelected
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
		self.layout.operator(HidePartlySelected.bl_idname, icon="PLUGIN")
		self.layout.operator(HideNotSelected.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(InvertHide.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(HideVertexOnly.bl_idname, icon="PLUGIN")
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
