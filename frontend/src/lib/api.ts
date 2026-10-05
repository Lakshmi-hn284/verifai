import {
  User,
  VaultDocument,
  Claim,
  Opportunity,
  EligibilityReport,
  DisclosurePreview,
  VerifiablePresentationPackage,
  CareerGaps,
  AuditLogItem,
  GraphData
} from '../types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class ApiClient {
  private token: string | null = null;

  constructor() {
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('verifai_token');
    }
  }

  setToken(token: string | null) {
    this.token = token;
    if (typeof window !== 'undefined') {
      if (token) {
        localStorage.setItem('verifai_token', token);
      } else {
        localStorage.removeItem('verifai_token');
      }
    }
  }

  getToken(): string | null {
    if (!this.token && typeof window !== 'undefined') {
      this.token = localStorage.getItem('verifai_token');
    }
    return this.token;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = this.getToken();
    const headers: Record<string, string> = {
      ...(options.headers as Record<string, string> || {}),
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    if (!(options.body instanceof FormData) && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    const json = await response.json();

    if (!response.ok || json.success === false) {
      const msg = json.error?.message || json.detail || 'An error occurred';
      throw new Error(msg);
    }

    return json.data as T;
  }

  // --- Auth & Profile ---
  async register(email: string, password: string, full_name: string) {
    const data = await this.request<{ access_token: string; refresh_token: string; user: User }>(
      '/auth/register',
      {
        method: 'POST',
        body: JSON.stringify({ email, password, full_name }),
      }
    );
    this.setToken(data.access_token);
    return data;
  }

  async login(email: string, password: string) {
    const data = await this.request<{ access_token: string; refresh_token: string; user: User }>(
      '/auth/login',
      {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      }
    );
    this.setToken(data.access_token);
    return data;
  }

  async logout() {
    try {
      await this.request('/auth/logout', { method: 'POST' });
    } finally {
      this.setToken(null);
    }
  }

  async getMe(): Promise<User> {
    return this.request<User>('/users/me');
  }

  async getDashboardSummary(): Promise<{
    documents_count: number;
    total_claims: number;
    verified_claims: number;
    opportunities_count: number;
    average_match_score: number;
    user: User;
  }> {
    return this.request('/users/me/dashboard');
  }

  // --- Documents Vault ---
  async uploadDocument(file: File): Promise<VaultDocument> {
    const formData = new FormData();
    formData.append('file', file);
    return this.request<VaultDocument>('/documents', {
      method: 'POST',
      body: formData,
    });
  }

  async listDocuments(): Promise<{ documents: VaultDocument[]; count: number }> {
    return this.request('/documents');
  }

  async getDocument(id: string): Promise<VaultDocument> {
    return this.request<VaultDocument>(`/documents/${id}`);
  }

  async deleteDocument(id: string): Promise<{ message: string }> {
    return this.request(`/documents/${id}`, { method: 'DELETE' });
  }

  // --- Credentials & Claims ---
  async listCredentials(): Promise<{ claims: Claim[]; count: number }> {
    return this.request('/credentials');
  }

  async createClaim(data: { category: string; field_name: string; field_value: any; issuer?: string }): Promise<Claim> {
    return this.request<Claim>('/credentials', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // --- Knowledge Graph ---
  async getKnowledgeGraph(): Promise<GraphData> {
    return this.request<GraphData>('/graph');
  }

  // --- Opportunities ---
  async createOpportunity(data: {
    title: string;
    organization: string;
    description: string;
    opportunity_type: string;
  }): Promise<Opportunity> {
    return this.request<Opportunity>('/opportunities', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async listOpportunities(): Promise<{ opportunities: Opportunity[]; count: number }> {
    return this.request('/opportunities');
  }

  async getOpportunity(id: string): Promise<Opportunity> {
    return this.request<Opportunity>(`/opportunities/${id}`);
  }

  // --- Eligibility & Reasoning ---
  async evaluateEligibility(opportunity_id: string): Promise<EligibilityReport> {
    return this.request<EligibilityReport>('/eligibility/evaluate', {
      method: 'POST',
      body: JSON.stringify({ opportunity_id }),
    });
  }

  async getLatestEvaluation(opportunity_id: string): Promise<EligibilityReport> {
    return this.request<EligibilityReport>(`/eligibility/opportunity/${opportunity_id}`);
  }

  // --- Privacy & Selective Disclosure ---
  async previewDisclosure(opportunity_id: string): Promise<DisclosurePreview> {
    return this.request<DisclosurePreview>(`/disclosures/preview/${opportunity_id}`);
  }

  async approveDisclosure(opportunity_id: string, allowed_attributes: string[]): Promise<VerifiablePresentationPackage> {
    return this.request<VerifiablePresentationPackage>('/disclosures/approve', {
      method: 'POST',
      body: JSON.stringify({
        opportunity_id,
        approved: true,
        allowed_attributes,
      }),
    });
  }

  async listPackages(): Promise<{ packages: any[]; count: number }> {
    return this.request('/disclosures/packages');
  }

  // --- Career Gap Analytics ---
  async getCareerGaps(): Promise<CareerGaps> {
    return this.request<CareerGaps>('/career/gaps');
  }

  // --- Audit Trail ---
  async getAuditLogs(): Promise<{ logs: AuditLogItem[]; count: number }> {
    return this.request('/audit/logs');
  }
}

export const api = new ApiClient();
