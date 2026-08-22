"""
Vector (Agent 03) - Future Scope and Career Trajectory Engine
============================================================
Translates curriculum schedules, student career goals, and academic performance
into an actionable 3-step Strategic Momentum Plan (Project, Internship, Certification).
"""

from typing import Any, Dict, List, Optional
try:
    from .schemas import MomentumPlan
except ImportError:
    from schemas import MomentumPlan

# Comprehensive Career Velocity Blueprints
CAREER_BLUEPRINTS: Dict[str, Dict[str, Any]] = {
    "AI Researcher": {
        "project": "Implement and benchmark a multi-head Transformer architecture from scratch in PyTorch, evaluating attention degradation on sparse biomedical datasets.",
        "internship": "Target 'AI Research Intern' and 'Applied GenAI Scientist Intern' positions at research labs (DeepMind, FAIR, Microsoft Research) focusing on LLM alignment.",
        "milestone": "Publish a preprint on arXiv or submit a workshop paper to NeurIPS/ICLR/CVPR on efficient parameter-tuning.",
        "certifications": ["TensorFlow Developer Certificate", "DeepLearning.AI Generative AI Specialization", "NVIDIA CUDA Acceleration & Deep Learning"]
    },
    "Data Scientist": {
        "project": "Construct an end-to-end predictive churn and customer lifetime value pipeline utilizing XGBoost, MLflow experiment tracking, and FastAPI serving.",
        "internship": "Search LinkedIn and Handshake for 'Data Science Intern' and 'Quantitative Analytics Intern' roles in fintech or healthcare tech.",
        "milestone": "Achieve Kaggle Competitions Expert rank by competing in top tabular and time-series benchmark challenges.",
        "certifications": ["AWS Certified Machine Learning - Specialty", "Google Professional Data Engineer", "Databricks Certified Data Scientist Associate"]
    },
    "Cloud Architect": {
        "project": "Architect an enterprise multi-region disaster recovery infrastructure on AWS/GCP using Terraform, Kubernetes (EKS/GKE), and Istio Service Mesh.",
        "internship": "Apply for 'Cloud Engineering Intern' or 'Infrastructure Architecture Intern' positions across hyperscalers and tier-1 SaaS enterprises.",
        "milestone": "Deploy a zero-downtime blue-green CI/CD deployment pipeline with automated chaos engineering tests using Chaos Mesh.",
        "certifications": ["AWS Certified Solutions Architect - Associate", "Google Cloud Professional Cloud Architect", "HashiCorp Certified Terraform Associate"]
    },
    "Cybersecurity Analyst": {
        "project": "Build an automated Security Information and Event Management (SIEM) log parser and threat detection heuristic tool using Python and ElasticSearch.",
        "internship": "Target 'SOC Analyst Intern' and 'Information Security Associate Intern' roles at managed detection and response firms.",
        "milestone": "Complete 50+ medium/hard machines on HackTheBox and rank in the top 10% on TryHackMe CTF challenges.",
        "certifications": ["CompTIA Security+", "Certified Information Systems Security Professional (CISSP - Associate)", "Offensive Security Certified Professional (OSCP)"]
    },
    "Machine Learning Engineer": {
        "project": "Build an end-to-end streaming MLOps pipeline that continuously ingests Kafka event streams, retrains LightGBM models, and deploys ONNX runtimes.",
        "internship": "Search for 'MLOps Intern' and 'Machine Learning Engineer Intern' opportunities at high-growth AI startups.",
        "milestone": "Containerize and deploy 3 production microservices serving LLM embeddings with sub-20ms latency using Triton Inference Server.",
        "certifications": ["AWS Certified Machine Learning - Specialty", "Google Professional Machine Learning Engineer", "Kubernetes CKA (Certified Kubernetes Administrator)"]
    },
    "DevOps Engineer": {
        "project": "Construct a GitOps infrastructure pipeline utilizing ArgoCD, GitHub Actions, Prometheus, and Grafana for full Kubernetes cluster observability.",
        "internship": "Target 'Site Reliability Engineering (SRE) Intern' and 'DevOps Cloud Intern' positions at cloud-native platforms.",
        "milestone": "Implement automated canary deployments with automated rollback thresholds triggered by Prometheus SLO metric breaches.",
        "certifications": ["CKA - Certified Kubernetes Administrator", "AWS Certified DevOps Engineer - Professional", "Docker Certified Associate (DCA)"]
    },
    "Full Stack Developer": {
        "project": "Develop a real-time collaborative workspace canvas utilizing React, WebSockets, Node.js, PostgreSQL with Prisma ORM, and Redis Pub/Sub.",
        "internship": "Apply for 'Full Stack Software Engineer Intern' and 'Frontend/Backend Engineer Intern' postings on Wellfound and LinkedIn.",
        "milestone": "Deploy a production web application with 100% Lighthouse performance score and full test coverage using Vitest and Cypress.",
        "certifications": ["Meta Front-End Developer Professional Certificate", "MongoDB Certified Developer Associate", "AWS Certified Developer - Associate"]
    },
    "Software Engineer": {
        "project": "Design and build a high-throughput distributed key-value store in Go or C++ implementing the Raft consensus algorithm and write-ahead logging.",
        "internship": "Target 'Software Engineering Intern' roles at top product organizations (Google, Amazon, Meta, Bloomberg).",
        "milestone": "Solve 300+ LeetCode problems covering Dynamic Programming, Graph Theory, and Concurrency, maintaining a 2000+ contest rating.",
        "certifications": ["Oracle Certified Professional: Java SE Developer", "AWS Certified Solutions Architect - Associate", "Linux Foundation Certified System Administrator (LFCS)"]
    },
    "Systems Software Engineer": {
        "project": "Develop a custom multi-threaded memory allocator and virtual memory manager in C with slab allocation and lock-free thread synchronization.",
        "internship": "Search for 'Systems Engineer Intern' and 'Kernel/Firmware Intern' positions at semiconductor firms (NVIDIA, Intel, Qualcomm).",
        "milestone": "Contribute a performance optimization or bugfix patch to an open-source Linux kernel module or LLVM compiler backend.",
        "certifications": ["Linux Foundation Certified Engineer (LFCE)", "Embedded Systems Professional Certificate", "Arm System-on-Chip Architecture Certification"]
    },
    "Robotics & Embedded Systems Specialist": {
        "project": "Build an autonomous obstacle avoidance and SLAM navigation robot using ROS 2 (Robot Operating System), LiDAR sensor fusion, and Raspberry Pi/Jetson.",
        "internship": "Target 'Robotics Software Intern' and 'Embedded Firmware Intern' roles at autonomy and drone development companies.",
        "milestone": "Implement real-time PID motor velocity control and Kalman filter state estimation with sub-5ms control loop response.",
        "certifications": ["ROS 2 Certified Developer", "Embedded Linux System Development Certificate", "NVIDIA Jetson AI Specialist"]
    }
}


class Agent3Vector:
    """
    Agent 3: Vector (Future Scope & Strategic Career Trajectory Engine).
    Ingests student career goal, academic standing, and pathway schedule to formulate
    a high-impact 3-step Strategic Momentum Plan devoid of conversational fluff.
    """

    def __init__(self):
        pass

    def generate_momentum_plan(
        self,
        student_goal: str,
        matrix_schedule: Optional[Any] = None,
        cgpa: Optional[float] = None
    ) -> MomentumPlan:
        """
        Takes the career goal and matrix schedule and returns the structured MomentumPlan.
        """
        blueprint = CAREER_BLUEPRINTS.get(
            student_goal,
            CAREER_BLUEPRINTS["Software Engineer"]
        )

        project = blueprint["project"]
        internship = blueprint["internship"]
        milestone = blueprint["milestone"]
        certs = blueprint["certifications"]

        raw_md = (
            f"**Strategic Momentum Plan ({student_goal}):**\n"
            f"*   **Actionable Project:** {project}\n"
            f"*   **Internship/Career Target:** {internship}\n"
            f"*   **Next-Level Milestone:** {milestone}\n"
            f"*   **Recommended Certifications:** {', '.join(certs)}"
        )

        return MomentumPlan(
            student_goal=student_goal,
            actionable_project=project,
            internship_target=internship,
            next_level_milestone=milestone,
            target_certifications=certs,
            raw_markdown=raw_md
        )


# Functional wrapper
def run_vector(student_goal: str, matrix_schedule: Optional[Any] = None) -> MomentumPlan:
    vector = Agent3Vector()
    return vector.generate_momentum_plan(student_goal, matrix_schedule)
