# Courthouse Debate Agents

**Detailed documentation of the Defense, Prosecution, and Judge agents.**

## Overview

The Courthouse Debate system uses three specialized agents that work together through adversarial collaboration:

```text
Defense ←→ Prosecution
      ↘   ↙
      Judge
```

Each agent has distinct responsibilities, methods, and behaviors designed to produce balanced, well-reasoned conclusions.

---

## Defense Agent

**File**: `backend/elysia/tools/courthouse/defense_agent.py`

### Role

Supports and strengthens the initial response using available evidence.

### Visual Identity

| Property | Value |
|----------|-------|
| Color | Blue |
| Icon | Shield (PiShield) |
| Gradient | `from-blue-500/10 via-blue-400/5 to-transparent` |

### Responsibilities

1. Present arguments supporting the initial response
2. Cite evidence from available source documents
3. Address prosecution challenges directly
4. Build logical case for response validity

### DSPy Signature

```python
class DefenseArgument(dspy.Signature):
    """Construct a defense for the initial response"""
    query = dspy.InputField(desc="The original user query")
    initial_response = dspy.InputField(desc="The response to defend")
    available_sources = dspy.InputField(desc="Sources supporting the response")
    prosecution_challenge = dspy.InputField(desc="Challenge from prosecution if any")
    debate_history = dspy.InputField(desc="History of the debate")

    defense = dspy.OutputField(desc="Strong defense of the initial response")
    key_evidence = dspy.OutputField(desc="Key evidence from sources")
    reasoning = dspy.OutputField(desc="Logical reasoning for the defense")
    addresses_challenges = dspy.OutputField(desc="How this addresses prosecution's challenges")
```

### Behavior

**First Round** (no prosecution challenge yet):
- Presents initial defense of the response
- Establishes evidentiary foundation
- Anticipates potential weaknesses

**Subsequent Rounds** (responding to prosecution):
- Directly addresses each prosecution challenge
- Provides counter-evidence from sources
- Strengthens weak points identified

### Output Example

```typescript
{
  agent_role: "defense",
  argument: "The initial response represents a **prudent and evidence-based approach**...\n\n**Why this methodology is appropriate:**\n\n1. Claims about deliberate exploitation require concrete evidence...",
  supporting_sources: [
    {
      title: "Paul_Stangl_85.txt",
      excerpt: "Brazilian Consular Qualification Card documentation",
      relevance: "Supporting evidence"
    }
  ],
  reasoning: "The defense argues that claims about systematic abuse require examining both the legal framework and the specific case...",
  debate_round: 1,
  agrees_with_consensus: null
}
```

### Implementation Details

```python
class DefenseAgent:
    def __init__(self, base_lm: dspy.LM):
        self.lm = base_lm
        self.argument_builder = dspy.ChainOfThought(DefenseArgument)

    async def defend(
        self,
        context: DebateContext,
        prosecution_challenge: CourthouseMessage = None
    ) -> CourthouseMessage:
        # Prepare sources summary (first 5 sources)
        sources_summary = self._summarize_sources(context.initial_sources)

        # Get prosecution challenge text
        challenge_text = prosecution_challenge.argument if prosecution_challenge else "No challenges yet"

        # Generate defense using LLM
        with dspy.context(lm=self.lm):
            result = self.argument_builder(
                query=context.initial_query,
                initial_response=context.initial_response,
                available_sources=sources_summary,
                prosecution_challenge=challenge_text,
                debate_history=debate_summary
            )

        return CourthouseMessage(
            agent_role=AgentRole.DEFENSE,
            argument=defense_text,
            supporting_sources=supporting_sources,
            reasoning=result.reasoning,
            debate_round=context.current_round,
            agrees_with_consensus=None
        )
```

---

## Prosecution Agent

**File**: `backend/elysia/tools/courthouse/prosecution_agent.py`

### Role

Critically evaluates responses through logical challenges and counter-arguments.

### Visual Identity

| Property | Value |
|----------|-------|
| Color | Red |
| Icon | Sword (PiSword) |
| Gradient | `from-red-500/10 via-red-400/5 to-transparent` |

### Responsibilities

1. Identify logical gaps in the defense
2. Challenge unsupported claims
3. Provide constructive improvement suggestions
4. Determine when to accept the defense (be "easily convincible")

### DSPy Signature

```python
class ProsecutionChallenge(dspy.Signature):
    """Construct logical challenges to the response"""
    query = dspy.InputField(desc="The original user query")
    initial_response = dspy.InputField(desc="The response to challenge")
    defense_argument = dspy.InputField(desc="Defense's latest argument")
    debate_history = dspy.InputField(desc="History of the debate")
    previous_challenges = dspy.InputField(desc="Previous challenges made")

    challenge = dspy.OutputField(desc="Logical challenge to the response or defense")
    specific_issues = dspy.OutputField(desc="Specific logical flaws or missing elements")
    reasoning = dspy.OutputField(desc="Reasoning behind the challenge")
    constructive_suggestion = dspy.OutputField(desc="How the response could be improved")
    convince_threshold_reached = dspy.OutputField(desc="Whether prosecution is convinced (true/false)")
```

### Behavior

**Challenge Mode** (not yet convinced):
- Identifies specific logical flaws
- Points out missing information
- Provides constructive suggestions for improvement
- Continues challenging until convinced or limit reached

**Convinced Mode** (defense addressed concerns):
- Returns `agrees_with_consensus: true`
- Acknowledges defense arguments
- Debate moves toward consensus

### Challenge Limits

The prosecution is designed to be "easily convincible":

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `max_prosecution_arguments` | 3 | Prevents endless debate |
| `conviction_threshold` | 0.7 | High bar for being convinced |

When the limit is reached, prosecution automatically agrees:

```python
if not context.can_prosecution_argue():
    return None  # Signals automatic agreement
```

### Output Example

```typescript
{
  agent_role: "prosecution",
  argument: "Does committing to examine evidence constitute an adequate response?\n\n**Specific concerns:**\n\n1. **Circular reasoning**: The defense praises the response for avoiding 'unsubstantiated claims' while ignoring that the response makes no claims at all...\n\n**Suggestion**: The response should be reframed: (1) First, clarify whether the document can be located...",
  supporting_sources: [],
  reasoning: "The prosecution argues that the defense conflates two separate issues...",
  debate_round: 1,
  agrees_with_consensus: false
}
```

### Key Design Principle

**Logic over sources**: Prosecution uses logical analysis, not document citations. This ensures challenges are based on reasoning quality, not competing evidence claims.

```python
return CourthouseMessage(
    agent_role=AgentRole.PROSECUTION,
    argument=challenge_text,
    supporting_sources=[],  # Prosecution uses logic, not sources
    reasoning=result.reasoning,
    debate_round=context.current_round,
    agrees_with_consensus=False
)
```

---

## Judge Agent

**File**: `backend/elysia/tools/courthouse/judge_agent.py`

### Role

Neutral moderator that evaluates arguments and synthesizes conclusions.

### Visual Identity

| Property | Value |
|----------|-------|
| Color | Purple |
| Icon | Scales (PiScales) |
| Gradient | `from-purple-500/10 via-purple-400/5 to-transparent` |

### Responsibilities

1. Maintain strict neutrality between defense and prosecution
2. Evaluate logical strength of both arguments
3. Determine when consensus is possible
4. Synthesize final verdict when consensus reached

### DSPy Signature

```python
class JudgeEvaluation(dspy.Signature):
    """Evaluate arguments and maintain neutrality in the debate"""
    query = dspy.InputField(desc="The original user query")
    initial_response = dspy.InputField(desc="The initial response being debated")
    defense_argument = dspy.InputField(desc="Defense agent's argument")
    prosecution_argument = dspy.InputField(desc="Prosecution agent's counter-argument")
    debate_history = dspy.InputField(desc="History of the debate so far")

    evaluation = dspy.OutputField(desc="Neutral evaluation of both arguments")
    consensus_possible = dspy.OutputField(desc="Whether consensus can be reached (true/false)")
    reasoning = dspy.OutputField(desc="Logical reasoning for the evaluation")
    final_verdict = dspy.OutputField(desc="If consensus reached, the final agreed-upon answer")
```

### Behavior

**Evaluation Mode** (consensus not yet reached):
- Objectively assesses both arguments
- Identifies strengths and weaknesses in each position
- Guides debate toward resolution

**Consensus Mode** (agreement achieved):
- Declares "CONSENSUS REACHED"
- Provides synthesized final verdict
- Integrates valid points from both sides

### Output Example

**During Debate**:
```typescript
{
  agent_role: "judge",
  argument: "The defense is correct that systemic claims require rigorous evidence, but the prosecution is correct that this rigor begins with establishing facts, not deferring them...",
  supporting_sources: [],
  reasoning: "The judge evaluates both arguments and finds merit in each...",
  debate_round: 1,
  agrees_with_consensus: null
}
```

**At Consensus**:
```typescript
{
  agent_role: "judge",
  argument: "**CONSENSUS REACHED**: The debate concludes with agreement on a **revised understanding** of how to approach the Brazilian immigration law question...",
  supporting_sources: [],
  reasoning: "The judge confirms consensus has been reached. Both prosecution and defense agree...",
  debate_round: 2,
  agrees_with_consensus: true
}
```

### Neutrality Enforcement

The judge does not cite sources - only evaluates logical arguments:

```python
return CourthouseMessage(
    agent_role=AgentRole.JUDGE,
    argument=evaluation_text,
    supporting_sources=[],  # Judge doesn't provide sources, only evaluation
    reasoning=result.reasoning,
    debate_round=context.current_round,
    agrees_with_consensus=consensus_reached
)
```

---

## Debate Orchestration

**File**: `backend/elysia/tools/courthouse/courthouse_debate.py`

### Flow Control

```python
async def __call__(self, ...):
    # Initialize agents
    judge = JudgeAgent(base_lm=base_lm)
    defense = DefenseAgent(base_lm=base_lm)
    prosecution = ProsecutionAgent(base_lm=base_lm)

    # Conduct debate rounds
    while current_round <= max_rounds and not consensus_reached:
        # Defense presents
        defense_msg = await defense.defend(context, prosecution_last)
        yield defense_msg

        # Prosecution challenges
        prosecution_msg = await prosecution.challenge(context, defense_msg)
        yield prosecution_msg

        # Judge evaluates
        judge_msg = await judge.evaluate(context, defense_msg, prosecution_msg)
        yield judge_msg

        # Check for consensus
        if self._check_consensus(context):
            consensus_reached = True
```

### Consensus Detection

```python
def _check_consensus(self, context: DebateContext) -> bool:
    # Get messages from current round
    current_round_messages = [
        msg for msg in context.debate_history
        if msg.debate_round == context.current_round
    ]

    # Need all three agents to have responded
    if len(current_round_messages) < 3:
        return False

    # Check if all agents agree
    judge_agrees = any(
        msg.agent_role == AgentRole.JUDGE and msg.agrees_with_consensus
        for msg in current_round_messages
    )
    prosecution_agrees = any(
        msg.agent_role == AgentRole.PROSECUTION and msg.agrees_with_consensus
        for msg in current_round_messages
    )

    return judge_agrees and prosecution_agrees
```

---

## Data Structures

### DebateContext

Shared state passed between agents:

```python
@dataclass
class DebateContext:
    initial_query: str
    initial_response: str
    initial_sources: List[Dict[str, Any]]
    debate_history: List[CourthouseMessage]
    current_round: int
    max_rounds: int = 5
    prosecution_counter_arguments: int = 0
    max_prosecution_arguments: int = 3
```

### CourthouseMessage

Standard message format for all agents:

```python
@dataclass
class CourthouseMessage(Result):
    agent_role: AgentRole
    argument: str
    supporting_sources: List[Dict[str, Any]]
    reasoning: str
    debate_round: int
    agrees_with_consensus: Optional[bool] = None
```

### AgentRole Enum

```python
class AgentRole(Enum):
    JUDGE = "judge"
    DEFENSE = "defense"
    PROSECUTION = "prosecution"
```

---

## See Also

- [Courthouse Debate Overview](index.md) - Main guide
- [Intelligence Analysis](../intelligence-analysis/) - Alternative multi-agent system
- [Rat Lines Demo](../../demos/rat-lines/) - Full demo using this system
