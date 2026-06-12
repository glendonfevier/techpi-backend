import { useState, useRef, useEffect } from "react";

const styles = `
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Space+Grotesk:wght@400;500;600;700&display=swap');

  .tp-root {
    font-family: 'Inter', sans-serif;
    background: #0a0a0f;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    position: relative;
    overflow: hidden;
  }

  .tp-bg-orb1 {
    position: fixed; top: -100px; right: -80px;
    width: 380px; height: 380px; border-radius: 50%;
    background: radial-gradient(circle, rgba(99,102,241,0.16) 0%, transparent 70%);
    pointer-events: none; z-index: 0;
  }
  .tp-bg-orb2 {
    position: fixed; bottom: 60px; left: -80px;
    width: 300px; height: 300px; border-radius: 50%;
    background: radial-gradient(circle, rgba(20,184,166,0.1) 0%, transparent 70%);
    pointer-events: none; z-index: 0;
  }

  .tp-header {
    padding: 18px 24px 14px;
    display: flex; align-items: center; justify-content: space-between;
    border-bottom: 0.5px solid rgba(255,255,255,0.07);
    position: relative; z-index: 10;
    background: rgba(10,10,15,0.85);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    position: sticky; top: 0;
  }

  .tp-logo-group { display: flex; align-items: center; gap: 10px; }

  .tp-logo-icon {
    width: 38px; height: 38px; border-radius: 11px;
    background: linear-gradient(135deg, #6366f1, #14b8a6);
    display: flex; align-items: center; justify-content: center;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700; font-size: 14px; color: #fff; letter-spacing: -0.5px;
    box-shadow: 0 0 20px rgba(99,102,241,0.3);
  }

  .tp-logo-text { display: flex; flex-direction: column; gap: 1px; }
  .tp-logo-name {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700; font-size: 18px; color: #fff; letter-spacing: -0.5px;
    line-height: 1;
  }
  .tp-logo-by {
    font-size: 10px; color: rgba(255,255,255,0.3);
    font-weight: 400; letter-spacing: 0.5px;
  }

  .tp-status-pill {
    display: flex; align-items: center; gap: 6px;
    background: rgba(20,184,166,0.1);
    border: 0.5px solid rgba(20,184,166,0.3);
    border-radius: 20px; padding: 5px 12px;
  }
  .tp-status-pill.error {
    background: rgba(248,113,113,0.1);
    border-color: rgba(248,113,113,0.3);
  }
  .tp-status-pill.thinking {
    background: rgba(99,102,241,0.1);
    border-color: rgba(99,102,241,0.3);
  }
  .tp-status-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: #14b8a6;
    animation: pulse-dot 2s ease-in-out infinite;
  }
  .tp-status-pill.error .tp-status-dot { background: #f87171; animation: none; }
  .tp-status-pill.thinking .tp-status-dot { background: #6366f1; }
  @keyframes pulse-dot {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.35; }
  }
  .tp-status-text { font-size: 11px; color: #14b8a6; font-weight: 500; }
  .tp-status-pill.error .tp-status-text { color: #f87171; }
  .tp-status-pill.thinking .tp-status-text { color: #818cf8; }

  .tp-messages {
    flex: 1; overflow-y: auto; padding: 24px 20px 16px;
    display: flex; flex-direction: column; gap: 16px;
    position: relative; z-index: 2;
    scrollbar-width: thin; scrollbar-color: rgba(255,255,255,0.08) transparent;
  }

  .tp-empty {
    flex: 1; display: flex; flex-direction: column;
    align-items: center; justify-content: center; gap: 10px;
    padding: 60px 24px; margin: auto;
  }
  .tp-empty-icon {
    width: 60px; height: 60px; border-radius: 18px;
    background: linear-gradient(135deg, rgba(99,102,241,0.18), rgba(20,184,166,0.12));
    border: 0.5px solid rgba(99,102,241,0.25);
    display: flex; align-items: center; justify-content: center;
    margin-bottom: 6px;
  }
  .tp-empty-title { font-size: 17px; font-weight: 500; color: rgba(255,255,255,0.7); }
  .tp-empty-sub { font-size: 13px; color: rgba(255,255,255,0.25); text-align: center; max-width: 240px; line-height: 1.6; }

  .tp-msg {
    display: flex; gap: 10px; align-items: flex-end;
    animation: msg-in 0.3s cubic-bezier(0.34,1.56,0.64,1);
  }
  @keyframes msg-in {
    from { opacity: 0; transform: translateY(12px) scale(0.96); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
  }
  .tp-msg.user { flex-direction: row-reverse; }

  .tp-avatar {
    width: 30px; height: 30px; border-radius: 50%; flex-shrink: 0;
    background: linear-gradient(135deg, #6366f1, #14b8a6);
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 600; color: #fff;
  }
  .tp-avatar.user-av {
    background: rgba(255,255,255,0.08);
    border: 0.5px solid rgba(255,255,255,0.15);
  }

  .tp-bubble {
    max-width: 70%; padding: 11px 15px;
    border-radius: 18px 18px 18px 5px;
    font-size: 14px; line-height: 1.65; color: rgba(255,255,255,0.88);
    background: rgba(255,255,255,0.07);
    border: 0.5px solid rgba(255,255,255,0.08);
    word-break: break-word; white-space: pre-wrap;
  }
  .tp-msg.user .tp-bubble {
    border-radius: 18px 18px 5px 18px;
    background: linear-gradient(135deg, rgba(99,102,241,0.3), rgba(20,184,166,0.2));
    border: 0.5px solid rgba(99,102,241,0.25);
    color: #fff;
  }

  .tp-typing {
    display: flex; gap: 4px; align-items: center; padding: 3px 0;
  }
  .tp-typing span {
    width: 5px; height: 5px; border-radius: 50%;
    background: rgba(255,255,255,0.4);
    animation: blink 1.2s ease-in-out infinite;
  }
  .tp-typing span:nth-child(2) { animation-delay: 0.2s; }
  .tp-typing span:nth-child(3) { animation-delay: 0.4s; }
  @keyframes blink {
    0%, 80%, 100% { opacity: 0.25; transform: scale(0.9); }
    40% { opacity: 1; transform: scale(1.2); }
  }

  .tp-bottom {
    position: sticky; bottom: 0; z-index: 10;
    background: rgba(10,10,15,0.9);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-top: 0.5px solid rgba(255,255,255,0.07);
    padding: 12px 16px 20px;
  }

  .tp-config-row {
    display: flex; align-items: center; gap: 8px; margin-bottom: 10px;
  }
  .tp-config-label { font-size: 10px; color: rgba(255,255,255,0.25); letter-spacing: 0.8px; white-space: nowrap; }
  .tp-api-input {
    flex: 1; background: rgba(255,255,255,0.05);
    border: 0.5px solid rgba(255,255,255,0.08);
    border-radius: 8px; padding: 6px 10px;
    font-size: 12px; color: rgba(255,255,255,0.55);
    font-family: 'Inter', monospace; outline: none;
    transition: border-color 0.2s;
  }
  .tp-api-input:focus { border-color: rgba(99,102,241,0.5); color: rgba(255,255,255,0.75); }
  .tp-api-input::placeholder { color: rgba(255,255,255,0.18); }

  .tp-err {
    font-size: 11.5px; color: #f87171;
    margin-bottom: 8px; padding-left: 2px; line-height: 1.5;
  }

  .tp-input-row { display: flex; gap: 10px; align-items: flex-end; }

  .tp-textarea {
    flex: 1; background: rgba(255,255,255,0.06);
    border: 0.5px solid rgba(255,255,255,0.1);
    border-radius: 16px; padding: 12px 16px;
    font-size: 14px; color: #fff; font-family: 'Inter', sans-serif;
    resize: none; outline: none; line-height: 1.5;
    transition: border-color 0.2s; min-height: 46px;
  }
  .tp-textarea:focus { border-color: rgba(99,102,241,0.45); }
  .tp-textarea::placeholder { color: rgba(255,255,255,0.2); }

  .tp-send {
    width: 46px; height: 46px; border-radius: 14px; border: none; cursor: pointer;
    background: linear-gradient(135deg, #6366f1, #14b8a6);
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; transition: transform 0.15s, opacity 0.15s;
    box-shadow: 0 0 16px rgba(99,102,241,0.3);
  }
  .tp-send:hover { transform: scale(1.07); }
  .tp-send:active { transform: scale(0.93); }
  .tp-send:disabled { opacity: 0.35; cursor: not-allowed; transform: none; box-shadow: none; }

  .tp-footer-text {
    text-align: center; margin-top: 8px;
    font-size: 10px; color: rgba(255,255,255,0.12); letter-spacing: 0.4px;
  }
`;

function TypingIndicator() {
  return (
    <div className="tp-typing">
      <span /><span /><span />
    </div>
  );
}

function Message({ role, content, isTyping }) {
  const isUser = role === "user";
  return (
    <div className={`tp-msg${isUser ? " user" : ""}`}>
      <div className={`tp-avatar${isUser ? " user-av" : ""}`}>
        {isUser ? "G" : "AI"}
      </div>
      <div className="tp-bubble">
        {isTyping ? <TypingIndicator /> : content}
      </div>
    </div>
  );
}

export default function TechPI() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [endpoint, setEndpoint] = useState("http://localhost:8000/chat");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("ready");
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const statusClass = status === "error" ? "error" : status === "thinking..." ? "thinking" : "";

  async function send() {
    if (loading || !input.trim()) return;
    if (!endpoint.trim()) { setError("Isi endpoint dulu ya."); return; }

    const userText = input.trim();
    const newMsgs = [...messages, { role: "user", content: userText }];
    setMessages(newMsgs);
    setInput("");
    setError("");
    setLoading(true);
    setStatus("thinking...");

    if (textareaRef.current) textareaRef.current.style.height = "auto";

    try {
      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: newMsgs }),
      });

      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();

      const reply =
        data.reply ||
        data.response ||
        data.message ||
        data.content ||
        data.choices?.[0]?.message?.content ||
        JSON.stringify(data);

      setMessages([...newMsgs, { role: "assistant", content: reply }]);
      setStatus("ready");
    } catch (e) {
      setError("Gagal konek: " + e.message);
      setStatus("error");
    }

    setLoading(false);
    textareaRef.current?.focus();
  }

  function handleKey(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }

  function handleTextarea(e) {
    setInput(e.target.value);
    e.target.style.height = "auto";
    e.target.style.height = Math.min(e.target.scrollHeight, 140) + "px";
  }

  return (
    <>
      <style>{styles}</style>
      <div className="tp-root">
        <div className="tp-bg-orb1" />
        <div className="tp-bg-orb2" />

        <header className="tp-header">
          <div className="tp-logo-group">
            <div className="tp-logo-icon">TP</div>
            <div className="tp-logo-text">
              <span className="tp-logo-name">TechPI</span>
              <span className="tp-logo-by">by Glendon</span>
            </div>
          </div>
          <div className={`tp-status-pill ${statusClass}`}>
            <div className="tp-status-dot" />
            <span className="tp-status-text">{status}</span>
          </div>
        </header>

        <div className="tp-messages">
          {messages.length === 0 && !loading && (
            <div className="tp-empty">
              <div className="tp-empty-icon">
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="rgba(99,102,241,0.85)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 2L2 7l10 5 10-5-10-5z" />
                  <path d="M2 17l10 5 10-5" />
                  <path d="M2 12l10 5 10-5" />
                </svg>
              </div>
              <div className="tp-empty-title">Halo! Gw TechPI</div>
              <div className="tp-empty-sub">TechPI dibuat oleh Glendon</div>
            </div>
          )}

          {messages.map((m, i) => (
            <Message key={i} role={m.role} content={m.content} />
          ))}

          {loading && (
            <Message role="assistant" isTyping />
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="tp-bottom">
          <div className="tp-config-row">
            <span className="tp-config-label">ENDPOINT</span>
            <input
              className="tp-api-input"
              value={endpoint}
              onChange={e => setEndpoint(e.target.value)}
              placeholder="http://localhost:5000/chat"
            />
          </div>

          {error && <div className="tp-err">{error}</div>}

          <div className="tp-input-row">
            <textarea
              ref={textareaRef}
              className="tp-textarea"
              rows={1}
              value={input}
              onChange={handleTextarea}
              onKeyDown={handleKey}
              placeholder="Ketik pesan..."
            />
            <button
              className="tp-send"
              onClick={send}
              disabled={loading || !input.trim()}
              aria-label="Kirim"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            </button>
          </div>

          <div className="tp-footer-text">TechPI · by Glendon</div>
        </div>
      </div>
    </>
  );
}
