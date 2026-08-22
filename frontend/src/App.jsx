import { useState, useEffect, useRef, useCallback } from 'react';
import { User, KeyRound, ArrowRight, Brain, Cpu, MessageSquare, Briefcase, GraduationCap, Map as MapIcon, Sparkles, X } from 'lucide-react';
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  Handle,
  Position
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

// Custom hook for typewriter effect
const Typewriter = ({ text, delay = 30 }) => {
  const [currentText, setCurrentText] = useState('');
  
  useEffect(() => {
    let i = 0;
    setCurrentText('');
    const timer = setInterval(() => {
      if (i < text.length) {
        setCurrentText(prev => prev + text.charAt(i));
        i++;
      } else {
        clearInterval(timer);
      }
    }, delay);
    return () => clearInterval(timer);
  }, [text, delay]);

  return <span>{currentText}</span>;
};

// --- REACT FLOW NODE (TREASURE MAP STYLE) ---
const GodmodeCourseNode = ({ data, selected }) => {
  const isCompleted = data.status === 'COMPLETED';
  const isEnrolled = data.status === 'ENROLLED';
  const isBottleneck = data.is_bottleneck;
  const isTreasure = data.status === 'TREASURE';

  let bgClass = 'bg-white';
  let badgeText = 'AVAILABLE';
  let badgeColor = 'bg-gray-200 text-gray-600';
  
  if (isTreasure) {
    bgClass = 'bg-yellow-300';
    badgeText = 'ULTIMATE GOAL';
    badgeColor = 'bg-yellow-600 text-white';
  } else if (isCompleted) {
    bgClass = 'bg-green-300';
    badgeText = 'COMPLETED';
    badgeColor = 'bg-green-600 text-white';
  } else if (isEnrolled) {
    bgClass = 'bg-blue-300';
    badgeText = 'ENROLLED';
    badgeColor = 'bg-blue-600 text-white';
  } else if (isBottleneck) {
    bgClass = 'bg-red-200';
    badgeText = 'BOTTLENECK';
    badgeColor = 'bg-red-600 text-white';
  }

  return (
    <div className={`border-[6px] border-[#451a03] ${bgClass} p-4 shadow-[8px_8px_0_#78350f] w-64 transition-transform ${selected ? 'scale-110 border-yellow-500' : ''}`}>
      <Handle type="target" position={Position.Left} className="w-4 h-4 bg-[#451a03] rounded-none border-2 border-[#fcd34d] -ml-2" />
      
      <div className="flex justify-between items-start mb-2">
        <div className="title-text text-xs bg-[#451a03] text-white inline-block px-2 py-1">{data.subject_id}</div>
        <div className={`title-text text-[10px] px-2 py-1 border-[3px] border-[#451a03] ${badgeColor} shadow-[2px_2px_0_#451a03]`}>{badgeText}</div>
      </div>
      
      <div className="font-bold text-xl text-[#451a03] mb-3 leading-tight mt-2">{data.label}</div>
      
      {!isTreasure && (
        <div className="flex justify-between items-center text-sm font-bold border-t-[4px] border-[#451a03] pt-2 text-[#78350f]">
          <span>SEM {data.semester}</span>
          <span>{data.credits} CR</span>
        </div>
      )}
      
      <Handle type="source" position={Position.Right} className="w-4 h-4 bg-[#451a03] rounded-none border-2 border-[#fcd34d] -mr-2" />
    </div>
  );
};
const nodeTypes = { customCourseNode: GodmodeCourseNode };

export default function App() {
  const [view, setView] = useState('landing'); // landing, login, details, agent_chat, dashboard, knowledge_graph
  const [regNo, setRegNo] = useState('');
  const [name, setName] = useState('');
  
  // Landing Page Typewriter
  const [typewriterText, setTypewriterText] = useState('');
  const fullTitle = 'OMEGA';
  
  const studentDetails = {
    cgpa: 8.4,
    semester: 5,
    creditsEarned: 90,
    department: 'Computer Science'
  };

  const [chatInput, setChatInput] = useState('');
  const [goalSet, setGoalSet] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [pipelineStep, setPipelineStep] = useState(-1);

  // React Flow State
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  useEffect(() => {
    if (view === 'landing') {
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
    }
  }, [view]);

  const handleLogin = (e) => {
    e.preventDefault();
    if (regNo.trim() && name.trim()) {
      setView('details');
    }
  };

  const startAgentConsultation = () => {
    setView('agent_chat');
    setChatHistory([
      { sender: 'NEXUS', text: `Hello ${name}. I am Nexus, your AI Advisor. To build your academic pipeline, I need to know: what is your ultimate career goal?` }
    ]);
  };

  // 1. Goal Validation & Dynamic Subject Generation
  const validDomains = ['software', 'data', 'ai', 'cyber', 'security', 'machine learning', 'ml', 'cloud', 'systems', 'robotics', 'web', 'app', 'developer', 'engineer', 'frontend', 'backend', 'fullstack', 'game'];

  const getDynamicPath = (goal) => {
    const g = goal.toLowerCase();
    if (g.includes('data') || g.includes('ai') || g.includes('ml') || g.includes('machine learning')) {
      return [
        { sem: 'SEM 6', name: 'Intro to AI', delay: '0s' },
        { sem: 'SEM 7', name: 'Deep Learning', delay: '0.4s' },
        { sem: 'SEM 8', name: 'AI Capstone', delay: '0.8s' }
      ];
    }
    if (g.includes('cyber') || g.includes('security')) {
      return [
        { sem: 'SEM 6', name: 'Cryptography', delay: '0s' },
        { sem: 'SEM 7', name: 'Network Security', delay: '0.4s' },
        { sem: 'SEM 8', name: 'Cyber Capstone', delay: '0.8s' }
      ];
    }
    if (g.includes('game')) {
      return [
        { sem: 'SEM 6', name: 'Computer Graphics', delay: '0s' },
        { sem: 'SEM 7', name: 'Game Engine Architecture', delay: '0.4s' },
        { sem: 'SEM 8', name: 'Studio Capstone', delay: '0.8s' }
      ];
    }
    // Default / Software
    return [
      { sem: 'SEM 6', name: 'Data Structures II', delay: '0s' },
      { sem: 'SEM 7', name: 'System Design', delay: '0.4s' },
      { sem: 'SEM 8', name: 'Software Capstone', delay: '0.8s' }
    ];
  };

  const handleSendChat = (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    if (!goalSet) {
      const userGoal = chatInput;
      setChatHistory(prev => [...prev, { sender: 'YOU', text: userGoal }]);
      
      const isRelevant = validDomains.some(domain => userGoal.toLowerCase().includes(domain));

      setTimeout(() => {
        if (!isRelevant) {
          setChatHistory(prev => [
            ...prev,
            { sender: 'NEXUS', text: `ERROR: I am sorry, but there are no subjects relevant to "${userGoal}" available in this university's curriculum. Please choose an engineering or technology focused career goal.` }
          ]);
          setChatInput(''); // reset input
        } else {
          setGoalSet(true);
          setChatHistory(prev => [
            ...prev,
            { sender: 'NEXUS', text: `Goal validated: "${userGoal}". All prerequisite subjects are available. Assembling the swarm to compute your optimal pathway...` }
          ]);
          
          setTimeout(() => {
            setView('dashboard');
          }, 4500);
        }
      }, 1000);
    }
  };

  useEffect(() => {
    if (view === 'dashboard') {
      const steps = [
        setTimeout(() => setPipelineStep(0), 1000),
        setTimeout(() => setPipelineStep(1), 2500),
        setTimeout(() => setPipelineStep(2), 4000),
        setTimeout(() => setPipelineStep(3), 5500),
        setTimeout(() => setPipelineStep(4), 7500)
      ];
      return () => steps.forEach(clearTimeout);
    }
  }, [view]);

  // 2. Treasure Map Tree Graph Setup
  const openKnowledgeGraph = () => {
    setView('knowledge_graph');
    
    // Create a beautiful branching treasure map!
    const tNodes = [
      { id: 'start', type: 'customCourseNode', position: { x: 50, y: 300 }, data: { subject_id: 'START', label: 'Academic Journey', credits: 0, semester: 1, status: 'COMPLETED' } },
      
      // Core Branch
      { id: 'core1', type: 'customCourseNode', position: { x: 350, y: 300 }, data: { subject_id: 'CS201', label: 'Data Structures', credits: 4, semester: 3, status: 'COMPLETED' } },
      
      // Upper Tree Branch (Math / AI)
      { id: 't1', type: 'customCourseNode', position: { x: 700, y: 100 }, data: { subject_id: 'MATH201', label: 'Discrete Math', credits: 3, semester: 4, status: 'ENROLLED' } },
      { id: 't2', type: 'customCourseNode', position: { x: 1050, y: 100 }, data: { subject_id: 'AI301', label: 'Machine Learning', credits: 4, semester: 5, status: 'AVAILABLE', is_bottleneck: true } },
      
      // Lower Tree Branch (Systems)
      { id: 'b1', type: 'customCourseNode', position: { x: 700, y: 500 }, data: { subject_id: 'CS302', label: 'Operating Systems', credits: 4, semester: 4, status: 'ENROLLED' } },
      { id: 'b2', type: 'customCourseNode', position: { x: 1050, y: 500 }, data: { subject_id: 'CS401', label: 'Cloud Architecture', credits: 4, semester: 5, status: 'AVAILABLE' } },
      
      // Convergence / Capstone
      { id: 'cap', type: 'customCourseNode', position: { x: 1400, y: 300 }, data: { subject_id: 'PRJ401', label: 'Project Phase I', credits: 3, semester: 7, status: 'AVAILABLE' } },
      
      // The Treasure!
      { id: 'treasure', type: 'customCourseNode', position: { x: 1750, y: 300 }, data: { subject_id: 'X_MARKS_SPOT', label: chatInput || 'Ultimate Goal', credits: 0, semester: 8, status: 'TREASURE' } }
    ];

    const tEdges = [
      { id: 'e-start', source: 'start', target: 'core1', type: 'step', style: { strokeWidth: 6, strokeDasharray: '10,10', stroke: '#78350f' }, animated: true },
      
      { id: 'e-up', source: 'core1', target: 't1', type: 'step', style: { strokeWidth: 6, strokeDasharray: '10,10', stroke: '#78350f' }, animated: true },
      { id: 'e-t12', source: 't1', target: 't2', type: 'step', style: { strokeWidth: 6, strokeDasharray: '10,10', stroke: '#78350f' }, animated: true },
      
      { id: 'e-down', source: 'core1', target: 'b1', type: 'step', style: { strokeWidth: 6, strokeDasharray: '10,10', stroke: '#78350f' }, animated: true },
      { id: 'e-b12', source: 'b1', target: 'b2', type: 'step', style: { strokeWidth: 6, strokeDasharray: '10,10', stroke: '#78350f' }, animated: true },
      
      { id: 'e-conv1', source: 't2', target: 'cap', type: 'step', style: { strokeWidth: 6, strokeDasharray: '10,10', stroke: '#78350f' }, animated: true },
      { id: 'e-conv2', source: 'b2', target: 'cap', type: 'step', style: { strokeWidth: 6, strokeDasharray: '10,10', stroke: '#78350f' }, animated: true },
      
      { id: 'e-win', source: 'cap', target: 'treasure', type: 'step', style: { strokeWidth: 8, strokeDasharray: '10,10', stroke: '#eab308' }, animated: true }
    ];

    setNodes(tNodes);
    setEdges(tEdges);
  };

  const chatEndRef = useRef(null);
  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatHistory, view]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4 md:p-8 crt godmode-bg relative overflow-hidden">
      
      {/* Decorative Floating Pixels */}
      {view !== 'knowledge_graph' && (
        <>
          <div className="absolute top-20 left-20 w-4 h-4 bg-blue-400 animate-bounce shadow-[2px_2px_0_#000]"></div>
          <div className="absolute bottom-40 right-20 w-6 h-6 bg-yellow-400 animate-pulse shadow-[3px_3px_0_#000]"></div>
          <div className="absolute top-40 right-40 w-3 h-3 bg-red-400 animate-ping"></div>
        </>
      )}

      {/* HEADER (Hidden on Landing) */}
      {view !== 'landing' && (
        <header className="absolute top-0 w-full p-4 flex justify-between items-center bg-white border-b-[6px] border-black z-10 shadow-[0_8px_0_rgba(0,0,0,0.15)]">
          <div className="flex items-center gap-3">
            <Brain size={32} className="text-blue-600 animate-pulse" />
            <span className="title-text text-2xl text-black drop-shadow-[2px_2px_0_#3b82f6]">OMEGA ADVISOR</span>
          </div>
          {name && view !== 'login' && (
            <div className="title-text text-sm md:text-base flex items-center gap-2 bg-yellow-300 px-4 py-2 border-4 border-black shadow-[4px_4px_0_#000] transform hover:-rotate-2 transition-transform cursor-default">
              <User size={18}/> {name} <span className="text-gray-600">[{regNo}]</span>
            </div>
          )}
        </header>
      )}

      {/* VIEW: TREASURE MAP KNOWLEDGE GRAPH */}
      {view === 'knowledge_graph' && (
        <div className="fixed inset-0 pt-24 bg-[#fef3c7] z-0">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            nodeTypes={nodeTypes}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            fitView
            className="bg-[#fef3c7] bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTIwIDIwTDIwIDBMMjAgMjBMMCAyMEwyMCAyMHoiIHN0cm9rZT0icmdiYSgxMjAsIDUzLCAxNSwgMC4xKSIgc3Ryb2tlLXdpZHRoPSIyIiBmaWxsPSJub25lIi8+PC9zdmc+')]"
          >
            <Background color="#78350f" gap={40} size={2} />
            <Controls className="border-4 border-[#451a03] shadow-[4px_4px_0_#78350f] bg-[#fef3c7] rounded-none" />
            <MiniMap className="border-4 border-[#451a03] shadow-[4px_4px_0_#78350f] rounded-none bg-[#fde68a]" nodeColor="#78350f" maskColor="rgba(254, 243, 199, 0.6)" />
          </ReactFlow>
          
          <button 
            onClick={() => setView('dashboard')}
            className="absolute top-28 left-8 z-50 pixel-btn bg-[#451a03] text-white text-xl flex items-center gap-2 py-4 px-6 border-[4px] border-[#fcd34d] shadow-[6px_6px_0_#78350f] hover:shadow-[2px_2px_0_#78350f] hover:translate-x-1 hover:translate-y-1 transition-all"
          >
            <X size={24}/> CLOSE TREASURE MAP
          </button>
        </div>
      )}

      <div className={`mt-20 w-full max-w-5xl relative z-10 ${view === 'knowledge_graph' ? 'hidden' : ''}`}>
        
        {/* VIEW: LANDING PAGE */}
        {view === 'landing' && (
          <div className="flex flex-col items-center justify-center min-h-[75vh] animate-[slideUp_0.6s_ease-out_forwards]">
            
            {/* Cinematic Floating Mascots */}
            <div className="flex flex-wrap justify-center gap-6 md:gap-10 mb-12">
              {[
                { name: 'NEXUS', src: '/assets/nexus.png', delay: '0s', bg: 'bg-blue-100', border: 'border-blue-600' },
                { name: 'MATRIX', src: '/assets/matrix.png', delay: '0.2s', bg: 'bg-yellow-100', border: 'border-yellow-500' },
                { name: 'VECTOR', src: '/assets/vector.png', delay: '0.4s', bg: 'bg-purple-100', border: 'border-purple-600' },
                { name: 'SENTINEL', src: '/assets/sentinel.png', delay: '0.6s', bg: 'bg-red-100', border: 'border-red-600' }
              ].map((m, i) => (
                <div key={i} className={`w-28 h-28 md:w-40 md:h-40 border-[6px] ${m.border} ${m.bg} shadow-[12px_12px_0_#000] relative animate-[bounce_3s_infinite]`} style={{ animationDelay: m.delay }}>
                  <img src={m.src} alt={m.name} className="w-full h-full object-cover" style={{ imageRendering: 'pixelated' }} />
                </div>
              ))}
            </div>

            {/* OMEGA Typewriter Title */}
            <h1 className="title-text text-7xl md:text-9xl text-black drop-shadow-[8px_8px_0_#3b82f6] mb-8 tracking-widest relative inline-block bg-white px-10 py-6 border-[8px] border-black shadow-[16px_16px_0_#000] transform -rotate-2">
              <Sparkles className="absolute -top-8 -left-8 text-yellow-400 animate-pulse w-16 h-16" />
              {typewriterText}
              <span className="animate-pulse inline-block w-10 h-16 bg-black ml-4 align-bottom"></span>
            </h1>

            <h2 className="title-text text-xl md:text-3xl text-gray-800 mb-16 bg-yellow-300 px-8 py-3 border-[6px] border-black shadow-[8px_8px_0_#000] transform rotate-1">
              AUTONOMOUS MULTI-AGENT ACADEMIC INTELLIGENCE
            </h2>

            <button 
              onClick={() => setView('login')}
              className="pixel-btn bg-black text-white text-3xl md:text-4xl flex items-center gap-6 px-16 py-8 border-[6px] border-white shadow-[12px_12px_0_#3b82f6] hover:shadow-[6px_6px_0_#3b82f6] hover:translate-x-1 hover:translate-y-1 active:shadow-none active:translate-x-2 active:translate-y-2 transition-all group"
            >
              INITIALIZE SYSTEM <ArrowRight size={40} className="group-hover:translate-x-4 transition-transform" />
            </button>
          </div>
        )}

        {/* VIEW: LOGIN */}
        {view === 'login' && (
          <div className="pixel-box animate-[slideUp_0.6s_cubic-bezier(0.175,0.885,0.32,1.275)_forwards] mx-auto max-w-2xl bg-white border-[6px] shadow-[12px_12px_0_rgba(0,0,0,0.2)]">
            <div className="window-header bg-black text-white px-4 py-3 flex justify-between border-b-[6px] border-black">
              <span className="text-lg">STUDENT_LOGIN.EXE</span>
              <div className="flex gap-2">
                <div className="w-4 h-4 bg-white hover:bg-gray-300"></div>
                <div className="w-4 h-4 border-2 border-white"></div>
                <div className="w-4 h-4 bg-white hover:bg-red-500 hover:text-white flex items-center justify-center text-black text-[10px] font-bold cursor-pointer">X</div>
              </div>
            </div>
            
            <form onSubmit={handleLogin} className="p-8 md:p-14 flex flex-col gap-8 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTEgMWgydjJIMXoiIGZpbGw9InJnYmEoMCwwLDAsMC4wNCkiIGZpbGwtcnVsZT0iZXZlbm9kZCIvPjwvc3ZnPg==')]">
              <div className="text-center mb-4">
                <h1 className="title-text text-3xl md:text-5xl mb-4 text-blue-600 drop-shadow-[3px_3px_0_#000]">WELCOME TO OMEGA</h1>
                <p className="text-2xl text-gray-700 bg-white inline-block px-4 py-1 border-2 border-black">Enter your credentials to continue.</p>
              </div>

              <div className="flex flex-col gap-2 relative group">
                <label className="title-text text-sm bg-black text-white px-2 py-1 absolute -top-3 left-4 z-10">REGISTRATION NO</label>
                <div className="flex relative transition-transform group-hover:translate-x-1">
                  <KeyRound className="absolute left-4 top-4 text-gray-400" size={28} />
                  <input 
                    type="text" 
                    className="pixel-input pl-14 text-2xl py-4 uppercase shadow-[inset_4px_4px_0_rgba(0,0,0,0.05)] border-[4px]" 
                    placeholder="e.g. REG1001"
                    value={regNo}
                    onChange={(e) => setRegNo(e.target.value)}
                    required
                  />
                </div>
              </div>

              <div className="flex flex-col gap-2 relative group">
                <label className="title-text text-sm bg-black text-white px-2 py-1 absolute -top-3 left-4 z-10">STUDENT NAME</label>
                <div className="flex relative transition-transform group-hover:translate-x-1">
                  <User className="absolute left-4 top-4 text-gray-400" size={28} />
                  <input 
                    type="text" 
                    className="pixel-input pl-14 text-2xl py-4 shadow-[inset_4px_4px_0_rgba(0,0,0,0.05)] border-[4px]" 
                    placeholder="e.g. John Doe"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                  />
                </div>
              </div>

              <button type="submit" className="pixel-btn bg-blue-600 text-white mt-6 flex items-center justify-center gap-3 text-2xl py-5 border-[4px] border-black shadow-[8px_8px_0_#000] hover:shadow-[4px_4px_0_#000] hover:translate-x-1 hover:translate-y-1 active:shadow-none active:translate-x-2 active:translate-y-2 transition-all">
                ACCESS PORTAL <ArrowRight size={28} />
              </button>
            </form>
          </div>
        )}

        {/* VIEW: DETAILS */}
        {view === 'details' && (
          <div className="pixel-box animate-[slideUp_0.6s_cubic-bezier(0.175,0.885,0.32,1.275)_forwards] mx-auto max-w-4xl border-[6px]">
            <div className="window-header bg-black text-white px-4 py-3 text-lg border-b-[6px] border-black">
              <span>ACADEMIC_RECORD.SYS</span>
            </div>
            
            <div className="p-8 md:p-12 bg-white">
              <h2 className="title-text text-3xl mb-8 flex items-center gap-4 drop-shadow-[2px_2px_0_#3b82f6]">
                <GraduationCap size={36} className="text-blue-600" /> 
                STUDENT PROFILE
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
                {[
                  { label: 'CURRENT CGPA', value: studentDetails.cgpa, color: 'text-green-600', border: 'border-green-500', bg: 'bg-green-50', shadow: 'shadow-[8px_8px_0_#22c55e]' },
                  { label: 'SEMESTER', value: `0${studentDetails.semester}`, color: 'text-blue-600', border: 'border-blue-500', bg: 'bg-blue-50', shadow: 'shadow-[8px_8px_0_#3b82f6]' },
                  { label: 'CREDITS EARNED', value: studentDetails.creditsEarned, color: 'text-yellow-600', border: 'border-yellow-500', bg: 'bg-yellow-50', shadow: 'shadow-[8px_8px_0_#eab308]' },
                  { label: 'DEPARTMENT', value: studentDetails.department, color: 'text-purple-600', border: 'border-purple-500', bg: 'bg-purple-50', shadow: 'shadow-[8px_8px_0_#a855f7]', text: 'text-2xl' }
                ].map((stat, i) => (
                  <div key={i} className={`border-[6px] ${stat.border} ${stat.bg} p-6 flex flex-col items-center ${stat.shadow} hover:-translate-y-2 hover:-translate-x-2 hover:shadow-[12px_12px_0_rgba(0,0,0,0.8)] transition-all duration-300 cursor-default relative overflow-hidden group`}>
                    <div className="absolute -right-4 -top-4 w-16 h-16 bg-white opacity-20 rotate-45 transform group-hover:scale-150 transition-transform"></div>
                    <span className="title-text text-base text-gray-700 mb-3 bg-white px-2 border-2 border-black">{stat.label}</span>
                    <span className={`title-text ${stat.text || 'text-5xl'} ${stat.color} drop-shadow-[2px_2px_0_#000] text-center leading-tight`}>{stat.value}</span>
                  </div>
                ))}
              </div>

              <div className="flex justify-center relative">
                <div className="absolute -inset-2 bg-gradient-to-r from-blue-400 via-purple-500 to-red-500 opacity-20 blur-lg animate-pulse"></div>
                <button 
                  onClick={startAgentConsultation}
                  className="relative pixel-btn bg-yellow-400 text-black text-2xl md:text-3xl flex items-center gap-4 w-full justify-center py-6 border-[6px] border-black shadow-[8px_8px_0_#000] hover:shadow-[4px_4px_0_#000] hover:translate-x-1 hover:translate-y-1 active:shadow-none active:translate-x-2 active:translate-y-2 transition-all"
                >
                  <MessageSquare size={32} /> CONSULT AI ADVISOR
                </button>
              </div>
            </div>
          </div>
        )}

        {/* VIEW: AGENT DIALOGUE CONVERSATION */}
        {view === 'agent_chat' && (
          <div className="pixel-box animate-[slideUp_0.6s_cubic-bezier(0.175,0.885,0.32,1.275)_forwards] w-full mx-auto flex flex-col md:flex-row border-[6px] shadow-[16px_16px_0_rgba(0,0,0,0.2)] bg-white overflow-hidden">
            
            {/* Left side: Avatar Box */}
            <div className="w-full md:w-1/3 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTEgMWgydjJIMXoiIGZpbGw9InJnYmEoMjU1LDI1NSwyNTUsMC4xKSIgZmlsbC1ydWxlPSJldmVub2RkIi8+PC9zdmc+')] bg-blue-600 flex flex-col items-center justify-center p-8 border-b-[6px] md:border-b-0 md:border-r-[6px] border-black relative">
              <div className="absolute top-4 left-4 flex gap-2">
                <div className="w-4 h-4 bg-white shadow-[2px_2px_0_#000]"></div>
                <div className="w-4 h-4 border-[3px] border-white shadow-[2px_2px_0_#000]"></div>
              </div>
              <div className="title-text text-white text-2xl mb-6 text-center mt-6 drop-shadow-[2px_2px_0_#000]">NEXUS AGENT</div>
              <div className="w-40 h-40 md:w-56 md:h-56 border-[6px] border-black bg-white shadow-[12px_12px_0_rgba(0,0,0,0.5)] overflow-hidden animate-[bounce_2s_infinite]">
                <img src="/assets/nexus.png" alt="Nexus Agent" className="w-full h-full object-cover" style={{ imageRendering: 'pixelated' }} />
              </div>
            </div>

            {/* Right side: Chat Log */}
            <div className="w-full md:w-2/3 flex flex-col bg-gray-50 h-[600px] relative">
              <div className="absolute inset-0 bg-[linear-gradient(rgba(0,0,0,0.03)_1px,transparent_1px)] bg-[size:100%_4px] pointer-events-none z-0"></div>
              
              <div className="flex-1 overflow-y-auto p-8 flex flex-col gap-6 relative z-10 scrollbar-hide">
                {chatHistory.map((msg, idx) => (
                  <div key={idx} className={`w-full ${msg.sender === 'YOU' ? 'text-right' : 'text-left'} animate-[slideUp_0.3s_ease-out_forwards]`}>
                    <div className={`inline-block border-[4px] border-black p-5 max-w-[90%] text-2xl md:text-3xl leading-relaxed relative ${msg.sender === 'YOU' ? 'bg-yellow-300 text-black shadow-[6px_6px_0_#000]' : 'bg-white text-black shadow-[6px_6px_0_#3b82f6]'}`}>
                      {msg.sender === 'NEXUS' && (
                        <div className="absolute -left-[14px] top-4 w-0 h-0 border-t-[8px] border-t-transparent border-r-[10px] border-r-black border-b-[8px] border-b-transparent"></div>
                      )}
                      {msg.sender === 'YOU' && (
                        <div className="absolute -right-[14px] top-4 w-0 h-0 border-t-[8px] border-t-transparent border-l-[10px] border-l-black border-b-[8px] border-b-transparent"></div>
                      )}
                      <div className="title-text text-sm text-gray-500 mb-2 bg-black text-white inline-block px-2">{msg.sender}</div>
                      <div className="mt-1">
                        {/* Typewriter effect for Nexus, instant for YOU */}
                        {msg.sender === 'NEXUS' && idx === chatHistory.length - 1 ? (
                          <Typewriter text={msg.text} />
                        ) : (
                          msg.text
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                <div ref={chatEndRef} />
              </div>

              {!goalSet && (
                <form onSubmit={handleSendChat} className="w-full flex p-6 bg-white border-t-[6px] border-black animate-slide-up relative z-10">
                  <div className="flex-1 relative">
                    <Sparkles className="absolute left-4 top-5 text-yellow-400 animate-pulse" size={24} />
                    <input 
                      type="text"
                      className="pixel-input w-full pl-12 text-2xl py-4 border-[4px] shadow-[inset_4px_4px_0_rgba(0,0,0,0.05)] focus:border-blue-600 focus:outline-none"
                      placeholder="Enter your career goal..."
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      autoFocus
                    />
                  </div>
                  <button type="submit" className="pixel-btn bg-blue-600 text-white text-2xl px-8 ml-4 border-[4px] border-black shadow-[6px_6px_0_#000] hover:translate-x-1 hover:translate-y-1 hover:shadow-[4px_4px_0_#000] active:translate-x-2 active:translate-y-2 active:shadow-none transition-all">
                    SEND
                  </button>
                </form>
              )}
            </div>
          </div>
        )}

        {/* VIEW: DASHBOARD (MULTI-AGENT PIPELINE & PATH) */}
        {view === 'dashboard' && (
          <div className="flex flex-col gap-10 w-full pb-20">
            
            {/* The Agents Assembling */}
            <div className="pixel-box w-full animate-[slideUp_0.6s_cubic-bezier(0.175,0.885,0.32,1.275)_forwards] border-[6px]">
              <div className="window-header bg-black text-white px-4 py-3 border-b-[6px] border-black text-lg">
                <span>MULTI_AGENT_ASSEMBLY.SYS</span>
              </div>
              <div className="p-8 md:p-12 bg-white">
                <div className="text-center mb-10">
                  <h2 className="title-text text-3xl md:text-4xl text-black mb-4 drop-shadow-[2px_2px_0_#22c55e]">AGENT SWARM ACTIVATED</h2>
                  <p className="text-2xl md:text-3xl text-gray-600 bg-gray-100 inline-block px-4 py-2 border-2 border-black">Computing pathway for: <span className="text-blue-600 font-bold">"{chatInput}"</span></p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  {[
                    { id: 0, name: 'NEXUS', role: 'Front Desk', avatar: '/assets/nexus.png', color: 'blue' },
                    { id: 1, name: 'MATRIX', role: 'Pathfinder', avatar: '/assets/matrix.png', color: 'yellow' },
                    { id: 2, name: 'VECTOR', role: 'Career Velocity', avatar: '/assets/vector.png', color: 'purple' },
                    { id: 3, name: 'SENTINEL', role: 'Verifier', avatar: '/assets/sentinel.png', color: 'red' }
                  ].map((agent) => {
                    const isActive = pipelineStep >= agent.id;
                    const isDone = pipelineStep > agent.id;
                    
                    return (
                      <div key={agent.id} className={`border-[6px] border-black p-5 flex flex-col items-center text-center transition-all duration-500 transform ${isActive ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-50 grayscale'} ${isDone ? 'bg-green-100 shadow-[8px_8px_0_#22c55e]' : (isActive ? 'bg-white shadow-[8px_8px_0_#3b82f6] animate-pulse-border' : 'bg-gray-200 shadow-[8px_8px_0_#000]')}`}>
                        
                        <div className={`w-24 h-24 border-[4px] border-black mb-4 overflow-hidden bg-white shadow-[4px_4px_0_#000] ${isActive && !isDone ? 'animate-bounce' : ''}`}>
                          <img src={agent.avatar} alt={agent.name} className="w-full h-full object-cover" style={{ imageRendering: 'pixelated' }} />
                        </div>
                        
                        <div className="title-text text-lg mb-1 bg-black text-white px-2">{agent.name}</div>
                        <div className="text-lg text-gray-700 mb-4 font-bold">{agent.role}</div>
                        
                        <div className="mt-auto w-full">
                          {!isActive && <div className="border-4 border-gray-400 bg-gray-300 text-gray-500 py-2 title-text text-sm">STANDBY</div>}
                          {isActive && !isDone && <div className="border-4 border-blue-600 bg-blue-100 text-blue-600 py-2 title-text text-sm animate-pulse">COMPUTING</div>}
                          {isDone && <div className="border-4 border-green-600 bg-green-500 text-white py-2 title-text text-sm">SYNCED</div>}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* The Visual Path Output */}
            {pipelineStep >= 4 && (
              <div className="pixel-box w-full bg-blue-50 animate-[slideUp_0.8s_ease-out_forwards] border-[6px] border-black shadow-[16px_16px_0_#3b82f6]">
                <div className="window-header bg-blue-600 text-white px-4 py-3 border-b-[6px] border-black text-lg">
                  <span>OPTIMAL_PATHWAY_GENERATED.DAT</span>
                </div>
                
                <div className="p-8 md:p-14 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTEgMWgydjJIMXoiIGZpbGw9InJnYmEoMCwwLDAsMC4wMikiIGZpbGwtcnVsZT0iZXZlbm9kZCIvPjwvc3ZnPg==')]">
                  <h3 className="title-text text-4xl mb-16 text-center text-black drop-shadow-[3px_3px_0_#3b82f6] bg-white inline-block px-6 py-2 border-4 border-black mx-auto block w-fit">ACADEMIC ROADMAP</h3>
                  
                  <div className="relative mt-8">
                    {/* The drawn line connecting the nodes */}
                    <div className="absolute top-1/2 left-0 w-full h-4 bg-gray-300 -translate-y-1/2 z-0 hidden md:block border-y-4 border-black">
                      <div className="h-full bg-blue-500 animate-[growWidth_2s_ease-out_forwards] origin-left border-y-4 border-transparent" style={{ animationName: 'growWidth', animationDuration: '2s', animationFillMode: 'forwards' }}></div>
                      <style>{`@keyframes growWidth { 0% { width: 0%; } 100% { width: 100%; } }`}</style>
                    </div>

                    <div className="relative z-10 flex flex-col md:flex-row justify-between items-center gap-12 md:gap-0 px-4">
                      
                      {getDynamicPath(chatInput).map((node, i) => (
                        <div key={i} className="flex flex-col items-center bg-white border-[6px] border-black p-6 w-48 text-center shadow-[8px_8px_0_#000] transform transition-all duration-500 hover:-translate-y-4 hover:shadow-[12px_16px_0_#000] relative group" style={{ animation: `slideUp 0.5s ease-out ${node.delay} both` }}>
                          <div className="absolute -top-6 bg-black text-white px-3 py-1 title-text text-sm border-2 border-white shadow-[2px_2px_0_#000] group-hover:bg-blue-600 transition-colors">{node.sem}</div>
                          <div className="text-2xl font-bold mt-2">{node.name}</div>
                          <div className="w-4 h-4 bg-blue-500 border-2 border-black rounded-full mt-4 animate-ping"></div>
                        </div>
                      ))}

                      {/* Goal Node */}
                      <div className="flex flex-col items-center bg-yellow-300 border-[6px] border-black p-6 w-64 text-center shadow-[12px_12px_0_#000] transform transition-all duration-500 hover:scale-110 relative" style={{ animation: `slideUp 0.5s ease-out 1.2s both, pulseBorder 2s infinite` }}>
                        <div className="absolute -top-8 bg-yellow-500 text-black px-4 py-2 title-text text-lg border-[4px] border-black shadow-[4px_4px_0_#000] animate-bounce">GOAL REACHED</div>
                        <Briefcase className="text-black mb-3 mt-4" size={48} />
                        <div className="text-2xl font-bold truncate w-full px-2 bg-white border-2 border-black py-2">{chatInput}</div>
                      </div>

                    </div>
                  </div>
                  
                  <div className="mt-20 text-center animate-[slideUp_0.5s_ease-out_2s_both]">
                    <button onClick={openKnowledgeGraph} className="pixel-btn bg-black text-white text-2xl md:text-3xl flex items-center gap-4 mx-auto py-6 px-10 border-[6px] border-white shadow-[8px_8px_0_#000] hover:shadow-[4px_4px_0_#000] hover:translate-x-1 hover:translate-y-1 active:shadow-none active:translate-x-2 active:translate-y-2 transition-all">
                      <MapIcon size={28}/> OPEN TREASURE MAP
                    </button>
                  </div>
                </div>
              </div>
            )}

          </div>
        )}
      </div>
    </div>
  );
}
