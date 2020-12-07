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
	bl_label = "Remove Groups with Specific Name"
	bl_description = "Removes all vertex groups that contain a designated text"
	bl_options = {'REGISTER', 'UNDO'}

	string : StringProperty(name="Remove groups which names contain :", default="")

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
		count = 0
		for vg in obj.vertex_groups[:]:
			if (self.string in vg.name):
				obj.vertex_groups.remove(vg)
				count += 1
		self.report(type={'INFO'}, message=str(count)+" removed vertex groups")
		return {'FINISHED'}
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self, width=350)
	def draw(self, context):
		sp = self.layout.split(factor=0.6)
		sp.label(text="Remove groups which names contain :")
		sp.prop(self, 'string', text="")

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

################
# クラスの登録 #
################

classes = [
	RemoveEmptyVertexGroups,
	RemoveSpecifiedStringVertexGroups,
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
		if context.active_object and context.active_object.mode == 'EDIT':
			sp = row.split(factor=0.87)
			spsp = sp.row()
			spsp.menu(RemoveVertexGroupMenu.bl_idname, text="", icon='CANCEL')
			spsp.active = is_active
		else:
			sp = row.split(factor=0.6)
			sp.menu(RemoveVertexGroupMenu.bl_idname, icon='CANCEL')
			sp.active = is_active

	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]