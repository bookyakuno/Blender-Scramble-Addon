# 「プロパティ」エリア > 「テクスチャ」タブ > 「マッピング」パネル
# "Propaties" Area > "Texture" Tab > "Mapping" Panel

import bpy
from bpy.props import *

################
# オペレーター #
################

class UseActiveUV(bpy.types.Operator):
	bl_idname = "texture.select_uv"
	bl_label = "Select UV"
	bl_description = "Select UV mesh used in this slot"
	bl_property = "uv_list"
	bl_options = {'REGISTER', 'UNDO'}

	def get_object_list_callback(self, context):
		items = ((uv.name, uv.name, "") for uv in context.object.data.uv_layers)
		return items
	
	uv_list : EnumProperty(name="active UV", items=get_object_list_callback)
	
	@classmethod
	def poll(cls, context):
		if (context.object.type != 'MESH'):
			return False
		if (len(context.object.data.uv_layers) <= 1):
			return False			
		if (not context.object.active_material):
			return False
		if (context.scene.tool_settings.image_paint.mode == 'IMAGE'):
			return False	
		if len(context.object.active_material.texture_paint_images) == 0:
			return False
		return True
	def invoke(self, context, event):
		context.window_manager.invoke_search_popup(self)
		return {'RUNNING_MODAL'}
	def execute(self, context):
		context.object.data.uv_layers.active = context.object.data.uv_layers[self.uv_list]
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	UseActiveUV
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
		if (context.scene.tool_settings.image_paint.mode == 'MATERIAL'):
			row = self.layout.row(align=True)
			row.prop_search(context.object.data.uv_layers, "active", context.object.data, "uv_layers",text="Select UV", text_ctxt="", translate=True, icon='PLUGIN')
			#row.label(text=f" UV name : {context.object.data.uv_layers.active.name}")
			#row.operator(UseActiveUV.bl_idname, icon='PLUGIN')
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
