# 「3Dビュー」エリア > 「メッシュ編集」モード > 「X」キー
# "3D View" Area > "Mesh Editor" Mode > "X" Key

import bpy
import bmesh
from bpy.props import *

################
# オペレーター #
################

class DeleteBySelectMode(bpy.types.Operator):
	bl_idname = "mesh.delete_by_select_mode"
	bl_label = "Delete Based on Select Mode"
	bl_description = "Delete selected vertices / edges / faces in the specific way based on current mesh select mode"
	bl_options = {'REGISTER', 'UNDO'}

	use_current : BoolProperty(name="Registered", default=False, options={'HIDDEN'})
	vertex_items = [
		("delete(type='VERT')","Delete","Delete selected vertices",1),
		("dissolve_verts()"," Dissolve","Dissolve vertices, merge edges and faces",2),
		("remove_doubles()","Remove Doubles","Merge vertices based on their proximity",3)
	]
	vertex_mode : EnumProperty(name="Method on Vertex Mode", items=vertex_items)
	edge_items = [
		("delete(type='EDGE')","Delete","Delete selected edges",1),
		("dissolve_edges()"," Dissolve","Dissolve edges, merging faces",2),
		("edge_collapse()","Collapse","Collapse each edge to one vertex",3),
		("delete_edgeloop()","Delete Loop","Delete an edge loop by merging the faces on each side",4)
	]
	edge_mode : EnumProperty(name="Method on Edge Mode", items=edge_items)
	face_items = [
		("delete(type='FACE')","Delete","Delete selected faces",1),
		("dissolve_faces()"," Dissolve","Dissolve faces",2),
		("delete(type='ONLY_FACE')","Only Faces","Delete selected faces keeping their vertices and edges",3)
	]
	face_mode : EnumProperty(name="Method on Face Mode", items=face_items)

	def __init__(self):
		for p in ['use_current','vertex_mode','edge_mode','face_mode',]:
			exec(f"self.{p} = bpy.context.scene.scramble_dl_prop.{p}")

	def invoke(self, context, event):
		if not self.use_current:
			return context.window_manager.invoke_props_dialog(self, width=330)
		else:
			return self.execute(context)
	def draw(self, context):
		for p in ['vertex_mode','edge_mode','face_mode',]:
			box = self.layout.box()
			row = box.split(factor=0.6).row()
			row.alignment = 'LEFT'
			target = p.split("_")[0]
			row.label(text=target.capitalize(), icon =f"{target.upper()}SEL")
			row.label(text="Delete Method")
			row = box.row(align=True)
			row.prop(self, p, expand=True)

	def execute(self, context):
		if not self.use_current:
			self.use_current = True
		mode = context.tool_settings.mesh_select_mode[:]
		if (mode[0]):
			exec(f"bpy.ops.mesh.{self.vertex_mode}")
		elif (mode[1]):
			exec(f"bpy.ops.mesh.{self.edge_mode}")
		elif (mode[2]):
			exec(f"bpy.ops.mesh.{self.face_mode}")
		for p in ['use_current','vertex_mode','edge_mode','face_mode',]:
			if eval(f"bpy.context.scene.scramble_dl_prop.{p} != self.{p}"):
				exec(f"bpy.context.scene.scramble_dl_prop.{p} = self.{p}")
		return {'FINISHED'}

class DeleteHideMesh(bpy.types.Operator):
	bl_idname = "mesh.delete_hide_mesh"
	bl_label = "Delete Hidden Vertices"
	bl_description = "Delete all hidden vertices of active object"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if not context.active_object.type == "MESH":
			return False
		return True

	def execute(self, context):
		me = context.active_object.data
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

class ScrambleDeletePropGroup(bpy.types.PropertyGroup):
	use_current : bpy.props.BoolProperty(
		name="Use current setting",
		description="",
		default=False
	)

	vertex_mode : bpy.props.StringProperty(
		name="Delete method on vertex mode",
		description="",
		default="delete(type='VERT')"
	)

	edge_mode : bpy.props.StringProperty(
		name="Delete method on edge mode",
		description="",
		default="delete(type='EDGE')"
	)

	face_mode : bpy.props.StringProperty(
		name="Delete method on face mode",
		description="",
		default="delete(type='FACE')"
	)

################
# クラスの登録 #
################

classes = [
	DeleteBySelectMode,
	DeleteHideMesh,
	ScrambleDeletePropGroup
]

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.Scene.scramble_dl_prop = bpy.props.PointerProperty(type=ScrambleDeletePropGroup)

def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)
	del bpy.types.Scene.scramble_dl_prop


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
		self.layout.operator(DeleteBySelectMode.bl_idname, icon="PLUGIN")
		self.layout.operator(DeleteHideMesh.bl_idname, icon="PLUGIN")
		self.layout.operator('mesh.dissolve_mode')
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
