# 「プロパティ」エリア > 「アーマチュアデータ」タブ > 「スケルトン」パネル
# "Propaties" Area > "Armature" Tab > "Skeleton" Panel

import bpy

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
	pre_layers = bpy.props.BoolVectorProperty(name="Last Layer Information", size=32, default=layers[:])
	
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

################
# クラスの登録 #
################

classes = [
	ShowAllBoneLayers
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
		row = self.layout.row(align=True)
		row.operator('pose.toggle_pose_position', icon='POSE_HLT', text="Enable/Disable Pose")
		row.operator(ShowAllBoneLayers.bl_idname, icon='RESTRICT_VIEW_OFF', text="Show All Layers")
	if (context.preferences.addons[__name__.partition('.')[0]].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
