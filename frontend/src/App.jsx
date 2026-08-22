import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  Handle,
  Position,
  MarkerType
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import {
  Brain,
  Cpu,
  Compass,
  AlertTriangle,
  FileText,
  MessageSquare,
  ShieldCheck,
  Award,
  BookOpen,
  Search,
  CheckCircle2,
  XCircle,
  Clock,
  Sparkles,
  ExternalLink,
  ChevronRight,
  TrendingUp,
  GraduationCap,
  Layers,
  ArrowRight,
  Send,
  Zap,
  Lock,
  Flame,
  Check,
  X
} from 'lucide-react';
import './App.css';

const API_BASE_URL = 'http://localhost:8000/api';

// ---------------------------------------------------------------------------
// 1. Custom React Flow Course Node
// ---------------------------------------------------------------------------
const CustomCourseNode = ({ data, selected }) => {
  const isCompleted = data.status === 'COMPLETED';
  const isEnrolled = data.status === 'ENROLLED';
  const isBottleneck = data.is_bottleneck;

  let borderColor = 'rgba(59, 130, 246, 0.3)';
  let bgGradient = 'rgba(15, 23, 42, 0.95)';
  let statusBadge = (
    <span className="badge badge-blue">Available</span>
  );

  if (isCompleted) {
    borderColor = '#10b981';
    bgGradient = 'rgba(6, 78, 59, 0.35)';
    statusBadge = <span className="badge badge-emerald"><Check size={10} /> Done</span>;
  } else if (isEnrolled) {
    borderColor = '#06b6d4';
    bgGradient = 'rgba(8, 51, 68, 0.45)';
    statusBadge = <span className="badge badge-cyan"><Clock size={10} /> Enrolled</span>;
  }

  return (
    <div
      style={{
        width: '260px',
        padding: '12px 14px',
        borderRadius: '10px',
        border: `1.5px solid ${selected ? '#38bdf8' : borderColor}`,
        background: bgGradient,
        backdropFilter: 'blur(8px)',
        color: '#f8fafc',
        boxShadow: selected
          ? '0 0 24px rgba(56, 189, 248, 0.5)'
          : isEnrolled
          ? '0 0 16px rgba(6, 182, 212, 0.25)'
          : '0 4px 16px rgba(0, 0, 0, 0.4)',
        transition: 'all 0.2s ease',
        cursor: 'pointer'
      }}
    >
      <Handle type="target" position={Position.Left} style={{ background: '#38bdf8', width: 8, height: 8 }} />

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
        <span style={{ fontSize: '11px', fontWeight: 700, color: '#38bdf8', letterSpacing: '0.05em' }}>
          {data.subject_id}
        </span>
        <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
          {isBottleneck && (
            <span className="badge badge-amber" title="Critical Gateway Node">
              <Flame size={10} /> Gateway
            </span>
          )}
          {statusBadge}
        </div>
      </div>

      <div style={{ fontSize: '13px', fontWeight: 600, lineHeight: '1.35', marginBottom: '8px', minHeight: '34px' }}>
        {data.label}
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: '6px', fontSize: '11px', color: '#94a3b8' }}>
        <span>Sem {data.semester}</span>
        <span style={{ fontWeight: 600, color: '#f8fafc' }}>{data.credits} Credits</span>
      </div>

      <Handle type="source" position={Position.Right} style={{ background: '#38bdf8', width: 8, height: 8 }} />
    </div>
  );
};

const nodeTypes = {
  customCourseNode: CustomCourseNode
};

// ---------------------------------------------------------------------------
// 2. Main App Component
// ---------------------------------------------------------------------------
export default function App() {
  // Navigation & View States
  const [loading, setLoading] = useState(true);
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [currentView, setCurrentView] = useState('login'); // 'login' | 'dashboard'
  const [activeTab, setActiveTab] = useState('graph'); // 'graph' | 'multiagent' | 'pathway' | 'conflicts' | 'vector' | 'chat' | 'faculty'
  const [portalMode, setPortalMode] = useState('student'); // 'student' | 'faculty'

  // Student State
  const [studentsList, setStudentsList] = useState([]);
  const [selectedStudentId, setSelectedStudentId] = useState('REG1001');
  const [customRegInput, setCustomRegInput] = useState('');
  const [studentData, setStudentData] = useState(null);

  // Multi-Agent Pipeline Data
  const [pipelineResult, setPipelineResult] = useState(null);
  const [isPipelineRunning, setIsPipelineRunning] = useState(false);

  // Graph Data
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNodeData, setSelectedNodeData] = useState(null);
  const [nodeSubstitutions, setNodeSubstitutions] = useState([]);

  // Chat State
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [isChatSending, setIsChatSending] = useState(false);

  // Faculty Petitions State
  const [petitionsList, setPetitionsList] = useState([]);
  const [isPetitionModalOpen, setIsPetitionModalOpen] = useState(false);
  const [petitionSubjectId, setPetitionSubjectId] = useState('Sub_4_2');
  const [petitionType, setPetitionType] = useState('PREREQUISITE_WAIVER');
  const [petitionReason, setPetitionReason] = useState('');
  const [facultyRemarks, setFacultyRemarks] = useState('');
  const [activePetitionActionId, setActivePetitionActionId] = useState(null);

  // Policy Modal
  const [activePolicyModal, setActivePolicyModal] = useState(null);

  // -------------------------------------------------------------------------
  // Initial Boot & Loading Screen Animation
  // -------------------------------------------------------------------------
  useEffect(() => {
    const interval = setInterval(() => {
      setLoadingProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setTimeout(() => setLoading(false), 400);
          return 100;
        }
        return prev + 20;
      });
    }, 150);

    fetchStudents();
    return () => clearInterval(interval);
  }, []);

  // -------------------------------------------------------------------------
  // API Fetch Functions
  // -------------------------------------------------------------------------
  const fetchStudents = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/students`);
      if (res.ok) {
        const data = await res.json();
        setStudentsList(data.students || []);
      }
    } catch (err) {
      console.warn('Backend not yet reachable, using offline mock data.');
    }
  };

  const loadStudentSession = async (regNo) => {
    setSelectedStudentId(regNo);
    setIsPipelineRunning(true);
    try {
      // 1. Fetch Student Profile
      const stRes = await fetch(`${API_BASE_URL}/students/${regNo}`);
      if (stRes.ok) {
        const stData = await stRes.json();
        setStudentData(stData.student);
      }

      // 2. Fetch Curriculum Graph with Student Overlay
      const graphRes = await fetch(`${API_BASE_URL}/graph/curriculum?student_id=${regNo}`);
      if (graphRes.ok) {
        const gData = await graphRes.json();
        setNodes(gData.nodes || []);
        setEdges(gData.edges || []);
      }

      // 3. Trigger Full Multi-Agent Pipeline
      const pipeRes = await fetch(`${API_BASE_URL}/advising/pipeline`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ student_id: regNo })
      });
      if (pipeRes.ok) {
        const pData = await pipeRes.json();
        setPipelineResult(pData);
        // Seed initial chat greetings
        setChatMessages([
          {
            sender: 'Nexus Advisor',
            text: `Hello ${pData.student_name}! I'm Nexus, your academic advisor. I have analyzed your ${pData.career_goal} progression roadmap with verified curriculum citations. What can I assist you with today?`,
            citations: pData.citations
          }
        ]);
      }

      // 4. Fetch Petitions
      fetchPetitions(regNo);
    } catch (err) {
      console.error('Error running advising pipeline:', err);
    } finally {
      setIsPipelineRunning(false);
    }
  };

  const fetchPetitions = async (regNo) => {
    try {
      const url = portalMode === 'faculty'
        ? `${API_BASE_URL}/faculty/petitions`
        : `${API_BASE_URL}/faculty/petitions?reg_no=${regNo}`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setPetitionsList(data.petitions || []);
      }
    } catch (err) {
      console.error('Error fetching petitions:', err);
    }
  };

  // Node Click Inspector
  const onNodeClick = async (event, node) => {
    setSelectedNodeData(node.data);
    try {
      const res = await fetch(`${API_BASE_URL}/substitutions/${node.data.subject_id}`);
      if (res.ok) {
        const data = await res.json();
        setNodeSubstitutions(data.substitutions || []);
      }
    } catch (err) {
      setNodeSubstitutions([]);
    }
  };

  // Chat Send Handler
  const handleSendChat = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userMsg = chatInput;
    setChatMessages((prev) => [...prev, { sender: 'Student', text: userMsg }]);
    setChatInput('');
    setIsChatSending(true);

    try {
      const res = await fetch(`${API_BASE_URL}/advising/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ student_id: selectedStudentId, message: userMsg })
      });
      if (res.ok) {
        const data = await res.json();
        setChatMessages((prev) => [
          ...prev,
          { sender: 'Nexus Advisor', text: data.reply, citations: data.citations }
        ]);
      }
    } catch (err) {
      setChatMessages((prev) => [
        ...prev,
        { sender: 'Nexus Advisor', text: 'Error connecting to Nexus advising core. Please retry.' }
      ]);
    } finally {
      setIsChatSending(false);
    }
  };

  // Submit Faculty Petition
  const handleSubmitPetition = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE_URL}/faculty/petitions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          reg_no: selectedStudentId,
          subject_id: petitionSubjectId,
          petition_type: petitionType,
          reason: petitionReason
        })
      });
      if (res.ok) {
        setIsPetitionModalOpen(false);
        setPetitionReason('');
        fetchPetitions(selectedStudentId);
      }
    } catch (err) {
      console.error('Error submitting petition:', err);
    }
  };

  // Action Faculty Petition (Approve/Reject)
  const handleFacultyAction = async (petitionId, action) => {
    try {
      const res = await fetch(`${API_BASE_URL}/faculty/petitions/${petitionId}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action,
          faculty_remarks: facultyRemarks || `Action executed by Faculty Advisor.`
        })
      });
      if (res.ok) {
        setActivePetitionActionId(null);
        setFacultyRemarks('');
        fetchPetitions(selectedStudentId);
      }
    } catch (err) {
      console.error('Error taking faculty action:', err);
    }
  };

  // Open Policy Details Modal
  const openPolicyCitation = async (citationCode) => {
    try {
      const res = await fetch(`${API_BASE_URL}/policies/search?query=${encodeURIComponent(citationCode)}`);
      if (res.ok) {
        const data = await res.json();
        if (data.citations && data.citations.length > 0) {
          setActivePolicyModal(data.citations[0]);
        }
      }
    } catch (err) {
      setActivePolicyModal({
        citation_code: citationCode,
        title: 'Academic Policy Grounding Clause',
        relevance_snippet: 'This requirement is formally enforced under university catalog regulations.'
      });
    }
  };

  // -------------------------------------------------------------------------
  // RENDER: 1. Loading Screen
  // -------------------------------------------------------------------------
  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: '#0a0d14', color: '#f8fafc', padding: '24px' }}>
        <div style={{ position: 'relative', width: '120px', height: '120px', marginBottom: '32px' }}>
          <div style={{ position: 'absolute', inset: 0, borderRadius: '50%', border: '2px solid rgba(6,182,212,0.2)', borderTopColor: '#06b6d4', animation: 'spin 1.2s linear infinite' }}></div>
          <div style={{ position: 'absolute', inset: '16px', borderRadius: '50%', border: '2px solid rgba(168,85,247,0.2)', borderBottomColor: '#a855f7', animation: 'spin 1.8s linear infinite reverse' }}></div>
          <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Brain size={42} color="#38bdf8" />
          </div>
        </div>

        <h1 style={{ fontSize: '28px', fontWeight: 800, letterSpacing: '-0.03em', marginBottom: '8px' }}>
          <span style={{ color: '#06b6d4' }}>Omega</span> — Academic Pathway Intelligence
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '14px', marginBottom: '24px' }}>
          Initializing Decentralized Graph-RAG & Prerequisite Multi-Agent Cores...
        </p>

        <div style={{ width: '320px', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '9999px', overflow: 'hidden' }}>
          <div style={{ width: `${loadingProgress}%`, height: '100%', background: 'linear-gradient(90deg, #06b6d4, #3b82f6, #a855f7)', transition: 'width 0.2s ease' }}></div>
        </div>
        <span style={{ fontSize: '12px', color: '#64748b', marginTop: '8px', fontFamily: 'monospace' }}>
          {loadingProgress}% SYSTEM INTEGRITY VERIFIED
        </span>
      </div>
    );
  }

  // -------------------------------------------------------------------------
  // RENDER: 2. Login & Student Selection Screen
  // -------------------------------------------------------------------------
  if (currentView === 'login') {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '32px 16px', background: '#0a0d14' }}>
        <div style={{ maxWidth: '980px', width: '100%' }}>
          {/* Header */}
          <div style={{ textAlign: 'center', marginBottom: '36px' }}>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '6px 14px', borderRadius: '9999px', background: 'rgba(6,182,212,0.1)', border: '1px solid rgba(6,182,212,0.3)', color: '#22d3ee', fontSize: '12px', fontWeight: 600, marginBottom: '16px' }}>
              <Sparkles size={14} /> AUTONOMOUS MULTI-AGENT ADVISING PLATFORM
            </div>
            <h1 style={{ fontSize: '38px', fontWeight: 800, letterSpacing: '-0.03em', color: '#f8fafc', marginBottom: '10px' }}>
              <span style={{ color: '#06b6d4' }}>Omega</span> Pathway Intelligence
            </h1>
            <p style={{ color: '#94a3b8', fontSize: '16px', maxWidth: '640px', margin: '0 auto' }}>
              Decentralized Graph-RAG Academic Advising, Prerequisite Conflict Resolution & Faculty Governance Portal.
            </p>
          </div>

          {/* Mode Switcher */}
          <div style={{ display: 'flex', justifyContent: 'center', gap: '12px', marginBottom: '28px' }}>
            <button
              onClick={() => setPortalMode('student')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 20px',
                borderRadius: '8px',
                border: portalMode === 'student' ? '1.5px solid #06b6d4' : '1px solid rgba(255,255,255,0.1)',
                background: portalMode === 'student' ? 'rgba(6,182,212,0.15)' : 'rgba(15,23,42,0.6)',
                color: portalMode === 'student' ? '#22d3ee' : '#94a3b8',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              <GraduationCap size={18} /> Student Advising View
            </button>
            <button
              onClick={() => setPortalMode('faculty')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 20px',
                borderRadius: '8px',
                border: portalMode === 'faculty' ? '1.5px solid #a855f7' : '1px solid rgba(255,255,255,0.1)',
                background: portalMode === 'faculty' ? 'rgba(168,85,247,0.15)' : 'rgba(15,23,42,0.6)',
                color: portalMode === 'faculty' ? '#c084fc' : '#94a3b8',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              <ShieldCheck size={18} /> Faculty Override Portal
            </button>
          </div>

          {/* Student Selector Card */}
          <div className="glass-panel" style={{ padding: '28px', marginBottom: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <div>
                <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#f8fafc' }}>
                  {portalMode === 'student' ? 'Select Student Profile' : 'Faculty Audit Target'}
                </h3>
                <p style={{ fontSize: '13px', color: '#94a3b8' }}>
                  Choose from 50 simulated profiles across 4 semesters and 10 tech specializations.
                </p>
              </div>

              {/* Direct RegNo Input */}
              <div style={{ display: 'flex', gap: '8px' }}>
                <input
                  type="text"
                  placeholder="e.g. REG1004"
                  value={customRegInput}
                  onChange={(e) => setCustomRegInput(e.target.value.toUpperCase())}
                  style={{
                    padding: '8px 12px',
                    borderRadius: '6px',
                    border: '1px solid rgba(59,130,246,0.3)',
                    background: 'rgba(15,23,42,0.8)',
                    color: '#f8fafc',
                    fontSize: '13px',
                    outline: 'none'
                  }}
                />
                <button
                  onClick={() => {
                    const id = customRegInput || selectedStudentId;
                    loadStudentSession(id);
                    setCurrentView('dashboard');
                  }}
                  style={{
                    padding: '8px 16px',
                    borderRadius: '6px',
                    background: 'linear-gradient(135deg, #06b6d4, #3b82f6)',
                    color: '#f8fafc',
                    fontWeight: 600,
                    border: 'none',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}
                >
                  Enter Session <ArrowRight size={14} />
                </button>
              </div>
            </div>

            {/* Quick Demo Cards Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '14px' }}>
              {studentsList.slice(0, 6).map((st) => (
                <div
                  key={st.RegNo}
                  className="glass-card-interactive"
                  onClick={() => {
                    setSelectedStudentId(st.RegNo);
                    loadStudentSession(st.RegNo);
                    setCurrentView('dashboard');
                  }}
                  style={{
                    padding: '16px',
                    border: selectedStudentId === st.RegNo ? '1.5px solid #06b6d4' : '1px solid rgba(59,130,246,0.15)'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span style={{ fontSize: '12px', fontWeight: 700, color: '#38bdf8', fontFamily: 'monospace' }}>
                      {st.RegNo || st.reg_no}
                    </span>
                    <span className="badge badge-cyan">Sem {st.Semester || st.semester}</span>
                  </div>
                  <div style={{ fontSize: '15px', fontWeight: 700, color: '#f8fafc', marginBottom: '4px' }}>
                    {st.StudentName || st.student_name}
                  </div>
                  <div style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '10px' }}>
                    🎯 {st.Goal || st.goal || st.career_goal}
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '8px' }}>
                    <span style={{ fontSize: '12px', color: '#94a3b8' }}>Cumulative GPA</span>
                    <span style={{ fontSize: '13px', fontWeight: 700, color: (st.CGPA ?? st.cgpa ?? st.current_gpa ?? 7.5) >= 8.5 ? '#34d399' : (st.CGPA ?? st.cgpa ?? st.current_gpa ?? 7.5) < 6.0 ? '#fb7185' : '#38bdf8' }}>
                      {Number(st.CGPA ?? st.cgpa ?? st.current_gpa ?? 7.5).toFixed(2)} / 10.00
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // -------------------------------------------------------------------------
  // RENDER: 3. Main Dashboard Command Center
  // -------------------------------------------------------------------------
  return (
    <div className="app-container">
      {/* Top Navbar */}
      <header className="glass-panel" style={{ borderRadius: 0, borderTop: 0, borderLeft: 0, borderRight: 0, padding: '12px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', position: 'sticky', top: 0, zIndex: 50 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div
            onClick={() => setCurrentView('login')}
            style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}
          >
            <Brain size={26} color="#06b6d4" />
            <span style={{ fontSize: '18px', fontWeight: 800, letterSpacing: '-0.02em', color: '#f8fafc' }}>
              <span style={{ color: '#06b6d4' }}>Omega</span> Advisor
            </span>
          </div>

          <div style={{ height: '24px', width: '1px', background: 'rgba(255,255,255,0.1)' }}></div>

          {/* Student Profile Quick Badge */}
          {pipelineResult && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div>
                <span style={{ fontSize: '14px', fontWeight: 700, color: '#f8fafc' }}>
                  {pipelineResult.student_name}
                </span>
                <span style={{ fontSize: '12px', color: '#38bdf8', marginLeft: '6px', fontFamily: 'monospace' }}>
                  ({pipelineResult.student_id})
                </span>
              </div>

              <span className="badge badge-cyan">Sem {pipelineResult.current_semester}</span>
              <span className={`badge ${pipelineResult.cgpa >= 8.5 ? 'badge-emerald' : pipelineResult.cgpa < 6.0 ? 'badge-rose' : 'badge-blue'}`}>
                GPA {pipelineResult.cgpa.toFixed(2)}
              </span>
              <span className="badge badge-purple">{pipelineResult.career_goal}</span>
            </div>
          )}
        </div>

        {/* Tab Navigation Controls */}
        <div style={{ display: 'flex', gap: '6px' }}>
          {[
            { id: 'graph', label: 'Knowledge Graph', icon: <Compass size={15} /> },
            { id: 'multiagent', label: 'Agent Center', icon: <Cpu size={15} /> },
            { id: 'pathway', label: 'Degree Pathway', icon: <Layers size={15} /> },
            { id: 'conflicts', label: 'Conflict Resolver', icon: <AlertTriangle size={15} /> },
            { id: 'vector', label: 'Career Velocity', icon: <TrendingUp size={15} /> },
            { id: 'chat', label: 'Advisor Chat', icon: <MessageSquare size={15} /> },
            { id: 'faculty', label: 'Faculty Portal', icon: <ShieldCheck size={15} /> }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '8px 14px',
                borderRadius: '6px',
                border: activeTab === tab.id ? '1px solid #06b6d4' : '1px solid transparent',
                background: activeTab === tab.id ? 'rgba(6,182,212,0.15)' : 'transparent',
                color: activeTab === tab.id ? '#22d3ee' : '#94a3b8',
                fontSize: '13px',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.15s ease'
              }}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>
      </header>

      {/* Main Content Area */}
      <main style={{ flex: 1, padding: '20px 24px', display: 'flex', flexDirection: 'column' }}>
        {/* =================================================================== */}
        {/* TAB 1: KNOWLEDGE GRAPH VISUALIZER (REACT FLOW)                      */}
        {/* =================================================================== */}
        {activeTab === 'graph' && (
          <div style={{ display: 'flex', gap: '20px', height: 'calc(100vh - 120px)' }}>
            {/* React Flow Graph Canvas */}
            <div className="glass-panel" style={{ flex: 1, position: 'relative', overflow: 'hidden' }}>
              <ReactFlow
                nodes={nodes}
                edges={edges}
                nodeTypes={nodeTypes}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onNodeClick={onNodeClick}
                fitView
                attributionPosition="bottom-left"
              >
                <Background color="#1e293b" gap={24} size={1.5} />
                <Controls />
                <MiniMap
                  nodeStrokeColor="#38bdf8"
                  nodeColor="#1e293b"
                  nodeBorderRadius={2}
                />
              </ReactFlow>

              {/* Semester Column Headers Floating Banner */}
              <div style={{ position: 'absolute', top: 14, left: 50, right: 50, display: 'flex', justifyContent: 'space-around', pointerEvents: 'none' }}>
                {['Semester 1 (Foundations)', 'Semester 2 (Core CS)', 'Semester 3 (Advanced Systems)', 'Semester 4 (Specializations)'].map((semLabel, idx) => (
                  <div key={idx} style={{ background: 'rgba(15,23,42,0.85)', backdropFilter: 'blur(8px)', border: '1px solid rgba(59,130,246,0.3)', padding: '6px 16px', borderRadius: '20px', fontSize: '12px', fontWeight: 700, color: '#38bdf8' }}>
                    {semLabel}
                  </div>
                ))}
              </div>
            </div>

            {/* Selected Node Inspector Sidepanel */}
            <div className="glass-panel" style={{ width: '340px', padding: '20px', display: 'flex', flexDirection: 'column' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#f8fafc', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Brain size={18} color="#06b6d4" /> Course Inspector
              </h3>

              {selectedNodeData ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                  <div style={{ background: 'rgba(15,23,42,0.8)', padding: '14px', borderRadius: '8px', border: '1px solid rgba(59,130,246,0.2)' }}>
                    <span style={{ fontSize: '12px', fontWeight: 700, color: '#38bdf8' }}>
                      {selectedNodeData.subject_id}
                    </span>
                    <h4 style={{ fontSize: '15px', fontWeight: 700, color: '#f8fafc', marginTop: '4px', marginBottom: '8px' }}>
                      {selectedNodeData.label}
                    </h4>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <span className="badge badge-blue">Sem {selectedNodeData.semester}</span>
                      <span className="badge badge-cyan">{selectedNodeData.credits} Credits</span>
                      <span className="badge badge-emerald">{selectedNodeData.status}</span>
                    </div>
                  </div>

                  {/* Course Equivalences & Substitutions */}
                  <div>
                    <h5 style={{ fontSize: '13px', fontWeight: 700, color: '#94a3b8', marginBottom: '8px' }}>
                      Approved Course Substitutions:
                    </h5>
                    {nodeSubstitutions.length > 0 ? (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        {nodeSubstitutions.map((sub, sidx) => (
                          <div key={sidx} style={{ background: 'rgba(15,23,42,0.6)', padding: '10px', borderRadius: '6px', border: '1px solid rgba(168,85,247,0.3)', fontSize: '12px' }}>
                            <div style={{ fontWeight: 600, color: '#c084fc' }}>
                              🔄 {sub.EquivalentSubjectID}: {sub.EquivalentName}
                            </div>
                            <span style={{ fontSize: '11px', color: '#64748b' }}>
                              Type: {sub.EquivalenceType}
                            </span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p style={{ fontSize: '12px', color: '#64748b' }}>
                        No special elective substitution rules configured. Standard prerequisite chain applies.
                      </p>
                    )}
                  </div>

                  {/* 1-Click Waiver Petition Trigger */}
                  <button
                    onClick={() => {
                      setPetitionSubjectId(selectedNodeData.subject_id);
                      setIsPetitionModalOpen(true);
                    }}
                    style={{
                      marginTop: 'auto',
                      padding: '10px',
                      borderRadius: '8px',
                      background: 'rgba(168,85,247,0.15)',
                      border: '1px solid rgba(168,85,247,0.4)',
                      color: '#c084fc',
                      fontSize: '13px',
                      fontWeight: 600,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '8px'
                    }}
                  >
                    <ShieldCheck size={16} /> Petition Prerequisite Waiver
                  </button>
                </div>
              ) : (
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: '#64748b', textAlign: 'center' }}>
                  <Compass size={36} style={{ marginBottom: '10px', opacity: 0.5 }} />
                  <p style={{ fontSize: '13px' }}>
                    Click any course node on the Knowledge Graph to inspect prerequisite chains, credits, and substitutions.
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* =================================================================== */}
        {/* TAB 2: MULTI-AGENT TELEMETRY COMMAND CENTER                         */}
        {/* =================================================================== */}
        {activeTab === 'multiagent' && pipelineResult && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {/* Live Agents Status Row */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '14px' }}>
              {[
                { name: 'Agent 1: Nexus', role: 'Front Desk & Supervisor', status: 'ACTIVE', color: '#06b6d4' },
                { name: 'Agent 4: State', role: 'DBMS Synthesizer', status: 'SYNTHESIZED', color: '#10b981' },
                { name: 'Agent 2: The Matrix', role: 'Graph Pathfinder', status: 'OPTIMIZED', color: '#3b82f6' },
                { name: 'Agent 3: Vector', role: 'Career Velocity', status: 'MAPPED', color: '#f59e0b' },
                { name: 'Agent 5: Codex', role: 'Graph-RAG Policy', status: 'GROUNDED', color: '#a855f7' },
                { name: 'Agent 6: Sentinel', role: 'Constraint Verifier', status: 'AUDITED', color: '#10b981' }
              ].map((ag, aidx) => (
                <div key={aidx} className="glass-panel" style={{ padding: '16px', position: 'relative' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: ag.color, boxShadow: `0 0 10px ${ag.color}` }}></div>
                    <span style={{ fontSize: '10px', fontWeight: 700, color: ag.color, fontFamily: 'monospace' }}>
                      {ag.status}
                    </span>
                  </div>
                  <div style={{ fontSize: '14px', fontWeight: 700, color: '#f8fafc' }}>{ag.name}</div>
                  <div style={{ fontSize: '11px', color: '#94a3b8' }}>{ag.role}</div>
                </div>
              ))}
            </div>

            {/* Telemetry Execution Log Table */}
            <div className="glass-panel" style={{ padding: '24px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#f8fafc', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Cpu size={18} color="#38bdf8" /> Real-Time Multi-Agent Execution Telemetry
              </h3>

              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', textAlign: 'left' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', color: '#94a3b8' }}>
                      <th style={{ padding: '10px' }}>Agent Module</th>
                      <th style={{ padding: '10px' }}>Operational Action</th>
                      <th style={{ padding: '10px' }}>Duration</th>
                      <th style={{ padding: '10px' }}>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {pipelineResult.agent_telemetry.map((t, tidx) => (
                      <tr key={tidx} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                        <td style={{ padding: '12px 10px', fontWeight: 600, color: '#f8fafc' }}>{t.agent}</td>
                        <td style={{ padding: '12px 10px', color: '#cbd5e1' }}>{t.action}</td>
                        <td style={{ padding: '12px 10px', color: '#38bdf8', fontFamily: 'monospace' }}>{t.duration_ms} ms</td>
                        <td style={{ padding: '12px 10px' }}>
                          <span className="badge badge-emerald"><Check size={10} /> {t.status}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Synthesized Briefing Output */}
            <div className="glass-panel" style={{ padding: '24px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#f8fafc', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <FileText size={18} color="#06b6d4" /> Comprehensive Multi-Agent Advising Briefing
              </h3>
              <div style={{ whiteSpace: 'pre-line', color: '#cbd5e1', fontSize: '14px', lineHeight: '1.7' }}>
                {pipelineResult.advising_narrative}
              </div>
            </div>
          </div>
        )}

        {/* =================================================================== */}
        {/* TAB 3: DEGREE PATHWAY PLANNER                                       */}
        {/* =================================================================== */}
        {activeTab === 'pathway' && pipelineResult && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div className="glass-panel" style={{ padding: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <div>
                  <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#f8fafc' }}>
                    Topological Degree Pathway to Graduation
                  </h3>
                  <p style={{ fontSize: '13px', color: '#94a3b8' }}>
                    Generated by Agent 2 (The Matrix) respecting all prerequisite dependencies and 20-credit balancing rules.
                  </p>
                </div>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <span className="badge badge-cyan">{pipelineResult.degree_pathway.total_steps_required} Remaining Terms</span>
                  <span className="badge badge-emerald">Conflict-Free</span>
                </div>
              </div>

              {/* Pathway Sequence Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
                {pipelineResult.degree_pathway.path_sequence.map((step) => (
                  <div key={step.step_number} className="glass-panel" style={{ padding: '18px', border: '1.5px solid rgba(59,130,246,0.3)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                      <span style={{ fontSize: '15px', fontWeight: 700, color: '#38bdf8' }}>
                        {step.step_label}
                      </span>
                      <span className="badge badge-purple">{step.step_total_credits_or_effort} Credits</span>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      {step.nodes_details && step.nodes_details.length > 0 ? (
                        step.nodes_details.map((node, nidx) => (
                          <div key={nidx} style={{ background: 'rgba(15,23,42,0.8)', padding: '10px 12px', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.06)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div>
                              <div style={{ fontSize: '13px', fontWeight: 600, color: '#f8fafc' }}>
                                {node.name}
                              </div>
                              <span style={{ fontSize: '11px', color: '#94a3b8', fontFamily: 'monospace' }}>
                                {node.subject_id}
                              </span>
                            </div>
                            <span style={{ fontSize: '12px', fontWeight: 700, color: '#38bdf8' }}>
                              {node.credits} CR
                            </span>
                          </div>
                        ))
                      ) : (
                        step.nodes_to_complete.map((nid, nidx) => (
                          <div key={nidx} style={{ background: 'rgba(15,23,42,0.8)', padding: '8px 12px', borderRadius: '6px', fontSize: '13px', color: '#f8fafc' }}>
                            {nid}
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* =================================================================== */}
        {/* TAB 4: CONFLICT RESOLVER & DIAGNOSTICS CENTER                      */}
        {/* =================================================================== */}
        {activeTab === 'conflicts' && pipelineResult && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div className="glass-panel" style={{ padding: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <div>
                  <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <AlertTriangle size={20} color="#f59e0b" /> Formal Constraint Diagnostics & Conflict Resolver
                  </h3>
                  <p style={{ fontSize: '13px', color: '#94a3b8' }}>
                    Agent 6 (Sentinel) constraint verification matrix detecting unmet prerequisites, credit overloads, and risk factors.
                  </p>
                </div>

                {/* Risk Score Gauge Badge */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', background: 'rgba(15,23,42,0.8)', padding: '10px 18px', borderRadius: '10px', border: '1px solid rgba(59,130,246,0.3)' }}>
                  <div>
                    <div style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'uppercase' }}>Graduation Risk Score</div>
                    <div style={{ fontSize: '20px', fontWeight: 800, color: pipelineResult.conflict_report.graduation_risk_score > 0.4 ? '#fb7185' : '#34d399' }}>
                      {(pipelineResult.conflict_report.graduation_risk_score * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>
              </div>

              {/* Conflict Items List */}
              {pipelineResult.conflict_report.conflicts.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {pipelineResult.conflict_report.conflicts.map((conf) => (
                    <div
                      key={conf.conflict_id}
                      style={{
                        background: conf.severity === 'CRITICAL' ? 'rgba(159, 18, 57, 0.2)' : 'rgba(120, 53, 15, 0.2)',
                        border: `1.5px solid ${conf.severity === 'CRITICAL' ? '#f43f5e' : '#f59e0b'}`,
                        borderRadius: '8px',
                        padding: '16px'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                        <span style={{ fontSize: '13px', fontWeight: 700, color: conf.severity === 'CRITICAL' ? '#fb7185' : '#fbbf24' }}>
                          {conf.conflict_type}
                        </span>
                        <span className={`badge ${conf.severity === 'CRITICAL' ? 'badge-rose' : 'badge-amber'}`}>
                          {conf.severity}
                        </span>
                      </div>

                      <p style={{ fontSize: '14px', color: '#f8fafc', marginBottom: '8px' }}>
                        {conf.description}
                      </p>

                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '8px', fontSize: '12px' }}>
                        <span style={{ color: '#94a3b8' }}>
                          💡 <strong>Remedy:</strong> {conf.remedy_recommendation}
                        </span>
                        {conf.policy_citation && (
                          <span
                            onClick={() => openPolicyCitation(conf.policy_citation)}
                            style={{ color: '#38bdf8', cursor: 'pointer', textDecoration: 'underline' }}
                          >
                            {conf.policy_citation}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{ padding: '32px', textAlign: 'center', color: '#34d399' }}>
                  <CheckCircle2 size={42} style={{ margin: '0 auto 12px auto' }} />
                  <h4 style={{ fontSize: '16px', fontWeight: 700 }}>Zero Conflicts Detected</h4>
                  <p style={{ fontSize: '13px', color: '#94a3b8' }}>
                    All enrolled and upcoming course sequences strictly conform to catalog rules.
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* =================================================================== */}
        {/* TAB 5: CAREER VELOCITY (VECTOR ENGINE)                             */}
        {/* =================================================================== */}
        {activeTab === 'vector' && pipelineResult && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div className="glass-panel" style={{ padding: '24px' }}>
              <div style={{ marginBottom: '20px' }}>
                <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <TrendingUp size={20} color="#f59e0b" /> Strategic Career Momentum Blueprint
                </h3>
                <p style={{ fontSize: '13px', color: '#94a3b8' }}>
                  Generated by Agent 3 (Vector) tailored for <strong>{pipelineResult.career_goal}</strong> specialization.
                </p>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
                <div className="glass-panel" style={{ padding: '20px', border: '1px solid rgba(6,182,212,0.3)' }}>
                  <h4 style={{ fontSize: '15px', fontWeight: 700, color: '#22d3ee', marginBottom: '8px' }}>
                    🛠️ Actionable Project
                  </h4>
                  <p style={{ fontSize: '13px', color: '#cbd5e1', lineHeight: '1.6' }}>
                    {pipelineResult.career_vector.actionable_project}
                  </p>
                </div>

                <div className="glass-panel" style={{ padding: '20px', border: '1px solid rgba(59,130,246,0.3)' }}>
                  <h4 style={{ fontSize: '15px', fontWeight: 700, color: '#60a5fa', marginBottom: '8px' }}>
                    💼 Internship & Career Targets
                  </h4>
                  <p style={{ fontSize: '13px', color: '#cbd5e1', lineHeight: '1.6' }}>
                    {pipelineResult.career_vector.internship_target}
                  </p>
                </div>

                <div className="glass-panel" style={{ padding: '20px', border: '1px solid rgba(168,85,247,0.3)' }}>
                  <h4 style={{ fontSize: '15px', fontWeight: 700, color: '#c084fc', marginBottom: '8px' }}>
                    🏆 Next-Level Milestone
                  </h4>
                  <p style={{ fontSize: '13px', color: '#cbd5e1', lineHeight: '1.6' }}>
                    {pipelineResult.career_vector.next_level_milestone}
                  </p>
                </div>
              </div>

              {/* Recommended Certifications */}
              <div style={{ marginTop: '20px', background: 'rgba(15,23,42,0.6)', padding: '16px', borderRadius: '8px' }}>
                <h5 style={{ fontSize: '13px', fontWeight: 700, color: '#94a3b8', marginBottom: '10px' }}>
                  Target Industry Certifications:
                </h5>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                  {pipelineResult.career_vector.target_certifications.map((cert, cidx) => (
                    <span key={cidx} className="badge badge-cyan" style={{ padding: '6px 12px', fontSize: '12px' }}>
                      <Award size={13} /> {cert}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* =================================================================== */}
        {/* TAB 6: CITATION-TRACEABLE ADVISOR CHAT                             */}
        {/* =================================================================== */}
        {activeTab === 'chat' && (
          <div className="glass-panel" style={{ height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column' }}>
            {/* Chat Messages Log */}
            <div style={{ flex: 1, padding: '20px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {chatMessages.map((msg, midx) => (
                <div
                  key={midx}
                  style={{
                    alignSelf: msg.sender === 'Student' ? 'flex-end' : 'flex-start',
                    maxWidth: '80%',
                    background: msg.sender === 'Student' ? 'rgba(59,130,246,0.2)' : 'rgba(15,23,42,0.85)',
                    border: msg.sender === 'Student' ? '1px solid #3b82f6' : '1px solid rgba(59,130,246,0.2)',
                    borderRadius: '10px',
                    padding: '14px 16px'
                  }}
                >
                  <div style={{ fontSize: '11px', fontWeight: 700, color: msg.sender === 'Student' ? '#60a5fa' : '#22d3ee', marginBottom: '4px' }}>
                    {msg.sender}
                  </div>
                  <div style={{ fontSize: '14px', color: '#f8fafc', whiteSpace: 'pre-line', lineHeight: '1.5' }}>
                    {msg.text}
                  </div>

                  {/* Inline Citation Badges */}
                  {msg.citations && msg.citations.length > 0 && (
                    <div style={{ display: 'flex', gap: '6px', marginTop: '8px', flexWrap: 'wrap' }}>
                      {msg.citations.map((cite, cidx) => (
                        <span
                          key={cidx}
                          onClick={() => openPolicyCitation(cite)}
                          className="badge badge-purple"
                          style={{ cursor: 'pointer' }}
                        >
                          <BookOpen size={10} /> {cite}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
              {isChatSending && (
                <div style={{ alignSelf: 'flex-start', color: '#94a3b8', fontSize: '13px' }}>
                  Nexus Advisor is retrieving policy graphs...
                </div>
              )}
            </div>

            {/* Chat Input Bar */}
            <form onSubmit={handleSendChat} style={{ padding: '16px', borderTop: '1px solid rgba(255,255,255,0.08)', display: 'flex', gap: '10px' }}>
              <input
                type="text"
                placeholder="Ask about prerequisite waivers, overload policies, career recommendations..."
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                style={{
                  flex: 1,
                  padding: '12px 16px',
                  borderRadius: '8px',
                  border: '1px solid rgba(59,130,246,0.3)',
                  background: 'rgba(15,23,42,0.8)',
                  color: '#f8fafc',
                  fontSize: '14px',
                  outline: 'none'
                }}
              />
              <button
                type="submit"
                disabled={isChatSending}
                style={{
                  padding: '12px 20px',
                  borderRadius: '8px',
                  background: 'linear-gradient(135deg, #06b6d4, #3b82f6)',
                  color: '#f8fafc',
                  fontWeight: 600,
                  border: 'none',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}
              >
                <Send size={16} /> Send
              </button>
            </form>
          </div>
        )}

        {/* =================================================================== */}
        {/* TAB 7: FACULTY OVERRIDE & PETITION PORTAL                           */}
        {/* =================================================================== */}
        {activeTab === 'faculty' && (
          <div className="glass-panel" style={{ padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <div>
                <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <ShieldCheck size={20} color="#a855f7" /> Formal Faculty Exception & Waiver Review Portal
                </h3>
                <p style={{ fontSize: '13px', color: '#94a3b8' }}>
                  Review prerequisite waiver requests, credit overload petitions, and audit cryptographic approval hashes.
                </p>
              </div>

              <button
                onClick={() => setIsPetitionModalOpen(true)}
                style={{
                  padding: '8px 16px',
                  borderRadius: '6px',
                  background: 'linear-gradient(135deg, #a855f7, #6366f1)',
                  color: '#f8fafc',
                  fontWeight: 600,
                  border: 'none',
                  cursor: 'pointer'
                }}
              >
                + New Petition
              </button>
            </div>

            {/* Petitions Table */}
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', textAlign: 'left' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', color: '#94a3b8' }}>
                    <th style={{ padding: '10px' }}>Petition ID</th>
                    <th style={{ padding: '10px' }}>Student</th>
                    <th style={{ padding: '10px' }}>Type</th>
                    <th style={{ padding: '10px' }}>Subject</th>
                    <th style={{ padding: '10px' }}>Reason & Justification</th>
                    <th style={{ padding: '10px' }}>Status</th>
                    <th style={{ padding: '10px' }}>Audit Hash</th>
                    <th style={{ padding: '10px' }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {petitionsList.map((p) => (
                    <tr key={p.petition_id} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                      <td style={{ padding: '12px 10px', fontWeight: 700, color: '#38bdf8', fontFamily: 'monospace' }}>
                        {p.petition_id}
                      </td>
                      <td style={{ padding: '12px 10px', color: '#f8fafc' }}>
                        {p.student_name || p.reg_no}
                      </td>
                      <td style={{ padding: '12px 10px' }}>
                        <span className="badge badge-purple">{p.petition_type}</span>
                      </td>
                      <td style={{ padding: '12px 10px', color: '#cbd5e1' }}>
                        {p.subject_name || p.subject_id}
                      </td>
                      <td style={{ padding: '12px 10px', maxWidth: '280px', color: '#cbd5e1' }}>
                        {p.reason}
                        {p.faculty_remarks && (
                          <div style={{ fontSize: '11px', color: '#34d399', marginTop: '4px' }}>
                            📝 Remarks: {p.faculty_remarks}
                          </div>
                        )}
                      </td>
                      <td style={{ padding: '12px 10px' }}>
                        <span className={`badge ${p.status === 'APPROVED' ? 'badge-emerald' : p.status === 'REJECTED' ? 'badge-rose' : 'badge-amber'}`}>
                          {p.status}
                        </span>
                      </td>
                      <td style={{ padding: '12px 10px', fontFamily: 'monospace', fontSize: '10px', color: '#64748b' }}>
                        {p.audit_hash ? p.audit_hash.slice(0, 12) + '...' : 'N/A'}
                      </td>
                      <td style={{ padding: '12px 10px' }}>
                        {p.status === 'PENDING' && (
                          <div style={{ display: 'flex', gap: '6px' }}>
                            <button
                              onClick={() => handleFacultyAction(p.petition_id, 'APPROVE')}
                              style={{ padding: '4px 8px', borderRadius: '4px', background: 'rgba(16,185,129,0.2)', border: '1px solid #10b981', color: '#34d399', cursor: 'pointer', fontSize: '11px' }}
                            >
                              Approve
                            </button>
                            <button
                              onClick={() => handleFacultyAction(p.petition_id, 'REJECT')}
                              style={{ padding: '4px 8px', borderRadius: '4px', background: 'rgba(244,63,94,0.2)', border: '1px solid #f43f5e', color: '#fb7185', cursor: 'pointer', fontSize: '11px' }}
                            >
                              Reject
                            </button>
                          </div>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>

      {/* =================================================================== */}
      {/* MODAL: Submit New Faculty Petition                                  */}
      {/* =================================================================== */}
      {isPetitionModalOpen && (
        <div className="modal-backdrop" style={{ position: 'fixed', inset: 0, zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '16px' }}>
          <div className="glass-panel" style={{ maxWidth: '520px', width: '100%', padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#f8fafc' }}>
                Submit Formal Faculty Petition
              </h3>
              <button onClick={() => setIsPetitionModalOpen(false)} style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleSubmitPetition} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '4px', display: 'block' }}>Target Course</label>
                <input
                  type="text"
                  value={petitionSubjectId}
                  onChange={(e) => setPetitionSubjectId(e.target.value)}
                  style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid rgba(59,130,246,0.3)', background: 'rgba(15,23,42,0.8)', color: '#f8fafc', fontSize: '13px' }}
                />
              </div>

              <div>
                <label style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '4px', display: 'block' }}>Petition Type</label>
                <select
                  value={petitionType}
                  onChange={(e) => setPetitionType(e.target.value)}
                  style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid rgba(59,130,246,0.3)', background: 'rgba(15,23,42,0.8)', color: '#f8fafc', fontSize: '13px' }}
                >
                  <option value="PREREQUISITE_WAIVER">Prerequisite Waiver</option>
                  <option value="CREDIT_OVERLOAD">Credit Overload Exception</option>
                  <option value="COURSE_SUBSTITUTION">Course Substitution</option>
                  <option value="SPECIAL_PERMISSION">Special Department Permission</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '4px', display: 'block' }}>Academic Justification & Evidence</label>
                <textarea
                  rows={4}
                  required
                  placeholder="Describe your academic credentials, verified certificates, or rationale..."
                  value={petitionReason}
                  onChange={(e) => setPetitionReason(e.target.value)}
                  style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid rgba(59,130,246,0.3)', background: 'rgba(15,23,42,0.8)', color: '#f8fafc', fontSize: '13px', resize: 'vertical' }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '10px' }}>
                <button
                  type="button"
                  onClick={() => setIsPetitionModalOpen(false)}
                  style={{ padding: '8px 16px', borderRadius: '6px', background: 'transparent', border: '1px solid rgba(255,255,255,0.2)', color: '#94a3b8', cursor: 'pointer' }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{ padding: '8px 20px', borderRadius: '6px', background: 'linear-gradient(135deg, #a855f7, #3b82f6)', color: '#f8fafc', fontWeight: 600, border: 'none', cursor: 'pointer' }}
                >
                  Submit for Faculty Review
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* =================================================================== */}
      {/* MODAL: Policy Citation Details                                      */}
      {/* =================================================================== */}
      {activePolicyModal && (
        <div className="modal-backdrop" style={{ position: 'fixed', inset: 0, zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '16px' }}>
          <div className="glass-panel" style={{ maxWidth: '560px', width: '100%', padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <BookOpen size={18} color="#06b6d4" />
                <span style={{ fontSize: '12px', fontWeight: 700, color: '#38bdf8', fontFamily: 'monospace' }}>
                  {activePolicyModal.citation_code}
                </span>
              </div>
              <button onClick={() => setActivePolicyModal(null)} style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            <h3 style={{ fontSize: '17px', fontWeight: 700, color: '#f8fafc', marginBottom: '10px' }}>
              {activePolicyModal.title}
            </h3>

            <p style={{ fontSize: '14px', color: '#cbd5e1', lineHeight: '1.6', marginBottom: '18px' }}>
              {activePolicyModal.relevance_snippet}
            </p>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: '12px' }}>
              <span className="badge badge-cyan">{activePolicyModal.category || 'REGULATION'}</span>
              <button
                onClick={() => setActivePolicyModal(null)}
                style={{ padding: '6px 14px', borderRadius: '6px', background: 'rgba(59,130,246,0.2)', border: '1px solid #3b82f6', color: '#60a5fa', cursor: 'pointer', fontSize: '12px' }}
              >
                Close Policy
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
