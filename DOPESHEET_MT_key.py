# 「ドープシート」エリア > 「キー」メニュー
# "Dope Sheet" Area > "Key" Menu

import bpy
from bpy.props import *

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

	keep_fcurves : BoolProperty(name="Except One Key", default=False)
	threshold : FloatProperty(name="Threshold", default=0.00001, min=0, max=1, soft_min=0, soft_max=1, step=0.001, precision=5)

	def execute(self, context):
		threshold = self.threshold
		animations = [ob.animation_data for ob in bpy.data.objects if ob.hide_get() == False]
		action_datas = [an.action for an in animations if an != None and an.action != None]
		for action in action_datas:
			for fcurve in action.fcurves[:]:
				if (not fcurve.modifiers):
					delete_points = []
					for i in reversed(range(len(fcurve.keyframe_points))):
						now_point = fcurve.keyframe_points[i].co[1]
						if (0 < i):
							pre_point = fcurve.keyframe_points[i-1].co[1]
						else:
							#pre_point = now_point
							pre_point = fcurve.keyframe_points[i+1].co[1]
						try:
							next_point = fcurve.keyframe_points[i+1].co[1]
						except IndexError:
							#next_point = now_point
							next_point = fcurve.keyframe_points[i-1].co[1]
						now_pre = (now_point-threshold <= pre_point <= now_point+threshold)
						now_next = (now_point-threshold <= next_point <= now_point+threshold)
						#pre_next = (pre_point-threshold <= next_point <= pre_point+threshold)
						if (now_pre or now_next):#(now_pre and pre_next):
							handle_left = fcurve.keyframe_points[i].handle_left[1]
							handle_right = fcurve.keyframe_points[i].handle_right[1]
							if (handle_left-threshold <= handle_right <= handle_left+threshold):
								delete_points.append(fcurve.keyframe_points[i])
					if self.keep_fcurves:
						delete_points = delete_points[:-1]
					for point in delete_points:
						fcurve.keyframe_points.remove(point)
					if len(fcurve.keyframe_points) == 0:
						action.fcurves.remove(fcurve)
				else:
					nam = action.name + "'s " + fcurve.data_path + " "
					self.report(type={'ERROR'}, message= nam + "is ignored because it has f-curve modifiers")
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

################
# クラスの登録 #
################

classes = [
	DeleteUnmessage,
	CreanEX
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
		self.layout.operator(DeleteUnmessage.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(CreanEX.bl_idname, icon="PLUGIN")
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
