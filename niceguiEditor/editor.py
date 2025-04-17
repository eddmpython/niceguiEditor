from nicegui import ui, app
import inspect
import os
import re
import sys
import importlib
import importlib.util
import traceback
import textwrap
import uuid


class Editor:
    def __init__(self, endpoint, callerInfo=None):
        self.endpoint = endpoint
        self.callerInfo = callerInfo
        self.editorDialog = None
        self.codeEditor = None
        self.sourceCode = None
        self.sourceFile = None
        self.setupDialog()
        self.setupClientCode()

    def setupDialog(self):
        self.editorDialog = ui.dialog()
        with self.editorDialog:
            with ui.card().classes('w-full h-full p-0 rounded-3xl gap-0'):
                with ui.row().classes('w-full justify-between items-center bg-[#1A1B1D] text-white p-2'):
                    self.filePathLabel = ui.label('Source: Unknown').classes('text-sm')
                    with ui.row().classes('gap-1'):
                        ui.button('실행', icon='play_arrow', on_click=self.runCode).props('flat color=green')
                        ui.button('저장', icon='save', on_click=self.saveCode).props('flat color=blue')
                        ui.button('닫기', icon='close', on_click=self.editorDialog.close).props('flat color=red')

                self.codeEditor = ui.codemirror('# Loading...', language='python', theme='monokai').classes('h-full w-full')

    def setupClientCode(self):
        ui.run_javascript('''
        window.editorSocket = {
            updateComponent: function(sourceFile) {
                const fileId = sourceFile.replace(/[^a-zA-Z0-9]/g, '_');
                console.log('요청된 컴포넌트 업데이트:', fileId);
                
                // NiceGUI 소켓에 커스텀 이벤트 발송
                if (window._nicegui && window._nicegui.socket) {
                    window._nicegui.socket.emit('client_custom_event', {
                        name: 'editor_update', 
                        args: {fileId: fileId, sourceFile: sourceFile}
                    });
                }
                
                // UI 업데이트 시도
                document.querySelectorAll('[data-nicegui-component]').forEach(comp => {
                    if (comp._update && typeof comp._update === 'function') {
                        try {
                            comp._update();
                        } catch (e) {}
                    }
                });
                
                // 특수 엘리먼트 찾기
                const targetElem = document.querySelector(`[data-source-file="${sourceFile}"]`);
                if (targetElem) {
                    targetElem.classList.add('updated');
                    setTimeout(() => targetElem.classList.remove('updated'), 1000);
                }
            }
        };
        
        // 스타일 추가
        const style = document.createElement('style');
        style.textContent = `
            .updated {
                outline: 2px solid #4CAF50 !important;
                animation: pulse 1s !important;
            }
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.6; }
                100% { opacity: 1; }
            }
        `;
        document.head.appendChild(style);
        ''')

    def open(self):
        if not self.sourceCode:
            self.findSource()
            
        if self.sourceCode:
            self.codeEditor.set_value(self.sourceCode)
        
        self.editorDialog.open()
    
    def findSource(self):
        try:
            if not self.callerInfo or 'filename' not in self.callerInfo:
                self.sourceCode = "# No caller information available"
                return
                
            callerFile = self.callerInfo['filename']
            
            if not os.path.exists(callerFile):
                self.sourceCode = f"# File not found: {callerFile}"
                return
            
            with open(callerFile, 'r', encoding='utf-8') as f:
                self.sourceCode = f.read()
                
            self.sourceFile = callerFile
            self.filePathLabel.text = f'Source: {os.path.basename(callerFile)}'
            
        except Exception as e:
            errorDetails = traceback.format_exc()
            self.sourceCode = f"# Error: {str(e)}\n\n{errorDetails}"
            
    def saveCode(self):
        if not self.sourceFile:
            ui.notify('저장할 파일이 없습니다', color='negative')
            return
            
        try:
            editedCode = self.codeEditor.value
            if not editedCode:
                ui.notify('저장할 코드가 없습니다', color='negative')
                return
                
            backupFile = f"{self.sourceFile}.bak"
            try:
                with open(self.sourceFile, 'r', encoding='utf-8') as src:
                    with open(backupFile, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
            except Exception as e:
                ui.notify(f'백업 파일 생성 실패: {str(e)}', color='warning')
            
            with open(self.sourceFile, 'w', encoding='utf-8') as f:
                f.write(editedCode)
                
            self.sourceCode = editedCode
            
            ui.notify('파일 저장 완료', color='positive')
            
            self.reloadModule()
            
        except Exception as e:
            errorDetails = traceback.format_exc()
            ui.notify(f'저장 실패: {str(e)}', color='negative')
    
    def reloadModule(self):
        try:
            ui.notify('변경사항이 저장되었습니다', color='positive')
            
            if self.sourceFile:
                ui.run_javascript(f'''
                // 코드 변경 시 WebSocket 이벤트 발송
                if (window.editorSocket) {{
                    window.editorSocket.updateComponent("{self.sourceFile}");
                    console.log("컴포넌트 업데이트 요청: {self.sourceFile}");
                }}
                ''')
            else:
                ui.run_javascript('''
                setTimeout(() => {
                    window.location.reload();
                }, 500);
                ''')
                
        except Exception as e:
            ui.notify(f'업데이트 실패: {str(e)}', color='negative')
    
    def fixIndentation(self, code):
        try:
            try:
                dedented = textwrap.dedent(code)
                lines = dedented.split('\n')
                
                indentLevel = 0
                resultLines = []
                
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    
                    if not stripped or stripped.startswith('#'):
                        resultLines.append(' ' * indentLevel + stripped)
                        continue
                    
                    if stripped.startswith(('else:', 'elif ', 'except', 'finally:', 'except:')):
                        if indentLevel >= 4:
                            indentLevel -= 4
                    
                    resultLines.append(' ' * indentLevel + stripped)
                    
                    if stripped.endswith(':') and not stripped.startswith(('else:', 'elif', 'except:', 'finally:')):
                        indentLevel += 4
                
                return '\n'.join(resultLines)
                
            except Exception as e:
                lines = code.split('\n')
                fixedLines = []
                currentIndent = 0
                
                for line in lines:
                    stripped = line.strip()
                    if not stripped:
                        fixedLines.append('')
                        continue
                        
                    if stripped.startswith(('else:', 'elif ', 'except', 'finally:')):
                        if currentIndent >= 4:
                            currentIndent -= 4
                            
                    fixedLines.append(' ' * currentIndent + stripped)
                    
                    if stripped.endswith(':') and not stripped.startswith(('else:', 'elif', 'except:', 'finally:')):
                        currentIndent += 4
                
                return '\n'.join(fixedLines)
                
        except Exception as e:
            return code
            
    def runCode(self):
        try:
            codeToRun = self.codeEditor.value
            if not codeToRun:
                ui.notify('실행할 코드가 없습니다', color='negative')
                return
                
            try:
                compile(codeToRun, '<string>', 'exec')
            except IndentationError as ie:
                ui.notify(f'들여쓰기 오류 감지: {str(ie)}', color='warning')
                
                fixedCode = self.fixIndentation(codeToRun)
                
                try:
                    compile(fixedCode, '<string>', 'exec')
                    ui.notify('들여쓰기 자동 수정 완료', color='positive')
                    self.codeEditor.set_value(fixedCode)
                    codeToRun = fixedCode
                except Exception as e:
                    ui.notify(f'들여쓰기 자동 수정 실패: {str(e)}', color='negative')
                    
                    try:
                        wrappedCode = "def run_code():\n" + textwrap.indent(codeToRun, '    ') + "\n\nrun_code()"
                        compile(wrappedCode, '<string>', 'exec')
                        ui.notify('대체 방식으로 실행 시도', color='info')
                        codeToRun = wrappedCode
                    except Exception:
                        return
            
            tempFile = f"temp_{uuid.uuid4().hex}.py"
            try:
                with open(tempFile, 'w', encoding='utf-8') as f:
                    f.write(codeToRun)
                
                globalsDict = {
                    'ui': ui,
                    'os': os,
                    'sys': sys,
                    're': re,
                    'inspect': inspect,
                    'importlib': importlib,
                    '__file__': self.sourceFile or tempFile,
                    '__name__': '__main__'
                }
                
                localsDict = {}
                
                # 코드 실행
                exec(codeToRun, globalsDict, localsDict)
                
                ui.notify('코드 실행 완료', color='positive')
                
                if self.sourceFile:
                    ui.run_javascript(f'''
                    // 코드 실행 시 WebSocket 이벤트 발송
                    if (window.editorSocket) {{
                        window.editorSocket.updateComponent("{self.sourceFile}");
                        console.log("코드 실행 후 컴포넌트 업데이트: {self.sourceFile}");
                    }}
                    ''')
                else:
                    ui.run_javascript('''
                    setTimeout(() => {
                        window.location.reload();
                    }, 500);
                    ''')
            
            finally:
                if os.path.exists(tempFile):
                    try:
                        os.remove(tempFile)
                    except:
                        pass
            
        except Exception as e:
            errorDetails = traceback.format_exc()
            ui.notify(f'실행 오류: {str(e)}', color='negative')
            

        
