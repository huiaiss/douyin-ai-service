// ==UserScript==
// @name         抖音 AI 客服助手
// @namespace    https://github.com/douyin-ai-service
// @version      0.1.0
// @description  AI 智能回复建议，帮你打字，绝不自动发送
// @author       douyin-ai
// @match        https://fxg.jinritemai.com/*
// @match        https://buyin.jinritemai.com/*
// @grant        GM_addStyle
// @grant        GM_getValue
// @grant        GM_setValue
// @grant        unsafeWindow
// @run-at       document-end
// ==/UserScript==

(function () {
  "use strict";

  // ========== 样式注入 ==========
  GM_addStyle(`
    #__ai_panel__ { transition: opacity 0.3s ease; }
    #__ai_content__ { transition: border-left 0.2s ease, padding-left 0.2s ease; }
  `);

  // ========== WebSocket 连接 ==========
  let ws = null;
  let reconnectTimer = null;
  let isConnected = false;
  let currentConvoId = null;
  let currentMode = "suggest"; // suggest | alert_only

  function connectWS() {
    if (ws && ws.readyState === WebSocket.OPEN) return;
    ws = new WebSocket("ws://localhost:8765");

    ws.onopen = () => {
      isConnected = true;
      updateStatus("● 在线", true);
      if (reconnectTimer) { clearTimeout(reconnectTimer); reconnectTimer = null; }
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "ai_reply") {
          if (data.convo_id) currentConvoId = data.convo_id;
          panel._currentReply = data.content;
          const contentEl = document.getElementById("__ai_content__");
          const statusEl = document.getElementById("__ai_status__");
          if (contentEl) contentEl.textContent = data.content;
          if (statusEl) statusEl.textContent = data.handoff ? "已转人工" : "● 就绪";
          panel.style.display = "block";
        }
      } catch (e) {}
    };

    ws.onclose = () => {
      isConnected = false;
      updateStatus("○ 离线", false);
      reconnectTimer = setTimeout(connectWS, 5000);
    };

    ws.onerror = () => {};
  }

  function sendMessage(data) {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(data));
    }
  }

  connectWS();

  // ========== AI 建议面板 ==========
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
    '<div style="display:flex;align-items:center;gap:8px;">' +
    '<button id="__ai_mode__" style="background:transparent;border:1px solid rgba(100,130,255,0.2);' +
    'border-radius:6px;color:#888;cursor:pointer;font-size:11px;padding:2px 8px;">建议模式</button>' +
    '<span id="__ai_status__" style="font-size:11px;color:#666;"></span>' +
    '<button id="__ai_close__" style="background:none;border:none;color:#666;cursor:pointer;font-size:16px;">×</button>' +
    "</div>" +
    "</div>" +
    '<div id="__ai_content__" style="line-height:1.8;min-height:40px;color:#d0d0e0;"></div>' +
    '<div style="margin-top:12px;display:flex;gap:8px;">' +
    '<button id="__ai_fill__" style="flex:1;padding:8px;background:#3a3a6e;border:none;border-radius:8px;' +
    'color:#a0b4ff;cursor:pointer;font-size:13px;">填入输入框</button>' +
    '<button id="__ai_refresh__" style="padding:8px 16px;background:transparent;border:1px solid rgba(100,130,255,0.2);' +
    'border-radius:8px;color:#888;cursor:pointer;font-size:13px;">换一个</button>' +
    "</div>";
  document.body.appendChild(panel);

  function updateStatus(text, online) {
    const statusEl = document.getElementById("__ai_status__");
    if (statusEl) statusEl.textContent = text;
    isConnected = online;
  }

  // ========== 面板按钮事件 ==========
  document.getElementById("__ai_close__").onclick = () => { panel.style.display = "none"; };

  document.getElementById("__ai_fill__").onclick = () => {
    fillInputBox(panel._currentReply || "");
  };

  document.getElementById("__ai_refresh__").onclick = () => {
    if (!currentConvoId) return;
    sendMessage({ type: "user_message", data: { convo_id: currentConvoId, request_new: true } });
  };

  document.getElementById("__ai_mode__").onclick = () => {
    currentMode = currentMode === "suggest" ? "alert_only" : "suggest";
    document.getElementById("__ai_mode__").textContent =
      currentMode === "suggest" ? "建议模式" : "仅提醒";
    GM_setValue("reply_mode", currentMode);
  };

  // 恢复模式
  const savedMode = GM_getValue("reply_mode");
  if (savedMode) {
    currentMode = savedMode;
    document.getElementById("__ai_mode__").textContent =
      currentMode === "suggest" ? "建议模式" : "仅提醒";
  }

  // ========== 填入输入框 ==========
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

  // ========== 监听抖音聊天 DOM ==========
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

    sendMessage({
      type: "user_message",
      data: {
        convo_id: currentConvoId || window.location.href,
        content: text,
        platform: "douyin",
      },
    });
  }

  // ========== 启动 ==========
  watchChatMessages();
  updateStatus(isConnected ? "● 在线" : "○ 离线", isConnected);

})();
