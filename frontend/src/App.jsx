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
  Server
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
  let bgGradient = 'rgba(13, 18, 30, 0.95)';
  let statusBadge = <span className="badge badge-blue">Available</span>;

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
          ? '0 0 18px rgba(6, 182, 212, 0.3)'
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

      <div style={{ fontSize: '13px', fontWeight: 600, color: '#f1f5f9', marginBottom: '8px', lineHeight: '1.3' }}>
        {data.label}
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '6px', fontSize: '11px', color: '#94a3b8' }}>
        <span>Sem {data.semester}</span>
        <span style={{ fontWeight: 700, color: '#cbd5e1' }}>{data.credits} Credits</span>
      </div>

      <Handle type="source" position={Position.Right} style={{ background: '#06b6d4', width: 8, height: 8 }} />
    </div>
  );
};

const nodeTypes = {
  customCourseNode: CustomCourseNode
};

// ---------------------------------------------------------------------------
// 2. Multi-Agent Metadata Directory
// ---------------------------------------------------------------------------
const AGENTS_INFO = [
  {
    id: 'nexus',
    name: 'Nexus (Agent 01)',
    role: 'Front Desk & Central Supervisor',
    desc: 'Orchestrates multi-agent routing, student intake, and final narrative synthesis.',
    color: '#06b6d4',
    icon: Brain,
    avatar: '/assets/nexus.png'
  },
  {
    id: 'state',
    name: 'State (Agent 04)',
    role: 'The Background Check Synthesizer',
    desc: 'Validates immutable student history from DBMS, scrubs PII, and assigns standing.',
    color: '#3b82f6',
    icon: ShieldCheck,
    avatar: '/assets/state.png'
  },
  {
    id: 'matrix',
    name: 'The Matrix (Agent 02)',
    role: 'Graph Navigator & Degree Pathfinder',
    desc: 'Computes topological prerequisite paths, gateway chokepoints, and degree steps.',
    color: '#10b981',
    icon: Compass,
    avatar: '/assets/matrix.png'
  },
  {
    id: 'sentinel',
    name: 'Sentinel (Agent 06)',
    role: 'Formal Constraint & Faculty Verifier',
    desc: 'Enforces credit bounds (12-24 CR), graduation risks, and SHA-256 faculty petitions.',
    color: '#f43f5e',
    icon: AlertTriangle,
    avatar: '/assets/vector.png'
  },
  {
    id: 'codex',
    name: 'Codex (Agent 05)',
    role: 'Graph-RAG Policy & Citation Engine',
    desc: 'Retrieves verifiable regulatory clauses for zero-hallucination grounded citations.',
    color: '#a855f7',
    icon: BookOpen,
    avatar: '/assets/codex.png'
  },
  {
    id: 'vector',
    name: 'Vector (Agent 03)',
    role: 'Strategic Career Momentum Engine',
    desc: 'Aligns 10 industry tracks with tailored capstone projects, milestones, and certifications.',
    color: '#f59e0b',
    icon: TrendingUp,
    avatar: '/assets/vector.png'
  }
];

export default function App() {
  // Navigation & View States
  const [currentView, setCurrentView] = useState('login'); // 'login' | 'dashboard'
  const [activeTab, setActiveTab] = useState('graph'); // 'graph' | 'pathway' | 'conflicts' | 'career' | 'chat' | 'faculty'
  const [portalMode, setPortalMode] = useState('student'); // 'student' | 'faculty'
  const [loadingProgress, setLoadingProgress] = useState(0);

  // Student State
  const [selectedStudentId, setSelectedStudentId] = useState('REG1001');
  const [customRegInput, setCustomRegInput] = useState('');
  const [studentsList, setStudentsList] = useState([]);
  const [studentProfile, setStudentProfile] = useState(null);

  // Multi-Agent Pipeline Data
  const [pipelineData, setPipelineData] = useState(null);
  const [isPipelineRunning, setIsPipelineRunning] = useState(false);
  const [activeAgentIndex, setActiveAgentIndex] = useState(-1);

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
  // INITIALIZATION: Fetch Students Catalog & Run Loading Sequence
  // -------------------------------------------------------------------------
  useEffect(() => {
    let progress = 0;
    const interval = setInterval(() => {
      progress += 15;
      if (progress >= 100) {
        setLoadingProgress(100);
        clearInterval(interval);
      } else {
        setLoadingProgress(progress);
      }
    }, 90);

    // Fetch Students List from API
    fetch(`${API_BASE_URL}/students`)
      .then((r) => r.json())
      .then((data) => {
        const list = Array.isArray(data) ? data : data.students || [];
        setStudentsList(list);
      })
      .catch((err) => console.log('Using default mock student pool:', err));

    return () => clearInterval(interval);
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
      }

      // Step simulation pulses
      setTimeout(() => setActiveAgentIndex(1), 200);
      setTimeout(() => setActiveAgentIndex(2), 400);

      // 2. Fetch Knowledge Graph for React Flow
      const graphRes = await fetch(`${API_BASE_URL}/graph/curriculum?student_id=${studentId}`);
      if (graphRes.ok) {
        const graphData = await graphRes.json();
        
        // Ensure proper node coordinates & styling
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

      setTimeout(() => setActiveAgentIndex(3), 600);
      setTimeout(() => setActiveAgentIndex(4), 800);

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

      setTimeout(() => setActiveAgentIndex(5), 1000);
    } catch (err) {
      console.error('Pipeline execution warning:', err);
    } finally {
      setTimeout(() => {
        setIsPipelineRunning(false);
        setActiveAgentIndex(-1);
      }, 1200);
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
        { sender: 'Nexus Advisor', text: 'Error connecting to agent core. Please ensure backend is running.' }
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
        alert(`Petition submitted successfully with SHA-256 Audit Hash: ${newRecord.audit_hash.substring(0, 12)}...`);
      }
    } catch (err) {
      alert('Error submitting faculty petition.');
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
  // RENDER: 1. Loading Sequence Screen
  // -------------------------------------------------------------------------
  if (loadingProgress < 100) {
    return (
      <div className="cyber-background" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ position: 'relative', marginBottom: '24px' }}>
          <div style={{ width: '84px', height: '84px', borderRadius: '50%', background: 'rgba(6,182,212,0.15)', border: '2px solid #06b6d4', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 35px rgba(6,182,212,0.5)' }}>
            <Brain size={44} color="#22d3ee" />
          </div>
        </div>
        <h1 style={{ fontSize: '28px', fontWeight: 800, letterSpacing: '-0.02em', color: '#f8fafc', marginBottom: '8px' }}>
          <span style={{ color: '#06b6d4' }}>Omega</span> Pathway Intelligence
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '14px', marginBottom: '24px' }}>
          Initializing Decentralized Graph-RAG & Prerequisite Multi-Agent Cores...
        </p>

        <div style={{ width: '340px', height: '6px', background: 'rgba(255,255,255,0.08)', borderRadius: '9999px', overflow: 'hidden' }}>
          <div style={{ width: `${loadingProgress}%`, height: '100%', background: 'linear-gradient(90deg, #06b6d4, #3b82f6, #a855f7)', transition: 'width 0.15s ease' }}></div>
        </div>
        <span style={{ fontSize: '11px', color: '#64748b', marginTop: '10px', fontFamily: 'monospace' }}>
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
      <div className="cyber-background" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '36px 16px' }}>
        <div style={{ maxWidth: '1020px', width: '100%' }}>
          {/* Header */}
          <div style={{ textAlign: 'center', marginBottom: '36px' }}>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '6px 16px', borderRadius: '9999px', background: 'rgba(6,182,212,0.1)', border: '1px solid rgba(6,182,212,0.3)', color: '#22d3ee', fontSize: '12px', fontWeight: 700, marginBottom: '16px' }}>
              <Sparkles size={14} /> AUTONOMOUS MULTI-AGENT ADVISING PLATFORM
            </div>
            <h1 style={{ fontSize: '42px', fontWeight: 900, letterSpacing: '-0.03em', color: '#f8fafc', marginBottom: '12px' }}>
              <span style={{ color: '#06b6d4' }}>Omega</span> Academic Pathway Intelligence
            </h1>
            <p style={{ color: '#94a3b8', fontSize: '16px', maxWidth: '680px', margin: '0 auto', lineHeight: '1.5' }}>
              Decentralized Graph-RAG Academic Advising, Prerequisite Conflict Resolution & Faculty Exception Governance.
            </p>
          </div>

          {/* Mode Switcher */}
          <div style={{ display: 'flex', justifyContent: 'center', gap: '14px', marginBottom: '32px' }}>
            <button
              onClick={() => setPortalMode('student')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '12px 24px',
                borderRadius: '10px',
                border: portalMode === 'student' ? '1.5px solid #06b6d4' : '1px solid rgba(255,255,255,0.1)',
                background: portalMode === 'student' ? 'rgba(6,182,212,0.15)' : 'rgba(15,23,42,0.6)',
                color: portalMode === 'student' ? '#22d3ee' : '#94a3b8',
                fontWeight: 700,
                cursor: 'pointer',
                transition: 'all 0.2s'
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
                background: portalMode === 'faculty' ? 'rgba(168,85,247,0.15)' : 'rgba(15,23,42,0.6)',
                color: portalMode === 'faculty' ? '#c084fc' : '#94a3b8',
                fontWeight: 700,
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              <ShieldCheck size={18} /> Faculty Exception Portal
            </button>
          </div>

          {/* Student Selection Container */}
          <div className="glass-panel" style={{ padding: '28px', marginBottom: '28px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '14px' }}>
              <div>
                <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#f8fafc', marginBottom: '4px' }}>
                  Select Student Profile for Simulation
                </h3>
                <p style={{ fontSize: '13px', color: '#94a3b8' }}>
                  Choose from 50 simulated profiles across 4 semesters and 10 tech career tracks.
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
                  style={{
                    padding: '10px 20px',
                    borderRadius: '8px',
                    background: 'linear-gradient(135deg, #06b6d4, #3b82f6)',
                    color: '#f8fafc',
                    fontWeight: 700,
                    border: 'none',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}
                >
                  Enter Session <ArrowRight size={16} />
                </button>
              </div>
            </div>

            {/* Quick Demo Cards Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(290px, 1fr))', gap: '16px' }}>
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
      {/* Top Cyber Navigation Bar */}
      <header style={{ height: '68px', borderBottom: '1px solid rgba(59,130,246,0.18)', background: 'rgba(10,13,20,0.85)', backdropFilter: 'blur(16px)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 24px', position: 'sticky', top: 0, zIndex: 50 }}>
        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }} onClick={() => setCurrentView('login')}>
          <div style={{ width: '38px', height: '38px', borderRadius: '10px', background: 'rgba(6,182,212,0.15)', border: '1.5px solid #06b6d4', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Brain size={22} color="#22d3ee" />
          </div>
          <div>
            <div style={{ fontSize: '17px', fontWeight: 800, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ color: '#06b6d4' }}>Omega</span> Pathway Intelligence
              <span style={{ fontSize: '10px', padding: '2px 6px', borderRadius: '4px', background: 'rgba(6,182,212,0.2)', color: '#22d3ee', fontWeight: 700 }}>v2.0</span>
            </div>
            <div style={{ fontSize: '11px', color: '#64748b' }}>Decentralized Multi-Agent Platform</div>
          </div>
        </div>

        {/* Live Active Student Pill */}
        <div className="glass-panel" style={{ display: 'flex', alignItems: 'center', gap: '16px', padding: '8px 16px', borderRadius: '9999px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div className="pulse-dot"></div>
            <span style={{ fontSize: '12px', fontWeight: 800, color: '#38bdf8', fontFamily: 'monospace' }}>
              {selectedStudentId}
            </span>
          </div>
          <div style={{ height: '14px', width: '1px', background: 'rgba(255,255,255,0.1)' }}></div>
          <span style={{ fontSize: '13px', fontWeight: 700, color: '#f8fafc' }}>{studentName}</span>
          <span className="badge badge-cyan">Sem {studentSem}</span>
          <span style={{ fontSize: '12px', fontWeight: 700, color: studentCGPA >= 8.5 ? '#34d399' : studentCGPA < 6.0 ? '#fb7185' : '#38bdf8' }}>
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
              cursor: isPipelineRunning ? 'not-allowed' : 'pointer'
            }}
          >
            <RotateCcw size={14} className={isPipelineRunning ? 'animate-spin' : ''} />
            {isPipelineRunning ? 'Running Pipeline...' : 'Re-Run Agents'}
          </button>

          <button
            onClick={() => setCurrentView('login')}
            style={{
              padding: '8px 14px',
              borderRadius: '8px',
              border: '1px solid rgba(255,255,255,0.12)',
              background: 'rgba(15,23,42,0.8)',
              color: '#94a3b8',
              fontWeight: 600,
              fontSize: '12px',
              cursor: 'pointer'
            }}
          >
            Switch Student
          </button>
        </div>
      </header>

      {/* Multi-Agent Dynamic Live Telemetry Ribbon */}
      <section style={{ background: 'rgba(13,18,30,0.95)', borderBottom: '1px solid rgba(59,130,246,0.15)', padding: '12px 24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', fontWeight: 800, color: '#38bdf8' }}>
            <Activity size={14} /> AUTONOMOUS MULTI-AGENT TELEMETRY PIPELINE
          </div>
          <span style={{ fontSize: '11px', color: '#64748b', fontFamily: 'monospace' }}>
            SESSION HASH: {pipelineData?.session_id || 'SES_LIVE_READY'}
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
                style={{
                  padding: '10px 12px',
                  border: isActive ? `1.5px solid ${ag.color}` : '1px solid rgba(59,130,246,0.15)',
                  background: isActive ? 'rgba(6,182,212,0.15)' : 'rgba(15,23,42,0.85)'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <IconComp size={14} color={ag.color} />
                    <span style={{ fontSize: '11px', fontWeight: 800, color: '#f8fafc' }}>{ag.name.split(' ')[0]}</span>
                  </div>
                  <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: ag.color }}></span>
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
      <div style={{ padding: '16px 24px 0 24px', display: 'flex', gap: '8px', borderBottom: '1px solid rgba(59,130,246,0.15)' }}>
        {[
          { id: 'graph', label: 'Curriculum Knowledge Graph', icon: Layers },
          { id: 'pathway', label: 'Degree Pathway Planner', icon: Compass },
          { id: 'conflicts', label: 'Conflict & Risk Resolver', icon: AlertTriangle, badge: pipelineData?.conflict_report?.critical_count },
          { id: 'career', label: 'Career Velocity Blueprint', icon: TrendingUp },
          { id: 'chat', label: 'Citation-Traceable AI Chat', icon: MessageSquare },
          { id: 'faculty', label: 'Faculty Override Portal', icon: ShieldCheck, badge: facultyPetitions.filter((p) => p.status === 'PENDING').length }
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
                borderColor: isCurrent ? 'rgba(6,182,212,0.4)' : 'transparent',
                borderBottom: isCurrent ? '2px solid #06b6d4' : 'none',
                background: isCurrent ? 'rgba(15,23,42,0.9)' : 'transparent',
                color: isCurrent ? '#22d3ee' : '#94a3b8',
                fontWeight: 700,
                fontSize: '13px',
                cursor: 'pointer',
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
          <div style={{ height: '720px', width: '100%', position: 'relative', borderRadius: '14px', overflow: 'hidden', border: '1px solid rgba(59,130,246,0.2)' }}>
            {/* Graph Control Bar Overlay */}
            <div style={{ position: 'absolute', top: '16px', left: '16px', zIndex: 10, display: 'flex', gap: '8px' }} className="glass-panel">
              <button
                onClick={() => setGraphFilter('ALL')}
                style={{ padding: '6px 12px', borderRadius: '6px', border: 'none', background: graphFilter === 'ALL' ? '#06b6d4' : 'transparent', color: '#fff', fontSize: '11px', fontWeight: 700, cursor: 'pointer' }}
              >
                All 60 Courses
              </button>
              <button
                onClick={() => setGraphFilter('BOTTLENECKS')}
                style={{ padding: '6px 12px', borderRadius: '6px', border: 'none', background: graphFilter === 'BOTTLENECKS' ? '#f59e0b' : 'transparent', color: '#fff', fontSize: '11px', fontWeight: 700, cursor: 'pointer' }}
              >
                Chokepoints
              </button>
            </div>

            {/* Semester Header Markers */}
            <div style={{ position: 'absolute', top: '16px', right: '16px', zIndex: 10, display: 'flex', gap: '16px' }} className="glass-panel">
              <div style={{ padding: '6px 12px', fontSize: '11px', color: '#94a3b8', display: 'flex', gap: '12px' }}>
                <span style={{ color: '#10b981', display: 'flex', alignItems: 'center', gap: '4px' }}>● Completed</span>
                <span style={{ color: '#06b6d4', display: 'flex', alignItems: 'center', gap: '4px' }}>● Enrolled</span>
                <span style={{ color: '#3b82f6', display: 'flex', alignItems: 'center', gap: '4px' }}>● Available</span>
                <span style={{ color: '#f59e0b', display: 'flex', alignItems: 'center', gap: '4px' }}>★ Gateway Chokepoint</span>
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
              <Background color="#1e293b" gap={20} size={1} />
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
                <h4 style={{ fontSize: '15px', fontWeight: 700, color: '#f8fafc', marginBottom: '8px' }}>{selectedNodeData.label}</h4>
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
                      <div key={i} style={{ fontSize: '11px', color: '#22d3ee', background: 'rgba(6,182,212,0.1)', padding: '4px 8px', borderRadius: '4px', marginBottom: '4px' }}>
                        ⇄ {sub.EquivalentSubjectID}: {sub.EquivalentName}
                      </div>
                    ))
                  ) : (
                    <div style={{ fontSize: '11px', color: '#64748b' }}>No direct elective substitutions configured.</div>
                  )}
                </div>

                <button
                  onClick={() => setIsWaiverModalOpen(true)}
                  style={{
                    width: '100%',
                    padding: '8px',
                    borderRadius: '6px',
                    background: 'linear-gradient(135deg, #a855f7, #3b82f6)',
                    color: '#fff',
                    fontWeight: 700,
                    fontSize: '12px',
                    border: 'none',
                    cursor: 'pointer'
                  }}
                >
                  Request Faculty Waiver Petition
                </button>
              </div>
            )}
          </div>
        )}

        {/* -------------------------------------------------------------------
            TAB 2: Degree Pathway Planner Grid (Agent 2 - The Matrix)
        -------------------------------------------------------------------- */}
        {activeTab === 'pathway' && (
          <div>
            <div className="glass-panel" style={{ padding: '20px', marginBottom: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
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
            TAB 3: Conflict & Risk Diagnostic Center (Agent 6 - Sentinel)
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
                      style={{
                        padding: '6px 12px',
                        borderRadius: '6px',
                        background: 'rgba(244,63,94,0.15)',
                        border: '1px solid rgba(244,63,94,0.3)',
                        color: '#fb7185',
                        fontSize: '11px',
                        fontWeight: 700,
                        cursor: 'pointer'
                      }}
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
            TAB 4: Career Velocity Blueprint (Agent 3 - Vector)
        -------------------------------------------------------------------- */}
        {activeTab === 'career' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '20px' }}>
            <div className="glass-panel" style={{ padding: '24px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                <TrendingUp size={20} color="#f59e0b" />
                <h3 style={{ fontSize: '18px', fontWeight: 800, color: '#f8fafc' }}>
                  Strategic Momentum Blueprint (Vector Engine)
                </h3>
              </div>

              <div style={{ marginBottom: '18px' }}>
                <div style={{ fontSize: '12px', fontWeight: 700, color: '#fbbf24', textTransform: 'uppercase', marginBottom: '4px' }}>
                  Actionable Capstone Project
                </div>
                <div style={{ fontSize: '14px', color: '#f1f5f9', background: 'rgba(15,23,42,0.8)', padding: '14px', borderRadius: '8px', border: '1px solid rgba(59,130,246,0.15)' }}>
                  {pipelineData?.career_vector?.actionable_project || 'Construct an end-to-end predictive machine learning pipeline.'}
                </div>
              </div>

              <div style={{ marginBottom: '18px' }}>
                <div style={{ fontSize: '12px', fontWeight: 700, color: '#38bdf8', textTransform: 'uppercase', marginBottom: '4px' }}>
                  Target Internship Roles
                </div>
                <div style={{ fontSize: '14px', color: '#f1f5f9', background: 'rgba(15,23,42,0.8)', padding: '14px', borderRadius: '8px', border: '1px solid rgba(59,130,246,0.15)' }}>
                  {pipelineData?.career_vector?.internship_target || 'Target Applied Data Scientist and Quantitative Analytics Intern positions.'}
                </div>
              </div>

              <div>
                <div style={{ fontSize: '12px', fontWeight: 700, color: '#34d399', textTransform: 'uppercase', marginBottom: '4px' }}>
                  Next-Level Milestone
                </div>
                <div style={{ fontSize: '14px', color: '#f1f5f9', background: 'rgba(15,23,42,0.8)', padding: '14px', borderRadius: '8px', border: '1px solid rgba(59,130,246,0.15)' }}>
                  {pipelineData?.career_vector?.next_level_milestone || 'Achieve Kaggle Expert rank across benchmark challenges.'}
                </div>
              </div>
            </div>

            <div className="glass-panel" style={{ padding: '24px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                <Award size={20} color="#a855f7" />
                <h3 style={{ fontSize: '18px', fontWeight: 800, color: '#f8fafc' }}>
                  Recommended Industry Certifications
                </h3>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {(pipelineData?.career_vector?.target_certifications || [
                  'AWS Certified Machine Learning - Specialty',
                  'Google Professional Data Engineer',
                  'Databricks Certified Associate Developer'
                ]).map((cert, idx) => (
                  <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '12px', borderRadius: '8px', background: 'rgba(168,85,247,0.1)', border: '1px solid rgba(168,85,247,0.25)', color: '#c084fc', fontSize: '13px', fontWeight: 600 }}>
                    <CheckCircle2 size={16} />
                    {cert}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* -------------------------------------------------------------------
            TAB 5: Citation-Traceable AI Advisor Chat (Nexus + Codex Graph-RAG)
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

            {/* Chat History */}
            <div style={{ flex: 1, overflowY: 'auto', padding: '16px 0', display: 'flex', flexDirection: 'column', gap: '12px' }}>
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
                <div className="chat-bubble-agent" style={{ width: '140px', fontSize: '12px', color: '#94a3b8' }}>
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
              <button
                type="submit"
                disabled={isChatSending}
                style={{
                  padding: '12px 20px',
                  borderRadius: '8px',
                  background: 'linear-gradient(135deg, #06b6d4, #3b82f6)',
                  color: '#f8fafc',
                  fontWeight: 700,
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

        {/* -------------------------------------------------------------------
            TAB 6: Faculty Override & Petition Review Portal
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

              <span className="badge badge-purple">IMMUTABLE SHA-256 AUDIT LOG</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {facultyPetitions.map((pet) => (
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
                    {pet.student_name} ({pet.reg_no}) ➔ Course: {pet.subject_id} {pet.subject_name ? `(${pet.subject_name})` : ''}
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
                          padding: '6px 14px',
                          borderRadius: '6px',
                          background: '#10b981',
                          color: '#fff',
                          fontWeight: 700,
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
                          padding: '6px 14px',
                          borderRadius: '6px',
                          background: '#f43f5e',
                          color: '#fff',
                          fontWeight: 700,
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
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(8px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
          <div className="glass-panel" style={{ width: '480px', padding: '24px' }}>
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
                style={{
                  width: '100%',
                  padding: '12px',
                  borderRadius: '8px',
                  background: 'linear-gradient(135deg, #06b6d4, #3b82f6)',
                  color: '#fff',
                  fontWeight: 700,
                  fontSize: '13px',
                  border: 'none',
                  cursor: 'pointer'
                }}
              >
                Sign & Submit Petition
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
