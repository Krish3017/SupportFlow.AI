// Mock data for SupportFlow AI Admin Panel
// Production-ready fixtures for development and testing

export type Priority = 'critical' | 'high' | 'medium' | 'low';
export type Status = 'new' | 'in_progress' | 'resolved' | 'escalated';
export type Sentiment = 'positive' | 'neutral' | 'negative';
export type Channel = 'email' | 'chat' | 'telegram';
export type CustomerTier = 'vip' | 'standard' | 'new';
export type AgentStatus = 'healthy' | 'degraded' | 'offline';
export type AgentType = 'intent' | 'customer_intelligence' | 'priority' | 'knowledge' | 'resolution' | 'escalation';

// ==================== TICKETS ====================

export interface Ticket {
  id: string;
  subject: string;
  customer: {
    id: string;
    name: string;
    email: string;
    avatar?: string;
  };
  priority: Priority;
  status: Status;
  channel: Channel;
  sentiment: Sentiment;
  intent: string;
  createdAt: Date;
  updatedAt: Date;
  currentAgent: AgentType | null;
  timeElapsed: number; // seconds
  assignee?: string;
}

export const mockTickets: Ticket[] = [
  {
    id: 'T001',
    subject: 'Billing issue - charged twice for subscription',
    customer: {
      id: 'C001',
      name: 'John Doe',
      email: 'john@example.com',
    },
    priority: 'critical',
    status: 'in_progress',
    channel: 'email',
    sentiment: 'negative',
    intent: 'billing_issue',
    createdAt: new Date('2026-06-28T10:30:00'),
    updatedAt: new Date('2026-06-28T10:32:15'),
    currentAgent: 'knowledge',
    timeElapsed: 135,
  },
  {
    id: 'T002',
    subject: 'How to reset my password?',
    customer: {
      id: 'C002',
      name: 'Jane Smith',
      email: 'jane@example.com',
    },
    priority: 'medium',
    status: 'in_progress',
    channel: 'chat',
    sentiment: 'neutral',
    intent: 'account_access',
    createdAt: new Date('2026-06-28T11:15:00'),
    updatedAt: new Date('2026-06-28T11:16:45'),
    currentAgent: 'resolution',
    timeElapsed: 105,
  },
  {
    id: 'T003',
    subject: 'Feature request: Dark mode for mobile app',
    customer: {
      id: 'C003',
      name: 'Alice Johnson',
      email: 'alice@example.com',
    },
    priority: 'low',
    status: 'resolved',
    channel: 'email',
    sentiment: 'positive',
    intent: 'feature_request',
    createdAt: new Date('2026-06-28T09:00:00'),
    updatedAt: new Date('2026-06-28T09:45:00'),
    currentAgent: null,
    timeElapsed: 2700,
  },
  {
    id: 'T004',
    subject: 'Account locked after too many login attempts',
    customer: {
      id: 'C004',
      name: 'Bob Wilson',
      email: 'bob@example.com',
    },
    priority: 'high',
    status: 'escalated',
    channel: 'chat',
    sentiment: 'negative',
    intent: 'technical_issue',
    createdAt: new Date('2026-06-28T08:30:00'),
    updatedAt: new Date('2026-06-28T08:50:00'),
    currentAgent: null,
    timeElapsed: 1200,
    assignee: 'Sarah Chen',
  },
  {
    id: 'T005',
    subject: 'Cannot upload files larger than 10MB',
    customer: {
      id: 'C005',
      name: 'Emma Davis',
      email: 'emma@example.com',
    },
    priority: 'medium',
    status: 'new',
    channel: 'email',
    sentiment: 'neutral',
    intent: 'technical_issue',
    createdAt: new Date('2026-06-28T12:00:00'),
    updatedAt: new Date('2026-06-28T12:00:00'),
    currentAgent: 'intent',
    timeElapsed: 30,
  },
  {
    id: 'T006',
    subject: 'Great product! Just wanted to say thanks',
    customer: {
      id: 'C006',
      name: 'Michael Brown',
      email: 'michael@example.com',
    },
    priority: 'low',
    status: 'resolved',
    channel: 'chat',
    sentiment: 'positive',
    intent: 'feedback',
    createdAt: new Date('2026-06-27T16:20:00'),
    updatedAt: new Date('2026-06-27T16:25:00'),
    currentAgent: null,
    timeElapsed: 300,
  },
];

// ==================== CUSTOMERS ====================

export interface Customer {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  tier: CustomerTier;
  sentiment: Sentiment;
  totalTickets: number;
  resolvedTickets: number;
  avgResponseTime: number; // minutes
  interactionFrequency: string;
  lastInteraction: Date;
  joinedDate: Date;
  riskScore: number; // 0-100
  lifetimeValue: number; // USD
  tags: string[];
}

export const mockCustomers: Customer[] = [
  {
    id: 'C001',
    name: 'John Doe',
    email: 'john@example.com',
    tier: 'vip',
    sentiment: 'negative',
    totalTickets: 12,
    resolvedTickets: 12,
    avgResponseTime: 3.1,
    interactionFrequency: '2x/week',
    lastInteraction: new Date('2026-06-28T10:30:00'),
    joinedDate: new Date('2024-01-15'),
    riskScore: 35,
    lifetimeValue: 12500,
    tags: ['Enterprise', 'High-Touch'],
  },
  {
    id: 'C002',
    name: 'Jane Smith',
    email: 'jane@example.com',
    tier: 'standard',
    sentiment: 'neutral',
    totalTickets: 5,
    resolvedTickets: 4,
    avgResponseTime: 5.2,
    interactionFrequency: '1x/month',
    lastInteraction: new Date('2026-06-28T11:15:00'),
    joinedDate: new Date('2025-08-20'),
    riskScore: 15,
    lifetimeValue: 2400,
    tags: [],
  },
  {
    id: 'C003',
    name: 'Alice Johnson',
    email: 'alice@example.com',
    tier: 'vip',
    sentiment: 'positive',
    totalTickets: 18,
    resolvedTickets: 18,
    avgResponseTime: 2.5,
    interactionFrequency: '3x/week',
    lastInteraction: new Date('2026-06-28T09:00:00'),
    joinedDate: new Date('2023-05-10'),
    riskScore: 5,
    lifetimeValue: 28000,
    tags: ['Champion', 'Beta Tester'],
  },
  {
    id: 'C004',
    name: 'Bob Wilson',
    email: 'bob@example.com',
    tier: 'standard',
    sentiment: 'negative',
    totalTickets: 8,
    resolvedTickets: 6,
    avgResponseTime: 8.3,
    interactionFrequency: '2x/month',
    lastInteraction: new Date('2026-06-28T08:30:00'),
    joinedDate: new Date('2025-11-03'),
    riskScore: 65,
    lifetimeValue: 3200,
    tags: ['At Risk'],
  },
  {
    id: 'C005',
    name: 'Emma Davis',
    email: 'emma@example.com',
    tier: 'new',
    sentiment: 'neutral',
    totalTickets: 1,
    resolvedTickets: 0,
    avgResponseTime: 0,
    interactionFrequency: 'First interaction',
    lastInteraction: new Date('2026-06-28T12:00:00'),
    joinedDate: new Date('2026-06-20'),
    riskScore: 20,
    lifetimeValue: 0,
    tags: ['New Customer'],
  },
];

// ==================== AGENTS ====================

export interface Agent {
  id: AgentType;
  name: string;
  description: string;
  status: AgentStatus;
  successRate: number; // percentage
  avgLatency: number; // seconds
  totalExecutions: number;
  failedExecutions: number;
  lastError?: string;
  cost: number; // USD
}

export const mockAgents: Agent[] = [
  {
    id: 'intent',
    name: 'Intent Agent',
    description: 'Classifies customer intent and sentiment',
    status: 'healthy',
    successRate: 99.2,
    avgLatency: 1.2,
    totalExecutions: 1247,
    failedExecutions: 10,
    cost: 2.34,
  },
  {
    id: 'customer_intelligence',
    name: 'Customer Intelligence',
    description: 'Retrieves customer context and history',
    status: 'healthy',
    successRate: 97.8,
    avgLatency: 2.1,
    totalExecutions: 1247,
    failedExecutions: 27,
    cost: 3.87,
  },
  {
    id: 'priority',
    name: 'Priority Agent',
    description: 'Assigns priority levels to tickets',
    status: 'healthy',
    successRate: 100,
    avgLatency: 0.8,
    totalExecutions: 1247,
    failedExecutions: 0,
    cost: 1.56,
  },
  {
    id: 'knowledge',
    name: 'Knowledge Agent',
    description: 'Retrieves information using RAG from Vector DB',
    status: 'degraded',
    successRate: 85.3,
    avgLatency: 4.5,
    totalExecutions: 892,
    failedExecutions: 131,
    lastError: 'Vector DB connection timeout (attempt 1/3)',
    cost: 8.92,
  },
  {
    id: 'resolution',
    name: 'Resolution Agent',
    description: 'Generates personalized customer responses',
    status: 'healthy',
    successRate: 94.1,
    avgLatency: 3.2,
    totalExecutions: 1184,
    failedExecutions: 70,
    cost: 12.45,
  },
  {
    id: 'escalation',
    name: 'Escalation Agent',
    description: 'Determines if human intervention is required',
    status: 'healthy',
    successRate: 98.5,
    avgLatency: 1.5,
    totalExecutions: 1184,
    failedExecutions: 18,
    cost: 2.01,
  },
];

// ==================== CONVERSATIONS ====================

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  agentType?: AgentType;
}

export interface Conversation {
  id: string;
  ticketId: string;
  customerId: string;
  channel: Channel;
  messages: Message[];
  status: Status;
  startedAt: Date;
  lastMessageAt: Date;
}

export const mockConversations: Conversation[] = [
  {
    id: 'CONV001',
    ticketId: 'T001',
    customerId: 'C001',
    channel: 'email',
    messages: [
      {
        id: 'M001',
        role: 'user',
        content: 'I was charged twice for my subscription this month. Can you help?',
        timestamp: new Date('2026-06-28T10:30:00'),
      },
      {
        id: 'M002',
        role: 'system',
        content: 'Intent Agent detected: billing_issue (confidence: 0.95)',
        timestamp: new Date('2026-06-28T10:30:05'),
        agentType: 'intent',
      },
      {
        id: 'M003',
        role: 'system',
        content: 'Customer Intelligence: VIP customer, 12 previous tickets, 100% resolved',
        timestamp: new Date('2026-06-28T10:30:08'),
        agentType: 'customer_intelligence',
      },
      {
        id: 'M004',
        role: 'system',
        content: 'Priority Agent assigned: CRITICAL',
        timestamp: new Date('2026-06-28T10:30:10'),
        agentType: 'priority',
      },
    ],
    status: 'in_progress',
    startedAt: new Date('2026-06-28T10:30:00'),
    lastMessageAt: new Date('2026-06-28T10:30:10'),
  },
  {
    id: 'CONV002',
    ticketId: 'T002',
    customerId: 'C002',
    channel: 'chat',
    messages: [
      {
        id: 'M005',
        role: 'user',
        content: 'How do I reset my password?',
        timestamp: new Date('2026-06-28T11:15:00'),
      },
      {
        id: 'M006',
        role: 'assistant',
        content: 'I can help you reset your password. You can do this by clicking on "Forgot Password" on the login page, or I can send you a reset link directly to your email. Which would you prefer?',
        timestamp: new Date('2026-06-28T11:15:45'),
        agentType: 'resolution',
      },
    ],
    status: 'in_progress',
    startedAt: new Date('2026-06-28T11:15:00'),
    lastMessageAt: new Date('2026-06-28T11:15:45'),
  },
];

// ==================== AGENT EXECUTIONS ====================

export interface AgentExecutionStep {
  agentId: AgentType;
  agentName: string;
  status: 'success' | 'failed' | 'running';
  latency: number;
  input: string;
  output: string;
  cost: number;
  error?: string;
}

export interface AgentExecution {
  id: string;
  ticketId: string;
  startTime: Date;
  endTime?: Date;
  totalLatency: number;
  totalCost: number;
  steps: AgentExecutionStep[];
  status: 'success' | 'failed' | 'running';
}

export const mockAgentExecutions: AgentExecution[] = [
  {
    id: 'EX001',
    ticketId: 'T001',
    startTime: new Date('2026-06-28T10:30:00'),
    endTime: new Date('2026-06-28T10:32:15'),
    totalLatency: 13.3,
    totalCost: 0.0191,
    status: 'running',
    steps: [
      {
        agentId: 'intent',
        agentName: 'Intent Agent',
        status: 'success',
        latency: 1.2,
        input: 'I was charged twice for my subscription',
        output: '{"intent": "billing_issue", "sentiment": "frustrated", "confidence": 0.95}',
        cost: 0.0023,
      },
      {
        agentId: 'customer_intelligence',
        agentName: 'Customer Intelligence',
        status: 'success',
        latency: 2.1,
        input: 'customer_id=C001',
        output: '{"tier": "VIP", "history": "12 tickets, 100% resolved"}',
        cost: 0.0031,
      },
      {
        agentId: 'priority',
        agentName: 'Priority Agent',
        status: 'success',
        latency: 0.8,
        input: 'intent="billing_issue", sentiment="frustrated"',
        output: '{"priority": "CRITICAL"}',
        cost: 0.0018,
      },
      {
        agentId: 'knowledge',
        agentName: 'Knowledge Agent',
        status: 'failed',
        latency: 4.5,
        input: 'query="How to handle double billing"',
        output: '',
        cost: 0.0042,
        error: 'Vector DB connection timeout',

      },
      {
        agentId: 'resolution',
        agentName: 'Resolution Agent',
        status: 'running',
        latency: 0,
        input: 'Generating response...',
        output: '',
        cost: 0,
      },
    ],
  },
];

// ==================== KNOWLEDGE BASE ====================

export interface KnowledgeDocument {
  id: string;
  title: string;
  type: 'pdf' | 'md' | 'txt' | 'url';
  status: 'indexed' | 'pending' | 'failed';
  chunks: number;
  retrievalCount: number;
  lastUpdated: Date;
  size: string;
}

export const mockKnowledgeDocuments: KnowledgeDocument[] = [
  {
    id: 'KB001',
    title: 'Billing and Payment Guide',
    type: 'pdf',
    status: 'indexed',
    chunks: 42,
    retrievalCount: 234,
    lastUpdated: new Date('2026-06-15'),
    size: '2.3 MB',
  },
  {
    id: 'KB002',
    title: 'Account Management FAQ',
    type: 'md',
    status: 'indexed',
    chunks: 18,
    retrievalCount: 156,
    lastUpdated: new Date('2026-06-20'),
    size: '145 KB',
  },
  {
    id: 'KB003',
    title: 'Troubleshooting Common Issues',
    type: 'md',
    status: 'indexed',
    chunks: 35,
    retrievalCount: 312,
    lastUpdated: new Date('2026-06-10'),
    size: '287 KB',
  },
  {
    id: 'KB004',
    title: 'Product Feature Documentation',
    type: 'url',
    status: 'pending',
    chunks: 0,
    retrievalCount: 0,
    lastUpdated: new Date('2026-06-28'),
    size: 'Unknown',
  },
  {
    id: 'KB005',
    title: 'API Integration Guide (Legacy)',
    type: 'pdf',
    status: 'failed',
    chunks: 0,
    retrievalCount: 0,
    lastUpdated: new Date('2026-06-25'),
    size: '5.8 MB',
  },
];

// ==================== ANALYTICS ====================

export interface AnalyticsMetric {
  label: string;
  value: number;
  change: number; // percentage change
  trend: 'up' | 'down' | 'stable';
}

export const mockAnalytics = {
  ticketsResolved: { label: 'Tickets Resolved', value: 47, change: 12, trend: 'up' as const },
  avgResponseTime: { label: 'Avg Response Time', value: 3.2, change: -0.5, trend: 'down' as const },
  escalationRate: { label: 'Escalation Rate', value: 8, change: -2, trend: 'down' as const },
  customerSatisfaction: { label: 'CSAT Score', value: 4.6, change: 0.3, trend: 'up' as const },
};

// ==================== ACTIVITY LOG ====================

export type ActivityType = 'system' | 'agent' | 'email' | 'security';

export interface ActivityLogEntry {
  id: string;
  type: ActivityType;
  level: 'info' | 'warning' | 'error' | 'critical';
  message: string;
  timestamp: Date;
  metadata?: Record<string, unknown>;
}

export const mockActivityLog: ActivityLogEntry[] = [
  {
    id: 'LOG001',
    type: 'email',
    level: 'info',
    message: 'Gmail API: New email received from john@example.com',
    timestamp: new Date('2026-06-28T10:30:00'),
  },
  {
    id: 'LOG002',
    type: 'system',
    level: 'info',
    message: 'Ticket #T001 created',
    timestamp: new Date('2026-06-28T10:30:01'),
  },
  {
    id: 'LOG003',
    type: 'agent',
    level: 'info',
    message: 'Intent Agent started (ticket_id=T001)',
    timestamp: new Date('2026-06-28T10:30:02'),
  },
  {
    id: 'LOG004',
    type: 'agent',
    level: 'info',
    message: 'Intent Agent completed (latency=1.2s)',
    timestamp: new Date('2026-06-28T10:30:03'),
  },
  {
    id: 'LOG005',
    type: 'agent',
    level: 'error',
    message: 'Vector DB: Connection timeout (attempt 1/3)',
    timestamp: new Date('2026-06-28T10:30:15'),
    metadata: { agent: 'knowledge', ticketId: 'T001' },
  },
  {
    id: 'LOG006',
    type: 'system',
    level: 'info',
    message: 'Vector DB: Reconnected successfully',
    timestamp: new Date('2026-06-28T10:30:16'),
  },
  {
    id: 'LOG007',
    type: 'security',
    level: 'warning',
    message: 'Failed login attempt from IP 192.168.1.100',
    timestamp: new Date('2026-06-28T09:45:00'),
  },
  {
    id: 'LOG008',
    type: 'email',
    level: 'info',
    message: 'Resend: Email sent to john@example.com',
    timestamp: new Date('2026-06-28T09:15:00'),
  },
];

// ==================== CHART DATA ====================

export const mockChartData = {
  ticketVolumeByDay: [
    { date: '2026-06-22', email: 12, chat: 8, telegram: 0 },
    { date: '2026-06-23', email: 15, chat: 10, telegram: 0 },
    { date: '2026-06-24', email: 18, chat: 12, telegram: 0 },
    { date: '2026-06-25', email: 14, chat: 15, telegram: 0 },
    { date: '2026-06-26', email: 20, chat: 18, telegram: 0 },
    { date: '2026-06-27', email: 16, chat: 14, telegram: 0 },
    { date: '2026-06-28', email: 11, chat: 9, telegram: 0 },
  ],
  sentimentDistribution: [
    { name: 'Positive', value: 45 },
    { name: 'Neutral', value: 35 },
    { name: 'Negative', value: 20 },
  ],
  agentPerformance: [
    { agent: 'Intent', successRate: 99.2, avgLatency: 1.2 },
    { agent: 'Customer Intel', successRate: 97.8, avgLatency: 2.1 },
    { agent: 'Priority', successRate: 100, avgLatency: 0.8 },
    { agent: 'Knowledge', successRate: 85.3, avgLatency: 4.5 },
    { agent: 'Resolution', successRate: 94.1, avgLatency: 3.2 },
    { agent: 'Escalation', successRate: 98.5, avgLatency: 1.5 },
  ],
  resolutionTimeDistribution: [
    { range: '0-5min', count: 28 },
    { range: '5-15min', count: 42 },
    { range: '15-30min', count: 18 },
    { range: '30min+', count: 12 },
  ],
};
