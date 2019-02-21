# 「ドープシート」エリア > 「キー」メニュー
# "Dope Sheet" Area > "Key" Menu

import bpy

################
# オペレーター #
################

class DeleteUnmessage(bpy.types.Operator):
	bl_idname = "action.delete_unmessage"
	bl_label = "Delete KeyFrames (Non-Confirm)"
	bl_description = "Delete without checking all selected keyframes"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		bpy.ops.action.delete()
		return {'FINISHED'}

class CreanEX(bpy.types.Operator):
	bl_idname = "action.crean_ex"
	bl_label = "Cleaning up all keyframes"
	bl_description = "Remove keyframe duplicates for all actions"
	bl_options = {'REGISTER', 'UNDO'}
	
	keep_fcurves = bpy.props.BoolProperty(name="Except One Key", default=False)
	threshold = bpy.props.FloatProperty(name="Threshold", default=0.00001, min=0, max=1, soft_min=0, soft_max=1, step=0.001, precision=5)
	
	def execute(self, context):
		threshold = self.threshold
		for action in bpy.data.actions[:]:
			for fcurve in action.fcurves[:]:
				if (not fcurve.modifiers):
					delete_points = []
					for i in reversed(range(len(fcurve.keyframe_points))):
						now_point = fcurve.keyframe_points[i].co[1]
						if (0 < i):
							pre_point = fcurve.keyframe_points[i-1].co[1]
						else:
							pre_point = now_point
						try:
							next_point = fcurve.keyframe_points[i+1].co[1]
						except IndexError:
							next_point = now_point
						if (now_point-threshold <= pre_point <= now_point+threshold):
							if (pre_point-threshold <= next_point <= pre_point+threshold):
								handle_left = fcurve.keyframe_points[i].handle_left[1]
								handle_right = fcurve.keyframe_points[i].handle_right[1]
								if (handle_left-threshold <= handle_right <= handle_left+threshold):
									delete_points.append(fcurve.keyframe_points[i])
					for point in delete_points:
						if (self.keep_fcurves and len(fcurve.keyframe_points) <= 1):
							break
						fcurve.keyframe_points.remove(point)
					if (len(fcurve.keyframe_points) <= 1 and not self.keep_fcurves):
						action.fcurves.remove(fcurve)
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

################
# メニュー追加 #
################

# メニューのオン/オフの判定
def IsMenuEnable(self_id):
	for id in bpy.context.user_preferences.addons["Scramble Addon"].preferences.disabled_menu.split(','):
		if (id == self_id):
			return False
	else:
		return True

# メニューを登録する関数
def menu(self, context):
	if (IsMenuEnable(__name__.split('.')[-1])):
		self.layout.separator()
		self.layout.operator(DeleteUnmessage.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(CreanEX.bl_idname, icon="PLUGIN")
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
