# 「プロパティ」エリア > 「シーン」タブ > 「剛体ワールド」パネル
# "Propaties" Area > "Scene" Tab > "Rigid Body World" Panel

import bpy

################
# オペレーター #
################

class WorldReset(bpy.types.Operator):
	bl_idname = "rigidbody.world_reset"
	bl_label = "Recreate RigidBody World"
	bl_description = "Keep setting, recreate rigid world"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if (not context.scene.rigidbody_world):
			return False
		return context.scene.rigidbody_world.enabled
	def execute(self, context):
		group = context.scene.rigidbody_world.group
		constraints = context.scene.rigidbody_world.constraints
		time_scale = context.scene.rigidbody_world.time_scale
		steps_per_second = context.scene.rigidbody_world.steps_per_second
		use_split_impulse = context.scene.rigidbody_world.use_split_impulse
		solver_iterations = context.scene.rigidbody_world.solver_iterations
		frame_start = context.scene.rigidbody_world.point_cache.frame_start
		frame_end = context.scene.rigidbody_world.point_cache.frame_end
		
		bpy.ops.rigidbody.world_remove()
		bpy.ops.rigidbody.world_add()
		
		context.scene.rigidbody_world.group = group
		context.scene.rigidbody_world.constraints = constraints
		context.scene.rigidbody_world.time_scale = time_scale
		context.scene.rigidbody_world.steps_per_second = steps_per_second
		context.scene.rigidbody_world.use_split_impulse = use_split_impulse
		context.scene.rigidbody_world.solver_iterations = solver_iterations
		context.scene.rigidbody_world.point_cache.frame_start = frame_start
		context.scene.rigidbody_world.point_cache.frame_end = frame_end
		return {'FINISHED'}

class SyncFrames(bpy.types.Operator):
	bl_idname = "rigidbody.sync_frames"
	bl_label = "Set start/end frames rigid body world"
	bl_description = "Start / end frame rigid world of sets to start / end frame rendering"
	bl_options = {'REGISTER', 'UNDO'}
	
	frame_margin = bpy.props.IntProperty(name="Margin", default=0, min=-999, max=999, soft_min=-999, soft_max=999)
	
	@classmethod
	def poll(cls, context):
		if context.scene.rigidbody_world:
			if context.scene.rigidbody_world.point_cache:
				return True
		return False
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	
	def execute(self, context):
		rigidbody_world = context.scene.rigidbody_world
		point_cache = rigidbody_world.point_cache
		point_cache.frame_start = context.scene.frame_start - self.frame_margin
		point_cache.frame_end = context.scene.frame_end + self.frame_margin
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

################
# クラスの登録 #
################

classes = [
	WorldReset,
	SyncFrames
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
	for id in bpy.context.preferences.addons["Blender-Scramble-Addon-master"].preferences.disabled_menu.split(','):
		if (id == self_id):
			return False
	else:
		return True

# メニューを登録する関数
def menu(self, context):
	if (IsMenuEnable(__name__.split('.')[-1])):
		row = self.layout.row(align=True)
		row.operator(WorldReset.bl_idname, icon='PLUGIN')
		op = row.operator('wm.context_set_string', icon='PHYSICS', text="")
		op.data_path = 'space_data.context'
		op.value = 'PHYSICS'
		if context.scene.rigidbody_world:
			if context.scene.rigidbody_world.point_cache:
				row = self.layout.row(align=True)
				row.prop(context.scene.rigidbody_world.point_cache, 'frame_start')
				row.prop(context.scene.rigidbody_world.point_cache, 'frame_end')
				row.operator('rigidbody.sync_frames', icon='LINKED', text="")
	if (context.preferences.addons["Blender-Scramble-Addon-master"].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
