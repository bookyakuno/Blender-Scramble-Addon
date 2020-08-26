# 「3Dビュー」エリア > 「メッシュ編集」モード > 「X」キー
# "3D View" Area > "Mesh Editor" Mode > "X" Key

import bpy
import bmesh

################
# オペレーター #
################

class DeleteBySelectMode(bpy.types.Operator):
	bl_idname = "mesh.delete_by_select_mode"
	bl_label = "Remove same element to selection mode"
	bl_description = "Same mesh selection mode of current element (vertex and side and side) remove"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		mode = context.tool_settings.mesh_select_mode[:]
		if (mode[0]):
			bpy.ops.mesh.delete(type="VERT")
		elif (mode[1]):
			bpy.ops.mesh.delete(type="EDGE")
		elif (mode[2]):
			bpy.ops.mesh.delete(type="FACE")
		return {'FINISHED'}

class DeleteHideMesh(bpy.types.Operator):
	bl_idname = "mesh.delete_hide_mesh"
	bl_label = "Remove Hidden Meshes"
	bl_description = "Delete all are mesh"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		obj = context.active_object
		if (obj.type != 'MESH'):
			self.report(type={"ERROR"}, message="This is not mesh object")
			return {"CANCELLED"}
		me = obj.data
		bm = bmesh.from_edit_mesh(me)
		for face in bm.faces[:]:
			if (face.hide):
				bm.faces.remove(face)
		for edge in bm.edges[:]:
			if (edge.hide):
				bm.edges.remove(edge)
		for vert in bm.verts[:]:
			if (vert.hide):
				bm.verts.remove(vert)
		bmesh.update_edit_mesh(me)
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	DeleteBySelectMode,
	DeleteHideMesh
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
	for id in bpy.context.preferences.addons["Scramble Addon"].preferences.disabled_menu.split(','):
		if (id == self_id):
			return False
	else:
		return True

# メニューを登録する関数
def menu(self, context):
	if (IsMenuEnable(__name__.split('.')[-1])):
		self.layout.separator()
		self.layout.operator(DeleteBySelectMode.bl_idname, icon="PLUGIN")
		self.layout.operator(DeleteHideMesh.bl_idname, icon="PLUGIN")
		self.layout.operator('mesh.dissolve_mode')
	if (context.preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
