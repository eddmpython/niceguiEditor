# niceguiEditor

NiceGUI 기반 실시간 에디터 라이브러리

이 라이브러리는 NiceGUI 앱에 실시간 에디터 기능을 추가합니다. 개발자는 앱이 실행되는 동안 UI 컴포넌트를 동적으로 수정하고 테스트할 수 있어 개발 효율성을 높일 수 있습니다.

## 특징

- 앱 리로드 없이 UI 컴포넌트 실시간 수정
- 코드 에디터 내장
- 간편한 통합 (단 한 줄의 코드로 추가)
- NiceGUI 컴포넌트 전체 지원

## 설치 방법

```bash
# 저장소에서 직접 설치
pip install -e .

# 또는 개발 모드로 설치
pip install -e .
```

## 사용 방법

### 기본 사용법

```python
from nicegui import ui
import niceguiEditor

# 기본 UI 설정
with ui.page('/'):
    ui.label('Hello, World!')
    
    # 에디터로 커스터마이징할 영역
    with ui.card().classes('w-full p-4'):
        ui.label('이 영역을 커스터마이징하세요')

# 에디터 활성화 (단 한 줄로 추가)
niceguiEditor.enable()

# 앱 실행
ui.run()
```

### 에디터 사용하기

1. 앱이 실행되면 우측 상단에 "에디터" 버튼이 표시됩니다.
2. 버튼을 클릭하면 코드 에디터가 열립니다.
3. 에디터에서 코드를 작성하고 "실행" 버튼을 클릭하면 변경사항이 즉시 적용됩니다.

## 의존성

- Python 3.10 이상
- nicegui 1.3.5 이상
- plotly 5.14.0 이상

## 개발 환경 설정

```bash
# 가상 환경 생성
python -m venv .venv

# 가상 환경 활성화 (Windows)
.venv\Scripts\activate

# 가상 환경 활성화 (Linux/Mac)
source .venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 개발 모드로 설치
pip install -e .
```

## 테스트 실행

```bash
# 테스트 앱 실행
python -m niceguiEditor.tests.test_basic

# 예제 앱 실행
python -m niceguiEditor.examples.simple_app
```

## 라이선스

MIT 라이선스 