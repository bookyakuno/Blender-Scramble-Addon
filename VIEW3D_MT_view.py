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
	bl_label = "Toggle Local View (Keep Current)"
	bl_description = "Switch to display of selected objects separately keeping current location and distance"
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
			self.report(type={'INFO'}, message="Local View")
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
	bl_idname = "view3d.toggle_panels_b"
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
	bl_idname = "view3d.toggle_panels_c"
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

class ToggleViewportShadeA(bpy.types.Operator):
	bl_idname = "view3d.toggle_viewport_shade_a"
	bl_label = "Switch Viewport Shading"
	bl_description = "Switch viewport shading in designated order"
	bl_options = {'REGISTER', 'UNDO'}

	items = [("WIREFRAME", "Wireframe", "", 1),	("SOLID", "Solid", "", 2),
			("MATERIAL", "Material", "", 3), ("RENDERED", "Rendered", "", 4)]
	first : EnumProperty(name="1st ", items=items)
	second : EnumProperty(name="2nd ", items=[items[1],items[0],items[2],items[3]])
	third : EnumProperty(name="3rd ", items=[items[2],items[1],items[0],items[3]])
	fourth : EnumProperty(name="4th ", items=[items[3],items[0],items[1],items[2]])
	methods = [
			("4", "1-2-3-4", "", 1),
			("3", "1-2-3", "", 2),
			("2", "1-2", "", 3),
		]
	loopMethod : EnumProperty(name="Loop", items=methods)
	index : IntProperty(name="Index", default=0, options={'HIDDEN'})

	def draw(self, context):
		row = self.layout.split(factor=0.2)
		row.label(text="Loop")
		row.prop(self, 'loopMethod', expand=True)
		for p in ['first', 'second', 'third', 'fourth']:
			row = self.layout.row()
			row.use_property_split = True
			if p == 'third':
				row.enabled = (self.loopMethod in ["3","4"])
			elif p == 'fourth':
				row.enabled = (self.loopMethod == "4")
			row.prop(self, p)

	def execute(self, context):
		items = [self.first, self.second,self.third,self.fourth][:int(self.loopMethod)]
		try:
			context.space_data.shading.type = items[self.index+1]
			self.index += 1
		except IndexError:
			context.space_data.shading.type = items[0]
			self.index = 0
		self.temp = self.loopMethod
		return {'FINISHED'}

class ProjectEditEX(bpy.types.Operator):
	bl_idname = "image.project_edit_ex"
	bl_label = "Edit Screenshot with Editors"
	bl_description = "Take a screenshot of viewport and edit it in the external image editor referenced at User Preference"
	bl_options = {'REGISTER'}

	index : IntProperty(name="Number of Use", default=1, min=1, max=3, soft_min=1, soft_max=3)

	def execute(self, context):
		pre_path = context.preferences.filepaths.image_editor
		if (self.index == 1):
			context.preferences.filepaths.image_editor = context.preferences.addons[__name__.partition('.')[0]].preferences.image_editor_path_1
		elif (self.index == 2):
			context.preferences.filepaths.image_editor = context.preferences.addons[__name__.partition('.')[0]].preferences.image_editor_path_2
		elif (self.index == 3):
			context.preferences.filepaths.image_editor = context.preferences.addons[__name__.partition('.')[0]].preferences.image_editor_path_3
		bpy.ops.image.project_edit()
		context.preferences.filepaths.image_editor = pre_path
		return {'FINISHED'}

class OldSnapMenuOperator(bpy.types.Operator):
	bl_idname = "view3d.old_snap_menu_operator"
	bl_label = "Snap Menu (Blender 2.7)"
	bl_description = "Display snap menu panel used in Blender 2.7"
	bl_options = {'REGISTER'}

	def execute(self, context):
		bpy.ops.wm.call_menu(name='VIEW3D_MT_snap')
		return {'FINISHED'}

################
# パイメニュー #
################

class ViewNumpadPieOperator(bpy.types.Operator):
	bl_idname = "view3d.view_numpad_pie_operator"
	bl_label = "Pie Menu: Viewport"
	bl_description = "Switch a preset viewport"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		bpy.ops.wm.call_menu_pie(name=ViewNumpadPie.bl_idname)
		return {'FINISHED'}

class ViewNumpadPie(bpy.types.Menu): #
	bl_idname = "VIEW3D_MT_view_pie_view_numpad"
	bl_label = "Pie Menu: Viewport"
	bl_description = "Switch a preset viewport"

	def draw(self, context):
		self.layout.menu_pie().operator("view3d.view_axis", text="Left", icon="TRIA_LEFT").type = "LEFT"
		self.layout.menu_pie().operator("view3d.view_axis", text="Right", icon="TRIA_RIGHT").type = "RIGHT"
		self.layout.menu_pie().operator("view3d.view_axis", text="Bottom", icon="TRIA_DOWN").type = "BOTTOM"
		self.layout.menu_pie().operator("view3d.view_axis", text="Top", icon="TRIA_UP").type = "TOP"
		self.layout.menu_pie().operator("view3d.view_axis", text="Back", icon="SHADING_BBOX").type = "BACK"
		self.layout.menu_pie().operator("view3d.view_camera", text="Camera", icon="CAMERA_DATA")
		self.layout.menu_pie().operator("view3d.view_axis", text="Front", icon="SHADING_SOLID").type = "FRONT"
		self.layout.menu_pie().operator("view3d.view_persportho", text="Perspective/Orthographic", icon="BORDERMOVE")

class ViewportShadePieOperator(bpy.types.Operator):
	bl_idname = "view3d.viewport_shade_pie_operator"
	bl_label = "Pie Menu: Viewport Shading"
	bl_description = "Switch viewport shading"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		bpy.ops.wm.call_menu_pie(name=ViewportShadePie.bl_idname)
		return {'FINISHED'}

class ViewportShadePie(bpy.types.Menu): #
	bl_idname = "VIEW3D_MT_view_pie_viewport_shade"
	bl_label = "Pie Menu: Viewport Shading"
	bl_description = "Switch viewport shading"

	def draw(self, context):
		self.layout.menu_pie().operator(SetViewportShade.bl_idname, text="Rendered", icon="SHADING_TEXTURE").mode = "RENDERED"
		self.layout.menu_pie().operator(SetViewportShade.bl_idname, text="Solid", icon="SHADING_SOLID").mode = "SOLID"
		self.layout.menu_pie().operator(SetViewportShade.bl_idname, text="Wireframe", icon="SHADING_WIRE").mode = "WIREFRAME"
		self.layout.menu_pie().operator(SetViewportShade.bl_idname, text="Material", icon="MATERIAL").mode = "MATERIAL"

class SetViewportShade(bpy.types.Operator): #
	bl_idname = "view3d.set_viewport_shade"
	bl_label = "Switch Viewport Shading"
	bl_description = "Switch viewport shading"
	bl_options = {'REGISTER', 'UNDO'}

	mode : StringProperty(name="Shading", default="SOLID")

	def execute(self, context):
		context.space_data.shading.type = self.mode
		return {'FINISHED'}

class CollectionDisplayOperator(bpy.types.Operator):
	bl_idname = "view3d.collection_display_operator"
	bl_label = "Switch Collections Display"
	bl_description = "Switch display state of each collection"
	bl_options = {'REGISTER','UNDO'}

	def invoke(self, context, event):
		return context.window_manager.invoke_popup(self)
	def flatten(self, layer_collection):
		flat = []
		for coll in layer_collection.children:
			if len(coll.children) > 0:
				flat.append(coll)
				flat += self.flatten(coll)
			else:
				flat.append(coll)
				flat.append(None)
		return flat
	def GetIcon(self, layer_collection, TYPE=None):
		if not TYPE:
			if layer_collection.hide_viewport:
				return "HIDE_ON"
			else:
				return "HIDE_OFF"
		elif TYPE == 'WIRE':
			for obj in layer_collection.collection.objects[:5]:
				if (obj.display_type != 'WIRE'):
					return "SHADING_TEXTURE"
			else:
				return 'SHADING_WIRE'
		elif TYPE == 'OBJ_ACTIVE':
			for obj in layer_collection.collection.objects[:5]:
				if (obj.hide_get() == False):
					return 'KEYTYPE_KEYFRAME_VEC'
			else:
				return 'KEYTYPE_JITTER_VEC'
		elif TYPE == 'OBJ_OTHER':
			for obj in layer_collection.collection.objects[:5]:
				if (obj.hide_get() == False):
					return 'HANDLETYPE_AUTO_VEC'
			else:
				return 'HANDLETYPE_VECTOR_VEC'
	def make_collec_dic(self, layer_collection, dictionary, idx=1):
		for coll in layer_collection.children:
			dictionary[coll.name] = {"self":coll, "idx":idx}
			idx += 1
			if len(coll.children) > 0:
				dictionary = self.make_collec_dic(coll, dictionary, idx)
		return dictionary

	def draw(self, context):
		dic = {}
		collec_dic = self.make_collec_dic(context.view_layer.layer_collection, dic)
		if context.view_layer.objects.active:
			obj_par_collection = context.view_layer.objects.active.users_collection[0].name
		else:
			obj_par_collection = ""
		row = self.layout.split(factor=0.45)
		row.label(text="")
		row.operator(CollectionShowHide.bl_idname, text="Show All", icon='NONE').is_all = "SHOW"
		row.operator(CollectionShowHide.bl_idname, text="Hide All", icon='NONE').is_all = "HIDE"
		root = self.layout.box()
		for col in context.view_layer.layer_collection.children:
			branch = root.box()
			item = branch.row()
			if col.name == obj_par_collection:
				item.operator(CollectionObjectsShowHide.bl_idname, text="", icon=self.GetIcon(col, TYPE='OBJ_ACTIVE') ).name = col.name
			else:
				item.operator(CollectionObjectsShowHide.bl_idname, text="", icon=self.GetIcon(col, TYPE='OBJ_OTHER')).name = col.name
			item.operator("object.hide_collection", text=f"{col.name}", icon='NONE', emboss=False).collection_index = collec_dic[col.name]["idx"]
			op =item.operator(CollectionShowHide.bl_idname, text="", icon=self.GetIcon(col), emboss=False)
			op.name, op.is_all = [col.name, 'SINGLE']
			item.operator(CollectionWireFrame.bl_idname, text="", icon=self.GetIcon(col, TYPE="WIRE"), emboss=False).name = col.name
			flatten_nest = self.flatten(col)
			for coll in flatten_nest:
				if coll == None:
					branch.separator(factor=0.3)
				else:
					item2 = branch.row()
					if coll.name == obj_par_collection:
						item2.operator(CollectionObjectsShowHide.bl_idname, text="", icon=self.GetIcon(coll, TYPE='OBJ_ACTIVE')).name = coll.name
					else:
						item2.operator(CollectionObjectsShowHide.bl_idname, text="", icon=self.GetIcon(coll, TYPE='OBJ_OTHER')).name = coll.name
					item2.operator("object.hide_collection", text=f"{coll.name}", icon='NONE', emboss=False).collection_index = collec_dic[coll.name]["idx"]
					op = item2.operator(CollectionShowHide.bl_idname, text="", icon=self.GetIcon(coll), emboss=False)
					op.name, op.is_all = [coll.name, 'SINGLE']
					item2.operator(CollectionWireFrame.bl_idname, text="", icon=self.GetIcon(coll, TYPE="WIRE"), emboss=False).name = coll.name
			branch.separator(factor=1.0)
	def execute(self, context):
		return {"FINISHED"}

class CollectionShowHide(bpy.types.Operator):
	bl_idname = "view3d.collection_show_hide"
	bl_label = "Show / Hide Collection"
	bl_description = "Shows or hides the collection"
	bl_options = {'REGISTER'}

	name : StringProperty(name="Collection Name")
	items = [
		("SINGLE", "Single target", "", 1),
		("SHOW", "Show all", "", 2),
		("HIDE", "Hide all", "", 3)
	]
	is_all : EnumProperty(name="Show/hide all collections", items=items)

	def make_collec_dic(self, layer_collection, dictionary, idx=1):
		for coll in layer_collection.children:
			dictionary[coll.name] = {"self":coll, "idx":idx}
			idx += 1
			if len(coll.children) > 0:
				dictionary = self.make_collec_dic(coll, dictionary, idx)
		return dictionary
	def execute(self, context):
		dic = {}
		collec_dic = self.make_collec_dic(context.view_layer.layer_collection, dic)
		if self.is_all == "SINGLE":
			target = collec_dic[self.name]["self"]
			target.hide_viewport = not target.hide_viewport
		elif self.is_all == "SHOW":
			for key in collec_dic.keys():
				collec_dic[key]["self"].hide_viewport = False
		elif self.is_all == "HIDE":
			for key in collec_dic.keys():
				collec_dic[key]["self"].hide_viewport = True
		return {'FINISHED'}

class CollectionWireFrame(bpy.types.Operator):
	bl_idname = "view3d.collection_show_as_wireframe"
	bl_label = "Switch Textured / Wireframe"
	bl_description = "Display objects in collection as wire edges or textured"
	bl_options = {'REGISTER'}

	name : StringProperty(name="Collection Name")

	def make_collec_dic(self, layer_collection, dictionary, idx=1):
		for coll in layer_collection.children:
			dictionary[coll.name] = {"self":coll, "idx":idx}
			idx += 1
			if len(coll.children) > 0:
				dictionary = self.make_collec_dic(coll, dictionary, idx)
		return dictionary
	def execute(self, context):
		dic = {}
		collec_dic = self.make_collec_dic(context.view_layer.layer_collection, dic)
		target = collec_dic[self.name]["self"]
		for obj in target.collection.objects:
			obj.show_all_edges = True
			if obj.display_type != 'WIRE':
				obj.display_type = 'WIRE'
			else:
				obj.display_type = 'TEXTURED'
		return {'FINISHED'}

class CollectionObjectsShowHide(bpy.types.Operator):
	bl_idname = "view3d.collection_objects_show_hide"
	bl_label = "Show / Hide Contained Objects"
	bl_description = "Show or hide all objects in collection"
	bl_options = {'REGISTER'}

	name : StringProperty(name="Collection Name")

	def make_collec_dic(self, layer_collection, dictionary, idx=1):
		for coll in layer_collection.children:
			dictionary[coll.name] = {"self":coll, "idx":idx}
			idx += 1
			if len(coll.children) > 0:
				dictionary = self.make_collec_dic(coll, dictionary, idx)
		return dictionary
	def execute(self, context):
		dic = {}
		collec_dic = self.make_collec_dic(context.view_layer.layer_collection, dic)
		target = collec_dic[self.name]["self"]
		for obj in target.collection.objects[:5]:
			if obj.hide_get() == False:
				is_show = False
				break
		else:
			is_show = True
		if is_show:
			for obj in target.collection.objects: obj.hide_set(False)
		else:
			for obj in target.collection.objects: obj.hide_set(True)
		return {'FINISHED'}

class PanelPieOperator(bpy.types.Operator):
	bl_idname = "view3d.panel_pie_operator"
	bl_label = "Pie Menu : Sidebar/Toolbar"
	bl_description = "Toggle sidebar and toolbar's display states"
	bl_options = {'MACRO'}

	def execute(self, context):
		bpy.ops.wm.call_menu_pie(name=PanelPie.bl_idname)
		return {'FINISHED'}

class PanelPie(bpy.types.Menu): #
	bl_idname = "VIEW3D_MT_view_pie_panel"
	bl_label = "Pie menu : Sidebar/Toolbar"
	bl_description = "Toggle sidebar and toolbar's display states"

	def draw(self, context):
		op = self.layout.menu_pie().operator(RunPanelPie.bl_idname, text="Only Toolbar", icon='TRIA_LEFT')
		op.properties, op.toolshelf = False, True
		op = self.layout.menu_pie().operator(RunPanelPie.bl_idname, text="Only Sidebar", icon='TRIA_RIGHT')
		op.properties, op.toolshelf = True, False
		op = self.layout.menu_pie().operator(RunPanelPie.bl_idname, text="Both Show", icon='ARROW_LEFTRIGHT')
		op.properties, op.toolshelf = True, True
		op = self.layout.menu_pie().operator(RunPanelPie.bl_idname, text="Both Hide", icon='RESTRICT_VIEW_ON')
		op.properties, op.toolshelf = False, False

class RunPanelPie(bpy.types.Operator): #
	bl_idname = "view3d.run_panel_pie"
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
	bl_idname = "VIEW3D_MT_view_shortcuts"
	bl_label = "Toggle Display (For Shortcut)"
	bl_description = "Functions to toggle display states or so that can be used easily by assigning shortcut"

	def draw(self, context):
		self.layout.operator(ViewNumpadPieOperator.bl_idname, icon='PLUGIN')
		self.layout.operator(ViewportShadePieOperator.bl_idname, icon='PLUGIN')
		self.layout.operator(PanelPieOperator.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(TogglePanelsA.bl_idname, icon='PLUGIN')
		self.layout.operator(TogglePanelsB.bl_idname, icon='PLUGIN')
		self.layout.operator(TogglePanelsC.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(LocalViewEx.bl_idname, icon='PLUGIN')
		self.layout.operator(ToggleViewportShadeA.bl_idname, icon='PLUGIN')
		self.layout.operator(CollectionDisplayOperator.bl_idname, icon='PLUGIN')
		self.layout.operator(OldSnapMenuOperator.bl_idname)


################
# クラスの登録 #
################

classes = [
	LocalViewEx,
	TogglePanelsA,
	TogglePanelsB,
	TogglePanelsC,
	ToggleViewportShadeA,
	ProjectEditEX,
	ViewNumpadPieOperator,
	ViewNumpadPie,
	ViewportShadePieOperator,
	ViewportShadePie,
	SetViewportShade,
	CollectionDisplayOperator,
	CollectionShowHide,
	CollectionWireFrame,
	CollectionObjectsShowHide,
	OldSnapMenuOperator,
	PanelPieOperator,
	PanelPie,
	RunPanelPie,
	ShortcutsMenu
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
		flag = False
		prefs = context.preferences.addons[__name__.partition('.')[0]].preferences
		for idx in ['1', '2', '3']:
			if eval(f"prefs.image_editor_path_{idx}"):
				if not flag:
					self.layout.label(text="=== Edit Screenshot ===")
					flag = True
				path = os.path.basename(eval(f"prefs.image_editor_path_{idx}"))
				name, ext = os.path.splitext(path)
				self.layout.operator(ProjectEditEX.bl_idname, icon="PLUGIN", text=name).index = int(idx)
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
