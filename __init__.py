from nicegui import ui
from nicegui.client import Client
from .niceguiEditor.editor import Editor
import inspect
import traceback

__version__ = "0.1.0"

class ButtonMaker:
    def __init__(self, callerInfo=None):
        self.isActive = False
        self.processedClients = set()
        self.callerInfo = callerInfo
    
    def addButton(self, client):
        clientId = client.id
        if clientId in self.processedClients:
            return
            
        self.processedClients.add(clientId)
        try:
            with client:
                endPoint = ""
                if hasattr(client, 'page') and hasattr(client.page, 'path'):
                    endPoint = client.page.path
                
                editor = Editor(endPoint, self.callerInfo)
                ui.button(icon='description', on_click=editor.open).classes('fixed top-0 right-0').props('flat rounded padding="0px"')
        except Exception as e:
            print(f"Error adding button to client {clientId}: {e}")
    
    def checkClients(self):
        try:
            for client in Client.instances.values():
                if hasattr(client, 'page') and hasattr(client.page, 'path'):
                    self.addButton(client)
        except Exception as e:
            print(f"Error checking clients: {e}")
    
    def start(self):
        if not self.isActive:
            self.isActive = True
            # 간단한 타이머로만 클라이언트 감지
            ui.timer(0.5, self.checkClients, active=True)

def enable():
    callerFrame = inspect.currentframe().f_back
    callerInfo = {
        'filename': callerFrame.f_code.co_filename,
        'lineno': callerFrame.f_lineno,
        'function': callerFrame.f_code.co_name,
        'globals': callerFrame.f_globals.keys()
    }
    
    try:
        print(f"NiceGUI Editor enabled from: {callerInfo['filename']}, line {callerInfo['lineno']}")
        btnMaker = ButtonMaker(callerInfo)
        btnMaker.start()
        return btnMaker
    except Exception as e:
        print(f"Error enabling NiceGUI Editor: {e}")
        print(traceback.format_exc())

__all__ = ["enable", "__version__"] 