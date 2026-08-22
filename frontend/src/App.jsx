import { useState, useEffect, useRef } from 'react';
import { User, KeyRound, ArrowRight, Brain, Cpu, MessageSquare, Briefcase, GraduationCap, Map as MapIcon, ChevronRight } from 'lucide-react';

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

  const [chatInput, setChatInput] = useState('');
  const [goalSet, setGoalSet] = useState(false);
  const [pipelineStep, setPipelineStep] = useState(-1);

  const handleLogin = (e) => {
    e.preventDefault();
    if (regNo.trim() && name.trim()) {
      setView('details');
    }
  };

  const startAgentConsultation = () => {
    setView('agent_chat');
  };

  const handleSendChat = (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    if (!goalSet) {
      setGoalSet(true);
      setTimeout(() => {
        setView('dashboard');
      }, 2500);
    }
  };

  // Pipeline Animation Effect
  useEffect(() => {
    if (view === 'dashboard') {
      const steps = [
        setTimeout(() => setPipelineStep(0), 500),
        setTimeout(() => setPipelineStep(1), 2000),
        setTimeout(() => setPipelineStep(2), 3500),
        setTimeout(() => setPipelineStep(3), 5000),
        setTimeout(() => setPipelineStep(4), 6500)
      ];
      return () => steps.forEach(clearTimeout);
    }
  }, [view]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4 md:p-8">
      
      {/* HEADER */}
      <header className="absolute top-0 w-full p-4 flex justify-between items-center bg-white border-b-4 border-black z-10 shadow-[0_4px_0_rgba(0,0,0,0.1)]">
        <div className="flex items-center gap-3">
          <Brain size={28} className="text-blue-500 animate-pulse" />
          <span className="title-text text-xl">OMEGA ADVISOR</span>
        </div>
        {name && (
          <div className="title-text text-sm flex items-center gap-2 animate-slide-up">
            <User size={16}/> {name} [{regNo}]
          </div>
        )}
      </header>

      <div className="mt-16 w-full max-w-4xl">
        
        {/* VIEW: LOGIN */}
        {view === 'login' && (
          <div className="pixel-box animate-slide-up mx-auto max-w-2xl">
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
                <div className="flex relative hover:-translate-y-1 transition-transform">
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
                <div className="flex relative hover:-translate-y-1 transition-transform">
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

              <button type="submit" className="pixel-btn pixel-btn-primary mt-4 flex items-center justify-center gap-2 text-lg hover:scale-[1.02] active:scale-95 transition-all">
                ACCESS PORTAL <ArrowRight size={20} />
              </button>
            </form>
          </div>
        )}

        {/* VIEW: DETAILS */}
        {view === 'details' && (
          <div className="pixel-box animate-slide-up mx-auto max-w-3xl">
            <div className="window-header">
              <span>ACADEMIC_RECORD.SYS</span>
            </div>
            
            <div className="p-8 md:p-12">
              <h2 className="title-text text-2xl mb-6 flex items-center gap-3">
                <GraduationCap size={28} className="text-blue-500" /> 
                STUDENT PROFILE
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
                <div className="border-4 border-black p-4 bg-gray-50 flex flex-col items-center shadow-[4px_4px_0_rgba(0,0,0,0.1)] hover:-translate-y-2 transition-transform duration-300">
                  <span className="title-text text-sm text-gray-500 mb-2">CURRENT CGPA</span>
                  <span className="title-text text-4xl text-green-600">{studentDetails.cgpa}</span>
                </div>
                <div className="border-4 border-black p-4 bg-gray-50 flex flex-col items-center shadow-[4px_4px_0_rgba(0,0,0,0.1)] hover:-translate-y-2 transition-transform duration-300 delay-75">
                  <span className="title-text text-sm text-gray-500 mb-2">SEMESTER</span>
                  <span className="title-text text-4xl text-blue-600">0{studentDetails.semester}</span>
                </div>
                <div className="border-4 border-black p-4 bg-gray-50 flex flex-col items-center shadow-[4px_4px_0_rgba(0,0,0,0.1)] hover:-translate-y-2 transition-transform duration-300 delay-150">
                  <span className="title-text text-sm text-gray-500 mb-2">CREDITS EARNED</span>
                  <span className="title-text text-4xl text-yellow-500">{studentDetails.creditsEarned}</span>
                </div>
                <div className="border-4 border-black p-4 bg-gray-50 flex flex-col items-center shadow-[4px_4px_0_rgba(0,0,0,0.1)] text-center hover:-translate-y-2 transition-transform duration-300 delay-200">
                  <span className="title-text text-sm text-gray-500 mb-2">DEPARTMENT</span>
                  <span className="title-text text-2xl mt-2">{studentDetails.department}</span>
                </div>
              </div>

              <div className="flex justify-center animate-pulse">
                <button 
                  onClick={startAgentConsultation}
                  className="pixel-btn pixel-btn-success text-xl flex items-center gap-3 w-full justify-center py-4 hover:scale-[1.02] transition-transform"
                >
                  <MessageSquare size={24} /> CONSULT AI ADVISOR
                </button>
              </div>
            </div>
          </div>
        )}

        {/* VIEW: AGENT DIALOGUE */}
        {view === 'agent_chat' && (
          <div className="pixel-box animate-[fadeIn_0.5s_ease-out] w-full mx-auto animate-pulse-border">
            <div className="window-header bg-blue-600">
              <span>NEXUS_ENCOUNTER.EXE</span>
            </div>
            
            <div className="p-6 md:p-10 flex flex-col items-center bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTEgMWgydjJIMXoiIGZpbGw9InJnYmEoMCwwLDAsMC4wNSkiIGZpbGwtcnVsZT0iZXZlbm9kZCIvPjwvc3ZnPg==')]">
              
              <div className="w-32 h-32 md:w-40 md:h-40 mb-8 border-4 border-black bg-blue-50 shadow-[8px_8px_0_rgba(0,0,0,0.2)] overflow-hidden relative animate-bounce">
                <img src="/assets/nexus.png" alt="Nexus Agent" className="w-full h-full object-cover" style={{ imageRendering: 'pixelated' }} />
              </div>

              <div className="w-full border-4 border-black p-6 md:p-8 mb-8 bg-white shadow-[8px_8px_0_rgba(0,0,0,0.15)] relative transform hover:scale-[1.01] transition-transform">
                <div className="absolute -top-5 left-4 bg-blue-600 text-white px-4 py-1 border-4 border-black title-text text-lg">
                  NEXUS
                </div>
                <div className="text-2xl md:text-3xl leading-relaxed mt-2 min-h-[100px] flex items-center">
                  {goalSet 
                    ? `Goal locked in: "${chatInput}". I'm assembling the agent swarm to compute your optimal academic path. Stand by...`
                    : `Hello ${name}. I am Nexus, your AI Advisor. To build your academic pipeline, I need to know: what is your ultimate career goal?`
                  }
                </div>
              </div>

              {!goalSet && (
                <form onSubmit={handleSendChat} className="w-full flex flex-col md:flex-row gap-4 animate-slide-up">
                  <div className="flex-1 relative hover:-translate-y-1 transition-transform">
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
                  <button type="submit" className="pixel-btn pixel-btn-primary text-2xl px-8 hover:scale-105 transition-transform">
                    ENTER
                  </button>
                </form>
              )}
            </div>
          </div>
        )}

        {/* VIEW: DASHBOARD (MULTI-AGENT PIPELINE & PATH) */}
        {view === 'dashboard' && (
          <div className="flex flex-col gap-8 w-full">
            
            {/* The Agents Assembling */}
            <div className="pixel-box w-full animate-slide-up">
              <div className="window-header bg-green-600">
                <span>MULTI_AGENT_ASSEMBLY.SYS</span>
              </div>
              <div className="p-6 md:p-8">
                <div className="text-center mb-6">
                  <h2 className="title-text text-xl md:text-2xl text-green-600 mb-2">AGENT SWARM ACTIVATED</h2>
                  <p className="text-xl md:text-2xl text-gray-600">Computing pathway for: <span className="text-blue-600 font-bold">"{chatInput}"</span></p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  {[
                    { id: 0, name: 'Nexus', role: 'Front Desk', color: 'bg-blue-500' },
                    { id: 1, name: 'Matrix', role: 'Pathfinder', color: 'bg-yellow-500' },
                    { id: 2, name: 'Vector', role: 'Career Velocity', color: 'bg-purple-500' },
                    { id: 3, name: 'Sentinel', role: 'Verifier', color: 'bg-red-500' }
                  ].map((agent) => {
                    const isActive = pipelineStep >= agent.id;
                    const isDone = pipelineStep > agent.id;
                    
                    return (
                      <div key={agent.id} className={`agent-card border-4 border-black p-4 flex flex-col items-center text-center shadow-[4px_4px_0_rgba(0,0,0,0.15)] ${isActive ? 'visible' : ''} ${isDone ? 'bg-green-50' : (isActive ? 'bg-gray-50' : 'bg-gray-200')}`}>
                        <Cpu size={32} className={`mb-2 ${isActive ? 'text-gray-800' : 'text-gray-400'} ${isDone ? 'text-green-600' : ''}`} />
                        <div className="title-text text-sm mb-1">{agent.name}</div>
                        <div className="text-sm text-gray-500">{agent.role}</div>
                        <div className="mt-3">
                          {!isActive && <span className="title-text text-[10px] text-gray-400">STANDBY</span>}
                          {isActive && !isDone && <span className="title-text text-[10px] text-blue-600 animate-pulse">COMPUTING...</span>}
                          {isDone && <span className="title-text text-[10px] text-green-600">COMPLETE</span>}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* The Visual Path Output */}
            {pipelineStep >= 4 && (
              <div className="pixel-box w-full bg-blue-50 animate-slide-up border-blue-500 border-4">
                <div className="window-header bg-blue-600">
                  <span>OPTIMAL_PATHWAY_GENERATED</span>
                </div>
                
                <div className="p-8">
                  <h3 className="title-text text-2xl mb-8 text-center text-blue-700">YOUR ACADEMIC ROADMAP</h3>
                  
                  <div className="relative">
                    {/* The drawn line connecting the nodes */}
                    <div className="absolute top-1/2 left-0 w-full h-2 bg-blue-200 -translate-y-1/2 z-0">
                      <div className="h-full bg-blue-600 animate-[drawLine_2s_ease-out_forwards]" style={{ width: '100%', clipPath: 'polygon(0 0, 0 100%, 0 100%, 0 0)'}}>
                         {/* We use CSS keyframes or simple inline style hack for the bar growing */}
                         <div className="h-full bg-blue-600 animate-[growWidth_1.5s_ease-out_forwards] origin-left" style={{ animationName: 'growWidth', animationDuration: '1.5s', animationFillMode: 'forwards' }}></div>
                         <style>{`@keyframes growWidth { from { width: 0%; } to { width: 100%; } }`}</style>
                      </div>
                    </div>

                    <div className="relative z-10 flex flex-col md:flex-row justify-between items-center gap-8 md:gap-0">
                      
                      {/* Node 1 */}
                      <div className="flex flex-col items-center bg-white border-4 border-black p-4 w-40 text-center shadow-[4px_4px_0_rgba(0,0,0,0.1)] hover:-translate-y-2 transition-transform duration-300">
                        <div className="title-text text-sm text-gray-500 mb-2">SEM 6</div>
                        <div className="text-xl font-bold">Data Structures II</div>
                      </div>

                      {/* Node 2 */}
                      <div className="flex flex-col items-center bg-white border-4 border-black p-4 w-40 text-center shadow-[4px_4px_0_rgba(0,0,0,0.1)] hover:-translate-y-2 transition-transform duration-300 delay-100">
                        <div className="title-text text-sm text-gray-500 mb-2">SEM 7</div>
                        <div className="text-xl font-bold">Machine Learning</div>
                      </div>

                      {/* Node 3 */}
                      <div className="flex flex-col items-center bg-white border-4 border-black p-4 w-40 text-center shadow-[4px_4px_0_rgba(0,0,0,0.1)] hover:-translate-y-2 transition-transform duration-300 delay-200">
                        <div className="title-text text-sm text-gray-500 mb-2">SEM 8</div>
                        <div className="text-xl font-bold text-blue-600">Capstone Project</div>
                      </div>

                      {/* Goal Node */}
                      <div className="flex flex-col items-center bg-yellow-100 border-4 border-yellow-500 p-4 w-48 text-center shadow-[4px_4px_0_rgba(234,179,8,0.4)] animate-pulse hover:scale-105 transition-transform duration-300">
                        <Briefcase className="text-yellow-500 mb-2" size={32} />
                        <div className="title-text text-sm text-yellow-700">GOAL REACHED</div>
                        <div className="text-lg font-bold truncate w-full">{chatInput}</div>
                      </div>

                    </div>
                  </div>
                  
                  <div className="mt-12 text-center">
                    <button className="pixel-btn pixel-btn-primary text-xl flex items-center gap-2 mx-auto hover:scale-105 transition-transform">
                      <MapIcon size={20}/> VIEW FULL KNOWLEDGE GRAPH
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
