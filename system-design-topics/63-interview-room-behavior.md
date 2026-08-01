# Interview Room Behavior — What No One Teaches You

> The framework tells you what to design. This document tells you how to behave
> in the room. Technically strong candidates fail system design interviews for
> behavioral reasons more often than technical ones.

---

## The 45-Minute Time Budget

Most system design interviews are 45–50 minutes. How you spend that time
signals seniority more than what you say. Here's the target allocation:

```
Minutes 0–5:   Clarify requirements (ask questions, write answers down)
Minutes 5–8:   Back-of-the-envelope (derive 3–4 key numbers out loud)
Minutes 8–20:  High-level design (draw the boxes, walk the happy path)
Minutes 20–35: Deep dive (pick 2–3 hard components, go deep)
Minutes 35–42: Trade-offs and bottlenecks (proactive, before they ask)
Minutes 42–45: Buffer (interviewer questions, wrapping up)
```

**The most common time failure:** spending 25 minutes on requirements and
estimates, then rushing the deep dive. The deep dive is where you demonstrate
senior/staff-level thinking. Guard that time aggressively.

**The check-in rule:** Every 10–12 minutes, pause and ask:
> "Does this level of depth make sense, or would you like me to focus on
> a different component?"

This does three things: shows self-awareness, gives the interviewer a chance
to redirect you toward what they actually care about, and prevents you from
spending 15 minutes on a component the interviewer considers trivial.

---

## How to Handle Interviewer Hints

Interviewers give hints when you're heading in the wrong direction or missing
something important. Most candidates either ignore hints or overcorrect.
Neither is right.

### Recognizing a hint

Hints come in several forms:

```
Direct:    "What happens if that service goes down?"
           → They want failure modes. You haven't covered them.

Probing:   "Interesting. Why did you choose Kafka over RabbitMQ there?"
           → They want you to justify the decision, not change it.

Redirecting: "What about the write path — you've focused a lot on reads."
           → They want you to shift focus, not abandon what you've done.

Challenging: "Hmm, would that really scale to 10M users?"
           → They may be testing if you'll stand your ground or cave.
```

### The right response to each

**For direct hints** — acknowledge and address immediately:
> "Good point. Let me add the failure mode for that. If the service goes
> down, the circuit breaker opens and we fall back to [X]..."

**For probing questions** — defend your decision with constraints:
> "Kafka over RabbitMQ because we need log replay for the retry path.
> RabbitMQ deletes messages after consumption, which breaks our ability
> to reprocess failed deliveries. If replay wasn't a requirement,
> RabbitMQ would be simpler."

**For redirecting hints** — shift without abandoning:
> "You're right, I've been focused on reads. Let me cover the write path —
> the key constraint there is [X], which means..."

**For challenging questions** — the most important one.

---

## How to Handle Pushback Without Caving

This is where staff candidates distinguish themselves. When an interviewer
challenges your design, there are three possible situations:

```
Situation A: They're right, you made a mistake.
Situation B: They're testing if you'll defend a correct decision.
Situation C: They're exploring a genuine trade-off, not declaring you wrong.
```

The failure mode: treating all pushback as Situation A and immediately
abandoning your design. Interviewers are frequently testing Situation B —
they give pushback on a correct decision to see if you have conviction.

**Framework for responding to any challenge:**

```
Step 1: Acknowledge the concern genuinely (not dismissively)
Step 2: Restate your constraint (why you made the decision)
Step 3: Either defend or adapt, with explicit reasoning
Step 4: If you're adapting, name what changed
```

**Example — defending a correct decision:**

Interviewer: "You chose eventual consistency for the feed. But users will
see stale data. Isn't that a problem?"

Bad response: "You're right, maybe I should use strong consistency."

Good response: "The staleness is bounded — the SWR revalidation window is
under 5 seconds. For a social feed, seeing a post 3 seconds late is not a
user-visible problem. Strong consistency would require distributed locking
across the fanout pipeline, adding 50–200ms to every feed read. That
latency trade-off is worse than 3 seconds of bounded staleness. If the
requirement was financial data — balances, prices — I'd flip to strong
consistency immediately. But for feed content, eventual is the right call."

**Example — genuinely adapting when they're right:**

Interviewer: "Your matching algorithm sends the trip offer to one driver
at a time. What if the top 5 drivers all decline? That's 75 seconds of wait
time before you widen the search."

Good response: "That's a real problem I didn't account for. You're right that
sequential offers with a 15-second timeout creates a poor experience under
high decline rates. Let me adjust — after 2 consecutive declines, I'd widen
the radius in parallel rather than waiting for the full 15 seconds on each.
The driver offer system should have a parallel path for high-decline-rate
conditions. I'd trigger it based on a decline_rate signal from the past hour
in that geo-zone."

Notice: you acknowledge they're right, explain why your original was wrong,
and give a specific fix. You don't just say "good point, I'll fix it."

---

## What to Do When You Don't Know

Silence kills interviews. If you don't know something:

**Don't:** Sit quietly hoping it comes to you.
**Don't:** Guess and state it as fact.
**Do:** Reason out loud from first principles.

The script:

```
"I'm not immediately certain about [specific thing]. Let me reason
through it from what I do know..."

Then actually reason:
  "The constraint here is [X]. I know that [Y] satisfies [X] in general.
   The question is whether [Y] also handles [edge case Z]..."
```

Most of the time, reasoning out loud gets you to the right answer anyway.
And even when it doesn't, you've demonstrated the reasoning process —
which is what interviewers are actually evaluating.

**Real example — you're asked about a technology you've never used:**

"I haven't worked with Apache Flink specifically, but the requirement is
stream processing with windowed aggregations — the same class of problem
that Spark Streaming and Kafka Streams also solve. I'd describe the
architecture using the properties I need — exactly-once processing, stateful
windowing, backpressure handling — and note that Flink is a strong fit for
those properties based on its design goals, even though I'd want to
prototype before committing."

This is better than pretending you know Flink's internals and better than
saying "I don't know Flink."

---

## The Disagreement Scenario

Sometimes you'll genuinely disagree with direction the interviewer gives.
This happens more at staff-level interviews — interviewers intentionally
push suboptimal directions to see how you handle it.

**The wrong response:** Roll over and adopt their suggestion uncritically.
**The also wrong response:** Argue defensively.
**The right response:** Engage with the substance, propose a comparison.

Script:
```
"I want to make sure I'm understanding the concern correctly —
are you suggesting [paraphrase their suggestion] primarily because
of [reason you inferred]?

If that's the constraint, then [their suggestion] addresses it, but
it introduces [trade-off you see]. My original approach handles [constraint]
differently by [your approach]. 

I think the decision comes down to which trade-off we're more willing to
accept: [trade-off A] vs. [trade-off B]. Do you have a preference given
the system's requirements?"
```

This converts a disagreement into a structured trade-off discussion — which
is exactly the conversation staff-level interviews are supposed to be.

---

## The "Philosophy" Questions

At staff level, some interviewers open with or close with broad judgment
questions. These are not trick questions — they want to hear how you think.

**"What's the most important property of a well-designed system?"**

There's no single right answer, but there are bad answers:
- "Scalability" (too generic, sounds memorized)
- "Reliability" (also generic)

A good answer is specific and shows a point of view:

> "Operability — can the team that didn't build it run it at 3am without
> calling the original author? Scalability and reliability matter, but they're
> downstream of having a system you can understand, observe, and fix under
> pressure. I've seen highly scalable systems that were operationally
> nightmares and caused more incidents than the simpler systems they replaced."

**"Tell me about a design decision you regret."**

This is a trap for candidates who can't be self-critical. The answer should:
- Name a specific, real decision (not vague)
- Explain what you thought at the time and why it seemed right
- Explain what actually happened
- Name what you'd do differently and why

Example:
> "Early in my career I designed a notification system with synchronous
> webhook delivery — the API didn't return until the webhook was acknowledged.
> My reasoning was that it kept the flow simple and guaranteed delivery order.
> What happened: as merchant endpoints got slower, our API latency degraded
> with them. A merchant's slow server became our latency problem. I'd
> decouple delivery from the API response — return immediately with an event
> ID and deliver asynchronously. The lesson was that coupling your availability
> to a third party's behavior is almost always the wrong trade-off."

**"How do you decide when a system is ready to ship?"**

Staff-level answer addresses more than "tests pass":
> "Three things: the happy path works and is tested, the failure modes are
> handled and have runbooks, and the team that will own it on-call can
> describe how it works without me in the room. The third one is often the
> last to be ready."

---

## Signs You're Running the Interview Well

These are positive signals — keep doing them:

- The interviewer is asking follow-up questions (engagement, not confusion)
- You're naming trade-offs before they ask
- You're asking "does this make sense?" periodically and adjusting
- The interviewer says "good point" or "exactly" — rare but meaningful
- You're connecting components back to constraints ("because we have 1M writes/s")

## Signs You're Off Track

Act on these immediately:

- More than 15 minutes have passed without drawing anything
- You've been talking about one component for more than 8 minutes
- The interviewer has said "interesting" without a follow-up question twice
  (usually means they're waiting for you to move on)
- You've contradicted yourself and haven't noticed (they have)
- You're listing technologies without explaining why

When you notice any of these, stop and reset:
> "Let me step back — I want to make sure I'm focusing on the right areas.
> Would it be more useful to go deeper on [component A] or move to [component B]?"

---

## Pre-Interview Checklist (30 minutes before)

```
Technical warmup:
  □ Review the 6-step framework out loud (not in your head)
  □ Run through one estimation: pick any system, derive writes/s and storage
  □ Remind yourself of 3 constraint → technology mappings
    (e.g., "1M writes/s → Cassandra, not Postgres")

Mental prep:
  □ What are you most likely to rush? (Usually: trade-offs and failure modes)
  □ What's your "I don't know" script? Rehearse it once.
  □ What's your check-in question? ("Does this level of depth make sense?")

Logistics:
  □ Have something to write on (whiteboard, paper, shared doc)
  □ Speak as you draw — narrate every component as you place it
  □ First thing you say after "hi": clarifying questions, not a solution
```
