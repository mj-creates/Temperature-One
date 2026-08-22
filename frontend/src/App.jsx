import { useState, useEffect, useRef } from 'react';
import { User, KeyRound, ArrowRight, Brain, Cpu, MessageSquare, Briefcase, GraduationCap } from 'lucide-react';

export default function App() {
  const [view, setView] = useState('login'); // login, details, agent_chat, dashboard
  const [regNo, setRegNo] = useState('');
  const [name, setName] = useState('');
  
  // Student Mock Details
  const studentDetails = {
    cgpa: 8.4,
    semester: 5,
    creditsEarned: 90,
    department: 'Computer Science'
  };

  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [goalSet, setGoalSet] = useState(false);
  const chatEndRef = useRef(null);

  const handleLogin = (e) => {
    e.preventDefault();
    if (regNo.trim() && name.trim()) {
      setView('details');
    }
  };

  const startAgentConsultation = () => {
    setView('agent_chat');
    setChatMessages([
      {
        sender: 'Nexus Advisor',
        text: `Hello ${name}! I am Nexus, your primary AI Advisor. Before we build your multi-agent academic pipeline, what is your ultimate career goal?`
      }
    ]);
  };

  const handleSendChat = (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    // Keep chatInput to display in the dialogue box response!

    if (!goalSet) {
      setGoalSet(true);
      setTimeout(() => {
        setTimeout(() => {
          setView('dashboard');
        }, 3000);
      }, 500);
    }
  };

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatMessages, view]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4 md:p-8">
      
      {/* HEADER */}
      <header className="absolute top-0 w-full p-4 flex justify-between items-center bg-white border-b-4 border-black z-10 shadow-[0_4px_0_rgba(0,0,0,0.1)]">
        <div className="flex items-center gap-3">
          <Brain size={28} className="text-blue-500" />
          <span className="title-text text-xl">OMEGA ADVISOR</span>
        </div>
        {name && (
          <div className="title-text text-sm flex items-center gap-2">
            <User size={16}/> {name} [{regNo}]
          </div>
        )}
      </header>

      <div className="mt-16 w-full max-w-3xl">
        
        {/* VIEW: LOGIN */}
        {view === 'login' && (
          <div className="pixel-box">
            <div className="window-header">
              <span>STUDENT_LOGIN.EXE</span>
              <div className="flex gap-2">
                <div className="w-3 h-3 bg-white"></div>
                <div className="w-3 h-3 border-2 border-white"></div>
                <div className="w-3 h-3 bg-white flex items-center justify-center text-black text-[10px] font-bold">X</div>
              </div>
            </div>
            
            <form onSubmit={handleLogin} className="p-8 md:p-12 flex flex-col gap-6">
              <div className="text-center mb-4">
                <h1 className="title-text text-2xl md:text-3xl mb-2 text-blue-600">WELCOME TO OMEGA</h1>
                <p className="text-2xl text-gray-600">Enter your credentials to continue.</p>
              </div>

              <div className="flex flex-col gap-2">
                <label className="title-text text-sm">REGISTRATION NUMBER</label>
                <div className="flex relative">
                  <KeyRound className="absolute left-3 top-3 text-gray-400" size={24} />
                  <input 
                    type="text" 
                    className="pixel-input pl-12 uppercase" 
                    placeholder="e.g. REG1001"
                    value={regNo}
                    onChange={(e) => setRegNo(e.target.value)}
                    required
                  />
                </div>
              </div>

              <div className="flex flex-col gap-2">
                <label className="title-text text-sm">STUDENT NAME</label>
                <div className="flex relative">
                  <User className="absolute left-3 top-3 text-gray-400" size={24} />
                  <input 
                    type="text" 
                    className="pixel-input pl-12" 
                    placeholder="e.g. John Doe"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                  />
                </div>
              </div>

              <button type="submit" className="pixel-btn pixel-btn-primary mt-4 flex items-center justify-center gap-2 text-lg">
                ACCESS PORTAL <ArrowRight size={20} />
              </button>
            </form>
          </div>
        )}

        {/* VIEW: DETAILS */}
        {view === 'details' && (
          <div className="pixel-box animate-[fadeIn_0.3s_ease-out]">
            <div className="window-header">
              <span>ACADEMIC_RECORD.SYS</span>
              <div className="flex gap-2">
                <div className="w-3 h-3 bg-white"></div>
                <div className="w-3 h-3 border-2 border-white"></div>
                <div className="w-3 h-3 bg-white flex items-center justify-center text-black text-[10px] font-bold">X</div>
              </div>
            </div>
            
            <div className="p-8 md:p-12">
              <h2 className="title-text text-2xl mb-6 flex items-center gap-3">
                <GraduationCap size={28} className="text-blue-500" /> 
                STUDENT PROFILE
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
                <div className="border-4 border-black p-4 bg-gray-50 flex flex-col items-center shadow-[4px_4px_0_rgba(0,0,0,0.1)]">
                  <span className="title-text text-sm text-gray-500 mb-2">CURRENT CGPA</span>
                  <span className="title-text text-4xl text-green-600">{studentDetails.cgpa}</span>
                </div>
                <div className="border-4 border-black p-4 bg-gray-50 flex flex-col items-center shadow-[4px_4px_0_rgba(0,0,0,0.1)]">
                  <span className="title-text text-sm text-gray-500 mb-2">SEMESTER</span>
                  <span className="title-text text-4xl text-blue-600">0{studentDetails.semester}</span>
                </div>
                <div className="border-4 border-black p-4 bg-gray-50 flex flex-col items-center shadow-[4px_4px_0_rgba(0,0,0,0.1)]">
                  <span className="title-text text-sm text-gray-500 mb-2">CREDITS EARNED</span>
                  <span className="title-text text-4xl text-yellow-500">{studentDetails.creditsEarned}</span>
                </div>
                <div className="border-4 border-black p-4 bg-gray-50 flex flex-col items-center shadow-[4px_4px_0_rgba(0,0,0,0.1)] text-center">
                  <span className="title-text text-sm text-gray-500 mb-2">DEPARTMENT</span>
                  <span className="title-text text-2xl mt-2">{studentDetails.department}</span>
                </div>
              </div>

              <div className="flex justify-center">
                <button 
                  onClick={startAgentConsultation}
                  className="pixel-btn pixel-btn-success text-xl flex items-center gap-3 w-full justify-center py-4"
                >
                  <MessageSquare size={24} /> CONSULT AI ADVISOR
                </button>
              </div>
            </div>
          </div>
        )}

        {/* VIEW: AGENT DIALOGUE */}
        {view === 'agent_chat' && (
          <div className="pixel-box animate-[fadeIn_0.3s_ease-out] w-full max-w-4xl mx-auto">
            <div className="window-header bg-blue-600">
              <span>NEXUS_ENCOUNTER.EXE</span>
              <div className="flex gap-2">
                <div className="w-3 h-3 bg-white"></div>
                <div className="w-3 h-3 border-2 border-white"></div>
                <div className="w-3 h-3 bg-white flex items-center justify-center text-blue-600 text-[10px] font-bold">X</div>
              </div>
            </div>
            
            <div className="p-6 md:p-10 flex flex-col items-center bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTEgMWgydjJIMXoiIGZpbGw9InJnYmEoMCwwLDAsMC4wNSkiIGZpbGwtcnVsZT0iZXZlbm9kZCIvPjwvc3ZnPg==')]">
              
              {/* Agent Avatar Box */}
              <div className="w-32 h-32 md:w-40 md:h-40 mb-8 border-4 border-black bg-blue-50 shadow-[8px_8px_0_rgba(0,0,0,0.2)] overflow-hidden relative">
                <img src="/assets/nexus.png" alt="Nexus Agent" className="w-full h-full object-cover" style={{ imageRendering: 'pixelated' }} />
              </div>

              {/* RPG Dialogue Box */}
              <div className="w-full border-4 border-black p-6 md:p-8 mb-8 bg-white shadow-[8px_8px_0_rgba(0,0,0,0.15)] relative">
                <div className="absolute -top-5 left-4 bg-blue-600 text-white px-4 py-1 border-4 border-black title-text text-lg">
                  NEXUS
                </div>
                <div className="text-2xl md:text-3xl leading-relaxed mt-2 min-h-[100px] flex items-center">
                  {goalSet 
                    ? `Understood, ${name}! Goal registered: "${chatInput}". Initializing the Omega Multi-Agent Pipeline to map your prerequisite graph...`
                    : `Hello ${name}! I am Nexus, your primary AI Advisor. To build your multi-agent academic pipeline, I need to know: what is your ultimate career goal?`
                  }
                </div>
              </div>

              {/* Input Form */}
              {!goalSet && (
                <form onSubmit={handleSendChat} className="w-full flex flex-col md:flex-row gap-4">
                  <div className="flex-1 relative">
                    <div className="absolute -top-3 left-4 bg-white px-2 title-text text-sm text-gray-500 z-10">YOUR GOAL</div>
                    <input 
                      type="text"
                      className="pixel-input w-full text-2xl py-4 relative z-0"
                      placeholder="e.g. Software Engineer at Google"
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      autoFocus
                    />
                  </div>
                  <button type="submit" className="pixel-btn pixel-btn-primary text-2xl px-8">
                    ENTER
                  </button>
                </form>
              )}
            </div>
          </div>
        )}

        {/* VIEW: DASHBOARD (MULTI-AGENT PIPELINE) */}
        {view === 'dashboard' && (
          <div className="pixel-box animate-[fadeIn_0.3s_ease-out]">
            <div className="window-header bg-green-600">
              <span>MULTI_AGENT_PIPELINE.SYS</span>
            </div>
            
            <div className="p-8">
              <div className="text-center mb-8">
                <h2 className="title-text text-2xl text-green-600 mb-2">PIPELINE INITIALIZED</h2>
                <p className="text-2xl text-gray-600">Generating optimum academic pathway...</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[
                  { name: 'Agent 1: Nexus', role: 'Front Desk', status: 'ACTIVE', color: 'bg-blue-500' },
                  { name: 'Agent 2: Matrix', role: 'Graph Pathfinder', status: 'WORKING', color: 'bg-yellow-500' },
                  { name: 'Agent 3: Vector', role: 'Career Velocity', status: 'WORKING', color: 'bg-purple-500' },
                  { name: 'Agent 4: Sentinel', role: 'Constraint Verifier', status: 'STANDBY', color: 'bg-gray-400' }
                ].map((agent, i) => (
                  <div key={i} className="border-4 border-black p-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Cpu size={24} className="text-gray-700" />
                      <div>
                        <div className="title-text text-sm">{agent.name}</div>
                        <div className="text-lg text-gray-500">{agent.role}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`w-3 h-3 ${agent.color} animate-pulse`}></span>
                      <span className="title-text text-xs">{agent.status}</span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-8 border-4 border-black p-6 text-center bg-blue-50">
                <Briefcase size={48} className="mx-auto mb-4 text-blue-500" />
                <h3 className="title-text text-xl mb-4">ROADMAP READY</h3>
                <p className="text-2xl mb-6">Your customized prerequisite graph has been generated by the agent swarm.</p>
                <button onClick={() => alert('Knowledge Graph View would open here!')} className="pixel-btn pixel-btn-primary text-lg">
                  OPEN KNOWLEDGE GRAPH
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
