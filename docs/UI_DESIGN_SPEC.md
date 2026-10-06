# Customer Support AI — Frontend UI Design & Implementation Specification

## 1. Purpose

This document is the complete frontend specification for the Customer Support AI Agent.

The frontend must reproduce the visual style, layout, sections, interactions, and behavior shown in the provided UI reference image:

`docs/ui-reference.png`

This document is intended to be read by OpenCode and used as the implementation specification.

The frontend is a presentation layer for the existing Python/Groq AI agent backend.

### Core rule

The browser must communicate with our backend API.

The browser must NOT communicate directly with Groq.

```text
Customer
   ↓
Frontend UI
   ↓
Python Backend API
   ↓
Customer Support Agent
   ↓
Groq LLM
   ↓
RAG / Tools
   ↓
Python Backend
   ↓
Frontend
   ↓
Customer
```

Never expose the Groq API key in frontend code.

---

# 2. Reference Image

The visual reference is:

```text
docs/ui-reference.png
```

OpenCode must inspect this image before implementing the frontend.

The implementation should follow both:

1. This specification
2. The visual reference image

If there is a small visual difference between the image and this written specification, prefer the written specification for behavior and structure, and use the image for visual details.

---

# 3. Design Direction

The application is a modern AI customer-support SaaS dashboard.

The visual style should be:

- Modern
- Professional
- Clean
- Minimal
- Premium
- Friendly
- Trustworthy
- Spacious
- Easy to use
- Suitable for a real SaaS product

Avoid making the interface look like a generic ChatGPT clone.

The design should look like a real customer-support product.

---

# 4. Overall Layout

The desktop application uses three primary columns:

```text
┌────────────────────┬──────────────────────────────────────┬──────────────────────┐
│                    │                                      │                      │
│   LEFT SIDEBAR     │          MAIN CHAT AREA              │    RIGHT SIDEBAR     │
│                    │                                      │                      │
│   Brand            │   Greeting                          │    Agent Status      │
│   Navigation       │   Conversation                      │    Quick Actions     │
│                    │   Message Input                     │    Recent Topics     │
│   Agent Status     │                                      │    Help Card         │
│                    │                                      │                      │
└────────────────────┴──────────────────────────────────────┴──────────────────────┘
```

Recommended desktop proportions:

```text
Left sidebar:   280px
Main content:   flexible
Right sidebar:  360px
```

The page should occupy the full viewport height.

Recommended:

```css
min-height: 100vh;
```

Do not create horizontal scrolling.

---

# 5. Color Palette

Use a professional navy and blue color system.

## Primary Dark Navy

```text
#17233F
```

Use for:

- Left sidebar background
- Brand area
- Dark navigation area

## Primary Blue

```text
#2563EB
```

Use for:

- Active navigation item
- User message bubbles
- Primary buttons
- Send button
- Important interactive elements
- Accent icons

## Light Blue

```text
#EFF6FF
```

Use for:

- Quick action hover/soft backgrounds
- Help card
- Information areas
- Highlighted UI

## Very Light Background

```text
#F8FAFC
```

Use for:

- AI message bubbles
- Soft UI areas
- Secondary backgrounds
- Input-related areas where appropriate

## White

```text
#FFFFFF
```

Use for:

- Main page
- Cards
- Chat card
- Right sidebar
- Input backgrounds

## Border

```text
#E2E8F0
```

Use for:

- Card borders
- Input borders
- Dividers
- Subtle separators

## Primary Text

```text
#172554
```

Use for:

- Headings
- Important text
- Navigation labels
- Message text

## Secondary Text

```text
#64748B
```

Use for:

- Descriptions
- Timestamps
- Placeholder text
- Supporting text

## Success Green

```text
#22C55E
```

Use for:

- Online status
- AI Agent Online indicator

---

# 6. Typography

Use a modern sans-serif font.

Preferred:

```text
Inter
```

Fallback:

```text
system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif
```

## Page Heading

Example:

```text
Hello! 👋
```

Recommended:

```text
font-size: 28px–32px;
font-weight: 700;
color: #172554;
```

## Subtitle

Recommended:

```text
font-size: 16px;
font-weight: 400;
color: #64748B;
```

## Section Titles

Recommended:

```text
font-size: 18px–20px;
font-weight: 600–700;
```

## Normal Text

Recommended:

```text
font-size: 14px–16px;
```

## Small Text

Recommended:

```text
font-size: 12px;
```

Used for:

- Timestamps
- Secondary metadata
- Status details

---

# 7. Spacing System

Use a consistent spacing scale:

```text
4px
8px
12px
16px
20px
24px
32px
```

Avoid random spacing values unless required by the design.

Cards should generally have:

```text
20px–24px
```

internal padding.

---

# 8. Border Radius

Use consistent rounded corners.

Small controls:

```text
8px
```

Medium controls:

```text
10px
```

Cards:

```text
12px
```

Large containers:

```text
12px–14px
```

Do not make every element pill-shaped.

---

# 9. Left Sidebar

The left sidebar is dark navy.

Background:

```text
#17233F
```

Width:

```text
280px
```

It should occupy the full viewport height.

---

# 10. Left Sidebar — Brand Section

At the top of the sidebar display a support/headset icon.

Brand:

```text
Support AI
```

Tagline:

```text
Always here to help
```

Visual structure:

```text
[Headset Icon]  Support AI
                Always here to help
```

Brand name:

- White
- Bold
- Approximately 24px

Tagline:

- Light blue/gray
- Approximately 14px

The headset icon should use the primary blue accent.

---

# 11. Left Sidebar — Navigation

The sidebar contains four navigation items.

## Navigation Item 1 — Chat

Icon:

```text
Message / Chat
```

Label:

```text
Chat
```

This item is active by default.

Active background:

```text
#2563EB
```

Active text:

```text
#FFFFFF
```

Active item should have:

- Rounded corners
- Comfortable padding
- White icon
- White label
- Blue background

---

## Navigation Item 2 — Knowledge Base

Icon:

```text
Book / BookOpen
```

Label:

```text
Knowledge Base
```

Inactive style:

- Transparent background
- Light text
- Light icon

---

## Navigation Item 3 — Support Tickets

Icon:

```text
Ticket
```

Label:

```text
Support Tickets
```

Inactive style.

---

## Navigation Item 4 — Settings

Icon:

```text
Settings / Gear
```

Label:

```text
Settings
```

Inactive style.

---

# 12. Sidebar Navigation Behavior

Navigation items should be interactive.

On hover:

- Slight background highlight
- Smooth transition
- Cursor changes to pointer

On active:

- Blue background
- White icon
- White text

Recommended transition:

```text
150ms–200ms ease
```

Do not implement full separate pages for these sections unless required by the existing application.

For Version 1, the Chat screen is the primary functional screen.

---

# 13. Left Sidebar — Bottom Agent Status

At the bottom of the sidebar display:

```text
● AI Agent Online
  Ready to assist you
```

Green status dot:

```text
#22C55E
```

Primary text:

```text
AI Agent Online
```

Secondary text:

```text
Ready to assist you
```

The status should remain visually anchored near the bottom of the sidebar.

---

# 14. Main Content Area

The main content is white.

It contains:

1. Greeting
2. Subtitle
3. Main chat card

The center area should have comfortable horizontal and vertical spacing.

---

# 15. Main Header

Display:

```text
Hello! 👋
```

Then:

```text
I'm your AI customer support assistant. Ask me anything about your orders, products, refunds, or account.
```

Heading:

```text
28px–32px
font-weight: 700
color: #172554
```

Subtitle:

```text
16px
color: #64748B
```

---

# 16. Main Chat Card

The chat conversation belongs inside a large card.

Card:

```css
background: #FFFFFF;
border: 1px solid #E2E8F0;
border-radius: 12px;
```

Use a subtle shadow.

Suggested:

```css
box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
```

The chat card should occupy most of the center content height.

The conversation area should be scrollable when messages become numerous.

The message composer remains accessible at the bottom.

---

# 17. User Message Bubble

User messages appear on the right.

Example:

```text
Where is my order #12345?
```

Style:

```text
background: #2563EB
color: #FFFFFF
```

Maximum width:

```text
approximately 70%
```

The bubble should have rounded corners.

Add:

- User avatar/icon
- Timestamp
- Read/delivery indicator if appropriate

Example:

```text
                           ┌───────────────────────────┐
                           │ Where is my order #12345? │
                           │                  10:24 AM ✓│
                           └───────────────────────────┘
                                                   [User]
```

---

# 18. AI Message Bubble

AI messages appear on the left.

Use a circular AI/robot avatar.

The avatar should use:

- Blue icon
- White or very light circular background

AI bubble background:

```text
#F8FAFC
```

Text:

```text
#17233F
```

Example:

```text
[AI] ┌──────────────────────────────────────────────┐
     │ Your order #12345 is currently on its way! 🚚│
     │                                              │
     │ Order Number: 12345                          │
     │ Status: Out for delivery                     │
     │ Estimated Delivery: April 26, 2025           │
     │ Tracking Number: 1Z999AA10123456784          │
     │                                              │
     │ You can track your package using the         │
     │ tracking number above on the courier's       │
     │ website.                                     │
     └──────────────────────────────────────────────┘
```

---

# 19. AI Response Formatting

The chat UI must support formatted AI responses.

Support:

- Paragraphs
- Line breaks
- Bold text
- Lists
- Links when returned safely by backend
- Code only if necessary

Example:

```text
Your order #12345 is currently on its way! 🚚

Order Number: 12345
Status: Out for delivery
Estimated Delivery: April 26, 2025
Tracking Number: 1Z999AA10123456784

You can track your package using the tracking number above
on the courier's website.
```

Important values can use:

```text
font-weight: 600;
```

Do not make the entire response bold.

---

# 20. Conversation Example

The initial demo conversation can visually contain:

### User

```text
Where is my order #12345?
```

### AI

```text
Your order #12345 is currently on its way! 🚚

Order Number: 12345
Status: Out for delivery
Estimated Delivery: April 26, 2025
Tracking Number: 1Z999AA10123456784

You can track your package using the tracking number above
on the courier's website. Let me know if you need anything else!
```

### User

```text
Can I change the delivery address?
```

### AI

```text
Yes, you can change the delivery address, but only before
the order is out for delivery. Since your order is already
out for delivery, address changes are not possible at this stage.

If you need further assistance, you can also contact our
support team, and they'll be happy to help.
```

These are only UI examples.

Do not hard-code fake order data into production behavior.

Actual responses must come from the backend agent.

---

# 21. Message Composer

At the bottom of the chat card create a message input.

Visual structure:

```text
┌────────────────────────────────────────────────────────────┐
│ 📎   Type your message...                            [Send]│
└────────────────────────────────────────────────────────────┘
```

---

# 22. Attachment Button

Use a paperclip icon.

Color:

```text
#64748B
```

It should be visually subtle.

If attachment functionality is not implemented in Version 1, the icon can remain a non-functional visual element or be disabled.

Do not pretend attachments work if the backend does not support them.

---

# 23. Message Input

Placeholder:

```text
Type your message...
```

Background:

```text
#FFFFFF
```

Border:

```text
#E2E8F0
```

Text:

```text
#172554
```

Placeholder:

```text
#64748B
```

Input should support:

- Typing
- Enter to send
- Shift + Enter for newline
- Disabled state while request is being submitted if appropriate

---

# 24. Send Button

Primary blue:

```text
#2563EB
```

Use a paper-plane/send icon.

Icon:

```text
#FFFFFF
```

Rounded corners.

Hover:

- Slightly darker blue
- Smooth transition

Disabled:

- Muted appearance
- Not clickable

---

# 25. Right Sidebar

The right sidebar contains stacked cards.

Recommended width:

```text
360px
```

Background:

```text
#FFFFFF
```

Cards are separated by consistent vertical spacing.

---

# 26. Right Sidebar — Agent Status Card

Title:

```text
Support AI Agent
```

Show robot/avatar icon.

Status:

```text
● Online
```

Green dot:

```text
#22C55E
```

Description:

```text
I can help you with:
orders, tracking, refunds, account
issues, and more.
```

Card:

```css
background: #FFFFFF;
border: 1px solid #E2E8F0;
border-radius: 12px;
```

---

# 27. Right Sidebar — Quick Actions

Title:

```text
Quick Actions
```

Provide these five actions:

## Action 1

Icon:

```text
Truck
```

Text:

```text
Track My Order
```

## Action 2

Icon:

```text
RefreshCw
```

Text:

```text
Request a Refund
```

## Action 3

Icon:

```text
MapPin
```

Text:

```text
Change Delivery Address
```

## Action 4

Icon:

```text
FileText
```

Text:

```text
View Return Policy
```

## Action 5

Icon:

```text
Headset
```

Text:

```text
Contact Human Support
```

---

# 28. Quick Action Styling

Each action is a horizontal rounded control.

Default:

```text
background: #F8FAFC
```

Hover:

```text
background: #EFF6FF
```

Icon:

```text
#2563EB
```

Text:

```text
#17233F
```

Each button should:

- Have consistent height
- Have an icon on the left
- Have text next to the icon
- Fill the card width
- Be keyboard accessible
- Have hover and focus states

---

# 29. Quick Action Behavior

Version 1 should keep these actions simple.

Possible behavior:

```text
Track My Order
→ Send/prepopulate a relevant chat question

Request a Refund
→ Send/prepopulate refund-related question

Change Delivery Address
→ Send/prepopulate address-change question

View Return Policy
→ Ask the agent about the return policy

Contact Human Support
→ Show human-support information or create a support request
```

Do not invent backend functionality that does not exist.

If a backend action is not implemented, the frontend should not falsely indicate that the action completed.

---

# 30. Recent Topics Card

Title:

```text
Recent Topics
```

Show recent conversations/topics.

Example:

```text
◷ Order #12345 - Tracking
  2 min ago

◷ Refund Process
  12 min ago

◷ Account Login Issue
  25 min ago
```

Use a clock/history icon.

Topic:

```text
#172554
```

Timestamp:

```text
#64748B
```

The list should be visually clean and compact.

---

# 31. Help Card

At the bottom of the right sidebar show a soft information card.

Background:

```text
#EFF6FF
```

Icon:

```text
Lightbulb
```

Title:

```text
Need more help?
```

Description:

```text
Type your question in the chat or
use the quick actions above.
```

Title should use the primary blue.

---

# 32. Icons

Use one consistent icon library.

Recommended:

```text
Lucide Icons
```

Useful icons:

```text
Headphones
MessageCircle
BookOpen
Ticket
Settings
Bot
User
Truck
RefreshCw
MapPin
FileText
Headset
Clock3
Paperclip
Send
Lightbulb
```

Do not mix icon libraries with different visual styles.

Use consistent stroke width.

---

# 33. Responsive Design

The design must be responsive.

## Desktop

Display all three columns:

```text
Left Sidebar + Main Chat + Right Sidebar
```

## Tablet

Possible layout:

```text
Left Sidebar + Main Chat
```

Right sidebar can collapse or move below the chat.

## Mobile

Display the main chat.

Navigation becomes a mobile menu/drawer.

Right sidebar becomes:

- Collapsible
- Drawer
- Or stacked content below the chat

Choose the simplest implementation compatible with the existing frontend architecture.

Never allow horizontal page scrolling.

---

# 34. Loading State

When waiting for the backend:

Display an AI typing indicator.

Example:

```text
[AI]  ● ● ●
```

or:

```text
AI is thinking...
```

Use a subtle animation.

Do not freeze the interface.

The input should be handled appropriately while a request is in progress.

---

# 35. Error State

If the backend fails, display:

```text
Sorry, I couldn't process your request right now.
Please try again.
```

Do NOT expose:

- API keys
- Stack traces
- Python exceptions
- Internal server paths
- Environment variables
- Backend implementation details

to the user.

Log technical errors on the backend instead.

---

# 36. Empty Chat State

If no messages exist:

```text
Hello! 👋

How can I help you today?

Try asking about:
```

Suggested prompts:

```text
Track my order
What is your refund policy?
How do I return a product?
Contact support
```

Clicking a suggestion should populate or send the corresponding question.

---

# 37. Accessibility

The UI should be accessible.

Requirements:

- Keyboard navigation
- Visible focus states
- Buttons must have accessible labels
- Inputs must have labels or appropriate aria-labels
- Sufficient text contrast
- Do not rely only on color to communicate state
- Interactive elements should be actual buttons/links
- Images should have meaningful alt text where appropriate

---

# 38. Animation

Keep animations subtle.

Use:

```text
150ms–250ms
```

for:

- Hover
- Focus
- Button transitions
- Sidebar interactions
- Message appearance

Do not use excessive animations.

The product should feel professional.

---

# 39. Frontend Architecture

Use reusable components.

Suggested conceptual structure:

```text
frontend/
└── src/
    ├── components/
    │   ├── Sidebar/
    │   │   ├── Sidebar
    │   │   ├── Brand
    │   │   └── Navigation
    │   │
    │   ├── Chat/
    │   │   ├── ChatHeader
    │   │   ├── ChatWindow
    │   │   ├── MessageBubble
    │   │   ├── TypingIndicator
    │   │   └── MessageInput
    │   │
    │   ├── RightPanel/
    │   │   ├── AgentStatus
    │   │   ├── QuickActions
    │   │   ├── RecentTopics
    │   │   └── HelpCard
    │   │
    │   └── common/
    │       ├── Card
    │       └── Icon
    │
    ├── pages/
    │   └── ChatPage
    │
    ├── services/
    │   └── api
    │
    └── styles/
        └── globals
```

Adapt this structure to the existing project.

Do not create unnecessary abstractions.

Do not duplicate components.

---

# 40. Backend Integration

The frontend should communicate with a backend endpoint.

Conceptually:

```text
POST /chat
```

Example request:

```json
{
  "message": "What is your refund policy?"
}
```

Example response:

```json
{
  "response": "Our refund policy is..."
}
```

The exact endpoint and request/response shape must be determined by inspecting the existing backend.

Do NOT invent a new API if an existing API already exists.

---

# 41. API Layer

Create a small frontend API/service layer.

Example conceptual flow:

```text
MessageInput
     ↓
ChatPage
     ↓
api.sendMessage()
     ↓
Backend
     ↓
Response
     ↓
ChatWindow
```

Do not put API request code inside every UI component.

Centralize backend communication.

---

# 42. Security

NEVER put this in frontend source code:

```text
GROQ_API_KEY
LLM_API_KEY
gsk_...
```

The Groq key belongs only in backend environment configuration.

Correct:

```text
Browser
  ↓
Python Backend
  ↓
Groq
```

Incorrect:

```text
Browser
  ↓
Groq directly
```

---

# 43. Data and Business Logic

The frontend must not implement:

- RAG
- Embedding generation
- Vector search
- Tool execution
- Agent reasoning
- Groq API calls
- Knowledge ingestion

Those belong to the backend.

The frontend is responsible for:

- Displaying conversations
- Capturing user input
- Sending requests
- Showing loading states
- Showing errors
- Rendering AI responses
- Providing UI navigation/actions

---

# 44. Do Not Hard-Code Fake Business Data

The reference image contains example order information.

That information is for visual demonstration only.

Do not make the production agent claim that:

```text
Order #12345
```

actually exists.

Do not hard-code fake tracking numbers or delivery dates into business logic.

Demo content can be used only for the initial visual state if clearly treated as sample data.

Real answers must come from the backend/knowledge base/tools.

---

# 45. Chat State

The frontend should maintain a message list.

Conceptually:

```text
messages = [
  {
    role: "user",
    content: "Where is my order?"
  },
  {
    role: "assistant",
    content: "Your order is..."
  }
]
```

Use the existing frontend framework's appropriate state management.

Do not introduce Redux or another large state-management library unless the existing project actually needs it.

For Version 1, simple component/application state is preferred.

---

# 46. Auto Scroll

When a new message arrives:

- Scroll the conversation toward the latest message.
- Avoid aggressively forcing scroll if the user is manually reading older messages.
- Keep the latest response visible.

---

# 47. Keyboard Behavior

Message input:

```text
Enter
```

should send the message.

```text
Shift + Enter
```

should create a newline.

Do not submit an empty message.

Trim whitespace before sending.

---

# 48. Button States

Buttons must have:

## Default

Normal appearance.

## Hover

Subtle visual change.

## Focus

Visible keyboard focus ring.

## Disabled

Muted appearance and no interaction.

## Loading

Show an appropriate loading state when the action is waiting for the backend.

---

# 49. Frontend Performance

Keep the frontend lightweight.

Avoid unnecessary dependencies.

Do not add a large UI framework if simple CSS/components can implement the design.

Optimize images and static assets.

Do not introduce complicated state management for Version 1.

---

# 50. Recommended Implementation Order

Implement in this exact general order:

```text
1. Inspect existing repository
2. Identify frontend framework
3. Identify existing backend API
4. Create overall page layout
5. Build left sidebar
6. Build main header
7. Build chat card
8. Build user message component
9. Build AI message component
10. Build message composer
11. Build right sidebar
12. Build agent status card
13. Build quick actions
14. Build recent topics
15. Build help card
16. Add responsive layout
17. Add loading state
18. Add error state
19. Connect chat to existing backend API
20. Test real Groq-backed responses
21. Polish spacing/typography/colors
22. Verify accessibility
23. Verify no secrets are exposed
```

---

# 51. Do Not Add These Features Yet

Version 1 frontend should NOT add:

- Authentication
- Payment UI
- Admin dashboard
- CRM dashboard
- Voice chat
- Video
- Multi-agent visualization
- Complex analytics
- Notifications system
- WebSocket infrastructure unless already required
- File uploads unless backend supports them
- Full ticket management system
- User profile management
- Dark mode
- Theme builder
- Complex animation system

Keep Version 1 focused.

---

# 52. Definition of Done — Frontend

The frontend is considered complete when:

- [ ] Three-column desktop layout works
- [ ] Left sidebar matches the design
- [ ] Brand section exists
- [ ] Navigation exists
- [ ] Chat is the active section
- [ ] AI online status exists
- [ ] Main greeting exists
- [ ] Chat card exists
- [ ] User messages render on the right
- [ ] AI messages render on the left
- [ ] AI avatar exists
- [ ] Message timestamps render
- [ ] Message input works
- [ ] Send button works
- [ ] Enter sends messages
- [ ] Shift+Enter creates newline
- [ ] Loading state exists
- [ ] Error state exists
- [ ] Right agent status card exists
- [ ] Quick actions exist
- [ ] Recent topics exist
- [ ] Help card exists
- [ ] Responsive behavior exists
- [ ] Keyboard accessibility works
- [ ] No Groq API key is exposed to the browser
- [ ] Frontend communicates with backend
- [ ] Real backend response appears in chat
- [ ] Visual design follows this specification
- [ ] No unnecessary dependencies are added
- [ ] Existing backend functionality is not unnecessarily rewritten

---

# 53. OpenCode Instructions

OpenCode MUST read:

```text
CONSTITUTION.md
docs/UI_DESIGN_SPEC.md
docs/ui-reference.png
```

before implementing the frontend.

First inspect the existing repository.

Determine:

1. Current frontend framework
2. Current backend framework
3. Existing API endpoints
4. Existing project structure
5. Existing dependencies
6. Existing styling approach

Do NOT blindly create a new frontend stack if one already exists.

Do NOT rewrite working backend code just to make the UI work.

Do NOT expose API keys.

Do NOT hard-code business logic into the frontend.

Do NOT implement the entire project in one giant file.

Use small reusable components.

Follow the project's existing architecture where reasonable.

---

# 54. OpenCode Planning Requirement

Before writing code, provide a short implementation plan containing:

```text
1. Existing frontend stack
2. Existing backend API
3. Files that need to be created
4. Files that need to be modified
5. Components to create
6. API integration approach
7. Responsive strategy
8. Any dependency that must be added
9. Any architectural concern
```

Do not modify code during this planning step.

After the plan is approved, implement incrementally.

---

# 55. OpenCode Implementation Rule

Implement the frontend in small milestones.

Recommended milestones:

```text
Milestone 1:
Static UI layout

Milestone 2:
Chat state and message rendering

Milestone 3:
Backend API connection

Milestone 4:
Loading/error states

Milestone 5:
Responsive/accessibility polish

Milestone 6:
Final visual polish
```

After each milestone:

1. Run the application
2. Check for errors
3. Test the relevant functionality
4. Report what changed
5. Continue only when the milestone is stable

---

# 56. Final Design Summary

The final visual hierarchy must be:

```text
┌───────────────────────────────────────────────────────────────────────────┐
│                           CUSTOMER SUPPORT AI                            │
├──────────────────┬───────────────────────────────────────┬────────────────┤
│                  │                                       │                │
│   SUPPORT AI     │ Hello! 👋                            │ Support AI     │
│                  │                                       │ Agent          │
│   Chat           │ I'm your AI customer support...      │                │
│   Knowledge Base │                                       │ ● Online       │
│   Support Tickets│ ┌─────────────────────────────────┐ │                │
│   Settings       │ │                                 │ │ Quick Actions  │
│                  │ │ User message                    │ │                │
│                  │ │                                 │ │ Track Order    │
│                  │ │ AI response                     │ │ Refund         │
│                  │ │                                 │ │ Address        │
│                  │ │ User message                    │ │ Return Policy  │
│                  │ │                                 │ │ Human Support  │
│                  │ │ AI response                     │ │                │
│                  │ │                                 │ │ Recent Topics │
│                  │ └─────────────────────────────────┘ │                │
│                  │                                     │ Need help?     │
│   ● AI Online    │ [📎 Type your message...     Send] │                │
└──────────────────┴───────────────────────────────────────┴────────────────┘
```

The finished product should feel like a polished, production-quality AI customer-support SaaS interface while remaining simple enough for a portfolio project and easy to understand and maintain.

---

# 57. Final Instruction

Build the UI from this specification and the provided reference image.

Prioritize:

```text
Correctness
   ↓
Understandability
   ↓
Reusability
   ↓
Visual quality
   ↓
Polish
```

Do not sacrifice clean architecture for visual similarity.

The frontend should be a clean, reusable presentation layer over the Customer Support AI backend.
