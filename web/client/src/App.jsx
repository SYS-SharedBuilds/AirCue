import React, { useState, useEffect } from 'react';
import {
  Activity,
  Mic,
  BrainCircuit,
  Volume2,
  BarChart3,
  ShieldCheck,
  ShieldAlert,
  Radio,
  MapPin,
  Sparkles,
  Play,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  Info,
  Clock,
  Layers,
  Cpu
} from 'lucide-react';

const API_BASE = 'http://localhost:5001';

export default function App() {
  const [activeTab, setActiveTab] = useState('announcement');
  const [status, setStatus] = useState(null);
  const [locations, setLocations] = useState([]);
  const [selectedLoc, setSelectedLoc] = useState('Vijay Nagar Scheme-78, Indore - Glenmark');
  const [telemetry, setTelemetry] = useState(null);
  const [loadingTelemetry, setLoadingTelemetry] = useState(false);

  // Tab 2: LLM Announcement Generator state
  const [model, setModel] = useState('deepseek/deepseek-chat');
  const [alertLevel, setAlertLevel] = useState(3);
  const [aqiInput, setAqiInput] = useState(245);
  const [pm25Input, setPm25Input] = useState(112.5);
  const [slot, setSlot] = useState('Sports PT');
  const [language, setLanguage] = useState('hi');
  const [temperature, setTemperature] = useState(0.7);
  const [announcementResult, setAnnouncementResult] = useState(null);
  const [generatingAnnouncement, setGeneratingAnnouncement] = useState(false);

  // Tab 3: LLM Decision Engine state
  const [decisionModel, setDecisionModel] = useState('deepseek/deepseek-chat');
  const [decisionResult, setDecisionResult] = useState(null);
  const [evaluatingDecision, setEvaluatingDecision] = useState(false);

  // Tab 5: Clip Preview state
  const [clipLevel, setClipLevel] = useState(2);
  const [clipKind, setClipKind] = useState('escalate');
  const [clipLang, setClipLang] = useState('hi');
  const [clipSlot, setClipSlot] = useState('sports_pt');
  const [clipResult, setClipResult] = useState(null);

  // Initial load
  useEffect(() => {
    fetch(`${API_BASE}/api/status`)
      .then((res) => res.json())
      .then((data) => setStatus(data))
      .catch((err) => console.error('Status fetch error:', err));

    fetch(`${API_BASE}/api/locations`)
      .then((res) => res.json())
      .then((data) => {
        if (data.locations) {
          setLocations(data.locations);
        }
      })
      .catch((err) => console.error('Locations fetch error:', err));
  }, []);

  // Fetch telemetry when selected location changes
  useEffect(() => {
    if (!selectedLoc) return;
    setLoadingTelemetry(true);
    fetch(`${API_BASE}/api/telemetry?location=${encodeURIComponent(selectedLoc)}&limit=100`)
      .then((res) => res.json())
      .then((data) => {
        setTelemetry(data);
        setLoadingTelemetry(false);
      })
      .catch((err) => {
        console.error('Telemetry fetch error:', err);
        setLoadingTelemetry(false);
      });
  }, [selectedLoc]);

  // Handle LLM Announcement Generation
  const handleGenerateAnnouncement = async () => {
    setGeneratingAnnouncement(true);
    setAnnouncementResult(null);
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
      setAnnouncementResult(data);
    } catch (err) {
      setAnnouncementResult({ error: err.message });
    } finally {
      setGeneratingAnnouncement(false);
    }
  };

  // Handle LLM Decision Evaluation
  const handleEvaluateDecision = async () => {
    setEvaluatingDecision(true);
    setDecisionResult(null);
    try {
      const history = [
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
          history,
          current_state: { level: 0, minutes_since_last: 180 },
        }),
      });
      const data = await res.json();
      setDecisionResult(data);
    } catch (err) {
      setDecisionResult({ error: err.message });
    } finally {
      setEvaluatingDecision(false);
    }
  };

  // Handle Pre-synthesized Clip preview
  const handlePreviewClip = async () => {
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
      setClipResult(data);
    } catch (err) {
      console.error('Clip preview error:', err);
    }
  };

  const getAQIColor = (aqi) => {
    if (aqi <= 50) return '#10b981';
    if (aqi <= 100) return '#84cc16';
    if (aqi <= 200) return '#eab308';
    if (aqi <= 300) return '#f97316';
    if (aqi <= 400) return '#ef4444';
    return '#881337';
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', flexDirection: 'column' }}>
      {/* Header */}
      <header
        style={{
          borderBottom: '1px solid var(--border-color)',
          backgroundColor: 'var(--bg-secondary)',
          padding: '16px 32px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div
            style={{
              width: '42px',
              height: '42px',
              borderRadius: '10px',
              background: 'linear-gradient(135deg, var(--accent-cyan), var(--accent-blue))',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#fff',
            }}
          >
            <Radio size={24} />
          </div>
          <div>
            <h1 style={{ fontSize: '20px', fontWeight: '700', letterSpacing: '-0.5px' }}>AirCue</h1>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
              Outdoor School AQI Voice Alert System & LLM Benchmark Testbed
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div
            style={{
              padding: '6px 14px',
              borderRadius: '20px',
              backgroundColor: status?.has_openrouter_key ? '#064e3b' : '#450a0a',
              border: `1px solid ${status?.has_openrouter_key ? '#059669' : '#b91c1c'}`,
              color: status?.has_openrouter_key ? '#6ee7b7' : '#fca5a5',
              fontSize: '12px',
              fontWeight: '600',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <span
              style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                backgroundColor: status?.has_openrouter_key ? '#10b981' : '#ef4444',
              }}
            />
            {status?.has_openrouter_key ? 'OpenRouter Connected' : 'No OpenRouter Key'}
          </div>

          <div
            style={{
              padding: '6px 14px',
              borderRadius: '20px',
              backgroundColor: 'var(--bg-card)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-secondary)',
              fontSize: '12px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <Cpu size={14} color="var(--accent-cyan)" />
            Node.js / Express Engine
          </div>
        </div>
      </header>

      {/* Main Navigation Bar */}
      <nav
        style={{
          display: 'flex',
          gap: '8px',
          padding: '12px 32px',
          backgroundColor: 'var(--bg-secondary)',
          borderBottom: '1px solid var(--border-subtle)',
        }}
      >
        {[
          { id: 'announcement', label: 'LLM Spoken Alert Generator', icon: Mic },
          { id: 'decision', label: 'LLM Trigger Decision Engine', icon: BrainCircuit },
          { id: 'telemetry', label: 'Madhya Pradesh AQI Telemetry', icon: Activity },
          { id: 'clips', label: 'Pregenerated Audio Clips', icon: Volume2 },
          { id: 'quota', label: 'Benchmark & Quota Tracker', icon: BarChart3 },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 18px',
                borderRadius: '8px',
                fontSize: '13px',
                fontWeight: isActive ? '600' : '500',
                color: isActive ? '#fff' : 'var(--text-secondary)',
                backgroundColor: isActive ? 'var(--bg-card)' : 'transparent',
                border: isActive ? '1px solid var(--accent-cyan)' : '1px solid transparent',
                transition: 'all 0.15s ease',
              }}
            >
              <Icon size={16} color={isActive ? 'var(--accent-cyan)' : 'var(--text-muted)'} />
              {tab.label}
            </button>
          );
        })}
      </nav>

      {/* Main Content Area */}
      <main style={{ flex: 1, padding: '32px', maxWidth: '1440px', width: '100%', margin: '0 auto' }}>
        {/* ======================================================== */}
        {/* TAB 1: LLM SPOKEN ANNOUNCEMENT GENERATOR */}
        {/* ======================================================== */}
        {activeTab === 'announcement' && (
          <div style={{ display: 'grid', gridTemplateColumns: '420px 1fr', gap: '32px' }}>
            {/* Control Panel */}
            <div
              style={{
                backgroundColor: 'var(--bg-secondary)',
                borderRadius: '12px',
                border: '1px solid var(--border-color)',
                padding: '24px',
                display: 'flex',
                flexDirection: 'column',
                gap: '20px',
              }}
            >
              <div>
                <h2 style={{ fontSize: '16px', fontWeight: '700', marginBottom: '6px' }}>
                  Announcement Parameters
                </h2>
                <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                  Configure outdoor alert conditions and test LLM generation via OpenRouter.
                </p>
              </div>

              {/* Model Select */}
              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: '600', marginBottom: '8px', color: 'var(--text-secondary)' }}>
                  OpenRouter Model
                </label>
                <select
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px 14px',
                    borderRadius: '8px',
                    backgroundColor: 'var(--bg-card)',
                    border: '1px solid var(--border-color)',
                    color: 'var(--text-primary)',
                    fontSize: '13px',
                  }}
                >
                  <option value="deepseek/deepseek-chat">DeepSeek Chat (deepseek/deepseek-chat)</option>
                  <option value="moonshotai/kimi-k3">Moonshot Kimi K3 (moonshotai/kimi-k3)</option>
                  <option value="meta-llama/llama-3.3-70b-instruct">Llama 3.3 70B Instruct</option>
                  <option value="qwen/qwen-2.5-72b-instruct">Qwen 2.5 72B Instruct</option>
                  <option value="mistralai/mistral-small-3.2-24b-instruct">Mistral Small 3.2 24B</option>
                  <option value="google/gemma-4-31b-it:free">Gemma 4 31B (free preview)</option>
                </select>
              </div>

              {/* Target Location */}
              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: '600', marginBottom: '8px', color: 'var(--text-secondary)' }}>
                  School Ground / Station Location
                </label>
                <select
                  value={selectedLoc}
                  onChange={(e) => setSelectedLoc(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px 14px',
                    borderRadius: '8px',
                    backgroundColor: 'var(--bg-card)',
                    border: '1px solid var(--border-color)',
                    color: 'var(--text-primary)',
                    fontSize: '13px',
                  }}
                >
                  {locations.map((loc) => (
                    <option key={loc.name} value={loc.name}>
                      {loc.name} ({loc.dataset_kind === 'measured_station' ? 'Station' : 'Model'})
                    </option>
                  ))}
                </select>
              </div>

              {/* Severity Level */}
              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: '600', marginBottom: '8px', color: 'var(--text-secondary)' }}>
                  CPCB Trigger Severity Level
                </label>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px' }}>
                  {[
                    { lvl: 1, label: 'L1: Moderate', color: '#eab308' },
                    { lvl: 2, label: 'L2: Poor', color: '#f97316' },
                    { lvl: 3, label: 'L3: V. Poor', color: '#ef4444' },
                    { lvl: 4, label: 'L4: Severe', color: '#991b1b' },
                  ].map((item) => (
                    <button
                      key={item.lvl}
                      type="button"
                      onClick={() => setAlertLevel(item.lvl)}
                      style={{
                        padding: '10px 6px',
                        borderRadius: '6px',
                        fontSize: '11px',
                        fontWeight: '700',
                        textAlign: 'center',
                        backgroundColor: alertLevel === item.lvl ? item.color : 'var(--bg-card)',
                        color: alertLevel === item.lvl ? '#fff' : 'var(--text-secondary)',
                        border: `1px solid ${alertLevel === item.lvl ? item.color : 'var(--border-color)'}`,
                      }}
                    >
                      {item.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Numeric Inputs */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', marginBottom: '6px', color: 'var(--text-secondary)' }}>
                    Simulated AQI
                  </label>
                  <input
                    type="number"
                    value={aqiInput}
                    onChange={(e) => setAqiInput(Number(e.target.value))}
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      borderRadius: '6px',
                      backgroundColor: 'var(--bg-card)',
                      border: '1px solid var(--border-color)',
                      color: 'var(--text-primary)',
                      fontSize: '13px',
                    }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', marginBottom: '6px', color: 'var(--text-secondary)' }}>
                    PM2.5 (µg/m³)
                  </label>
                  <input
                    type="number"
                    value={pm25Input}
                    onChange={(e) => setPm25Input(Number(e.target.value))}
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      borderRadius: '6px',
                      backgroundColor: 'var(--bg-card)',
                      border: '1px solid var(--border-color)',
                      color: 'var(--text-primary)',
                      fontSize: '13px',
                    }}
                  />
                </div>
              </div>

              {/* Slot & Language */}
              <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '12px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', marginBottom: '6px', color: 'var(--text-secondary)' }}>
                    School Slot
                  </label>
                  <select
                    value={slot}
                    onChange={(e) => setSlot(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      borderRadius: '6px',
                      backgroundColor: 'var(--bg-card)',
                      border: '1px solid var(--border-color)',
                      color: 'var(--text-primary)',
                      fontSize: '13px',
                    }}
                  >
                    <option value="Sports PT">Sports PT / Field</option>
                    <option value="Morning Assembly">Morning Assembly</option>
                    <option value="Recess">Recess / Outdoor Lunch</option>
                    <option value="Dismissal">Dismissal / Gate</option>
                    <option value="General Campus">General Grounds</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '12px', marginBottom: '6px', color: 'var(--text-secondary)' }}>
                    Language
                  </label>
                  <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      borderRadius: '6px',
                      backgroundColor: 'var(--bg-card)',
                      border: '1px solid var(--border-color)',
                      color: 'var(--text-primary)',
                      fontSize: '13px',
                    }}
                  >
                    <option value="hi">Hindi (Devanagari)</option>
                    <option value="en">English (School)</option>
                  </select>
                </div>
              </div>

              {/* Temperature slider */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '6px', color: 'var(--text-secondary)' }}>
                  <span>Sampling Temperature</span>
                  <span>{temperature}</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={temperature}
                  onChange={(e) => setTemperature(Number(e.target.value))}
                  style={{ width: '100%' }}
                />
              </div>

              {/* Action Button */}
              <button
                type="button"
                onClick={handleGenerateAnnouncement}
                disabled={generatingAnnouncement}
                style={{
                  marginTop: '8px',
                  backgroundColor: 'var(--accent-cyan)',
                  color: '#0b0f19',
                  padding: '12px',
                  borderRadius: '8px',
                  fontWeight: '700',
                  fontSize: '14px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  boxShadow: '0 4px 12px rgba(6, 182, 212, 0.25)',
                  opacity: generatingAnnouncement ? 0.7 : 1,
                }}
              >
                {generatingAnnouncement ? (
                  <>
                    <RotateCcw className="spin" size={18} /> Generating via OpenRouter...
                  </>
                ) : (
                  <>
                    <Sparkles size={18} /> Generate Spoken Alert
                  </>
                )}
              </button>
            </div>

            {/* Response & Verification Panel */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              {/* Spoken Alert Card */}
              <div
                style={{
                  backgroundColor: 'var(--bg-secondary)',
                  borderRadius: '12px',
                  border: '1px solid var(--border-color)',
                  padding: '28px',
                  minHeight: '260px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'center',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
                  <span style={{ fontSize: '12px', textTransform: 'uppercase', letterSpacing: '1px', color: 'var(--text-muted)', fontWeight: '700' }}>
                    Generated Spoken Alert Output
                  </span>
                  {announcementResult?.latency_s && (
                    <span
                      style={{
                        fontSize: '12px',
                        padding: '4px 10px',
                        borderRadius: '12px',
                        backgroundColor: 'var(--bg-card)',
                        border: '1px solid var(--border-color)',
                        color: 'var(--accent-cyan)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                      }}
                    >
                      <Clock size={12} /> {announcementResult.latency_s}s Latency
                    </span>
                  )}
                </div>

                {announcementResult?.clean_text ? (
                  <div>
                    <blockquote
                      style={{
                        fontSize: '22px',
                        fontWeight: '600',
                        lineHeight: '1.5',
                        color: '#fff',
                        fontStyle: 'normal',
                        borderLeft: '4px solid var(--accent-cyan)',
                        paddingLeft: '20px',
                        marginBottom: '24px',
                      }}
                    >
                      "{announcementResult.clean_text}"
                    </blockquote>

                    {/* Audio Player if generated */}
                    {announcementResult.audio_base64 && (
                      <div
                        style={{
                          backgroundColor: 'var(--bg-card)',
                          padding: '16px',
                          borderRadius: '8px',
                          border: '1px solid var(--border-color)',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '16px',
                        }}
                      >
                        <Volume2 size={24} color="var(--accent-cyan)" />
                        <div style={{ flex: 1 }}>
                          <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                            Spoken Voice Audio Preview (Google TTS Engine)
                          </p>
                          <audio
                            controls
                            src={`data:audio/mp3;base64,${announcementResult.audio_base64}`}
                            style={{ width: '100%', height: '36px' }}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                ) : announcementResult?.error ? (
                  <div style={{ color: 'var(--accent-rose)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <AlertTriangle size={20} />
                    <span>Error: {announcementResult.error}</span>
                  </div>
                ) : (
                  <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                    <Mic size={48} style={{ opacity: 0.2, marginBottom: '12px' }} />
                    <p style={{ fontSize: '14px' }}>Select parameters and click "Generate Spoken Alert" to test live inference.</p>
                  </div>
                )}
              </div>

              {/* 6-Point Safety Scorecard */}
              {announcementResult?.validation && (
                <div
                  style={{
                    backgroundColor: 'var(--bg-secondary)',
                    borderRadius: '12px',
                    border: '1px solid var(--border-color)',
                    padding: '24px',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
                    <h3 style={{ fontSize: '15px', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <ShieldCheck size={18} color="var(--accent-cyan)" /> 6-Point Safety & Domain Rule Audit
                    </h3>
                    <span
                      style={{
                        padding: '4px 12px',
                        borderRadius: '12px',
                        fontSize: '12px',
                        fontWeight: '700',
                        backgroundColor: announcementResult.validation.passed ? '#064e3b' : '#450a0a',
                        color: announcementResult.validation.passed ? '#6ee7b7' : '#fca5a5',
                      }}
                    >
                      {announcementResult.validation.passed ? 'ALL CHECKS PASSED' : 'SAFETY VIOLATION DETECTED'}
                    </span>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
                    {[
                      {
                        key: 'word_limit',
                        title: 'Word Limit (≤ 22 words)',
                        desc: 'Keeps alert under natural 10-15s speaker budget',
                      },
                      {
                        key: 'sentence_count',
                        title: 'Sentence Count (1-2 sentences)',
                        desc: 'Concise announcement without rambling',
                      },
                      {
                        key: 'no_indoor_ventilation',
                        title: 'Zero Indoor Ventilation Advice',
                        desc: 'Bans doors, windows, fresh air, stuffiness',
                      },
                      {
                        key: 'no_medical_scare',
                        title: 'Zero Medical Panic',
                        desc: 'Bans asthma, toxic, cancer, death, hospital',
                      },
                      {
                        key: 'language_script',
                        title: 'Script & Language Match',
                        desc: 'Devanagari for Hindi, Latin for English',
                      },
                      {
                        key: 'no_hallucinated_digits',
                        title: 'Zero Number Hallucination',
                        desc: 'Prevents inventing unverified AQI numbers',
                      },
                    ].map((rule) => {
                      const isPass = announcementResult.validation.rules[rule.key];
                      return (
                        <div
                          key={rule.key}
                          style={{
                            backgroundColor: 'var(--bg-card)',
                            padding: '16px',
                            borderRadius: '8px',
                            border: `1px solid ${isPass ? 'rgba(16, 185, 129, 0.3)' : 'rgba(244, 63, 94, 0.4)'}`,
                          }}
                        >
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                            {isPass ? (
                              <CheckCircle2 size={16} color="var(--accent-emerald)" />
                            ) : (
                              <AlertTriangle size={16} color="var(--accent-rose)" />
                            )}
                            <span style={{ fontSize: '13px', fontWeight: '600' }}>{rule.title}</span>
                          </div>
                          <p style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{rule.desc}</p>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ======================================================== */}
        {/* TAB 2: LLM TRIGGER DECISION ENGINE */}
        {/* ======================================================== */}
        {activeTab === 'decision' && (
          <div style={{ display: 'grid', gridTemplateColumns: '420px 1fr', gap: '32px' }}>
            <div
              style={{
                backgroundColor: 'var(--bg-secondary)',
                borderRadius: '12px',
                border: '1px solid var(--border-color)',
                padding: '24px',
                display: 'flex',
                flexDirection: 'column',
                gap: '20px',
              }}
            >
              <div>
                <h2 style={{ fontSize: '16px', fontWeight: '700', marginBottom: '6px' }}>
                  Zero-Shot Decision Evaluator
                </h2>
                <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                  Task 2 benchmark: tests whether an LLM can evaluate multi-hour particulate sequences and emit strict JSON triggers.
                </p>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: '600', marginBottom: '8px', color: 'var(--text-secondary)' }}>
                  Decision Model
                </label>
                <select
                  value={decisionModel}
                  onChange={(e) => setDecisionModel(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px 14px',
                    borderRadius: '8px',
                    backgroundColor: 'var(--bg-card)',
                    border: '1px solid var(--border-color)',
                    color: 'var(--text-primary)',
                    fontSize: '13px',
                  }}
                >
                  <option value="deepseek/deepseek-chat">DeepSeek Chat (deepseek/deepseek-chat)</option>
                  <option value="moonshotai/kimi-k3">Moonshot Kimi K3 (moonshotai/kimi-k3)</option>
                  <option value="meta-llama/llama-3.3-70b-instruct">Llama 3.3 70B Instruct</option>
                  <option value="qwen/qwen-2.5-72b-instruct">Qwen 2.5 72B Instruct</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: '600', marginBottom: '8px', color: 'var(--text-secondary)' }}>
                  Input 5-Hour Sequence (Increasing PM Trajectory)
                </label>
                <div
                  style={{
                    backgroundColor: 'var(--bg-card)',
                    borderRadius: '8px',
                    padding: '12px',
                    border: '1px solid var(--border-color)',
                    fontSize: '12px',
                    fontFamily: 'monospace',
                    color: 'var(--text-secondary)',
                  }}
                >
                  <div>08:00 | PM2.5: 42.0 | AQI: 95</div>
                  <div>09:00 | PM2.5: 68.0 | AQI: 145</div>
                  <div>10:00 | PM2.5: 98.0 | AQI: 215</div>
                  <div>11:00 | PM2.5: 118.0 | AQI: 255</div>
                  <div>12:00 | PM2.5: 135.0 | AQI: 285</div>
                </div>
              </div>

              <button
                type="button"
                onClick={handleEvaluateDecision}
                disabled={evaluatingDecision}
                style={{
                  backgroundColor: 'var(--accent-blue)',
                  color: '#fff',
                  padding: '12px',
                  borderRadius: '8px',
                  fontWeight: '700',
                  fontSize: '14px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  opacity: evaluatingDecision ? 0.7 : 1,
                }}
              >
                {evaluatingDecision ? (
                  <>
                    <RotateCcw className="spin" size={18} /> Evaluating Sequence...
                  </>
                ) : (
                  <>
                    <BrainCircuit size={18} /> Evaluate Decision Trigger
                  </>
                )}
              </button>
            </div>

            {/* Decision Result */}
            <div
              style={{
                backgroundColor: 'var(--bg-secondary)',
                borderRadius: '12px',
                border: '1px solid var(--border-color)',
                padding: '28px',
                display: 'flex',
                flexDirection: 'column',
                gap: '20px',
              }}
            >
              <h3 style={{ fontSize: '15px', fontWeight: '700' }}>Parsed Trigger Decision JSON</h3>

              {decisionResult?.parsed ? (
                <div>
                  <div
                    style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(3, 1fr)',
                      gap: '16px',
                      marginBottom: '24px',
                    }}
                  >
                    <div style={{ backgroundColor: 'var(--bg-card)', padding: '16px', borderRadius: '8px' }}>
                      <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Speak Trigger</span>
                      <p style={{ fontSize: '20px', fontWeight: '700', color: decisionResult.parsed.speak ? 'var(--accent-rose)' : 'var(--accent-emerald)' }}>
                        {decisionResult.parsed.speak ? 'SPEAK' : 'SILENT'}
                      </p>
                    </div>
                    <div style={{ backgroundColor: 'var(--bg-card)', padding: '16px', borderRadius: '8px' }}>
                      <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Event Kind</span>
                      <p style={{ fontSize: '20px', fontWeight: '700', color: 'var(--accent-cyan)' }}>
                        {decisionResult.parsed.event}
                      </p>
                    </div>
                    <div style={{ backgroundColor: 'var(--bg-card)', padding: '16px', borderRadius: '8px' }}>
                      <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Alert Level</span>
                      <p style={{ fontSize: '20px', fontWeight: '700', color: 'var(--accent-amber)' }}>
                        Level {decisionResult.parsed.level}
                      </p>
                    </div>
                  </div>

                  <h4 style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '8px' }}>
                    Raw LLM Response String:
                  </h4>
                  <pre
                    style={{
                      backgroundColor: 'var(--bg-card)',
                      padding: '16px',
                      borderRadius: '8px',
                      fontSize: '12px',
                      color: 'var(--accent-emerald)',
                      overflowX: 'auto',
                    }}
                  >
                    {decisionResult.raw_text}
                  </pre>
                </div>
              ) : decisionResult?.error ? (
                <div style={{ color: 'var(--accent-rose)' }}>{decisionResult.error}</div>
              ) : (
                <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '40px 0' }}>
                  <BrainCircuit size={48} style={{ opacity: 0.2, marginBottom: '12px' }} />
                  <p>Click "Evaluate Decision Trigger" to test LLM sequence reasoning.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ======================================================== */}
        {/* TAB 3: MADHYA PRADESH AQI TELEMETRY */}
        {/* ======================================================== */}
        {activeTab === 'telemetry' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div
              style={{
                backgroundColor: 'var(--bg-secondary)',
                borderRadius: '12px',
                border: '1px solid var(--border-color)',
                padding: '24px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <div>
                <h2 style={{ fontSize: '16px', fontWeight: '700' }}>Active Monitoring Station</h2>
                <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                  Browse real physical monitoring stations and statewide district models in Madhya Pradesh.
                </p>
              </div>

              <select
                value={selectedLoc}
                onChange={(e) => setSelectedLoc(e.target.value)}
                style={{
                  minWidth: '380px',
                  padding: '10px 14px',
                  borderRadius: '8px',
                  backgroundColor: 'var(--bg-card)',
                  border: '1px solid var(--border-color)',
                  color: 'var(--text-primary)',
                  fontSize: '13px',
                }}
              >
                {locations.map((loc) => (
                  <option key={loc.name} value={loc.name}>
                    {loc.name} ({loc.dataset_kind === 'measured_station' ? 'Physical Station' : 'Atmospheric Model'})
                  </option>
                ))}
              </select>
            </div>

            {/* Metrics Row */}
            {telemetry?.stats && (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
                <div style={{ backgroundColor: 'var(--bg-secondary)', padding: '20px', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
                  <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Telemetry Source</span>
                  <p style={{ fontSize: '18px', fontWeight: '700', color: telemetry.stats.dataset_kind === 'measured_station' ? 'var(--accent-emerald)' : 'var(--accent-cyan)' }}>
                    {telemetry.stats.dataset_kind === 'measured_station' ? 'Ground CAAQMS Station' : 'CAMS Reanalysis'}
                  </p>
                </div>
                <div style={{ backgroundColor: 'var(--bg-secondary)', padding: '20px', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
                  <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Mean PM2.5</span>
                  <p style={{ fontSize: '24px', fontWeight: '700' }}>
                    {telemetry.stats.mean_pm25 ?? 'N/A'} µg/m³
                  </p>
                </div>
                <div style={{ backgroundColor: 'var(--bg-secondary)', padding: '20px', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
                  <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Mean CPCB AQI</span>
                  <p style={{ fontSize: '24px', fontWeight: '700', color: getAQIColor(telemetry.stats.mean_aqi || 0) }}>
                    {telemetry.stats.mean_aqi ?? 'N/A'}
                  </p>
                </div>
                <div style={{ backgroundColor: 'var(--bg-secondary)', padding: '20px', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
                  <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Max Recorded AQI</span>
                  <p style={{ fontSize: '24px', fontWeight: '700', color: getAQIColor(telemetry.stats.max_aqi || 0) }}>
                    {telemetry.stats.max_aqi ?? 'N/A'}
                  </p>
                </div>
              </div>
            )}

            {/* Table of Records */}
            <div
              style={{
                backgroundColor: 'var(--bg-secondary)',
                borderRadius: '12px',
                border: '1px solid var(--border-color)',
                padding: '24px',
              }}
            >
              <h3 style={{ fontSize: '15px', fontWeight: '700', marginBottom: '16px' }}>
                Recent Hourly Readings ({telemetry?.records?.length || 0} observations)
              </h3>
              <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left', color: 'var(--text-muted)' }}>
                      <th style={{ padding: '10px' }}>Timestamp</th>
                      <th style={{ padding: '10px' }}>PM2.5 (µg/m³)</th>
                      <th style={{ padding: '10px' }}>PM10 (µg/m³)</th>
                      <th style={{ padding: '10px' }}>CPCB AQI</th>
                      <th style={{ padding: '10px' }}>Category</th>
                    </tr>
                  </thead>
                  <tbody>
                    {telemetry?.records?.slice(-30).reverse().map((r, i) => (
                      <tr key={i} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                        <td style={{ padding: '10px' }}>{r.dt}</td>
                        <td style={{ padding: '10px' }}>{r.pm2_5 ?? '-'}</td>
                        <td style={{ padding: '10px' }}>{r.pm10 ?? '-'}</td>
                        <td style={{ padding: '10px', fontWeight: '700', color: getAQIColor(r.cpcb_aqi || 0) }}>
                          {r.cpcb_aqi ?? '-'}
                        </td>
                        <td style={{ padding: '10px' }}>{r.cpcb_category}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* ======================================================== */}
        {/* TAB 4: PREGENERATED AUDIO CLIPS */}
        {/* ======================================================== */}
        {activeTab === 'clips' && (
          <div style={{ display: 'grid', gridTemplateColumns: '420px 1fr', gap: '32px' }}>
            <div
              style={{
                backgroundColor: 'var(--bg-secondary)',
                borderRadius: '12px',
                border: '1px solid var(--border-color)',
                padding: '24px',
                display: 'flex',
                flexDirection: 'column',
                gap: '20px',
              }}
            >
              <div>
                <h2 style={{ fontSize: '16px', fontWeight: '700', marginBottom: '6px' }}>
                  Deterministic Backup Clips
                </h2>
                <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                  AirCue pregenerates 200 production WAV audio clips with SHA-256 hashes for zero-latency network failover.
                </p>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '12px', marginBottom: '6px', color: 'var(--text-secondary)' }}>
                  Event Kind
                </label>
                <select
                  value={clipKind}
                  onChange={(e) => setClipKind(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    borderRadius: '6px',
                    backgroundColor: 'var(--bg-card)',
                    border: '1px solid var(--border-color)',
                    color: 'var(--text-primary)',
                    fontSize: '13px',
                  }}
                >
                  <option value="escalate">Escalate (Air quality worsened)</option>
                  <option value="reminder">Reminder (Ongoing high PM)</option>
                  <option value="improving">Improving (Partial recovery)</option>
                  <option value="recovered">Recovered (Air fresh again)</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '12px', marginBottom: '6px', color: 'var(--text-secondary)' }}>
                  Alert Level
                </label>
                <select
                  value={clipLevel}
                  onChange={(e) => setClipLevel(Number(e.target.value))}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    borderRadius: '6px',
                    backgroundColor: 'var(--bg-card)',
                    border: '1px solid var(--border-color)',
                    color: 'var(--text-primary)',
                    fontSize: '13px',
                  }}
                >
                  <option value={1}>Level 1 (Moderate)</option>
                  <option value={2}>Level 2 (Poor)</option>
                  <option value={3}>Level 3 (Very Poor)</option>
                  <option value={4}>Level 4 (Severe)</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '12px', marginBottom: '6px', color: 'var(--text-secondary)' }}>
                  Language
                </label>
                <select
                  value={clipLang}
                  onChange={(e) => setClipLang(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    borderRadius: '6px',
                    backgroundColor: 'var(--bg-card)',
                    border: '1px solid var(--border-color)',
                    color: 'var(--text-primary)',
                    fontSize: '13px',
                  }}
                >
                  <option value="hi">Hindi</option>
                  <option value="en">English</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '12px', marginBottom: '6px', color: 'var(--text-secondary)' }}>
                  Timetable Slot
                </label>
                <select
                  value={clipSlot}
                  onChange={(e) => setClipSlot(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    borderRadius: '6px',
                    backgroundColor: 'var(--bg-card)',
                    border: '1px solid var(--border-color)',
                    color: 'var(--text-primary)',
                    fontSize: '13px',
                  }}
                >
                  <option value="general">General</option>
                  <option value="sports_pt">Sports PT</option>
                  <option value="assembly">Assembly</option>
                  <option value="recess">Recess</option>
                  <option value="dismissal">Dismissal</option>
                </select>
              </div>

              <button
                type="button"
                onClick={handlePreviewClip}
                style={{
                  backgroundColor: 'var(--accent-emerald)',
                  color: '#0b0f19',
                  padding: '12px',
                  borderRadius: '8px',
                  fontWeight: '700',
                  fontSize: '14px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                }}
              >
                <Volume2 size={18} /> Resolve & Preview Audio Clip
              </button>
            </div>

            {/* Clip details */}
            <div
              style={{
                backgroundColor: 'var(--bg-secondary)',
                borderRadius: '12px',
                border: '1px solid var(--border-color)',
                padding: '28px',
              }}
            >
              <h3 style={{ fontSize: '15px', fontWeight: '700', marginBottom: '16px' }}>
                Clip Resolution Result
              </h3>
              {clipResult ? (
                <div>
                  <div style={{ backgroundColor: 'var(--bg-card)', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Clip Identifier</span>
                    <p style={{ fontSize: '18px', fontWeight: '700', color: 'var(--accent-cyan)', fontFamily: 'monospace' }}>
                      {clipResult.clip_id}.wav
                    </p>
                    <p style={{ fontSize: '16px', fontWeight: '500', color: '#fff', marginTop: '12px' }}>
                      "{clipResult.text}"
                    </p>
                  </div>

                  {clipResult.exists && clipResult.clip_url ? (
                    <div>
                      <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                        Audio Playback (Direct WAV stream from clips repository):
                      </p>
                      <audio controls src={`${API_BASE}${clipResult.clip_url}`} style={{ width: '100%' }} />
                    </div>
                  ) : (
                    <div style={{ color: 'var(--accent-amber)' }}>
                      Clip not pre-built in `clips/` directory. Run `aircue clips build`.
                    </div>
                  )}
                </div>
              ) : (
                <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '40px 0' }}>
                  <Volume2 size={48} style={{ opacity: 0.2, marginBottom: '12px' }} />
                  <p>Choose an event configuration to inspect resolved backup clip.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ======================================================== */}
        {/* TAB 5: BENCHMARK & QUOTA TRACKER */}
        {/* ======================================================== */}
        {activeTab === 'quota' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div
              style={{
                backgroundColor: 'var(--bg-secondary)',
                borderRadius: '12px',
                border: '1px solid var(--border-color)',
                padding: '24px',
              }}
            >
              <h2 style={{ fontSize: '16px', fontWeight: '700', marginBottom: '8px' }}>
                LLM Benchmark Quota & Budget Manager
              </h2>
              <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '20px' }}>
                Track daily request consumption to stay within OpenRouter rate limits.
              </p>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
                <div style={{ backgroundColor: 'var(--bg-card)', padding: '16px', borderRadius: '8px' }}>
                  <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Today's API Calls</span>
                  <p style={{ fontSize: '24px', fontWeight: '700', color: 'var(--accent-cyan)' }}>
                    {status?.quota?.['2026-11-21']?.calls || 0} / 180
                  </p>
                </div>
                <div style={{ backgroundColor: 'var(--bg-card)', padding: '16px', borderRadius: '8px' }}>
                  <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Cumulative Tokens Used</span>
                  <p style={{ fontSize: '24px', fontWeight: '700' }}>
                    {status?.quota?.['2026-11-21']?.total_tokens?.toLocaleString() || 0}
                  </p>
                </div>
                <div style={{ backgroundColor: 'var(--bg-card)', padding: '16px', borderRadius: '8px' }}>
                  <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Estimated Spend</span>
                  <p style={{ fontSize: '24px', fontWeight: '700', color: 'var(--accent-emerald)' }}>
                    $0.00 (Free / Low Cost Tier)
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer
        style={{
          borderTop: '1px solid var(--border-color)',
          backgroundColor: 'var(--bg-secondary)',
          padding: '16px 32px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontSize: '12px',
          color: 'var(--text-muted)',
        }}
      >
        <span>AirCue Major Project — Yusuf Malu Bhai Wala (PIEMR Indore)</span>
        <span>CPCB Outdoor Scales • OpenAQ v3 • OpenRouter AI</span>
      </footer>
    </div>
  );
}
