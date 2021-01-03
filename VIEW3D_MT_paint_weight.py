# 「3Dビュー」エリア > 「ウェイトペイント」モード > 「ウェイト」メニュー
# "3D View" Area > "Weight Paint" Mode > "Weights" Menu

import bpy, bmesh
from bpy.props import *

################
# オペレーター #
################

class MargeSelectedVertexGroup(bpy.types.Operator):
	bl_idname = "paint.marge_selected_vertex_group"
	bl_label = "Add Designated Bone's Weight"
	bl_description = "Add to active vertex group the weight of vertex group linked to designated bone"
	bl_options = {'REGISTER', 'UNDO'}

	crate_newvg : BoolProperty(name="Create new vertex group", default=False)
	target : StringProperty(name="Target", default="")
	new_name : StringProperty(name="Name", default="")

	@classmethod
	def poll(cls, context):
		if context.active_object.vertex_groups.active_index == -1:
			return False
		return True
	def __init__(self):
		idx = bpy.context.active_object.vertex_groups.active_index
		self.target = bpy.context.active_object.vertex_groups[0].name
		self.new_name = f"{bpy.context.active_object.vertex_groups[idx].name}_merged"
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	def draw(self, context):
		self.layout.prop_search(self, 'target', context.active_object, "vertex_groups", text="Target", translate=True, icon='GROUP_VERTEX')
		row = self.layout.row()
		row.use_property_split = True
		row.prop(self, 'crate_newvg')
		row = self.layout.row()
		row.use_property_split = True
		row.enabled = self.crate_newvg
		row.prop(self, 'new_name')

	def execute(self, context):
		obj = context.active_object
		if (self.crate_newvg):
			newVg = obj.vertex_groups.new(name=self.new_name)
		else:
			newVg = obj.vertex_groups[obj.vertex_groups.active_index]
		target_vg_idx = obj.vertex_groups.find(self.target)
		for vert in obj.data.vertices:
			for vg in vert.groups:
				if vg.group == target_vg_idx:
					newVg.add([vert.index], vg.weight, 'ADD')
		bpy.ops.object.mode_set(mode="WEIGHT_PAINT")
		obj.vertex_groups.active_index = newVg.index
		return {'FINISHED'}

class RemoveSelectedVertexGroup(bpy.types.Operator):
	bl_idname = "paint.remove_selected_vertex_group"
	bl_label = "Subtract Designated Bone's Weight"
	bl_description = "Subtract the weight of vertex group linked to designated bone from active vertex group"
	bl_options = {'REGISTER', 'UNDO'}

	target : StringProperty(name="Target", default="")

	@classmethod
	def poll(cls, context):
		if context.active_object.vertex_groups.active_index == -1:
			return False
		return True
	def __init__(self):
		self.target = bpy.context.active_object.vertex_groups[0].name
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	def draw(self, context):
		self.layout.prop_search(self, 'target', context.active_object, "vertex_groups", text="Target", translate=True, icon='GROUP_VERTEX')

	def execute(self, context):
		obj = context.active_object
		newVg = obj.vertex_groups[obj.vertex_groups.active_index]
		target_vg_idx = obj.vertex_groups.find(self.target)
		for vert in obj.data.vertices:
			for vg in vert.groups:
				if vg.group == target_vg_idx:
					newVg.add([vert.index], vg.weight, 'SUBTRACT')
		bpy.ops.object.mode_set(mode="WEIGHT_PAINT")
		return {'FINISHED'}

class VertexGroupAverageAll(bpy.types.Operator):
	bl_idname = "paint.vertex_group_average_all"
	bl_label = "Average All Vertices' Weight"
	bl_description ="Change all vertices' weight to their average value"
	bl_options = {'REGISTER', 'UNDO'}

	all_group : BoolProperty(name="Apply to All Groups", default=True)
	target : StringProperty(name="Target", default="")
	strength : FloatProperty(name="Original Values' Effect", default=0, min=0, max=1, soft_min=0, soft_max=1, step=10, precision=3)

	@classmethod
	def poll(cls, context):
		if context.active_object.vertex_groups.active_index == -1:
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
		selected_verts = obj.data.vertices
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

class ApplyDynamicPaint(bpy.types.Operator):
	bl_idname = "mesh.apply_dynamic_paint"
	bl_label = "Set Weight to Overlapping Area"
	bl_description = "Set weight to vertices at areas where active object overlaps selected objects"
	bl_options = {'REGISTER', 'UNDO'}

	is_new : BoolProperty(name="Create new vertex group", default=False)
	new_name : StringProperty(name="Name", default="Overlapping Area")
	distance : FloatProperty(name="Distance", default=1.0, min=0, max=100, soft_min=0, soft_max=100, step=10, precision=3)
	items = [
		("ADD", "Add", "", 1),
		("SUBTRACT", "Subtract", "", 2),
		("REPLACE", "Replace", "", 3),
		]
	mode : EnumProperty(items=items, name="Method")

	@classmethod
	def poll(cls, context):
		if not context.selected_objects or len(context.selected_objects) < 2:
			return False
		if context.active_object.vertex_groups.active_index == -1:
			return False
		return True
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True
		for p in ['mode','distance','is_new']:
			layout.prop(self, p)
		row = layout.row()
		row.enabled = self.is_new
		row.prop(self, 'new_name')

	@classmethod
	def poll(cls, context):
		if not context.selected_objects or len(context.selected_objects) < 2:
			return False
		return True
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True
		for p in ['mode','distance','is_new']:
			layout.prop(self, p)
		row = layout.row()
		row.enabled = self.is_new
		row.prop(self, 'new_name')

	def execute(self, context):
		activeObj = context.active_object
		if len(activeObj.vertex_groups) == 0 or self.is_new:
			target_vg = activeObj.vertex_groups.new(name=self.new_name)
		else:
			target_vg = activeObj.vertex_groups.active
		bpy.ops.object.mode_set(mode="OBJECT")
		brushObjs = list(set(context.selected_objects) - {activeObj})
		for obj in brushObjs:
			bpy.context.view_layer.objects.active = obj
			bpy.ops.object.modifier_add(type='DYNAMIC_PAINT')
			obj.modifiers[-1].ui_type = 'BRUSH'
			bpy.ops.dpaint.type_toggle(type='BRUSH')
			obj.modifiers[-1].brush_settings.paint_source = 'VOLUME_DISTANCE'
			obj.modifiers[-1].brush_settings.paint_distance = self.distance

		bpy.context.view_layer.objects.active = activeObj
		bpy.ops.object.modifier_add(type='DYNAMIC_PAINT')
		bpy.ops.dpaint.type_toggle(type='CANVAS')
		activeObj.modifiers[-1].canvas_settings.canvas_surfaces[-1].surface_type = 'WEIGHT'
		bpy.ops.dpaint.output_toggle(output='A')
		dpVg = activeObj.vertex_groups[-1]
		#"Dynamic Paint weight group isn't updated unless weight has been assigned" というバグが2.80にある
		#おそらくこれに関連し、スクリプト経由でダイナミックペイントを適用する場合、
		#作成される頂点グループ dp_weight の中身がリセットされるので対処する
		bpy.ops.object.modifier_add(type='SOFT_BODY')#ソフトボディ追加(対処1-1)
		activeObj.modifiers[-2].settings.vertex_group_mass = dpVg.name
		print(activeObj.modifiers[-1].name)#ソフトボディに関連付けて dp_weight の中身を固定(対処1-2)
		bpy.ops.object.modifier_apply(modifier=activeObj.modifiers[-1].name)#ダイナミックペイントを適用
		activeObj.modifiers.remove(activeObj.modifiers[-1])#ソフトボディを除去(後始末)
		dpVg_idx = activeObj.vertex_groups.find(dpVg.name)
		for vert in activeObj.data.vertices:
			for vg in vert.groups:
				if vg.group == dpVg_idx:
					if target_vg.name == self.new_name:
						target_vg.add([vert.index], vg.weight, 'REPLACE')
						break
					else:
						target_vg.add([vert.index], vg.weight, self.mode)
		activeObj.vertex_groups.remove(dpVg)
		activeObj.vertex_groups.active_index = target_vg.index
		bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
		for obj in brushObjs:
			obj.modifiers.remove(obj.modifiers[-1])
		return {'FINISHED'}


class BlurWeight(bpy.types.Operator):
	bl_idname = "mesh.blur_weight"
	bl_label = "Blur Weight (Active Group)"
	bl_description = "Blur active or all vertex groups' weight"
	bl_options = {'REGISTER', 'UNDO'}

	all_group : BoolProperty(name="Apply to All Groups", default=False)
	blur_count : IntProperty(name="Strength", default=10, min=1, max=100, soft_min=1, soft_max=100, step=1)
	use_clean : BoolProperty(name="Remove Zero-Weight Vertices", default=True)

	@classmethod
	def poll(cls, context):
		if context.active_object.vertex_groups.active_index == -1:
			return False
		return True
	def draw(self, context):
		for p in ['all_group', 'blur_count']:
			row = self.layout.row()
			row.use_property_split = True
			row.prop(self, p)
		row = self.layout.split(factor=0.25)
		row.label(text="")
		row.prop(self, 'use_clean')

	def execute(self, context):
		activeObj = context.active_object
		pre_mode = activeObj.mode
		bpy.ops.object.mode_set(mode='OBJECT')
		me = activeObj.data
		if not self.all_group:
			target_groups = [activeObj.vertex_groups.active]
		else:
			target_groups = activeObj.vertex_groups
		bm = bmesh.new()
		bm.from_mesh(me)
		for count in range(self.blur_count):
			for vg in target_groups:
				vg_index = vg.index
				new_weights = []
				for vert in bm.verts:
					for group in me.vertices[vert.index].groups:
						if (group.group == vg_index):
							my_weight = group.weight
							break
					else:
						my_weight = 0.0
					near_weights = []
					for edge in vert.link_edges:
						for v in edge.verts:
							if (v.index != vert.index):
								edges_vert = v
								break
						for group in me.vertices[edges_vert.index].groups:
							if (group.group == vg_index):
								near_weights.append(group.weight)
								break
						else:
							near_weights.append(0.0)
					near_weight_average = 0
					for weight in near_weights:
						near_weight_average += weight
					try:
						near_weight_average /= len(near_weights)
					except ZeroDivisionError:
						near_weight_average = 0.0
					new_weights.append( (my_weight*2 + near_weight_average) / 3 )
				for vert, weight in zip(me.vertices, new_weights):
					if (self.use_clean and weight <= 0.000001):
						vg.remove([vert.index])
					else:
						vg.add([vert.index], weight, 'REPLACE')
		bm.free()
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	MargeSelectedVertexGroup,
	RemoveSelectedVertexGroup,
	VertexGroupAverageAll,
	ApplyDynamicPaint,
	BlurWeight
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
		self.layout.operator(MargeSelectedVertexGroup.bl_idname, icon="PLUGIN")
		self.layout.operator(RemoveSelectedVertexGroup.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(BlurWeight.bl_idname, icon="PLUGIN")
		self.layout.operator(BlurWeight.bl_idname, text="Blur Weight (All Groups)", icon="PLUGIN").all_group = True
		self.layout.separator()
		self.layout.operator(VertexGroupAverageAll.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(ApplyDynamicPaint.bl_idname, icon="PLUGIN")
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
