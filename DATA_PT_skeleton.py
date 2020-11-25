# 「プロパティ」エリア > 「アーマチュアデータ」タブ > 「スケルトン」パネル
# "Propaties" Area > "Armature" Tab > "Skeleton" Panel

import bpy
from bpy.props import *
import numpy as np

################
# オペレーター #
################

class ShowAllBoneLayers(bpy.types.Operator):
	bl_idname = "pose.show_all_bone_layers"
	bl_label = "View all bone layer"
	bl_description = "All bone layer and then displays the"
	bl_options = {'REGISTER'}

	layers = [False] * 32
	layers[0] = True
	pre_layers : BoolVectorProperty(name="Last Layer Information", size=32, default=layers[:])

	@classmethod
	def poll(cls, context):
		if (context.object):
			if (context.object.type == 'ARMATURE'):
				return True
		return False

	def execute(self, context):
		if (all(context.object.data.layers)):
			context.object.data.layers = self.pre_layers[:]
			self.report(type={'INFO'}, message="Unshow All Layers")
		else:
			self.pre_layers = context.object.data.layers[:]
			for i in range(len(context.object.data.layers)):
				context.object.data.layers[i] = True
			self.report(type={'WARNING'}, message="Show All Layers")
		return {'FINISHED'}

class ShowGroupLayers(bpy.types.Operator):
	bl_idname = "pose.show_group_layers"
	bl_label = "Show selected bone group's layers"
	bl_description = "Show layers containing the selected pose group"
	bl_options = {'REGISTER'}

	group_name : StringProperty(name="Bone Group", default="")
	extend : BoolProperty(name="Extend Selection", default=False)


	@classmethod
	def poll(cls, context):
		if (context.object):
			if (context.object.type == 'ARMATURE'):
				if (context.mode == 'POSE'):
					return True
		return False

	def invoke(self, context, event):
		if (event.shift):
			self.extend = True
		else:
			self.extend = False
		return self.execute(context)

	def update_group_idx(self, context, idx, method):
		if method == "NEW":
			g_idx = "0"*12
			g_idx = g_idx[:idx] + "1" + g_idx[idx+1:]
		elif method == "EXTEND":
			g_idx = context.active_object.scramble_sk_prop.bone_group_idx
			g_idx = g_idx[:idx] + "1" + g_idx[idx+1:]
		elif method == "SUBTRACT":
			g_idx = context.active_object.scramble_sk_prop.bone_group_idx
			g_idx = g_idx[:idx] + "0" + g_idx[idx+1:]
		context.active_object.scramble_sk_prop.bone_group_idx = g_idx

	def execute(self, context):
		pre_LAYERS = np.array(context.object.data.layers, dtype=np.float16)
		target = context.active_object.pose.bone_groups[self.group_name]
		target_idx = context.active_object.pose.bone_groups.find(target.name)
		bone_layers = []
		context.object.data.layers = [True]*32
		context.active_object.pose.bone_groups.active = target
		bpy.ops.pose.select_all(action='DESELECT')
		bpy.ops.pose.group_select()
		for b in context.selected_pose_bones:
			if b.bone.layers not in bone_layers:
				arr = np.array(b.bone.layers[:], dtype=np.float16)
				bone_layers.append(arr)
		summation = np.array([False]*32, dtype=np.float16)
		for i in range(len(bone_layers)):
			summation = summation + bone_layers[i]
		if self.extend:
			LAYERS = ((pre_LAYERS + summation) > 0).tolist()
			PRE_LAYERS = (pre_LAYERS > 0).tolist()
			self.update_group_idx(context, target_idx, 'EXTEND')
			if (LAYERS == PRE_LAYERS):
				LAYERS = ((pre_LAYERS - summation) > 0).tolist()
				self.update_group_idx(context, target_idx, 'SUBTRACT')
		else:
			LAYERS = (summation > 0).tolist()
			self.update_group_idx(context, target_idx, 'NEW')
		context.object.data.layers = LAYERS
		bpy.ops.pose.select_all(action='DESELECT')
		return {'FINISHED'}

class ShowLayersforGroups(bpy.types.Operator):
	bl_idname = "pose.show_layers_for_groups"
	bl_label = "Show selected bone group's layers"
	bl_description = "Show layers containing the selected pose group"
	bl_options = {'REGISTER'}

	@classmethod
	def poll(cls, context):
		if (context.object):
			if len(context.active_object.pose.bone_groups) > 0:
				return True
		return False

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	def draw(self, context):
		row = self.layout.row()
		for idx, g in enumerate(context.active_object.pose.bone_groups):
			if idx != 0 and idx % 3 == 0:
				row = self.layout.row()
			if context.active_object.scramble_sk_prop.bone_group_idx[idx] == "1":
				icon = 'KEYTYPE_MOVING_HOLD_VEC'
			else: icon = 'NONE'
			row.operator(ShowGroupLayers.bl_idname, text=f"{g.name}", icon=icon).group_name = g.name

	def execute(self, context):
		return {'FINISHED'}

class ScrambleSkeltonPropGroup(bpy.types.PropertyGroup):
	use_panel : bpy.props.BoolProperty(
		name="Display on panel",
		description="",
		default=False
	)

	bone_group_idx : bpy.props.StringProperty(
		name="bone-group index",
		description="Str-index of displayed bone groups",
		default="000000000000000000000"
	)

################
# クラスの登録 #
################

classes = [
	ShowAllBoneLayers,
	ShowGroupLayers,
	ShowLayersforGroups,
	ScrambleSkeltonPropGroup
]

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.Object.scramble_sk_prop = bpy.props.PointerProperty(type=ScrambleSkeltonPropGroup)

def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)
	del bpy.types.Object.scramble_sk_prop


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
		layout = self.layout
		obj = context.active_object
		row = layout.row(align=True)
		row.prop(obj.scramble_sk_prop, 'use_panel', icon="TRIA_DOWN" if obj.scramble_sk_prop.use_panel else "TRIA_RIGHT", icon_only=True, emboss=False)
		sp = row.split(factor=0.6)
		row = sp.row(align=True)
		row.alignment="LEFT"
		row.prop(obj.scramble_sk_prop, 'use_panel',text="Show for Bone Group",emboss=False)
		sp.operator(ShowAllBoneLayers.bl_idname, icon='RESTRICT_VIEW_OFF', text="Show All Layers")
		if obj.scramble_sk_prop.use_panel:
			box = layout.box()
			if not len(context.active_object.pose.bone_groups):
				box.label(text="No Bone groups",icon="NONE")
			else:
				row = box.row()
				for idx, g in enumerate(context.active_object.pose.bone_groups):
					if idx != 0 and idx % 3 == 0:
						row = box.row()
					if context.active_object.scramble_sk_prop.bone_group_idx[idx] == "1":
						icon = 'KEYTYPE_MOVING_HOLD_VEC'
					else: icon = 'BLANK1'
					row.operator(ShowGroupLayers.bl_idname, text=f"{g.name}", icon=icon,translate=False).group_name = g.name


	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
