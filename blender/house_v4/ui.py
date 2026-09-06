"""Blender sidebar for inspecting the eight model/reference states."""
import bpy

VIEWS=[('plan','01  Haus geschlossen'),('opening','02  Dach und Geschosse öffnen'),
       ('installation','03  Erdgeschoss / Installation'),('lighting','04  Beleuchtung'),
       ('smart-home','05  Obergeschoss / Smart Home'),('security','06  Eingang / Sicherheit'),
       ('photovoltaic','07  Photovoltaik'),('closing','08  Warmes Abschlussbild')]


class V4_OT_reference_view(bpy.types.Operator):
    bl_idname='v4.reference_view'
    bl_label='V4-Ansicht öffnen'
    bl_options={'REGISTER','UNDO'}
    view: bpy.props.StringProperty(default='plan')

    def execute(self,context):
        import build_house_v4
        build_house_v4.set_view(self.view)
        context.scene.render.filepath=str(build_house_v4.OUT/(build_house_v4.POSES[self.view][0]+'.png'))
        for area in context.screen.areas:area.tag_redraw()
        return {'FINISHED'}


class V4_PT_reference_views(bpy.types.Panel):
    bl_label='Haus V4 · Modellansichten'
    bl_idname='V4_PT_reference_views'
    bl_space_type='VIEW_3D'
    bl_region_type='UI'
    bl_category='V4 Haus'

    def draw(self,context):
        layout=self.layout
        layout.label(text='Zwei Geschosse · Satteldach')
        active=context.scene.get('active_reference_view','plan')
        column=layout.column(align=True)
        column.scale_y=1.25
        for key,label in VIEWS:
            op=column.operator('v4.reference_view',text=label,depress=key==active)
            op.view=key
        layout.separator()
        layout.operator('render.render',text='Aktuelle Ansicht rendern',icon='RENDER_STILL').write_still=True
        layout.label(text='Einzelansichten zur Modellprüfung',icon='INFO')


def register():
    for cls in [V4_OT_reference_view,V4_PT_reference_views]:
        old=getattr(bpy.types,cls.__name__,None)
        if old:bpy.utils.unregister_class(old)
        bpy.utils.register_class(cls)


if __name__=='__main__':register()
