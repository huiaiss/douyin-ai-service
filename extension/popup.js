const statusDot = document.getElementById("status_dot");
const statusText = document.getElementById("status_text");
const btnMode = document.getElementById("btn_mode");
const btnSettings = document.getElementById("btn_settings");

let currentMode = "suggest";

chrome.runtime.sendMessage({ type: "get_status" }, (resp) => {
  if (resp && resp.connected) {
    statusDot.className = "dot online";
    statusText.textContent = "已连接";
  } else {
    statusDot.className = "dot offline";
    statusText.textContent = "未连接";
  }
});

btnSettings.onclick = () => {
  chrome.tabs.create({ url: "http://localhost:8000/admin" });
};

btnMode.onclick = () => {
  currentMode = currentMode === "suggest" ? "alert_only" : "suggest";
  btnMode.textContent =
    currentMode === "suggest" ? "模式：建议模式" : "模式：仅提醒";
  chrome.storage.local.set({ reply_mode: currentMode });
};

chrome.storage.local.get("reply_mode", (data) => {
  if (data.reply_mode) {
    currentMode = data.reply_mode;
    btnMode.textContent =
      currentMode === "suggest" ? "模式：建议模式" : "模式：仅提醒";
  }
});
