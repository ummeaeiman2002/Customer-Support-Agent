(function () {
  "use strict";

  var ERROR_FALLBACK =
    "Sorry, I couldn't process your request right now. Please try again.";
  var MAX_TOPICS = 5;

  var chatScroll = document.getElementById("chatScroll");
  var emptyState = document.getElementById("emptyState");
  var form = document.getElementById("composer");
  var input = document.getElementById("input");
  var sendBtn = document.getElementById("sendBtn");
  var newChatBtn = document.getElementById("newChat");
  var topicsEl = document.getElementById("topics");
  var sidebarLeft = document.getElementById("sidebarLeft");
  var menuBtn = document.getElementById("menuBtn");
  var drawerClose = document.getElementById("drawerClose");
  var overlay = document.getElementById("overlay");

  var messages = [];
  var topics = [];
  var busy = false;
  var typingRow = null;

  /* ---------- API layer ---------- */

  var api = {
    sendMessage: function (text) {
      return fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text })
      }).then(function (res) {
        return res.json().then(function (data) {
          if (!res.ok || !data.reply) {
            throw new Error(data.error || ERROR_FALLBACK);
          }
          return data.reply;
        });
      });
    },
    reset: function () {
      return fetch("/api/reset", { method: "POST" });
    }
  };

  /* ---------- helpers ---------- */

  function escapeHtml(s) {
    return s
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function formatTime(d) {
    return d.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
  }

  function escapeAttr(s) {
    return escapeHtml(s).replace(/'/g, "&#39;");
  }

  /* markdown-lite: paragraphs, line breaks, bold, inline code, links, lists */
  function renderRich(text) {
    var lines = escapeHtml(text).split(/\r?\n/);
    var html = "";
    var para = [];
    var list = null; // "ul" | "ol"

    function flushPara() {
      if (para.length) {
        html += "<p>" + para.join("<br>") + "</p>";
        para = [];
      }
    }
    function flushList() {
      if (list) {
        html += "<" + list + ">" + htmlItems.join("") + "</" + list + ">";
        list = null;
        htmlItems = [];
      }
    }
    var htmlItems = [];

    for (var i = 0; i < lines.length; i++) {
      var line = lines[i];
      var ul = line.match(/^\s*[-*]\s+(.*)$/);
      var ol = line.match(/^\s*\d+[.)]\s+(.*)$/);
      if (ul) {
        flushPara();
        if (list !== "ul") { flushList(); list = "ul"; }
        htmlItems.push("<li>" + inline(ul[1]) + "</li>");
      } else if (ol) {
        flushPara();
        if (list !== "ol") { flushList(); list = "ol"; }
        htmlItems.push("<li>" + inline(ol[1]) + "</li>");
      } else if (line.trim() === "") {
        flushList();
        flushPara();
      } else {
        flushList();
        para.push(inline(line));
      }
    }
    flushList();
    flushPara();
    return html;

    function inline(s) {
      s = s.replace(/`([^`]+)`/g, "<code>$1</code>");
      s = s.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
      s = s.replace(
        /(https?:\/\/[^\s<]+[^\s<.,;:!?)])/g,
        '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
      );
      return s;
    }
  }

  function nearBottom() {
    return (
      chatScroll.scrollHeight - chatScroll.scrollTop - chatScroll.clientHeight <
      120
    );
  }

  function scrollToBottom() {
    chatScroll.scrollTop = chatScroll.scrollHeight;
  }

  /* ---------- rendering ---------- */

  function hideEmpty() {
    if (emptyState && emptyState.parentNode) emptyState.remove();
  }

  function addRow(role, time) {
    var row = document.createElement("div");
    row.className = "row " + role;

    if (role === "bot") {
      row.innerHTML =
        '<div class="avatar avatar-ai" aria-hidden="true">' +
        '<svg class="icon" viewBox="0 0 24 24"><use href="#i-bot"/></svg></div>' +
        '<div class="stack"></div>';
    } else {
      row.innerHTML =
        '<div class="stack"></div>' +
        '<div class="avatar avatar-user" aria-hidden="true">' +
        '<svg class="icon" viewBox="0 0 24 24"><use href="#i-user"/></svg></div>';
    }
    chatScroll.appendChild(row);

    var meta = document.createElement("div");
    meta.className = "meta";
    meta.innerHTML =
      "<span>" + formatTime(time) + "</span>" +
      (role === "user" ? '<span class="check" title="Sent">&#10003;</span>' : "");

    row.querySelector(".stack").appendChild(meta);
    return row;
  }

  function appendUser(text, time) {
    hideEmpty();
    var row = addRow("user", time);
    var stack = row.querySelector(".stack");
    var bubble = document.createElement("div");
    bubble.className = "bubble user";
    bubble.innerHTML = renderRich(text);
    stack.insertBefore(bubble, metaOf(stack));
    scrollToBottom();
  }

  function appendBot(text, time) {
    var row = addRow("bot", time);
    var stack = row.querySelector(".stack");
    var bubble = document.createElement("div");
    bubble.className = "bubble bot";
    bubble.innerHTML = renderRich(text);
    stack.insertBefore(bubble, metaOf(stack));
    scrollToBottom();
  }

  function metaOf(stack) {
    return stack.querySelector(".meta");
  }

  function appendError() {
    var note = document.createElement("div");
    note.className = "error-note";
    note.textContent = ERROR_FALLBACK;
    chatScroll.appendChild(note);
    scrollToBottom();
  }

  function showTyping() {
    hideEmpty();
    var row = document.createElement("div");
    row.className = "row bot";
    row.innerHTML =
      '<div class="avatar avatar-ai" aria-hidden="true">' +
      '<svg class="icon" viewBox="0 0 24 24"><use href="#i-bot"/></svg></div>' +
      '<div class="bubble bot typing-bubble" aria-label="Assistant is typing">' +
      "<i></i><i></i><i></i></div>";
    chatScroll.appendChild(row);
    typingRow = row;
    scrollToBottom();
  }

  function hideTyping() {
    if (typingRow && typingRow.parentNode) typingRow.remove();
    typingRow = null;
  }

  /* ---------- recent topics ---------- */

  function addTopic(text) {
    var title = text.length > 46 ? text.slice(0, 46).trim() + "…" : text;
    topics.unshift({ title: title, at: Date.now() });
    if (topics.length > MAX_TOPICS) topics.length = MAX_TOPICS;
    renderTopics();
  }

  function relativeTime(at) {
    var mins = Math.floor((Date.now() - at) / 60000);
    if (mins < 1) return "just now";
    if (mins === 1) return "1 min ago";
    if (mins < 60) return mins + " min ago";
    var hrs = Math.floor(mins / 60);
    return hrs === 1 ? "1 hour ago" : hrs + " hours ago";
  }

  function renderTopics() {
    if (!topics.length) {
      topicsEl.innerHTML = '<li class="topics-empty">No recent topics yet.</li>';
      return;
    }
    topicsEl.innerHTML = topics
      .map(function (t) {
        return (
          '<li class="topic">' +
          '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-clock"/></svg>' +
          "<div>" +
          '<div class="topic-title" title="' + escapeAttr(t.title) + '">' +
          escapeHtml(t.title) + "</div>" +
          '<div class="topic-time">' + relativeTime(t.at) + "</div>" +
          "</div></li>"
        );
      })
      .join("");
  }

  setInterval(renderTopics, 30000);

  /* ---------- busy state ---------- */

  function setBusy(b) {
    busy = b;
    input.disabled = b;
    sendBtn.disabled = b;
    document.querySelectorAll(".qa").forEach(function (el) {
      el.disabled = b;
    });
    if (!b) input.focus();
  }

  /* ---------- send flow ---------- */

  function ask(text) {
    if (busy) return;
    text = text.trim();
    if (!text) return;

    input.value = "";
    autoGrow();

    var now = new Date();
    messages.push({ role: "user", content: text, time: now });
    appendUser(text, now);
    addTopic(text);

    setBusy(true);
    showTyping();

    api
      .sendMessage(text)
      .then(function (reply) {
        hideTyping();
        var t = new Date();
        messages.push({ role: "assistant", content: reply, time: t });
        appendBot(reply, t);
      })
      .catch(function () {
        hideTyping();
        appendError();
      })
      .then(function () {
        setBusy(false);
      });
  }

  /* ---------- composer ---------- */

  function autoGrow() {
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 120) + "px";
  }

  input.addEventListener("input", autoGrow);

  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      var t = input.value.trim();
      if (t && !busy) ask(t);
    }
  });

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    if (busy) return;
    var t = input.value.trim();
    if (!t) return;
    ask(t);
  });

  /* ---------- suggestions & quick actions ---------- */

  document.querySelectorAll(".suggestion").forEach(function (btn) {
    btn.addEventListener("click", function () {
      ask(btn.textContent.trim());
    });
  });

  document.querySelectorAll(".qa").forEach(function (btn) {
    btn.addEventListener("click", function () {
      ask(btn.getAttribute("data-q"));
    });
  });

  /* ---------- new chat / reset ---------- */

  newChatBtn.addEventListener("click", function () {
    if (busy) return;
    api.reset().catch(function () {});
    messages = [];
    topics = [];
    renderTopics();
    chatScroll.innerHTML =
      '<div class="empty-state" id="emptyState">' +
      '<div class="empty-greeting">Hello! &#128075;</div>' +
      '<p class="empty-line">How can I help you today?</p>' +
      '<p class="empty-hint">Try asking about:</p>' +
      '<div class="suggestions">' +
      '<button class="suggestion">Track my order</button>' +
      '<button class="suggestion">What is your refund policy?</button>' +
      '<button class="suggestion">How do I return a product?</button>' +
      '<button class="suggestion">Contact support</button>' +
      "</div></div>";
    chatScroll.querySelectorAll(".suggestion").forEach(function (btn) {
      btn.addEventListener("click", function () {
        ask(btn.textContent.trim());
      });
    });
    emptyState = document.getElementById("emptyState");
    input.focus();
  });

  /* ---------- mobile drawer ---------- */

  function openDrawer() {
    sidebarLeft.classList.add("open");
    overlay.hidden = false;
  }
  function closeDrawer() {
    sidebarLeft.classList.remove("open");
    overlay.hidden = true;
  }

  menuBtn.addEventListener("click", openDrawer);
  drawerClose.addEventListener("click", closeDrawer);
  overlay.addEventListener("click", closeDrawer);

  /* ---------- view switching (Chat / Knowledge Base) ---------- */

  var chatCard = document.querySelector(".chat-card");
  var viewTitle = document.getElementById("viewTitle");
  var viewSubtitle = document.getElementById("viewSubtitle");
  var navChat = document.getElementById("navChat");
  var navKnowledge = document.getElementById("navKnowledge");
  var kbView = document.getElementById("kbView");
  var kbDocs = document.getElementById("kbDocs");
  var kbContent = document.getElementById("kbContent");
  var kbSearch = document.getElementById("kbSearch");
  var kbSearchBtn = document.getElementById("kbSearchBtn");

  var CHAT_TITLE = viewTitle.textContent;
  var CHAT_SUBTITLE = viewSubtitle.textContent;
  var KB_TITLE = "Knowledge Base";
  var KB_SUBTITLE =
    "Browse the company knowledge documents — the same source the agent answers from.";
  var kbLoaded = false;

  function setActiveNav(active) {
    [navChat, navKnowledge].forEach(function (el) {
      var on = el === active;
      el.classList.toggle("active", on);
      if (on) el.setAttribute("aria-current", "page");
      else el.removeAttribute("aria-current");
    });
  }

  function showView(view) {
    var kb = view === "knowledge";
    chatCard.hidden = kb;
    kbView.hidden = !kb;
    newChat.style.display = kb ? "none" : "";
    viewTitle.textContent = kb ? KB_TITLE : CHAT_TITLE;
    viewSubtitle.textContent = kb ? KB_SUBTITLE : CHAT_SUBTITLE;
    setActiveNav(kb ? navKnowledge : navChat);
    if (kb) {
      loadKB();
      kbSearch.focus();
    } else {
      input.focus();
    }
    closeDrawer();
  }

  navChat.addEventListener("click", function () {
    showView("chat");
  });
  navKnowledge.addEventListener("click", function () {
    showView("knowledge");
  });

  /* ---------- knowledge base ---------- */

  function renderDoc(md) {
    var lines = escapeHtml(md).split(/\r?\n/);
    var out = [];
    var buf = [];
    var list = null;
    var items = [];

    function inline(s) {
      s = s.replace(/`([^`]+)`/g, "<code>$1</code>");
      s = s.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
      s = s.replace(
        /\[([^\]]+)\]\((https?:[^)\s]+)\)/g,
        '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>'
      );
      return s;
    }
    function flushP() {
      if (buf.length) {
        out.push("<p>" + inline(buf.join(" ")) + "</p>");
        buf = [];
      }
    }
    function flushL() {
      if (list) {
        out.push("<" + list + ">" + items.join("") + "</" + list + ">");
        list = null;
        items = [];
      }
    }
    function flushAll() {
      flushP();
      flushL();
    }

    for (var i = 0; i < lines.length; i++) {
      var line = lines[i];
      var h = line.match(/^(#{1,6})\s+(.*)$/);
      var ul = line.match(/^\s*[-*]\s+(.*)$/);
      var ol = line.match(/^\s*\d+[.)]\s+(.*)$/);
      if (h) {
        flushAll();
        var n = h[1].length;
        out.push("<h" + n + ">" + inline(h[2]) + "</h" + n + ">");
      } else if (line.trim() === "") {
        flushAll();
      } else if (ul || ol) {
        flushP();
        var kind = ul ? "ul" : "ol";
        var text = ul ? ul[1] : ol[1];
        if (list !== kind) {
          flushL();
          list = kind;
        }
        items.push("<li>" + inline(text) + "</li>");
      } else if (list && /^\s{2,}\S/.test(line)) {
        items[items.length - 1] = items[items.length - 1].replace(
          /<\/li>$/,
          " " + inline(line.trim()) + "</li>"
        );
      } else {
        flushL();
        buf.push(line.trim());
      }
    }
    flushAll();
    return out.join("");
  }

  function loadKB() {
    if (kbLoaded) return;
    fetch("/api/knowledge")
      .then(function (r) {
        return r.json();
      })
      .then(function (data) {
        kbLoaded = true;
        var docs = data.documents || [];
        if (!docs.length) {
          kbDocs.innerHTML = '<p class="kb-empty">No documents found.</p>';
          return;
        }
        kbDocs.innerHTML = "";
        docs.forEach(function (d) {
          var btn = document.createElement("button");
          btn.className = "kb-doc";
          btn.dataset.name = d.name;
          btn.innerHTML =
            '<span class="kb-doc-title">' +
            escapeHtml(d.title) +
            '</span><span class="kb-doc-name">' +
            escapeHtml(d.name) +
            "</span>";
          btn.addEventListener("click", function () {
            openDoc(d.name);
          });
          kbDocs.appendChild(btn);
        });
      })
      .catch(function () {
        kbLoaded = false;
        kbDocs.innerHTML =
          '<p class="kb-empty">Could not load documents.</p>';
      });
  }

  function markActiveDoc(name) {
    kbDocs.querySelectorAll(".kb-doc").forEach(function (el) {
      el.classList.toggle("active", el.dataset.name === name);
    });
  }

  function kbMessage(text) {
    kbContent.innerHTML =
      '<div class="kb-placeholder">' + escapeHtml(text) + "</div>";
  }

  function openDoc(name) {
    kbContent.innerHTML =
      '<div class="kb-placeholder">Loading ' + escapeHtml(name) + "…</div>";
    fetch("/api/knowledge/" + encodeURIComponent(name))
      .then(function (r) {
        return r.json();
      })
      .then(function (data) {
        if (!data.content) {
          kbMessage(data.error || "Document not found.");
          return;
        }
        kbContent.innerHTML =
          '<article class="kb-doc-body">' + renderDoc(data.content) + "</article>";
        kbContent.scrollTop = 0;
        markActiveDoc(name);
      })
      .catch(function () {
        kbMessage("Could not load the document.");
      });
  }

  function doSearch() {
    var q = kbSearch.value.trim();
    if (!q) return;
    kbContent.innerHTML = '<div class="kb-placeholder">Searching…</div>';
    fetch("/api/knowledge/search?q=" + encodeURIComponent(q))
      .then(function (r) {
        return r.json();
      })
      .then(function (data) {
        if (data.error) {
          kbMessage(data.error);
          return;
        }
        var results = data.results || [];
        if (!results.length) {
          kbMessage('No results for "' + q + '".');
          return;
        }
        var html =
          '<div class="kb-results">' +
          '<h3 class="kb-results-title">' +
          results.length +
          ' result' + (results.length === 1 ? "" : "s") +
          ' for "' + escapeHtml(q) + '"</h3>';
        results.forEach(function (r) {
          html +=
            '<button class="kb-result" data-source="' + escapeAttr(r.source) + '">' +
            '<div class="kb-result-head">' +
            '<span class="kb-result-src">' + escapeHtml(r.source) + "</span>" +
            '<span class="kb-result-score">match ' +
            Math.round(r.score * 100) +
            "%</span></div>" +
            '<p class="kb-result-text">' +
            escapeHtml(r.text).replace(/\n/g, "<br>") +
            "</p></button>";
        });
        html += "</div>";
        kbContent.innerHTML = html;
        kbContent.querySelectorAll(".kb-result").forEach(function (el) {
          el.addEventListener("click", function () {
            openDoc(el.dataset.source);
          });
        });
        kbContent.scrollTop = 0;
      })
      .catch(function () {
        kbMessage("Search failed. Please retry.");
      });
  }

  kbSearchBtn.addEventListener("click", doSearch);
  kbSearch.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
      e.preventDefault();
      doSearch();
    }
  });

  /* ---------- init ---------- */

  renderTopics();
  input.focus();
})();
