# From Ambiguous Prompt to Concrete Design — In 5 Minutes

> The hardest part of a system design interview is the first 5 minutes.
> The problem is always under-specified. Candidates who studied system design
> know what to build once they know what the problem is. The skill being
> tested here is extracting the right problem from a vague prompt.

---

## Why This Is Hard

An interviewer says: *"Design Nordstrom's checkout system."*

That sentence contains almost no information. It could mean:
- The checkout cart UI flow
- The payment processing pipeline
- The inventory reservation system
- The order management system
- The promotion/discount engine
- All of the above

A candidate who starts drawing immediately is designing for their own
assumptions — not for what the interviewer wants to evaluate. They'll spend
20 minutes on payment processing when the interviewer wanted to talk about
inventory consistency under peak load.

The fix: **a structured 4-question clarification sequence** that takes
3–5 minutes and gives you everything you need to design the right system.

---

## The 4-Question Clarification Sequence

Ask these in order. Each one narrows the problem space significantly.

```
Q1: "What's the most important user-facing behavior?"
    → Surfaces the core scenario you're designing for

Q2: "What's the hardest constraint — latency, consistency, or scale?"
    → Identifies which non-functional requirement dominates

Q3: "What's explicitly out of scope for this session?"
    → Prevents scope creep and signals the interviewer what you're not doing

Q4: "Is there a specific failure mode you'd like me to focus on?"
    → Often the interviewer already knows what hard problem they want to
       discuss — this gives them a chance to point you there
```

You won't always get answers to all four. That's fine. The act of asking
signals that you're structured and that you understand design is about
trade-offs, not just knowing the right boxes to draw.

---

## Worked Example 1 — "Design Nordstrom's Checkout"

**Prompt:** *"Design the checkout experience for Nordstrom.com."*

### The clarification conversation

**You:** "Before I start, a few questions to make sure I'm solving the right
problem. First — what's the most important behavior we're designing for?
Is this the end-to-end purchase flow, or is there a specific part you want
to go deep on — payment processing, inventory reservation, the cart,
something else?"

**Interviewer:** "Think of it as the full checkout flow — from cart to
confirmed order."

**You:** "Got it. Second question — what's the hardest constraint here?
Is it peak scale (like Anniversary Sale), consistency (preventing overselling),
or latency (fast checkout experience)?"

**Interviewer:** "Both scale and consistency matter. We can't oversell, and
during Anniversary Sale we get a lot of concurrent traffic."

**You:** "Good — that tells me inventory reservation is the core hard problem.
Third, what's out of scope? Should I include the payment processing integration,
or treat that as a black box?"

**Interviewer:** "Treat payment as a black box — focus on what happens on
our side."

**You:** "Last question — is there a specific failure mode you want me to
address? Like what happens if two users are buying the last item, or what
happens if we have a partial system failure during checkout?"

**Interviewer:** "Yes — the two users buying the last item is interesting.
Let's make sure your design handles that."

### What you now know

```
Core problem:    Cart → inventory reservation → order creation
Hard constraint: Inventory consistency + peak scale (500K concurrent users)
Out of scope:    Payment processing internals
Focus area:      The "last item" race condition
```

You've gone from one vague sentence to a concrete, scoped problem. You know
exactly what to design and what the interviewer wants to see.

### What you say next

*"Great. Let me write down the key requirements and then do a quick
back-of-the-envelope before drawing anything."*

Then write on the whiteboard/shared doc:
```
Core: Cart → reserve inventory → create order → payment → confirm

Non-functional:
  - No overselling (strong consistency at reservation)
  - 500K concurrent users at peak (Anniversary Sale)
  - Checkout p99 < 3s

Out of scope: payment provider integration

Key scenario to nail: two users buying the last SKU simultaneously
```

Now start estimating. You're designing the right thing.

---

## Worked Example 2 — "Design a Notification System"

**Prompt:** *"Design a notification system."*

This is intentionally vague. The right design is completely different
depending on the answers.

### The clarification conversation

**You:** "What types of notifications — push (mobile), email, SMS, in-app,
or all of the above?"

**Interviewer:** "All of the above. The system should be channel-agnostic."

**You:** "And what triggers notifications? User actions like likes and
comments, system events like order shipping, or scheduled marketing
campaigns?"

**Interviewer:** "All three — transactional (order shipped), social
(someone liked your post), and marketing (campaign blasts)."

**You:** "Important question on the consistency requirement: for marketing
campaigns, if we send to 100M users and 0.1% don't receive it, is that
acceptable? Or do we need at-least-once guaranteed delivery for everything?"

**Interviewer:** "Transactional notifications (order shipped, password reset)
must be delivered. Marketing campaigns can have some loss."

**You:** "Last one — what's the scale? DAU, and roughly how many
notifications per user per day?"

**Interviewer:** "500M DAU, roughly 50 notifications per user per day
across all types."

### What you now know

```
Problem:       Multi-channel notification dispatch (push, email, SMS, in-app)
Sources:       Transactional, social, marketing
Consistency:   At-least-once for transactional; best-effort for marketing
Scale:         500M DAU × 50 = 25B notifications/day → 289K/s
Hard problem:  Handling three different delivery guarantees efficiently
```

The consistency split between transactional and marketing is the key insight.
Without this question, you'd either over-engineer the marketing path (adding
expensive exactly-once guarantees where they're not needed) or under-engineer
the transactional path (losing password reset emails). The clarification
question surfaced the most important architectural decision before you drew
a single box.

---

## Worked Example 3 — "Design Twitter's Search"

**Prompt:** *"Design Twitter search."*

### The clarification conversation

**You:** "Should this handle full search — users, tweets, hashtags — or
just tweet content search?"

**Interviewer:** "Focus on tweet content search."

**You:** "Time-bounded? Like do users expect to search tweets from 5 years
ago, or is it primarily recent content?"

**Interviewer:** "Both — recent results ranked first, but full history
should be searchable."

**You:** "Is the hard problem the indexing pipeline (getting tweets into
search quickly) or the query serving (returning results fast at scale)?"

**Interviewer:** "Both, but if you had to pick one, the freshness — tweets
should appear in search within seconds of being posted."

**You:** "One more — any relevance ranking beyond recency? Like engagement
signals, personalization, trending topic boosting?"

**Interviewer:** "Yes, engagement signals matter — a tweet with 10K likes
should rank above one with 2 likes for the same query."

### What you now know

```
Scope:         Tweet content search (not users, not hashtags)
History:       Full history, recency-ranked
Hard problem:  Freshness — tweets indexed within seconds of posting
Ranking:       Recency + engagement signals (not pure chronological)
```

The freshness requirement is the architectural constraint that drives
everything. It means you can't use a batch indexing pipeline — you need
a real-time Kafka → Elasticsearch pipeline. The engagement ranking means
you need to update the search index when engagement changes, not just when
a tweet is created. These two insights change the architecture significantly
from a naive "index tweets in Elasticsearch" approach.

---

## Worked Example 4 — "Design Uber's Surge Pricing"

**Prompt:** *"Design Uber's surge pricing."*

This is a tricky one because it sounds like it could be an ML problem, a
real-time computation problem, or a display/UX problem.

### The clarification conversation

**You:** "Is the focus on the algorithm that computes the surge multiplier,
the system that applies it to ride requests, or how it's displayed to users?"

**Interviewer:** "Let's focus on the computation — how does the system
know when to surge, and what multiplier to apply."

**You:** "Is this real-time computation on current supply and demand, or
ML-based prediction?"

**Interviewer:** "Both — there's a real-time component and a predictive
component. Start with real-time."

**You:** "Geographic granularity — is surge applied per city, per
neighborhood, or at a finer level?"

**Interviewer:** "Think of it as geo-zones — custom polygons, could be
as small as a few city blocks in dense areas."

**You:** "Latency requirement — when supply/demand changes, how quickly
does the surge price need to update?"

**Interviewer:** "Within 60 seconds is fine."

### What you now know

```
Problem:       Real-time surge multiplier computation per geo-zone
Input:         Current driver supply + rider demand per zone
Output:        Multiplier per zone, updated every 60 seconds
Hard problem:  Computing supply/demand across thousands of zones in real-time
               from a stream of 1.25M driver location updates/second
```

The 60-second update window is generous — this isn't a sub-second realtime
problem. The hard part is aggregating 1.25M driver location updates/second
into per-zone supply counts. This is a stream processing problem
(Kafka → Flink/Spark Streaming → Redis). The clarification turned a vague
"pricing system" into a specific stream aggregation problem.

---

## The Most Important Clarification Questions by Problem Type

Different problem types have different key questions. Have these ready.

### For storage/database problems
```
- What's the read:write ratio?
- How long is data retained?
- What's the primary access pattern (lookup by ID / range query / full scan)?
- Strong consistency or eventual acceptable?
```

### For real-time/streaming problems
```
- What's the maximum acceptable latency?
- At-least-once or exactly-once delivery?
- What happens if the consumer falls behind?
- Is the data ordered (per-user, per-topic) or unordered?
```

### For search problems
```
- Full-text or structured (faceted) search?
- How fresh must results be?
- Relevance ranking — what signals matter?
- Search history scope (recent only / full history)?
```

### For ML/recommendation problems
```
- Is this real-time inference or pre-computed?
- What's the freshness requirement on recommendations?
- What data is available (collaborative filtering / content-based / hybrid)?
- What's the consequence of a bad recommendation?
```

### For marketplace/e-commerce problems
```
- What's the consistency requirement on inventory?
- Is there a two-sided problem (seller + buyer) or one-sided?
- What's the peak load scenario?
- What happens if an order fails mid-flow?
```

### For communication/messaging problems
```
- 1:1 or group? What's the max group size?
- Real-time delivery or async (like email)?
- Message persistence — forever, or delete after delivery?
- Encryption requirements?
```

---

## What Good Clarification Looks Like vs. Bad

### Bad clarification (common mistakes)

**Asking too many questions:**
> "What's the DAU? What's the p99 latency requirement? What's the retention
> period? Do we need multi-region? What's the team size? What's the budget?
> How many engineers will maintain this?"

Asking 8 questions signals that you don't know which questions matter.
Ask 3–4 targeted questions, not everything you can think of.

**Asking questions you should know:**
> "What's a webhook? Should I use SQL or NoSQL?"

These are implementation knowledge questions, not scoping questions.
Clarification is about the problem, not your knowledge of solutions.

**Not writing down the answers:**
> *[Asks three questions, gets answers, starts drawing without writing
>   anything down]*

Write the requirements on the whiteboard as you get them. This shows you're
being systematic and gives both you and the interviewer a shared reference
point throughout the discussion.

### Good clarification

**Scoped questions that reveal constraints:**
> "Is the hard part getting content to users quickly, or is it managing
> concurrent edits? That changes the architecture significantly."

**Connecting the answer to the design:**
> "Got it — so consistency at checkout is the hard constraint. That tells
> me I need row-level locking on inventory, not an eventual consistency
> model. Let me write that down."

**Knowing when to stop:**
> "I think I have enough to start. Let me write down what I understand
> the requirements to be — tell me if I've missed anything important."

---

## The 5-Minute Conversion Template

Use this every time. Fill it in during clarification, show it to the
interviewer, confirm before drawing anything.

```
System: ________________________

Core behavior: ________________________
(What does the happy path look like in one sentence?)

Hard constraint: ________________________
(Latency / consistency / scale / cost — which one dominates?)

Peak scenario: ________________________
(What's the worst-case load? When does it happen?)

Out of scope: ________________________
(What are we explicitly not designing today?)

Key scenario to nail: ________________________
(The one failure mode or edge case the interviewer flagged)

Non-functional targets:
  DAU: _____ | Requests/s: _____ | Storage: _____ | Latency: _____
```

When this template is filled in, you have a concrete problem. Start designing.
