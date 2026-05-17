# Prompt Template Frameworks

12 structural templates. Pick based on task type, not habit.

---

## CO-STAR
**Best for:** Writing, communication, content creation
```
Context: [Background the model needs]
Objective: [Specific task]
Style: [Writing style]
Tone: [Emotional register]
Audience: [Who reads the output]
Response: [Format and length]
```

## RISEN
**Best for:** Complex tasks requiring methodology
```
Role: [Expert identity]
Instructions: [What to do]
Steps: [Ordered procedure]
End-goal: [What success looks like]
Narrowing: [Constraints and scope limits]
```

## RTF (Role / Task / Format)
**Best for:** Quick, well-scoped tasks
```
Role: [Who you are]
Task: [What to do]
Format: [How to present output]
```

## Chain-of-Thought
**Best for:** Reasoning, math, multi-step logic. NOT for O1/O3/O4-mini.
```
[Task description]
Think through this step by step before giving your final answer.
```

## Few-Shot
**Best for:** Classification, consistent formatting, stylistic tasks
```
[Task description]
Input: [example 1] → Output: [example 1 output]
Input: [example 2] → Output: [example 2 output]
Input: [actual input] → Output:
```

## Grounding Template
**Best for:** Factual tasks, reducing hallucination
```
Using ONLY the following source material, [task].
If the answer isn't in the source, say "I don't know."

<source>[document here]</source>

Before answering, pull relevant quotes into <quotes> tags.
Then answer from those quotes.
```

## ReAct (Reason + Act)
**Best for:** Agentic tasks, tool use
```
[Task description]
Thought: [reason about next step]
Action: [take an action]
Observation: [note what you observed]
... repeat ...
Final Answer: [conclusion]
Stop and ask before: [list irreversible actions]
```

## Decomposition
**Best for:** Large tasks benefiting from sub-task isolation
```
Complete this in phases. Finish each before starting the next.
Phase 1: [sub-task]
Phase 2: [sub-task]
Phase 3: [sub-task]
After each phase, state what you completed and what comes next.
```

## Reflection / Self-Check
**Best for:** High-stakes outputs
```
[Task description]
After completing your response:
1. Re-read it against the original request
2. Check: [specific criteria]
3. Revise anything that doesn't meet criteria
4. Give me your final version
```

## Perspective Shifting
**Best for:** Comprehensive analysis, avoiding bias
```
Analyze [topic] from three perspectives:
1. [Perspective A]
2. [Perspective B]
3. [Perspective C]
For each: 2-3 sentence assessment + one-word verdict.
Close with overall recommendation.
```

## Memory Block (Multi-Turn)
**Best for:** Long sessions where decisions carry forward
```
## Prior Decisions (Carry Forward)
- [Decision 1]
- [Decision 2]
Do not contradict these. Flag conflicts before proceeding.

[Current task]
```

## Universal Fallback
**Best for:** When unsure which template fits — answer these 4 questions:
1. What do I want the model to DO? (verb + object)
2. What CONTEXT does it need that it doesn't already have?
3. What does the OUTPUT look like? (format, length, structure)
4. What should it NOT do? (scope, style, content exclusions)
