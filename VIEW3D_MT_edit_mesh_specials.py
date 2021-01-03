# 「3Dビュー」エリア > 「メッシュ編集」モード > 「W」キー
# "3D View" Area > "Mesh Editor" Mode > "W" Key

import bpy
from bpy.props import *

################
# オペレーター #
################

class PaintSelectedVertexColor(bpy.types.Operator):
	bl_idname = "mesh.paint_selected_vertex_color"
	bl_label = "Fill Selected Vertices' Vertex Color"
	bl_description = "Fill selected vertices with designated color at active vertex color"
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
	bl_label = "Show Base Shape"
	bl_description = "Show base shape of active object's shape keys in viewport"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		context.active_object.active_shape_key_index = 0
		return {'FINISHED'}

class ToggleShowCage(bpy.types.Operator):
	bl_idname = "mesh.toggle_show_cage"
	bl_label = "Switch Display Method of Modifiers' Results"
	bl_description = "Switch display method of meshes or their vertices which are created by modifiers"
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
	bl_label = "Switch Display of Mirror Modifiers"
	bl_description = "Switch display state of mirror modifiers (and add it if not exist)"
	bl_options = {'REGISTER', 'UNDO'}

	use_x : BoolProperty(name="X Axis", default=True)
	use_y : BoolProperty(name="Y Axis", default=False)
	use_z : BoolProperty(name="Z Axis", default=False)
	use_mirror_merge : BoolProperty(name="Merge", default=True)
	merge_threshold : FloatProperty(name="Merge Distance", default=0.001, min=0, max=1, soft_min=0, soft_max=1, step=0.01, precision=6)
	use_clip : BoolProperty(name="Clipping", default=False)
	use_mirror_u : BoolProperty(name="Texture U Mirror", default=False)
	use_mirror_v : BoolProperty(name="Texture V Mirror", default=False)
	use_mirror_vertex_groups : BoolProperty(name="Vertex Groups", default=True)
	is_top : BoolProperty(name="Add at Top", default=True)
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
	bl_label = "Average Selected Vertices' Weight"
	bl_description = "Change selected vertices' weight to their average value"
	bl_options = {'REGISTER', 'UNDO'}

	all_group : BoolProperty(name="Apply to All Groups", default=True)
	target : StringProperty(name="Target", default="")
	strength : FloatProperty(name="Original Values' Effect", default=0, min=0, max=1, soft_min=0, soft_max=1, step=10, precision=3)

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		if len(obj.vertex_groups) == 0:
			return False
		if not obj.type == "MESH":
			return False
		return True
	def __init__(self):
		idx = bpy.context.active_object.vertex_groups.active_index
		self.target = bpy.context.active_object.vertex_groups[idx].name
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	def draw(self, context):
		self.layout.prop(self, 'all_group')
		row = self.layout.row()
		row.enabled = not self.all_group
		row.prop_search(self, 'target', context.active_object, "vertex_groups", text="Target", translate=True, icon='GROUP_VERTEX')
		row = self.layout.split(factor=0.55)
		row.label(text="Original Values' Effect")
		row.prop(self, 'strength', text="")

	def execute(self, context):
		obj = context.active_object
		pre_mode = obj.mode
		bpy.ops.object.mode_set(mode='OBJECT')
		vg_dic = {idx: dict() for idx, vg in enumerate(obj.vertex_groups)}
		selected_verts = [v for v in obj.data.vertices if v.select]
		if (len(selected_verts) <= 0):
			bpy.ops.object.mode_set(mode=pre_mode)
			self.report(type={'ERROR'}, message="Need to select at least one vertex")
			return {'CANCELLED'}
		for v in selected_verts:
			for vge in v.groups:
				belonged_vg_dic = vg_dic[vge.group]
				belonged_vg_dic[v.index] = vge.weight
		if self.all_group:
			keys = list(vg_dic.keys())
		else:
			keys = [obj.vertex_groups.find(self.target)]
		for key in keys:
			v_group = obj.vertex_groups[key]
			counts = len(list(vg_dic[key].keys()))
			weight = sum(list(vg_dic[key].values()))
			average = weight/counts
			for vert_idx in vg_dic[key].keys():
				pre_weight = vg_dic[key][vert_idx]
				new_weight = pre_weight*self.strength + average*(1-self.strength)
				v_group.add([vert_idx], new_weight, 'REPLACE')
		bpy.ops.object.mode_set(mode=pre_mode)
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
		self.layout.prop(context.object.data, "use_mirror_x", icon="PLUGIN", text="X-Axis Mirror")
		self.layout.operator(ToggleMirrorModifier.bl_idname, icon="PLUGIN")
		self.layout.operator(ToggleShowCage.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(SelectedVertexGroupAverage.bl_idname, icon="PLUGIN")
		self.layout.operator(PaintSelectedVertexColor.bl_idname, icon="PLUGIN")
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
