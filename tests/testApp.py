import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from nicegui import ui
import niceguiEditor

@ui.page('/')
def mainPage():
    ui.label('NiceGUI Editor 테스트').classes('text-h3')
    with ui.row():
        ui.label('이것은 테스트d 입니다.')
        ui.button('버튼', on_click=lambda: ui.notify('클릭됨!'))

@ui.page('/abdcdd')
def mainPage():
    ui.label('NiceGUI Editor 테스트').classes('text-h3')


niceguiEditor.enable()
ui.run(reload=False)