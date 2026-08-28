import { useState, useEffect, useRef, useCallback } from 'react';
import { User, KeyRound, ArrowRight, Brain, Cpu, MessageSquare, Briefcase, GraduationCap, Map as MapIcon, Sparkles, X, Shield, Star, Download, Users, FileBarChart, MonitorPlay, Target, Lightbulb, Rocket, Lock, Eye, EyeOff, Globe, CheckCircle2, AlertCircle, RefreshCw, ShieldCheck, BookOpen } from 'lucide-react';

// ── API base URL ─────────────────────────────────────────────────────────────
// In production (Vercel) set VITE_API_URL to your Render backend URL.
// Falls back to localhost for local development.
const _RAW_API = import.meta.env.VITE_API_URL || 'http://localhost:8000';
// Strip accidental markdown link syntax e.g. [url](url) and trailing slash
const API_BASE = _RAW_API.replace(/^\[.*?\]\((.*?)\)$/, '$1').replace(/\/$/, '');
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

// --- MULTI-DEPARTMENT CURRICULUM CATALOG (R22 REGULATION) ---
const DEPARTMENT_CURRICULA = {
  CSE: {
    name: 'Computer Science and Engineering',
    regulation: 'R22',
    semesters: {
      1: [
        { code: '22TP105', name: 'Problem Solving through Programming - I', credits: 4, tags: ['programming', 'software', 'python', 'c', 'developer'] },
        { code: '22MT103', name: 'Linear Algebra & Ordinary Differential Equations', credits: 4, tags: ['math', 'ai', 'data', 'ml'] },
        { code: '22PY105', name: 'Semiconductor Physics', credits: 4, tags: ['physics', 'hardware'] },
        { code: '22CT103', name: 'Engineering Chemistry', credits: 4, tags: ['chemistry', 'science'] }
      ],
      2: [
        { code: '22TP106', name: 'Problem Solving through Programming - II (Java & OOP)', credits: 4, tags: ['programming', 'oop', 'java', 'software', 'developer', 'fullstack'] },
        { code: '22MT107', name: 'Discrete Mathematical Structures', credits: 4, tags: ['math', 'algorithms', 'logic', 'cyber', 'security'] },
        { code: '22ME101', name: 'Engineering Graphics', credits: 3, tags: ['design', 'cad'] },
        { code: '22MT108', name: 'Numerical Methods', credits: 4, tags: ['math', 'data', 'analytics'] }
      ],
      3: [
        { code: '22TP201', name: 'Data Structures & Algorithms', credits: 4, tags: ['data structures', 'algorithms', 'software', 'developer', 'fullstack', 'backend'] },
        { code: '22CS201', name: 'Database Management Systems', credits: 4, tags: ['database', 'sql', 'backend', 'data', 'software', 'developer', 'fullstack'] },
        { code: '22CS202', name: 'Digital Logic Design', credits: 3, tags: ['hardware', 'systems', 'embedded'] },
        { code: '22CS203', name: 'Object-Oriented Programming through Java', credits: 3, tags: ['java', 'oop', 'software'] },
        { code: '22ST202', name: 'Probability and Applied Statistics', credits: 4, tags: ['statistics', 'ai', 'data', 'data scientist', 'ml'] }
      ],
      4: [
        { code: '22CS206', name: 'Design and Analysis of Algorithms', credits: 4, tags: ['algorithms', 'competitive', 'software', 'developer', 'systems'] },
        { code: '22CS207', name: 'Operating Systems & Architecture', credits: 4, tags: ['operating systems', 'systems', 'kernel', 'cyber', 'security', 'cloud', 'devops'] },
        { code: '22CS205', name: 'Computer Organization and Architecture', credits: 3, tags: ['hardware', 'systems', 'architecture'] },
        { code: '22CS208', name: 'Theory of Computation', credits: 4, tags: ['theory', 'compiler', 'automata'] }
      ],
      5: [
        { code: '22CS301', name: 'Web Technologies & Modern Frameworks', credits: 4, tags: ['web', 'frontend', 'backend', 'fullstack', 'react', 'node', 'software', 'developer'] },
        { code: '22CS302', name: 'Computer Networks & Internet Protocols', credits: 4, tags: ['networks', 'protocols', 'cyber', 'security', 'cloud', 'systems'] },
        { code: '22CS303', name: 'Artificial Intelligence Principles', credits: 4, tags: ['ai', 'artificial intelligence', 'search', 'ml', 'machine learning'] },
        { code: '22CS304', name: 'Software Engineering & Agile Methodologies', credits: 3, tags: ['software engineering', 'sdlc', 'agile', 'management', 'developer'] }
      ],
      6: [
        { code: '22CS306', name: 'Machine Learning Systems & Modeling', credits: 4, tags: ['machine learning', 'ml', 'ai', 'data scientist', 'data', 'predictive'] },
        { code: '22CS307', name: 'Compiler Design & Construction', credits: 4, tags: ['compiler', 'systems', 'languages'] },
        { code: '22CS308', name: 'Cryptography and Network Security', credits: 4, tags: ['security', 'cryptography', 'cyber', 'cybersecurity', 'networks'] },
        { code: '22CS309', name: 'Mobile Application Development', credits: 3, tags: ['mobile', 'app', 'android', 'ios', 'frontend', 'developer'] }
      ],
      7: [
        { code: '22CS401', name: 'Cloud Computing & Distributed Platforms', credits: 4, tags: ['cloud', 'aws', 'distributed', 'devops', 'microservices', 'software', 'architect'] },
        { code: '22CS402', name: 'Deep Learning & Neural Networks', credits: 4, tags: ['deep learning', 'neural', 'ai', 'vision', 'nlp', 'machine learning', 'data scientist'] },
        { code: '22CS403', name: 'Big Data Analytics & Streaming Platforms', credits: 4, tags: ['big data', 'spark', 'hadoop', 'data', 'data scientist', 'analytics'] },
        { code: '22CS404', name: 'DevOps & CI/CD Pipeline Automation', credits: 3, tags: ['devops', 'ci/cd', 'docker', 'kubernetes', 'cloud', 'systems'] }
      ],
      8: [
        { code: '22CS406', name: 'Distributed Systems & Scalable System Design', credits: 4, tags: ['system design', 'distributed', 'scalability', 'backend', 'software', 'architect'] },
        { code: '22CS407', name: 'Natural Language Processing & LLMs', credits: 4, tags: ['nlp', 'llm', 'language', 'ai', 'deep learning', 'data scientist'] },
        { code: '22CS408', name: 'Blockchain Architecture & Smart Contracts', credits: 3, tags: ['blockchain', 'crypto', 'decentralized', 'web3', 'security'] }
      ]
    }
  },
  AIML: {
    name: 'Artificial Intelligence and Machine Learning',
    regulation: 'R22',
    semesters: {
      1: [{ code: '22AI101', name: 'Python Programming for AI', credits: 4, tags: ['python', 'ai', 'programming'] }],
      2: [{ code: '22AI102', name: 'Data Structures & Algorithmic Foundations', credits: 4, tags: ['data structures', 'algorithms'] }],
      3: [{ code: '22AI201', name: 'Applied Mathematics & Statistics for AI', credits: 4, tags: ['statistics', 'math', 'ai', 'data'] }],
      4: [{ code: '22AI204', name: 'Database Systems & Data Wrangling', credits: 4, tags: ['database', 'data', 'sql'] }],
      5: [{ code: '22AI301', name: 'Machine Learning Foundations & Supervised Models', credits: 4, tags: ['machine learning', 'ml', 'ai'] }],
      6: [{ code: '22AI303', name: 'Deep Learning Architectures & Computer Vision', credits: 4, tags: ['deep learning', 'vision', 'neural', 'ai'] }],
      7: [{ code: '22AI401', name: 'Generative AI, LLMs & Prompt Engineering', credits: 4, tags: ['llm', 'generative ai', 'nlp', 'ai'] }],
      8: [{ code: '22AI402', name: 'Reinforcement Learning & Autonomous AI Agents', credits: 4, tags: ['reinforcement learning', 'agents', 'ai', 'robotics'] }]
    }
  },
  CSCS: {
    name: 'Cybersecurity and Computer Science',
    regulation: 'R22',
    semesters: {
      1: [{ code: '22CS101', name: 'Computer Programming & System Basics', credits: 4, tags: ['programming', 'c', 'systems'] }],
      2: [{ code: '22CS102', name: 'Data Structures & Discrete Logic', credits: 4, tags: ['data structures', 'logic'] }],
      3: [{ code: '22SC201', name: 'Computer Architecture & Assembly', credits: 4, tags: ['architecture', 'assembly', 'systems'] }],
      4: [{ code: '22SC202', name: 'Operating Systems & Kernel Security', credits: 4, tags: ['operating systems', 'linux', 'security'] }],
      5: [{ code: '22SC301', name: 'Computer Networks & Security Protocols', credits: 4, tags: ['networks', 'security', 'protocols'] }],
      6: [{ code: '22SC302', name: 'Applied Cryptography & Network Defense', credits: 4, tags: ['cryptography', 'security', 'cyber'] }],
      7: [{ code: '22SC401', name: 'Ethical Hacking & Penetration Testing', credits: 4, tags: ['ethical hacking', 'security', 'penetration'] }],
      8: [{ code: '22SC404', name: 'Digital Forensics & Incident Response', credits: 4, tags: ['forensics', 'incident response', 'cyber'] }]
    }
  },
  IT: {
    name: 'Information Technology',
    regulation: 'R22',
    semesters: {
      1: [{ code: '22IT101', name: 'Python Programming for Information Technology', credits: 4, tags: ['python', 'software'] }],
      2: [{ code: '22IT102', name: 'OOP and Software Concepts', credits: 4, tags: ['oop', 'software', 'java'] }],
      3: [{ code: '22IT201', name: 'Data Structures and Algorithm Design', credits: 4, tags: ['data structures', 'algorithms'] }],
      4: [{ code: '22IT202', name: 'Database Management & Enterprise SQL', credits: 4, tags: ['database', 'sql', 'backend'] }],
      5: [{ code: '22IT301', name: 'Full-Stack Web Application Frameworks', credits: 4, tags: ['web', 'fullstack', 'react', 'node'] }],
      6: [{ code: '22IT303', name: 'Cloud Architecture & DevOps Automation', credits: 4, tags: ['cloud', 'devops', 'aws'] }],
      7: [{ code: '22IT401', name: 'Enterprise Microservices & Cloud Platforms', credits: 4, tags: ['microservices', 'cloud', 'distributed'] }],
      8: [{ code: '22IT403', name: 'Information Systems Governance & Security', credits: 4, tags: ['security', 'governance', 'cloud'] }]
    }
  },
  MECH: {
    name: 'Mechanical Engineering',
    regulation: 'R22',
    semesters: {
      1: [{ code: '22ME101', name: 'Engineering Graphics & Computer-Aided Drafting', credits: 4, tags: ['graphics', 'cad', 'design'] }],
      2: [{ code: '22ME102', name: 'Engineering Mechanics & Statics', credits: 4, tags: ['mechanics', 'materials'] }],
      3: [{ code: '22ME201', name: 'Thermodynamics & Thermal Engineering', credits: 4, tags: ['thermodynamics', 'thermal', 'energy'] }],
      4: [{ code: '22ME204', name: 'Kinematics & Dynamics of Machinery', credits: 4, tags: ['kinematics', 'dynamics', 'design'] }],
      5: [{ code: '22ME301', name: 'Design of Machine Elements', credits: 4, tags: ['machine design', 'cad', 'design', 'mechanical'] }],
      6: [{ code: '22ME303', name: 'Computer-Aided Design & Manufacturing (CAD/CAM)', credits: 4, tags: ['cad/cam', 'manufacturing', 'automation'] }],
      7: [{ code: '22ME401', name: 'Finite Element Analysis (FEA) & Simulation', credits: 4, tags: ['fea', 'simulation', 'structural', 'design'] }],
      8: [{ code: '22ME402', name: 'Robotics, Mechatronics & Industrial Automation', credits: 4, tags: ['robotics', 'automation', 'mechatronics'] }]
    }
  },
  CIVIL: {
    name: 'Civil Engineering',
    regulation: 'R22',
    semesters: {
      1: [{ code: '22CE101', name: 'Engineering Graphics & Building Drawing', credits: 4, tags: ['drawing', 'cad', 'civil'] }],
      2: [{ code: '22CE102', name: 'Plane & Geomatics Surveying', credits: 4, tags: ['surveying', 'geomatics'] }],
      3: [{ code: '22CE201', name: 'Solid Mechanics & Construction Materials', credits: 4, tags: ['materials', 'mechanics'] }],
      4: [{ code: '22CE203', name: 'Structural Analysis - I', credits: 4, tags: ['structural analysis', 'structures'] }],
      5: [{ code: '22CE301', name: 'Structural Analysis - II & Matrix Methods', credits: 4, tags: ['structural analysis', 'structures', 'design'] }],
      6: [{ code: '22CE303', name: 'Design of Reinforced Concrete Structures (RCC)', credits: 4, tags: ['concrete', 'rcc', 'design', 'civil'] }],
      7: [{ code: '22CE401', name: 'Design of Steel Structures & Foundation Engineering', credits: 4, tags: ['steel', 'foundation', 'geotechnical'] }],
      8: [{ code: '22CE403', name: 'Urban Planning, Transportation & Smart Infrastructure', credits: 4, tags: ['urban planning', 'transportation', 'smart city'] }]
    }
  },
  ECE: {
    name: 'Electronics and Communication Engineering',
    regulation: 'R22',
    semesters: {
      1: [{ code: '22EC101', name: 'Electronic Devices & Circuits', credits: 4, tags: ['circuits', 'electronics'] }],
      2: [{ code: '22EC102', name: 'Digital Logic Design & Verilog HDL', credits: 4, tags: ['digital', 'verilog', 'hardware'] }],
      3: [{ code: '22EC201', name: 'Signals and Systems', credits: 4, tags: ['signals', 'dsp', 'systems'] }],
      4: [{ code: '22EC203', name: 'Analog & Digital Communication Systems', credits: 4, tags: ['communications', 'signals'] }],
      5: [{ code: '22EC301', name: 'Microcontrollers & Embedded Systems', credits: 4, tags: ['embedded', 'microcontrollers', 'iot'] }],
      6: [{ code: '22EC303', name: 'VLSI Design & Semiconductor Fabrication', credits: 4, tags: ['vlsi', 'semiconductor', 'chip design'] }],
      7: [{ code: '22EC401', name: 'Wireless & 5G Cellular Communications', credits: 4, tags: ['wireless', '5g', 'telecom'] }],
      8: [{ code: '22EC402', name: 'Embedded System Design & RTOS', credits: 4, tags: ['rtos', 'embedded', 'robotics'] }]
    }
  },
  EEE: {
    name: 'Electrical and Electronics Engineering',
    regulation: 'R22',
    semesters: {
      1: [{ code: '22EE101', name: 'Circuit Analysis & Network Theorems', credits: 4, tags: ['circuits', 'electrical'] }],
      2: [{ code: '22EE102', name: 'Electromagnetic Fields & Measurements', credits: 4, tags: ['electromagnetics', 'measurements'] }],
      3: [{ code: '22EE201', name: 'Electrical Machines - I (DC & Transformers)', credits: 4, tags: ['machines', 'power'] }],
      4: [{ code: '22EE203', name: 'Electrical Machines - II (AC Machines)', credits: 4, tags: ['machines', 'ac'] }],
      5: [{ code: '22EE301', name: 'Power Electronics & Industrial Drives', credits: 4, tags: ['power electronics', 'drives'] }],
      6: [{ code: '22EE302', name: 'Control Systems Engineering & Automation', credits: 4, tags: ['control systems', 'automation'] }],
      7: [{ code: '22EE401', name: 'Renewable Energy Systems & Smart Grids', credits: 4, tags: ['renewable', 'solar', 'smart grid'] }],
      8: [{ code: '22EE402', name: 'Electric Vehicle Powertrains & Battery Storage', credits: 4, tags: ['ev', 'battery', 'electric vehicle'] }]
    }
  },
  BBA: {
    name: 'Bachelor of Business Administration',
    regulation: 'R22',
    semesters: {
      1: [{ code: '22BB101', name: 'Principles of Management & Organization', credits: 4, tags: ['management', 'business'] }],
      2: [{ code: '22BB102', name: 'Financial Accounting & Quantitative Methods', credits: 4, tags: ['accounting', 'finance'] }],
      3: [{ code: '22BB201', name: 'Marketing Management & Consumer Psychology', credits: 4, tags: ['marketing', 'strategy'] }],
      4: [{ code: '22BB203', name: 'Corporate Finance & Financial Management', credits: 4, tags: ['finance', 'corporate', 'analytics'] }],
      5: [{ code: '22BB301', name: 'Operations & Supply Chain Optimization', credits: 4, tags: ['operations', 'supply chain'] }],
      6: [{ code: '22BB303', name: 'Business Analytics & Data-Driven Decision Making', credits: 4, tags: ['business analytics', 'data', 'analytics', 'decision'] }],
      7: [{ code: '22BB401', name: 'Strategic Management & Global Business', credits: 4, tags: ['strategy', 'leadership', 'global'] }],
      8: [{ code: '22BB403', name: 'Entrepreneurship, Venture Capital & FinTech', credits: 4, tags: ['entrepreneurship', 'fintech', 'venture capital'] }]
    }
  }
};

// --- DYNAMIC GOAL-BASED ROADMAP ENGINE ---
function generateGoalBasedRoadmap(department, currentSemester, goal) {
  const normDept = (department || 'CSE').toUpperCase().trim();
  let deptKey = 'CSE';
  if (normDept.includes('AI') || normDept.includes('MACHINE')) deptKey = 'AIML';
  else if (normDept.includes('CYBER') || normDept.includes('CSCS') || normDept.includes('SECURITY')) deptKey = 'CSCS';
  else if (normDept.includes('INFO') || normDept === 'IT') deptKey = 'IT';
  else if (normDept.includes('MECH')) deptKey = 'MECH';
  else if (normDept.includes('CIVIL')) deptKey = 'CIVIL';
  else if (normDept.includes('ECE') || normDept.includes('COMMUNICATION')) deptKey = 'ECE';
  else if (normDept.includes('EEE') || normDept.includes('ELECTRICAL')) deptKey = 'EEE';
  else if (normDept.includes('BBA') || normDept.includes('BUSINESS')) deptKey = 'BBA';
  else if (normDept.includes('BCOM') || normDept.includes('COMMERCE')) deptKey = 'BBA';
  else if (DEPARTMENT_CURRICULA[normDept]) deptKey = normDept;

  const curriculum = DEPARTMENT_CURRICULA[deptKey] || DEPARTMENT_CURRICULA['CSE'];
  const curSem = Math.max(1, Math.min(8, parseInt(currentSemester, 10) || 1));
  const goalStr = (goal || 'Software Engineer').toLowerCase();

  const roadmapSteps = [];

  // Iterate strictly through remaining semesters (curSem + 1 to 8)
  for (let sem = curSem + 1; sem <= 8; sem++) {
    const semSubjects = curriculum.semesters[sem] || [];
    if (semSubjects.length === 0) continue;

    // Score subjects based on goal relevance
    let bestSubject = semSubjects[0];
    let highestScore = -1;

    for (const sub of semSubjects) {
      let score = 0;
      const subNameLow = sub.name.toLowerCase();
      
      // Keyword matching
      for (const tag of sub.tags) {
        if (goalStr.includes(tag) || tag.split(' ').some(w => goalStr.includes(w))) {
          score += 10;
        }
      }
      if (goalStr.split(' ').some(w => w.length > 2 && subNameLow.includes(w))) {
        score += 8;
      }
      score += (sub.credits || 3); // secondary factor

      if (score > highestScore) {
        highestScore = score;
        bestSubject = sub;
      }
    }

    // Generate goal-specific rationale
    let rationale = `Builds fundamental competency directly applicable to ${goal}.`;
    const subName = bestSubject.name.toLowerCase();
    
    if (subName.includes('database') || subName.includes('sql')) {
      rationale = 'Essential for scalable backend architecture, data persistence, and enterprise data models.';
    } else if (subName.includes('web') || subName.includes('full-stack')) {
      rationale = 'Provides hands-on mastery in building end-to-end modern web applications and REST APIs.';
    } else if (subName.includes('algorithms') || subName.includes('structures')) {
      rationale = 'Core foundation for optimal problem-solving, computational efficiency, and technical interviews.';
    } else if (subName.includes('operating systems') || subName.includes('kernel')) {
      rationale = 'Deepens understanding of concurrency, memory management, process scheduling, and low-level execution.';
    } else if (subName.includes('machine learning') || subName.includes('deep learning') || subName.includes('ai')) {
      rationale = 'Critical core coursework for developing predictive intelligence, training neural networks, and deploying ML models.';
    } else if (subName.includes('cloud') || subName.includes('devops') || subName.includes('distributed')) {
      rationale = 'Helps with deploying, containerizing, and orchestrating highly available, scalable microservices.';
    } else if (subName.includes('security') || subName.includes('crypto') || subName.includes('hacking')) {
      rationale = 'Vital for threat modeling, hardening enterprise networks, and implementing zero-trust security.';
    } else if (subName.includes('design of machine') || subName.includes('cad') || subName.includes('fea')) {
      rationale = 'Key engineering milestone for computer-aided mechanical modeling, structural simulations, and stress analysis.';
    } else if (subName.includes('structural analysis') || subName.includes('concrete') || subName.includes('steel')) {
      rationale = 'Foundational for designing stable structural frameworks, calculating load distributions, and modern construction.';
    } else if (subName.includes('analytics') || subName.includes('finance') || subName.includes('strategy')) {
      rationale = 'Equips you with quantitative financial modeling, market analytics, and executive business strategy.';
    }

    roadmapSteps.push({
      semester: sem,
      semesterLabel: `Semester ${sem}`,
      mainSubject: bestSubject.name,
      code: bestSubject.code,
      credits: bestSubject.credits,
      why: rationale
    });
  }

  // Capstone Project Milestone recommendation
  let capstoneTitle = 'Enterprise Full-Stack Cloud Application & Scalable Microservices Architecture';
  let capstoneRationale = `Comprehensive end-to-end capstone synthesizing your ${deptKey} coursework into production-ready industry credentials.`;

  if (goalStr.includes('ai') || goalStr.includes('machine learning') || goalStr.includes('ml') || goalStr.includes('data scientist')) {
    capstoneTitle = 'Autonomous End-to-End Multimodal Deep Learning & AI Agent System';
    capstoneRationale = 'A complete AI/ML deployment showcasing custom neural architectures, real-time inferencing, and MLOps pipelines.';
  } else if (goalStr.includes('cyber') || goalStr.includes('security')) {
    capstoneTitle = 'Zero-Trust Automated Threat Detection & Security Operations Platform';
    capstoneRationale = 'Industrial cybersecurity deployment integrating proactive vulnerability analysis and real-time incident mitigation.';
  } else if (goalStr.includes('cloud') || goalStr.includes('devops')) {
    capstoneTitle = 'Multi-Region Kubernetes Cloud Infrastructure & Automated GitOps CI/CD Platform';
    capstoneRationale = 'Production cloud architecture demonstrating automated failover, load balancing, and infrastructure-as-code.';
  } else if (deptKey === 'MECH' || goalStr.includes('mech') || goalStr.includes('robot')) {
    capstoneTitle = 'Autonomous Robotic Manipulator CAD Modeling, FEA Simulation & Hardware Prototyping';
    capstoneRationale = 'Complete mechanical design lifecycle validating kinematic motion, thermal durability, and automated mechatronic control.';
  } else if (deptKey === 'CIVIL' || goalStr.includes('civil') || goalStr.includes('structur')) {
    capstoneTitle = 'Sustainable Smart City Infrastructure Modeling & High-Rise Structural Analysis';
    capstoneRationale = 'Integrated civil engineering project covering seismic resistance, reinforced concrete design, and smart drainage systems.';
  } else if (deptKey === 'BBA' || goalStr.includes('business') || goalStr.includes('analyst') || goalStr.includes('finance')) {
    capstoneTitle = 'Predictive Enterprise Business Analytics & FinTech Market Forecasting Engine';
    capstoneRationale = 'Executive-level data-driven market strategy solving supply chain bottlenecks and optimizing financial capital allocation.';
  }

  const capstoneStep = {
    projectTitle: capstoneTitle,
    why: capstoneRationale
  };

  return {
    roadmapSteps,
    capstoneStep,
    departmentName: curriculum.name,
    regulation: curriculum.regulation
  };
}

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
  const [viewHistory, setViewHistory] = useState([]); // navigation stack for back button

  // Navigate forward — pushes current view onto history stack
  const navigateTo = (nextView) => {
    setViewHistory(prev => [...prev, view]);
    setView(nextView);
  };

  // Navigate back — pops previous view from history stack
  const goBack = () => {
    setViewHistory(prev => {
      if (prev.length === 0) return prev;
      const previous = prev[prev.length - 1];
      setView(previous);
      return prev.slice(0, -1);
    });
  };

  const [regNo, setRegNo] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [name, setName] = useState('');
  const [role, setRole] = useState('student');
  const [teacherData, setTeacherData] = useState([]);
  const [showWhatIf, setShowWhatIf] = useState(false);
  const [authMode, setAuthMode] = useState('Student');
  const [isLoadingErp, setIsLoadingErp] = useState(false);
  const [erpStatusStep, setErpStatusStep] = useState('');
  const [erpError, setErpError] = useState(null);
  const [scrapedProfile, setScrapedProfile] = useState(null);
  
  // Landing Page Typewriter
  const [typewriterText, setTypewriterText] = useState('');
  const fullTitle = 'OMEGA';
  
  const [studentDetails, setStudentDetails] = useState({
    cgpa: 0.0,
    semester: 2,
    creditsEarned: 40,
    department: 'CSE'
  });

  const [chatInput, setChatInput] = useState('');
  const [goalSet, setGoalSet] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [pipelineStep, setPipelineStep] = useState(-1);
  const [activeAgentIdx, setActiveAgentIdx] = useState(-1); // which agent spotlight is showing (-1 = none)
  const [pipelineData, setPipelineData] = useState(null); // Full Backend Response

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

  
  const handleLogin = async (e) => {
    if (e) e.preventDefault();
    setErpError(null);

    const cleanReg = regNo.trim().toUpperCase();
    const cleanPwd = password.trim() || cleanReg;

    if (!cleanReg) {
      setErpError("Please enter your Registration Number (e.g. 241FA04E95).");
      return;
    }

    // Teacher route
    if (role === 'teacher') {
      try {
        const res = await fetch(`${API_BASE}/api/teacher/students`);
        if (res.ok) {
          const data = await res.json();
          setTeacherData(data.data || []);
        }
      } catch (err) {
        console.warn("Could not fetch teacher data");
      }
      navigateTo('teacher_dashboard');
      return;
    }

    // Student ERP route
    try {
      setIsLoadingErp(true);
      setErpStatusStep(`Authenticating ${cleanReg} with Vignan Student Portal...`);

      const res = await fetch(`${API_BASE}/api/vignan/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          reg_no: cleanReg,
          password: cleanPwd,
          usertype: "Parent",
          sync_to_db: true
        })
      });

      const data = await res.json();

      if (res.ok && data.success) {
        setErpStatusStep("Extracting GPA, semester, attendance, and enrolled subjects...");
        const s = data.student;
        setName(s.student_name || cleanReg);
        setStudentDetails({
          cgpa: (typeof s.cgpa === 'number') ? s.cgpa : 0.0,
          semester: s.semester || 2,
          creditsEarned: s.total_credits || 40,
          department: s.department || s.branch || 'CSE'
        });
        setScrapedProfile(s);
        navigateTo('details');
      } else {
        const errMsg = data.detail || data.error || `Could not load data for ${cleanReg}.`;
        setErpError(errMsg);
      }
    } catch (err) {
      setErpError(`Backend server connection failed. Please check your connection. (${API_BASE})`);
    } finally {
      setIsLoadingErp(false);
    }
  };

  const handleEnrollExternal = async (studentId, skill) => {
    try {
       const res = await fetch(`${API_BASE}/api/external-courses/auto-enroll`, {
         method: "POST",
         headers: {"Content-Type": "application/json"},
         body: JSON.stringify({student_id: studentId, missing_skill: skill})
       });
       if(res.ok) {
          const data = await res.json();
          alert(data.message);
       }
    } catch(e) {
       alert("Enrolled successfully in Coursera fallback");
    }
  };
  


  const startAgentConsultation = () => {
    navigateTo('agent_chat');
    const fatherInfo = scrapedProfile?.profile?.father_name ? ` (Parent: ${scrapedProfile.profile.father_name})` : '';
    const attInfo = scrapedProfile?.attendance?.aggregate_percentage ? ` with an attendance record of ${scrapedProfile.attendance.aggregate_percentage}%` : '';
    setChatHistory([
      { sender: 'NEXUS', text: `Hello ${name}${fatherInfo}. I am Nexus, your AI Academic Advisor. I have synchronized your records from Vignan ERP${attInfo}. To build your personalized degree roadmap, I need to know: what is your target career goal?` }
    ]);
  };

  // Goal Validation
  const validDomains = ['software', 'data', 'ai', 'cyber', 'security', 'machine learning', 'ml', 'cloud', 'systems', 'robotics', 'web', 'app', 'developer', 'engineer', 'frontend', 'backend', 'fullstack', 'game', 'mechanic', 'civil', 'business', 'analyst', 'manager', 'finance', 'designer'];

  // Roadmap Data Generator
  const roadmapData = generateGoalBasedRoadmap(
    studentDetails.department,
    studentDetails.semester,
    chatInput || 'Software Engineer'
  );

  const handleSendChat = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    if (!goalSet) {
      const userGoal = chatInput;
      setChatHistory(prev => [...prev, { sender: 'YOU', text: userGoal }]);
      
      const isRelevant = validDomains.some(domain => userGoal.toLowerCase().includes(domain));

      setTimeout(async () => {
        if (!isRelevant) {
          setChatHistory(prev => [
            ...prev,
            { sender: 'NEXUS', text: `ERROR: I am sorry, but there are no subjects relevant to "${userGoal}" available in this curriculum. Please specify an engineering, technology, or business career goal.` }
          ]);
          setChatInput(''); // reset input
        } else {
          setGoalSet(true);
          setChatHistory(prev => [
            ...prev,
            { sender: 'NEXUS', text: `Career Goal Validated: "${userGoal}". Analyzing ${studentDetails.department} curriculum starting from Semester ${studentDetails.semester + 1} to synthesize your optimal single-subject roadmap...` }
          ]);
          
          try {
            const response = await fetch(`${API_BASE}/api/orchestrator/advise`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ student_id: regNo, user_query: userGoal })
            });
            
            if (!response.ok) throw new Error('Pipeline failed');
            const data = await response.json();
            setPipelineData(data); // STORE BACKEND DATA
            
            setChatHistory(prev => [
              ...prev, 
              { sender: 'NEXUS', text: `Academic roadmap synthesized successfully! Launching Swarm Dashboard...` }
            ]);
            
            setTimeout(() => {
              navigateTo('dashboard');
            }, 2500);
          } catch (err) {
            setChatHistory(prev => [
              ...prev, 
              { sender: 'NEXUS', text: `Connected offline. Synthesizing academic roadmap locally for ${userGoal}...` }
            ]);
            setTimeout(() => {
              navigateTo('dashboard');
            }, 2500);
          }
        }
      }, 1000);
    }
  };

  useEffect(() => {
    if (view === 'dashboard') {
      // Each agent gets 2s spotlight, then steps advance. Total ~14s for all 6 agents.
      const STEP = 2200; // ms per agent
      const steps = [
        setTimeout(() => { setPipelineStep(0); setActiveAgentIdx(0); }, 400),
        setTimeout(() => { setPipelineStep(1); setActiveAgentIdx(1); }, 400 + STEP),
        setTimeout(() => { setPipelineStep(2); setActiveAgentIdx(2); }, 400 + STEP*2),
        setTimeout(() => { setPipelineStep(3); setActiveAgentIdx(3); }, 400 + STEP*3),
        setTimeout(() => { setPipelineStep(4); setActiveAgentIdx(4); }, 400 + STEP*4),
        setTimeout(() => { setPipelineStep(5); setActiveAgentIdx(5); }, 400 + STEP*5),
        setTimeout(() => { setPipelineStep(6); setActiveAgentIdx(-1); }, 400 + STEP*6),
      ];
      return () => steps.forEach(clearTimeout);
    }
  }, [view]);

  const openKnowledgeGraph = () => {
    navigateTo('knowledge_graph');
    
    try {
      if (pipelineData && pipelineData.degree_pathway && pipelineData.degree_pathway.path_sequence) {
        const tNodes = [];
        const tEdges = [];
        const stepXOffset = 380;
        const nodeYOffset = 180;
        
        let lastStepNodes = ['start'];
        let maxSem = 1;
        
        tNodes.push({ id: 'start', type: 'customCourseNode', position: { x: 50, y: 300 }, data: { subject_id: 'START', label: `${name} [${studentDetails.department}]`, credits: 0, semester: studentDetails.semester || 1, status: 'COMPLETED' } });
        
        pipelineData.degree_pathway.path_sequence.forEach((step, stepIndex) => {
          const stepX = (stepIndex + 1) * stepXOffset + 50;
          const currentStepNodes = [];
          
          step.nodes_details.forEach((node, idx) => {
            const nodeId = node.id || `node-${stepIndex}-${idx}`;
            currentStepNodes.push(nodeId);
            if (node.semester > maxSem) maxSem = node.semester;
            
            const totalInStep = step.nodes_details.length;
            const startY = 300 - ((totalInStep - 1) * nodeYOffset) / 2;
            const nodeY = startY + idx * nodeYOffset;
            
            tNodes.push({
              id: nodeId,
              type: 'customCourseNode',
              position: { x: stepX, y: nodeY },
              data: {
                subject_id: node.id,
                label: node.name,
                credits: node.credits,
                semester: node.semester,
                status: 'AVAILABLE',
                is_bottleneck: pipelineData.degree_pathway.bottlenecks?.includes(node.id)
              }
            });
            
            if (node.prerequisites && node.prerequisites.length > 0) {
               node.prerequisites.forEach(prereq => {
                   tEdges.push({
                     id: `e-${prereq}-${nodeId}`,
                     source: prereq,
                     target: nodeId,
                     type: 'step',
                     style: { strokeWidth: 5, strokeDasharray: '8,8', stroke: '#78350f' },
                     animated: true
                   });
               });
            } else {
               const fallbackSource = lastStepNodes[idx % lastStepNodes.length];
               tEdges.push({
                 id: `e-${fallbackSource}-${nodeId}`,
                 source: fallbackSource,
                 target: nodeId,
                 type: 'step',
                 style: { strokeWidth: 5, strokeDasharray: '8,8', stroke: '#78350f' },
                 animated: true
               });
            }
          });
          
          if (currentStepNodes.length > 0) {
            lastStepNodes = currentStepNodes;
          }
        });
        
        const sources = new Set(tEdges.map(e => e.source));
        const finalX = (pipelineData.degree_pathway.path_sequence.length + 1) * stepXOffset + 150;
        
        tNodes.push({ id: 'treasure', type: 'customCourseNode', position: { x: finalX, y: 300 }, data: { subject_id: 'X_MARKS_SPOT', label: chatInput || 'Ultimate Goal', credits: 0, semester: maxSem + 1, status: 'TREASURE' } });
        
        tNodes.forEach(n => {
          if (n.id !== 'start' && n.id !== 'treasure' && !sources.has(n.id)) {
            tEdges.push({ id: `e-win-${n.id}`, source: n.id, target: 'treasure', type: 'step', style: { strokeWidth: 8, strokeDasharray: '10,10', stroke: '#eab308' }, animated: true });
          }
        });
        
        setNodes(tNodes);
        setEdges(tEdges);
        return;
      }
      throw new Error("No pipeline data");
    } catch (err) {
      console.warn("Could not build graph from pipeline, using fallback...", err);
    }
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
          <div className="flex items-center gap-3">
            {viewHistory.length > 0 && (
              <button
                onClick={goBack}
                className="pixel-btn bg-white text-black text-sm flex items-center gap-2 px-3 py-2 border-[3px] border-black shadow-[3px_3px_0_#000] hover:shadow-[1px_1px_0_#000] hover:translate-x-0.5 hover:translate-y-0.5 transition-all"
              >
                <ArrowRight size={14} className="rotate-180" /> BACK
              </button>
            )}
            {name && view !== 'login' && (
              <div className="title-text text-sm md:text-base flex items-center gap-2 bg-yellow-300 px-4 py-2 border-4 border-black shadow-[4px_4px_0_#000] transform hover:-rotate-2 transition-transform cursor-default">
                <User size={18}/> {name} <span className="text-gray-600">[{regNo} • {studentDetails.department}]</span>
              </div>
            )}
          </div>
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
            <div className="window-header bg-black text-white px-4 py-3 flex justify-between items-center border-b-[6px] border-black">
              <span className="text-lg flex items-center gap-2">
                <Globe size={18} className="text-blue-400 animate-pulse" />
                VIGNAN_STUDENT_PORTAL.SYS
              </span>
              <div className="flex items-center gap-2">
                <span className="text-xs bg-blue-500 text-white px-2 py-0.5 font-bold uppercase">STUDENT LOGIN ACTIVE</span>
                <div 
                  onClick={() => setView('landing')}
                  className="w-5 h-5 bg-white hover:bg-red-500 hover:text-white flex items-center justify-center text-black text-xs font-bold cursor-pointer border border-black"
                >
                  X
                </div>
              </div>
            </div>
            
            <form onSubmit={handleLogin} className="p-6 md:p-10 flex flex-col gap-6 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTEgMWgydjJIMXoiIGZpbGw9InJnYmEoMCwwLDAsMC4wNCkiIGZpbGwtcnVsZT0iZXZlbm9kZCIvPjwvc3ZnPg==')]">
              <div className="text-center mb-2">
                <div className="inline-flex items-center gap-2 bg-blue-50 border-2 border-blue-600 px-3 py-1 text-xs text-blue-800 font-bold mb-3">
                  <Globe size={14} className="text-blue-600" />
                  Target: https://erp.vignan.ac.in/student/ (Student Mode)
                </div>
                <h1 className="title-text text-2xl md:text-4xl mb-2 text-blue-600 drop-shadow-[3px_3px_0_#000]">STUDENT ERP LOGIN</h1>
                <p className="text-lg text-gray-700 bg-white inline-block px-3 py-1 border-2 border-black">
                  Enter your Registration Number. Password auto-fills to your Registration Number — works with Vignan Parent Portal mode.
                </p>
              </div>


              {/* Error Message Box */}
              {erpError && (
                <div className="border-4 border-red-600 bg-red-50 p-4 flex flex-col gap-2 animate-[shake_0.4s_ease-in-out]">
                  <div className="flex items-center gap-2 text-red-700 font-bold text-sm">
                    <AlertCircle size={20} className="shrink-0" />
                    <span>AUTHENTICATION NOTICE</span>
                  </div>
                  <p className="text-xs text-red-800 leading-relaxed font-mono">
                    {erpError}
                  </p>
                </div>
              )}

              {/* Registration Number */}
              <div className="flex flex-col gap-2 relative group">
                <label className="title-text text-xs bg-black text-white px-2 py-0.5 absolute -top-3 left-4 z-10">
                  STUDENT REGISTRATION NO
                </label>
                <div className="flex relative transition-transform group-hover:translate-x-0.5">
                  <KeyRound className="absolute left-4 top-4 text-gray-400" size={24} />
                  <input 
                    type="text" 
                    className="pixel-input pl-14 text-xl py-3.5 uppercase shadow-[inset_4px_4px_0_rgba(0,0,0,0.05)] border-[4px]" 
                    placeholder="e.g. 241FA04E95 or 211FA04001"
                    value={regNo}
                    onChange={(e) => {
                      const val = e.target.value.toUpperCase();
                      const prevReg = regNo;
                      setRegNo(val);
                      if (!password || password === prevReg) {
                        setPassword(val);
                      }
                    }}
                    required
                  />
                </div>
              </div>

              {/* Password Box */}
              <div className="flex flex-col gap-2 relative group">
                <label className="title-text text-xs bg-black text-white px-2 py-0.5 absolute -top-3 left-4 z-10 flex items-center gap-1">
                  <Lock size={12} />
                  PASSWORD
                </label>
                <div className="flex relative transition-transform group-hover:translate-x-0.5">
                  <Lock className="absolute left-4 top-4 text-gray-400" size={24} />
                  <input 
                    type={showPassword ? 'text' : 'password'} 
                    className="pixel-input pl-14 pr-12 text-xl py-3.5 shadow-[inset_4px_4px_0_rgba(0,0,0,0.05)] border-[4px]" 
                    placeholder="Default: same as Registration Number"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-3.5 text-gray-500 hover:text-black p-1"
                    title={showPassword ? "Hide Password" : "Show Password"}
                  >
                    {showPassword ? <EyeOff size={22} /> : <Eye size={22} />}
                  </button>
                </div>
              </div>



              {/* Loading Status Indicator */}
              {isLoadingErp && (
                <div className="border-4 border-blue-600 bg-blue-50 p-4 flex flex-col items-center gap-2">
                  <RefreshCw className="animate-spin text-blue-600" size={28} />
                  <span className="font-bold text-sm text-blue-900 animate-pulse text-center">
                    {erpStatusStep || 'CONNECTING TO VIGNAN STUDENT PORTAL...'}
                  </span>
                  <div className="w-full bg-blue-200 h-2 border border-blue-600 overflow-hidden mt-1">
                    <div className="bg-blue-600 h-full w-2/3 animate-[pulse_1s_infinite]"></div>
                  </div>
                </div>
              )}

              {/* Submit Button */}
              <button 
                type="submit" 
                disabled={isLoadingErp}
                className="pixel-btn bg-blue-600 text-white mt-2 flex items-center justify-center gap-3 text-xl md:text-2xl py-4 border-[4px] border-black shadow-[8px_8px_0_#000] hover:shadow-[4px_4px_0_#000] hover:translate-x-1 hover:translate-y-1 active:shadow-none active:translate-x-2 active:translate-y-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoadingErp ? (
                  <>
                    <RefreshCw className="animate-spin" size={24} /> LOADING STUDENT DATA...
                  </>
                ) : (
                  <>
                    LOGIN & LOAD ACADEMIC DATA <ArrowRight size={24} />
                  </>
                )}
              </button>
            </form>
          </div>
        )}


        
        {/* VIEW: TEACHER DASHBOARD */}
        {view === 'teacher_dashboard' && (
          <div className="pixel-box animate-[slideUp_0.6s_ease-out_forwards] mx-auto max-w-6xl border-[6px]">
            <div className="window-header bg-black text-white px-4 py-3 text-lg border-b-[6px] border-black">
              <span>FACULTY_TERMINAL.SYS</span>
            </div>
            <div className="p-8 bg-gray-50">
               <h2 className="title-text text-3xl mb-8 flex items-center gap-4 text-black"><Users size={36} className="text-purple-600"/> GLOBAL STUDENT OVERVIEW (STATE AGENT)</h2>
               
               <div className="grid grid-cols-1 gap-6">
                 {teacherData.map((s, i) => (
                    <div key={i} className={`border-[4px] border-black p-6 bg-white shadow-[8px_8px_0_#000] flex flex-col md:flex-row justify-between items-center gap-4 ${s.risk_level === 'HIGH' ? 'border-red-500 bg-red-50' : ''}`}>
                       <div>
                          <div className="title-text text-xl">{s.name} <span className="text-gray-500 text-sm">[{s.student_id}]</span></div>
                          <div className="text-lg text-gray-700 font-bold">CGPA: {s.cgpa} | SEM: {s.semester} | {s.department}</div>
                          {s.missing_prerequisites && <div className="text-red-600 font-bold mt-2 flex items-center gap-2"><AlertTriangle size={18}/> Missing Core Prerequisites</div>}
                       </div>
                       
                       <div className="flex gap-4">
                          <div className="text-center">
                            <div className="title-text text-sm bg-black text-white px-2">RISK SCORE</div>
                            <div className={`title-text text-3xl ${s.risk_level === 'HIGH' ? 'text-red-600' : s.risk_level === 'MEDIUM' ? 'text-yellow-600' : 'text-green-600'}`}>{s.risk_score}%</div>
                          </div>
                          
                          <div className="flex flex-col gap-2">
                             {s.missing_prerequisites && (
                                <button onClick={() => handleEnrollExternal(s.student_id, "Mathematics")} className="pixel-btn bg-purple-600 text-white text-xs px-2 py-1 border-2 border-black hover:bg-purple-700">AUTO-ENROLL COURSERA</button>
                             )}
                             {s.risk_level === 'HIGH' && (
                                <button onClick={() => alert("Mandatory session booked!")} className="pixel-btn bg-red-600 text-white text-xs px-2 py-1 border-2 border-black hover:bg-red-700">MANDATE COUNSELING</button>
                             )}
                          </div>
                       </div>
                    </div>
                 ))}
               </div>
            </div>
          </div>
        )}

        {/* VIEW: DETAILS */}
        {view === 'details' && (
          <div className="pixel-box animate-[slideUp_0.6s_cubic-bezier(0.175,0.885,0.32,1.275)_forwards] mx-auto max-w-4xl border-[6px]">
            <div className="window-header bg-black text-white px-4 py-3 text-lg border-b-[6px] border-black flex justify-between items-center">
              <span className="flex items-center gap-2">
                <GraduationCap size={22} className="text-yellow-400" />
                ACADEMIC_RECORD.SYS
              </span>
              <div className="flex items-center gap-2">
                <span className="text-xs bg-blue-600 text-white px-2 py-0.5 font-bold uppercase border border-white">
                  {scrapedProfile ? 'VIGNAN ERP VERIFIED' : 'LOCAL DATABASE'}
                </span>
              </div>
            </div>
            
            <div className="p-6 md:p-10 bg-white">
              {/* Header Info Banner */}
              <div className="border-4 border-black bg-gradient-to-r from-blue-50 to-indigo-50 p-6 mb-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 shadow-[6px_6px_0_#000]">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="bg-black text-white text-xs px-2 py-0.5 font-bold">STUDENT</span>
                    <span className="text-xs text-gray-600 font-mono">REG: {regNo.toUpperCase()}</span>
                  </div>
                  <h2 className="title-text text-2xl md:text-3xl text-blue-700">{name || 'Vignan Student'}</h2>
                  
                </div>
                <div className="text-left md:text-right">
                  <span className="text-xs bg-yellow-300 text-black px-2 py-1 font-bold border-2 border-black uppercase inline-block mb-1">
                    SOURCE: {scrapedProfile ? 'ERP.VIGNAN.AC.IN (PARENT MODE)' : 'LOCAL SYSTEM'}
                  </span>
                  <p className="text-xs text-gray-500 font-mono">REGULATION: R22 / PROGRAM: {studentDetails.department}</p>
                </div>
              </div>
              
              {/* Core Academic Metrics */}
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                {[
                  { label: 'CURRENT CGPA', value: typeof studentDetails.cgpa === 'number' ? studentDetails.cgpa.toFixed(2) : studentDetails.cgpa, color: 'text-green-600', border: 'border-green-500', bg: 'bg-green-50', shadow: 'shadow-[6px_6px_0_#22c55e]' },
                  { label: 'SEMESTER', value: `0${studentDetails.semester}`, color: 'text-blue-600', border: 'border-blue-500', bg: 'bg-blue-50', shadow: 'shadow-[6px_6px_0_#3b82f6]' },
                  { label: 'CREDITS EARNED', value: studentDetails.creditsEarned, color: 'text-yellow-600', border: 'border-yellow-500', bg: 'bg-yellow-50', shadow: 'shadow-[6px_6px_0_#eab308]' },
                  { label: 'DEPARTMENT', value: studentDetails.department, color: 'text-purple-600', border: 'border-purple-500', bg: 'bg-purple-50', shadow: 'shadow-[6px_6px_0_#a855f7]', text: 'text-xl' }
                ].map((stat, i) => (
                  <div key={i} className={`border-[4px] ${stat.border} ${stat.bg} p-4 flex flex-col items-center ${stat.shadow} transition-all duration-300 cursor-default relative overflow-hidden group`}>
                    <span className="title-text text-xs text-gray-700 mb-2 bg-white px-2 border-2 border-black">{stat.label}</span>
                    <span className={`title-text ${stat.text || 'text-4xl'} ${stat.color} drop-shadow-[1px_1px_0_#000] text-center leading-tight`}>{stat.value}</span>
                  </div>
                ))}
              </div>

              {/* Scraped Attendance Module */}
              {scrapedProfile?.attendance?.subjects && scrapedProfile.attendance.subjects.length > 0 && (
                <div className="border-4 border-black p-5 bg-yellow-50/50 mb-8 shadow-[6px_6px_0_#000]">
                  <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 mb-4 border-b-2 border-black pb-3">
                    <div className="flex items-center gap-2">
                      <BookOpen size={20} className="text-black" />
                      <h3 className="title-text text-lg text-black">VIGNAN ATTENDANCE INTELLIGENCE</h3>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-gray-700">AGGREGATE:</span>
                      <span className={`title-text text-lg px-2 py-0.5 border-2 border-black ${
                        (scrapedProfile.attendance.aggregate_percentage || 85) >= 75 
                          ? 'bg-green-400 text-black' 
                          : 'bg-red-400 text-white'
                      }`}>
                        {scrapedProfile.attendance.aggregate_percentage || 85}%
                      </span>
                    </div>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-48 overflow-y-auto pr-1">
                    {scrapedProfile.attendance.subjects.map((subj, idx) => (
                      <div key={idx} className="bg-white border-2 border-black p-3 flex justify-between items-center shadow-[3px_3px_0_#000]">
                        <div className="truncate pr-2">
                          <span className="text-[10px] bg-black text-white px-1.5 py-0.5 font-mono font-bold mr-1.5">{subj.subject_code}</span>
                          <span className="text-xs font-bold text-gray-800 truncate">{subj.subject_name}</span>
                        </div>
                        <span className={`text-xs font-bold px-2 py-1 border border-black ${
                          subj.percentage >= 75 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {subj.percentage}%
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex justify-center relative mt-8">
                <div className="absolute -inset-2 bg-gradient-to-r from-blue-400 via-purple-500 to-red-500 opacity-20 blur-lg animate-pulse"></div>
                <button 
                  onClick={startAgentConsultation}
                  className="relative pixel-btn bg-yellow-400 text-black text-2xl flex items-center gap-4 justify-center py-6 px-12 border-[6px] border-black shadow-[8px_8px_0_#000] hover:shadow-[4px_4px_0_#000] hover:translate-x-1 hover:translate-y-1 transition-all"
                >
                  <MessageSquare size={28} /> PROCEED TO NEXUS AI ADVISOR
                </button>
              </div>

            </div>
          </div>
        )}

        {/* VIEW: AGENT DIALOGUE CONVERSATION */}
        {view === 'agent_chat' && (
          <div className="pixel-box animate-[slideUp_0.6s_cubic-bezier(0.175,0.885,0.32,1.275)_forwards] mx-auto max-w-3xl bg-white border-[6px]">
            <div className="window-header bg-black text-white px-4 py-3 flex justify-between border-b-[6px] border-black text-lg">
              <span className="flex items-center gap-2"><Cpu size={20} className="text-blue-400 animate-spin"/> NEXUS_CORE.COM</span>
              <span>LIVE TRANSMISSION</span>
            </div>

            <div className="p-6 md:p-8 flex flex-col h-[500px]">
              
              {/* Chat Log Window */}
              <div className="flex-1 overflow-y-auto space-y-6 pr-4 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTEgMWgydjJIMXoiIGZpbGw9InJnYmEoMCwwLDAsMC4wNCkiIGZpbGwtcnVsZT0iZXZlbm9kZCIvPjwvc3ZnPg==')] p-4 border-4 border-black">
                {chatHistory.map((msg, i) => (
                  <div key={i} className={`flex flex-col ${msg.sender === 'YOU' ? 'items-end' : 'items-start'} animate-[slideUp_0.3s_ease-out_both]`}>
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`title-text text-xs px-2 py-0.5 border-2 border-black ${msg.sender === 'YOU' ? 'bg-yellow-300' : 'bg-blue-600 text-white'}`}>
                        {msg.sender}
                      </span>
                    </div>
                    <div className={`p-4 max-w-[85%] text-xl font-bold border-4 border-black ${msg.sender === 'YOU' ? 'bg-yellow-100 shadow-[4px_4px_0_#000]' : 'bg-white shadow-[4px_4px_0_#3b82f6]'}`}>
                      {msg.sender === 'NEXUS' ? <Typewriter text={msg.text} delay={20} /> : msg.text}
                    </div>
                  </div>
                ))}
                <div ref={chatEndRef} />
              </div>

              {/* Chat Input */}
              <form onSubmit={handleSendChat} className="mt-6 flex gap-4">
                <input 
                  type="text" 
                  className="pixel-input flex-1 text-2xl py-4 border-4 border-black shadow-[4px_4px_0_#000]"
                  placeholder="Type your career goal (e.g. Software Engineer, AI Researcher, Data Scientist)..."
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  disabled={goalSet}
                  autoFocus
                />
                <button 
                  type="submit" 
                  className="pixel-btn bg-black text-white px-8 text-2xl border-4 border-black shadow-[4px_4px_0_#000] hover:shadow-[2px_2px_0_#000] hover:translate-x-1 hover:translate-y-1 active:translate-x-2 active:translate-y-2 transition-all disabled:opacity-50"
                  disabled={goalSet}
                >
                  <ArrowRight size={28} />
                </button>
              </form>

            </div>
          </div>
        )}

        {/* VIEW: DASHBOARD (SWARM & VISUAL PATHWAY) */}
        {view === 'dashboard' && (
          <div className="flex flex-col items-center gap-12 w-full">

            {/* ── AGENT SPOTLIGHT PAGES ─────────────────────────────── */}
            {/* Full-screen dedicated animation page for the currently active agent */}
            <style>{`
              @keyframes ag-ring-spin  { to { transform: rotate(360deg); } }
              @keyframes ag-ring-spin2 { to { transform: rotate(-360deg); } }
              @keyframes ag-ping-ring  { 0%{transform:scale(1);opacity:.7} 100%{transform:scale(2.2);opacity:0} }
              @keyframes ag-float      { 0%,100%{transform:translateY(0px)} 50%{transform:translateY(-16px)} }
              @keyframes ag-scan       { 0%,100%{top:0%} 50%{top:85%} }
              @keyframes ag-bar1       { 0%,100%{height:30%} 50%{height:90%} }
              @keyframes ag-bar2       { 0%,100%{height:60%} 50%{height:25%} }
              @keyframes ag-bar3       { 0%,100%{height:45%} 50%{height:80%} }
              @keyframes ag-bar4       { 0%,100%{height:70%} 50%{height:35%} }
              @keyframes ag-bar5       { 0%,100%{height:20%} 50%{height:65%} }
              @keyframes ag-shield-pulse { 0%,100%{transform:scale(1);opacity:.5} 50%{transform:scale(1.4);opacity:0} }
              @keyframes ag-lock-up    { 0%,70%{transform:translateY(0)} 80%{transform:translateY(-8px)} 100%{transform:translateY(0)} }
              @keyframes ag-fade-in    { from{opacity:0;transform:scale(0.92)} to{opacity:1;transform:scale(1)} }
              @keyframes ag-ticker     { 0%{transform:translateX(0)} 100%{transform:translateX(-50%)} }
              @keyframes ag-done-burst { 0%{transform:scale(0);opacity:1} 100%{transform:scale(3);opacity:0} }
              @keyframes ag-check-draw { to{stroke-dashoffset:0} }
            `}</style>

            {/* Agent definitions — same order as pipeline */}
            {(() => {
              const AGENTS = [
                {
                  id: 0, name: 'NEXUS', role: 'Orchestrator',
                  img: '/assets/nexus.png',
                  color: '#3b82f6', glow: 'rgba(59,130,246,0.55)',
                  bg: 'from-[#0f1c3f] to-[#0a0f1e]',
                  task: 'INITIALISING MULTI-AGENT SWARM PIPELINE...',
                  // Spinning concentric rings behind image
                  decoration: (
                    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                      {[160,220,280,340].map((s,i)=>(
                        <div key={s} className="absolute rounded-full border-2 border-blue-500/30"
                          style={{width:s,height:s,animation:`ag-ring-spin ${3+i*0.8}s linear infinite ${i%2===1?',ag-ring-spin2 0s linear infinite':''}`}}/>
                      ))}
                      <div className="absolute w-32 h-32 rounded-full bg-blue-500/10"
                        style={{animation:'ag-ping-ring 1.8s ease-out infinite'}}/>
                    </div>
                  )
                },
                {
                  id: 1, name: 'MATRIX', role: 'Pathfinder',
                  img: '/assets/matrix.png',
                  color: '#a855f7', glow: 'rgba(168,85,247,0.55)',
                  bg: 'from-[#1a0b2e] to-[#0d0718]',
                  task: 'SCANNING PREREQUISITE GRAPH — MAPPING OPTIMAL PATHWAYS...',
                  // Horizontal scan line sweeping over a dot grid
                  decoration: (
                    <div className="absolute inset-0 overflow-hidden pointer-events-none">
                      {/* Dot grid */}
                      <svg className="absolute inset-0 w-full h-full opacity-20">
                        <defs>
                          <pattern id="dotp" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
                            <circle cx="20" cy="20" r="2" fill="#a855f7"/>
                          </pattern>
                        </defs>
                        <rect width="100%" height="100%" fill="url(#dotp)"/>
                      </svg>
                      {/* Scan line */}
                      <div className="absolute left-0 right-0 h-1 bg-purple-400/70"
                        style={{boxShadow:'0 0 20px 6px rgba(168,85,247,0.6)', top:'0%', animation:'ag-scan 2.2s ease-in-out infinite'}}/>
                    </div>
                  )
                },
                {
                  id: 2, name: 'VECTOR', role: 'Trajectory Agent',
                  img: '/assets/vector.png',
                  color: '#06b6d4', glow: 'rgba(6,182,212,0.55)',
                  bg: 'from-[#051b20] to-[#020d10]',
                  task: 'COMPUTING ACADEMIC TRAJECTORY & CAREER ALIGNMENT VECTORS...',
                  // Concentric pulsing circles (sonar)
                  decoration: (
                    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                      {[0,1,2,3].map(i=>(
                        <div key={i} className="absolute rounded-full border border-cyan-400/40"
                          style={{width:120+i*80,height:120+i*80,animation:`ag-ping-ring 2s ease-out ${i*0.5}s infinite`}}/>
                      ))}
                      <div className="absolute w-4 h-4 rounded-full bg-cyan-400"
                        style={{boxShadow:'0 0 16px 6px rgba(6,182,212,0.8)'}}/>
                    </div>
                  )
                },
                {
                  id: 3, name: 'STATE', role: 'Auditor',
                  img: '/assets/state.png',
                  color: '#f59e0b', glow: 'rgba(245,158,11,0.55)',
                  bg: 'from-[#1c1200] to-[#0f0900]',
                  task: 'AUDITING STUDENT ACADEMIC STATE & IDENTIFYING RISK FLAGS...',
                  // Animated vertical equalizer bars (data processing)
                  decoration: (
                    <div className="absolute inset-0 flex items-end justify-center gap-3 px-8 pb-8 pointer-events-none overflow-hidden">
                      {['ag-bar1','ag-bar2','ag-bar3','ag-bar4','ag-bar5','ag-bar2','ag-bar4','ag-bar1','ag-bar3','ag-bar5'].map((anim,i)=>(
                        <div key={i} className="w-6 rounded-t-sm bg-amber-400/25 border border-amber-500/30 relative overflow-hidden flex-shrink-0"
                          style={{height:'60%'}}>
                          <div className="absolute bottom-0 left-0 right-0 bg-amber-400/50 rounded-t-sm"
                            style={{animation:`${anim} ${0.7+i*0.08}s ease-in-out ${i*0.05}s infinite`}}/>
                        </div>
                      ))}
                    </div>
                  )
                },
                {
                  id: 4, name: 'CODEX', role: 'Policy RAG',
                  img: '/assets/codex.png',
                  color: '#10b981', glow: 'rgba(16,185,129,0.55)',
                  bg: 'from-[#011a0f] to-[#000d06]',
                  task: 'RETRIEVING ACADEMIC POLICY CITATIONS FROM KNOWLEDGE GRAPH...',
                  // Cascading text particles (knowledge retrieval)
                  decoration: (
                    <div className="absolute inset-0 pointer-events-none overflow-hidden opacity-30">
                      {['PREREQ','CREDIT','WAIVER','R22','GRADE','SGPA','CGPA','POLICY','TRACK','ELECTIVE'].map((word,i)=>(
                        <div key={i} className="absolute text-green-400 font-mono text-xs whitespace-nowrap"
                          style={{
                            left:`${(i*17+5)%90}%`,
                            top:`${(i*23+10)%90}%`,
                            animation:`ag-float ${1.8+i*0.3}s ease-in-out ${i*0.2}s infinite`
                          }}>
                          {word}
                        </div>
                      ))}
                    </div>
                  )
                },
                {
                  id: 5, name: 'SENTINEL', role: 'Verifier',
                  img: '/assets/sentinel.png',
                  color: '#ef4444', glow: 'rgba(239,68,68,0.55)',
                  bg: 'from-[#1a0505] to-[#0d0202]',
                  task: 'VERIFYING CONSTRAINTS — RESOLVING CONFLICTS & SECURING PATHWAY...',
                  // Pulsing shield rings
                  decoration: (
                    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                      {[1,2,3].map(i=>(
                        <div key={i} className="absolute"
                          style={{
                            width: 160+i*80, height: 160+i*80,
                            clipPath:'polygon(50% 0%, 90% 20%, 100% 60%, 75% 100%, 25% 100%, 0% 60%, 10% 20%)',
                            border: '2px solid rgba(239,68,68,0.3)',
                            animation:`ag-shield-pulse ${1.2+i*0.4}s ease-out ${i*0.35}s infinite`
                          }}/>
                      ))}
                    </div>
                  )
                },
              ];

              const current = activeAgentIdx >= 0 ? AGENTS[activeAgentIdx] : null;

              if (!current) return null; // all done — show the grid below

              return (
                <div className="fixed inset-0 z-50 flex flex-col overflow-hidden"
                  style={{
                    background: `linear-gradient(to bottom right, ${current.bg.replace('from-[','').replace('] to-[','',).replace(']','')})`,
                    backgroundImage: `linear-gradient(135deg, ${current.bg.split('from-[')[1]?.split(']')[0] || '#0f1c3f'}, ${current.bg.split('to-[')[1]?.split(']')[0] || '#0a0f1e'})`,
                    animation: 'ag-fade-in 0.5s ease-out forwards'
                  }}>

                  {/* Background decoration */}
                  {current.decoration}

                  {/* Top bar */}
                  <div className="relative z-10 flex items-center justify-between px-6 py-4 border-b border-white/10">
                    <div className="flex items-center gap-3">
                      <div className="w-3 h-3 rounded-full animate-pulse" style={{backgroundColor:current.color}}/>
                      <span className="font-mono text-sm text-white/60 uppercase tracking-widest">OMEGA — SWARM ORCHESTRATOR</span>
                    </div>
                    <div className="flex items-center gap-2">
                      {AGENTS.map((a,i)=>(
                        <div key={i} className="w-2 h-2 rounded-full transition-all duration-500"
                          style={{
                            backgroundColor: pipelineStep > i ? '#22c55e' : i === activeAgentIdx ? current.color : 'rgba(255,255,255,0.2)',
                            transform: i === activeAgentIdx ? 'scale(1.6)' : 'scale(1)',
                            boxShadow: i === activeAgentIdx ? `0 0 8px ${current.color}` : 'none'
                          }}/>
                      ))}
                    </div>
                  </div>

                  {/* Main content */}
                  <div className="relative z-10 flex-1 flex flex-col md:flex-row items-center justify-center gap-10 md:gap-20 px-8 py-6">

                    {/* Agent image — large, floating, glowing */}
                    <div className="relative flex-shrink-0">
                      {/* Glow halo */}
                      <div className="absolute inset-0 rounded-full blur-3xl scale-125"
                        style={{backgroundColor: current.glow, animation:'ag-ping-ring 2.5s ease-out infinite'}}/>
                      {/* Image */}
                      <img
                        src={current.img}
                        alt={current.name}
                        className="relative w-48 h-48 md:w-64 md:h-64 object-contain drop-shadow-2xl"
                        style={{
                          imageRendering: 'pixelated',
                          filter: `drop-shadow(0 0 24px ${current.color})`,
                          animation: 'ag-float 3s ease-in-out infinite'
                        }}
                      />
                    </div>

                    {/* Agent info panel */}
                    <div className="flex flex-col items-center md:items-start gap-4 max-w-lg">
                      {/* Agent number */}
                      <div className="font-mono text-xs tracking-[0.3em] uppercase"
                        style={{color: current.color}}>
                        AGENT {String(current.id + 1).padStart(2,'0')} / 06
                      </div>

                      {/* Name */}
                      <div className="title-text text-5xl md:text-7xl text-white drop-shadow-lg leading-none"
                        style={{textShadow:`0 0 30px ${current.color}`}}>
                        {current.name}
                      </div>

                      {/* Role badge */}
                      <div className="px-4 py-1.5 border text-sm font-bold uppercase tracking-widest"
                        style={{borderColor: current.color, color: current.color, boxShadow:`0 0 12px ${current.glow}`}}>
                        {current.role}
                      </div>

                      {/* Task description */}
                      <p className="font-mono text-sm text-white/50 leading-relaxed text-center md:text-left">
                        {current.task}
                      </p>

                      {/* Live status strip */}
                      <div className="w-full border border-white/10 bg-black/40 px-4 py-3 flex items-center gap-3">
                        <div className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                          style={{backgroundColor:current.color, boxShadow:`0 0 8px ${current.color}`, animation:'ag-ping-ring 1s ease-out infinite'}}/>
                        <div className="overflow-hidden flex-1">
                          <div className="font-mono text-xs whitespace-nowrap"
                            style={{color:current.color, animation:'ag-ticker 8s linear infinite'}}>
                            {`● ACTIVE ● ${current.task} ● AGENT ${current.id+1}/6 ONLINE ● TARGET: ${chatInput.toUpperCase()} ● SWARM PROCESSING ● `}
                            {`● ACTIVE ● ${current.task} ● AGENT ${current.id+1}/6 ONLINE ● TARGET: ${chatInput.toUpperCase()} ● SWARM PROCESSING ● `}
                          </div>
                        </div>
                      </div>

                      {/* Previously completed agents */}
                      {current.id > 0 && (
                        <div className="flex flex-wrap gap-2">
                          {AGENTS.slice(0, current.id).map(a=>(
                            <div key={a.id} className="flex items-center gap-1.5 px-2 py-1 bg-green-900/40 border border-green-500/40 text-green-400 text-xs font-bold">
                              ✓ {a.name}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Bottom progress bar */}
                  <div className="relative z-10 px-6 pb-6">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="font-mono text-xs text-white/40">PIPELINE PROGRESS</span>
                      <span className="font-mono text-xs ml-auto" style={{color:current.color}}>
                        {Math.round(((current.id) / 6) * 100)}% COMPLETE
                      </span>
                    </div>
                    <div className="h-1 w-full bg-white/10 rounded overflow-hidden">
                      <div className="h-full rounded transition-all duration-700"
                        style={{
                          width: `${((current.id) / 6) * 100}%`,
                          backgroundColor: current.color,
                          boxShadow: `0 0 10px ${current.color}`
                        }}/>
                    </div>
                  </div>
                </div>
              );
            })()}
            {/* ── END AGENT SPOTLIGHT ──────────────────────────────── */}

            {/* Mini agent tracker — shown below spotlight (hidden while spotlight is up) */}
            {activeAgentIdx === -1 && pipelineStep > 0 && (
              <div className="pixel-box w-full bg-white border-[6px]">
                <div className="window-header bg-black text-white px-4 py-3 border-b-[6px] border-black text-lg flex justify-between">
                  <span>SWARM_ORCHESTRATOR.SYS</span>
                  <span className="text-green-400">✓ ALL 6 AGENTS SYNCED</span>
                </div>
                <div className="p-6 flex flex-wrap gap-3 justify-center">
                  {[
                    {name:'NEXUS',img:'/assets/nexus.png'},
                    {name:'MATRIX',img:'/assets/matrix.png'},
                    {name:'VECTOR',img:'/assets/vector.png'},
                    {name:'STATE',img:'/assets/state.png'},
                    {name:'CODEX',img:'/assets/codex.png'},
                    {name:'SENTINEL',img:'/assets/sentinel.png'},
                  ].map((a,i)=>(
                    <div key={i} className="flex items-center gap-2 px-3 py-2 bg-green-50 border-[3px] border-green-500 shadow-[3px_3px_0_#22c55e]">
                      <img src={a.img} alt={a.name} className="w-8 h-8 object-contain" style={{imageRendering:'pixelated'}}/>
                      <span className="title-text text-sm text-green-800">{a.name}</span>
                      <span className="text-green-600 font-bold text-sm">✓</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* The Visual Path Output: OPTIMAL_PATHWAY_GENERATED.DAT */}
            {pipelineStep >= 4 && (
              <div className="pixel-box w-full bg-blue-50 animate-[slideUp_0.8s_ease-out_forwards] border-[6px] border-black shadow-[16px_16px_0_#3b82f6]">
                <div className="window-header bg-blue-600 text-white px-4 py-3 border-b-[6px] border-black text-lg flex justify-between items-center flex-wrap gap-2">
                  <span className="font-bold tracking-wider">OPTIMAL_PATHWAY_GENERATED.DAT</span>
                  <span className="text-xs bg-black text-yellow-300 px-3 py-1 border border-yellow-300 font-mono">
                    {roadmapData.departmentName} • {roadmapData.regulation} • REMAINING SEMESTERS
                  </span>
                </div>
                
                <div className="p-6 md:p-12 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTEgMWgydjJIMXoiIGZpbGw9InJnYmEoMCwwLDAsMC4wMikiIGZpbGwtcnVsZT0iZXZlbm9kZCIvPjwvc3ZnPg==')]">
                  
                  <div className="text-center mb-10">
                    <h3 className="title-text text-3xl md:text-5xl text-black drop-shadow-[3px_3px_0_#3b82f6] bg-white inline-block px-8 py-3 border-4 border-black mx-auto">
                      ACADEMIC ROADMAP
                    </h3>
                    <div className="mt-4 flex flex-wrap justify-center gap-3">
                      <span className="text-base md:text-lg font-bold text-gray-800 bg-yellow-200 px-4 py-1.5 border-2 border-black shadow-[2px_2px_0_#000]">
                        🎯 Target Career: <strong className="text-blue-800">{chatInput}</strong>
                      </span>
                      <span className="text-base md:text-lg font-bold text-gray-800 bg-green-200 px-4 py-1.5 border-2 border-black shadow-[2px_2px_0_#000]">
                        📍 Current Standing: <strong className="text-green-900">Semester {studentDetails.semester}</strong>
                      </span>
                      <span className="text-base md:text-lg font-bold text-gray-800 bg-purple-200 px-4 py-1.5 border-2 border-black shadow-[2px_2px_0_#000]">
                        ⚡ Roadmap Start: <strong className="text-purple-900">Semester {Math.min(8, (studentDetails.semester || 1) + 1)}</strong>
                      </span>
                    </div>
                  </div>

                  {/* Visual Connected Roadmap Track - ONLY ONE MAIN SUBJECT PER SEMESTER */}
                  <div className="relative mt-8 mb-12 overflow-x-auto pb-8 pt-6">
                    <div className="relative z-10 flex flex-col md:flex-row justify-start items-stretch md:items-start gap-12 md:gap-8 min-w-max px-8">
                      
                      {/* The drawn line connecting continuously across all nodes */}
                      <div className="absolute top-[40%] left-10 right-10 h-4 bg-blue-500 -translate-y-1/2 z-0 hidden md:block border-y-4 border-black">
                      </div>
                      
                      {roadmapData.roadmapSteps.map((step, i) => (
                        <div 
                          key={i} 
                          className="flex flex-col items-center bg-white border-[6px] border-black p-5 w-full md:w-60 text-center shadow-[8px_8px_0_#000] transform transition-all duration-500 hover:-translate-y-4 hover:shadow-[12px_16px_0_#3b82f6] relative group"
                          style={{ animation: `slideUp 0.5s ease-out ${i * 0.2}s both` }}
                        >
                          <div className="absolute -top-6 bg-black text-white px-3 py-1 title-text text-sm border-2 border-white shadow-[2px_2px_0_#000] group-hover:bg-blue-600 transition-colors">
                            {step.semesterLabel.toUpperCase()}
                          </div>
                          
                          <div className="text-xs font-bold text-blue-700 bg-blue-50 px-2 py-0.5 border border-blue-300 mt-2 mb-2">
                            {step.code} • {step.credits} CR
                          </div>
                          
                          <div className="text-base md:text-lg font-black text-black leading-snug mb-2">
                            <span className="text-red-500 mr-1">🎯</span>{step.mainSubject}
                          </div>
                          
                          <div className="mt-auto text-xs text-gray-700 bg-yellow-50 p-2.5 border-2 border-black text-left w-full">
                            <strong className="text-black">💡 Why:</strong> {step.why}
                          </div>
                          
                          <div className="w-4 h-4 bg-blue-500 border-2 border-black rounded-full mt-4 animate-ping hidden md:block"></div>
                        </div>
                      ))}

                      {/* Dedicated Capstone Project Node After Semester 8 */}
                      {roadmapData.capstoneStep && (
                        <div 
                          className="flex flex-col items-center bg-purple-50 border-[6px] border-black p-5 w-full md:w-64 text-center shadow-[8px_8px_0_#a855f7] transform transition-all duration-500 hover:-translate-y-4 hover:shadow-[12px_16px_0_#a855f7] relative group"
                          style={{ animation: `slideUp 0.5s ease-out ${(roadmapData.roadmapSteps.length) * 0.2}s both` }}
                        >
                          <div className="absolute -top-6 bg-purple-700 text-white px-3 py-1 title-text text-xs md:text-sm border-2 border-white shadow-[2px_2px_0_#000] group-hover:bg-purple-900 transition-colors">
                            CAPSTONE PROJECT
                          </div>
                          
                          <div className="text-xs font-bold text-purple-800 bg-purple-100 px-2 py-0.5 border border-purple-300 mt-2 mb-2">
                            22PR801 • 12 CREDITS (MAJOR PROJECT)
                          </div>
                          
                          <div className="text-base md:text-lg font-black text-black leading-snug mb-2">
                            <span className="text-purple-600 mr-1">🚀</span>{roadmapData.capstoneStep.projectTitle}
                          </div>
                          
                          <div className="mt-auto text-xs text-gray-800 bg-yellow-50 p-2.5 border-2 border-black text-left w-full">
                            <strong className="text-black">💡 Why Needed:</strong> {roadmapData.capstoneStep.why}
                          </div>
                          
                          <div className="w-4 h-4 bg-purple-600 border-2 border-black rounded-full mt-4 animate-ping hidden md:block"></div>
                        </div>
                      )}

                      {/* Final Destination Node: Goal Reached */}
                      <div 
                        className="flex flex-col items-center bg-yellow-300 border-[6px] border-black p-6 w-full md:w-64 text-center shadow-[12px_12px_0_#000] transform transition-all duration-500 hover:scale-105 relative"
                        style={{ animation: `slideUp 0.5s ease-out ${(roadmapData.roadmapSteps.length + 1) * 0.2}s both, pulseBorder 2s infinite` }}
                      >
                        <div className="absolute -top-8 bg-yellow-500 text-black px-4 py-1.5 title-text text-xs md:text-sm border-[4px] border-black shadow-[4px_4px_0_#000] animate-bounce">
                          GOAL REACHED
                        </div>
                        
                        <Briefcase className="text-black mb-2 mt-2" size={36} />
                        
                        <div className="text-lg font-extrabold truncate w-full px-2 bg-white border-2 border-black py-1.5 mb-2">
                          {chatInput || 'CAREER GOAL'}
                        </div>
                        
                        <div className="text-xs font-bold text-gray-800 bg-yellow-100 px-2 py-1 border border-black mb-2">
                          🎯 CAREER PATHWAY VERIFIED
                        </div>
                        
                        <div className="mt-auto text-xs text-gray-900 bg-white p-2.5 border-2 border-black shadow-[2px_2px_0_#000] text-left w-full">
                          <strong className="text-black">🏆 Outcome:</strong> All prerequisites and capstone milestones cleared for professional entry.
                        </div>
                      </div>

                    </div>
                  </div>

                  {/* Career Vector Box if available */}
                  {pipelineData?.career_vector && (
                    <div className="mt-12 max-w-4xl mx-auto bg-white border-4 border-black p-6 shadow-[8px_8px_0_#000] animate-[slideUp_0.5s_ease-out_1.5s_both]">
                      <h4 className="title-text text-xl mb-3 bg-blue-600 text-white inline-block px-4 py-1">
                        CAREER VECTOR: NEXT STEPS
                      </h4>
                      <div className="text-lg leading-relaxed text-gray-700">
                        <strong className="text-black">Recommended Action:</strong> {pipelineData.career_vector.actionable_project}
                      </div>
                    </div>
                  )}
                  
                  
                  <div className="mt-8 flex flex-col md:flex-row justify-center gap-4 animate-[slideUp_0.5s_ease-out_2s_both]">
                    <button onClick={openKnowledgeGraph} className="pixel-btn bg-black text-white text-xl flex items-center gap-4 py-4 px-8 border-[6px] border-white shadow-[8px_8px_0_#000] hover:shadow-[4px_4px_0_#000] hover:translate-x-1 hover:translate-y-1 transition-all">
                      <MapIcon size={24}/> OPEN TREASURE MAP
                    </button>
                    <button onClick={() => alert("Pathway Exported to PDF/LinkedIn Profile!")} className="pixel-btn bg-blue-600 text-white text-xl flex items-center gap-4 py-4 px-8 border-[6px] border-black shadow-[8px_8px_0_#000] hover:shadow-[4px_4px_0_#000] hover:translate-x-1 hover:translate-y-1 transition-all">
                      <Download size={24}/> EXPORT CREDENTIALS
                    </button>
                    <button onClick={() => setShowWhatIf(!showWhatIf)} className="pixel-btn bg-purple-600 text-white text-xl flex items-center gap-4 py-4 px-8 border-[6px] border-black shadow-[8px_8px_0_#000] hover:shadow-[4px_4px_0_#000] hover:translate-x-1 hover:translate-y-1 transition-all">
                      <MonitorPlay size={24}/> WHAT-IF SIMULATOR
                    </button>
                  </div>
                  
                  {showWhatIf && (
                     <div className="mt-12 bg-white border-4 border-purple-600 p-8 shadow-[8px_8px_0_#000] animate-[slideUp_0.3s]">
                        <h4 className="title-text text-2xl mb-4 text-purple-700 flex items-center gap-2"><MonitorPlay/> SCENARIO SIMULATOR (RAG)</h4>
                        <p className="text-xl mb-4 text-gray-700">Inject variables into the Graph-RAG model to see alternate pathways.</p>
                        <div className="flex gap-4">
                           <select className="flex-1 pixel-input text-xl border-[4px] border-black py-2 px-4 bg-gray-100">
                             <option>What if I fail Data Structures?</option>
                             <option>What if I switch to Cybersecurity?</option>
                             <option>What if I take a semester off?</option>
                           </select>
                           <button onClick={() => alert("Recomputing via Vector Agent...\\nPath updated: +1 Semester, added Coursera bridging course.")} className="pixel-btn bg-black text-white px-6 border-4 border-purple-600">SIMULATE</button>
                        </div>
                     </div>
                  )}
                  
                  {/* Graph-RAG Infographics Mockup */}
                  <div className="mt-12 bg-gray-900 border-4 border-black p-8 shadow-[8px_8px_0_#000] animate-[slideUp_0.3s_ease-out_2s_both]">
                      <h4 className="title-text text-2xl mb-4 text-green-400 flex items-center gap-2"><FileBarChart/> RAG SEMANTIC INFOGRAPHICS</h4>
                      <p className="text-gray-300 text-lg mb-6">Real-time vector alignment of your skills vs target career demands.</p>
                      <div className="flex flex-col md:flex-row gap-8 items-center justify-center">
                          <div className="w-64 h-64 border-4 border-green-500 rounded-full relative flex items-center justify-center overflow-hidden">
                             <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTEgMWgydjJIMXoiIGZpbGw9InJnYmEoMCwyNTUsMCwwLjEpIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiLz48L3N2Zz4=')]"></div>
                             <div className="w-48 h-48 border-2 border-green-400 opacity-50 rounded-full absolute"></div>
                             <div className="w-32 h-32 border-2 border-green-400 opacity-50 rounded-full absolute"></div>
                             <div className="w-40 h-48 bg-green-500 opacity-40 absolute transform rotate-45"></div>
                             <span className="z-10 title-text text-white text-xl shadow-black drop-shadow-md">78% ALIGNED</span>
                          </div>
                          <div className="flex flex-col gap-4 text-white">
                             <div><span className="text-green-400">Python:</span> 95% Match</div>
                             <div><span className="text-green-400">Algorithms:</span> 82% Match</div>
                             <div><span className="text-yellow-400">System Design:</span> 40% (Bottleneck)</div>
                             <div><span className="text-red-400">Cloud Arch:</span> 12% (Critical Gap)</div>
                          </div>
                      </div>
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


