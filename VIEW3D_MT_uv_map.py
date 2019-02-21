# 「3Dビュー」エリア > 「メッシュ編集」モード > 「U」キー
# "3D View" Area > "Mesh Edit" Mode > "U" Key

import bpy

################
# オペレーター #
################

class CopyOtherUVMenuOperator(bpy.types.Operator): #
	bl_idname = "uv.copy_other_uv_menu_operator"
	bl_label = "Copy from other UV"
	bl_description = "Active UV unwrapping can be copied from other UV"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		obj = context.active_object
		if (obj.type != 'MESH'):
			self.report(type={"ERROR"}, message="Try run on mesh object")
			return {"CANCELLED"}
		if (len(obj.data.uv_layers) < 2):
			self.report(type={"ERROR"}, message="After add 2 or more UVs, please run")
			return {"CANCELLED"}
		bpy.ops.wm.call_menu(name=CopyOtherUVMenu.bl_idname)
		return {'FINISHED'}
class CopyOtherUVMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_uv_map_copy_other"
	bl_label = "Copy from other UV"
	bl_description = "Active UV unwrapping can be copied from other UV"
	
	def draw(self, context):
		me = context.active_object.data
		for uv in me.uv_layers:
			if (me.uv_layers.active.name != uv.name):
				self.layout.operator(CopyOtherUV.bl_idname, text=uv.name, icon="PLUGIN").uv = uv.name
class CopyOtherUV(bpy.types.Operator):
	bl_idname = "uv.copy_other_uv"
	bl_label = "Copy from other UV"
	bl_description = "Active UV unwrapping of selection can be copied from other UV"
	bl_options = {'REGISTER', 'UNDO'}
	
	uv = bpy.props.StringProperty(name="Source UV")
	
	def execute(self, context):
		obj = context.active_object
		me = obj.data
		pre_mode = obj.mode
		bpy.ops.object.mode_set(mode='OBJECT')
		active_uv = me.uv_layers.active
		source_uv = me.uv_layers[self.uv]
		for i in range(len(active_uv.data)):
			if (me.vertices[me.loops[i].vertex_index].select):
				active_uv.data[i].pin_uv = source_uv.data[i].pin_uv
				active_uv.data[i].select = source_uv.data[i].select
				active_uv.data[i].select_edge = source_uv.data[i].select_edge
				active_uv.data[i].uv = source_uv.data[i].uv
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

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
		self.layout.separator()
		self.layout.operator(CopyOtherUVMenuOperator.bl_idname, icon="PLUGIN")
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
