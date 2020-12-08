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
	bl_label = "Add Group with Left-Right-Flipped name"
	bl_description = "For each vertex group with left-right suffixes, add an empty group with the suffix"
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
		vgs = obj.vertex_groups[:]
		for vg in vgs:
			oldName = vg.name
			if oldName[-4:] in ['Left', 'left'] and oldName[-5] in ['.', '_', '-'] :
				newName = oldName[:-4] + oldName[-4:].replace('Left', 'Right').replace('left', 'right')
			elif oldName[-5:] in ['Right', 'right'] and oldName[-6] in ['.', '_', '-'] :
				newName = oldName[:-5] + oldName[-5:].replace('Right', 'Left').replace('right', 'left')
			elif oldName[-1] in ['L', 'l'] and oldName[-2] in ['.', '_', '-'] :
				newName = oldName[:-1] + oldName[-1].replace('L', 'R').replace('l', 'r')
			elif oldName[-1] in ['R', 'r'] and oldName[-2] in ['.', '_', '-'] :
				newName = oldName[:-1] + oldName[-1].replace('R', 'L').replace('r', 'l')
			for v in vgs:
				if (newName.lower() == v.name.lower()):
					break
			else:
				obj.vertex_groups.new(name=newName)
		return {'FINISHED'}

class SelectVertexGroupsTop(bpy.types.Operator):
	bl_idname = "mesh.select_vertex_groups_top"
	bl_label = "Select Top"
	bl_description = "Select the top vertex groups"
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
	bl_description = "Select the bottom vertex groups"
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
	bl_label = "Move to Top"
	bl_description = "Move the active vertex groups to top"
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
	bl_label = "Move to Bottom"
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

class CopyMirrorVertexGroups(bpy.types.Operator):
	bl_idname = "mesh.copy_mirror_vertex_groups"
	bl_label = "Add Mirrored Vertex Group"
	bl_description = "For the active vertex group, add its copy with flipped weight and name"
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
		source_group = obj.vertex_groups.active
		oldName = source_group.name
		if oldName[-4:] in ['Left', 'left'] and oldName[-5] in ['.', '_', '-'] :
			newName = oldName[:-4] + oldName[-4:].replace('Left', 'Right').replace('left', 'right')
		elif oldName[-5:] in ['Right', 'right'] and oldName[-6] in ['.', '_', '-'] :
			newName = oldName[:-5] + oldName[-5:].replace('Right', 'Left').replace('right', 'left')
		elif oldName[-1] in ['L', 'l'] and oldName[-2] in ['.', '_', '-'] :
			newName = oldName[:-1] + oldName[-1].replace('L', 'R').replace('l', 'r')
		elif oldName[-1] in ['R', 'r'] and oldName[-2] in ['.', '_', '-'] :
			newName = oldName[:-1] + oldName[-1].replace('R', 'L').replace('r', 'l')
		vert_dic = {}
		for vert in obj.data.vertices:
			try:
				vert_dic[vert.index] = source_group.weight(vert.index)
			except RuntimeError:
				pass
		bpy.ops.object.vertex_group_copy()
		bpy.ops.object.vertex_group_mirror(all_groups=True, use_topology=False)
		obj.vertex_groups.active.name = newName
		obj.vertex_groups.active = source_group
		bpy.ops.object.vertex_group_clean()
		for vert in obj.data.vertices:
			try:
				source_group.add([vert.index], vert_dic[vert.index], 'REPLACE')
			except KeyError:
				source_group.remove([vert.index])
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
	CopyMirrorVertexGroups,
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
		self.layout.operator(CopyMirrorVertexGroups.bl_idname, icon='MOD_MIRROR')
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
