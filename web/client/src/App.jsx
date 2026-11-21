import React, { useState, useEffect, useRef } from 'react';

const API_BASE = 'http://localhost:5001';

// Custom lightweight SVG icons following Claude's understated stroke design
const Icons = {
  Asterisk: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
      <path d="M12 2v20M2 12h20M4.93 4.93l14.14 14.14M4.93 19.07L19.07 4.93" />
    </svg>
  ),
  Chat: () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" />
    </svg>
  ),
  Speech: () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
    </svg>
  ),
  Pulse: () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
    </svg>
  ),
  Audio: () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
      <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
      <path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
    </svg>
  ),
  Sparkle: () => (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z" />
    </svg>
  ),
  Play: () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
      <polygon points="5 3 19 12 5 21 5 3" />
    </svg>
  ),
  Sliders: () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
      <line x1="4" y1="21" x2="4" y2="14" />
      <line x1="4" y1="10" x2="4" y2="3" />
      <line x1="12" y1="21" x2="12" y2="12" />
      <line x1="12" y1="8" x2="12" y2="3" />
      <line x1="20" y1="21" x2="20" y2="16" />
      <line x1="20" y1="12" x2="20" y2="3" />
      <line x1="1" y1="14" x2="7" y2="14" />
      <line x1="9" y1="8" x2="15" y2="8" />
      <line x1="17" y1="16" x2="23" y2="16" />
    </svg>
  ),
  Check: () => (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  ),
  ArrowUp: () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="12" y1="19" x2="12" y2="5" />
      <polyline points="5 12 12 5 19 12" />
    </svg>
  ),
  Database: () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
      <ellipse cx="12" cy="5" rx="9" ry="3" />
      <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
      <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
    </svg>
  ),
};

// Simple Markdown formatting helper for assistant text
function FormattedContent({ text }) {
  if (!text) return null;
  const lines = text.split('\n');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', lineHeight: '1.65' }}>
      {lines.map((line, idx) => {
        const trimmed = line.trim();
        if (!trimmed) {
          return <div key={idx} style={{ height: '4px' }} />;
        }
        if (trimmed.startsWith('### ')) {
          return (
            <h4
              key={idx}
              style={{
                fontFamily: 'var(--font-serif)',
                fontSize: '15px',
                fontWeight: '600',
                color: 'var(--text-primary)',
                marginTop: '10px',
                marginBottom: '4px',
              }}
            >
              {trimmed.replace('### ', '')}
            </h4>
          );
        }
        if (trimmed.startsWith('## ')) {
          return (
            <h3
              key={idx}
              style={{
                fontFamily: 'var(--font-serif)',
                fontSize: '17px',
                fontWeight: '600',
                color: 'var(--text-primary)',
                marginTop: '14px',
                marginBottom: '6px',
              }}
            >
              {trimmed.replace('## ', '')}
            </h3>
          );
        }
        if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
          const itemText = trimmed.substring(2);
          return (
            <div key={idx} style={{ display: 'flex', gap: '8px', alignItems: 'baseline', marginLeft: '6px' }}>
              <span style={{ color: 'var(--clay)', fontSize: '14px', lineHeight: '1' }}>•</span>
              <span style={{ fontSize: '13.5px', color: 'var(--text-primary)' }}>
                {renderBold(itemText)}
              </span>
            </div>
          );
        }
        if (/^\d+\.\s/.test(trimmed)) {
          const num = trimmed.match(/^(\d+\.)\s/)[1];
          const itemText = trimmed.replace(/^(\d+\.)\s/, '');
          return (
            <div key={idx} style={{ display: 'flex', gap: '8px', alignItems: 'baseline', marginLeft: '6px' }}>
              <span style={{ fontSize: '12px', fontWeight: '600', color: 'var(--text-secondary)' }}>{num}</span>
              <span style={{ fontSize: '13.5px', color: 'var(--text-primary)' }}>
                {renderBold(itemText)}
              </span>
            </div>
          );
        }
        return (
          <p key={idx} style={{ fontSize: '13.5px', color: 'var(--text-primary)', margin: 0 }}>
            {renderBold(line)}
          </p>
        );
      })}
    </div>
  );
}

function renderBold(str) {
  const parts = str.split(/(\*\*.*?\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return (
        <strong key={i} style={{ fontWeight: '600', color: 'var(--text-primary)' }}>
          {part.slice(2, -2)}
        </strong>
      );
    }
    return part;
  });
}

export default function App() {
  // Navigation: primary tabs are 'chat' (Conversational on dataset) and 'trigger_voice' (Trigger Voice Generator)
  const [activeTab, setActiveTab] = useState('chat'); // 'chat' | 'trigger_voice' | 'telemetry' | 'decision' | 'clips'
  const [status, setStatus] = useState(null);
  const [locations, setLocations] = useState([]);
  const [selectedLoc, setSelectedLoc] = useState('Vijay Nagar Scheme-78, Indore - Glenmark');

  // ==========================================
  // TAB 1: CONVERSATIONAL AQI MODEL STATE
  // ==========================================
  const [chatModel, setChatModel] = useState('deepseek/deepseek-chat');
  const [chatInput, setChatInput] = useState('');
  const [isChatting, setIsChatting] = useState(false);
  const [chatMessages, setChatMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      content: `Welcome to **AirCue Conversational Intelligence**. 

I am specifically trained and grounded over the comprehensive **Madhya Pradesh Air Quality Telemetry Dataset** (217,370 observations across 87 monitoring stations in all 55 districts) and the Indian **Central Pollution Control Board (CPCB)** school safety framework.

You can ask me to:
- Compare air quality between specific MP localities (e.g., *Vijay Nagar* vs *Chhoti Gwaltoli* in Indore).
- Retrieve empirical trends for Indore, Jabalpur, Gwalior, Bhopal, Ujjain, Satna, or Singrauli.
- Explain outdoor physical training and morning assembly protocols for schools under different AQI brackets.
- Review historical peak pollution episodes and particulate matter (PM2.5 / PM10) distributions.`,
      timestamp: 'Ready',
      grounding_summary: null,
      matched_locations: [],
    },
  ]);
  const chatScrollRef = useRef(null);

  // ==========================================
  // TAB 2: TRIGGER VOICE GENERATOR STATE
  // ==========================================
  const [triggerModel, setTriggerModel] = useState('deepseek/deepseek-chat');
  const [language, setLanguage] = useState('hi');
  const [alertLevel, setAlertLevel] = useState(2);
  const [aqiInput, setAqiInput] = useState(245);
  const [pm25Input, setPm25Input] = useState(115.0);
  const [slot, setSlot] = useState('Sports PT');
  const [triggerKind, setTriggerKind] = useState('escalate');
  const [temperature, setTemperature] = useState(0.7);
  const [isGeneratingVoice, setIsGeneratingVoice] = useState(false);

  const [voiceHistory, setVoiceHistory] = useState([
    {
      id: 'voice-init',
      sender: 'assistant',
      text: 'वायु गुणवत्ता खराब श्रेणी में है। कृपया खेल का अभ्यास तुरंत इनडोर हॉल में स्थानांतरित करें।',
      rawText: 'वायु गुणवत्ता खराब श्रेणी में है। कृपया खेल का अभ्यास तुरंत इनडोर हॉल में स्थानांतरित करें।',
      facts: {
        category: 'Poor',
        level: 2,
        aqi: 245,
        pm25: 115.0,
        activity_slot: 'Sports PT',
        language: 'hi',
        site: 'Vijay Nagar Scheme-78, Indore - Glenmark',
      },
      validation: {
        passed: true,
        rules: {
          word_count: true,
          sentence_count: true,
          single_action: true,
          no_indoor_ventilation: true,
          consistent_facts: true,
          no_scary_medical: true,
          language_match: true,
        },
        failures: [],
      },
      model: 'deepseek/deepseek-chat',
      latency: 1.84,
      timestamp: 'Demo',
      audioBase64: null,
    },
  ]);
  const voiceScrollRef = useRef(null);

  // ==========================================
  // TELEMETRY & DECISION STATE
  // ==========================================
  const [telemetry, setTelemetry] = useState(null);
  const [loadingTelemetry, setLoadingTelemetry] = useState(false);

  const [decisionModel, setDecisionModel] = useState('deepseek/deepseek-chat');
  const [decisionResult, setDecisionResult] = useState(null);
  const [isEvaluatingDecision, setIsEvaluatingDecision] = useState(false);

  // Pregenerated Clips state
  const [clipKind, setClipKind] = useState('escalate');
  const [clipLevel, setClipLevel] = useState(2);
  const [clipLang, setClipLang] = useState('hi');
  const [clipSlot, setClipSlot] = useState('sports_pt');
  const [clipData, setClipData] = useState(null);

  // Audio Playback state
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [playingClipId, setPlayingClipId] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/status`)
      .then((r) => r.json())
      .then((d) => setStatus(d))
      .catch((err) => console.error('Status fetch error:', err));

    fetch(`${API_BASE}/api/locations`)
      .then((r) => r.json())
      .then((d) => {
        if (d.locations) setLocations(d.locations);
      })
      .catch((err) => console.error('Locations fetch error:', err));
  }, []);

  useEffect(() => {
    if (!selectedLoc) return;
    setLoadingTelemetry(true);
    fetch(`${API_BASE}/api/telemetry?location=${encodeURIComponent(selectedLoc)}&limit=60`)
      .then((r) => r.json())
      .then((d) => {
        setTelemetry(d);
        setLoadingTelemetry(false);
      })
      .catch(() => setLoadingTelemetry(false));
  }, [selectedLoc]);

  useEffect(() => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
    }
  }, [chatMessages, isChatting]);

  useEffect(() => {
    if (voiceScrollRef.current) {
      voiceScrollRef.current.scrollTop = voiceScrollRef.current.scrollHeight;
    }
  }, [voiceHistory, isGeneratingVoice]);

  // Synchronize telemetry readings to trigger inputs
  const handleSyncStationData = () => {
    if (!telemetry || !telemetry.records || telemetry.records.length === 0) return;
    const latest = telemetry.records[telemetry.records.length - 1];
    if (latest.cpcb_aqi != null) {
      setAqiInput(Math.round(latest.cpcb_aqi));
      if (latest.cpcb_aqi <= 50) setAlertLevel(0);
      else if (latest.cpcb_aqi <= 100) setAlertLevel(1);
      else if (latest.cpcb_aqi <= 200) setAlertLevel(1);
      else if (latest.cpcb_aqi <= 300) setAlertLevel(2);
      else if (latest.cpcb_aqi <= 400) setAlertLevel(3);
      else setAlertLevel(4);
    }
    if (latest.pm2_5 != null) {
      setPm25Input(Math.round(latest.pm2_5 * 10) / 10);
    }
  };

  // ------------------------------------------
  // TAB 1: SEND CONVERSATIONAL MESSAGE
  // ------------------------------------------
  const handleSendChat = async (promptOverride = null) => {
    const textToSend = (promptOverride || chatInput).trim();
    if (!textToSend || isChatting) return;

    const userMsg = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    const updatedMessages = [...chatMessages, userMsg];
    setChatMessages(updatedMessages);
    if (!promptOverride) setChatInput('');
    setIsChatting(true);

    try {
      // Build conversation payload for backend
      const payloadMessages = updatedMessages
        .filter((m) => m.role === 'user' || m.role === 'assistant')
        .map((m) => ({ role: m.role, content: m.content }));

      const res = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: payloadMessages,
          model: chatModel,
          temperature: 0.5,
        }),
      });

      const data = await res.json();

      if (data.error) {
        setChatMessages((prev) => [
          ...prev,
          {
            id: `err-${Date.now()}`,
            role: 'assistant',
            isError: true,
            content: `Error from OpenRouter: ${data.error}`,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          },
        ]);
      } else {
        setChatMessages((prev) => [
          ...prev,
          {
            id: `asst-${Date.now()}`,
            role: 'assistant',
            content: data.reply,
            model: data.model,
            latency_s: data.latency_s,
            grounding_summary: data.grounding_summary,
            matched_locations: data.matched_locations,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          },
        ]);
      }
    } catch (err) {
      setChatMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          role: 'assistant',
          isError: true,
          content: `Communication failure: ${err.message}`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } finally {
      setIsChatting(false);
    }
  };

  // ------------------------------------------
  // TAB 2: GENERATE TRIGGER-BASED VOICE ALERT
  // ------------------------------------------
  const handleGenerateVoice = async () => {
    setIsGeneratingVoice(true);

    try {
      const res = await fetch(`${API_BASE}/api/llm/announcement`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: triggerModel,
          level: alertLevel,
          aqi: aqiInput,
          pm25: pm25Input,
          slot,
          language,
          temperature,
          site: selectedLoc,
        }),
      });
      const data = await res.json();

      if (data.error) {
        setVoiceHistory((prev) => [
          ...prev,
          {
            id: `err-${Date.now()}`,
            sender: 'assistant',
            isError: true,
            text: `OpenRouter error: ${data.error}`,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          },
        ]);
      } else {
        setVoiceHistory((prev) => [
          ...prev,
          {
            id: `voice-${Date.now()}`,
            sender: 'assistant',
            text: data.clean_text,
            rawText: data.raw_text,
            audioBase64: data.audio_base64,
            validation: data.validation,
            facts: data.facts,
            model: data.model,
            latency: data.latency_s,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          },
        ]);
      }
    } catch (err) {
      setVoiceHistory((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          sender: 'assistant',
          isError: true,
          text: `Request failed: ${err.message}`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } finally {
      setIsGeneratingVoice(false);
    }
  };

  // Play audio in-browser using Web Speech API or Base64 audio buffer
  const playSpeech = (text, lang, audioBase64 = null) => {
    if (audioBase64) {
      try {
        const audio = new Audio(`data:audio/mp3;base64,${audioBase64}`);
        setIsPlayingAudio(true);
        audio.onended = () => setIsPlayingAudio(false);
        audio.onerror = () => {
          fallbackSpeech(text, lang);
        };
        audio.play();
        return;
      } catch (e) {
        // Fallback to Web Speech API
      }
    }
    fallbackSpeech(text, lang);
  };

  const fallbackSpeech = (text, lang) => {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang === 'hi' ? 'hi-IN' : 'en-IN';
    utterance.rate = 0.95;
    utterance.onstart = () => setIsPlayingAudio(true);
    utterance.onend = () => setIsPlayingAudio(false);
    utterance.onerror = () => setIsPlayingAudio(false);
    window.speechSynthesis.speak(utterance);
  };

  const handleRunDecision = async () => {
    setIsEvaluatingDecision(true);
    setDecisionResult(null);
    try {
      const trajectory = [
        { timestamp: '08:00', pm2_5: 42.0, cpcb_aqi: 95 },
        { timestamp: '09:00', pm2_5: 68.0, cpcb_aqi: 145 },
        { timestamp: '10:00', pm2_5: 98.0, cpcb_aqi: 215 },
        { timestamp: '11:00', pm2_5: 118.0, cpcb_aqi: 255 },
        { timestamp: '12:00', pm2_5: 135.0, cpcb_aqi: 285 },
      ];
      const res = await fetch(`${API_BASE}/api/llm/decision`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: decisionModel,
          history: trajectory,
          current_state: { level: 0, minutes_since_last: 180 },
        }),
      });
      const data = await res.json();
      setDecisionResult(data);
    } catch (err) {
      setDecisionResult({ error: err.message });
    } finally {
      setIsEvaluatingDecision(false);
    }
  };

  const handleResolveClip = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/clips/preview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          level: clipLevel,
          kind: clipKind,
          language: clipLang,
          slot: clipSlot,
          aqi: aqiInput,
        }),
      });
      const data = await res.json();
      setClipData(data);
    } catch (err) {
      console.error(err);
    }
  };

  const playWav = (url, clipId) => {
    const audio = new Audio(url);
    setPlayingClipId(clipId);
    audio.onended = () => setPlayingClipId(null);
    audio.onerror = () => setPlayingClipId(null);
    audio.play();
  };

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden', backgroundColor: 'var(--bg-app)' }}>
      {/* ======================================================== */}
      {/* LEFT NAVIGATION SIDEBAR (Warm Claude-Style Minimalist) */}
      {/* ======================================================== */}
      <aside
        style={{
          width: '260px',
          backgroundColor: 'var(--bg-sidebar)',
          borderRight: '1px solid var(--border)',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          flexShrink: 0,
        }}
      >
        <div style={{ padding: '20px 16px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Logo & Product Heading */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div
              style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                backgroundColor: 'var(--clay-subtle)',
                color: 'var(--clay)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                border: '1px solid var(--clay-border)',
              }}
            >
              <Icons.Asterisk />
            </div>
            <div>
              <div style={{ fontFamily: 'var(--font-serif)', fontSize: '18px', fontWeight: '600', color: 'var(--text-primary)', lineHeight: '1.2' }}>
                AirCue
              </div>
              <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', letterSpacing: '0.02em' }}>
                Madhya Pradesh AQI & Voice
              </div>
            </div>
          </div>

          {/* Primary Navigation Section: Two Core Tabs */}
          <div>
            <div style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-tertiary)', marginBottom: '8px', paddingLeft: '8px', fontWeight: '600' }}>
              Core Models
            </div>
            <nav style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              {[
                { id: 'chat', label: 'AQI Dataset Intelligence', subtitle: 'Conversational LLM', icon: Icons.Chat },
                { id: 'trigger_voice', label: 'Trigger Voice Messages', subtitle: 'PA Alert Generator', icon: Icons.Speech },
              ].map((item) => {
                const Icon = item.icon;
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                      padding: '10px 12px',
                      borderRadius: '8px',
                      textAlign: 'left',
                      width: '100%',
                      backgroundColor: isActive ? 'var(--clay-subtle)' : 'transparent',
                      border: isActive ? '1px solid var(--clay-border)' : '1px solid transparent',
                    }}
                  >
                    <div style={{ color: isActive ? 'var(--clay)' : 'var(--text-secondary)' }}>
                      <Icon />
                    </div>
                    <div>
                      <div style={{ fontSize: '13px', fontWeight: isActive ? '600' : '500', color: isActive ? 'var(--clay)' : 'var(--text-primary)' }}>
                        {item.label}
                      </div>
                      <div style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>
                        {item.subtitle}
                      </div>
                    </div>
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Secondary Utilities */}
          <div>
            <div style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-tertiary)', marginBottom: '8px', paddingLeft: '8px', fontWeight: '600' }}>
              Operational Telemetry
            </div>
            <nav style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              {[
                { id: 'telemetry', label: 'Station Telemetry', icon: Icons.Pulse },
                { id: 'decision', label: 'Decision Reasoner', icon: Icons.Sliders },
                { id: 'clips', label: 'Pregenerated Clips', icon: Icons.Audio },
              ].map((item) => {
                const Icon = item.icon;
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '10px',
                      padding: '8px 12px',
                      borderRadius: '6px',
                      fontSize: '13px',
                      fontWeight: isActive ? '600' : '400',
                      color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
                      backgroundColor: isActive ? 'var(--bg-hover)' : 'transparent',
                      textAlign: 'left',
                      width: '100%',
                    }}
                  >
                    <Icon />
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>
        </div>

        {/* Footer info in sidebar */}
        <div style={{ padding: '16px', borderTop: '1px solid var(--border)', fontSize: '11px', color: 'var(--text-tertiary)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
            <span
              style={{
                width: '7px',
                height: '7px',
                borderRadius: '50%',
                backgroundColor: status?.has_openrouter_key ? 'var(--olive)' : 'var(--crimson)',
              }}
            />
            <span style={{ fontWeight: '500', color: 'var(--text-secondary)' }}>
              {status?.has_openrouter_key ? 'OpenRouter Connected' : 'No API Key'}
            </span>
          </div>
          <div>Grounded on 87 MP stations</div>
          <div style={{ marginTop: '2px' }}>B.Tech Major Project • PIEMR</div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
        {/* Top Header with Primary Two Tabs */}
        <header
          style={{
            height: '56px',
            borderBottom: '1px solid var(--border)',
            padding: '0 28px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            backgroundColor: 'var(--bg-surface)',
            flexShrink: 0,
          }}
        >
          {/* Top Primary Tab Switcher */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <button
              onClick={() => setActiveTab('chat')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '6px 14px',
                borderRadius: '6px',
                fontSize: '13px',
                fontWeight: activeTab === 'chat' ? '600' : '500',
                color: activeTab === 'chat' ? 'var(--clay)' : 'var(--text-secondary)',
                backgroundColor: activeTab === 'chat' ? 'var(--clay-subtle)' : 'transparent',
                border: activeTab === 'chat' ? '1px solid var(--clay-border)' : '1px solid transparent',
              }}
            >
              <Icons.Chat />
              <span>AQI Dataset Conversational Model</span>
            </button>

            <button
              onClick={() => setActiveTab('trigger_voice')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '6px 14px',
                borderRadius: '6px',
                fontSize: '13px',
                fontWeight: activeTab === 'trigger_voice' ? '600' : '500',
                color: activeTab === 'trigger_voice' ? 'var(--clay)' : 'var(--text-secondary)',
                backgroundColor: activeTab === 'trigger_voice' ? 'var(--clay-subtle)' : 'transparent',
                border: activeTab === 'trigger_voice' ? '1px solid var(--clay-border)' : '1px solid transparent',
              }}
            >
              <Icons.Speech />
              <span>Trigger-Based Voice Messages</span>
            </button>
          </div>

          {/* Right Header Status Badges */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: 'var(--text-secondary)' }}>
              <Icons.Database />
              <span>217,370 records</span>
            </div>
            <div
              style={{
                fontSize: '11px',
                padding: '3px 8px',
                borderRadius: '12px',
                backgroundColor: 'var(--bg-subtle)',
                color: 'var(--text-secondary)',
                border: '1px solid var(--border)',
              }}
            >
              CPCB MP Telemetry
            </div>
          </div>
        </header>

        {/* ======================================================== */}
        {/* TAB 1: CONVERSATIONAL MODEL (AQI DATASET GROUNDED) */}
        {/* ======================================================== */}
        {activeTab === 'chat' && (
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: 'calc(100% - 56px)', overflow: 'hidden' }}>
            {/* Conversation Messages Scroll Area */}
            <div
              ref={chatScrollRef}
              style={{
                flex: 1,
                overflowY: 'auto',
                padding: '32px 15% 20px 15%',
                display: 'flex',
                flexDirection: 'column',
                gap: '24px',
              }}
            >
              {chatMessages.map((msg) => (
                <div
                  key={msg.id}
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start',
                    width: '100%',
                  }}
                >
                  {msg.role === 'user' ? (
                    <div
                      style={{
                        maxWidth: '80%',
                        backgroundColor: 'var(--bg-subtle)',
                        border: '1px solid var(--border)',
                        borderRadius: '16px 16px 4px 16px',
                        padding: '12px 18px',
                        fontSize: '13.5px',
                        lineHeight: '1.55',
                        color: 'var(--text-primary)',
                      }}
                    >
                      {msg.content}
                    </div>
                  ) : (
                    <div style={{ maxWidth: '90%', display: 'flex', gap: '14px', alignItems: 'flex-start' }}>
                      <div
                        style={{
                          width: '28px',
                          height: '28px',
                          borderRadius: '6px',
                          backgroundColor: 'var(--clay-subtle)',
                          border: '1px solid var(--clay-border)',
                          color: 'var(--clay)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          flexShrink: 0,
                          marginTop: '2px',
                        }}
                      >
                        <Icons.Asterisk />
                      </div>
                      <div style={{ flex: 1 }}>
                        <div
                          style={{
                            backgroundColor: 'var(--bg-surface)',
                            border: '1px solid var(--border)',
                            borderRadius: '4px 16px 16px 16px',
                            padding: '18px 22px',
                            boxShadow: '0 1px 3px rgba(0,0,0,0.03)',
                          }}
                        >
                          <FormattedContent text={msg.content} />

                          {/* Grounding Telemetry summary pill if available */}
                          {msg.grounding_summary && msg.grounding_summary.length > 0 && (
                            <div
                              style={{
                                marginTop: '16px',
                                paddingTop: '12px',
                                borderTop: '1px solid var(--border-light)',
                                display: 'flex',
                                flexWrap: 'wrap',
                                gap: '8px',
                                alignItems: 'center',
                              }}
                            >
                              <span style={{ fontSize: '11px', color: 'var(--text-tertiary)', fontWeight: '600' }}>
                                Verified Telemetry Grounding:
                              </span>
                              {msg.grounding_summary.map((g, i) => (
                                <span
                                  key={i}
                                  style={{
                                    fontSize: '11px',
                                    padding: '2px 8px',
                                    borderRadius: '10px',
                                    backgroundColor: 'var(--bg-subtle)',
                                    border: '1px solid var(--border)',
                                    color: 'var(--text-secondary)',
                                  }}
                                >
                                  <strong>{g.location}</strong>: Mean AQI {g.mean_aqi} (Max {g.max_aqi})
                                </span>
                              ))}
                            </div>
                          )}
                        </div>

                        {/* Message Metadata */}
                        <div style={{ display: 'flex', gap: '12px', marginTop: '6px', fontSize: '11px', color: 'var(--text-tertiary)', paddingLeft: '4px' }}>
                          <span>{msg.timestamp}</span>
                          {msg.model && <span>• {msg.model.split('/')[1] || msg.model}</span>}
                          {msg.latency_s && <span>• {msg.latency_s}s</span>}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}

              {isChatting && (
                <div style={{ display: 'flex', gap: '14px', alignItems: 'center', paddingLeft: '4px' }}>
                  <div
                    style={{
                      width: '28px',
                      height: '28px',
                      borderRadius: '6px',
                      backgroundColor: 'var(--clay-subtle)',
                      border: '1px solid var(--clay-border)',
                      color: 'var(--clay)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Icons.Asterisk />
                  </div>
                  <div style={{ fontSize: '13px', color: 'var(--text-secondary)', fontStyle: 'italic' }}>
                    Consulting Madhya Pradesh telemetry dataset and CPCB guidelines...
                  </div>
                </div>
              )}
            </div>

            {/* Quick Prompt Suggestions */}
            {chatMessages.length <= 2 && (
              <div style={{ padding: '0 15% 12px 15%', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {[
                  'Compare Vijay Nagar and Chhoti Gwaltoli in Indore',
                  'Which MP districts have recorded the highest AQI levels?',
                  'What outdoor sports guidelines apply during Poor AQI?',
                  'Summarize PM2.5 and PM10 trends for Jabalpur and Gwalior',
                ].map((prompt, i) => (
                  <button
                    key={i}
                    onClick={() => handleSendChat(prompt)}
                    style={{
                      padding: '6px 12px',
                      borderRadius: '16px',
                      backgroundColor: 'var(--bg-surface)',
                      border: '1px solid var(--border)',
                      fontSize: '12px',
                      color: 'var(--text-secondary)',
                      cursor: 'pointer',
                    }}
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            )}

            {/* Bottom Claude-Style Conversational Input Box */}
            <div style={{ padding: '0 15% 24px 15%', backgroundColor: 'transparent' }}>
              <div
                style={{
                  backgroundColor: 'var(--bg-surface)',
                  border: '1px solid var(--border)',
                  borderRadius: '12px',
                  padding: '12px 16px',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '8px',
                }}
              >
                <textarea
                  rows={2}
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSendChat();
                    }
                  }}
                  placeholder="Ask anything about Madhya Pradesh air quality, localities, CPCB rules, or school outdoor protocols..."
                  style={{
                    width: '100%',
                    border: 'none',
                    resize: 'none',
                    padding: 0,
                    fontSize: '14px',
                    lineHeight: '1.5',
                    backgroundColor: 'transparent',
                    boxShadow: 'none',
                  }}
                />

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: '6px', borderTop: '1px solid var(--border-light)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>Model:</span>
                    <select
                      value={chatModel}
                      onChange={(e) => setChatModel(e.target.value)}
                      style={{
                        padding: '3px 8px',
                        fontSize: '11px',
                        borderRadius: '6px',
                        backgroundColor: 'var(--bg-subtle)',
                        border: '1px solid var(--border)',
                      }}
                    >
                      <option value="deepseek/deepseek-chat">DeepSeek Chat</option>
                      <option value="anthropic/claude-3.5-haiku">Claude 3.5 Haiku</option>
                      <option value="openai/gpt-4o-mini">GPT-4o Mini</option>
                      <option value="google/gemini-2.0-flash-001">Gemini 2.0 Flash</option>
                    </select>

                    <button
                      onClick={() =>
                        setChatMessages([
                          {
                            id: 'reset',
                            role: 'assistant',
                            content: 'Conversation cleared. How can I assist you with Madhya Pradesh air quality data?',
                            timestamp: 'Just now',
                          },
                        ])
                      }
                      style={{ fontSize: '11px', color: 'var(--text-tertiary)', marginLeft: '8px' }}
                    >
                      Clear chat
                    </button>
                  </div>

                  <button
                    onClick={() => handleSendChat()}
                    disabled={isChatting || !chatInput.trim()}
                    style={{
                      width: '32px',
                      height: '32px',
                      borderRadius: '8px',
                      backgroundColor: isChatting || !chatInput.trim() ? 'var(--bg-subtle)' : 'var(--clay)',
                      color: isChatting || !chatInput.trim() ? 'var(--text-muted)' : '#FFFFFF',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      cursor: isChatting || !chatInput.trim() ? 'not-allowed' : 'pointer',
                    }}
                  >
                    <Icons.ArrowUp />
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ======================================================== */}
        {/* TAB 2: TRIGGER-BASED VOICE MESSAGE GENERATOR */}
        {/* ======================================================== */}
        {activeTab === 'trigger_voice' && (
          <div style={{ flex: 1, display: 'flex', height: 'calc(100% - 56px)', overflow: 'hidden' }}>
            {/* Left / Middle: Generated Announcements Feed */}
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', borderRight: '1px solid var(--border)' }}>
              {/* Voice Subheader */}
              <div
                style={{
                  height: '48px',
                  borderBottom: '1px solid var(--border)',
                  padding: '0 28px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  backgroundColor: 'var(--bg-surface)',
                  flexShrink: 0,
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <span style={{ fontFamily: 'var(--font-serif)', fontSize: '15px', color: 'var(--text-primary)' }}>
                    Trigger-Generated Spoken Announcements
                  </span>
                  <span
                    style={{
                      fontSize: '11px',
                      padding: '2px 8px',
                      borderRadius: '12px',
                      backgroundColor: 'var(--bg-subtle)',
                      color: 'var(--text-secondary)',
                      border: '1px solid var(--border)',
                    }}
                  >
                    {triggerModel.split('/')[1] || triggerModel}
                  </span>
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-tertiary)' }}>
                  Language: {language === 'hi' ? 'Hindi' : 'English'}
                </div>
              </div>

              {/* Announcements Feed */}
              <div
                ref={voiceScrollRef}
                style={{
                  flex: 1,
                  overflowY: 'auto',
                  padding: '28px 36px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '24px',
                }}
              >
                {voiceHistory.map((item) => (
                  <div
                    key={item.id}
                    style={{
                      backgroundColor: 'var(--bg-surface)',
                      border: '1px solid var(--border)',
                      borderRadius: '12px',
                      padding: '22px 24px',
                      boxShadow: '0 1px 3px rgba(0,0,0,0.03)',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '16px',
                    }}
                  >
                    {/* Header line of card */}
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span
                          style={{
                            padding: '3px 8px',
                            borderRadius: '4px',
                            fontSize: '11px',
                            fontWeight: '600',
                            backgroundColor:
                              item.facts?.level >= 3 ? 'var(--crimson-subtle)' : item.facts?.level >= 2 ? 'var(--amber-subtle)' : 'var(--olive-subtle)',
                            color:
                              item.facts?.level >= 3 ? 'var(--crimson)' : item.facts?.level >= 2 ? 'var(--amber)' : 'var(--olive)',
                          }}
                        >
                          Level {item.facts?.level ?? alertLevel} • {item.facts?.category ?? 'Air Alert'}
                        </span>
                        <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                          {item.facts?.activity_slot ?? slot}
                        </span>
                      </div>
                      <span style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>{item.timestamp}</span>
                    </div>

                    {/* Announcement Spoken Text */}
                    <div
                      style={{
                        fontFamily: 'var(--font-serif)',
                        fontSize: '18px',
                        lineHeight: '1.45',
                        color: 'var(--text-primary)',
                      }}
                    >
                      "{item.text}"
                    </div>

                    {/* Audio Player Strip */}
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        padding: '10px 14px',
                        borderRadius: '8px',
                        backgroundColor: 'var(--bg-subtle)',
                        border: '1px solid var(--border)',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <button
                          onClick={() => playSpeech(item.text, item.facts?.language || language, item.audioBase64)}
                          style={{
                            width: '32px',
                            height: '32px',
                            borderRadius: '50%',
                            backgroundColor: 'var(--clay)',
                            color: '#FFFFFF',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            cursor: 'pointer',
                          }}
                        >
                          <Icons.Play />
                        </button>
                        <div>
                          <div style={{ fontSize: '12px', fontWeight: '500', color: 'var(--text-primary)' }}>
                            Listen to Spoken PA Announcement
                          </div>
                          <div style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>
                            {item.audioBase64 ? 'Generated audio clip' : 'Browser Web Speech Engine'}
                          </div>
                        </div>
                      </div>

                      {isPlayingAudio && (
                        <span style={{ fontSize: '11px', color: 'var(--clay)', fontWeight: '500' }}>Playing...</span>
                      )}
                    </div>

                    {/* Rule Validation Strip */}
                    {item.validation && (
                      <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
                          <span style={{ color: 'var(--olive)' }}>
                            <Icons.Check />
                          </span>
                          <span style={{ fontWeight: '500' }}>CPCB Outdoor Safety Validation Passed</span>
                        </div>
                        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', color: 'var(--text-tertiary)' }}>
                          <span>Word count: ≤ 20 words</span>
                          <span>•</span>
                          <span>Single outdoor action</span>
                          <span>•</span>
                          <span>No indoor ventilation advice</span>
                          <span>•</span>
                          <span>No medical panic</span>
                        </div>
                      </div>
                    )}
                  </div>
                ))}

                {isGeneratingVoice && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '16px 20px', backgroundColor: 'var(--bg-surface)', borderRadius: '8px', border: '1px solid var(--border)' }}>
                    <div style={{ color: 'var(--clay)' }}>
                      <Icons.Asterisk />
                    </div>
                    <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                      Synthesizing authoritative spoken voice alert for outdoor PA system...
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Right Pane: Trigger Controls */}
            <div
              style={{
                width: '340px',
                backgroundColor: 'var(--bg-sidebar)',
                padding: '24px 20px',
                display: 'flex',
                flexDirection: 'column',
                gap: '20px',
                overflowY: 'auto',
                flexShrink: 0,
              }}
            >
              <div>
                <h3 style={{ fontFamily: 'var(--font-serif)', fontSize: '17px', marginBottom: '4px' }}>
                  Trigger Parameters
                </h3>
                <p style={{ fontSize: '12px', color: 'var(--text-tertiary)', lineHeight: '1.4' }}>
                  Configure incoming telemetry triggers and campus state to generate outdoor announcements.
                </p>
              </div>

              {/* Severity Level Selector */}
              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: '500', marginBottom: '6px' }}>
                  Trigger Severity Level: {alertLevel}
                </label>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '4px' }}>
                  {[
                    { lvl: 0, label: 'Good' },
                    { lvl: 1, label: 'Mod' },
                    { lvl: 2, label: 'Poor' },
                    { lvl: 3, label: 'V.Poor' },
                    { lvl: 4, label: 'Severe' },
                  ].map((item) => (
                    <button
                      key={item.lvl}
                      onClick={() => {
                        setAlertLevel(item.lvl);
                        if (item.lvl === 0) { setAqiInput(45); setPm25Input(25); }
                        else if (item.lvl === 1) { setAqiInput(140); setPm25Input(65); }
                        else if (item.lvl === 2) { setAqiInput(245); setPm25Input(115); }
                        else if (item.lvl === 3) { setAqiInput(340); setPm25Input(180); }
                        else if (item.lvl === 4) { setAqiInput(430); setPm25Input(280); }
                      }}
                      style={{
                        padding: '6px 0',
                        fontSize: '11px',
                        fontWeight: alertLevel === item.lvl ? '600' : '400',
                        borderRadius: '4px',
                        backgroundColor: alertLevel === item.lvl ? 'var(--clay)' : 'var(--bg-surface)',
                        color: alertLevel === item.lvl ? '#FFFFFF' : 'var(--text-secondary)',
                        border: '1px solid var(--border)',
                      }}
                    >
                      {item.lvl}: {item.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Station / Campus Location */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <label style={{ fontSize: '12px', fontWeight: '500' }}>Target Campus / Station</label>
                  <button
                    onClick={handleSyncStationData}
                    style={{ fontSize: '11px', color: 'var(--clay)', fontWeight: '500' }}
                  >
                    Sync Live Data
                  </button>
                </div>
                <select
                  value={selectedLoc}
                  onChange={(e) => setSelectedLoc(e.target.value)}
                  style={{ width: '100%', padding: '6px 10px', fontSize: '12px' }}
                >
                  {locations.map((loc, idx) => (
                    <option key={idx} value={loc.name}>
                      {loc.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* AQI & PM2.5 Inputs */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: '500', marginBottom: '4px' }}>
                    CPCB AQI
                  </label>
                  <input
                    type="number"
                    value={aqiInput}
                    onChange={(e) => setAqiInput(Number(e.target.value))}
                    style={{ width: '100%', padding: '6px 8px', fontSize: '13px' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: '500', marginBottom: '4px' }}>
                    PM2.5 (µg/m³)
                  </label>
                  <input
                    type="number"
                    value={pm25Input}
                    onChange={(e) => setPm25Input(Number(e.target.value))}
                    style={{ width: '100%', padding: '6px 8px', fontSize: '13px' }}
                  />
                </div>
              </div>

              {/* Timetable Activity Slot */}
              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: '500', marginBottom: '6px' }}>
                  Timetable Activity Slot
                </label>
                <select
                  value={slot}
                  onChange={(e) => setSlot(e.target.value)}
                  style={{ width: '100%', padding: '6px 10px', fontSize: '12px' }}
                >
                  <option value="Sports PT">Sports & Physical Training</option>
                  <option value="Morning Assembly">Morning School Assembly</option>
                  <option value="Recess & Lunch">Recess & Outdoor Lunch</option>
                  <option value="Class Dispersal">Campus Dispersal</option>
                  <option value="General Outdoor">General Campus</option>
                </select>
              </div>

              {/* Trigger Event Kind */}
              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: '500', marginBottom: '6px' }}>
                  Trigger Event Type
                </label>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px' }}>
                  {[
                    { id: 'escalate', label: 'Escalate' },
                    { id: 'reminder', label: 'Reminder' },
                    { id: 'improving', label: 'Improving' },
                    { id: 'recovered', label: 'Recovered' },
                  ].map((kind) => (
                    <button
                      key={kind.id}
                      onClick={() => setTriggerKind(kind.id)}
                      style={{
                        padding: '6px 8px',
                        fontSize: '11px',
                        borderRadius: '4px',
                        backgroundColor: triggerKind === kind.id ? 'var(--bg-hover)' : 'var(--bg-surface)',
                        color: triggerKind === kind.id ? 'var(--text-primary)' : 'var(--text-secondary)',
                        border: triggerKind === kind.id ? '1px solid var(--border-focus)' : '1px solid var(--border)',
                        fontWeight: triggerKind === kind.id ? '600' : '400',
                      }}
                    >
                      {kind.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Language Selection */}
              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: '500', marginBottom: '6px' }}>
                  Spoken Language
                </label>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                  <button
                    onClick={() => setLanguage('hi')}
                    style={{
                      padding: '8px',
                      borderRadius: '6px',
                      fontSize: '12px',
                      fontWeight: language === 'hi' ? '600' : '400',
                      backgroundColor: language === 'hi' ? 'var(--clay-subtle)' : 'var(--bg-surface)',
                      color: language === 'hi' ? 'var(--clay)' : 'var(--text-secondary)',
                      border: language === 'hi' ? '1px solid var(--clay-border)' : '1px solid var(--border)',
                    }}
                  >
                    हिंदी (Hindi)
                  </button>
                  <button
                    onClick={() => setLanguage('en')}
                    style={{
                      padding: '8px',
                      borderRadius: '6px',
                      fontSize: '12px',
                      fontWeight: language === 'en' ? '600' : '400',
                      backgroundColor: language === 'en' ? 'var(--clay-subtle)' : 'var(--bg-surface)',
                      color: language === 'en' ? 'var(--clay)' : 'var(--text-secondary)',
                      border: language === 'en' ? '1px solid var(--clay-border)' : '1px solid var(--border)',
                    }}
                  >
                    English
                  </button>
                </div>
              </div>

              {/* Model Selection */}
              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: '500', marginBottom: '4px' }}>
                  Underlying LLM
                </label>
                <select
                  value={triggerModel}
                  onChange={(e) => setTriggerModel(e.target.value)}
                  style={{ width: '100%', padding: '6px 10px', fontSize: '12px' }}
                >
                  <option value="deepseek/deepseek-chat">DeepSeek Chat</option>
                  <option value="anthropic/claude-3.5-haiku">Claude 3.5 Haiku</option>
                  <option value="openai/gpt-4o-mini">GPT-4o Mini</option>
                  <option value="google/gemini-2.0-flash-001">Gemini 2.0 Flash</option>
                </select>
              </div>

              {/* Generate Trigger Button */}
              <button
                onClick={handleGenerateVoice}
                disabled={isGeneratingVoice}
                style={{
                  marginTop: 'auto',
                  padding: '12px',
                  borderRadius: '8px',
                  backgroundColor: 'var(--clay)',
                  color: '#FFFFFF',
                  fontWeight: '500',
                  fontSize: '13px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  cursor: isGeneratingVoice ? 'not-allowed' : 'pointer',
                  boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
                }}
              >
                <Icons.Sparkle />
                <span>{isGeneratingVoice ? 'Generating Voice...' : 'Generate Voice Announcement'}</span>
              </button>
            </div>
          </div>
        )}

        {/* ======================================================== */}
        {/* VIEW 3: STATION TELEMETRY (UTILITY VIEW) */}
        {/* ======================================================== */}
        {activeTab === 'telemetry' && (
          <div style={{ flex: 1, overflowY: 'auto', padding: '32px 48px' }}>
            <div style={{ maxWidth: '1000px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: '24px', marginBottom: '4px' }}>
                    Madhya Pradesh Telemetry Stations
                  </h2>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
                    Air quality readings across all 55 districts and urban CPCB monitoring locations.
                  </p>
                </div>

                <div style={{ display: 'flex', gap: '10px' }}>
                  <select
                    value={selectedLoc}
                    onChange={(e) => setSelectedLoc(e.target.value)}
                    style={{ padding: '6px 12px', fontSize: '13px' }}
                  >
                    {locations.map((loc, idx) => (
                      <option key={idx} value={loc.name}>
                        {loc.name} ({loc.provider})
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Summary Stats */}
              {telemetry?.stats && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
                  {[
                    { label: 'Mean CPCB AQI', val: telemetry.stats.mean_aqi ?? 'N/A' },
                    { label: 'Peak AQI Recorded', val: telemetry.stats.max_aqi ?? 'N/A' },
                    { label: 'Mean PM2.5 (µg/m³)', val: telemetry.stats.mean_pm25 ?? 'N/A' },
                    { label: 'Sample Count', val: telemetry.stats.total_rows ?? '0' },
                  ].map((card, i) => (
                    <div
                      key={i}
                      style={{
                        padding: '16px 20px',
                        backgroundColor: 'var(--bg-surface)',
                        border: '1px solid var(--border)',
                        borderRadius: '8px',
                      }}
                    >
                      <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                        {card.label}
                      </div>
                      <div style={{ fontFamily: 'var(--font-serif)', fontSize: '24px', fontWeight: '500', color: 'var(--text-primary)', marginTop: '4px' }}>
                        {card.val}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Telemetry Table */}
              <div
                style={{
                  backgroundColor: 'var(--bg-surface)',
                  border: '1px solid var(--border)',
                  borderRadius: '8px',
                  overflow: 'hidden',
                }}
              >
                <div style={{ padding: '12px 18px', borderBottom: '1px solid var(--border)', fontWeight: '500', fontSize: '13px' }}>
                  Recent Observations for {selectedLoc}
                </div>
                <div style={{ maxHeight: '420px', overflowY: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '12px' }}>
                    <thead>
                      <tr style={{ backgroundColor: 'var(--bg-subtle)', color: 'var(--text-secondary)' }}>
                        <th style={{ padding: '8px 16px', fontWeight: '500' }}>Timestamp</th>
                        <th style={{ padding: '8px 16px', fontWeight: '500' }}>PM2.5 (µg/m³)</th>
                        <th style={{ padding: '8px 16px', fontWeight: '500' }}>PM10 (µg/m³)</th>
                        <th style={{ padding: '8px 16px', fontWeight: '500' }}>CPCB AQI</th>
                        <th style={{ padding: '8px 16px', fontWeight: '500' }}>Category</th>
                      </tr>
                    </thead>
                    <tbody>
                      {telemetry?.records?.slice(-50).reverse().map((r, i) => (
                        <tr key={i} style={{ borderBottom: '1px solid var(--border-light)' }}>
                          <td style={{ padding: '8px 16px', color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)' }}>{r.dt}</td>
                          <td style={{ padding: '8px 16px', fontFamily: 'var(--font-mono)' }}>{r.pm2_5 ?? '—'}</td>
                          <td style={{ padding: '8px 16px', fontFamily: 'var(--font-mono)' }}>{r.pm10 ?? '—'}</td>
                          <td style={{ padding: '8px 16px', fontFamily: 'var(--font-mono)', fontWeight: '500' }}>{r.cpcb_aqi ?? '—'}</td>
                          <td style={{ padding: '8px 16px' }}>
                            <span
                              style={{
                                padding: '2px 8px',
                                borderRadius: '10px',
                                fontSize: '11px',
                                backgroundColor:
                                  r.cpcb_category === 'Poor' || r.cpcb_category === 'Very Poor' || r.cpcb_category === 'Severe'
                                    ? 'var(--amber-subtle)'
                                    : 'var(--olive-subtle)',
                                color:
                                  r.cpcb_category === 'Poor' || r.cpcb_category === 'Very Poor' || r.cpcb_category === 'Severe'
                                    ? 'var(--amber)'
                                    : 'var(--olive)',
                              }}
                            >
                              {r.cpcb_category || 'Unknown'}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ======================================================== */}
        {/* VIEW 4: DECISION REASONER */}
        {/* ======================================================== */}
        {activeTab === 'decision' && (
          <div style={{ flex: 1, overflowY: 'auto', padding: '32px 48px' }}>
            <div style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '24px' }}>
              <div>
                <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: '24px', marginBottom: '4px' }}>
                  Zero-shot Decision Reasoner
                </h2>
                <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
                  Evaluates multi-hour sequential air readings and outputs strict JSON trigger decisions.
                </p>
              </div>

              <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                <select
                  value={decisionModel}
                  onChange={(e) => setDecisionModel(e.target.value)}
                  style={{ padding: '8px 12px', fontSize: '13px' }}
                >
                  <option value="deepseek/deepseek-chat">DeepSeek Chat</option>
                  <option value="anthropic/claude-3.5-haiku">Claude 3.5 Haiku</option>
                  <option value="openai/gpt-4o-mini">GPT-4o Mini</option>
                </select>

                <button
                  onClick={handleRunDecision}
                  disabled={isEvaluatingDecision}
                  style={{
                    padding: '8px 18px',
                    borderRadius: '6px',
                    backgroundColor: 'var(--clay)',
                    color: '#FFFFFF',
                    fontWeight: '500',
                    fontSize: '13px',
                    cursor: isEvaluatingDecision ? 'not-allowed' : 'pointer',
                  }}
                >
                  {isEvaluatingDecision ? 'Evaluating Sequence...' : 'Evaluate 5-Hour Sequence'}
                </button>
              </div>

              {decisionResult && (
                <div
                  style={{
                    backgroundColor: 'var(--bg-surface)',
                    border: '1px solid var(--border)',
                    borderRadius: '8px',
                    padding: '20px 24px',
                  }}
                >
                  <div style={{ fontSize: '12px', color: 'var(--text-tertiary)', marginBottom: '8px' }}>
                    Model Output ({decisionResult.model} • {decisionResult.latency_s}s)
                  </div>
                  <pre
                    style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize: '12px',
                      backgroundColor: 'var(--bg-subtle)',
                      padding: '16px',
                      borderRadius: '6px',
                      overflowX: 'auto',
                    }}
                  >
                    {JSON.stringify(decisionResult.parsed || decisionResult.raw_text, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ======================================================== */}
        {/* VIEW 5: PREGENERATED CLIPS */}
        {/* ======================================================== */}
        {activeTab === 'clips' && (
          <div style={{ flex: 1, overflowY: 'auto', padding: '32px 48px' }}>
            <div style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '24px' }}>
              <div>
                <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: '24px', marginBottom: '4px' }}>
                  Pregenerated Safety Clips
                </h2>
                <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
                  Deterministic offline WAV safety announcements recorded for school bell systems.
                </p>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                    Kind
                  </label>
                  <select
                    value={clipKind}
                    onChange={(e) => setClipKind(e.target.value)}
                    style={{ width: '100%', padding: '6px 8px', fontSize: '12px' }}
                  >
                    <option value="escalate">Escalate</option>
                    <option value="reminder">Reminder</option>
                    <option value="improving">Improving</option>
                    <option value="recovered">Recovered</option>
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                    Level
                  </label>
                  <select
                    value={clipLevel}
                    onChange={(e) => setClipLevel(Number(e.target.value))}
                    style={{ width: '100%', padding: '6px 8px', fontSize: '12px' }}
                  >
                    <option value={1}>1 (Moderate)</option>
                    <option value={2}>2 (Poor)</option>
                    <option value={3}>3 (Very Poor)</option>
                    <option value={4}>4 (Severe)</option>
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                    Language
                  </label>
                  <select
                    value={clipLang}
                    onChange={(e) => setClipLang(e.target.value)}
                    style={{ width: '100%', padding: '6px 8px', fontSize: '12px' }}
                  >
                    <option value="hi">Hindi</option>
                    <option value="en">English</option>
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                    Slot
                  </label>
                  <select
                    value={clipSlot}
                    onChange={(e) => setClipSlot(e.target.value)}
                    style={{ width: '100%', padding: '6px 8px', fontSize: '12px' }}
                  >
                    <option value="sports_pt">Sports PT</option>
                    <option value="assembly">Assembly</option>
                    <option value="recess">Recess</option>
                    <option value="general">General</option>
                  </select>
                </div>
              </div>

              <button
                onClick={handleResolveClip}
                style={{
                  alignSelf: 'flex-start',
                  padding: '8px 18px',
                  borderRadius: '6px',
                  backgroundColor: 'var(--clay)',
                  color: '#FFFFFF',
                  fontWeight: '500',
                  fontSize: '13px',
                }}
              >
                Resolve Clip
              </button>

              {clipData && (
                <div
                  style={{
                    backgroundColor: 'var(--bg-surface)',
                    border: '1px solid var(--border)',
                    borderRadius: '8px',
                    padding: '20px 24px',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '12px',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '13px', fontWeight: '600' }}>
                      {clipData.clip_id}.wav
                    </span>
                    <span
                      style={{
                        padding: '2px 8px',
                        borderRadius: '4px',
                        fontSize: '11px',
                        backgroundColor: clipData.exists ? 'var(--olive-subtle)' : 'var(--amber-subtle)',
                        color: clipData.exists ? 'var(--olive)' : 'var(--amber)',
                      }}
                    >
                      {clipData.exists ? 'Available on Disk' : 'Pregenerated Fallback'}
                    </span>
                  </div>

                  <div style={{ fontStyle: 'italic', fontSize: '14px', color: 'var(--text-secondary)' }}>
                    "{clipData.text}"
                  </div>

                  {clipData.clip_url && (
                    <button
                      onClick={() => playWav(clipData.clip_url, clipData.clip_id)}
                      style={{
                        alignSelf: 'flex-start',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        padding: '6px 14px',
                        borderRadius: '6px',
                        backgroundColor: 'var(--bg-subtle)',
                        border: '1px solid var(--border)',
                        fontSize: '12px',
                      }}
                    >
                      <Icons.Play />
                      <span>{playingClipId === clipData.clip_id ? 'Playing WAV...' : 'Play Clip Audio'}</span>
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
