from pymt import *

#little different...TODO
"""
'MTScatterPlane',
MTGestureWidget,
'MTCoverFlow',
MTKinetic
MTModalWindow
MTMultiSlider
MTObjectDisplay
MTSidePanel
MTStencilContainer
'MTInnerWindow',
MTKineticList
MTModalPopup
MTPopup
MTTabs
MTVideo
MTSimpleVideo
Form stuff
'MTFlippableWidget',
"""

widget_names = [

    'MTButton',
    'MTToggleButton',
    'MTButtonMatrix',

    'MTRectangularWidget',
    'MTSlider',
    'MTXYSlider',
    'MTBoundarySlider',
    'MTMultiSlider',
    

    'MTTextInput',
    'MTColorPicker',

    ]
"""


    'MTColorPicker',
    'MTFileBrowser',

    'MTVectorSlider',
    'MTScatterWidget',

    'MTSlider',
    'MTXYSlider',
    'MTBoundarySlider',
    'MTMultiSlider',


"""





if __name__ == '__main__':
    
    root = MTGridLayout(cols=5, rows=5)
    for widget in widget_names:
        box = MTBoxLayout(orientation='vertical', padding=30)
        w = MTWidgetFactory.get(widget)(label=widget[2:], size=(100,100))
        box.add_widget(w)
        box.add_widget(MTLabel(label=widget, width=w.width, anchor_x='center'))
        root.add_widget(box)
    runTouchApp(root)
