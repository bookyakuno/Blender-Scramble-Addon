# 「3Dビュー」エリア > 「ビュー」メニュー
# "3D View" Area > "View" Menu

import bpy, mathutils
import os, csv
import collections
from bpy.props import *

################
# オペレーター #
################

class LocalViewEx(bpy.types.Operator):
	bl_idname = "view3d.local_view_ex"
	bl_label = "Global / local view (non-zoom)"
	bl_description = "Displays only selected objects and centered point of view doesn\'t (zoom)"
	bl_options = {'REGISTER'}

	def execute(self, context):
		pre_smooth_view = context.preferences.view.smooth_view
		context.preferences.view.smooth_view = 0
		pre_view_distance = context.region_data.view_distance
		pre_view_location = context.region_data.view_location.copy()
		pre_view_rotation = context.region_data.view_rotation.copy()
		pre_cursor_location = context.scene.cursor.location.copy()
		bpy.ops.view3d.localview()
		if (context.space_data.local_view):
			self.report(type={'INFO'}, message="Local")
		else:
			self.report(type={'INFO'}, message="Global")
		context.scene.cursor.location = pre_cursor_location
		context.region_data.view_distance = pre_view_distance
		context.region_data.view_location = pre_view_location
		context.region_data.view_rotation = pre_view_rotation
		context.preferences.view.smooth_view = pre_smooth_view
		return {'FINISHED'}

class TogglePanelsA(bpy.types.Operator):
	bl_idname = "view3d.toggle_panels_a"
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
				context.space_data.show_region_toolbar = not context.space_data.show_region_toolbar
			if (1 < uiW):
				context.space_data.show_region_ui = not context.space_data.show_region_ui
		else:
			context.space_data.show_region_toolbar = not context.space_data.show_region_toolbar
			context.space_data.show_region_ui = not context.space_data.show_region_ui
		return {'FINISHED'}

class TogglePanelsB(bpy.types.Operator):
	bl_idname = "view3d.toggle_panels_b"
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
			context.space_data.show_region_toolbar = not context.space_data.show_region_toolbar
		elif (toolW <= 1 and 1 < uiW):
			context.space_data.show_region_toolbar = not context.space_data.show_region_toolbar
		else:
			context.space_data.show_region_toolbar = not context.space_data.show_region_toolbar
			context.space_data.show_region_ui = not context.space_data.show_region_ui
		return {'FINISHED'}

class TogglePanelsC(bpy.types.Operator):
	bl_idname = "view3d.toggle_panels_c"
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
			context.space_data.show_region_toolbar = not context.space_data.show_region_toolbar
		elif (1 < toolW and uiW <= 1):
			context.space_data.show_region_toolbar = not context.space_data.show_region_toolbar
			context.space_data.show_region_ui = not context.space_data.show_region_ui
		else:
			context.space_data.show_region_ui = not context.space_data.show_region_ui
		return {'FINISHED'}

class ToggleViewportShadeA(bpy.types.Operator):
	bl_idname = "view3d.toggle_viewport_shade_a"
	bl_label = "Shading Switch"
	bl_description = "Wireframe => Solid => Material => Rendered (modifiable)"
	bl_options = {'REGISTER', 'UNDO'}

	items = [
			("WIREFRAME", "Wireframe", "", 1),	("SOLID", "Solid", "", 2),
			("MATERIAL", "Material", "", 3), ("RENDERED", "Rendered", "", 4)
		]
	FirstItem : EnumProperty(name="1st ", items=items)
	SecondItem : EnumProperty(name="2nd ", items=[items[1],items[0],items[2],items[3]])
	ThirdItem : EnumProperty(name="3rd ", items=[items[2],items[1],items[0],items[3]])
	FourthItem : EnumProperty(name="4th ", items=[items[3],items[0],items[1],items[2]])
	methods = [
			("FOURLOOP", "1-2-3-4 loop", "", 1),
			("THREELOOP", "1-2-3 loop", "", 2),
			("TWOLOOP", "1-2 loop", "", 3),
		]
	loopMethod : EnumProperty(name="Loop Method", items=methods)

	def execute(self, context):
		if (context.space_data.shading.type == self.FirstItem):
			context.space_data.shading.type = self.SecondItem
		elif (context.space_data.shading.type == self.SecondItem):
			if self.loopMethod == "TWOLOOP":
				context.space_data.shading.type = self.FirstItem
			else:
				context.space_data.shading.type  = self.ThirdItem
		elif (context.space_data.shading.type == self.ThirdItem):
			if self.loopMethod == "FOURLOOP":
				context.space_data.shading.type  = self.FourthItem
			else:
				context.space_data.shading.type  = self.FirstItem
		else:
			context.space_data.shading.type = self.FirstItem
		return {'FINISHED'}

################
# パイメニュー #
################

class ViewNumpadPieOperator(bpy.types.Operator):
	bl_idname = "view3d.view_numpad_pie_operator"
	bl_label = "Preset View"
	bl_description = "Is pie menu of preset views or (NUMPAD 1, 3, 7)"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		bpy.ops.wm.call_menu_pie(name=ViewNumpadPie.bl_idname)
		return {'FINISHED'}
class ViewNumpadPie(bpy.types.Menu): #
	bl_idname = "VIEW3D_MT_view_pie_view_numpad"
	bl_label = "Preset View"
	bl_description = "Is pie menu of preset views or (NUMPAD 1, 3, 7)"

	def draw(self, context):
		self.layout.menu_pie().operator("view3d.view_axis", text="Left", icon="TRIA_LEFT").type = "LEFT"
		self.layout.menu_pie().operator("view3d.view_axis", text="Right", icon="TRIA_RIGHT").type = "RIGHT"
		self.layout.menu_pie().operator("view3d.view_axis", text="Down", icon="TRIA_DOWN").type = "BOTTOM"
		self.layout.menu_pie().operator("view3d.view_axis", text="Up", icon="TRIA_UP").type = "TOP"
		self.layout.menu_pie().operator("view3d.view_axis", text="Back", icon="SHADING_BBOX").type = "BACK"
		self.layout.menu_pie().operator("view3d.view_camera", text="Camera", icon="CAMERA_DATA")
		self.layout.menu_pie().operator("view3d.view_axis", text="Front", icon="SHADING_SOLID").type = "FRONT"
		self.layout.menu_pie().operator("view3d.view_persportho", text="Perspective/Orthographic", icon="BORDERMOVE")

class ViewportShadePieOperator(bpy.types.Operator):
	bl_idname = "view3d.viewport_shade_pie_operator"
	bl_label = "Shading Switch"
	bl_description = "Is shading switch pie"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		bpy.ops.wm.call_menu_pie(name=ViewportShadePie.bl_idname)
		return {'FINISHED'}
class ViewportShadePie(bpy.types.Menu): #
	bl_idname = "VIEW3D_MT_view_pie_viewport_shade"
	bl_label = "Shading Switch"
	bl_description = "Is shading switch pie"

	def draw(self, context):
		self.layout.menu_pie().operator(SetViewportShade.bl_idname, text="Render", icon="SHADING_TEXTURE").mode = "RENDERED"
		self.layout.menu_pie().operator(SetViewportShade.bl_idname, text="Solid", icon="SHADING_SOLID").mode = "SOLID"
		self.layout.menu_pie().operator(SetViewportShade.bl_idname, text="Wire Frame", icon="SHADING_WIRE").mode = "WIREFRAME"
		self.layout.menu_pie().operator(SetViewportShade.bl_idname, text="Material", icon="MATERIAL").mode = "MATERIAL"
class SetViewportShade(bpy.types.Operator): #
	bl_idname = "view3d.set_viewport_shade"
	bl_label = "Shading Switch"
	bl_description = "Toggle Shading"
	bl_options = {'REGISTER', 'UNDO'}

	mode : StringProperty(name="Shading", default="SOLID")

	def execute(self, context):
		context.space_data.shading.type = self.mode
		return {'FINISHED'}

class LayerPieOperator(bpy.types.Operator):
	bl_idname = "view3d.layer_pie_operator"
	bl_label = "Layer Pie Menu"
	bl_description = "Is pie menu toggle layer visibility"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		bpy.ops.wm.call_menu_pie(name=LayerPie.bl_idname)
		return {'FINISHED'}
class LayerPie(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_pie_layer"
	bl_label = "Layer Pie Menu"
	bl_description = "Is pie menu toggle layer visibility"

	def flatten(self, layer_collection, parent_name=""):
		flat = []
		for coll in layer_collection.children:
			if len(coll.children) > 0:
				flat.append((coll, f"{parent_name},{layer_collection.name}"))
				flat += self.flatten(coll, f"{parent_name},{layer_collection.name}")
			else:
				flat.append((coll, f"{parent_name},{layer_collection.name}"))
		return flat

	def draw(self, context):
		box = self.layout.box()
		column = box.column()
		row = column.row()
		row.label(text="Toggle collection show/hide (shift: Wireframe, ctrl:Hide others)", icon='PLUGIN')
		row = column.row()
		for col in context.view_layer.layer_collection.children:
			column = row.column()
			operator = column.operator(LayerPieRun.bl_idname, text=f"{col.name}", icon=self.GetIcon(col))
			operator.name = col.name
			operator.parent_names = ""
			flatten_nest = self.flatten(col)
			for coll in flatten_nest:
				operator = column.operator(LayerPieRun.bl_idname, text=f"{coll[0].name}", icon=self.GetIcon(coll[0]))
				operator.name = coll[0].name
				operator.parent_names = coll[1]
	def GetIcon(self, layer_collection):
		if layer_collection.hide_viewport:
			return "HIDE_ON"
		for obj in layer_collection.collection.objects[:5]:
			if (obj.display_type != 'WIRE'):
				return "HIDE_OFF"
		else:
			return 'SHADING_WIRE'
class LayerPieRun(bpy.types.Operator): #
	bl_idname = "view3d.layer_pie_run"
	bl_label = "Layer Pie Menu"
	bl_description = "Shows or hides collection"
	bl_options = {'REGISTER', 'UNDO'}

	name : StringProperty(name="Collection Name")
	parent_names : StringProperty(name="Parent-Collections\' Names")
	exclusive : BoolProperty(name="Hide Others", default=False)
	wire : BoolProperty(name="Wireframe", default=False)
	#unhalf : BoolProperty(name="Half-Unselect", default=False)

	def execute(self, context):
		par_names = [x for x in self.parent_names.split(",") if not len(x) == 0]
		if not par_names:
			coll = context.view_layer.layer_collection.children[self.name]
			if (self.exclusive):
				for col in context.view_layer.layer_collection.children:
					if col.name != self.name: col.hide_viewport = True
		else:
			par = context.view_layer.layer_collection.children[par_names[0]]
			if (self.exclusive):
				for col in context.view_layer.layer_collection.children:
					if col.name != par_names[0]: col.hide_viewport = True
			try:
				for name in par_names[1:]:
					if (self.exclusive):
						for col in par.children:
							if col.name != name: col.hide_viewport = True
					par = par.children[name]
			except IndexError:
				pass		
			coll = par.children[self.name]
		if (self.exclusive):
			coll.hide_viewport = False
			return {'FINISHED'}
		if (self.wire):
			for obj in coll.collection.objects:
				obj.show_all_edges = True
				if obj.display_type != 'WIRE':
					obj.display_type = 'WIRE'
				else:
					obj.display_type = 'TEXTURED'
		#elif (not self.unhalf):
		#	context.scene.layers[nr] = True
		#	for obj in context.blend_data.objects:
		#		if (obj.layers[nr]):
		#			obj.display_type = 'TEXTURED'
		else:
			coll.hide_viewport = not coll.hide_viewport
		return {'FINISHED'}
	def invoke(self, context, event):
		if (event.ctrl):
			self.exclusive = True
			self.wire = False
			#self.unhalf = False
		elif (event.shift):
			self.exclusive = False
			self.wire = True
			#self.unhalf = False
		elif (event.alt):
			self.exclusive = False
			self.wire = False
			#self.unhalf = True
		else:
			self.exclusive = False
			self.wire = False
			#self.unhalf = False
		return self.execute(context)

class PanelPieOperator(bpy.types.Operator):
	bl_idname = "view3d.panel_pie_operator"
	bl_label = "Switch panel pie menu"
	bl_description = "Toggle panel pie menu"
	bl_options = {'MACRO'}

	def execute(self, context):
		bpy.ops.wm.call_menu_pie(name=PanelPie.bl_idname)
		return {'FINISHED'}
class PanelPie(bpy.types.Menu): #
	bl_idname = "VIEW3D_MT_view_pie_panel"
	bl_label = "Switch panel pie menu"
	bl_description = "Toggle panel pie menu"

	def draw(self, context):
		op = self.layout.menu_pie().operator(RunPanelPie.bl_idname, text="Only Tool Shelf", icon='TRIA_LEFT')
		op.properties, op.toolshelf = False, True
		op = self.layout.menu_pie().operator(RunPanelPie.bl_idname, text="Only Properties", icon='TRIA_RIGHT')
		op.properties, op.toolshelf = True, False
		op = self.layout.menu_pie().operator(RunPanelPie.bl_idname, text="Double Sided", icon='ARROW_LEFTRIGHT')
		op.properties, op.toolshelf = True, True
		op = self.layout.menu_pie().operator(RunPanelPie.bl_idname, text="Hide", icon='RESTRICT_VIEW_ON')
		op.properties, op.toolshelf = False, False
class RunPanelPie(bpy.types.Operator): #
	bl_idname = "view3d.run_panel_pie"
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
			context.space_data.show_region_ui = not context.space_data.show_region_ui
			#bpy.ops.view3d.properties()
		if (toolshelf != self.toolshelf):
			context.space_data.show_region_toolbar = not context.space_data.show_region_toolbar
			#bpy.ops.view3d.toolshelf()
		return {'FINISHED'}

################
# サブメニュー #
################

class ShortcutsMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_view_shortcuts"
	bl_label = "By Shortcuts"
	bl_description = "Registering shortcut feature that might come in handy"

	def draw(self, context):
		self.layout.operator(LocalViewEx.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(TogglePanelsA.bl_idname, icon='PLUGIN')
		self.layout.operator(TogglePanelsB.bl_idname, icon='PLUGIN')
		self.layout.operator(TogglePanelsC.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(ToggleViewportShadeA.bl_idname, icon='PLUGIN')

class PieMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_view_pie"
	bl_label = "Pie Menu"
	bl_description = "This is pie menu of 3D view"

	def draw(self, context):
		self.layout.operator(ViewNumpadPieOperator.bl_idname, icon='PLUGIN')
		self.layout.operator(ViewportShadePieOperator.bl_idname, icon='PLUGIN')
		self.layout.operator(LayerPieOperator.bl_idname, text="Collection", icon='PLUGIN')
		self.layout.operator(PanelPieOperator.bl_idname, text="Panel Switch", icon='PLUGIN')

################
# クラスの登録 #
################

classes = [
	LocalViewEx,
	TogglePanelsA,
	TogglePanelsB,
	TogglePanelsC,
	ToggleViewportShadeA,
	ViewNumpadPieOperator,
	ViewNumpadPie,
	ViewportShadePieOperator,
	ViewportShadePie,
	SetViewportShade,
	LayerPieOperator,
	LayerPie,
	LayerPieRun,
	PanelPieOperator,
	PanelPie,
	RunPanelPie,
	ShortcutsMenu,
	PieMenu
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
		self.layout.menu(ShortcutsMenu.bl_idname, icon='PLUGIN')
		self.layout.menu(PieMenu.bl_idname, icon='PLUGIN')
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
