# 「3Dビュー」エリア > メッシュの「編集」モード > 「UV」メニュー
# "3D View" Area > "Edit" Mode with Mesh > "UV" Menu

import bpy
from bpy.props import *

################
# オペレーター #
################

class CopyFromOtherUV(bpy.types.Operator):
	bl_idname = "uv.copy_from_other_uv"
	bl_label = "Copy Selected Part's UV Data from Other"
	bl_description = "Copy UV data for mesh's selected part from another UV Map of active object"
	bl_properties = "target_uv"
	bl_options = {'REGISTER', 'UNDO'}

	target_uv : StringProperty(name="Copy from", default="")

	@classmethod
	def poll(cls, context):
		if context.active_object.type != 'MESH':
			return False
		if len(context.active_object.data.uv_layers) < 2 :
			return False
		return True
	def __init__(self):
		active = bpy.context.active_object.data.uv_layers.active
		for m in bpy.context.active_object.data.uv_layers:
			if m != active:
				self.target_uv = m.name
				break
		else:
			self.target_uv = active.name
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True
		layout.prop_search(self, 'target_uv', bpy.context.active_object.data, 'uv_layers', translate=True, icon='GROUP_UVS')

	def execute(self, context):
		me = context.active_object.data
		pre_mode = context.active_object.mode
		bpy.ops.object.mode_set(mode='OBJECT')
		active_uv = me.uv_layers.active
		source_uv = me.uv_layers[self.target_uv]
		for i in range(len(active_uv.data)):
			if (me.vertices[me.loops[i].vertex_index].select):
				active_uv.data[i].pin_uv = source_uv.data[i].pin_uv
				active_uv.data[i].select = source_uv.data[i].select
				active_uv.data[i].uv = source_uv.data[i].uv
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	CopyFromOtherUV
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
		self.layout.operator(CopyFromOtherUV.bl_idname, icon="PLUGIN")
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
