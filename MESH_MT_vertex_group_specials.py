# 「プロパティ」エリア > 「オブジェクトデータ」タブ > 頂点グループリスト右の▼
# "Propaties" Area > "Object" Tab > VertexGroups List Right ▼

import bpy
import re
from bpy.props import *

################
# オペレーター #
################

class AddOppositeVertexGroups(bpy.types.Operator):
	bl_idname = "mesh.add_opposite_vertex_groups"
	bl_label = "Add empty mirroring vertex group"
	bl_description = ". L... R, add an empty pair of bones according to mandate rule in Miller\'s new born"
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
			vgs = obj.vertex_groups[:]
			for vg in vgs:
				oldName = vg.name
				newName = re.sub(r'([_\.-])L$', r'\1R', vg.name)
				if (oldName == newName):
					newName = re.sub(r'([_\.-])R$', r'\1L', vg.name)
					if (oldName == newName):
						newName = re.sub(r'([_\.-])l$', r'\1r', vg.name)
						if (oldName == newName):
							newName = re.sub(r'([_\.-])r$', r'\1l', vg.name)
							if (oldName == newName):
								newName = re.sub(r'[lL][eE][fF][tT]$', r'Right', vg.name)
								if (oldName == newName):
									newName = re.sub(r'[rR][iI][gG][hH][tT]$', r'Left', vg.name)
									if (oldName == newName):
										newName = re.sub(r'^[lL][eE][fF][tT]', r'Right', vg.name)
										if (oldName == newName):
											newName = re.sub(r'^[rR][iI][gG][hH][tT]', r'Left', vg.name)
				for v in vgs:
					if (newName.lower() == v.name.lower()):
						break
				else:
					obj.vertex_groups.new(name=newName)
		return {'FINISHED'}

class SelectVertexGroupsTop(bpy.types.Operator):
	bl_idname = "mesh.select_vertex_groups_top"
	bl_label = "Select Top"
	bl_description = "Select item at top of vertex groups"
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
		context.active_object.vertex_groups.active_index = 0
		return {'FINISHED'}

class SelectVertexGroupsBottom(bpy.types.Operator):
	bl_idname = "mesh.select_vertex_groups_bottom"
	bl_label = "Select Bottom"
	bl_description = "Select item at bottom of vertex groups"
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
		context.active_object.vertex_groups.active_index = len(context.active_object.vertex_groups) - 1
		return {'FINISHED'}

class MoveVertexGroupTop(bpy.types.Operator):
	bl_idname = "mesh.move_vertex_group_top"
	bl_label = "To Top"
	bl_description = "Move to top active vertex groups"
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
		for i in range(context.active_object.vertex_groups.active_index):
			bpy.ops.object.vertex_group_move(direction='UP')
		return {'FINISHED'}

class MoveVertexGroupBottom(bpy.types.Operator):
	bl_idname = "mesh.move_vertex_group_bottom"
	bl_label = "To Bottom"
	bl_description = "Move to bottom vertex group active"
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
		for i in range(len(context.active_object.vertex_groups) - context.active_object.vertex_groups.active_index - 1):
			bpy.ops.object.vertex_group_move(direction='DOWN')
		return {'FINISHED'}

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
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	AddOppositeVertexGroups,
	SelectVertexGroupsTop,
	SelectVertexGroupsBottom,
	MoveVertexGroupTop,
	MoveVertexGroupBottom,
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
		self.layout.operator(AddOppositeVertexGroups.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(SelectVertexGroupsTop.bl_idname, icon='PLUGIN')
		self.layout.operator(SelectVertexGroupsBottom.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(MoveVertexGroupTop.bl_idname, icon='TRIA_UP_BAR')
		self.layout.operator(MoveVertexGroupBottom.bl_idname, icon='TRIA_DOWN_BAR')

	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
