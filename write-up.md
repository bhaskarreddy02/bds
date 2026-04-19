# Reflection Tree Design Rationale

## 1. Why I Chose These Specific Questions

The overarching goal in designing the questions was to **expose inherent mindsets rather than prompt the user for the "morally correct" answer**. 
When questions are too obvious (e.g., "Did you act like a victim today?"), self-reporting bias ruins the data. Instead, the questions are framed as contextual reactions to events.

- **Axis 1 (Locus):** I opened with a highly generic, non-judgmental question ("How did today go?"). Branching from this, the tree probes the user's *instinctual response* to friction or success. If they say the day was frustrating, asking "who was responsible" reveals if they externalize blame (External Locus) or focus on what they can salvage (Internal Locus).
- **Axis 2 (Orientation):** I asked about interactions concerning "work distribution or recognition". Option 1 ("unacknowledged work") and Option 2 ("annoyed by weight") naturally tease out entitlement. The follow-ups then distinguish between expecting recognition as a *trade-off* versus contributing to a collective outcome.
- **Axis 3 (Radius):** I explicitly avoided asking "Do you care about others?" Instead, I asked who was at the *center of the psychological narrative* during the most stressful moment. This directly maps to perspective-taking. Options widen the aperture logically from self -> manager -> broader team -> mission.

## 2. Branching Design and Trade-Offs

The core structural trade-off was between a flat scoring system and a highly contextual branching narrative. I chose to use **state-tracking coupled with contextual routing** to strike a balance.

- **The Opening "Funnel" (A_OPEN nodes):** I use the first question of each axis to determine the tone of the situation, but *not* necessarily to finalize the signal. A user can have a frustrating day (seemingly negative) but handle it with high agency (Victor). The branching splits the tree based on the *context* (Did things go well or poorly?) and then measures the axis signal contextually.
- **Signal Aggregation over Single-Question Elimination:** The tree tracks `signals` continuously. A decision node (`A1_D2`) routes to a reflection based on the `dominant` signal (`internal >= external`), rather than routing strictly on one answer. This design allows for slightly higher nuance despite strict determinism.
- **Trade-off:** By funneling paths back through `bridge` nodes, I lost the ability to create 12 entirely distinct endings in favor of creating three focused modular blocks. This trades extreme personalization for tighter thematic control over the three psychological vectors.

## 3. Psychological Grounding

- **Julian Rotter & Carol Dweck (Axis 1 - Locus):** Dweck’s research shows that fixed mindsets lead to externalizing failure to protect the ego. Rotter's locus metric is directly represented by options like "I relied on the environment" versus "I adapted my approach."
- **Campbell et al. & Organ (Axis 2 - Orientation):** Organ’s "Organizational Citizenship Behavior" acts as the counterbalance to Campbell’s "Psychological Entitlement." The questions explicitly force a choice between feeling owed (contractual relationship with work) versus discretionary effort (citizenship behavior).
- **Maslow & Batson (Axis 3 - Radius):** The progression from "just me" to "the mission" is directly inspired by Maslow’s later work on Self-Transcendence. Batson's empathy-altruism hypothesis is encoded in the follow-up questions, where understanding a colleague’s pressure (perspective-taking) acts as the antidote to self-centric stress.

## 4. Areas for Improvement (With More Time)

If granted more time, I would improve the system in the following ways:
1. **Weighted Signals:** Currently, every choice gives +1 to a signal. Some choices are stark indicators (e.g., "The system is entirely broken") and should carry heavier weights (+2 or +3) than mild indicators.
2. **Memory Over Sessions:** The determinism of the tree means a user who plays the same way gets the exact same questions daily. I would introduce a mechanism where the user's past dominant traits are passed in at runtime, slightly altering the `START` or `A1_OPEN` node to refer back to yesterday.
3. **Friction Scaling:** Right now, the reflections are polite. A more advanced tree would sense consecutive negative inputs over time and escalate the bluntness of the reflection nodes to force a structural breakthrough.
