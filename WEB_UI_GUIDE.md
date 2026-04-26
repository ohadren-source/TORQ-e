# 🎨 WEB UI GUIDE: Landing Page & Card Flows

Complete guide to the TORQ-e web interface. This is what users actually interact with.

---

## LANDING PAGE: https://torq-e-production.up.railway.app/

The entry point. Shows all 5 cards with descriptions and links.

### What You See

**Header:**
- TORQ-e logo (Torque de Santa Tegra)
- "Medicaid Clarity System" subtitle
- CLARITY definition (Oxford-style)

**5 Cards (clickable):**
1. UMID — Member Eligibility
2. UPID — Provider Enrollment & Claims
3. WHUP — Plan Network Management
4. USHI — Government Stakeholder Operations
5. UBADA — Data Analyst & authenticity investigation

**Each card shows:**
- Card number (1-5)
- Acronym name
- Subtitle (what it does)
- Description (1-2 sentences)
- "For: [user type]" (who uses it)
- **NEW:** Acronym reference (e.g., "UMID: Universal Member Identification")

**Footer:**
- Version, system name, department
- Logo explanation: "Torque de Santa Tegra — The rotational force driving institutional clarity through complexity."

### Click a Card

Clicking any card takes you to that card's login page.

---

## CARD FLOWS: Login → Tutorial → Chat

Each card has the same three-page flow:

### Page 1: Login

**URL:** `/login-card1.html`, `/login-card2.html`, etc.

**What you see:**
- Card number and name
- "Welcome" message (role-specific)
- Login form (placeholder - not actually authenticated yet)
- "Continue" button
- "Tutorial" button (skip login, go to tutorial)

**Design:**
- Clean, accessible form
- Role-specific color and messaging
- Links to tutorial for users who want to learn first

### Page 2: Tutorial

**URL:** `/tutorial-card1.html`, etc.

**What you see:**
- Step-by-step guide for that card's user type
- Examples of what they can do
- Screenshots/mockups of features
- "Ready to try it?" button that goes to Chat
- "Back to Login" link

**Content (per card):**

**Card 1 (UMID) Tutorial:**
- For members/beneficiaries
- "How to check if you're covered"
- "How to find recertification dates"
- "How to upload documents"
- "How to ask Claude about your benefits"

**Card 2 (UPID) Tutorial:**
- For healthcare providers
- "How to verify your enrollment"
- "How to get help routing a claim"
- "How to check claim status"
- "How to ask Claude about claims"

**Cards 3-5:**
- Placeholder tutorials (coming soon)
- Brief description of what that card will do

### Page 3: Chat Interface

**URL:** `/chat-card1.html`, etc.

**What you see:**
- Chat window with messages
- Input box at bottom ("Ask a question...")
- Real-time streaming responses from Claude
- Message history
- Role-specific context (Claude knows who you are)

**How it works:**

1. User types question: "How do I know if I qualify for Medicaid?"
2. Click send
3. Request goes to `/api/chat/stream` (FastAPI endpoint)
4. Claude API processes with role-specific system prompt
5. Response streams back character-by-character
6. User sees text appear in real-time

**Example exchanges:**

**Card 1 (Member):**
- "Am I still covered?" → Claude checks confidence, explains status
- "When do I recertify?" → Claude gives date and countdown
- "Can I work and still get Medicaid?" → Claude explains income limits
- "I lost my job, what happens?" → Claude explains next steps

**Card 2 (Provider):**
- "Is this claim valid?" → Claude validates before submission
- "Which MCO gets this claim?" → Claude routes to correct plan
- "Where's my claim?" → Claude checks status
- "Why was this claim denied?" → Claude explains reason

**Cards 3-5:**
- Coming soon (placeholder chat for now)

---

## TECHNICAL DETAILS

### Files Structure

```
TORQ-e/
├── landing.html              # Main entry point
├── login-card1.html          # Card 1 login
├── login-card2.html          # Card 2 login
├── login-card3.html          # Card 3 login (placeholder)
├── login-card4.html          # Card 4 login (placeholder)
├── login-card5.html          # Card 5 login (placeholder)
├── chat-card1.html           # Card 1 chat interface
├── chat-card2.html           # Card 2 chat interface
├── chat-card3.html           # Card 3 chat (placeholder)
├── chat-card4.html           # Card 4 chat (placeholder)
├── chat-card5.html           # Card 5 chat (placeholder)
├── tutorial-card1.html       # Card 1 tutorial
├── tutorial-card2.html       # Card 2 tutorial
├── tutorial-card3.html       # Card 3 tutorial (placeholder)
├── tutorial-card4.html       # Card 4 tutorial (placeholder)
├── tutorial-card5.html       # Card 5 tutorial (placeholder)
└── static/
    └── branding/logo/TdST.png # TORQ-e logo (displays in tabs & pages)
```

### Chat Implementation

**Frontend (in chat-card*.html):**
```javascript
// When user sends message
async function callClaudeAPI(message, cardNumber, userType) {
  const response = await fetch('/api/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: message,
      userType: userType,  // 'Member', 'Provider', etc.
      cardNumber: cardNumber,  // 1, 2, 3, 4, or 5
      sessionId: sessionId  // Unique session ID
    })
  });

  // Stream response (Server-Sent Events)
  const reader = response.body.getReader();
  while (true) {
    const {done, value} = await reader.read();
    if (done) break;
    
    // Parse SSE format: "data: {json}\n\n"
    // Extract text and append to chat bubble
  }
}
```

**Backend (in chat.py):**
```python
@router.post("/api/chat/stream")
async def chat_stream(chat_msg: ChatMessage):
  # Get role-specific system prompt
  system_prompt = get_system_prompt(chat_msg.userType, chat_msg.cardNumber)
  
  # Get tools for this card (UMID has lookup, check_eligibility, etc.)
  tools = TOOLS_BY_CARD.get(chat_msg.cardNumber, [])
  
  # Stream from Claude with tools enabled
  # If Claude calls a tool, we execute it and send result back
  # Claude can then use that result in next response
```

### System Prompts (Claude instructions per card)

**Card 1 (Member):**
> "You are helping a Medicaid member understand their eligibility, benefits, and next steps. Be empathetic and clear about benefits and limitations. Explain complex eligibility rules in simple terms."

**Card 2 (Provider):**
> "You are helping a healthcare provider understand enrollment, claims, and reimbursement. Use clinical/healthcare terminology when appropriate. Focus on enrollment status, claims processing, and payment details."

**Cards 3-5:**
> Similar role-specific instructions

### Static Files (Images, CSS, etc.)

All assets served from `/static/` directory:

```
static/
└── branding/
    └── logo/
        └── TdST.png  # Torque de Santa Tegra logo
```

All HTML files reference assets as absolute paths:
```html
<img src="/static/branding/logo/TdST.png" alt="Logo">
```

This ensures assets work in production (Railway) without relative path issues.

---

## USER FLOWS

### Flow 1: Member (Card 1)

1. Visit landing page
2. Click Card 1 (UMID)
3. On login page, click "Tutorial" to learn (or click "Continue" to skip)
4. Read tutorial: "How to check if you're covered"
5. Click "Ready to try it?"
6. Chat interface appears
7. Type: "How do I know if I qualify for Medicaid?"
8. Claude responds instantly with accessibility-first explanation
9. Can ask follow-up questions

### Flow 2: Provider (Card 2)

1. Visit landing page
2. Click Card 2 (UPID)
3. Click "Tutorial" to learn how to route claims
4. Click "Ready to try it?"
5. Chat interface appears
6. Type: "I need to submit a claim for Emily Chen, where does it go?"
7. Claude checks provider enrollment, suggests correct MCO
8. Can ask about claim status, authenticity verification, etc.

### Flow 3: Curious User (Any Card)

1. Visit landing page
2. Read CLARITY definition
3. Click Card 5 (UBADA - data analysis)
4. Click tutorial (not implemented yet, placeholder)
5. Chat placeholder appears
6. Learns about what card will do when built

---

## BRANDING & ACCESSIBILITY

### CLARITY Definition

Displayed below TORQ-e title on landing page:

> **CLARITY** (n.) Etymology: The primary instrument of institutional understanding. Established April 6, 2026. Definition: The ability to perceive, communicate, and act on the full spectrum of probability and complexity rather than false absolutes. Characterized by: transparency, accessibility, and grounded reasoning.

### Logo

**Torque de Santa Tegra** — Displays in:
- Browser tab
- Landing page header
- Each card
- Footer with explanation

### Acronym References

On each card (bottom):
- UMID: Universal Member Identification
- UPID: Universal Provider Identification
- WHUP: Universal Health & Wellness Program
- USHI: Universal Stakeholder Identity
- UBADA: Universal Business/Data Analyst

### Color Scheme

- Primary: Green (#2d6a4f, #1e5631) — Trust, healthcare
- Accent: Orange (#f97316) — Energy, accessibility
- Text: Dark on light backgrounds for contrast
- Hover effects on cards for interactivity

### Accessibility

- Large, readable fonts (14px+ for body text)
- High color contrast (WCAG AA compliant)
- Keyboard navigable
- Semantic HTML structure
- Alt text on all images

---

## KNOWN LIMITATIONS

### Cards 3-5

Currently have placeholder pages:
- Login page works
- Tutorial page is stub ("Coming soon")
- Chat interface is stub (not connected to Claude yet)

**Next phase:** Build out Cards 3, 4, 5 with full functionality

### Authentication

Login pages are UI-only (no actual authentication yet).

**Next phase:** Integrate with NY DOH authentication system

### Tool Use

Card 1 and 2 have tools defined (lookup_member, check_eligibility, etc.) but execution is mocked.

**Next phase:** Connect to real NY DOH APIs

---

## TESTING THE UI

### Local Testing

```bash
# Start the API
python main.py

# Visit in browser
http://localhost:8000/
```

### Walkthrough

1. **Landing Page:** https://localhost:8000/
   - Verify all 5 cards appear
   - Verify CLARITY definition displays
   - Verify acronym references show

2. **Card 1 Login:** https://localhost:8000/login-card1.html
   - Click "Tutorial" → loads tutorial page
   - Click "Continue" → loads chat page

3. **Card 1 Tutorial:** https://localhost:8000/tutorial-card1.html
   - Read the guide
   - Click "Ready to try it?" → loads chat page

4. **Card 1 Chat:** https://localhost:8000/chat-card1.html
   - Type a question about Medicaid eligibility
   - Watch response stream in real-time
   - Try follow-up questions
   - Check that Claude knows you're a Member (not a Provider)

5. **Card 2 Chat:** https://localhost:8000/chat-card2.html
   - Type a question about provider enrollment
   - Check that Claude knows you're a Provider (different language, context)

### Debugging

If chat returns error:
```bash
curl http://localhost:8000/api/chat/health
```

Should return:
```json
{
  "status": "healthy",
  "claude_api_configured": true
}
```

If `claude_api_configured` is `false`, ANTHROPIC_API_KEY isn't set.

---

## NEXT PHASE ROADMAP

### Phase 1 (DONE ✅)
- ✅ Landing page with 5 cards
- ✅ Login pages for all 5 cards
- ✅ Tutorial pages (Cards 1-2 functional, 3-5 placeholder)
- ✅ Chat interfaces (Cards 1-2 functional, 3-5 placeholder)
- ✅ Claude AI integration with streaming
- ✅ Role-specific system prompts
- ✅ Production deployment on Railway

### Phase 2 (NEXT)
- [ ] Complete tutorial pages for Cards 3, 4, 5
- [ ] Connect Card 3, 4, 5 chat to Claude
- [ ] Add tool use for Cards 3, 4, 