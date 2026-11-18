from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

# FastAPI 앱 생성
app = FastAPI()

# -----------------------------
# HTML 클라이언트 코드
# 브라우저에서 채팅 UI 역할
# -----------------------------
html = """
<!DOCTYPE html>
<html>
<head>
    <title>FastAPI WebSocket Chat</title>
</head>
<body>

<h1>WebSocket Chat</h1>

<!-- 사용자 이름 입력 -->
<input type="text" id="username" placeholder="username">

<br><br>

<!-- 메시지 입력 -->
<form onsubmit="sendMessage(event)">
    <input type="text" id="messageText" autocomplete="off">
    <button>Send</button>
</form>

<ul id='messages'></ul>

<script>

    // FastAPI WebSocket 서버 연결
    var ws = new WebSocket("ws://127.0.0.1:8000/ws");

    // 서버에서 메시지 받으면 화면에 출력
    ws.onmessage = function(event) {
        var messages = document.getElementById('messages');

        var message = document.createElement('li');
        var content = document.createTextNode(event.data);

        message.appendChild(content);
        messages.appendChild(message);
    };

    // 메시지 전송 함수
    function sendMessage(event) {

        var username = document.getElementById("username").value;
        var input = document.getElementById("messageText");

        // JSON 형식 메시지 생성
        var payload = {
            username: username,
            message: input.value
        };

        // 서버로 메시지 전송
        ws.send(JSON.stringify(payload));

        input.value = '';
        event.preventDefault();
    }

</script>

</body>
</html>
"""


# -----------------------------------------
# WebSocket 연결 관리 클래스
# 현재 접속 중인 사용자 관리
# -----------------------------------------
class ConnectionManager:

    def __init__(self):
        # 현재 접속한 WebSocket 목록
        self.active_connections = []

    async def connect(self, websocket: WebSocket):

        # WebSocket 연결 허용
        await websocket.accept()

        # 접속 목록에 추가
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):

        # 연결 종료 시 목록에서 제거
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):

        # 현재 접속한 모든 사용자에게 메시지 전송
        for connection in self.active_connections:
            await connection.send_text(message)


# ConnectionManager 객체 생성
manager = ConnectionManager()


# -----------------------------------------
# 기본 페이지
# 브라우저에서 채팅 UI 열기
# -----------------------------------------
@app.get("/")
async def get():
    return HTMLResponse(html)


# -----------------------------------------
# WebSocket 채팅 엔드포인트
# -----------------------------------------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    # 사용자 접속 처리
    await manager.connect(websocket)

    try:

        # 접속 알림
        await manager.broadcast("새 사용자가 입장했습니다.")

        while True:

            # 클라이언트 메시지 수신
            data = await websocket.receive_json()

            username = data.get("username", "anonymous")
            message = data.get("message", "")

            # 메시지를 모든 사용자에게 전송
            await manager.broadcast(f"{username}: {message}")

    except WebSocketDisconnect:

        # 연결 종료 시 처리
        manager.disconnect(websocket)

        await manager.broadcast("한 사용자가 나갔습니다.")
        