(function () {
  "use strict";

  let isConnected = false;
  let currentConvoId = null;

  // Create AI suggestion panel
  const panel = document.createElement("div");
  panel.id = "__ai_panel__";
  panel.style.cssText =
    "display:none;position:fixed;bottom:160px;right:20px;width:380px;max-height:300px;" +
    "background:#1a1a2e;border:1px solid rgba(100,130,255,0.3);border-radius:12px;" +
    "padding:16px;z-index:99999;color:#e0e0e0;font-size:14px;box-shadow:0 8px 32px rgba(0,0,0,0.4);" +
    "font-family:'PingFang SC','Microsoft YaHei',sans-serif;";
  panel.innerHTML =
    '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">' +
    '<span style="color:#a0b4ff;font-weight:600;font-size:13px;">AI 回复建议</span>' +
    '<div>' +
    '<span id="__ai_status__" style="font-size:11px;color:#666;"></span>' +
    '<button id="__ai_close__" style="background:none;border:none;color:#666;cursor:pointer;font-size:16px;">×</button>' +
    "</div>" +
    "</div>" +
    '<div id="__ai_content__" style="line-height:1.8;min-height:40px;color:#d0d0e0;"></div>' +
    '<div style="margin-top:12px;display:flex;gap:8px;">' +
    '<button id="__ai_fill__" style="flex:1;padding:8px;background:#3a3a6e;border:none;border-radius:8px;' +
    'color:#a0b4ff;cursor:pointer;font-size:13px;">📋 填入输入框</button>' +
    '<button id="__ai_refresh__" style="padding:8px 16px;background:transparent;border:1px solid rgba(100,130,255,0.2);' +
    'border-radius:8px;color:#888;cursor:pointer;font-size:13px;">换一个</button>' +
    "</div>";
  document.body.appendChild(panel);

  document.getElementById("__ai_close__").onclick = () => {
    panel.style.display = "none";
  };

  document.getElementById("__ai_fill__").onclick = () => {
    const text = panel._currentReply || "";
    fillInputBox(text);
  };

  document.getElementById("__ai_refresh__").onclick = () => {
    requestNewReply();
  };

  function fillInputBox(text) {
    const inputSelectors = [
      'textarea[placeholder*="输入"]',
      'div[contenteditable="true"]',
      '[class*="chat"] textarea',
      '[class*="input"] textarea',
    ];
    for (const sel of inputSelectors) {
      const input = document.querySelector(sel);
      if (input) {
        if (input.tagName === "TEXTAREA" || input.tagName === "INPUT") {
          input.value = text;
          input.dispatchEvent(new Event("input", { bubbles: true }));
        } else {
          input.textContent = text;
          input.dispatchEvent(new Event("input", { bubbles: true }));
        }
        // Visual feedback
        const contentEl = panel.querySelector("#__ai_content__");
        if (contentEl) {
          contentEl.style.borderLeft = "2px solid #4caf50";
          contentEl.style.paddingLeft = "12px";
          setTimeout(() => {
            contentEl.style.borderLeft = "none";
            contentEl.style.paddingLeft = "0";
          }, 2000);
        }
        return;
      }
    }
  }

  function requestNewReply() {
    if (!currentConvoId) return;
    chrome.runtime.sendMessage({
      type: "user_message",
      data: { convo_id: currentConvoId, request_new: true },
    });
  }

  // Watch for new messages in Douyin chat DOM
  function watchChatMessages() {
    const observer = new MutationObserver((mutations) => {
      for (const m of mutations) {
        for (const node of m.addedNodes) {
          if (node.nodeType !== Node.ELEMENT_NODE) continue;
          const msgText = extractMessageText(node);
          if (msgText && msgText.trim().length > 0) {
            onNewMessage(msgText.trim());
          }
        }
      }
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }

  function extractMessageText(node) {
    const selectors = [
      '[class*="message"] [class*="content"]',
      '[class*="msg"] [class*="text"]',
      '[class*="chat"] [class*="bubble"]',
    ];
    for (const sel of selectors) {
      const el = node.matches?.(sel) ? node : node.querySelector?.(sel);
      if (el && el.textContent && el.textContent.trim().length > 3) {
        return el.textContent;
      }
    }
    return null;
  }

  function onNewMessage(text, convoId) {
    currentConvoId = convoId || currentConvoId;
    panel.style.display = "block";
    const contentEl = document.getElementById("__ai_content__");
    const statusEl = document.getElementById("__ai_status__");
    if (contentEl) contentEl.textContent = "AI 思考中...";
    if (statusEl) statusEl.textContent = "思考中...";

    chrome.runtime.sendMessage({
      type: "user_message",
      data: {
        convo_id: currentConvoId || window.location.href,
        content: text,
        platform: "douyin",
      },
    });
  }

  // Listen for messages from background
  chrome.runtime.onMessage.addListener((message) => {
    if (message.type === "ws_status") {
      isConnected = message.connected;
      const statusEl = document.getElementById("__ai_status__");
      if (statusEl) statusEl.textContent = isConnected ? "● 在线" : "○ 离线";
    } else if (message.type === "ai_reply") {
      if (message.convo_id) currentConvoId = message.convo_id;
      panel._currentReply = message.content;
      const contentEl = document.getElementById("__ai_content__");
      const statusEl = document.getElementById("__ai_status__");
      if (contentEl) contentEl.textContent = message.content;
      if (statusEl) statusEl.textContent = "● 就绪";
      panel.style.display = "block";
    }
  });

  // Init
  watchChatMessages();
  chrome.runtime.sendMessage({ type: "get_status" }, (resp) => {
    if (resp) {
      isConnected = resp.connected;
      const statusEl = document.getElementById("__ai_status__");
      if (statusEl) statusEl.textContent = isConnected ? "● 在线" : "○ 离线";
    }
  });
})();
