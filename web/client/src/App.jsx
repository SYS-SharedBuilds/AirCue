import React, { useState, useEffect, useRef } from 'react';

const API_BASE = 'http://localhost:5001';

// Custom lightweight SVG icons following Claude's understated stroke design
const Icons = {
  Asterisk: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
      <path d="M12 2v20M2 12h20M4.93 4.93l14.14 14.14M4.93 19.07L19.07 4.93" />
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
};

export default function App() {
  const [view, setView] = useState('studio'); // 'studio' | 'telemetry' | 'decision' | 'clips'
  const [status, setStatus] = useState(null);
  const [locations, setLocations] = useState([]);
  const [selectedLoc, setSelectedLoc] = useState('Vijay Nagar Scheme-78, Indore - Glenmark');

  // Generator inputs
  const [model, setModel] = useState('deepseek/deepseek-chat');
  const [language, setLanguage] = useState('hi');
  const [alertLevel, setAlertLevel] = useState(3);
  const [aqiInput, setAqiInput] = useState(245);
  const [pm25Input, setPm25Input] = useState(115.0);
  const [slot, setSlot] = useState('Sports PT');
  const [temperature, setTemperature] = useState(0.7);
  const [isGenerating, setIsGenerating] = useState(false);

  // Conversation history
  const [history, setHistory] = useState([
    {
      id: 'init-1',
      sender: 'assistant',
      text: 'AirCue is ready. Select an outdoor school condition or simulate an AQI change to generate an announcement.',
      timestamp: 'Ready',
      meta: null,
    },
  ]);

  // Telemetry state
  const [telemetry, setTelemetry] = useState(null);
  const [loadingTelemetry, setLoadingTelemetry] = useState(false);

  // Decision Evaluator state
  const [decisionModel, setDecisionModel] = useState('deepseek/deepseek-chat');
  const [decisionResult, setDecisionResult] = useState(null);
  const [isEvaluatingDecision, setIsEvaluatingDecision] = useState(false);

  // Audio Clips state
  const [clipKind, setClipKind] = useState('escalate');
  const [clipLevel, setClipLevel] = useState(2);
  const [clipLang, setClipLang] = useState('hi');
  const [clipSlot, setClipSlot] = useState('sports_pt');
  const [clipData, setClipData] = useState(null);

  const scrollRef = useRef(null);

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
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [history]);

  const handleGenerate = async () => {
    setIsGenerating(true);
    const userPromptText = `Generate a ${language === 'hi' ? 'Hindi' : 'English'} announcement for ${slot} during Level ${alertLevel} air quality (AQI ${aqiInput}, PM2.5 ${pm25Input} µg/m³) at ${selectedLoc}.`;

    const userMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: userPromptText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setHistory((prev) => [...prev, userMessage]);

    try {
      const res = await fetch(`${API_BASE}/api/llm/announcement`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model,
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
        setHistory((prev) => [
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
        setHistory((prev) => [
          ...prev,
          {
            id: `asst-${Date.now()}`,
            sender: 'assistant',
            text: data.clean_text,
            rawText: data.raw_text,
            audioBase64: data.audio_base64,
            validation: data.validation,
            model: data.model,
            latency: data.latency_s,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          },
        ]);
      }
    } catch (err) {
      setHistory((prev) => [
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
      setIsGenerating(false);
    }
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
          aqi: 250,
        }),
      });
      const data = await res.json();
      setClipData(data);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden', backgroundColor: 'var(--bg-app)' }}>
      {/* Warm, minimal Left Sidebar */}
      <aside
        style={{
          width: '260px',
          backgroundColor: 'var(--bg-sidebar)',
          borderRight: '1px solid var(--border)',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          padding: '20px 16px',
          flexShrink: 0,
        }}
      >
        <div>
          {/* Logo / Header */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '0 8px 24px 8px' }}>
            <div
              style={{
                width: '30px',
                height: '30px',
                borderRadius: '8px',
                backgroundColor: 'var(--clay)',
                color: '#fff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Icons.Asterisk />
            </div>
            <div>
              <div style={{ fontFamily: 'var(--font-serif)', fontSize: '18px', fontWeight: '600', color: 'var(--text-primary)' }}>
                AirCue
              </div>
              <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', letterSpacing: '0.02em' }}>
                Voice Feedback System
              </div>
            </div>
          </div>

          {/* Navigation Links */}
          <nav style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            {[
              { id: 'studio', label: 'Spoken Alert Studio', icon: Icons.Speech },
              { id: 'telemetry', label: 'Station Telemetry', icon: Icons.Pulse },
              { id: 'decision', label: 'Decision Reasoner', icon: Icons.Sliders },
              { id: 'clips', label: 'Pregenerated Clips', icon: Icons.Audio },
            ].map((item) => {
              const Icon = item.icon;
              const isActive = view === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setView(item.id)}
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

        {/* Footer info in sidebar */}
        <div style={{ padding: '12px 8px', borderTop: '1px solid var(--border)', fontSize: '11px', color: 'var(--text-tertiary)' }}>
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
              {status?.has_openrouter_key ? 'OpenRouter Active' : 'No API Key'}
            </span>
          </div>
          <div>B.Tech Major Project • PIEMR</div>
          <div style={{ marginTop: '2px' }}>Indore, Madhya Pradesh</div>
        </div>
      </aside>

      {/* Main Content Pane */}
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
        {/* ======================================================== */}
        {/* VIEW 1: SPOKEN ALERT STUDIO (CLAUDE-LIKE CHAT INTERACTION) */}
        {/* ======================================================== */}
        {view === 'studio' && (
          <div style={{ display: 'flex', height: '100%', width: '100%' }}>
            {/* Middle: Conversation Thread */}
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', borderRight: '1px solid var(--border)' }}>
              {/* Top Bar */}
              <div
                style={{
                  height: '52px',
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
                  <span style={{ fontFamily: 'var(--font-serif)', fontSize: '16px', color: 'var(--text-primary)' }}>
                    Outdoor Speech Synthesis
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
                    {model.split('/')[1] || model}
                  </span>
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-tertiary)' }}>
                  Language: {language === 'hi' ? 'Hindi' : 'English'}
                </div>
              </div>

              {/* Message History Scroll Area */}
              <div
                ref={scrollRef}
                style={{
                  flex: 1,
                  overflowY: 'auto',
                  padding: '32px 48px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '24px',
                }}
              >
                {history.map((msg) => (
                  <div
                    key={msg.id}
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                      width: '100%',
                    }}
                  >
                    {msg.sender === 'user' ? (
                      <div
                        style={{
                          maxWidth: '75%',
                          backgroundColor: 'var(--bg-subtle)',
                          border: '1px solid var(--border)',
                          borderRadius: '16px 16px 4px 16px',
                          padding: '12px 18px',
                          fontSize: '13px',
                          lineHeight: '1.5',
                          color: 'var(--text-primary)',
                        }}
                      >
                        {msg.text}
                      </div>
                    ) : (
                      <div style={{ maxWidth: '85%', display: 'flex', gap: '14px', alignItems: 'flex-start' }}>
                        <div
                          style={{
                            width: '28px',
                            height: '28px',
                            borderRadius: '6px',
                            backgroundColor: 'var(--bg-subtle)',
                            border: '1px solid var(--border)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: 'var(--clay)',
                            flexShrink: 0,
                            marginTop: '2px',
                          }}
                        >
                          <Icons.Asterisk />
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                          <div
                            style={{
                              fontFamily: language === 'hi' ? 'var(--font-sans)' : 'var(--font-serif)',
                              fontSize: '17px',
                              lineHeight: '1.6',
                              color: msg.isError ? 'var(--crimson)' : 'var(--text-primary)',
                              letterSpacing: '-0.01em',
                            }}
                          >
                            {msg.text}
                          </div>

                          {/* Voice Player Pill */}
                          {msg.audioBase64 && (
                            <div
                              style={{
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: '10px',
                                padding: '6px 14px',
                                borderRadius: '20px',
                                backgroundColor: 'var(--bg-surface)',
                                border: '1px solid var(--border)',
                                marginTop: '4px',
                                width: 'fit-content',
                              }}
                            >
                              <audio
                                controls
                                src={`data:audio/mp3;base64,${msg.audioBase64}`}
                                style={{ height: '28px', width: '220px' }}
                              />
                              <span style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>
                                Spoken Preview
                              </span>
                            </div>
                          )}

                          {/* Validation summary inline tag */}
                          {msg.validation && (
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '11px', color: 'var(--text-secondary)' }}>
                              <span
                                style={{
                                  display: 'inline-flex',
                                  alignItems: 'center',
                                  gap: '4px',
                                  color: msg.validation.passed ? 'var(--olive)' : 'var(--crimson)',
                                  fontWeight: '600',
                                }}
                              >
                                {msg.validation.passed ? (
                                  <>
                                    <Icons.Check /> Validated (6 Safety Rules Passed)
                                  </>
                                ) : (
                                  `Flagged: ${msg.validation.failures.join(', ')}`
                                )}
                              </span>
                              <span>•</span>
                              <span>{msg.latency}s latency</span>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                ))}

                {isGenerating && (
                  <div style={{ display: 'flex', gap: '14px', alignItems: 'center', color: 'var(--text-tertiary)', fontSize: '13px' }}>
                    <div
                      style={{
                        width: '28px',
                        height: '28px',
                        borderRadius: '6px',
                        backgroundColor: 'var(--bg-subtle)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'var(--clay)',
                      }}
                    >
                      <Icons.Asterisk />
                    </div>
                    <span>Formulating announcement using {model.split('/')[1] || model}...</span>
                  </div>
                )}
              </div>

              {/* Bottom Prompt / Action Bar */}
              <div
                style={{
                  padding: '16px 28px 24px 28px',
                  backgroundColor: 'var(--bg-surface)',
                  borderTop: '1px solid var(--border)',
                }}
              >
                <div
                  style={{
                    border: '1px solid var(--border)',
                    borderRadius: '12px',
                    padding: '12px 16px',
                    backgroundColor: 'var(--bg-app)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    boxShadow: '0 2px 6px rgba(0,0,0,0.02)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flex: 1 }}>
                    <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                      Trigger: <strong style={{ color: 'var(--text-primary)' }}>Level {alertLevel} ({slot})</strong>, AQI {aqiInput} at {selectedLoc.split(',')[0]}
                    </span>
                  </div>

                  <button
                    onClick={handleGenerate}
                    disabled={isGenerating}
                    style={{
                      backgroundColor: 'var(--clay)',
                      color: '#ffffff',
                      borderRadius: '8px',
                      padding: '8px 16px',
                      fontSize: '13px',
                      fontWeight: '500',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      opacity: isGenerating ? 0.6 : 1,
                    }}
                  >
                    <span>Speak</span>
                    <Icons.ArrowUp />
                  </button>
                </div>
              </div>
            </div>

            {/* Right: Thoughtful Context & Parameter Inspector */}
            <div
              style={{
                width: '320px',
                backgroundColor: 'var(--bg-surface)',
                padding: '24px',
                overflowY: 'auto',
                display: 'flex',
                flexDirection: 'column',
                gap: '20px',
                flexShrink: 0,
              }}
            >
              <div>
                <h3 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '4px' }}>
                  Operating Context
                </h3>
                <p style={{ fontSize: '12px', color: 'var(--text-tertiary)', lineHeight: '1.4' }}>
                  Calibrate the physical condition parameters that inform the speaker announcement.
                </p>
              </div>

              {/* Location Selector */}
              <div>
                <label style={{ display: 'block', fontSize: '11px', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                  Campus Station
                </label>
                <select
                  value={selectedLoc}
                  onChange={(e) => setSelectedLoc(e.target.value)}
                  style={{ width: '100%', padding: '8px 10px', fontSize: '12px' }}
                >
                  {locations.map((loc) => (
                    <option key={loc.name} value={loc.name}>
                      {loc.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Alert Level Selector */}
              <div>
                <label style={{ display: 'block', fontSize: '11px', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                  Severity Category
                </label>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '4px' }}>
                  {[
                    { lvl: 1, label: 'L1' },
                    { lvl: 2, label: 'L2' },
                    { lvl: 3, label: 'L3' },
                    { lvl: 4, label: 'L4' },
                  ].map((item) => (
                    <button
                      key={item.lvl}
                      type="button"
                      onClick={() => setAlertLevel(item.lvl)}
                      style={{
                        padding: '6px 0',
                        fontSize: '12px',
                        fontWeight: alertLevel === item.lvl ? '600' : '400',
                        backgroundColor: alertLevel === item.lvl ? 'var(--clay-subtle)' : 'var(--bg-app)',
                        color: alertLevel === item.lvl ? 'var(--clay)' : 'var(--text-secondary)',
                        border: `1px solid ${alertLevel === item.lvl ? 'var(--clay-border)' : 'var(--border)'}`,
                        borderRadius: '4px',
                      }}
                    >
                      {item.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* AQI & PM2.5 sliders/inputs */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '6px' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Air Quality Index</span>
                  <span style={{ fontWeight: '600' }}>{aqiInput}</span>
                </div>
                <input
                  type="range"
                  min="50"
                  max="450"
                  value={aqiInput}
                  onChange={(e) => setAqiInput(Number(e.target.value))}
                  style={{ width: '100%', accentColor: 'var(--clay)' }}
                />
              </div>

              {/* Slot */}
              <div>
                <label style={{ display: 'block', fontSize: '11px', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                  School Timetable Slot
                </label>
                <select
                  value={slot}
                  onChange={(e) => setSlot(e.target.value)}
                  style={{ width: '100%', padding: '8px 10px', fontSize: '12px' }}
                >
                  <option value="Sports PT">Sports Field / PT Period</option>
                  <option value="Morning Assembly">Morning Assembly</option>
                  <option value="Recess">Outdoor Recess / Break</option>
                  <option value="Dismissal">Dismissal / Campus Gate</option>
                  <option value="General Campus">General Campus Grounds</option>
                </select>
              </div>

              {/* Language */}
              <div>
                <label style={{ display: 'block', fontSize: '11px', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                  Spoken Language
                </label>
                <div style={{ display: 'flex', gap: '8px' }}>
                  {[
                    { id: 'hi', label: 'Hindi (Devanagari)' },
                    { id: 'en', label: 'English' },
                  ].map((l) => (
                    <button
                      key={l.id}
                      type="button"
                      onClick={() => setLanguage(l.id)}
                      style={{
                        flex: 1,
                        padding: '6px 0',
                        fontSize: '12px',
                        borderRadius: '4px',
                        backgroundColor: language === l.id ? 'var(--clay-subtle)' : 'var(--bg-app)',
                        color: language === l.id ? 'var(--clay)' : 'var(--text-secondary)',
                        border: `1px solid ${language === l.id ? 'var(--clay-border)' : 'var(--border)'}`,
                        fontWeight: language === l.id ? '600' : '400',
                      }}
                    >
                      {l.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Model Choice */}
              <div>
                <label style={{ display: 'block', fontSize: '11px', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                  Underlying Model
                </label>
                <select
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  style={{ width: '100%', padding: '8px 10px', fontSize: '12px' }}
                >
                  <option value="deepseek/deepseek-chat">DeepSeek Chat</option>
                  <option value="moonshotai/kimi-k3">Moonshot Kimi K3</option>
                  <option value="meta-llama/llama-3.3-70b-instruct">Llama 3.3 70B</option>
                  <option value="qwen/qwen-2.5-72b-instruct">Qwen 2.5 72B</option>
                  <option value="google/gemma-4-31b-it:free">Gemma 4 31B (Free)</option>
                </select>
              </div>

              <div style={{ borderTop: '1px solid var(--border)', paddingTop: '16px', fontSize: '11px', color: 'var(--text-tertiary)', lineHeight: '1.5' }}>
                <strong>Deterministic Fallback:</strong> In live deployment, if OpenRouter response time exceeds 2.0s, the engine instantly plays a pregenerated audio clip.
              </div>
            </div>
          </div>
        )}

        {/* ======================================================== */}
        {/* VIEW 2: STATION TELEMETRY (CLEAN DATA LOG) */}
        {/* ======================================================== */}
        {view === 'telemetry' && (
          <div style={{ padding: '36px 48px', overflowY: 'auto', flex: 1 }}>
            <div style={{ maxWidth: '960px', margin: '0 auto' }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '28px' }}>
                <div>
                  <h2 style={{ fontSize: '24px', fontWeight: '500', marginBottom: '4px' }}>
                    Air Quality Observations
                  </h2>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
                    Continuous particulate matter monitoring data across Madhya Pradesh.
                  </p>
                </div>

                <select
                  value={selectedLoc}
                  onChange={(e) => setSelectedLoc(e.target.value)}
                  style={{ minWidth: '340px', padding: '8px 12px', fontSize: '13px' }}
                >
                  {locations.map((loc) => (
                    <option key={loc.name} value={loc.name}>
                      {loc.name} ({loc.dataset_kind === 'measured_station' ? 'Physical Station' : 'CAMS Model'})
                    </option>
                  ))}
                </select>
              </div>

              {/* Station metrics in warm quiet cards */}
              {telemetry?.stats && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '28px' }}>
                  <div style={{ backgroundColor: 'var(--bg-surface)', padding: '16px', borderRadius: '8px', border: '1px solid var(--border)' }}>
                    <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                      Station Type
                    </div>
                    <div style={{ fontSize: '16px', fontWeight: '500', marginTop: '4px', color: 'var(--text-primary)' }}>
                      {telemetry.stats.dataset_kind === 'measured_station' ? 'Physical CAAQMS' : 'Numerical Model'}
                    </div>
                  </div>

                  <div style={{ backgroundColor: 'var(--bg-surface)', padding: '16px', borderRadius: '8px', border: '1px solid var(--border)' }}>
                    <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                      Mean PM2.5
                    </div>
                    <div style={{ fontSize: '20px', fontWeight: '500', marginTop: '4px' }}>
                      {telemetry.stats.mean_pm25 ?? '—'} <span style={{ fontSize: '12px', color: 'var(--text-tertiary)' }}>µg/m³</span>
                    </div>
                  </div>

                  <div style={{ backgroundColor: 'var(--bg-surface)', padding: '16px', borderRadius: '8px', border: '1px solid var(--border)' }}>
                    <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                      Average CPCB AQI
                    </div>
                    <div style={{ fontSize: '20px', fontWeight: '500', marginTop: '4px' }}>
                      {telemetry.stats.mean_aqi ?? '—'}
                    </div>
                  </div>

                  <div style={{ backgroundColor: 'var(--bg-surface)', padding: '16px', borderRadius: '8px', border: '1px solid var(--border)' }}>
                    <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                      Peak Recorded AQI
                    </div>
                    <div style={{ fontSize: '20px', fontWeight: '500', marginTop: '4px' }}>
                      {telemetry.stats.max_aqi ?? '—'}
                    </div>
                  </div>
                </div>
              )}

              {/* Data Table */}
              <div style={{ backgroundColor: 'var(--bg-surface)', borderRadius: '8px', border: '1px solid var(--border)', overflow: 'hidden' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13px' }}>
                  <thead>
                    <tr style={{ backgroundColor: 'var(--bg-subtle)', borderBottom: '1px solid var(--border)', color: 'var(--text-secondary)' }}>
                      <th style={{ padding: '12px 16px', fontWeight: '500' }}>Timestamp</th>
                      <th style={{ padding: '12px 16px', fontWeight: '500' }}>PM2.5 (µg/m³)</th>
                      <th style={{ padding: '12px 16px', fontWeight: '500' }}>PM10 (µg/m³)</th>
                      <th style={{ padding: '12px 16px', fontWeight: '500' }}>CPCB AQI</th>
                      <th style={{ padding: '12px 16px', fontWeight: '500' }}>Category</th>
                    </tr>
                  </thead>
                  <tbody>
                    {telemetry?.records?.slice(-25).reverse().map((r, i) => (
                      <tr key={i} style={{ borderBottom: '1px solid var(--border-light)' }}>
                        <td style={{ padding: '10px 16px', color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)', fontSize: '12px' }}>
                          {r.dt}
                        </td>
                        <td style={{ padding: '10px 16px' }}>{r.pm2_5 ?? '—'}</td>
                        <td style={{ padding: '10px 16px' }}>{r.pm10 ?? '—'}</td>
                        <td style={{ padding: '10px 16px', fontWeight: '600' }}>{r.cpcb_aqi ?? '—'}</td>
                        <td style={{ padding: '10px 16px', color: 'var(--text-secondary)' }}>{r.cpcb_category}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* ======================================================== */}
        {/* VIEW 3: DECISION REASONER (TASK 2) */}
        {/* ======================================================== */}
        {view === 'decision' && (
          <div style={{ padding: '36px 48px', overflowY: 'auto', flex: 1 }}>
            <div style={{ maxWidth: '820px', margin: '0 auto' }}>
              <h2 style={{ fontSize: '24px', fontWeight: '500', marginBottom: '6px' }}>
                Zero-Shot Trigger Evaluation
              </h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '28px' }}>
                Testing language models on interpreting a 5-hour sequential outdoor particulate trend and producing strict structured JSON triggers.
              </p>

              <div style={{ backgroundColor: 'var(--bg-surface)', padding: '24px', borderRadius: '8px', border: '1px solid var(--border)', marginBottom: '24px' }}>
                <div style={{ display: 'flex', gap: '16px', alignItems: 'center', marginBottom: '20px' }}>
                  <div style={{ flex: 1 }}>
                    <label style={{ display: 'block', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                      Model
                    </label>
                    <select
                      value={decisionModel}
                      onChange={(e) => setDecisionModel(e.target.value)}
                      style={{ width: '100%', padding: '8px 12px' }}
                    >
                      <option value="deepseek/deepseek-chat">DeepSeek Chat</option>
                      <option value="moonshotai/kimi-k3">Moonshot Kimi K3</option>
                      <option value="meta-llama/llama-3.3-70b-instruct">Llama 3.3 70B</option>
                      <option value="qwen/qwen-2.5-72b-instruct">Qwen 2.5 72B</option>
                    </select>
                  </div>

                  <button
                    onClick={handleRunDecision}
                    disabled={isEvaluatingDecision}
                    style={{
                      alignSelf: 'flex-end',
                      backgroundColor: 'var(--clay)',
                      color: '#fff',
                      padding: '9px 18px',
                      borderRadius: '6px',
                      fontSize: '13px',
                      fontWeight: '500',
                      opacity: isEvaluatingDecision ? 0.6 : 1,
                    }}
                  >
                    {isEvaluatingDecision ? 'Evaluating...' : 'Evaluate Sequence'}
                  </button>
                </div>

                <div style={{ fontSize: '12px', color: 'var(--text-tertiary)', marginBottom: '8px' }}>
                  Input Multi-hour Sequence (Increasing PM Trajectory):
                </div>
                <div style={{ backgroundColor: 'var(--bg-subtle)', padding: '12px 16px', borderRadius: '6px', fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--text-secondary)' }}>
                  08:00 (PM2.5: 42.0, AQI: 95) → 09:00 (PM2.5: 68.0, AQI: 145) → 10:00 (PM2.5: 98.0, AQI: 215) → 11:00 (PM2.5: 118.0, AQI: 255) → 12:00 (PM2.5: 135.0, AQI: 285)
                </div>
              </div>

              {decisionResult && (
                <div style={{ backgroundColor: 'var(--bg-surface)', padding: '24px', borderRadius: '8px', border: '1px solid var(--border)' }}>
                  <div style={{ fontSize: '13px', fontWeight: '600', marginBottom: '12px' }}>
                    Model Response & Parsed Schema
                  </div>
                  {decisionResult.parsed ? (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginBottom: '16px' }}>
                      <div style={{ padding: '12px', backgroundColor: 'var(--bg-subtle)', borderRadius: '6px' }}>
                        <div style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>Decision</div>
                        <div style={{ fontSize: '16px', fontWeight: '600', color: decisionResult.parsed.speak ? 'var(--clay)' : 'var(--olive)' }}>
                          {decisionResult.parsed.speak ? 'TRIGGER SPEAK' : 'SILENT'}
                        </div>
                      </div>
                      <div style={{ padding: '12px', backgroundColor: 'var(--bg-subtle)', borderRadius: '6px' }}>
                        <div style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>Event Kind</div>
                        <div style={{ fontSize: '16px', fontWeight: '600' }}>
                          {decisionResult.parsed.event}
                        </div>
                      </div>
                      <div style={{ padding: '12px', backgroundColor: 'var(--bg-subtle)', borderRadius: '6px' }}>
                        <div style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>Level</div>
                        <div style={{ fontSize: '16px', fontWeight: '600' }}>
                          Level {decisionResult.parsed.level}
                        </div>
                      </div>
                    </div>
                  ) : null}

                  <pre style={{ backgroundColor: 'var(--bg-subtle)', padding: '12px', borderRadius: '6px', fontSize: '12px', fontFamily: 'var(--font-mono)', overflowX: 'auto' }}>
                    {decisionResult.raw_text || decisionResult.error}
                  </pre>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ======================================================== */}
        {/* VIEW 4: PREGENERATED CLIPS (OFFLINE CATALOG) */}
        {/* ======================================================== */}
        {view === 'clips' && (
          <div style={{ padding: '36px 48px', overflowY: 'auto', flex: 1 }}>
            <div style={{ maxWidth: '820px', margin: '0 auto' }}>
              <h2 style={{ fontSize: '24px', fontWeight: '500', marginBottom: '6px' }}>
                Pregenerated Backup Audio Clips
              </h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '28px' }}>
                Offline fallback repository containing 200 pre-synthesized announcements with SHA-256 integrity checks.
              </p>

              <div style={{ backgroundColor: 'var(--bg-surface)', padding: '24px', borderRadius: '8px', border: '1px solid var(--border)', marginBottom: '24px' }}>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '20px' }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px' }}>Event</label>
                    <select value={clipKind} onChange={(e) => setClipKind(e.target.value)} style={{ width: '100%', padding: '6px 8px' }}>
                      <option value="escalate">Escalate</option>
                      <option value="reminder">Reminder</option>
                      <option value="improving">Improving</option>
                      <option value="recovered">Recovered</option>
                    </select>
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px' }}>Level</label>
                    <select value={clipLevel} onChange={(e) => setClipLevel(Number(e.target.value))} style={{ width: '100%', padding: '6px 8px' }}>
                      <option value={1}>Level 1</option>
                      <option value={2}>Level 2</option>
                      <option value={3}>Level 3</option>
                      <option value={4}>Level 4</option>
                    </select>
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px' }}>Language</label>
                    <select value={clipLang} onChange={(e) => setClipLang(e.target.value)} style={{ width: '100%', padding: '6px 8px' }}>
                      <option value="hi">Hindi</option>
                      <option value="en">English</option>
                    </select>
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px' }}>Slot</label>
                    <select value={clipSlot} onChange={(e) => setClipSlot(e.target.value)} style={{ width: '100%', padding: '6px 8px' }}>
                      <option value="sports_pt">Sports PT</option>
                      <option value="assembly">Assembly</option>
                      <option value="recess">Recess</option>
                      <option value="dismissal">Dismissal</option>
                      <option value="general">General</option>
                    </select>
                  </div>
                </div>

                <button
                  onClick={handleResolveClip}
                  style={{
                    backgroundColor: 'var(--clay)',
                    color: '#fff',
                    padding: '8px 16px',
                    borderRadius: '6px',
                    fontSize: '13px',
                    fontWeight: '500',
                  }}
                >
                  Resolve Audio Clip
                </button>
              </div>

              {clipData && (
                <div style={{ backgroundColor: 'var(--bg-surface)', padding: '24px', borderRadius: '8px', border: '1px solid var(--border)' }}>
                  <div style={{ fontSize: '12px', color: 'var(--text-tertiary)', marginBottom: '4px' }}>
                    Resolved Clip Identifier: <code>{clipData.clip_id}.wav</code>
                  </div>
                  <div style={{ fontFamily: 'var(--font-serif)', fontSize: '18px', color: 'var(--text-primary)', margin: '12px 0 20px 0' }}>
                    "{clipData.text}"
                  </div>

                  {clipData.exists && clipData.clip_url ? (
                    <audio controls src={`${API_BASE}${clipData.clip_url}`} style={{ width: '100%' }} />
                  ) : (
                    <div style={{ color: 'var(--amber)', fontSize: '13px' }}>
                      Clip not found in local clips repository. Run <code>aircue clips build</code>.
                    </div>
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
