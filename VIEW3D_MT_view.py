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

class CollectionDisplayOperator(bpy.types.Operator):
	bl_idname = "view3d.collection_display_operator"
	bl_label = "Collection Display Menu"
	bl_description = "Toggle collection visibility"
	bl_options = {'REGISTER'}

	align : EnumProperty(name="Align", items=[("HORIZONTAL", "Horizontal", "", 1), ("VERTICAL", "Vertical", "", 2)])

	def invoke(self, context, event):
		if self.align == 'HORIZONTAL':
			WIDTH = len(context.view_layer.layer_collection.children)*200
		elif self.align == 'VERTICAL':
			WIDTH = 360
		return context.window_manager.invoke_props_dialog(self, width=WIDTH)
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
		row = self.layout.row().split(factor=0.7)
		row.label(text="Show/Hide objects | Hide others | Show/Hide collection | Texture/Wireframe", icon='NONE')
		row.operator(CollectionShowHide.bl_idname, text="Show All", icon='NONE').is_all = "SHOW"
		row.operator(CollectionShowHide.bl_idname, text="Hide All", icon='NONE').is_all = "HIDE"
		if self.align == 'HORIZONTAL': root = self.layout.row()
		elif self.align == 'VERTICAL': root = self.layout.box()
		for col in context.view_layer.layer_collection.children:
			if self.align == 'HORIZONTAL':
				branch= root.box().column()
				item = branch.row()
			elif self.align == 'VERTICAL':
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
		spl = self.layout.split(factor=0.5).prop(self, "align")
	def execute(self, context):
		return {"FINISHED"}

class CollectionPieOperator(bpy.types.Operator):
	bl_idname = "view3d.collection_pie_operator"
	bl_label = "Collection Pie Menu"
	bl_description = "Toggle collection visibility"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		bpy.ops.wm.call_menu_pie(name=CollectionPie.bl_idname)
		return {'FINISHED'}

class CollectionPie(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_pie_collection"
	bl_label = "Collection Display Menu"
	bl_description = "Toggle collection Show/Hide/Wireframe"

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
		box = self.layout.box()
		row = box.row().split(factor=0.7)
		row.label(text="Show/Hide objects | Hide others | Show/Hide collection | Texture/Wireframe", icon='NONE')
		row.operator(CollectionShowHide.bl_idname, text="Show All", icon='NONE').is_all = "SHOW"
		row.operator(CollectionShowHide.bl_idname, text="Hide All", icon='NONE').is_all = "HIDE"
		row = box.row()
		for col in context.view_layer.layer_collection.children:
			column = row.box().column()
			item = column.row()
			if col.name == obj_par_collection:
				item.operator(CollectionObjectsShowHide.bl_idname, text="", icon=self.GetIcon(col, TYPE='OBJ_ACTIVE') ).name = col.name
			else:
				item.operator(CollectionObjectsShowHide.bl_idname, text="", icon=self.GetIcon(col, TYPE='OBJ_OTHER')).name = col.name
			item.operator("object.hide_collection", text=f"{col.name}", icon='NONE').collection_index = collec_dic[col.name]["idx"]
			op = item.operator(CollectionShowHide.bl_idname, text="", icon=self.GetIcon(col))
			op.name, op.is_all = [col.name, 'SINGLE']
			item.operator(CollectionWireFrame.bl_idname, text="", icon=self.GetIcon(col, TYPE="WIRE")).name = col.name
			flatten_nest = self.flatten(col)
			for coll in flatten_nest:
				if coll == None:
					column.separator(factor=0.3)
				else:
					item2 = column.row()
					if coll.name == obj_par_collection:
						item2.operator(CollectionObjectsShowHide.bl_idname, text="", icon=self.GetIcon(coll, TYPE='OBJ_ACTIVE')).name = coll.name
					else:
						item2.operator(CollectionObjectsShowHide.bl_idname, text="", icon=self.GetIcon(coll, TYPE='OBJ_OTHER')).name = coll.name
					item2.operator("object.hide_collection", text=f"{coll.name}", icon='NONE').collection_index = collec_dic[coll.name]["idx"]
					op = item2.operator(CollectionShowHide.bl_idname, text="", icon=self.GetIcon(coll))
					op.name, op.is_all = [coll.name, 'SINGLE']

					item2.operator(CollectionWireFrame.bl_idname, text="", icon=self.GetIcon(coll, TYPE="WIRE")).name = coll.name
			column.separator(factor=1.0)

class CollectionShowHide(bpy.types.Operator):
	bl_idname = "view3d.collection_show_hide"
	bl_label = "Toggle Collection Show/Hide"
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
	bl_label = "Toggle Texture/Wireframe"
	bl_description = "Shows the objects as wire edges or textured"
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
	bl_label = "Toggle Show/Hide of contained objects"
	bl_description = "Show or hide all objects in the selected collection"
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
		self.layout.operator(CollectionDisplayOperator.bl_idname, text="Collection", icon='PLUGIN')
		# self.layout.operator(CollectionPieOperator.bl_idname, text="Collection", icon='PLUGIN')
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
	#CollectionPieOperator,
	CollectionDisplayOperator,
	#CollectionPie,
	CollectionShowHide,
	CollectionWireFrame,
	CollectionObjectsShowHide,
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
