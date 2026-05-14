let ws = null;
let reconnectTimer = null;

function connect() {
  if (ws && ws.readyState === WebSocket.OPEN) return;

  ws = new WebSocket("ws://localhost:8765");

  ws.onopen = () => {
    console.log("[AI客服] WebSocket 已连接");
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }
    broadcastToTabs({ type: "ws_status", connected: true });
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      broadcastToTabs(data);
    } catch (e) {
      console.error("[AI客服] 消息解析失败", e);
    }
  };

  ws.onclose = () => {
    console.log("[AI客服] WebSocket 断开，5秒后重连");
    broadcastToTabs({ type: "ws_status", connected: false });
    reconnectTimer = setTimeout(connect, 5000);
  };

  ws.onerror = (err) => {
    console.error("[AI客服] WebSocket 错误", err);
  };
}

function broadcastToTabs(data) {
  chrome.tabs.query(
    { url: ["https://fxg.jinritemai.com/*", "https://buyin.jinritemai.com/*"] },
    (tabs) => {
      tabs.forEach((tab) => {
        chrome.tabs.sendMessage(tab.id, data).catch(() => {});
      });
    }
  );
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "user_message") {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(message.data));
    }
  } else if (message.type === "get_status") {
    sendResponse({ connected: ws && ws.readyState === WebSocket.OPEN });
  }
});

connect();
