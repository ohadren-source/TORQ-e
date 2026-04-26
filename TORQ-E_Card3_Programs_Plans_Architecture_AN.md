# TORQ-E Card 3: Finding and Choosing Your Plan
## Architecture for Audience (AN)

---

## What is Card 3?

**Card 3 is your plan shopping experience.** It's the place where you discover what Medicaid plans are available to you, compare them side-by-side, and choose the one that works best for your life.

In New York, this is eMedNY. In California, this is the DHCS portal. No matter your state, it's your electronic enrollment system—the place where you find coverage.

---

## The Member Journey: How It Works

### Step 1: You Log In
You arrive at the platform and answer a simple question: **"What coverage do you need?"**

Three choices appear:
- *"I need new coverage"* — First time applying or coverage ended
- *"I already have Medicaid, changing plans"* — Switching from one plan to another
- *"I'm just browsing"* — Exploring options without committing

### Step 2: Eligibility Check
The system confirms: **"Are you eligible for Medicaid?"**

If you're already logged in, we already know your eligibility from your member profile. If not, a quick questionnaire asks:
- Your age
- Your income (approximate)
- Your citizenship status

**Real answer:** "Yes, you qualify for these programs: X, Y, Z"

Only programs you're actually eligible for appear next. This is important—we don't show you plans you can't use.

### Step 3: Browse Available Plans
You see a clean card view of plans available to you. Each card shows:

| What You See | Why It Matters |
|---|---|
| **Plan Name** | Which company runs this plan |
| **Monthly Cost** | What you pay per month (if anything) |
| **Your Copays** | What you pay when you use care (doctor visit = $X, specialist = $Y) |
| **Network Type** | HMO (pick one doctor, they coordinate), PPO (choose any doctor), or FFS (any provider) |
| **Key Benefits** | Checkmarks: Primary care ✓, Specialists ✓, Emergency ✓, Pharmacy ✓, Dental ✓, Vision ✓, Mental health ✓ |

**Total time to scan:** 30 seconds per plan

The card is clean. Not overwhelming. No unnecessary complexity.

### Step 4: Compare Plans (Optional)
Want to compare two or three plans side-by-side?

Click **"Compare"** and you see:
- Cost breakdown (what's the same, what's different)
- Network differences (which doctors are in each network)
- Benefit differences (which plan covers what)

Details are collapsed by default. If you want to expand and see more, click **"Show Details"**.

### Step 5: Dive Into Plan Details (Optional)
For the plan you're seriously considering, you can see:

- **Full Benefits List** — Everything this plan covers (primary care, specialists, emergency, hospitalization, pharmacy, mental health, dental, vision, long-term care, plus any special benefits)
- **Provider Directory** — Link to search: "Is my doctor in this network?"
- **Customer Service** — Phone number and hours if you have questions
- **Enrollment Deadline** — When you must enroll by
- **Terms & Conditions** — Legal details (expandable, collapsed by default)

### Step 6: Enroll
Ready to pick this plan?

Click **"Enroll"** and you're done.

Confirmation: **"You're enrolled. Your coverage starts [date]."**

---

## What Takes Time?

| Task | Time |
|---|---|
| Browsing plans | 2-3 minutes |
| Comparing 2-3 plans | 1-2 minutes |
| Reading detailed benefits (optional) | 2-5 minutes |
| **Enrollment** | 30 seconds |

**Total:** You can make a plan choice in **3-5 minutes** and enroll in **under 1 minute**.

---

## What About Your Data?

### What We Collect
- Your plan selections (which plans you looked at, which one you chose)
- When you looked at them
- What device you used (mobile, desktop, tablet)
- Whether you compared plans

### What We DON'T Collect
- Your name (stored separately, never shown in plan selection records)
- Your specific income (used only to check eligibility, then deleted)
- Your citizenship status (used only to check eligibility, then deleted)

### What Happens to Your Data
1. **Your plan choice is recorded** — Permanently logged so both you and the system can prove what you chose
2. **Reports are created** — Your choice is counted with all other members to show which plans are popular
3. **inauthenticity checks are performed** — Patterns are analyzed to catch suspicious activity (e.g., someone rapidly switching plans to commit inauthenticity)
4. **You can view your activity** — You can request "Show me what I've done on this system" anytime

### You Have Control
- You can change your plan during open enrollment
- You can request your activity history at any time
- You can ask what data is stored about you

---

## Progressive Disclosure: Find Complexity When You Need It

**By Default:** Card 3 is simple. You see only what you need to make a choice.

**If You Want Details:** Click **"More Information"**, **"Expand Details"**, or **"Learn More"** buttons to dig deeper.

- Collapsed: "This plan covers emergency care"
- Expanded: "This plan covers emergency care including ambulance, emergency room, trauma, urgent care, and out-of-network emergency (limited coverage)"

You control how much detail you see.

---

## Accessibility & Support

**Need help?**
- Hover over **"?"** icons for tooltips
- Call customer service (number in plan details)
- Request a specialist to help you enroll

**Language Support:**
- Available in English and Spanish
- Other languages by request

**Mobile Friendly:**
- Card 3 works exactly the same on phone, tablet, and desktop
- No separate "mobile version"—design is truly responsive

**Accessibility:**
- Screen reader compatible
- Keyboard navigation (no mouse required)
- High contrast mode available

---

## What If Something Goes Wrong?

### My Eligibility Changed
While you're browsing, your eligibility status changes (income went up, you got married, etc.).

**Solution:** The system re-checks your eligibility before you enroll. If you're no longer eligible, you see: "Your eligibility has changed. Here are plans you still qualify for."

### The Plan I Want Closed
The plan you were comparing is suddenly discontinued before you enroll.

**Solution:** At enrollment, the system checks if the plan still exists. If it's closed, you see: "This plan is no longer available. Similar plans you might like: [suggestions]"

### System Unavailable
The platform goes down for maintenance.

**Solution:** 
- If you're in the middle of browsing, you can see cached plan information
- You can complete your enrollment when the system is back up
- No coverage gap—everything is synchronized with the source system

### Plan Data Out of Sync
The plans showing on the platform don't match the official state list.

**Solution:** Automated daily reconciliation ensures accuracy. If a mismatch is found, we use the state's official data as the source of truth.

---

## Integration Points

### Card 3 ↔ Your Member Profile (Card 1)
- Card 3 checks your eligibility using your member profile
- Card 3 tells your member profile which plan you chose
- Your enrollment is processed in your member profile

### Card 3 ↔ Government Governance (Card 4)
- Anonymous reports are sent showing which plans members are choosing
- These help government monitor whether the system is healthy
- **You're not identified** — only: "Plan A: 50,000 selections, Plan B: 75,000 selections"

### Card 3 ↔ authenticity investigation (Card 5)
- Suspicious selection patterns are flagged (e.g., rapid plan switches, unusual timing)
- authenticity investigators review patterns to catch benefits inauthenticity
- **Your legitimate choices are safe** — only suspicious patterns are flagged

---

## Security: How Your Data Is Protected

**Encryption:**
- All data is encrypted as it travels to the platform
- Plan selection records are encrypted when stored

**Hashing:**
- Your name is never shown in plan selection records
- Your member ID is hashed (converted to code form)

**Immutable Logging:**
- Once a plan selection is recorded, it cannot be deleted or modified
- This protects you: your choice is permanent proof, cannot be undone by anyone
- This protects the system: no one can secretly change the records

**Access Control:**
- Only you can see your plan selections
- Government auditors can verify selections without seeing your name
- authenticity investigators can only see patterns that look suspicious

---

## Performance: Speed You Can Count On

**Plan list loads in:** <1 second

**Plan comparison appears in:** <500 milliseconds

**Details expand instantly:** All data is pre-loaded

**Mobile:** Responsive at all screen sizes

Peak times (9-11 AM, everyone shopping before work):
- 500,000 to 1,000,000 members browsing simultaneously
- System handles it without slowdown

---

## The Bottom Line

**Card 3 is designed around one principle: Your time is valuable.**

You're a busy person. You might be:
- Juggling work and kids
- Managing chronic illness
- Trying to understand healthcare for the first time
- Making this decision under time pressure

Card 3 respects that. **Browse → Compare → Choose → Done. In under 5 minutes.**

Complexity exists if you want it. Details are there if you need them. But by default, you see exactly what matters for your choice—nothing more.

---

**Your feedback matters.** If Card 3 is unclear, too slow, too complex, or missing something you need, tell us. This system exists for you.

---

End of Card 3 Architecture for Audience (AN)
