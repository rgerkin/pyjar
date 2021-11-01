import ipyvuetify as v

W = None

def get_all_widgets():
    return list(W.values())
    #return [val for key, val in globals().items()
    #        if v.generated.VuetifyWidget in val.__class__.__bases__
    #        and not key.startswith('_')]
    
def style_widgets(attr, value, widgets=[], not_widgets=[]):
    if not widgets:
        widgets = get_all_widgets()
    widgets = [widgets] if not isinstance(widgets, (list, tuple)) else widgets
    not_widgets = [not_widgets] if not isinstance(not_widgets, (list, tuple)) else not_widgets
    for widget in widgets:
        if widget not in not_widgets:
            setattr(widget.layout, attr, value)

def hide_widgets(widgets=[], not_widgets=[]):
    style_widgets("visibility", "hidden", widgets=widgets, not_widgets=not_widgets)
            
def show_widgets(widgets=[], not_widgets=[]):
    style_widgets("visibility", "visible", widgets=widgets, not_widgets=not_widgets)