# 「UV/画像エディター」エリア > 「ビュー」メニュー
# "UV/Image Editor" Area > "View" Menu

import bpy
from bpy.props import *

################
# オペレーター #
################

class Reset2DCursor(bpy.types.Operator):
	bl_idname = "image.reset_2d_cursor"
	bl_label = "Set 2DCursor Position"
	bl_description = "Move 2D cursor to a designated position"
	bl_options = {'REGISTER', 'UNDO'}

	items = [
		("C", "Center", "", 1),
		("U", "Up", "", 2),
		("RU", "Top Right", "", 3),
		("R", "Right", "", 4),
		("RD", "Down Right", "", 5),
		("D", "Down", "", 6),
		("LD", "Down Left", "", 7),
		("L", "Left", "", 8),
		("LU", "Top Left", "", 9),
		]
	mode : EnumProperty(items=items, name="Location", default="LD")

	def execute(self, context):
		x, y = (1.0, 1.0)
		if (self.mode == "C"):
			bpy.ops.uv.cursor_set(location=(x/2, y/2))
		elif (self.mode == "U"):
			bpy.ops.uv.cursor_set(location=(x/2, y))
		elif (self.mode == "RU"):
			bpy.ops.uv.cursor_set(location=(x, y))
		elif (self.mode == "R"):
			bpy.ops.uv.cursor_set(location=(x, y/2))
		elif (self.mode == "RD"):
			bpy.ops.uv.cursor_set(location=(x, 0))
		elif (self.mode == "D"):
			bpy.ops.uv.cursor_set(location=(x/2, 0))
		elif (self.mode == "LD"):
			bpy.ops.uv.cursor_set(location=(0, 0))
		elif (self.mode == "L"):
			bpy.ops.uv.cursor_set(location=(0, y/2))
		elif (self.mode == "LU"):
			bpy.ops.uv.cursor_set(location=(0, y))
		return {'FINISHED'}

class Reset2DCursorForPanel(bpy.types.Operator):
	bl_idname = "image.reset_2d_cursor_for_panel"
	bl_label = "Set 2DCursor Position"
	bl_description = "Move 2D cursor to a designated position"

	@classmethod
	def poll(cls, context):
		for a in bpy.context.screen.areas:
			if a.type == 'IMAGE_EDITOR':
				area = a
		if area.spaces[0].mode != 'UV':
			return False
		return True
	def invoke(self, context, event):
		wm = context.window_manager
		return wm.invoke_popup(self)

	def draw(self, context):
		row = self.layout.split(factor=0.33)
		col = row.column()
		col.operator(Reset2DCursor.bl_idname, text="Top Left").mode = 'LU'
		col.operator(Reset2DCursor.bl_idname, text="Left").mode = 'L'
		col.operator(Reset2DCursor.bl_idname, text="Down Left").mode = 'LD'
		col = row.column()
		col.operator(Reset2DCursor.bl_idname, text="Up").mode = 'U'
		col.operator(Reset2DCursor.bl_idname, text="Center").mode = 'C'
		col.operator(Reset2DCursor.bl_idname, text="Down").mode = 'D'
		col = row.column()
		col.operator(Reset2DCursor.bl_idname, text="Top Right").mode = 'RU'
		col.operator(Reset2DCursor.bl_idname, text="Right").mode = 'R'
		col.operator(Reset2DCursor.bl_idname, text="Down Right").mode = 'RD'

	def execute(self, context):
		return {'FINISHED'}

class TogglePanelsA(bpy.types.Operator):
	bl_idname = "image.toggle_panels_a"
	bl_label = "Toggle Panel : 'BOTH'"
	bl_description = "Show BOTH of Sidebar and Toolbar <=> Hide BOTH of them"
	bl_options = {'REGISTER'}

	def execute(self, context):
		toolW = 0
		uiW = 0
		for region in context.area.regions:
			if (region.type == 'TOOLS'):
				toolW = region.width
			if (region.type == 'UI'):
				uiW = region.width
		if (1 < toolW or 1 < uiW):
			if (1 < toolW):
				context.space_data.show_region_toolbar = not context.space_data.show_region_toolbar
			if (1 < uiW):
				context.space_data.show_region_ui = not context.space_data.show_region_ui

		else:
			context.space_data.show_region_toolbar = not context.space_data.show_region_toolbar
			context.space_data.show_region_ui = not context.space_data.show_region_ui
		return {'FINISHED'}

class TogglePanelsB(bpy.types.Operator):
	bl_idname = "image.toggle_panels_b"
	bl_label = "Toggle Panel : 'IN-TURN'"
	bl_description = "Hide BOTH of sidebar and toolbar => Show ONLY toolbar => Show ONLY sidebar => Show BOTH"
	bl_options = {'REGISTER'}

	def execute(self, context):
		toolW = 0
		uiW = 0
		for region in context.area.regions:
			if (region.type == 'TOOLS'):
				toolW = region.width
			if (region.type == 'UI'):
				uiW = region.width
		if (toolW <= 1 and uiW <= 1):
			context.space_data.show_region_toolbar = not context.space_data.show_region_toolbar
		elif (toolW <= 1 and 1 < uiW):
			context.space_data.show_region_toolbar = not context.space_data.show_region_toolbar
		else:
			context.space_data.show_region_toolbar = not context.space_data.show_region_toolbar
			context.space_data.show_region_ui = not context.space_data.show_region_ui
		return {'FINISHED'}

class TogglePanelsC(bpy.types.Operator):
	bl_idname = "image.toggle_panels_c"
	bl_label = "Toggle Panel : 'ONE-SIDE'"
	bl_description = "Hide BOTH of sidebar and toolbar => Show ONLY toolbar  => Show ONLY sidebar"
	bl_options = {'REGISTER'}

	def execute(self, context):
		toolW = 0
		uiW = 0
		for region in context.area.regions:
			if (region.type == 'TOOLS'):
				toolW = region.width
			if (region.type == 'UI'):
				uiW = region.width
		if (toolW <= 1 and uiW <= 1):
			context.space_data.show_region_toolbar = not context.space_data.show_region_toolbar
		elif (1 < toolW and uiW <= 1):
			context.space_data.show_region_toolbar = not context.space_data.show_region_toolbar
			context.space_data.show_region_ui = not context.space_data.show_region_ui
		else:
			context.space_data.show_region_ui = not context.space_data.show_region_ui
		return {'FINISHED'}

class panel_pie_operator(bpy.types.Operator):
	bl_idname = "image.panel_pie_operator"
	bl_label = "Pie menu : Sidebar/Toolbar"
	bl_description = "Toggle sidebar and toolbar's display states"
	bl_options = {'MACRO'}

	def execute(self, context):
		bpy.ops.wm.call_menu_pie(name=PanelPie.bl_idname)
		return {'FINISHED'}
class PanelPie(bpy.types.Menu): #
	bl_idname = "IMAGE_MT_view_pie_panel"
	bl_label = "Pie menu : Sidebar/Toolbar"

	def draw(self, context):
		op = self.layout.menu_pie().operator(run_panel_pie.bl_idname, text="Only Toolbar", icon='TRIA_LEFT')
		op.properties, op.toolshelf = False, True
		op = self.layout.menu_pie().operator(run_panel_pie.bl_idname, text="Only Sidebar", icon='TRIA_RIGHT')
		op.properties, op.toolshelf = True, False
		op = self.layout.menu_pie().operator(run_panel_pie.bl_idname, text="Both Show", icon='ARROW_LEFTRIGHT')
		op.properties, op.toolshelf = True, True
		op = self.layout.menu_pie().operator(run_panel_pie.bl_idname, text="Both Hide", icon='RESTRICT_VIEW_ON')
		op.properties, op.toolshelf = False, False
class run_panel_pie(bpy.types.Operator): #
	bl_idname = "image.run_panel_pie"
	bl_label = "Toggle Panels' Display"
	bl_description = "Toggle sidebar and toolbar's display states"
	bl_options = {'MACRO'}

	properties : BoolProperty(name="Sidebar")
	toolshelf : BoolProperty(name="Toolbar")

	def execute(self, context):
		properties = self.properties
		toolshelf = self.toolshelf
		for region in context.area.regions:
			if (region.type == 'UI'):
				properties = False
				if (1 < region.width):
					properties = True
			if (region.type == 'TOOLS'):
				toolshelf = False
				if (1 < region.width):
					toolshelf = True
		if (properties != self.properties):
			context.space_data.show_region_ui = not context.space_data.show_region_ui
		if (toolshelf != self.toolshelf):
			context.space_data.show_region_toolbar = not context.space_data.show_region_toolbar
		return {'FINISHED'}

################
# サブメニュー #
################

class ShortcutsMenu(bpy.types.Menu):
	bl_idname = "IMAGE_MT_view_shortcuts"
	bl_label = "Toggle Display (For Shortcut)"
	bl_description = "Functions to toggle display states or so that can be used easily by assigning shortcut"

	def draw(self, context):
		self.layout.operator(TogglePanelsA.bl_idname, icon='PLUGIN')
		self.layout.operator(TogglePanelsB.bl_idname, icon='PLUGIN')
		self.layout.operator(TogglePanelsC.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(panel_pie_operator.bl_idname, icon='PLUGIN')

################
# クラスの登録 #
################

classes = [
	Reset2DCursor,
	TogglePanelsA,
	TogglePanelsB,
	TogglePanelsC,
	panel_pie_operator,
	PanelPie,
	run_panel_pie,
	ShortcutsMenu,
	Reset2DCursorForPanel
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
		self.layout.operator(Reset2DCursorForPanel.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.menu(ShortcutsMenu.bl_idname, icon='PLUGIN')
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
