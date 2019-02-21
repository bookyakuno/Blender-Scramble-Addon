# 「情報」エリア > 「ウィンドウ」メニュー
# "Info" Area > "Window" Menu

import bpy

################
# パイメニュー #
################

class PieMenu(bpy.types.Menu):
	bl_idname = "INFO_MT_window_pie"
	bl_label = "Pie Menu"
	bl_description = "Window Pie Menus"
	
	def draw(self, context):
		self.layout.operator(AreaTypePieOperator.bl_idname, icon="PLUGIN")

class AreaTypePieOperator(bpy.types.Operator):
	bl_idname = "wm.area_type_pie_operator"
	bl_label = "Editor Type"
	bl_description = "This is pie menu of editor type change"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		bpy.ops.wm.call_menu_pie(name=AreaTypePie.bl_idname)
		return {'FINISHED'}
class AreaTypePie(bpy.types.Menu): #
	bl_idname = "INFO_MT_window_pie_area_type"
	bl_label = "Editor Type"
	bl_description = "This is pie menu of editor type change"
	
	def draw(self, context):
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Text Editor", icon="TEXT").type = "TEXT_EDITOR"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Outliner", icon="OOPS").type = "OUTLINER"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Property", icon="BUTS").type = "PROPERTIES"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="3D View", icon="MESH_CUBE").type = "VIEW_3D"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="UV/Image Editor", icon="IMAGE_COL").type = "IMAGE_EDITOR"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Node Editor", icon="NODETREE").type = "NODE_EDITOR"
		self.layout.menu_pie().operator("wm.call_menu_pie", text="Anime", icon="ACTION").name = AreaTypePieAnim.bl_idname
		self.layout.menu_pie().operator("wm.call_menu_pie", text="Other", icon="QUESTION").name = AreaTypePieOther.bl_idname
		

class AreaTypePieAnim(bpy.types.Menu):
	bl_idname = "INFO_MT_window_pie_area_type_anim"
	bl_label = "Editor Type (Animation)"
	bl_description = "Is pie menu change editor type (animation related)"
	
	def draw(self, context):
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="NLA Editor", icon="NLA").type = "NLA_EDITOR"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="DopeSheet", icon="ACTION").type = "DOPESHEET_EDITOR"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Graph Editor", icon="IPO").type = "GRAPH_EDITOR"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Timeline", icon="TIME").type = "TIMELINE"
class AreaTypePieOther(bpy.types.Menu):
	bl_idname = "INFO_MT_window_pie_area_type_other"
	bl_label = "Editor Type (other)"
	bl_description = "Is pie menu change editor type (other)"
	
	def draw(self, context):
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Logic Editor", icon="LOGIC").type = "LOGIC_EDITOR"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Video Sequence Editor", icon="SEQUENCE").type = "SEQUENCE_EDITOR"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Video Clip Editor", icon="RENDER_ANIMATION").type = "CLIP_EDITOR"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="File Browser", icon="FILESEL").type = "FILE_BROWSER"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Python Console", icon="CONSOLE").type = "CONSOLE"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Info", icon="INFO").type = "INFO"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="User Setting", icon="PREFERENCES").type = "USER_PREFERENCES"
class SetAreaType(bpy.types.Operator): #
	bl_idname = "wm.set_area_type"
	bl_label = "Change Editor Type"
	bl_description = "Change Editor Type"
	bl_options = {'REGISTER'}
	
	type = bpy.props.StringProperty(name="Area Type")
	
	def execute(self, context):
		context.area.type = self.type
		return {'FINISHED'}

################
# オペレーター #
################

class ToggleJapaneseInterface(bpy.types.Operator):
	bl_idname = "wm.toggle_japanese_interface"
	bl_label = "Switch UI English/Japanese"
	bl_description = "Switch interface English, Japan,"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		if (not bpy.context.user_preferences.system.use_international_fonts):
			bpy.context.user_preferences.system.use_international_fonts = True
		if (bpy.context.user_preferences.system.language != "ja_JP"):
			bpy.context.user_preferences.system.language = "ja_JP"
		bpy.context.user_preferences.system.use_translate_interface = not bpy.context.user_preferences.system.use_translate_interface
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
		self.layout.operator(ToggleJapaneseInterface.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.menu(PieMenu.bl_idname, icon="PLUGIN")
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
