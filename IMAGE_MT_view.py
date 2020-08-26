# 「UV/画像エディター」エリア > 「ビュー」メニュー
# "UV/Image Editor" Area > "View" Menu

import bpy
from bpy.props import *

################
# オペレーター #
################

class Reset2DCursor(bpy.types.Operator):
	bl_idname = "image.reset_2d_cursor"
	bl_label = "Reset Cursor Position"
	bl_description = "Move 2D cursor in lower left"
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
		if (bpy.context.edit_image):
			x, y = (1,1)
		else:
			x = 1
			y = 1

		area = None
		for area in bpy.context.screen.areas:
			if area.type == 'IMAGE_EDITOR':
				area
		if not area:
			self.report({'INFO'}, "Not found Image Editor !!")
			return{'FINISHED'}
			
		if (self.mode == "C"):
			area.spaces[0].cursor_location = [x/2, y/2]
		elif (self.mode == "U"):
			area.spaces[0].cursor_location = [x/2, y]
		elif (self.mode == "RU"):
			area.spaces[0].cursor_location = [x, y]
		elif (self.mode == "R"):
			area.spaces[0].cursor_location = [x, y/2]
		elif (self.mode == "RD"):
			area.spaces[0].cursor_location = [x, 0]
		elif (self.mode == "D"):
			area.spaces[0].cursor_location = [x/2, 0]
		elif (self.mode == "LD"):
			area.spaces[0].cursor_location = [0, 0]
		elif (self.mode == "L"):
			area.spaces[0].cursor_location = [0, y/2]
		elif (self.mode == "LU"):
			area.spaces[0].cursor_location = [0, y]
		return {'FINISHED'}

class TogglePanelsA(bpy.types.Operator):
	bl_idname = "image.toggle_panels_a"
	bl_label = "Toggle Panel (mode A)"
	bl_description = "properties/tool shelf \"both display\" / \"both hide\" toggle"
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
				bpy.ops.image.toolshelf()
			if (1 < uiW):
				bpy.ops.image.properties()
		else:
			bpy.ops.image.toolshelf()
			bpy.ops.image.properties()
		return {'FINISHED'}

class TogglePanelsB(bpy.types.Operator):
	bl_idname = "image.toggle_panels_b"
	bl_label = "Toggle Panel (mode B)"
	bl_description = "\"Panel both hide\" => show only tool shelf => show only properties => \"Panel both display\" for toggle"
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
			bpy.ops.image.toolshelf()
		elif (toolW <= 1 and 1 < uiW):
			bpy.ops.image.toolshelf()
		else:
			bpy.ops.image.toolshelf()
			bpy.ops.image.properties()
		return {'FINISHED'}

class TogglePanelsC(bpy.types.Operator):
	bl_idname = "image.toggle_panels_c"
	bl_label = "Toggle Panel (mode C)"
	bl_description = "\"Panel both hide\" => \"show only tool shelf => show only properties. toggle"
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
			bpy.ops.image.toolshelf()
		elif (1 < toolW and uiW <= 1):
			bpy.ops.image.toolshelf()
			bpy.ops.image.properties()
		else:
			bpy.ops.image.properties()
		return {'FINISHED'}

class panel_pie_operator(bpy.types.Operator):
	bl_idname = "image.panel_pie_operator"
	bl_label = "Switch panel pie menu"
	bl_description = "Toggle panel pie menu"
	bl_options = {'MACRO'}

	def execute(self, context):
		bpy.ops.wm.call_menu_pie(name=PanelPie.bl_idname)
		return {'FINISHED'}
class PanelPie(bpy.types.Menu): #
	bl_idname = "IMAGE_MT_view_pie_panel"
	bl_label = "Switch panel pie menu"
	bl_description = "Toggle panel pie menu"

	def draw(self, context):
		op = self.layout.menu_pie().operator(run_panel_pie.bl_idname, text="Only Tool Shelf", icon='TRIA_LEFT')
		op.properties, op.toolshelf = False, True
		op = self.layout.menu_pie().operator(run_panel_pie.bl_idname, text="Only Properties", icon='TRIA_RIGHT')
		op.properties, op.toolshelf = True, False
		op = self.layout.menu_pie().operator(run_panel_pie.bl_idname, text="Double Sided", icon='ARROW_LEFTRIGHT')
		op.properties, op.toolshelf = True, True
		op = self.layout.menu_pie().operator(run_panel_pie.bl_idname, text="Hide", icon='RESTRICT_VIEW_ON')
		op.properties, op.toolshelf = False, False
class run_panel_pie(bpy.types.Operator): #
	bl_idname = "image.run_panel_pie"
	bl_label = "Switch panel pie menu"
	bl_description = "Toggle panel pie menu"
	bl_options = {'MACRO'}

	properties : BoolProperty(name="Property")
	toolshelf : BoolProperty(name="Tool Shelf")

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
			bpy.ops.image.properties()
		if (toolshelf != self.toolshelf):
			bpy.ops.image.toolshelf()
		return {'FINISHED'}

################
# サブメニュー #
################

class ShortcutsMenu(bpy.types.Menu):
	bl_idname = "IMAGE_MT_view_shortcuts"
	bl_label = "By Shortcuts"
	bl_description = "Registering shortcut feature that might come in handy"

	def draw(self, context):
		self.layout.operator(TogglePanelsA.bl_idname, icon='PLUGIN')
		self.layout.operator(TogglePanelsB.bl_idname, icon='PLUGIN')
		self.layout.operator(TogglePanelsC.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(panel_pie_operator.bl_idname, icon='PLUGIN')

class Reset2DCursorMenu(bpy.types.Menu):
	bl_idname = "IMAGE_MT_view_reset_2d_cursor"
	bl_label = "Reset Cursor Position"
	bl_description = "Reset Cursor Position"

	def draw(self, context):
		self.layout.operator(Reset2DCursor.bl_idname, icon='PLUGIN', text="Up").mode = 'U'
		self.layout.operator(Reset2DCursor.bl_idname, icon='PLUGIN', text="Right").mode = 'R'
		self.layout.operator(Reset2DCursor.bl_idname, icon='PLUGIN', text="Down").mode = 'D'
		self.layout.operator(Reset2DCursor.bl_idname, icon='PLUGIN', text="Left").mode = 'L'
		self.layout.separator()
		self.layout.operator(Reset2DCursor.bl_idname, icon='PLUGIN', text="Top Right").mode = 'RU'
		self.layout.operator(Reset2DCursor.bl_idname, icon='PLUGIN', text="Down Right").mode = 'RD'
		self.layout.operator(Reset2DCursor.bl_idname, icon='PLUGIN', text="Down Left").mode = 'LD'
		self.layout.operator(Reset2DCursor.bl_idname, icon='PLUGIN', text="Top Left").mode = 'LU'
		self.layout.separator()
		self.layout.operator(Reset2DCursor.bl_idname, icon='PLUGIN', text="Center").mode = 'C'

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
	Reset2DCursorMenu
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
		self.layout.menu(Reset2DCursorMenu.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.menu(ShortcutsMenu.bl_idname, icon='PLUGIN')
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
