# AgentCore Project

This project was created with the [AgentCore CLI](https://github.com/aws/agentcore-cli).

## Project Structure

```
my-project/
├── AGENTS.md               # AI coding assistant context
├── agentcore/
│   ├── agentcore.json      # Project config (agents, memories, credentials, gateways, evaluators)
│   ├── aws-targets.json    # Deployment targets (account + region)
│   ├── .env.local          # Secrets — API keys (gitignored)
│   ├── .llm-context/       # TypeScript type definitions for AI assistants
│   │   ├── agentcore.ts    # AgentCoreProjectSpec types
│   │   └── aws-targets.ts  # Deployment target types
│   └── cdk/                # CDK infrastructure (@aws/agentcore-cdk)
├── app/                    # Agent application code
└── evaluators/             # Custom evaluator code (if any)
```

## Getting Started

### Prerequisites

- **Node.js** 20.x or later
- **Python 3.10+** and **uv** for Python agents ([install uv](https://docs.astral.sh/uv/getting-started/installation/))
- **AWS credentials** configured (`aws configure` or environment variables)
- **Docker** (only for Container build agents)

### Development

Run your agent locally:

```bash
agentcore dev
```

### Validate Invocation Input

Validate runtime invocation payloads before forwarding them to an agent framework. Keep user prompts typed as strings
and pass only prompt text to the agent.

### Deployment

Deploy to AWS:

```bash
agentcore deploy
```

## Commands

| Command | Description |
| --- | --- |
| `agentcore create` | Create a new AgentCore project |
| `agentcore add` | Add resources (agent, memory, credential, gateway, evaluator, policy) |
| `agentcore remove` | Remove resources |
| `agentcore dev` | Run agent locally with hot-reload |
| `agentcore deploy` | Deploy to AWS via CDK |
| `agentcore status` | Show deployment status |
| `agentcore invoke` | Invoke agent (local or deployed) |
| `agentcore logs` | View agent logs |
| `agentcore traces` | View agent traces |
| `agentcore eval` | Run evaluations |
| `agentcore package` | Package agent artifacts |
| `agentcore validate` | Validate configuration |
| `agentcore pause` | Pause a deployed agent |
| `agentcore resume` | Resume a paused agent |
| `agentcore fetch` | Fetch remote resource definitions |
| `agentcore import` | Import existing resources |
| `agentcore update` | Check for CLI updates |

## Configuration

Edit the JSON files in `agentcore/` to configure your project. See `agentcore/.llm-context/` for type definitions and validation constraints.

The project uses a **flat resource model** — agents, memories, credentials, gateways, evaluators, and policies are top-level arrays in `agentcore.json`. Resources are independent; agents discover memories and credentials at runtime via environment variables or SDK calls.

## Resources

| Resource | Purpose |
| --- | --- |
| Agent (runtime) | HTTP, MCP, or A2A agent deployed to AgentCore Runtime |
| Memory | Persistent context storage with configurable strategies |
| Credential | API key or OAuth credential providers |
| Gateway | MCP gateway that routes tool calls to targets |
| Gateway Target | Tool implementation (Lambda, MCP server, OpenAPI, Smithy, API Gateway) |
| Evaluator | Custom LLM-as-a-Judge or code-based evaluation |
| Online Eval Config | Continuous evaluation pipeline for deployed agents |
| Policy | Cedar authorization policies for gateway tools |

### Agent Types

- **Template agents**: Created from framework templates (Strands, LangChain/LangGraph, GoogleADK, OpenAI Agents, Autogen)
- **BYO agents**: Bring your own code with `agentcore add agent --type byo`
- **Import agents**: Import existing Bedrock agents with `agentcore import`

### Build Types

- **CodeZip**: Python source packaged as a zip and deployed directly to AgentCore Runtime
- **Container**: Docker image built via CodeBuild (ARM64), pushed to ECR, and deployed to AgentCore Runtime

## Documentation

- [AgentCore CLI](https://github.com/aws/agentcore-cli)
- [AgentCore CDK Constructs](https://github.com/aws/agentcore-l3-cdk-constructs)
- [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/)


# 🤖 AI Business Process Automation Agent

An AI-powered customer support automation agent built using **AWS Bedrock AgentCore Runtime**, **Amazon Bedrock**, and **Strands Agents**.

The agent analyzes customer support requests, uses business tools to retrieve information and make decisions, and provides an automated business-process response.

## 🚀 Use Case

### Customer Support Ticket Automation

A customer can ask:

> My order ORD1001 is late. Please check my order, determine the ticket priority, and recommend the appropriate support action.

The agent automatically:

1. Understands the customer request
2. Looks up the order
3. Determines ticket priority
4. Recommends the appropriate business action
5. Returns a clear customer response

## 🏗️ Architecture

```text
Customer Request
       ↓
AWS Bedrock AgentCore Runtime
       ↓
Strands Agent
       ↓
Amazon Nova 2 Lite
       ↓
Business Tools
 ┌─────────────────────────┐
 │ Order Lookup             │
 │ Ticket Priority Check    │
 │ Support Action           │
 └─────────────────────────┘
       ↓
Business Decision
       ↓
Customer Response
```

## 🛠️ Technologies

- Python
- AWS Bedrock
- Amazon Nova 2 Lite
- AWS Bedrock AgentCore Runtime
- Strands Agents
- AWS CLI
- Boto3
- MCP
- AWS Cloud infrastructure

## 🔧 Business Tools

### 1. Order Lookup

Checks the current status of a customer order.

Example:

```text
ORD1001 → Delayed → Expected delivery in 2 days
```

### 2. Ticket Priority

Analyzes the customer issue and determines:

```text
LOW
MEDIUM
HIGH
```

For example:

```text
"My order is late"
→ MEDIUM
```

### 3. Support Action

Recommends the appropriate business action based on the ticket priority.

Example:

```text
MEDIUM
→ Create a support ticket and notify the responsible team.
```

> Note: The current implementation demonstrates the business decision workflow. It does not connect to a real ticketing system.

## 📁 Project Structure

```text
BusinessProcessAgent/
│
├── agentcore/
│   ├── agentcore.json
│   ├── aws-targets.json
│   └── .gitignore
│
└── app/
    └── BusinessProcessAgent/
        ├── main.py
        ├── pyproject.toml
        ├── requirements.txt
        ├── README.md
        ├── uv.lock
        │
        └── model/
            ├── load.py
            └── __init__.py
```

## ⚙️ Setup

### 1. Configure AWS credentials

Make sure AWS CLI is configured:

```bash
aws configure
```

Verify:

```bash
aws sts get-caller-identity
```

### 2. Install dependencies

From the application directory:

```bash
cd app/BusinessProcessAgent
```

Install dependencies using the project's package configuration.

## 🧪 Local Testing

From the project root:

```bash
agentcore dev
```

Open the AgentCore agent inspector and send:

```text
My order ORD1001 is late. Please check my order, determine the ticket priority, and recommend the appropriate support action.
```

Expected workflow:

```text
lookup_order
       ↓
check_ticket_priority
       ↓
create_support_action
       ↓
Final response
```

## ☁️ Deployment

Deploy the agent to AWS:

```bash
agentcore deploy
```

Check deployment status:

```bash
agentcore status
```

The runtime should show:

```text
BusinessProcessAgent: Deployed - Runtime: READY
```

## 🔎 Example

### Customer Request

```text
My order ORD1001 is late. Please check my order,
determine the ticket priority, and recommend
the appropriate support action.
```

### Agent Result

```text
Order Status: Delayed
Expected Delivery: 2 days
Ticket Priority: Medium

Recommended Action:
Create a support ticket and notify the responsible team.
```

## 🎯 Project Objective

This project demonstrates how an AI agent can be deployed using **AWS Bedrock AgentCore Runtime** and integrated with business tools to automate a real-world customer support workflow.

## 👨‍💻 Skills Demonstrated

- AI Agent Development
- Amazon Bedrock
- AWS Bedrock AgentCore Runtime
- Strands Agents
- Tool Calling
- Business Process Automation
- Python
- AWS CLI
- Cloud Deployment
- Agent Workflow Design