# 「プロパティ」エリア > 「オブジェクトデータ」タブ > 頂点グループリスト右の▼
# "Propaties" Area > "Object" Tab > VertexGroups List Right ▼

import bpy
import re

################
# オペレーター #
################

class RemoveEmptyVertexGroups(bpy.types.Operator):
	bl_idname = "mesh.remove_empty_vertex_groups"
	bl_label = "Delete empty vertex groups"
	bl_description = "Remove weights assigned to mesh vertex groups"
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
					obj.vertex_groups.new(newName)
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

class RemoveSpecifiedStringVertexGroups(bpy.types.Operator):
	bl_idname = "mesh.remove_specified_string_vertex_groups"
	bl_label = "Delete vertex groups contain specific text"
	bl_description = "Removes all vertex group names contains specified string"
	bl_options = {'REGISTER', 'UNDO'}
	
	string = bpy.props.StringProperty(name="Part of name deleteing", default="")
	
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
		if (obj.type == "MESH"):
			for vg in obj.vertex_groups[:]:
				if (self.string in vg.name):
					obj.vertex_groups.remove(vg)
					count += 1
			self.report(type={'INFO'}, message=str(count)+" removed vertex groups")
		else:
			self.report(type={'ERROR'}, message="Try run on mesh object")
			return {'CANCELLED'}
		return {'FINISHED'}
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

################
# クラスの登録 #
################

classes = [
	RemoveEmptyVertexGroups,
	AddOppositeVertexGroups,
	SelectVertexGroupsTop,
	SelectVertexGroupsBottom,
	MoveVertexGroupTop,
	MoveVertexGroupBottom,
	RemoveSpecifiedStringVertexGroups
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
	for id in bpy.context.preferences.addons["Blender-Scramble-Addon-master"].preferences.disabled_menu.split(','):
		if (id == self_id):
			return False
	else:
		return True

# メニューを登録する関数
def menu(self, context):
	if (IsMenuEnable(__name__.split('.')[-1])):
		self.layout.separator()
		self.layout.operator(SelectVertexGroupsTop.bl_idname, icon='PLUGIN')
		self.layout.operator(SelectVertexGroupsBottom.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(MoveVertexGroupTop.bl_idname, icon='PLUGIN')
		self.layout.operator(MoveVertexGroupBottom.bl_idname, icon='PLUGIN')
		self.layout.separator()
		operator = self.layout.operator('object.vertex_group_normalize_all', icon='PLUGIN')
		operator.group_select_mode = 'ALL'
		operator.lock_active = False
		operator = self.layout.operator('object.vertex_group_clean', icon='PLUGIN')
		operator.group_select_mode = 'ALL'
		operator.limit = 0
		operator.keep_single = False
		self.layout.separator()
		self.layout.operator(RemoveSpecifiedStringVertexGroups.bl_idname, icon='PLUGIN')
		self.layout.operator(RemoveEmptyVertexGroups.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(AddOppositeVertexGroups.bl_idname, icon='PLUGIN')
	if (context.preferences.addons["Blender-Scramble-Addon-master"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
