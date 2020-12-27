# 「3Dビュー」エリア > 「メッシュ編集」モード > 「W」キー
# "3D View" Area > "Mesh Editor" Mode > "W" Key

import bpy
from bpy.props import *

################
# オペレーター #
################

class PaintSelectedVertexColor(bpy.types.Operator):
	bl_idname = "mesh.paint_selected_vertex_color"
	bl_label = "Paint out selected vertex color"
	bl_description = "Active vertex colors for selected vertices with specified color fills"
	bl_options = {'REGISTER', 'UNDO'}

	color : FloatVectorProperty(name="Color", default=(1, 1, 1), step=1, precision=3, subtype='COLOR_GAMMA', min=0, max=1, soft_min=0, soft_max=1)

	def execute(self, context):
		activeObj = context.active_object
		me = activeObj.data
		if not me.vertex_colors.active:
			me.vertex_colors.active = me.vertex_colors.new()
		bpy.ops.object.mode_set(mode='OBJECT')
		i = 0
		for poly in me.polygons:
			for vert in poly.vertices:
				if (me.vertices[vert].select):
					me.vertex_colors.active.data[i].color = (self.color[0], self.color[1], self.color[2], 1.0)
				i += 1
		bpy.ops.object.mode_set(mode='EDIT')
		return {'FINISHED'}

class SelectTopShape(bpy.types.Operator):
	bl_idname = "mesh.select_top_shape"
	bl_label = "Select shape at top"
	bl_description = "Schipke is at top of list, select"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		context.active_object.active_shape_key_index = 0
		return {'FINISHED'}

class ToggleShowCage(bpy.types.Operator):
	bl_idname = "mesh.toggle_show_cage"
	bl_label = "Transition modifiers apply to editing cage"
	bl_description = "Toggles whether to apply modifiers to total en bloc spondylectomy in editing"
	bl_options = {'REGISTER', 'UNDO'}

	mode_item = [
		("NON","Vertices: Hide,   Meshes: Hide","",1),("EDIT","Vertices: Hide,   Meshes: Show","",2),("BOTH","Vertices: Show,   Meshes: Show","",3)
	]
	mode : EnumProperty(name="Target", items=mode_item)

	def __init__(self):
		mods = bpy.context.active_object.modifiers
		edit_bools = [mod.show_in_editmode for mod in mods]
		cage_bools = [mod.show_on_cage for mod in mods]
		if sum(edit_bools)==0 and sum(cage_bools)==0:
			self.mode = self.mode_display = 'EDIT'
		elif sum(edit_bools)>=1 and sum(cage_bools)>=1:
			self.mode = 'NON'
		else:
			self.mode = 'BOTH'
	def draw(self, layout):
		self.layout.prop(self, 'mode', expand=True)

	def execute(self, context):
		dic = {
			'NON':[False,False,"Adjusting edit cage: Disabled, Display in edit mode: Disabled"],
			'EDIT':[False,True,"Adjusting edit cage: Disabled, Display in edit mode: Enabled"],
			'BOTH':[True,True,"Adjusting edit cage: Enabled, Display in edit mode: Enabled"]
		}
		activeObj = context.active_object
		items = dic[self.mode]
		for modi in activeObj.modifiers:
			modi.show_on_cage = items[0]
			modi.show_in_editmode = items[1]
			self.report(type={'INFO'}, message=items[2])
		return {'FINISHED'}

class ToggleMirrorModifier(bpy.types.Operator):
	bl_idname = "mesh.toggle_mirror_modifier"
	bl_label = "Toggle Mirror Modifiers"
	bl_description = "Delete if not Miller modifier added, Yes"
	bl_options = {'REGISTER', 'UNDO'}

	use_x : BoolProperty(name="X Axis", default=True)
	use_y : BoolProperty(name="Y Axis", default=False)
	use_z : BoolProperty(name="Z Axis", default=False)
	use_mirror_merge : BoolProperty(name="Combine", default=True)
	use_clip : BoolProperty(name="Clipping", default=False)
	use_mirror_vertex_groups : BoolProperty(name="Vertex Group Mirror", default=False)
	use_mirror_u : BoolProperty(name="Texture U Mirror", default=False)
	use_mirror_v : BoolProperty(name="Texture V Mirror", default=False)
	merge_threshold : FloatProperty(name="Combine Distance", default=0.001, min=0, max=1, soft_min=0, soft_max=1, step=0.01, precision=6)
	is_top : BoolProperty(name="Add Top", default=True)
	toggle : BoolProperty(name="Enabled / Disabled", default=True)
	is_add : BoolProperty(name="Add or not", default=False)

	def draw(self, context):
		row = self.layout.row()
		row.prop(self, 'toggle', toggle=1)
		row.alignment = 'CENTER'
		if self.is_add:
			self.layout.separator()
			row = self.layout.row()
			row.use_property_split = True
			row.prop(self, 'is_top')
			box = self.layout.box()
			row = box.row()
			for p in ['use_x','use_y','use_z',]:
				row.prop(self, p)
			box.prop(self, 'use_clip')
			row = box.row()
			row.prop(self, 'use_mirror_merge')
			row.prop(self, 'merge_threshold')
			row = box.row()
			row.prop(self, 'use_mirror_u')
			row.prop(self, 'use_mirror_v')
			box.prop(self, 'use_mirror_vertex_groups')

	def execute(self, context):
		self.toggle = True
		modis = context.active_object.modifiers
		mir_mods = [mod.name for mod in modis if mod.type=='MIRROR']
		if mir_mods:
			for nam in mir_mods:
				if not modis[nam].show_in_editmode:
					modis[nam].show_viewport = modis[nam].show_in_editmode = True
				else:
					modis[nam].show_viewport = not modis[nam].show_viewport
			self.is_add = False
		else:
			new_mod = modis.new("Mirror", 'MIRROR')
			new_mod.use_axis = [self.use_x, self.use_y, self.use_z]
			new_mod.use_mirror_merge = self.use_mirror_merge
			new_mod.use_clip = self.use_clip
			new_mod.use_mirror_vertex_groups = self.use_mirror_vertex_groups
			new_mod.use_mirror_u = self.use_mirror_u
			new_mod.use_mirror_v = self.use_mirror_v
			new_mod.merge_threshold = self.merge_threshold
			if (self.is_top):
				for i in range(len(modis)):
					bpy.ops.object.modifier_move_up(modifier=new_mod.name)
			self.is_add = True
		return {'FINISHED'}

class SelectedVertexGroupAverage(bpy.types.Operator):
	bl_idname = "mesh.selected_vertex_group_average"
	bl_label = "Fill selected vertices average weight"
	bl_description = "Fills selected vertex, vertices weighted average"
	bl_options = {'REGISTER', 'UNDO'}

	strength : FloatProperty(name="Mix Strength", default=1, min=0, max=1, soft_min=0, soft_max=1, step=10, precision=3)

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	def execute(self, context):
		obj = context.active_object
		if len(obj.vertex_groups) == 0:
			self.report(type={'ERROR'}, message="This object has no vertex_group")
			return {'CANCELLED'}		
		if (obj.type == "MESH"):
			pre_mode = obj.mode
			bpy.ops.object.mode_set(mode='OBJECT')
			vert_groups = []
			for vg in obj.vertex_groups:
				vert_groups.append([])
			selected_verts = []
			for vert in obj.data.vertices:
				if (vert.select):
					selected_verts.append(vert)
					for i in range(len(vert_groups)):
						for vge in vert.groups:
							if (i == vge.group):
								vert_groups[vge.group].append(vge.weight)
								break
						else:
							vert_groups[i].append(0)
			vert_groups_average = []
			for weights in vert_groups:
				vert_groups_average.append(0)
				for weight in weights:
					vert_groups_average[-1] += weight
				vert_groups_average[-1] /= len(weights)
			i = 0
			for vg in obj.vertex_groups:
				for vert in selected_verts:
					pre_weight = 0
					for vge in vert.groups:
						if (obj.vertex_groups[vge.group].name == vg.name):
							pre_weight = vge.weight
							break
					weight = (vert_groups_average[i] * self.strength) + (pre_weight * (1 - self.strength))
					vg.add([vert.index], weight, "REPLACE")
				i += 1
			bpy.ops.object.mode_set(mode=pre_mode)
		else:
			self.report(type={"ERROR"}, message="This is not mesh object")
			return {'CANCELLED'}
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	PaintSelectedVertexColor,
	SelectTopShape,
	ToggleShowCage,
	ToggleMirrorModifier,
	SelectedVertexGroupAverage
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
		self.layout.operator(SelectTopShape.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.prop(context.object.data, "use_mirror_x", icon="PLUGIN", text="X axis mirror edit")
		self.layout.operator(ToggleMirrorModifier.bl_idname, icon="PLUGIN")
		self.layout.operator(ToggleShowCage.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(SelectedVertexGroupAverage.bl_idname, icon="PLUGIN")
		self.layout.operator(PaintSelectedVertexColor.bl_idname, icon="PLUGIN")
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
