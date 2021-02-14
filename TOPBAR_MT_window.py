# 「トップバー」エリア > 「ウィンドウ」メニュー
# "TOPBAR" Area > "Window" Menu

import bpy
from bpy.props import *

################
# パイメニュー #
################

class PieMenu(bpy.types.Menu):
	bl_idname = "INFO_MT_window_pie"
	bl_label = "Switch Editors (For Shortcut)"
	bl_description = "Functions to switch editors that can be used easily by assigning shortcut"

	def draw(self, context):
		self.layout.operator(AreaTypePieOperator.bl_idname, icon="PLUGIN")

class AreaTypePieOperator(bpy.types.Operator):
	bl_idname = "wm.area_type_pie_operator"
	bl_label = "Pie menu : Editor Type"
	bl_description = "Switch editor types of this area"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		if context.area.type == 'TOPBAR':
			self.report(type={'ERROR'}, message="Cannot use in 'Topbar'. Please use in other areas (by using shortcut)")
			return {'CANCELLED'}
		bpy.ops.wm.call_menu_pie(name=AreaTypePie.bl_idname)
		return {'FINISHED'}
class AreaTypePie(bpy.types.Menu): #
	bl_idname = "INFO_MT_window_pie_area_type"
	bl_label = "Pie menu : Editor Type"

	def draw(self, context):
		#Left
		op = self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Compositor", icon="NODE_COMPOSITING")
		op.type, op.mode = ["NODE_EDITOR", "CompositorNodeTree"]
		#Right
		op = self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Image Editor", icon="IMAGE")
		op.type, op.mode = ["IMAGE_EDITOR", "VIEW"]
		#Bottom
		self.layout.menu_pie().operator("wm.call_menu_pie", text="Other", icon="QUESTION").name = AreaTypePieOther.bl_idname
		#Top
		op = self.layout.menu_pie().operator(SetAreaType.bl_idname, text="3D Viewport", icon="VIEW3D")
		op.type, op.mode = ["VIEW_3D", ""]
		#Top Left
		op = self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Shader Editor", icon="NODE_MATERIAL")
		op.type, op.mode = ["NODE_EDITOR", "ShaderNodeTree"]
		#Top Right
		op = self.layout.menu_pie().operator(SetAreaType.bl_idname, text="UV Editor", icon="UV")
		op.type, op.mode = ["IMAGE_EDITOR", "UV"]
		#Bottom Left
		op = self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Texture Node Editor", icon="NODE_TEXTURE")
		op.type, op.mode = ["NODE_EDITOR", "TextureNodeTree"]
		#Bottom Right
		self.layout.menu_pie().operator("wm.call_menu_pie", text="Animetion-related", icon="ACTION").name = AreaTypePieAnim.bl_idname

class AreaTypePieAnim(bpy.types.Menu):
	bl_idname = "INFO_MT_window_pie_area_type_anim"
	bl_label = "Pie menu : Editor Type (Animation)"
	bl_description = "Switch editor types of this area to animation-related editors"

	def draw(self, context):
		#Left
		op = self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Graph Editor", icon="GRAPH")
		op.type, op.mode = ["GRAPH_EDITOR", "FCURVES"]
		#Right
		op = self.layout.menu_pie().operator(SetAreaType.bl_idname, text="DopeSheet", icon="ACTION")
		op.type, op.mode = ["DOPESHEET_EDITOR", ""]
		#Bottom
		op = self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Video Clip Editor", icon="TRACKER")
		op.type, op.mode = ["CLIP_EDITOR", ""]
		#Top
		op = self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Video Sequence Editor", icon="SEQUENCE")
		op.type, op.mode = ["SEQUENCE_EDITOR", ""]
		#Top Left
		op = self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Timeline", icon="TIME")
		op.type, op.mode = ["TIMELINE", ""]
		#Top Right
		op = self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Non-Liner Animation", icon="NLA")
		op.type, op.mode = ["NLA_EDITOR", ""]
		#Left Bottom
		op = self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Drivers", icon="DRIVER")
		op.type, op.mode = ["GRAPH_EDITOR", "DRIVERS"]
class AreaTypePieOther(bpy.types.Menu):
	bl_idname = "INFO_MT_window_pie_area_type_other"
	bl_label = "Pie menu : Editor Type (Scripting/Data)"
	bl_description = "Switch editor types of this area to scripting/data-related editors"

	def draw(self, context):
		#Left
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Preferences", icon="PREFERENCES").type = "PREFERENCES"
		#Right
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Outliner", icon="OUTLINER").type = "OUTLINER"
		#Bottom
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Python Console", icon="CONSOLE").type = "CONSOLE"
		#Top
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Info", icon="INFO").type = "INFO"
		#Top Left
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Topbar", icon="BLENDER").type = "TOPBAR"
		#Top Right
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Property", icon="PROPERTIES").type = "PROPERTIES"
		#Bottom Left
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="File Browser", icon="FILEBROWSER").type = "FILE_BROWSER"
		#Bottom Right
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Text Editor", icon="TEXT").type = "TEXT_EDITOR"
class SetAreaType(bpy.types.Operator): #
	bl_idname = "wm.set_area_type"
	bl_label = "Change Editor Type"
	bl_description = "Switch editor types of this area"
	bl_options = {'REGISTER'}

	type : StringProperty(name="Area Type")
	mode : StringProperty(name="Space Mode", default="")

	def execute(self, context):
		context.area.type = self.type
		if (self.type != 'NODE_EDITOR') and len(self.mode):
			context.area.spaces[0].mode = self.mode
		elif (self.type == 'NODE_EDITOR') and len(self.mode):
			context.area.spaces[0].tree_type = self.mode
		return {'FINISHED'}

################
# オペレーター #
################

class ToggleJapaneseInterface(bpy.types.Operator):
	bl_idname = "wm.toggle_japanese_interface"
	bl_label = "Switch UI Language (English/Japanese)"
	bl_description = "Switch interface language between English and Japanese"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		if (bpy.context.preferences.view.language == "en_US"):
			bpy.context.preferences.view.language = "ja_JP"
		elif (bpy.context.preferences.view.language == "ja_JP"):
			bpy.context.preferences.view.language = "en_US"
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	PieMenu,
	AreaTypePieOperator,
	AreaTypePie,
	AreaTypePieAnim,
	AreaTypePieOther,
	SetAreaType,
	ToggleJapaneseInterface
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
		self.layout.operator(ToggleJapaneseInterface.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.menu(PieMenu.bl_idname, icon="PLUGIN")
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
