bl_info = {
    "name" : "Python Profiler",
    "author" : "Miguel Pozo",
    "description" : "A small utility to profile the performance of your addons.",
    "blender" : (2,80,0),
    "category" : "Development"
}

import bpy

import cProfile, io, pstats, time

PROFILER = None
PROFILER_DATA = None
PROFILE_STR = ''
START_TIME = 0
ELAPSED_TIME = 0

class Preferences(bpy.types.AddonPreferences):
    # this must match the addon name
    bl_idname = __name__
    
    def update_profile(self, context):
        global PROFILER, PROFILER_DATA, PROFILE_STR, START_TIME, ELAPSED_TIME
        if self.profile:
            PROFILER = cProfile.Profile()
            PROFILER_DATA = io.StringIO()
            PROFILER.enable()
            START_TIME = time.perf_counter()
            PROFILE_STR = ''
        else:
            PROFILER.disable()
            import tempfile
            if self.prof_viz:
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.prof')
                tmp.close()
                PROFILER.dump_stats(tmp.name)
                import subprocess
                subprocess.Popen((self.prof_viz, tmp.name))
            else:
                ELAPSED_TIME = time.perf_counter() - START_TIME
                stats = pstats.Stats(PROFILER, stream=PROFILER_DATA)
                stats.strip_dirs()
                stats.sort_stats(pstats.SortKey.CUMULATIVE)
                stats.print_stats()
                PROFILE_STR = f'Total Time : {ELAPSED_TIME}\n\n'
                PROFILE_STR += PROFILER_DATA.getvalue()
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix='-profile-stats.txt')
                tmp.write(PROFILE_STR.encode('utf-8'))
                tmp.close()
                bpy.ops.wm.path_open(filepath=tmp.name)

    profile : bpy.props.BoolProperty(name="Profile", default=False, update=update_profile)
    prof_viz : bpy.props.StringProperty(name=".prof Visualizer",
        description='''The path to a .prof visualizer, like "snakeviz" or "tuna".
If no option is provided, the stats are printed to a .txt file''')

    def draw(self, context):
        global PROFILE_STR, ELAPSED_TIME
        layout = self.layout
        layout.prop(self, "prof_viz")
        layout.prop(self, "profile", toggle=True)


def help_ui(self, context):
    preferences = bpy.context.preferences.addons['profiler'].preferences
    self.layout.prop(preferences, "profile", toggle=True)


classes = [
    Preferences,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.TOPBAR_MT_help.append(help_ui)

def unregister():
    bpy.types.TOPBAR_MT_help.remove(help_ui)
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
