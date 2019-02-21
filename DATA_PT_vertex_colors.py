# 「プロパティ」エリア > 「メッシュデータ」タブ > 「頂点色」パネル
# "Propaties" Area > "Mesh" Tab > "Vertex Colors" Panel

import bpy

################
# オペレーター #
################

class MoveActiveVertexColor(bpy.types.Operator):
	bl_idname = "object.move_active_vertex_color"
	bl_label = "Move Vertex Color"
	bl_description = "Move vertex color of active objects, sorts"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		('UP', "To Up", "", 1),
		('DOWN', "To Down", "", 2),
		]
	mode = bpy.props.EnumProperty(items=items, name="Direction", default="UP")
	
	@classmethod
	def poll(cls, context):
		obj = context.active_object
		if (obj):
			if (obj.type == 'MESH'):
				if (2 <= len(obj.data.vertex_colors)):
					return True
		return False
	
	def execute(self, context):
		obj = context.active_object
		if (not obj):
			self.report(type={'ERROR'}, message="There is no active object")
			return {'CANCELLED'}
		if (obj.type != 'MESH'):
			self.report(type={'ERROR'}, message="This is not mesh object")
			return {'CANCELLED'}
		me = obj.data
		if (len(me.vertex_colors) <= 1):
			self.report(type={'ERROR'}, message="Vertex color is less than one")
			return {'CANCELLED'}
		if (self.mode == 'UP'):
			if (me.vertex_colors.active_index <= 0):
				return {'CANCELLED'}
			target_index = me.vertex_colors.active_index - 1
		elif (self.mode == 'DOWN'):
			target_index = me.vertex_colors.active_index + 1
			if (len(me.vertex_colors) <= target_index):
				return {'CANCELLED'}
		pre_mode = obj.mode
		bpy.ops.object.mode_set(mode='OBJECT')
		vertex_color = me.vertex_colors.active
		vertex_color_target = me.vertex_colors[target_index]
		for data_name in dir(vertex_color):
			if (data_name[0] != '_' and data_name != 'bl_rna' and data_name != 'rna_type' and data_name != 'data'):
				temp = vertex_color.__getattribute__(data_name)
				temp_target = vertex_color_target.__getattribute__(data_name)
				vertex_color.__setattr__(data_name, temp_target)
				vertex_color_target.__setattr__(data_name, temp)
				vertex_color.__setattr__(data_name, temp_target)
				vertex_color_target.__setattr__(data_name, temp)
		for i in range(len(vertex_color.data)):
			temp = vertex_color.data[i].color[:]
			vertex_color.data[i].color = vertex_color_target.data[i].color[:]
			vertex_color_target.data[i].color = temp[:]
		me.vertex_colors.active_index = target_index
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

class VertexColorSet(bpy.types.Operator):
	bl_idname = "object.vertex_color_set"
	bl_label = "Fill Vertex Color"
	bl_description = "Vertex color of active object with specified color fills"
	bl_options = {'REGISTER', 'UNDO'}
	
	color = bpy.props.FloatVectorProperty(name="Vertex Color", default=(0.0, 0.0, 0.0), min=0, max=1, soft_min=0, soft_max=1, step=3, precision=10, subtype='COLOR_GAMMA')
	
	@classmethod
	def poll(cls, context):
		obj = context.active_object
		if (obj):
			if (obj.type == 'MESH'):
				if (obj.data.vertex_colors.active):
					return True
		return False
	
	def invoke(self, context, event):
		obj = context.active_object
		if (not obj):
			self.report(type={'ERROR'}, message="There is no active object")
			return {'CANCELLED'}
		if (obj.type != 'MESH'):
			self.report(type={'ERROR'}, message="This is not mesh object")
			return {'CANCELLED'}
		me = obj.data
		active_col = me.vertex_colors.active
		if (not active_col):
			self.report(type={'ERROR'}, message="Vertex color not exist")
			return {'CANCELLED'}
		return context.window_manager.invoke_props_dialog(self)
	
	def execute(self, context):
		obj = context.active_object
		pre_mode = obj.mode
		bpy.ops.object.mode_set(mode='OBJECT')
		me = obj.data
		active_col = me.vertex_colors.active
		for data in active_col.data:
			data.color = self.color[:]
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

class AddVertexColorSelectedObject(bpy.types.Operator):
	bl_idname = "object.add_vertex_color_selected_object"
	bl_label = "Altogether add vertex colors"
	bl_description = "Specify color and name all selected mesh object, adds vertex color"
	bl_options = {'REGISTER', 'UNDO'}
	
	name = bpy.props.StringProperty(name="Vertex Color Name", default="Col")
	color = bpy.props.FloatVectorProperty(name="Vertex Color", default=(0.0, 0.0, 0.0), min=0, max=1, soft_min=0, soft_max=1, step=10, precision=3, subtype='COLOR_GAMMA')
	
	@classmethod
	def poll(cls, context):
		for obj in context.selected_objects:
			if (obj.type == 'MESH'):
				return True
		return False
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	
	def execute(self, context):
		for obj in context.selected_objects:
			if (obj.type == "MESH"):
				me = obj.data
				try:
					col = me.vertex_colors[self.name]
				except KeyError:
					col = me.vertex_colors.new(self.name)
				for data in col.data:
					data.color = self.color
		return {'FINISHED'}

################
# サブメニュー #
################

class SubMenu(bpy.types.Menu):
	bl_idname = "DATA_PT_vertex_colors_sub_menu"
	bl_label = "Vertex Color Operation"
	bl_description = "Vertex color operators menu"
	
	def draw(self, context):
		self.layout.operator(AddVertexColorSelectedObject.bl_idname, icon='PLUGIN')

################
# メニュー追加 #
################

# メニューのオン/オフの判定
def IsMenuEnable(self_id):
	for id in bpy.context.user_preferences.addons["Scramble Addon"].preferences.disabled_menu.split(','):
		if (id == self_id):
			return False
	else:
		return True

# メニューを登録する関数
def menu(self, context):
	if (IsMenuEnable(__name__.split('.')[-1])):
		row = self.layout.row()
		if (context.active_object.type == 'MESH'):
			if (context.active_object.data.vertex_colors.active):
				sub = row.row(align=True)
				sub.operator(MoveActiveVertexColor.bl_idname, icon='TRIA_UP', text="").mode = 'UP'
				sub.operator(MoveActiveVertexColor.bl_idname, icon='TRIA_DOWN', text="").mode = 'DOWN'
				row.operator(VertexColorSet.bl_idname, icon='BRUSH_DATA', text="Paint Out")
		row.menu(SubMenu.bl_idname, icon='PLUGIN')
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
