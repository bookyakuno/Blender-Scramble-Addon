# 「3Dビュー」エリア > 「メッシュ編集」モード > 「メッシュ」メニュー
# "3D View" Area > "Mesh Editor" Mode > "Mesh" Menu

import bpy
from bpy.props import *

################
# オペレーター #
################

class ToggleMeshSelectMode(bpy.types.Operator):
	bl_idname = "mesh.toggle_mesh_select_mode"
	bl_label = "Switch Mesh Select Mode"
	bl_description = "Vertex Select => Edge Select => Face Select"
	bl_options = {'REGISTER'}

	def execute(self, context):
		mode = context.tool_settings.mesh_select_mode
		if (mode[2]):
			context.tool_settings.mesh_select_mode = (True, False, False)
		elif (mode[1]):
			context.tool_settings.mesh_select_mode = (False, False, True)
		else:
			context.tool_settings.mesh_select_mode = (False, True, False)
		return {'FINISHED'}

################
# パイメニュー #
################

class SelectModePieOperator(bpy.types.Operator):
	bl_idname = "mesh.select_mode_pie_operator"
	bl_label = "Pie menu : Mesh Select Mode"
	bl_description = "Switch mesh select mode"
	bl_options = {'REGISTER'}

	def execute(self, context):
		bpy.ops.wm.call_menu_pie(name=SelectModePie.bl_idname)
		return {'FINISHED'}
class SelectModePie(bpy.types.Menu): #
	bl_idname = "VIEW3D_MT_edit_mesh_pie_select_mode"
	bl_label = "Pie menu : Mesh Select Mode"
	bl_description = "Switch mesh select mode"

	def draw(self, context):
		self.layout.menu_pie().operator("mesh.select_mode", text="Vertex", icon='VERTEXSEL').type = 'VERT'
		self.layout.menu_pie().operator("mesh.select_mode", text="Face", icon='FACESEL').type = 'FACE'
		self.layout.menu_pie().operator("mesh.select_mode", text="Edge", icon='EDGESEL').type = 'EDGE'

class ProportionalPieOperator(bpy.types.Operator):
	bl_idname = "mesh.proportional_pie_operator"
	bl_label = "Pie menu : Proportional Edit"
	bl_description = "Switch proportional editing mode"
	bl_options = {'REGISTER'}

	def execute(self, context):
		if (not context.scene.tool_settings.use_proportional_edit):
			#context.scene.tool_settings.use_proportional_edit = True
			bpy.ops.wm.call_menu_pie(name=ProportionalPie.bl_idname)
		else:
			bpy.ops.wm.call_menu_pie(name=ProportionalPie.bl_idname)
		return {'FINISHED'}
class ProportionalPie(bpy.types.Menu): #
	bl_idname = "VIEW3D_MT_edit_mesh_pie_proportional"
	bl_label = "Pie menu : Proportional Edit"
	bl_description = "Switch proportional editing mode"

	def draw(self, context):
		self.layout.menu_pie().operator(SetProportionalEdit.bl_idname, text="Enabled", icon="PROP_ON").mode = "ENABLED"
		self.layout.menu_pie().operator(SetProportionalEdit.bl_idname, text="Projected from View", icon="PROP_ON").mode = "PROJECTED"
		self.layout.menu_pie().operator(SetProportionalEdit.bl_idname, text="Connected Only", icon="PROP_CON").mode = "CONNECTED"
		self.layout.menu_pie().operator(SetProportionalEdit.bl_idname, text="Disabled", icon="PROP_OFF").mode = "DISABLED"
class SetProportionalEdit(bpy.types.Operator): #
	bl_idname = "mesh.set_proportional_edit"
	bl_label = "Pie menu : Proportional Edit"
	bl_description = "Switch proportional editing mode"
	bl_options = {'REGISTER'}

	mode : StringProperty(name="Mode", default="DISABLED")

	def execute(self, context):
		settings = context.scene.tool_settings
		if self.mode == "ENABLED":
			settings.use_proportional_edit = True
			settings.use_proportional_projected = False
			settings.use_proportional_connected = False
		elif self.mode == "PROJECTED":
			settings.use_proportional_edit = True
			settings.use_proportional_projected = not settings.use_proportional_projected
		elif self.mode == "CONNECTED":
			settings.use_proportional_edit = True
			settings.use_proportional_connected = not settings.use_proportional_connected
		else:
			settings.use_proportional_edit = False
			settings.use_proportional_projected = False
			settings.use_proportional_connected = False
		return {'FINISHED'}

################
# サブメニュー #
################

class EditMeshShortcutMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_edit_mesh_shortcut"
	bl_label = "Switch Mode (For Shortcut)"
	bl_description = "Functions to switch editors that can be used easily by assigning shortcut"

	def draw(self, context):
		self.layout.operator(ToggleMeshSelectMode.bl_idname, icon="PLUGIN")
		self.layout.separator()	
		self.layout.operator(SelectModePieOperator.bl_idname, icon="PLUGIN")
		self.layout.operator(ProportionalPieOperator.bl_idname, icon="PLUGIN")		

################
# クラスの登録 #
################

classes = [
	ToggleMeshSelectMode,
	SelectModePieOperator,
	SelectModePie,
	ProportionalPieOperator,
	ProportionalPie,
	SetProportionalEdit,
	EditMeshShortcutMenu
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
		self.layout.menu(EditMeshShortcutMenu.bl_idname, icon="PLUGIN")
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
