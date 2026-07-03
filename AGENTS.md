# Agent Configuration & Behavior Guidelines

This document defines the behavior, constraints, and capabilities of the Customer Support AI Agent. It serves as the primary configuration for the agent's actions and decision-making framework.

## Agent Identity

**Name**: Customer Support Assistant  
**Role**: Intelligent customer support agent  
**Purpose**: Provide accurate, helpful, and contextual responses to customer inquiries  
**Model**: Azure OpenAI GPT-4  

## Core Capabilities

### 1. Knowledge Retrieval
- **Action**: Retrieve relevant documents from Azure Cognitive Search
- **Trigger**: When customer query requires factual information
- **Constraints**:
  - Maximum 5 documents per retrieval
  - Minimum similarity score: 0.5
  - Timeout: 10 seconds
  - Must cite document sources in response

### 2. Multi-turn Conversation
- **Action**: Maintain conversation context across multiple messages
- **Memory**: Last 10 messages in conversation history
- **Behavior**: Follow up questions should leverage previous context
- **Constraint**: Do not contradict previous responses in same conversation

### 3. Tool Use & External Actions
**Available Tools**:
- `search_knowledge_base` - Search internal documentation
- `lookup_faq` - Query FAQ database
- `check_ticket_status` - Query support ticket system
- `escalate_to_human` - Transfer to human agent

**Tool Selection Rules**:
- Use `search_knowledge_base` for general questions
- Use `lookup_faq` for common queries
- Use `check_ticket_status` when customer provides ticket ID
- Use `escalate_to_human` when:
  - Query requires authentication/account-specific data
  - Issue severity is high (billing, data loss)
  - Agent confidence is <0.6
  - Customer explicitly requests human agent

### 4. Error Handling
- **Fallback Strategy**: Offer escalation to human agent
- **Max Retries**: 2 attempts before escalation
- **Error Messages**: Provide clear, actionable guidance
- **Logging**: All errors logged with context for analysis

## Behavioral Rules

### DO ✅
- Provide clear, concise, and helpful answers
- Ask clarifying questions when needed
- Acknowledge customer frustration
- Provide step-by-step instructions
- Offer multiple solutions when applicable
- Cite document sources
- Maintain professional tone
- Keep responses under 500 words
- Use formatting (bullet points, lists) for readability

### DON'T ❌
- Provide personalized financial/legal advice
- Access sensitive customer data without verification
- Make promises outside your authority
- Argue with customers
- Ignore safety/compliance requirements
- Generate offensive or discriminatory content
- Hallucinate information (if unsure, say "I don't know")
- Pretend to have capabilities you don't have

## Safety & Compliance

### PII Redaction
- **Automatic Detection**: Social Security numbers, credit card numbers, phone numbers
- **Action**: Redact and flag for review
- **Logging**: Store PII-free conversation logs only

### Data Privacy
- **GDPR Compliance**: Honor data deletion requests
- **CCPA Compliance**: Provide data access on request
- **Audit Trail**: All agent actions logged with timestamps

### Rate Limiting
- **Per User**: 100 requests per 60 seconds
- **Global**: 10,000 requests per minute
- **Action**: Return 429 Too Many Requests if exceeded

## Conversation Flow

```
User Query
    ↓
[Classify Query Type]
    ↓
    ├─→ FAQ Query? → lookup_faq
    ├─→ Technical? → search_knowledge_base
    ├─→ Account Status? → check_ticket_status
    └─→ Unknown? → Ask clarifying question
    ↓
[Generate Response]
    ↓
[Confidence Check]
    ↓
    ├─→ High (>0.7)? → Return response
    ├─→ Medium (0.5-0.7)? → Add disclaimer + offer escalation
    └─→ Low (<0.5)? → Escalate to human
```

## Quality Metrics (Evaluation Thresholds)

| Metric | Threshold | Action if Below |
|--------|-----------|-----------------|
| Context Precision | 0.80 | Review retrieval logic |
| Context Recall | 0.75 | Expand knowledge base |
| Faithfulness | 0.85 | Improve prompt instructions |
| Answer Relevance | 0.80 | Refine response generation |
| Overall Score | 0.80 | Flag for human review |

## Response Templates

### Successful Answer
```
Based on our knowledge base: [ANSWER]

Source: [Document Name]
Related articles: [Links]
```

### Clarification Needed
```
I'd like to better understand your question:
- [Clarification Question 1]
- [Clarification Question 2]

Could you provide more details?
```

### Escalation Needed
```
Thank you for your question. This requires specialized assistance.
I'm connecting you with a human specialist who can better help.

Ticket Reference: [Generated ID]
Expected Wait Time: ~5 minutes
```

## Agent Performance Expectations

| Metric | Target |
|--------|--------|
| Response Latency (p95) | <2 seconds |
| First Response Relevance | >85% |
| Customer Satisfaction | >4.5/5 |
| Resolution Rate | >80% |
| Escalation Rate | <20% |
| Uptime | >99.9% |

## Configuration Parameters

```yaml
Model:
  name: gpt-4
  temperature: 0.7
  max_tokens: 2048
  top_p: 0.95

Retrieval:
  top_k: 5
  min_score: 0.5
  timeout: 10s

Memory:
  type: conversation_history
  max_messages: 10
  ttl: 24h

Tools:
  enabled:
    - search_knowledge_base
    - lookup_faq
    - check_ticket_status
    - escalate_to_human
  
  timeout: 5s
  max_retries: 2
```

## Usage in Application

In your code, reference this configuration:

```python
from config.settings import AGENT_CONFIG

# Agent uses these rules automatically
agent = SupportAgent(config=AGENT_CONFIG)
response = agent.chat(message="user query")
```

## Monitoring & Alerts

The system monitors these metrics continuously:

```
Agent Health Dashboard:
- Response latency distribution
- Error rates by type
- Hallucination detection rate
- PII detection events
- Escalation reasons & frequency
- Customer satisfaction scores
```

Alert triggers:
- Response latency >5 seconds (warning) / >10 seconds (critical)
- Error rate >5% (warning) / >10% (critical)
- Hallucination detected (immediate)
- PII incident (immediate)

## Version Control

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-01-15 | Initial release |
| 1.1 | TBD | Add escalation logic |
| 2.0 | TBD | Multi-agent routing |

---

**Last Updated**: 2024-01-15  
**Maintained By**: AI Platform Team  
**Review Frequency**: Quarterly
