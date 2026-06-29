const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Tickets APIs
export async function fetchTickets(params: {
  page?: number;
  limit?: number;
  status?: string;
  priority?: string;
  channel?: string;
  search?: string;
}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      query.append(key, String(value));
    }
  });

  const res = await fetch(`${API_BASE}/api/admin/tickets?${query}`);
  if (!res.ok) throw new Error('Failed to fetch tickets');
  const json = await res.json();
  return json.data;
}

export async function fetchTicketDetail(ticketId: string) {
  const res = await fetch(`${API_BASE}/api/admin/tickets/${ticketId}`);
  if (!res.ok) throw new Error('Failed to fetch ticket');
  const json = await res.json();
  return json.data;
}

export async function updateTicketStatus(ticketId: string, status: string) {
  const res = await fetch(`${API_BASE}/api/admin/tickets/${ticketId}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) throw new Error('Failed to update ticket');
  const json = await res.json();
  return json.data;
}

export async function fetchConversations(params: {
  page?: number;
  limit?: number;
  customer_id?: string;
  channel?: string;
  status?: string;
  ticket_id?: string;
  search?: string;
}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      query.append(key, String(value));
    }
  });

  const res = await fetch(`${API_BASE}/api/admin/conversations?${query}`);
  if (!res.ok) throw new Error('Failed to fetch conversations');
  const json = await res.json();
  return json.data;
}

export async function fetchConversationDetail(conversationId: string) {
  const res = await fetch(`${API_BASE}/api/admin/conversations/${conversationId}`);
  if (!res.ok) throw new Error('Failed to fetch conversation');
  const json = await res.json();
  return json.data;
}

export async function fetchConversationMessages(conversationId: string) {
  const res = await fetch(`${API_BASE}/api/admin/conversations/${conversationId}/messages`);
  if (!res.ok) throw new Error('Failed to fetch messages');
  const json = await res.json();
  return json.data;
}

export async function searchConversations(query: string, limit = 20) {
  const res = await fetch(`${API_BASE}/api/admin/conversations/search?q=${encodeURIComponent(query)}&limit=${limit}`);
  if (!res.ok) throw new Error('Failed to search conversations');
  const json = await res.json();
  return json.data;
}

export async function fetchCustomers(params: {
  page?: number;
  limit?: number;
  tier?: string;
  sentiment?: string;
  min_risk_score?: number;
  max_risk_score?: number;
  search?: string;
}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      query.append(key, String(value));
    }
  });

  const res = await fetch(`${API_BASE}/api/admin/customers?${query}`);
  if (!res.ok) throw new Error('Failed to fetch customers');
  const json = await res.json();
  return json.data;
}

export async function fetchCustomerDetail(customerId: string) {
  const res = await fetch(`${API_BASE}/api/admin/customers/${customerId}`);
  if (!res.ok) throw new Error('Failed to fetch customer');
  const json = await res.json();
  return json.data;
}

export async function fetchCustomerTickets(customerId: string) {
  const res = await fetch(`${API_BASE}/api/admin/customers/${customerId}/tickets`);
  if (!res.ok) throw new Error('Failed to fetch customer tickets');
  const json = await res.json();
  return json.data;
}

export async function fetchCustomerConversations(customerId: string) {
  const res = await fetch(`${API_BASE}/api/admin/customers/${customerId}/conversations`);
  if (!res.ok) throw new Error('Failed to fetch customer conversations');
  const json = await res.json();
  return json.data;
}

export async function searchCustomers(query: string, limit = 20) {
  const res = await fetch(`${API_BASE}/api/admin/customers/search?q=${encodeURIComponent(query)}&limit=${limit}`);
  if (!res.ok) throw new Error('Failed to search customers');
  const json = await res.json();
  return json.data;
}

// Observatory APIs
export async function fetchAgentHealth() {
  const res = await fetch(`${API_BASE}/api/admin/observatory/agents`);
  if (!res.ok) throw new Error('Failed to fetch agent health');
  const json = await res.json();
  return json.data;
}

export async function fetchAgentDetail(agentName: string) {
  const res = await fetch(`${API_BASE}/api/admin/observatory/agents/${agentName}`);
  if (!res.ok) throw new Error('Failed to fetch agent detail');
  const json = await res.json();
  return json.data;
}

export async function fetchExecutions(params: {
  page?: number;
  limit?: number;
  agent_id?: string;
  status?: string;
  ticket_id?: string;
}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      query.append(key, String(value));
    }
  });

  const res = await fetch(`${API_BASE}/api/admin/observatory/executions?${query}`);
  if (!res.ok) throw new Error('Failed to fetch executions');
  const json = await res.json();
  return json.data;
}

export async function fetchExecutionDetail(executionId: string) {
  const res = await fetch(`${API_BASE}/api/admin/observatory/executions/${executionId}`);
  if (!res.ok) throw new Error('Failed to fetch execution detail');
  const json = await res.json();
  return json.data;
}

export async function fetchExecutionTimeline(executionId: string) {
  const res = await fetch(`${API_BASE}/api/admin/observatory/executions/${executionId}/timeline`);
  if (!res.ok) throw new Error('Failed to fetch execution timeline');
  const json = await res.json();
  return json.data;
}

// Knowledge Base APIs
export async function fetchKnowledgeDocuments(params: {
  page?: number;
  limit?: number;
  type?: string;
  status?: string;
  search?: string;
}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      query.append(key, String(value));
    }
  });

  const res = await fetch(`${API_BASE}/api/admin/knowledge/documents?${query}`);
  if (!res.ok) throw new Error('Failed to fetch documents');
  const json = await res.json();
  return json.data;
}

export async function fetchKnowledgeStatistics() {
  const res = await fetch(`${API_BASE}/api/admin/knowledge/statistics`);
  if (!res.ok) throw new Error('Failed to fetch statistics');
  const json = await res.json();
  return json.data;
}

export async function fetchDocumentDetail(documentId: string) {
  const res = await fetch(`${API_BASE}/api/admin/knowledge/documents/${documentId}`);
  if (!res.ok) throw new Error('Failed to fetch document');
  const json = await res.json();
  return json.data;
}

export async function searchKnowledge(query: string, k = 5) {
  const res = await fetch(`${API_BASE}/api/admin/knowledge/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, k }),
  });
  if (!res.ok) throw new Error('Failed to search knowledge base');
  const json = await res.json();
  return json.data;
}

export async function uploadKnowledgeDocument(title: string, content: string, type = 'txt') {
  const res = await fetch(`${API_BASE}/api/admin/knowledge/upload`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, content, type }),
  });
  if (!res.ok) throw new Error('Failed to upload document');
  const json = await res.json();
  return json.data;
}

export async function deleteKnowledgeDocument(documentId: string) {
  const res = await fetch(`${API_BASE}/api/admin/knowledge/documents/${documentId}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete document');
  const json = await res.json();
  return json.data;
}

// Analytics APIs
export async function fetchAnalyticsOverview() {
  const res = await fetch(`${API_BASE}/api/admin/analytics/overview`);
  if (!res.ok) throw new Error('Failed to fetch analytics overview');
  const json = await res.json();
  return json.data;
}

export async function fetchTicketAnalytics() {
  const res = await fetch(`${API_BASE}/api/admin/analytics/tickets`);
  if (!res.ok) throw new Error('Failed to fetch ticket analytics');
  const json = await res.json();
  return json.data;
}

export async function fetchAgentAnalytics() {
  const res = await fetch(`${API_BASE}/api/admin/analytics/agents`);
  if (!res.ok) throw new Error('Failed to fetch agent analytics');
  const json = await res.json();
  return json.data;
}

// Email APIs
export async function fetchEmails(params: {
  page?: number;
  limit?: number;
  status?: string;
  search?: string;
}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      query.append(key, String(value));
    }
  });

  const res = await fetch(`${API_BASE}/api/admin/email?${query}`);
  if (!res.ok) throw new Error('Failed to fetch emails');
  const json = await res.json();
  return json.data;
}

export async function fetchEmailDetail(emailId: number) {
  const res = await fetch(`${API_BASE}/api/admin/email/${emailId}`);
  if (!res.ok) throw new Error('Failed to fetch email');
  const json = await res.json();
  return json.data;
}

export async function sendEmailReply(to: string, subject: string, body: string) {
  const res = await fetch(`${API_BASE}/api/admin/email/reply`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ to, subject, body }),
  });
  if (!res.ok) throw new Error('Failed to send reply');
  const json = await res.json();
  return json.data;
}

export async function retryEmail(emailId: number) {
  const res = await fetch(`${API_BASE}/api/admin/email/${emailId}/retry`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to retry email');
  const json = await res.json();
  return json.data;
}

// Activity APIs
export async function fetchActivity(params: {
  page?: number;
  limit?: number;
  type?: string;
  level?: string;
  search?: string;
}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      query.append(key, String(value));
    }
  });

  const res = await fetch(`${API_BASE}/api/admin/activity?${query}`);
  if (!res.ok) throw new Error('Failed to fetch activity');
  const json = await res.json();
  return json.data;
}
