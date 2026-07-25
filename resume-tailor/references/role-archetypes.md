# Role Archetypes

Load this file during Phase 1, after the JD recap and before assigning weights. The goal is to classify the role so the resume is tailored to the right *kind* of story, not just the right keywords.

## 1. Why This Matters

Many AI leadership JDs share the same vocabulary: LLMs, MLOps, platforms, governance, adoption, experimentation. But they are not hiring for the same thing.

If the skill fails to classify the role type, the output tends to flatten into a generic "AI leader" resume that sounds plausible but misses what the hiring team actually cares about.

## 2. Required Output in Phase 1

After the JD recap and before Phase 2, add these lines to the Phase 1 checkpoint:

- `Archetype selected: [one primary archetype]`
- `Resume story to foreground: [one-sentence direction]`
- `What to downplay: [1-3 items]`

Pick one primary archetype even if the JD spans multiple modes. Secondary traits can influence bullet selection, but the resume still needs one dominant story.

## 3. Archetypes

### A. Platform / Engineering Executive

**What they are really hiring for**

- technical direction across multiple teams or product lines
- platform architecture and production reliability
- org leadership, standards, and execution predictability
- enterprise-scale delivery, security, and operational maturity

**Foreground**

- architecture decisions
- MLOps / ModelOps / CI/CD / platform operating model
- multi-team execution
- reliability, compliance, observability, scalability

**Downplay**

- isolated prototypes
- content/education framing
- overly PM-ish roadmap language without engineering authority

**Seed examples from this batch**

- Cornerstone `Senior Director, AI Engineering`
- Maximus `Senior Director, AI Systems Engineering`
- Granicus `Senior Director - AI Engineering`

### B. AI Ops / CoE / Governance Leader

**What they are really hiring for**

- enterprise AI operating model
- governance frameworks, risk, vendor strategy, and metrics
- portfolio-level execution and accountability
- adoption structure, not just model building

**Foreground**

- governance and responsible AI
- vendor evaluation / build-vs-buy / contracting logic
- KPI definition, ROI visibility, steering mechanisms
- cross-functional operating cadence

**Downplay**

- purely hands-on model-building identity
- tool lists without governance meaning
- generic innovation language

**Seed examples from this batch**

- CentralSquare `Director of AI Engineering Operations`
- RIA `Director of AI Center of Excellence`
- parts of Maximus

### C. Builder-Leader / Regulated Enterprise

**What they are really hiring for**

- someone who can still build and architect
- direct translation of business problems into deployed systems
- regulated-environment pragmatism
- hands-on implementation with leadership credibility

**Foreground**

- production deployments
- HIPAA / privacy / explainability / security
- enterprise integration
- workflow automation and measurable operational outcomes

**Downplay**

- abstract strategy without evidence of implementation
- consulting-style thought leadership
- education/adoption language unless clearly tied to deployment

**Seed examples from this batch**

- TechHuman `Director of AI`

### D. Consulting / Practice / Client-Facing AI Leader

**What they are really hiring for**

- trusted advisor plus builder of repeatable offerings
- executive presence with customers
- workshops, GTM, solution framing, and delivery frameworks
- translating ambiguity into client value

**Foreground**

- strategic customer conversations
- repeatable delivery models and playbooks
- internal enablement plus external offerings
- practice building, workshops, thought leadership

**Downplay**

- purely internal platform language
- deep implementation detail with no client or commercial context
- org-internal governance as the main story unless the JD centers it

**Seed examples from this batch**

- GuidePoint `Director, AI & Agentic Enablement`
- SoftServe `Senior Consultant (Agentic AI)`
- TELUS `Forward Deployed Researcher, Director`

### E. AI Product / Adoption / Workforce Enablement

**What they are really hiring for**

- product ownership for AI-enabled user behavior
- adoption, engagement, learning design, and enterprise workflow fluency
- AI power-user credibility plus PM execution

**Foreground**

- roadmap and prioritization
- user behavior, experimentation, engagement, retention
- point of view on AI skills and adoption
- product strategy grounded in hands-on AI usage

**Downplay**

- platform architecture-first framing
- deep governance language unless the JD asks for it
- executive engineering identity

**Seed examples from this batch**

- Section `Product Manager, AI Coach`

### F. Domain ML Leader

**What they are really hiring for**

- applied ML judgment in one problem domain
- hands-on model lifecycle leadership
- business intuition plus technical depth
- smaller-team leadership with real production responsibility

**Foreground**

- model lifecycle ownership
- data sourcing, experimentation, monitoring
- domain-specific judgment
- production code plus team guidance

**Downplay**

- enterprise transformation rhetoric
- vague AI strategy language
- broad GenAI/platform story if the role is actually domain-ML-heavy

**Seed examples from this batch**

- kadence `Head of Machine Learning`

### G. Forward Deployed / Applied AI Engineer

**What they are really hiring for**

- an engineer who owns a build end to end inside a *customer's* environment
- discovery → integration → production system → eval/monitoring, on the hook when it breaks
- direct customer/stakeholder work done *as a builder*, not as a PM or advisor
- broad deploy-side range: any cloud, containers, CI/CD, API/data integration
- comfort making technical decisions under ambiguity before requirements are clear

**Foreground**

- production ownership carried from ambiguous problem to running system, with outcomes
- the applied LLM stack: Python, RAG, agents, prompt engineering
- deploy fluency matched to the JD's stack (AWS/GCP/Azure + Docker/K8s + CI/CD)
- feeding field lessons back into the product (bridges FDE + product sense)

**Downplay**

- curriculum/education framing
- thought-leadership / workshops as the headline (that is archetype D)
- governance-first or strategy narration not tied to a shipped system

**Note on seniority + leadership.** FDE is ~91% individual-contributor (only 11%
management). For a leadership search, target either the senior IC slice (Senior / Staff /
Principal / Lead / Founding — leadership-adjacent authority without a "Manager" title) or
the explicit-management framings (Head of Forward Deployed Engineering, FDE Manager,
Director/Forward Deployed Researcher). Either way the story is builder-who-owns-customer-
outcomes. Full empirical profile, adjacent titles, and title-field lead:
`references/fde-role-profile.md` — load it when this archetype is selected.

**Seed examples from this batch**

- TELUS `Forward Deployed Researcher, Director` (also touches archetype D, but the
  production-ownership + customer-deployment center of gravity is FDE)

## 4. Selection Heuristics

Use the JD's center of gravity, not just the most impressive phrases.

- If the JD repeats architecture, platform, MLOps, reliability, and engineering org leadership: choose `Platform / Engineering Executive`.
- If the JD repeats governance, CoE, vendor strategy, operational maturity, and KPI visibility: choose `AI Ops / CoE / Governance Leader`.
- If the JD asks for design, deploy, integrate, and govern systems directly in a regulated domain: choose `Builder-Leader / Regulated Enterprise`.
- If the JD emphasizes customers, offerings, workshops, regional practice development, or client trust: choose `Consulting / Practice / Client-Facing AI Leader`.
- If the JD emphasizes product ownership, roadmap, engagement, coaching, adoption, or power-user workflows: choose `AI Product / Adoption / Workforce Enablement`.
- If the JD emphasizes model development in one domain, hands-on data science leadership, and real-time production models: choose `Domain ML Leader`.
- If the title contains *forward deployed / applied AI engineer / solutions engineer / deployment engineer*, or the JD centers deploying production AI **inside a customer's environment** with the engineer owning discovery, integration, and outcomes: choose `Forward Deployed / Applied AI Engineer`. Distinguish from D — D leads with advisory/workshops/repeatable offerings; G leads with production ownership and hands-on customer deployment.

## 5. Resume Story Templates

Use these to fill the `Resume story to foreground` line in Phase 1.

- `Platform / Engineering Executive`: "Frame the candidate as the leader who sets technical direction, scales AI platforms, and makes production systems reliable across teams."
- `AI Ops / CoE / Governance Leader`: "Frame the candidate as the operator who turns AI ambition into governance, operating cadence, vendor decisions, and measurable enterprise adoption."
- `Builder-Leader / Regulated Enterprise`: "Frame the candidate as the technical leader who still architects and deploys real systems under HIPAA/security/privacy constraints."
- `Consulting / Practice / Client-Facing AI Leader`: "Frame the candidate as the advisor-builder who turns ambiguous client needs into repeatable AI offerings and measurable outcomes."
- `AI Product / Adoption / Workforce Enablement`: "Frame the candidate as the product owner of AI behavior change, adoption, and workflow value, not just feature delivery."
- `Domain ML Leader`: "Frame the candidate as the applied ML leader who combines domain intuition, model judgment, and hands-on delivery in production."
- `Forward Deployed / Applied AI Engineer`: "Frame the candidate as the builder who owns a customer's hardest AI deployment end to end — scoping under ambiguity, integrating their stack, shipping a production system, and staying accountable for whether it works."

## 6. Warning

Do not split the resume evenly across multiple archetypes. If the JD looks 60/40 between two modes, pick the 60 and let the 40 shape selected bullets.
