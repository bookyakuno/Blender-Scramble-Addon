# 「3Dビュー」エリア > 「ビュー」メニュー
# "3D View" Area > "View" Menu

import bpy, mathutils
import os, csv
import collections

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
		pre_cursor_location = context.space_data.cursor_location.copy()
		bpy.ops.view3d.localview()
		if (context.space_data.local_view):
			self.report(type={'INFO'}, message="Local")
		else:
			self.report(type={'INFO'}, message="Global")
		context.space_data.cursor_location = pre_cursor_location
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
				bpy.ops.view3d.toolshelf()
			if (1 < uiW):
				bpy.ops.view3d.properties()
		else:
			bpy.ops.view3d.toolshelf()
			bpy.ops.view3d.properties()
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
			bpy.ops.view3d.toolshelf()
		elif (toolW <= 1 and 1 < uiW):
			bpy.ops.view3d.toolshelf()
		else:
			bpy.ops.view3d.toolshelf()
			bpy.ops.view3d.properties()
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
			bpy.ops.view3d.toolshelf()
		elif (1 < toolW and uiW <= 1):
			bpy.ops.view3d.toolshelf()
			bpy.ops.view3d.properties()
		else:
			bpy.ops.view3d.properties()
		return {'FINISHED'}

class ToggleViewportShadeA(bpy.types.Operator):
	bl_idname = "view3d.toggle_viewport_shade_a"
	bl_label = "Shading Switch (Mode A)"
	bl_description = "\"Wireframe\", \"solid\" => \"texture\" shading... We will switch"
	bl_options = {'REGISTER'}
	
	def execute(self, context):
		if (context.space_data.viewport_shade == 'SOLID'):
			context.space_data.viewport_shade = 'TEXTURED'
		elif (context.space_data.viewport_shade == 'TEXTURED'):
			context.space_data.viewport_shade = 'WIREFRAME'
		else:
			context.space_data.viewport_shade = 'SOLID'
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
		self.layout.menu_pie().operator("view3d.viewnumpad", text="Left", icon="TRIA_LEFT").type = "LEFT"
		self.layout.menu_pie().operator("view3d.viewnumpad", text="Right", icon="TRIA_RIGHT").type = "RIGHT"
		self.layout.menu_pie().operator("view3d.viewnumpad", text="Down", icon="TRIA_DOWN").type = "BOTTOM"
		self.layout.menu_pie().operator("view3d.viewnumpad", text="Up", icon="TRIA_UP").type = "TOP"
		self.layout.menu_pie().operator("view3d.viewnumpad", text="Back", icon="BBOX").type = "BACK"
		self.layout.menu_pie().operator("view3d.viewnumpad", text="Camera", icon="CAMERA_DATA").type = "CAMERA"
		self.layout.menu_pie().operator("view3d.viewnumpad", text="Front", icon="SOLID").type = "FRONT"
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
		self.layout.menu_pie().operator(SetViewportShade.bl_idname, text="Bounding Box", icon="BBOX").mode = "BOUNDBOX"
		self.layout.menu_pie().operator(SetViewportShade.bl_idname, text="Render", icon="SMOOTH").mode = "RENDERED"
		self.layout.menu_pie().operator(SetViewportShade.bl_idname, text="Solid", icon="SOLID").mode = "SOLID"
		self.layout.menu_pie().operator(SetViewportShade.bl_idname, text="Texture", icon="POTATO").mode = "TEXTURED"
		self.layout.menu_pie().operator(SetViewportShade.bl_idname, text="Wire Frame", icon="WIRE").mode = "WIREFRAME"
		self.layout.menu_pie().operator(SetViewportShade.bl_idname, text="Material", icon="MATERIAL").mode = "MATERIAL"
class SetViewportShade(bpy.types.Operator): #
	bl_idname = "view3d.set_viewport_shade"
	bl_label = "Shading Switch"
	bl_description = "Toggle Shading"
	bl_options = {'REGISTER', 'UNDO'}
	
	mode = bpy.props.StringProperty(name="Shading", default="SOLID")
	
	def execute(self, context):
		context.space_data.viewport_shade = self.mode
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
	
	def draw(self, context):
		box = self.layout.box()
		column = box.column()
		row = column.row()
		row.label(text="Select layer switch (shift + add choice + CTRL semi-selection + ALT half-clear)", icon='PLUGIN')
		row = column.row()
		operator = row.operator(LayerPieRun.bl_idname, text="01", icon=self.GetIcon(0))
		operator.nr = 1
		operator = row.operator(LayerPieRun.bl_idname, text="02", icon=self.GetIcon(1))
		operator.nr = 2
		operator = row.operator(LayerPieRun.bl_idname, text="03", icon=self.GetIcon(2))
		operator.nr = 3
		operator = row.operator(LayerPieRun.bl_idname, text="04", icon=self.GetIcon(3))
		operator.nr = 4
		operator = row.operator(LayerPieRun.bl_idname, text="05", icon=self.GetIcon(4))
		operator.nr = 5
		row.separator()
		operator = row.operator(LayerPieRun.bl_idname, text="06", icon=self.GetIcon(5))
		operator.nr = 6
		operator = row.operator(LayerPieRun.bl_idname, text="07", icon=self.GetIcon(6))
		operator.nr = 7
		operator = row.operator(LayerPieRun.bl_idname, text="08", icon=self.GetIcon(7))
		operator.nr = 8
		operator = row.operator(LayerPieRun.bl_idname, text="09", icon=self.GetIcon(8))
		operator.nr = 9
		operator = row.operator(LayerPieRun.bl_idname, text="10", icon=self.GetIcon(9))
		operator.nr = 10
		row = column.row()
		operator = row.operator(LayerPieRun.bl_idname, text="11", icon=self.GetIcon(10))
		operator.nr = 11
		operator = row.operator(LayerPieRun.bl_idname, text="12", icon=self.GetIcon(11))
		operator.nr = 12
		operator = row.operator(LayerPieRun.bl_idname, text="13", icon=self.GetIcon(12))
		operator.nr = 13
		operator = row.operator(LayerPieRun.bl_idname, text="14", icon=self.GetIcon(13))
		operator.nr = 14
		operator = row.operator(LayerPieRun.bl_idname, text="15", icon=self.GetIcon(14))
		operator.nr = 15
		row.separator()
		operator = row.operator(LayerPieRun.bl_idname, text="16", icon=self.GetIcon(15))
		operator.nr = 16
		operator = row.operator(LayerPieRun.bl_idname, text="17", icon=self.GetIcon(16))
		operator.nr = 17
		operator = row.operator(LayerPieRun.bl_idname, text="18", icon=self.GetIcon(17))
		operator.nr = 18
		operator = row.operator(LayerPieRun.bl_idname, text="19", icon=self.GetIcon(18))
		operator.nr = 19
		operator = row.operator(LayerPieRun.bl_idname, text="20", icon=self.GetIcon(19))
		operator.nr = 20
	def GetIcon(self, layer):
		isIn = False
		isHalf = False
		objs = []
		for obj in bpy.data.objects:
			if (obj.layers[layer]):
				isIn = True
				objs.append(obj)
		if (objs):
			for obj in objs:
				if (obj.draw_type != 'WIRE'):
					break
			else:
				isHalf = True
		if (bpy.context.scene.layers[layer]):
			if (isHalf):
				return 'WIRE'
			if (isIn):
				return 'RADIOBUT_ON'
			return 'RADIOBUT_OFF'
		else:
			if (isHalf):
				return 'SOLID'
			if (isIn):
				return 'DOT'
			return 'BLANK1'
class LayerPieRun(bpy.types.Operator): #
	bl_idname = "view3d.layer_pie_run"
	bl_label = "Layer Pie Menu"
	bl_description = "Shows or hides layer (shift + add choice + CTRL semi-selection + ALT half-clear)"
	bl_options = {'REGISTER', 'UNDO'}
	
	nr = bpy.props.IntProperty(name="Layer Number")
	extend = bpy.props.BoolProperty(name="Select Extension", default=False)
	half = bpy.props.BoolProperty(name="Half Select", default=False)
	unhalf = bpy.props.BoolProperty(name="Half-Unselect", default=False)
	
	def execute(self, context):
		nr = self.nr - 1
		if (self.half):
			context.scene.layers[nr] = True
			for obj in context.blend_data.objects:
				if (obj.layers[nr]):
					obj.show_all_edges = True
					obj.draw_type = 'WIRE'
		elif (self.unhalf):
			context.scene.layers[nr] = True
			for obj in context.blend_data.objects:
				if (obj.layers[nr]):
					obj.draw_type = 'TEXTURED'
		elif (self.extend):
			context.scene.layers[nr] = not context.scene.layers[nr]
		else:
			context.scene.layers[nr] = not context.scene.layers[nr]
			for i in range(len(context.scene.layers)):
				if (nr != i):
					context.scene.layers[i] = False
		return {'FINISHED'}
	def invoke(self, context, event):
		if (event.ctrl):
			self.extend = False
			self.half = True
			self.unhalf = False
		elif (event.shift):
			self.extend = True
			self.half = False
			self.unhalf = False
		elif (event.alt):
			self.extend = False
			self.half = False
			self.unhalf = True
		else:
			self.extend = False
			self.half = False
			self.unhalf = False
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
	
	properties = bpy.props.BoolProperty(name="Property")
	toolshelf = bpy.props.BoolProperty(name="Tool Shelf")
	
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
			bpy.ops.view3d.properties()
		if (toolshelf != self.toolshelf):
			bpy.ops.view3d.toolshelf()
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
		self.layout.operator(LayerPieOperator.bl_idname, text="Layer", icon='PLUGIN')
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
