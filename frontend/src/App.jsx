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
  X,
  Play,
  RotateCcw,
  Sliders,
  Filter,
  UserCheck,
  Hash,
  Activity,
  Terminal,
  Server,
  UserPlus,
  Target,
  Star,
  Gamepad2,
  Radio,
  Eye,
  SlidersHorizontal,
  Home
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
  let bgGradient = 'rgba(11, 16, 28, 0.96)';
  let statusBadge = <span className="badge badge-blue">Available</span>;

  if (isCompleted) {
    borderColor = '#10b981';
    bgGradient = 'rgba(6, 78, 59, 0.4)';
    statusBadge = <span className="badge badge-emerald"><Check size={10} /> Done</span>;
  } else if (isEnrolled) {
    borderColor = '#06b6d4';
    bgGradient = 'rgba(8, 51, 68, 0.5)';
    statusBadge = <span className="badge badge-cyan"><Clock size={10} /> Enrolled</span>;
  }

  return (
    <div
      style={{
        width: '270px',
        padding: '12px 14px',
        borderRadius: '12px',
        border: `1.5px solid ${selected ? '#38bdf8' : borderColor}`,
        background: bgGradient,
        backdropFilter: 'blur(10px)',
        color: '#f8fafc',
        boxShadow: selected
          ? '0 0 26px rgba(56, 189, 248, 0.6)'
          : isEnrolled
          ? '0 0 18px rgba(6, 182, 212, 0.35)'
          : '0 4px 16px rgba(0, 0, 0, 0.5)',
        transition: 'all 0.25s ease',
        cursor: 'pointer'
      }}
    >
      <Handle type="target" position={Position.Left} style={{ background: '#38bdf8', width: 8, height: 8 }} />

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
        <span style={{ fontSize: '11px', fontWeight: 800, color: '#38bdf8', letterSpacing: '0.05em' }}>
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

      <div style={{ fontSize: '13px', fontWeight: 700, color: '#f1f5f9', marginBottom: '8px', lineHeight: '1.3' }}>
        {data.label}
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '6px', fontSize: '11px', color: '#94a3b8' }}>
        <span>Semester {data.semester}</span>
        <span style={{ fontWeight: 800, color: '#cbd5e1' }}>{data.credits} Credits</span>
      </div>

      <Handle type="source" position={Position.Right} style={{ background: '#06b6d4', width: 8, height: 8 }} />
    </div>
  );
};

const nodeTypes = {
  customCourseNode: CustomCourseNode
};

// ---------------------------------------------------------------------------
// 2. Multi-Agent Metadata Directory with Mascot Avatars & Cozy Descriptions
// ---------------------------------------------------------------------------
const AGENTS_INFO = [
  {
    id: 'nexus',
    name: 'Nexus (Agent 01)',
    shortName: 'Nexus',
    role: 'Front Desk & Central Supervisor',
    desc: 'Coordinates the multi-agent council, routes intents, and creates the unified briefing.',
    color: '#06b6d4',
    icon: Brain,
    avatar: '/assets/nexus.png',
    tip: '✨ Nexus Tip: Ask me anything about prerequisite paths or credit overload eligibility!'
  },
  {
    id: 'state',
    name: 'State (Agent 04)',
    shortName: 'State',
    role: 'The Background Check Synthesizer',
    desc: 'Extracts verified student history from DBMS, scrubs PII, and assigns academic standing.',
    color: '#3b82f6',
    icon: ShieldCheck,
    avatar: '/assets/state.png',
    tip: '🛡️ State Tip: Your academic record is cryptographically verified with zero hallucinations.'
  },
  {
    id: 'matrix',
    name: 'The Matrix (Agent 02)',
    shortName: 'The Matrix',
    role: 'Graph Navigator & Degree Pathfinder',
    desc: 'Topologically sorts prerequisite dependencies to compute optimal graduation terms.',
    color: '#10b981',
    icon: Compass,
    avatar: '/assets/matrix.png',
    tip: '🧭 Matrix Tip: Prioritize Gateway chokepoints early to prevent graduation bottlenecks!'
  },
  {
    id: 'sentinel',
    name: 'Sentinel (Agent 06)',
    shortName: 'Sentinel',
    role: 'Formal Constraint & Faculty Verifier',
    desc: 'Audits credit bounds (12-24 CR), graduation risks, and manages SHA-256 faculty petitions.',
    color: '#f43f5e',
    icon: AlertTriangle,
    avatar: '/assets/sentinel.png',
    tip: '⚠️ Sentinel Tip: Credit overload up to 24 CR requires Honors standing (CGPA >= 8.5).'
  },
  {
    id: 'codex',
    name: 'Codex (Agent 05)',
    shortName: 'Codex',
    role: 'Graph-RAG Policy & Citation Engine',
    desc: 'Indexes university regulations to return verifiable, clause-level policy citations.',
    color: '#a855f7',
    icon: BookOpen,
    avatar: '/assets/codex.png',
    tip: '📜 Codex Tip: All advising statements are grounded in University Policy Articles.'
  },
  {
    id: 'vector',
    name: 'Vector (Agent 03)',
    shortName: 'Vector',
    role: 'Strategic Career Momentum Engine',
    desc: 'Tailors 10 industry career blueprints with actionable capstone projects and milestones.',
    color: '#f59e0b',
    icon: TrendingUp,
    avatar: '/assets/vector.png',
    tip: '🚀 Vector Tip: Complete target capstone projects early to maximize internship velocity!'
  }
];

const CAREER_OPTIONS = [
  'Data Scientist',
  'Software Engineer',
  'AI Researcher',
  'Cybersecurity Analyst',
  'Cloud Architect',
  'Machine Learning Engineer',
  'DevOps Engineer',
  'Full Stack Developer',
  'Systems Software Engineer',
  'Robotics & Embedded Systems Specialist'
];

export default function App() {
  // Navigation & View States
  const [currentView, setCurrentView] = useState('landing'); // 'landing' | 'login' | 'dashboard'
  const [activeTab, setActiveTab] = useState('graph'); // 'graph' | 'council' | 'sandbox' | 'quest' | 'pathway' | 'conflicts' | 'chat' | 'faculty'
  const [portalMode, setPortalMode] = useState('student'); // 'student' | 'faculty'

  // Typewriter text state for Landing Page
  const [typewriterText, setTypewriterText] = useState('');
  const fullTitle = 'OMEGA';

  // Student State
  const [selectedStudentId, setSelectedStudentId] = useState('REG1001');
  const [customRegInput, setCustomRegInput] = useState('');
  const [studentsList, setStudentsList] = useState([]);
  const [studentProfile, setStudentProfile] = useState(null);

  // Multi-Agent Pipeline Data
  const [pipelineData, setPipelineData] = useState(null);
  const [isPipelineRunning, setIsPipelineRunning] = useState(false);
  const [activeAgentIndex, setActiveAgentIndex] = useState(-1);
  const [selectedAgentCard, setSelectedAgentCard] = useState(AGENTS_INFO[0]);

  // React Flow State
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNodeData, setSelectedNodeData] = useState(null);
  const [graphFilter, setGraphFilter] = useState('ALL'); // 'ALL' | 'BOTTLENECKS' | 'ENROLLED'

  // Substitutions & Faculty Waiver Modal
  const [courseSubstitutions, setCourseSubstitutions] = useState([]);
  const [isWaiverModalOpen, setIsWaiverModalOpen] = useState(false);
  const [waiverCourseId, setWaiverCourseId] = useState('');
  const [waiverReason, setWaiverReason] = useState('');
  const [waiverType, setWaiverType] = useState('PREREQUISITE_WAIVER');
  const [facultyPetitions, setFacultyPetitions] = useState([]);
  const [facultyFilter, setFacultyFilter] = useState('ALL'); // 'ALL' | 'PENDING' | 'APPROVED' | 'REJECTED'

  // New Student Registration Modal State
  const [isRegisterModalOpen, setIsRegisterModalOpen] = useState(false);
  const [regFormName, setRegFormName] = useState('');
  const [regFormRegNo, setRegFormRegNo] = useState('REG2001');
  const [regFormSem, setRegFormSem] = useState(1);
  const [regFormCGPA, setRegFormCGPA] = useState(8.5);
  const [regFormGoal, setRegFormGoal] = useState('AI Researcher');

  // Interactive Sandbox Simulator State
  const [sandboxCredits, setSandboxCredits] = useState(20);
  const [sandboxCGPA, setSandboxCGPA] = useState(8.4);
  const [sandboxClearedPrereqs, setSandboxClearedPrereqs] = useState(true);

  // Chat State
  const [chatMessages, setChatMessages] = useState([
    {
      sender: 'Nexus Advisor',
      text: 'Hello! I am Nexus, your Autonomous Academic Advisor. I am connected to all 6 academic intelligence agents. How may I assist your degree progression today?'
    }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [isChatSending, setIsChatSending] = useState(false);

  // -------------------------------------------------------------------------
  // TYPEWRITER ANIMATION FOR LANDING PAGE
  // -------------------------------------------------------------------------
  useEffect(() => {
    let index = 0;
    const interval = setInterval(() => {
      if (index <= fullTitle.length) {
        setTypewriterText(fullTitle.substring(0, index));
        index++;
      } else {
        clearInterval(interval);
      }
    }, 220);

    return () => clearInterval(interval);
  }, []);

  // Fetch initial students
  useEffect(() => {
    fetch(`${API_BASE_URL}/students`)
      .then((r) => r.json())
      .then((data) => {
        const list = Array.isArray(data) ? data : data.students || [];
        setStudentsList(list);
      })
      .catch((err) => console.log('Using default mock student pool:', err));
  }, []);

  // -------------------------------------------------------------------------
  // LOAD STUDENT SESSION & TRIGGER FULL MULTI-AGENT PIPELINE
  // -------------------------------------------------------------------------
  const loadStudentSession = useCallback(async (studentId) => {
    if (!studentId) return;
    setIsPipelineRunning(true);
    setActiveAgentIndex(0);

    try {
      // 1. Fetch Student Profile
      const stRes = await fetch(`${API_BASE_URL}/students/${studentId}`);
      if (stRes.ok) {
        const stData = await stRes.json();
        setStudentProfile(stData.student || stData);
        setSandboxCGPA(Number(stData.cgpa ?? stData.student?.CGPA ?? 8.4));
      }

      setTimeout(() => setActiveAgentIndex(1), 160);
      setTimeout(() => setActiveAgentIndex(2), 320);

      // 2. Fetch Knowledge Graph for React Flow
      const graphRes = await fetch(`${API_BASE_URL}/graph/curriculum?student_id=${studentId}`);
      if (graphRes.ok) {
        const graphData = await graphRes.json();
        
        const semesterCounters = { 1: 0, 2: 0, 3: 0, 4: 0 };
        const formattedNodes = (graphData.nodes || []).map((n) => {
          const sem = n.semester || n.data?.semester || 1;
          const idx = semesterCounters[sem] || 0;
          semesterCounters[sem] = idx + 1;

          const x = n.position?.x ?? (sem - 1) * 350 + 60;
          const y = n.position?.y ?? idx * 125 + 60;

          return {
            id: n.id,
            type: 'customCourseNode',
            position: { x, y },
            data: {
              subject_id: n.id,
              label: n.label || n.data?.label || n.id,
              credits: n.credits || n.data?.credits || 3,
              semester: sem,
              status: n.data?.status || 'AVAILABLE',
              is_bottleneck: n.data?.is_bottleneck || ['Sub_2_1', 'Sub_3_1', 'Sub_3_3', 'Sub_4_1'].includes(n.id)
            }
          };
        });

        setNodes(formattedNodes);
        setEdges(graphData.edges || []);
      }

      setTimeout(() => setActiveAgentIndex(3), 480);
      setTimeout(() => setActiveAgentIndex(4), 640);

      // 3. Run Unified Multi-Agent Pipeline
      const pipeRes = await fetch(`${API_BASE_URL}/advising/pipeline`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ student_id: studentId })
      });

      if (pipeRes.ok) {
        const fullData = await pipeRes.json();
        setPipelineData(fullData);
        if (fullData.faculty_petitions) {
          setFacultyPetitions(fullData.faculty_petitions);
        }
      }

      setTimeout(() => setActiveAgentIndex(5), 800);
    } catch (err) {
      console.error('Pipeline execution warning:', err);
    } finally {
      setTimeout(() => {
        setIsPipelineRunning(false);
        setActiveAgentIndex(-1);
      }, 1000);
    }
  }, [setNodes, setEdges]);

  // Handle Node Selection in Graph
  const onNodeClick = useCallback(async (_, node) => {
    setSelectedNodeData(node.data);
    setWaiverCourseId(node.data.subject_id);

    try {
      const res = await fetch(`${API_BASE_URL}/substitutions/${node.data.subject_id}`);
      if (res.ok) {
        const data = await res.json();
        setCourseSubstitutions(data.substitutions || []);
      }
    } catch (err) {
      setCourseSubstitutions([]);
    }
  }, []);

  // Handle Chat Submissions
  const handleSendChat = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userQuery = chatInput;
    setChatMessages((prev) => [...prev, { sender: 'Student', text: userQuery }]);
    setChatInput('');
    setIsChatSending(true);

    try {
      const res = await fetch(`${API_BASE_URL}/advising/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ student_id: selectedStudentId, message: userQuery })
      });
      if (res.ok) {
        const data = await res.json();
        setChatMessages((prev) => [
          ...prev,
          { sender: 'Nexus Advisor', text: data.reply, citations: data.citations || [] }
        ]);
      }
    } catch (err) {
      setChatMessages((prev) => [
        ...prev,
        { sender: 'Nexus Advisor', text: 'Error connecting to agent core. Please ensure backend server is active.' }
      ]);
    } finally {
      setIsChatSending(false);
    }
  };

  // Submit Faculty Waiver / Overload Petition
  const handleSubmitWaiver = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE_URL}/faculty/petitions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          reg_no: selectedStudentId,
          subject_id: waiverCourseId,
          petition_type: waiverType,
          reason: waiverReason
        })
      });
      if (res.ok) {
        const newRecord = await res.json();
        setFacultyPetitions((prev) => [newRecord, ...prev]);
        setIsWaiverModalOpen(false);
        setWaiverReason('');
        alert(`✨ Petition submitted successfully! SHA-256 Audit Stamp: ${newRecord.audit_hash.substring(0, 14)}...`);
      }
    } catch (err) {
      alert('Error submitting faculty petition.');
    }
  };

  // Create New Student Account
  const handleCreateStudent = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE_URL}/students`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          reg_no: regFormRegNo,
          student_name: regFormName,
          semester: Number(regFormSem),
          cgpa: Number(regFormCGPA),
          goal: regFormGoal
        })
      });
      if (res.ok) {
        const created = await res.json();
        setStudentsList((prev) => [created, ...prev]);
        setSelectedStudentId(created.reg_no);
        setIsRegisterModalOpen(false);
        loadStudentSession(created.reg_no);
        setCurrentView('dashboard');
      } else {
        const err = await res.json();
        alert(`Registration Error: ${err.detail || 'Could not register student.'}`);
      }
    } catch (err) {
      alert('Error connecting to backend API.');
    }
  };

  // Action Faculty Petition (Approve/Reject)
  const handleFacultyAction = async (petitionId, action) => {
    const remarks = prompt(`Enter official faculty remarks for ${action.toUpperCase()}:`, `Approved under department chair review.`);
    if (!remarks) return;

    try {
      const res = await fetch(`${API_BASE_URL}/faculty/petitions/${petitionId}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: action.toUpperCase(), faculty_remarks: remarks })
      });
      if (res.ok) {
        const updated = await res.json();
        setFacultyPetitions((prev) => prev.map((p) => (p.petition_id === petitionId ? updated : p)));
      }
    } catch (err) {
      alert('Action processing error.');
    }
  };

  // -------------------------------------------------------------------------
  // RENDER: 1. Cinematic Landing Page with Floating Mascots & Letter-by-Letter OMEGA
  // -------------------------------------------------------------------------
  if (currentView === 'landing') {
    return (
      <div
        className="cyber-background"
        style={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '24px',
          position: 'relative',
          cursor: 'pointer'
        }}
        onClick={() => setCurrentView('login')}
      >
        {/* Pixel Art Twinkling Stars */}
        <div className="pixel-star" style={{ top: '12%', left: '8%' }}>✦</div>
        <div className="pixel-star" style={{ top: '22%', right: '10%' }}>★</div>
        <div className="pixel-star" style={{ bottom: '18%', left: '16%' }}>✧</div>
        <div className="pixel-star" style={{ bottom: '24%', right: '14%' }}>✦</div>
        <div className="pixel-star" style={{ top: '45%', left: '6%' }}>★</div>
        <div className="pixel-star" style={{ top: '55%', right: '7%' }}>✧</div>

        {/* Mascot 1: Nexus (Top Left Floating) */}
        <div className="floating-mascot-container mascot-pos-1" onClick={(e) => { e.stopPropagation(); setCurrentView('login'); }}>
          <div className="landing-mascot-card">
            <img src="/assets/nexus.png" alt="Nexus Mascot" className="landing-mascot-img" />
            <span className="badge badge-cyan" style={{ fontSize: '10px' }}>Agent 01: Nexus</span>
            <div className="mascot-speech-bubble">✨ Central Supervisor</div>
          </div>
        </div>

        {/* Mascot 2: Matrix (Top Right Floating) */}
        <div className="floating-mascot-container mascot-pos-2" onClick={(e) => { e.stopPropagation(); setCurrentView('login'); }}>
          <div className="landing-mascot-card">
            <img src="/assets/matrix.png" alt="Matrix Mascot" className="landing-mascot-img" />
            <span className="badge badge-emerald" style={{ fontSize: '10px' }}>Agent 02: Matrix</span>
            <div className="mascot-speech-bubble">🧭 Graph Pathfinder</div>
          </div>
        </div>

        {/* Mascot 3: State (Bottom Left Floating) */}
        <div className="floating-mascot-container mascot-pos-3" onClick={(e) => { e.stopPropagation(); setCurrentView('login'); }}>
          <div className="landing-mascot-card">
            <img src="/assets/state.png" alt="State Mascot" className="landing-mascot-img" />
            <span className="badge badge-blue" style={{ fontSize: '10px' }}>Agent 04: State</span>
            <div className="mascot-speech-bubble">🛡️ DBMS Synthesizer</div>
          </div>
        </div>

        {/* Mascot 4: Vector (Bottom Right Floating) */}
        <div className="floating-mascot-container mascot-pos-4" onClick={(e) => { e.stopPropagation(); setCurrentView('login'); }}>
          <div className="landing-mascot-card">
            <img src="/assets/vector.png" alt="Vector Mascot" className="landing-mascot-img" />
            <span className="badge badge-amber" style={{ fontSize: '10px' }}>Agent 03: Vector</span>
            <div className="mascot-speech-bubble">🚀 Career Velocity</div>
          </div>
        </div>

        {/* Center Title & Letter-by-Letter Animated Display */}
        <div style={{ textAlign: 'center', maxWidth: '840px', zIndex: 15 }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '6px 18px', borderRadius: '9999px', background: 'rgba(6,182,212,0.14)', border: '1px solid rgba(6,182,212,0.4)', color: '#22d3ee', fontSize: '13px', fontWeight: 800, marginBottom: '20px' }}>
            <Sparkles size={16} /> AUTONOMOUS MULTI-AGENT ACADEMIC INTELLIGENCE
          </div>

          <div className="glitter-shimmer-title">
            {typewriterText}
            <span className="typewriter-cursor"></span>
          </div>

          <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#cbd5e1', letterSpacing: '-0.01em', marginBottom: '16px', lineHeight: '1.4' }}>
            Decentralized Graph-RAG Academic Pathway Intelligence & Prerequisite Conflict Resolver
          </h2>

          <p style={{ fontSize: '14px', color: '#94a3b8', maxWidth: '620px', margin: '0 auto 32px auto', lineHeight: '1.6' }}>
            Powered by 6 Autonomous Agents: Graph-RAG Policy Citations, Formal Constraint Verification, Topological Degree Pathfinding, and Faculty Governance.
          </p>

          <div style={{ display: 'flex', justifyContent: 'center', gap: '14px' }}>
            <button
              className="btn-glitter"
              onClick={(e) => {
                e.stopPropagation();
                setCurrentView('login');
              }}
              style={{ padding: '14px 32px', fontSize: '15px' }}
            >
              <Sparkles size={18} /> Enter Omega Platform <ArrowRight size={18} />
            </button>
          </div>

          <div style={{ marginTop: '36px', display: 'flex', justifyContent: 'center', gap: '28px', fontSize: '12px', color: '#64748b', fontFamily: 'monospace' }}>
            <span>● 6 AUTONOMOUS AGENTS</span>
            <span>● 60-COURSE KNOWLEDGE GRAPH</span>
            <span>● ZERO HALLUCINATIONS</span>
            <span>● SHA-256 AUDIT LOGS</span>
          </div>
        </div>
      </div>
    );
  }

  // -------------------------------------------------------------------------
  // RENDER: 2. Login & Student Selection Screen
  // -------------------------------------------------------------------------
  if (currentView === 'login') {
    return (
      <div className="cyber-background" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '36px 16px' }}>
        <div className="pixel-star" style={{ top: '10%', left: '8%' }}>✦</div>
        <div className="pixel-star" style={{ top: '20%', right: '12%' }}>★</div>
        <div className="pixel-star" style={{ bottom: '15%', left: '15%' }}>✧</div>
        <div className="pixel-star" style={{ bottom: '20%', right: '10%' }}>✦</div>

        <div style={{ maxWidth: '1080px', width: '100%' }}>
          {/* Header */}
          <div style={{ textAlign: 'center', marginBottom: '32px' }}>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '6px 18px', borderRadius: '9999px', background: 'rgba(6,182,212,0.12)', border: '1px solid rgba(6,182,212,0.35)', color: '#22d3ee', fontSize: '12px', fontWeight: 800, marginBottom: '14px' }}>
              <Sparkles size={14} /> DECENTRALIZED GRAPH-RAG ACADEMIC INTELLIGENCE
            </div>
            <h1 style={{ fontSize: '42px', fontWeight: 900, letterSpacing: '-0.03em', color: '#f8fafc', marginBottom: '10px' }}>
              <span style={{ color: '#06b6d4' }}>Omega</span> Academic Pathway Intelligence
            </h1>
            <p style={{ color: '#94a3b8', fontSize: '16px', maxWidth: '720px', margin: '0 auto', lineHeight: '1.5' }}>
              Select a simulated student profile or register a new enrollment account to explore personalized advising.
            </p>
          </div>

          {/* Mode Switcher & Create Account Trigger */}
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '14px', marginBottom: '28px', flexWrap: 'wrap' }}>
            <button
              onClick={() => setPortalMode('student')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '12px 24px',
                borderRadius: '10px',
                border: portalMode === 'student' ? '1.5px solid #06b6d4' : '1px solid rgba(255,255,255,0.1)',
                background: portalMode === 'student' ? 'rgba(6,182,212,0.18)' : 'rgba(15,23,42,0.6)',
                color: portalMode === 'student' ? '#22d3ee' : '#94a3b8',
                fontWeight: 700,
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
                padding: '12px 24px',
                borderRadius: '10px',
                border: portalMode === 'faculty' ? '1.5px solid #a855f7' : '1px solid rgba(255,255,255,0.1)',
                background: portalMode === 'faculty' ? 'rgba(168,85,247,0.18)' : 'rgba(15,23,42,0.6)',
                color: portalMode === 'faculty' ? '#c084fc' : '#94a3b8',
                fontWeight: 700,
                cursor: 'pointer'
              }}
            >
              <ShieldCheck size={18} /> Faculty Exception Portal
            </button>

            <button
              onClick={() => setIsRegisterModalOpen(true)}
              className="btn-glitter"
              style={{ padding: '12px 24px', borderRadius: '10px' }}
            >
              <UserPlus size={18} /> Create New Student Account
            </button>
          </div>

          {/* Student Selection Container */}
          <div className="glass-panel" style={{ padding: '28px', marginBottom: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '14px' }}>
              <div>
                <h3 style={{ fontSize: '18px', fontWeight: 800, color: '#f8fafc', marginBottom: '4px' }}>
                  Select Student Profile for Simulation
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
                    padding: '10px 14px',
                    borderRadius: '8px',
                    border: '1px solid rgba(59,130,246,0.3)',
                    background: 'rgba(15,23,42,0.9)',
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
                  className="btn-glitter"
                  style={{ padding: '10px 18px' }}
                >
                  Enter Session <ArrowRight size={16} />
                </button>
              </div>
            </div>

            {/* Quick Demo Cards Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '16px' }}>
              {studentsList.slice(0, 6).map((st) => {
                const regNo = st.RegNo || st.reg_no;
                const name = st.StudentName || st.student_name;
                const sem = st.Semester || st.semester;
                const goal = st.Goal || st.goal || st.career_goal;
                const gpa = Number(st.CGPA ?? st.cgpa ?? st.current_gpa ?? 7.5);

                return (
                  <div
                    key={regNo}
                    className="glass-card-interactive"
                    onClick={() => {
                      setSelectedStudentId(regNo);
                      loadStudentSession(regNo);
                      setCurrentView('dashboard');
                    }}
                    style={{
                      padding: '18px',
                      border: selectedStudentId === regNo ? '1.5px solid #06b6d4' : '1px solid rgba(59,130,246,0.18)'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <span style={{ fontSize: '12px', fontWeight: 800, color: '#38bdf8', fontFamily: 'monospace' }}>
                        {regNo}
                      </span>
                      <span className="badge badge-cyan">Sem {sem}</span>
                    </div>
                    <div style={{ fontSize: '15px', fontWeight: 700, color: '#f8fafc', marginBottom: '4px' }}>
                      {name}
                    </div>
                    <div style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '12px' }}>
                      🎯 {goal}
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '10px' }}>
                      <span style={{ fontSize: '12px', color: '#94a3b8' }}>Cumulative GPA</span>
                      <span style={{ fontSize: '13px', fontWeight: 800, color: gpa >= 8.5 ? '#34d399' : gpa < 6.0 ? '#fb7185' : '#38bdf8' }}>
                        {gpa.toFixed(2)} / 10.00
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Create Student Account Modal */}
        {isRegisterModalOpen && (
          <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(10px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
            <div className="glass-panel" style={{ width: '520px', padding: '28px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <UserPlus size={20} color="#06b6d4" />
                  <h3 style={{ fontSize: '18px', fontWeight: 800, color: '#f8fafc' }}>New Student Registration</h3>
                </div>
                <button onClick={() => setIsRegisterModalOpen(false)} style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>
                  <X size={20} />
                </button>
              </div>

              <form onSubmit={handleCreateStudent}>
                <div style={{ marginBottom: '14px' }}>
                  <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Student Full Name</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Saketh Rao"
                    value={regFormName}
                    onChange={(e) => setRegFormName(e.target.value)}
                    style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(15,23,42,0.9)', border: '1px solid rgba(59,130,246,0.3)', color: '#f8fafc', fontSize: '13px' }}
                  />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '14px' }}>
                  <div>
                    <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Registration ID</label>
                    <input
                      type="text"
                      required
                      value={regFormRegNo}
                      onChange={(e) => setRegFormRegNo(e.target.value.toUpperCase())}
                      style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(15,23,42,0.9)', border: '1px solid rgba(59,130,246,0.3)', color: '#f8fafc', fontSize: '13px' }}
                    />
                  </div>
                  <div>
                    <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Starting Semester</label>
                    <select
                      value={regFormSem}
                      onChange={(e) => setRegFormSem(e.target.value)}
                      style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(15,23,42,0.9)', border: '1px solid rgba(59,130,246,0.3)', color: '#f8fafc', fontSize: '13px' }}
                    >
                      <option value="1">Semester 1</option>
                      <option value="2">Semester 2</option>
                      <option value="3">Semester 3</option>
                      <option value="4">Semester 4</option>
                    </select>
                  </div>
                </div>

                <div style={{ marginBottom: '14px' }}>
                  <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Starting CGPA</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    max="10"
                    required
                    value={regFormCGPA}
                    onChange={(e) => setRegFormCGPA(e.target.value)}
                    style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(15,23,42,0.9)', border: '1px solid rgba(59,130,246,0.3)', color: '#f8fafc', fontSize: '13px' }}
                  />
                </div>

                <div style={{ marginBottom: '20px' }}>
                  <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Target Career Track</label>
                  <select
                    value={regFormGoal}
                    onChange={(e) => setRegFormGoal(e.target.value)}
                    style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(15,23,42,0.9)', border: '1px solid rgba(59,130,246,0.3)', color: '#f8fafc', fontSize: '13px' }}
                  >
                    {CAREER_OPTIONS.map((c) => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>

                <button
                  type="submit"
                  className="btn-glitter"
                  style={{ width: '100%', padding: '12px', borderRadius: '8px', justifyContent: 'center' }}
                >
                  <Sparkles size={16} /> Complete Registration & Open Advising
                </button>
              </form>
            </div>
          </div>
        )}
      </div>
    );
  }

  // -------------------------------------------------------------------------
  // RENDER: 3. Main Multi-Agent Dashboard
  // -------------------------------------------------------------------------
  const studentName = pipelineData?.student_name || studentProfile?.StudentName || studentProfile?.student_name || 'Diya Banerjee';
  const studentCGPA = Number(pipelineData?.cgpa ?? studentProfile?.CGPA ?? studentProfile?.current_gpa ?? 8.40);
  const studentSem = pipelineData?.current_semester || studentProfile?.Semester || studentProfile?.semester || 1;
  const studentGoal = pipelineData?.career_goal || studentProfile?.Goal || studentProfile?.career_goal || 'Data Scientist';
  const academicStanding = pipelineData?.academic_standing || (studentCGPA >= 8.5 ? 'HONORS' : studentCGPA < 6.0 ? 'AT_RISK' : 'GOOD_STANDING');

  return (
    <div className="cyber-background app-container">
      <div className="pixel-star" style={{ top: '8%', left: '5%' }}>✦</div>
      <div className="pixel-star" style={{ top: '15%', right: '6%' }}>★</div>

      {/* Top Cyber Navigation Bar */}
      <header style={{ height: '68px', borderBottom: '1px solid rgba(59,130,246,0.2)', background: 'rgba(10,13,20,0.88)', backdropFilter: 'blur(18px)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 24px', position: 'sticky', top: 0, zIndex: 50 }}>
        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }} onClick={() => setCurrentView('landing')}>
          <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'rgba(6,182,212,0.15)', border: '1.5px solid #06b6d4', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Brain size={24} color="#22d3ee" />
          </div>
          <div>
            <div style={{ fontSize: '18px', fontWeight: 900, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ color: '#06b6d4' }}>Omega</span> Pathway Intelligence
              <span style={{ fontSize: '10px', padding: '2px 6px', borderRadius: '4px', background: 'rgba(6,182,212,0.2)', color: '#22d3ee', fontWeight: 800 }}>v2.0</span>
            </div>
            <div style={{ fontSize: '11px', color: '#64748b' }}>Autonomous Multi-Agent Architecture</div>
          </div>
        </div>

        {/* Live Active Student Pill */}
        <div className="glass-panel" style={{ display: 'flex', alignItems: 'center', gap: '16px', padding: '8px 18px', borderRadius: '9999px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div className="pulse-dot"></div>
            <span style={{ fontSize: '12px', fontWeight: 800, color: '#38bdf8', fontFamily: 'monospace' }}>
              {selectedStudentId}
            </span>
          </div>
          <div style={{ height: '14px', width: '1px', background: 'rgba(255,255,255,0.1)' }}></div>
          <span style={{ fontSize: '13px', fontWeight: 700, color: '#f8fafc' }}>{studentName}</span>
          <span className="badge badge-cyan">Sem {studentSem}</span>
          <span style={{ fontSize: '12px', fontWeight: 800, color: studentCGPA >= 8.5 ? '#34d399' : studentCGPA < 6.0 ? '#fb7185' : '#38bdf8' }}>
            {studentCGPA.toFixed(2)} CGPA
          </span>
          <span className={`badge ${academicStanding === 'HONORS' ? 'badge-emerald' : academicStanding === 'AT_RISK' ? 'badge-rose' : 'badge-cyan'}`}>
            {academicStanding}
          </span>
        </div>

        {/* Action Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <button
            onClick={() => loadStudentSession(selectedStudentId)}
            disabled={isPipelineRunning}
            className="btn-glitter"
            style={{ padding: '8px 14px', fontSize: '12px' }}
          >
            <RotateCcw size={14} className={isPipelineRunning ? 'animate-spin' : ''} />
            {isPipelineRunning ? 'Running Council...' : 'Re-Run Agents'}
          </button>

          <button
            onClick={() => setCurrentView('landing')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 14px',
              borderRadius: '8px',
              border: '1px solid rgba(6,182,212,0.4)',
              background: 'rgba(6,182,212,0.12)',
              color: '#22d3ee',
              fontWeight: 700,
              fontSize: '12px',
              cursor: 'pointer'
            }}
          >
            <Home size={14} /> Landing
          </button>

          <button
            onClick={() => setCurrentView('login')}
            style={{
              padding: '8px 14px',
              borderRadius: '8px',
              border: '1px solid rgba(255,255,255,0.14)',
              background: 'rgba(15,23,42,0.8)',
              color: '#94a3b8',
              fontWeight: 700,
              fontSize: '12px',
              cursor: 'pointer'
            }}
          >
            Switch Profile
          </button>
        </div>
      </header>

      {/* Multi-Agent Dynamic Live Telemetry Ribbon with Mascot Avatars */}
      <section style={{ background: 'rgba(11,16,28,0.96)', borderBottom: '1px solid rgba(59,130,246,0.18)', padding: '12px 24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', fontWeight: 800, color: '#38bdf8' }}>
            <Activity size={14} /> AUTONOMOUS MULTI-AGENT TELEMETRY COUNCIL
          </div>
          <span style={{ fontSize: '11px', color: '#64748b', fontFamily: 'monospace' }}>
            SESSION HASH: {pipelineData?.session_id || 'SES_LIVE_ACTIVE'}
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '10px' }}>
          {AGENTS_INFO.map((ag, idx) => {
            const IconComp = ag.icon;
            const isActive = isPipelineRunning && activeAgentIndex === idx;

            return (
              <div
                key={ag.id}
                className={`agent-node-card ${isActive ? 'active-pulse' : ''}`}
                onClick={() => setSelectedAgentCard(ag)}
                style={{
                  border: isActive ? `1.5px solid ${ag.color}` : '1px solid rgba(59,130,246,0.18)',
                  background: isActive ? 'rgba(6,182,212,0.18)' : 'rgba(15,23,42,0.85)'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <img
                    src={ag.avatar}
                    alt={ag.name}
                    className="agent-avatar-img"
                    onError={(e) => {
                      e.target.style.display = 'none';
                    }}
                  />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: '11px', fontWeight: 800, color: '#f8fafc', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {ag.shortName}
                    </div>
                    <div style={{ fontSize: '9px', color: ag.color, fontWeight: 700 }}>
                      {isActive ? '● COMPUTING' : 'IDLE / READY'}
                    </div>
                  </div>
                </div>
                <div style={{ fontSize: '10px', color: '#94a3b8', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {ag.role}
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Main Tab Navigation Bar */}
      <div style={{ padding: '16px 24px 0 24px', display: 'flex', gap: '8px', borderBottom: '1px solid rgba(59,130,246,0.18)', overflowX: 'auto' }}>
        {[
          { id: 'graph', label: 'Prerequisite Graph Canvas', icon: Layers },
          { id: 'council', label: 'Agent Council Deliberation', icon: Brain },
          { id: 'sandbox', label: 'Degree Sandbox Simulator', icon: SlidersHorizontal },
          { id: 'quest', label: 'Career Quest Tree', icon: Gamepad2 },
          { id: 'pathway', label: 'Degree Pathway Planner', icon: Compass },
          { id: 'conflicts', label: 'Conflict & Risk Resolver', icon: AlertTriangle, badge: pipelineData?.conflict_report?.critical_count },
          { id: 'chat', label: 'Citation-Traceable AI Chat', icon: MessageSquare },
          { id: 'faculty', label: 'Faculty Governance Portal', icon: ShieldCheck, badge: facultyPetitions.filter((p) => p.status === 'PENDING').length }
        ].map((tab) => {
          const TabIcon = tab.icon;
          const isCurrent = activeTab === tab.id;

          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '12px 18px',
                borderRadius: '8px 8px 0 0',
                border: '1px solid',
                borderColor: isCurrent ? 'rgba(6,182,212,0.45)' : 'transparent',
                borderBottom: isCurrent ? '2px solid #06b6d4' : 'none',
                background: isCurrent ? 'rgba(15,23,42,0.92)' : 'transparent',
                color: isCurrent ? '#22d3ee' : '#94a3b8',
                fontWeight: 800,
                fontSize: '13px',
                cursor: 'pointer',
                whiteSpace: 'nowrap',
                transition: 'all 0.2s'
              }}
            >
              <TabIcon size={16} />
              {tab.label}
              {tab.badge > 0 && (
                <span style={{ background: '#f43f5e', color: '#fff', fontSize: '10px', padding: '1px 6px', borderRadius: '9999px', fontWeight: 800 }}>
                  {tab.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Main Workspace Body */}
      <main style={{ flex: 1, padding: '24px', display: 'flex', flexDirection: 'column' }}>
        {/* -------------------------------------------------------------------
            TAB 1: Interactive Curriculum Knowledge Graph (React Flow)
        -------------------------------------------------------------------- */}
        {activeTab === 'graph' && (
          <div style={{ height: '720px', width: '100%', position: 'relative', borderRadius: '14px', overflow: 'hidden', border: '1px solid rgba(59,130,246,0.22)' }}>
            {/* Graph Filter Controls */}
            <div style={{ position: 'absolute', top: '16px', left: '16px', zIndex: 10, display: 'flex', gap: '8px' }} className="glass-panel">
              <button
                onClick={() => setGraphFilter('ALL')}
                style={{ padding: '6px 14px', borderRadius: '6px', border: 'none', background: graphFilter === 'ALL' ? '#06b6d4' : 'transparent', color: '#fff', fontSize: '11px', fontWeight: 800, cursor: 'pointer' }}
              >
                All 60 Courses
              </button>
              <button
                onClick={() => setGraphFilter('BOTTLENECKS')}
                style={{ padding: '6px 14px', borderRadius: '6px', border: 'none', background: graphFilter === 'BOTTLENECKS' ? '#f59e0b' : 'transparent', color: '#fff', fontSize: '11px', fontWeight: 800, cursor: 'pointer' }}
              >
                Gateway Chokepoints
              </button>
            </div>

            {/* Legend */}
            <div style={{ position: 'absolute', top: '16px', right: '16px', zIndex: 10, display: 'flex', gap: '16px' }} className="glass-panel">
              <div style={{ padding: '6px 14px', fontSize: '11px', color: '#94a3b8', display: 'flex', gap: '14px' }}>
                <span style={{ color: '#10b981', display: 'flex', alignItems: 'center', gap: '4px' }}>● Completed</span>
                <span style={{ color: '#06b6d4', display: 'flex', alignItems: 'center', gap: '4px' }}>● Enrolled</span>
                <span style={{ color: '#3b82f6', display: 'flex', alignItems: 'center', gap: '4px' }}>● Available</span>
                <span style={{ color: '#f59e0b', display: 'flex', alignItems: 'center', gap: '4px' }}>★ Gateway</span>
              </div>
            </div>

            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onNodeClick={onNodeClick}
              nodeTypes={nodeTypes}
              fitView
            >
              <Background color="#1e293b" gap={22} size={1} />
              <Controls />
              <MiniMap style={{ background: '#0a0d14', border: '1px solid rgba(59,130,246,0.2)' }} />
            </ReactFlow>

            {/* Selected Node Details Drawer */}
            {selectedNodeData && (
              <div
                className="glass-panel"
                style={{
                  position: 'absolute',
                  bottom: '16px',
                  right: '16px',
                  width: '360px',
                  padding: '20px',
                  zIndex: 20
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <span style={{ fontSize: '12px', fontWeight: 800, color: '#38bdf8' }}>{selectedNodeData.subject_id}</span>
                  <button onClick={() => setSelectedNodeData(null)} style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>
                    <X size={16} />
                  </button>
                </div>
                <h4 style={{ fontSize: '15px', fontWeight: 800, color: '#f8fafc', marginBottom: '8px' }}>{selectedNodeData.label}</h4>
                <div style={{ display: 'flex', gap: '8px', marginBottom: '14px' }}>
                  <span className="badge badge-cyan">Sem {selectedNodeData.semester}</span>
                  <span className="badge badge-purple">{selectedNodeData.credits} Credits</span>
                </div>

                {/* Course Substitutions Recommendations */}
                <div style={{ borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: '10px', marginBottom: '14px' }}>
                  <div style={{ fontSize: '12px', fontWeight: 700, color: '#cbd5e1', marginBottom: '6px' }}>
                    Approved Substitutions ({courseSubstitutions.length}):
                  </div>
                  {courseSubstitutions.length > 0 ? (
                    courseSubstitutions.map((sub, i) => (
                      <div key={i} style={{ fontSize: '11px', color: '#22d3ee', background: 'rgba(6,182,212,0.12)', padding: '6px 10px', borderRadius: '6px', marginBottom: '4px' }}>
                        ⇄ {sub.EquivalentSubjectID}: {sub.EquivalentName}
                      </div>
                    ))
                  ) : (
                    <div style={{ fontSize: '11px', color: '#64748b' }}>No direct elective substitutions mapped.</div>
                  )}
                </div>

                <button
                  onClick={() => setIsWaiverModalOpen(true)}
                  className="btn-glitter"
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', justifyContent: 'center' }}
                >
                  <FileText size={14} /> Request Faculty Waiver Petition
                </button>
              </div>
            )}
          </div>
        )}

        {/* -------------------------------------------------------------------
            TAB 2: Multi-Agent Council Deliberation Chamber
        -------------------------------------------------------------------- */}
        {activeTab === 'council' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '20px' }}>
            <div className="glass-panel" style={{ padding: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <Brain size={22} color="#06b6d4" />
                  <h3 style={{ fontSize: '18px', fontWeight: 800, color: '#f8fafc' }}>
                    Autonomous Agent Council Deliberation Chamber
                  </h3>
                </div>
                <span className="badge badge-cyan">SESSION {pipelineData?.session_id || 'ACTIVE'}</span>
              </div>

              {/* Deliberation Transcript */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                <div className="council-bubble" style={{ borderLeft: '4px solid #3b82f6' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                    <img src="/assets/state.png" alt="State" className="agent-avatar-img" style={{ width: '28px', height: '28px' }} />
                    <span style={{ fontSize: '12px', fontWeight: 800, color: '#3b82f6' }}>Agent 04 (State Synthesizer)</span>
                  </div>
                  <p style={{ fontSize: '13px', color: '#cbd5e1', lineHeight: '1.5' }}>
                    Student record verified from DBMS: <strong>{studentName} ({selectedStudentId})</strong> is currently in Semester {studentSem} with CGPA {studentCGPA.toFixed(2)}. Standing evaluated as <strong>{academicStanding}</strong>.
                  </p>
                </div>

                <div className="council-bubble" style={{ borderLeft: '4px solid #10b981' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                    <img src="/assets/matrix.png" alt="Matrix" className="agent-avatar-img" style={{ width: '28px', height: '28px' }} />
                    <span style={{ fontSize: '12px', fontWeight: 800, color: '#10b981' }}>Agent 02 (The Matrix Pathfinder)</span>
                  </div>
                  <p style={{ fontSize: '13px', color: '#cbd5e1', lineHeight: '1.5' }}>
                    Prerequisite graph navigated. Synthesized a {pipelineData?.degree_pathway?.total_steps_required || 4}-term conflict-free degree sequence toward graduation (160 credits), respecting term load caps.
                  </p>
                </div>

                <div className="council-bubble" style={{ borderLeft: '4px solid #f43f5e' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                    <img src="/assets/sentinel.png" alt="Sentinel" className="agent-avatar-img" style={{ width: '28px', height: '28px' }} />
                    <span style={{ fontSize: '12px', fontWeight: 800, color: '#f43f5e' }}>Agent 06 (Sentinel Verifier)</span>
                  </div>
                  <p style={{ fontSize: '13px', color: '#cbd5e1', lineHeight: '1.5' }}>
                    Formal constraint audit executed: {pipelineData?.conflict_report?.critical_count || 0} critical conflict(s) detected. Graduation Risk Index evaluated at {((pipelineData?.conflict_report?.graduation_risk_score || 0) * 100).toFixed(0)}%.
                  </p>
                </div>

                <div className="council-bubble" style={{ borderLeft: '4px solid #a855f7' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                    <img src="/assets/codex.png" alt="Codex" className="agent-avatar-img" style={{ width: '28px', height: '28px' }} />
                    <span style={{ fontSize: '12px', fontWeight: 800, color: '#a855f7' }}>Agent 05 (Codex Graph-RAG)</span>
                  </div>
                  <p style={{ fontSize: '13px', color: '#cbd5e1', lineHeight: '1.5' }}>
                    Grounded policy articles retrieved: {pipelineData?.graph_rag_advising?.traceable_citations?.join(', ') || '[Policy §1.1], [Policy §2.1]'}.
                  </p>
                </div>

                <div className="council-bubble" style={{ borderLeft: '4px solid #f59e0b' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                    <img src="/assets/vector.png" alt="Vector" className="agent-avatar-img" style={{ width: '28px', height: '28px' }} />
                    <span style={{ fontSize: '12px', fontWeight: 800, color: '#f59e0b' }}>Agent 03 (Vector Career Velocity)</span>
                  </div>
                  <p style={{ fontSize: '13px', color: '#cbd5e1', lineHeight: '1.5' }}>
                    Career milestone configured for <strong>{studentGoal}</strong>: Recommended capstone project is <em>{pipelineData?.career_vector?.actionable_project?.substring(0, 100)}...</em>
                  </p>
                </div>
              </div>
            </div>

            {/* Agent Inspector Card */}
            <div className="glass-panel" style={{ padding: '24px' }}>
              <div style={{ textAlign: 'center', marginBottom: '16px' }}>
                <img src={selectedAgentCard.avatar} alt={selectedAgentCard.name} className="agent-avatar-img" style={{ width: '72px', height: '72px', margin: '0 auto 12px auto' }} />
                <h4 style={{ fontSize: '16px', fontWeight: 800, color: '#f8fafc' }}>{selectedAgentCard.name}</h4>
                <span className="badge badge-cyan" style={{ marginTop: '4px' }}>{selectedAgentCard.role}</span>
              </div>
              <p style={{ fontSize: '13px', color: '#94a3b8', lineHeight: '1.5', marginBottom: '16px' }}>
                {selectedAgentCard.desc}
              </p>
              <div style={{ background: 'rgba(6,182,212,0.12)', padding: '12px', borderRadius: '8px', border: '1px solid rgba(6,182,212,0.3)', fontSize: '12px', color: '#22d3ee', lineHeight: '1.4' }}>
                {selectedAgentCard.tip}
              </div>
            </div>
          </div>
        )}

        {/* -------------------------------------------------------------------
            TAB 3: Interactive Degree Sandbox & Simulator
        -------------------------------------------------------------------- */}
        {activeTab === 'sandbox' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '20px' }}>
            <div className="glass-panel" style={{ padding: '24px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '18px' }}>
                <SlidersHorizontal size={20} color="#06b6d4" />
                <h3 style={{ fontSize: '18px', fontWeight: 800, color: '#f8fafc' }}>
                  Interactive Academic Policy Sandbox Simulator
                </h3>
              </div>

              <div style={{ marginBottom: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <label style={{ fontSize: '13px', color: '#cbd5e1', fontWeight: 700 }}>Semester Credit Registration Load</label>
                  <span className="badge badge-cyan">{sandboxCredits} Credits</span>
                </div>
                <input
                  type="range"
                  min="12"
                  max="28"
                  value={sandboxCredits}
                  onChange={(e) => setSandboxCredits(Number(e.target.value))}
                  style={{ width: '100%' }}
                />
              </div>

              <div style={{ marginBottom: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <label style={{ fontSize: '13px', color: '#cbd5e1', fontWeight: 700 }}>Simulated Cumulative GPA</label>
                  <span className="badge badge-purple">{sandboxCGPA.toFixed(2)} / 10.00</span>
                </div>
                <input
                  type="range"
                  min="4.0"
                  max="10.0"
                  step="0.1"
                  value={sandboxCGPA}
                  onChange={(e) => setSandboxCGPA(Number(e.target.value))}
                  style={{ width: '100%' }}
                />
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
                <input
                  type="checkbox"
                  id="prereqCheck"
                  checked={sandboxClearedPrereqs}
                  onChange={(e) => setSandboxClearedPrereqs(e.target.checked)}
                />
                <label htmlFor="prereqCheck" style={{ fontSize: '13px', color: '#cbd5e1', cursor: 'pointer' }}>
                  All Hard Prerequisites Cleared in Prior Terms
                </label>
              </div>
            </div>

            {/* Real-time Projected Diagnostic Response */}
            <div className="glass-panel" style={{ padding: '24px' }}>
              <h4 style={{ fontSize: '16px', fontWeight: 800, color: '#f8fafc', marginBottom: '16px' }}>
                Real-Time Constraint & Risk Projections
              </h4>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div style={{ padding: '12px', borderRadius: '8px', background: sandboxCredits > 20 && sandboxCGPA < 8.0 ? 'rgba(244,63,94,0.15)' : 'rgba(16,185,129,0.15)', border: sandboxCredits > 20 && sandboxCGPA < 8.0 ? '1px solid #f43f5e' : '1px solid #10b981' }}>
                  <div style={{ fontSize: '12px', fontWeight: 800, color: sandboxCredits > 20 && sandboxCGPA < 8.0 ? '#fb7185' : '#34d399', marginBottom: '2px' }}>
                    {sandboxCredits > 20 && sandboxCGPA < 8.0 ? '⛔ Credit Overload Violation' : '✅ Credit Load Approved'}
                  </div>
                  <div style={{ fontSize: '12px', color: '#cbd5e1' }}>
                    {sandboxCredits > 20 && sandboxCGPA < 8.0
                      ? 'Credits exceed 20 CR limit without Honors qualification [Policy §2.1].'
                      : 'Load is within permitted academic limits.'}
                  </div>
                </div>

                <div style={{ padding: '12px', borderRadius: '8px', background: sandboxCGPA < 6.0 ? 'rgba(244,63,94,0.15)' : 'rgba(16,185,129,0.15)', border: sandboxCGPA < 6.0 ? '1px solid #f43f5e' : '1px solid #10b981' }}>
                  <div style={{ fontSize: '12px', fontWeight: 800, color: sandboxCGPA < 6.0 ? '#fb7185' : '#34d399', marginBottom: '2px' }}>
                    {sandboxCGPA < 6.0 ? '⚠️ Academic Probation Risk' : '✅ Good Academic Standing'}
                  </div>
                  <div style={{ fontSize: '12px', color: '#cbd5e1' }}>
                    {sandboxCGPA < 6.0
                      ? 'CGPA below 6.00 triggers remedial 16-credit registration ceiling [Policy §2.2].'
                      : 'Student maintains standard progression capacity.'}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* -------------------------------------------------------------------
            TAB 4: Career Quest Adventure Tree
        -------------------------------------------------------------------- */}
        {activeTab === 'quest' && (
          <div className="glass-panel" style={{ padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <Gamepad2 size={22} color="#f59e0b" />
                  <h3 style={{ fontSize: '18px', fontWeight: 800, color: '#f8fafc' }}>
                    Career Quest Progression Tree: {studentGoal}
                  </h3>
                </div>
                <p style={{ fontSize: '13px', color: '#94a3b8' }}>
                  Complete term levels and capstone quests to earn industry milestone badges.
                </p>
              </div>

              <span className="badge badge-amber" style={{ fontSize: '12px', padding: '6px 14px' }}>
                <Star size={14} /> LEVEL {studentSem} HERO
              </span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
              {[
                { lvl: 1, title: 'Foundation Level', creds: '40 CR', status: studentSem >= 1 ? 'COMPLETED' : 'LOCKED', desc: 'Programming, Calculus, Digital Systems' },
                { lvl: 2, title: 'Core Engineering', creds: '80 CR', status: studentSem >= 2 ? (studentSem === 2 ? 'ACTIVE' : 'COMPLETED') : 'LOCKED', desc: 'Data Structures, Computer Architecture, DBs' },
                { lvl: 3, title: 'Advanced Systems', creds: '120 CR', status: studentSem >= 3 ? (studentSem === 3 ? 'ACTIVE' : 'COMPLETED') : 'LOCKED', desc: 'Algorithms, OS, Cloud Foundations' },
                { lvl: 4, title: 'Boss Capstone', creds: '160 CR', status: studentSem >= 4 ? 'ACTIVE' : 'LOCKED', desc: 'Deep Learning, Microservices, Final Defense' }
              ].map((q) => (
                <div
                  key={q.lvl}
                  className={`quest-level-card ${q.status === 'ACTIVE' ? 'level-active' : q.status === 'LOCKED' ? 'level-locked' : ''}`}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span style={{ fontSize: '12px', fontWeight: 800, color: '#f59e0b' }}>STAGE 0{q.lvl}</span>
                    <span className={`badge ${q.status === 'COMPLETED' ? 'badge-emerald' : q.status === 'ACTIVE' ? 'badge-cyan' : 'badge-purple'}`}>
                      {q.status}
                    </span>
                  </div>
                  <h4 style={{ fontSize: '15px', fontWeight: 800, color: '#f8fafc', marginBottom: '6px' }}>{q.title}</h4>
                  <p style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '12px' }}>{q.desc}</p>
                  <div style={{ fontSize: '11px', fontWeight: 700, color: '#38bdf8' }}>{q.creds} Milestone</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* -------------------------------------------------------------------
            TAB 5: Degree Pathway Planner Grid (The Matrix)
        -------------------------------------------------------------------- */}
        {activeTab === 'pathway' && (
          <div>
            <div className="glass-panel" style={{ padding: '20px', marginBottom: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <div style={{ display: 'center', alignItems: 'center', gap: '8px' }}>
                  <Compass size={18} color="#10b981" />
                  <h3 style={{ fontSize: '16px', fontWeight: 800, color: '#f8fafc' }}>
                    Topological Degree Pathway (The Matrix Engine)
                  </h3>
                </div>
                <span className="badge badge-emerald">OPTIMAL 160-CREDIT PLAN</span>
              </div>
              <p style={{ fontSize: '13px', color: '#94a3b8' }}>
                {pipelineData?.degree_pathway?.matrix_analysis || 'All prerequisite dependencies topologically sorted up to graduation.'}
              </p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
              {(pipelineData?.degree_pathway?.path_sequence || []).map((step) => (
                <div key={step.step_number} className="glass-panel" style={{ padding: '18px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                    <span style={{ fontSize: '14px', fontWeight: 800, color: '#38bdf8' }}>{step.step_label}</span>
                    <span className="badge badge-cyan">{step.step_total_credits_or_effort} Credits</span>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {(step.nodes_details || step.nodes_to_complete || []).map((item, idx) => {
                      const sid = typeof item === 'string' ? item : item.subject_id;
                      const sname = typeof item === 'string' ? item : item.name;
                      const creds = typeof item === 'string' ? 3 : item.credits;

                      return (
                        <div key={idx} style={{ padding: '10px', background: 'rgba(15,23,42,0.7)', borderRadius: '8px', border: '1px solid rgba(59,130,246,0.15)' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', fontWeight: 700, color: '#38bdf8', marginBottom: '2px' }}>
                            <span>{sid}</span>
                            <span>{creds} CR</span>
                          </div>
                          <div style={{ fontSize: '12px', color: '#f1f5f9', fontWeight: 600 }}>{sname}</div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* -------------------------------------------------------------------
            TAB 6: Conflict & Risk Diagnostic Center (Sentinel)
        -------------------------------------------------------------------- */}
        {activeTab === 'conflicts' && (
          <div>
            <div className="glass-panel" style={{ padding: '20px', marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <AlertTriangle size={18} color="#f43f5e" />
                  <h3 style={{ fontSize: '16px', fontWeight: 800, color: '#f8fafc' }}>
                    Formal Constraint & Risk Diagnostic Center (Sentinel Agent)
                  </h3>
                </div>
                <p style={{ fontSize: '13px', color: '#94a3b8' }}>
                  {pipelineData?.conflict_report?.summary || 'Formal constraint audit complete.'}
                </p>
              </div>

              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '2px' }}>Graduation Risk Index</div>
                <div style={{ fontSize: '24px', fontWeight: 900, color: (pipelineData?.conflict_report?.graduation_risk_score || 0) > 0.5 ? '#fb7185' : '#34d399' }}>
                  {((pipelineData?.conflict_report?.graduation_risk_score || 0) * 100).toFixed(0)}%
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {(pipelineData?.conflict_report?.conflicts || []).length > 0 ? (
                pipelineData.conflict_report.conflicts.map((conf, i) => (
                  <div key={i} className="glass-panel" style={{ padding: '18px', borderLeft: conf.severity === 'CRITICAL' ? '4px solid #f43f5e' : '4px solid #f59e0b' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                      <span className={`badge ${conf.severity === 'CRITICAL' ? 'badge-rose' : 'badge-amber'}`}>
                        {conf.conflict_type}
                      </span>
                      <span style={{ fontSize: '11px', color: '#38bdf8', fontFamily: 'monospace' }}>
                        {conf.policy_citation}
                      </span>
                    </div>

                    <div style={{ fontSize: '14px', fontWeight: 700, color: '#f8fafc', marginBottom: '6px' }}>
                      {conf.description}
                    </div>

                    <div style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '12px' }}>
                      💡 <strong style={{ color: '#cbd5e1' }}>Remedy:</strong> {conf.remedy_recommendation}
                    </div>

                    <button
                      onClick={() => {
                        setWaiverCourseId(conf.affected_courses?.[0] || 'Sub_4_1');
                        setIsWaiverModalOpen(true);
                      }}
                      className="btn-glitter"
                      style={{ padding: '6px 14px', fontSize: '11px' }}
                    >
                      Petition Faculty Waiver
                    </button>
                  </div>
                ))
              ) : (
                <div className="glass-panel" style={{ padding: '36px', textAlign: 'center', color: '#34d399' }}>
                  <CheckCircle2 size={36} style={{ margin: '0 auto 12px auto' }} />
                  <div style={{ fontSize: '16px', fontWeight: 700 }}>Zero Prerequisite or Credit Conflicts Detected!</div>
                  <div style={{ fontSize: '13px', color: '#94a3b8', marginTop: '4px' }}>All enrollment rules and curriculum invariants are cleared for this profile.</div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* -------------------------------------------------------------------
            TAB 7: Citation-Traceable AI Advisor Chat (Nexus + Codex)
        -------------------------------------------------------------------- */}
        {activeTab === 'chat' && (
          <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', height: '680px', padding: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', paddingBottom: '14px', borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
              <Brain size={20} color="#06b6d4" />
              <div>
                <div style={{ fontSize: '15px', fontWeight: 800, color: '#f8fafc' }}>Nexus Grounded Advising Chat</div>
                <div style={{ fontSize: '11px', color: '#94a3b8' }}>Powered by Codex Graph-RAG policy retrieval & Sentinel constraint proofs</div>
              </div>
            </div>

            {/* Quick Prompt Chips */}
            <div style={{ display: 'flex', gap: '8px', padding: '10px 0', overflowX: 'auto' }}>
              {[
                'Can I take 24 credits next semester?',
                'How to get a waiver for a prerequisite?',
                'What is the course substitution for Web Dev?',
                'Am I eligible for Capstone Project?'
              ].map((chip, i) => (
                <button
                  key={i}
                  onClick={() => {
                    setChatInput(chip);
                  }}
                  style={{
                    padding: '4px 10px',
                    borderRadius: '9999px',
                    background: 'rgba(6,182,212,0.12)',
                    border: '1px solid rgba(6,182,212,0.3)',
                    color: '#22d3ee',
                    fontSize: '11px',
                    fontWeight: 700,
                    cursor: 'pointer',
                    whiteSpace: 'nowrap'
                  }}
                >
                  💬 {chip}
                </button>
              ))}
            </div>

            {/* Chat History */}
            <div style={{ flex: 1, overflowY: 'auto', padding: '12px 0', display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {chatMessages.map((msg, idx) => (
                <div key={idx} className={msg.sender === 'Student' ? 'chat-bubble-user' : 'chat-bubble-agent'} style={{ maxWidth: '80%' }}>
                  <div style={{ fontSize: '11px', fontWeight: 800, color: msg.sender === 'Student' ? '#93c5fd' : '#22d3ee', marginBottom: '4px' }}>
                    {msg.sender}
                  </div>
                  <div style={{ fontSize: '13px', lineHeight: '1.5' }}>{msg.text}</div>
                  {msg.citations && msg.citations.length > 0 && (
                    <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginTop: '8px' }}>
                      {msg.citations.map((cite, cIdx) => (
                        <span key={cIdx} className="badge badge-purple" style={{ fontSize: '10px' }}>
                          📜 {cite}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
              {isChatSending && (
                <div className="chat-bubble-agent" style={{ width: '150px', fontSize: '12px', color: '#94a3b8' }}>
                  Codex retrieving policy...
                </div>
              )}
            </div>

            {/* Chat Input Box */}
            <form onSubmit={handleSendChat} style={{ display: 'flex', gap: '10px', paddingTop: '12px', borderTop: '1px solid rgba(255,255,255,0.08)' }}>
              <input
                type="text"
                placeholder="Ask Nexus about prerequisite waivers, credit limits, capstones, or electives..."
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                style={{
                  flex: 1,
                  padding: '12px 16px',
                  borderRadius: '8px',
                  border: '1px solid rgba(59,130,246,0.3)',
                  background: 'rgba(15,23,42,0.9)',
                  color: '#f8fafc',
                  fontSize: '13px',
                  outline: 'none'
                }}
              />
              <button type="submit" disabled={isChatSending} className="btn-glitter">
                <Send size={16} /> Send
              </button>
            </form>
          </div>
        )}

        {/* -------------------------------------------------------------------
            TAB 8: Faculty Governance & Petition Portal
        -------------------------------------------------------------------- */}
        {activeTab === 'faculty' && (
          <div>
            <div className="glass-panel" style={{ padding: '20px', marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <ShieldCheck size={20} color="#a855f7" />
                  <h3 style={{ fontSize: '16px', fontWeight: 800, color: '#f8fafc' }}>
                    Faculty Override & Formal Petition Review Portal
                  </h3>
                </div>
                <p style={{ fontSize: '13px', color: '#94a3b8' }}>
                  Manage student exception requests for prerequisite waivers, credit overloads, and substitutions.
                </p>
              </div>

              <div style={{ display: 'flex', gap: '8px' }}>
                {['ALL', 'PENDING', 'APPROVED', 'REJECTED'].map((f) => (
                  <button
                    key={f}
                    onClick={() => setFacultyFilter(f)}
                    style={{
                      padding: '6px 12px',
                      borderRadius: '6px',
                      border: 'none',
                      background: facultyFilter === f ? '#a855f7' : 'rgba(255,255,255,0.08)',
                      color: '#fff',
                      fontSize: '11px',
                      fontWeight: 800,
                      cursor: 'pointer'
                    }}
                  >
                    {f}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {facultyPetitions
                .filter((p) => facultyFilter === 'ALL' || p.status === facultyFilter)
                .map((pet) => (
                  <div key={pet.petition_id} className="glass-panel" style={{ padding: '20px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <span style={{ fontSize: '13px', fontWeight: 800, color: '#38bdf8', fontFamily: 'monospace' }}>
                          {pet.petition_id}
                        </span>
                        <span className={`badge ${pet.status === 'APPROVED' ? 'badge-emerald' : pet.status === 'REJECTED' ? 'badge-rose' : 'badge-amber'}`}>
                          {pet.status}
                        </span>
                        <span className="badge badge-purple">{pet.petition_type}</span>
                      </div>
                      <span style={{ fontSize: '11px', color: '#64748b', fontFamily: 'monospace' }}>
                        HASH: {pet.audit_hash?.substring(0, 16)}...
                      </span>
                    </div>

                    <div style={{ fontSize: '14px', fontWeight: 700, color: '#f8fafc', marginBottom: '4px' }}>
                      {pet.student_name} ({pet.reg_no}) ➔ Target Course: {pet.subject_id} {pet.subject_name ? `(${pet.subject_name})` : ''}
                    </div>

                    <div style={{ fontSize: '13px', color: '#cbd5e1', marginBottom: '12px' }}>
                      "{pet.reason}"
                    </div>

                    {pet.faculty_remarks && (
                      <div style={{ fontSize: '12px', color: '#34d399', background: 'rgba(16,185,129,0.1)', padding: '8px 12px', borderRadius: '6px', marginBottom: '12px' }}>
                        🏛️ <strong>Faculty Remarks:</strong> {pet.faculty_remarks}
                      </div>
                    )}

                    {pet.status === 'PENDING' && (
                      <div style={{ display: 'flex', gap: '10px' }}>
                        <button
                          onClick={() => handleFacultyAction(pet.petition_id, 'APPROVE')}
                          style={{
                            padding: '8px 16px',
                            borderRadius: '6px',
                            background: '#10b981',
                            color: '#fff',
                            fontWeight: 800,
                            fontSize: '12px',
                            border: 'none',
                            cursor: 'pointer'
                          }}
                        >
                          Approve Exception
                        </button>
                        <button
                          onClick={() => handleFacultyAction(pet.petition_id, 'REJECT')}
                          style={{
                            padding: '8px 16px',
                            borderRadius: '6px',
                            background: '#f43f5e',
                            color: '#fff',
                            fontWeight: 800,
                            fontSize: '12px',
                            border: 'none',
                            cursor: 'pointer'
                          }}
                        >
                          Reject
                        </button>
                      </div>
                    )}
                  </div>
                ))}
            </div>
          </div>
        )}
      </main>

      {/* Faculty Waiver Petition Modal */}
      {isWaiverModalOpen && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(10px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
          <div className="glass-panel" style={{ width: '500px', padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 800, color: '#f8fafc' }}>Submit Faculty Exception Petition</h3>
              <button onClick={() => setIsWaiverModalOpen(false)} style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleSubmitWaiver}>
              <div style={{ marginBottom: '14px' }}>
                <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Target Course ID</label>
                <input
                  type="text"
                  value={waiverCourseId}
                  onChange={(e) => setWaiverCourseId(e.target.value)}
                  style={{ width: '100%', padding: '10px', borderRadius: '6px', background: 'rgba(15,23,42,0.9)', border: '1px solid rgba(59,130,246,0.3)', color: '#f8fafc', fontSize: '13px' }}
                />
              </div>

              <div style={{ marginBottom: '14px' }}>
                <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Petition Category</label>
                <select
                  value={waiverType}
                  onChange={(e) => setWaiverType(e.target.value)}
                  style={{ width: '100%', padding: '10px', borderRadius: '6px', background: 'rgba(15,23,42,0.9)', border: '1px solid rgba(59,130,246,0.3)', color: '#f8fafc', fontSize: '13px' }}
                >
                  <option value="PREREQUISITE_WAIVER">Prerequisite Waiver</option>
                  <option value="CREDIT_OVERLOAD">Credit Overload (24 CR)</option>
                  <option value="COURSE_SUBSTITUTION">Course Substitution</option>
                  <option value="SPECIAL_PERMISSION">Special Department Permission</option>
                </select>
              </div>

              <div style={{ marginBottom: '18px' }}>
                <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Academic Justification & Evidence</label>
                <textarea
                  rows={4}
                  placeholder="Provide details regarding prior certifications, MOOC credentials, or scheduling constraints..."
                  value={waiverReason}
                  onChange={(e) => setWaiverReason(e.target.value)}
                  required
                  style={{ width: '100%', padding: '10px', borderRadius: '6px', background: 'rgba(15,23,42,0.9)', border: '1px solid rgba(59,130,246,0.3)', color: '#f8fafc', fontSize: '13px' }}
                ></textarea>
              </div>

              <button
                type="submit"
                className="btn-glitter"
                style={{ width: '100%', padding: '12px', borderRadius: '8px', justifyContent: 'center' }}
              >
                <FileText size={16} /> Sign & Submit Petition with SHA-256 Hash
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
