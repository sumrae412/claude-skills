# Prompt Techniques Catalog

58 techniques organized by category. Each entry includes: what it is, when to use it, and a quick example.

---

## Reasoning Techniques

### 1. Chain of Thought (CoT)
Ask the model to reason step by step before answering.
- **Use when:** Complex reasoning, math, multi-step logic
- **Example:** "Think through this step by step before giving your final answer."

### 2. Zero-Shot CoT
Add "Let's think step by step" without examples.
- **Use when:** You want reasoning but don't have examples handy
- **Example:** "Let's think step by step: what are the risks of this approach?"

### 3. Tree of Thoughts
Ask the model to explore multiple reasoning branches before selecting the best.
- **Use when:** Problems with multiple valid approaches; creative or strategic tasks
- **Example:** "Consider three different approaches to solving this, evaluate each, then recommend the best."

### 4. Step-by-Step Decomposition
Break the task into explicit numbered steps.
- **Use when:** Complex workflows, tutorials, procedural tasks
- **Example:** "Complete this in three steps: 1) analyze, 2) draft, 3) revise."

### 5. Analogical Reasoning
Ask the model to draw analogies to familiar concepts.
- **Use when:** Explaining complex topics; creative problem-solving
- **Example:** "Explain this concept using an analogy a 10-year-old would understand."

### 6. Counterfactual Reasoning
Ask "what if" to explore alternatives.
- **Use when:** Risk analysis, scenario planning, exploring edge cases
- **Example:** "What would happen if we removed this constraint?"

### 7. Causal Analysis
Ask the model to trace causes and effects.
- **Use when:** Root cause analysis, debugging, understanding failures
- **Example:** "What caused this outcome, and what would prevent it?"

### 8. Socratic Method
Use probing questions to guide reasoning.
- **Use when:** Learning, debugging, uncovering assumptions
- **Example:** "What assumptions are we making? Are they valid?"

### 9. Devil's Advocate
Ask the model to argue against its own conclusion.
- **Use when:** Stress-testing decisions, avoiding confirmation bias
- **Example:** "Now argue the opposite position as convincingly as you can."

### 10. Hypothesis Testing
Ask the model to form and test hypotheses.
- **Use when:** Research, debugging, data analysis
- **Example:** "Form a hypothesis, then test it against the evidence provided."

---

## Context & Grounding Techniques

### 11. Few-Shot Learning
Provide 2-5 examples of input → output pairs.
- **Use when:** Consistent formatting, stylistic tasks, classification
- **Example:** "Input: X → Output: Y. Input: A → Output: B. Now: Input: C → Output:"

### 12. One-Shot Learning
Provide exactly one example.
- **Use when:** Simple tasks where one example is sufficient
- **Example:** "Example: [X]. Now do the same for: [Y]."

### 13. Zero-Shot Prompting
No examples; rely on task description alone.
- **Use when:** Simple, well-defined tasks; general knowledge questions
- **Example:** "Summarize the following text in 3 sentences."

### 14. Self-Consistency
Ask the model to generate multiple answers and pick the most consistent.
- **Use when:** Factual questions, calculations, decisions with right answers
- **Example:** "Generate three independent answers, then identify the one most supported by the evidence."

### 15. Retrieval Augmentation (Context Injection)
Provide relevant documents or facts in the prompt.
- **Use when:** Domain-specific tasks, reducing hallucination
- **Example:** "Using only the following document: [doc]. Answer: [question]."

### 16. Contextual Priming
Set up the conversation context before the task.
- **Use when:** Tone-sensitive tasks, domain setup
- **Example:** "We've been discussing X. Given that context, now..."

### 17. Background Framing
Provide relevant background before the main task.
- **Use when:** Domain-specific tasks, reducing assumptions
- **Example:** "Our company does X. Our users are Y. Given this, write Z."

### 18. Reflection Prompting
Ask the model to review and critique its own output.
- **Use when:** Quality improvement, catching errors
- **Example:** "Review your response above. What could be improved?"

### 19. Iterative Refinement
Ask the model to improve its output in multiple passes.
- **Use when:** Complex writing, polishing outputs
- **Example:** "Draft a response, then revise it once for clarity and once for conciseness."

### 20. Grounding Constraints
Restrict the model to only what's in provided materials.
- **Use when:** Preventing hallucination, factual accuracy
- **Example:** "Answer using only the information in the provided text. Say 'I don't know' if it's not there."

---

## Role & Persona Techniques

### 21. Role-Play / Expert Persona
Assign the model a specific role or expertise.
- **Use when:** Domain expertise needed, tone setting, perspective taking
- **Example:** "You are a senior product manager at a B2B SaaS company. Review this spec."

### 22. Audience Persona
Specify who the model is writing for.
- **Use when:** Tailoring tone, vocabulary, and depth
- **Example:** "Write this for a non-technical executive who cares about ROI, not implementation details."

### 23. Character Roleplay
Ask the model to embody a fictional or historical character.
- **Use when:** Creative writing, perspective exercises, education
- **Example:** "Respond as if you are Sherlock Holmes analyzing this business problem."

### 24. Adversarial Persona
Ask the model to take an opposing or critical stance.
- **Use when:** Stress-testing, debate prep, finding weaknesses
- **Example:** "You are a skeptical investor. What's your biggest concern with this pitch?"

### 25. Collaborative Partner
Frame the model as a co-creator, not just an executor.
- **Use when:** Brainstorming, iterative work
- **Example:** "Let's work on this together. Start by sharing your initial thoughts, then we'll refine."

---

## Structural Techniques

### 26. Template / Fill-in-the-Blank
Provide a structure for the model to fill in.
- **Use when:** Consistent format needed; reports, emails, specs
- **Example:** "Use this template: Subject: [X]. Background: [Y]. Ask: [Z]."

### 27. Framework Application
Ask the model to apply a named framework.
- **Use when:** Business analysis, strategic thinking
- **Example:** "Analyze this using the SWOT framework."

### 28. Checklist Prompting
Ask the model to work through a checklist.
- **Use when:** Quality assurance, completeness checks
- **Example:** "Check your response against this list: [1, 2, 3]."

### 29. Format Specification
Explicitly define the output format.
- **Use when:** Any task where format matters
- **Example:** "Respond in JSON with fields: title, summary, tags."

### 30. Length Specification
Set explicit length constraints.
- **Use when:** Summaries, social posts, executive briefs
- **Example:** "Keep your response under 150 words."

### 31. Section Headers
Ask the model to organize output into named sections.
- **Use when:** Reports, analyses, structured documents
- **Example:** "Structure your response with these sections: Summary, Findings, Recommendations."

### 32. Bullet vs. Prose
Specify whether to use lists or flowing text.
- **Use when:** Format consistency matters
- **Example:** "Use prose, not bullet points."

### 33. Priority Ordering
Ask the model to rank or order outputs.
- **Use when:** Recommendations, decisions, issue lists
- **Example:** "List these from highest to lowest priority, with your reasoning."

### 34. Tabular Output
Request data in table format.
- **Use when:** Comparisons, structured data, side-by-side analysis
- **Example:** "Present your findings in a table with columns: Option, Pros, Cons, Verdict."

### 35. Layered Output
Ask for output at multiple levels of detail.
- **Use when:** Executive + technical audiences, progressive disclosure
- **Example:** "Give a 1-sentence summary, then a 1-paragraph explanation, then full detail."

---

## Creative Techniques

### 36. Scenario / Situation Framing
Set a specific scenario before the task.
- **Use when:** Creative writing, strategic hypotheticals
- **Example:** "Imagine it's 2030 and AI is commodity. Now write a business case for X."

### 37. Constraint-Based Creativity
Add unusual constraints to spark creativity.
- **Use when:** Ideation, avoiding clichés
- **Example:** "Suggest 5 marketing ideas, but none can involve social media."

### 38. Perspective Shifting
Ask for multiple viewpoints on the same topic.
- **Use when:** Comprehensive analysis, avoiding bias
- **Example:** "Describe this product from the perspective of: a new user, a power user, and a skeptic."

### 39. Metaphor Generation
Ask the model to explain via metaphor.
- **Use when:** Complex concepts, teaching, persuasion
- **Example:** "Explain this architecture using a metaphor from everyday life."

### 40. Brainstorming Mode
Explicitly ask for quantity over quality.
- **Use when:** Ideation, early exploration
- **Example:** "Generate 20 ideas without filtering. Quantity matters more than quality here."

### 41. Reverse Brainstorming
Ask how to achieve the opposite of the goal, then invert.
- **Use when:** Finding failure modes, creative problem-solving
- **Example:** "How would you make this feature as confusing as possible? Now invert those."

### 42. SCAMPER
Apply the SCAMPER framework (Substitute, Combine, Adapt, Modify, Put to other uses, Eliminate, Reverse).
- **Use when:** Product ideation, improving existing solutions
- **Example:** "Apply SCAMPER to this feature to generate improvement ideas."

---

## Verification & Quality Techniques

### 43. Confidence Signaling
Ask the model to express uncertainty.
- **Use when:** Factual accuracy, reducing hallucination risk
- **Example:** "Indicate your confidence level (high/medium/low) for each claim."

### 44. Source Citation
Ask the model to cite evidence for claims.
- **Use when:** Research, factual tasks
- **Example:** "Support each claim with a source or clearly label it as your inference."

### 45. Assumption Listing
Ask the model to state its assumptions explicitly.
- **Use when:** Ambiguous tasks, complex reasoning
- **Example:** "Before answering, list any assumptions you're making."

### 46. Edge Case Identification
Ask the model to identify exceptions and edge cases.
- **Use when:** System design, testing, risk analysis
- **Example:** "After your main answer, list 3 edge cases or exceptions to be aware of."

### 47. Completeness Check
Ask the model to verify nothing is missing.
- **Use when:** Checklists, documents, specs
- **Example:** "Review your response and confirm you've addressed all parts of the request."

### 48. Output Validation
Ask the model to validate its own output against criteria.
- **Use when:** Code, data, structured outputs
- **Example:** "Check that your JSON is valid and all required fields are present."

---

## Instruction & Constraint Techniques

### 49. Negative Constraints
Explicitly state what NOT to do.
- **Use when:** Avoiding common pitfalls, style enforcement
- **Example:** "Do not use jargon. Do not start with 'Certainly.' Do not use bullet points."

### 50. Positive-Only Framing
Frame all instructions as what to do, not what to avoid.
- **Use when:** Creative tasks where constraints feel limiting
- **Example:** "Use plain language, short sentences, and active voice."

### 51. Priority Instructions
Tell the model which instruction takes precedence if there's a conflict.
- **Use when:** Complex multi-constraint prompts
- **Example:** "If brevity conflicts with completeness, prioritize completeness."

### 52. Conditional Logic
Include if/then rules in the prompt.
- **Use when:** Variable outputs depending on input
- **Example:** "If the query is technical, include code examples. If non-technical, use analogies."

### 53. Staged Instructions
Break instructions into phases.
- **Use when:** Long or complex tasks
- **Example:** "Phase 1: Research. Phase 2: Outline. Phase 3: Write. Complete each before moving on."

---

## Meta-Prompting Techniques

### 54. Prompt Refinement Request
Ask the model to improve the prompt itself.
- **Use when:** You're not sure how to phrase something
- **Example:** "Rewrite this prompt to be clearer and more specific: [original prompt]."

### 55. Task Clarification Request
Ask the model to ask clarifying questions before proceeding.
- **Use when:** High-stakes tasks where misunderstanding is costly
- **Example:** "Before answering, ask me any clarifying questions you need."

### 56. Instruction Explanation
Ask the model to explain its interpretation of the task.
- **Use when:** Complex or ambiguous tasks
- **Example:** "Before starting, explain how you interpret this task."

### 57. Output Preview
Ask the model to show a preview/outline before full execution.
- **Use when:** Long tasks, documents, code
- **Example:** "Show me an outline of your planned response before writing it in full."

### 58. Post-Task Reflection
Ask the model to reflect on what it would do differently.
- **Use when:** Learning, quality improvement, iteration
- **Example:** "After completing this task, note what you'd do differently on the next iteration."
