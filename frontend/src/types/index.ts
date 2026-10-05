export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface Claim {
  id: string;
  user_id: string;
  document_id?: string;
  category: 'EDUCATION' | 'SKILL' | 'EXPERIENCE' | 'CERTIFICATE' | 'IDENTITY';
  field_name: string;
  field_value: any;
  confidence: number;
  page_number?: number;
  bounding_box?: BoundingBox;
  verification_status: string;
  issuer?: string;
  issued_date?: string;
  created_at: string;
}

export interface VaultDocument {
  id: string;
  filename: string;
  content_type: string;
  file_size_bytes: number;
  status: string;
  doc_type: string;
  sha256_hash: string;
  claims_count?: number;
  created_at: string;
  claims?: Claim[];
  extracted_metadata?: Record<string, any>;
}

export interface Requirement {
  type: string;
  field: string;
  operator: string;
  value: any;
  importance: 'REQUIRED' | 'PREFERRED';
  description: string;
}

export interface Opportunity {
  id: string;
  title: string;
  organization: string;
  description: string;
  opportunity_type: string;
  status: string;
  extracted_requirements: {
    requirements: Requirement[];
    count: number;
  };
  created_at: string;
}

export interface EvidenceInfo {
  claim_id: string;
  field_name: string;
  field_value: any;
  confidence: number;
  document_id?: string;
  document_name: string;
  page_number: number;
  bounding_box?: BoundingBox;
}

export interface EligibilityReport {
  id: string;
  opportunity_id: string;
  opportunity_title?: string;
  status: 'ELIGIBLE' | 'PARTIALLY_ELIGIBLE' | 'INELIGIBLE';
  match_score: number;
  satisfied_rules: Array<{
    rule: Requirement;
    status: string;
    evidence: EvidenceInfo;
  }>;
  partially_satisfied_rules: Array<{
    rule: Requirement;
    status: string;
    reason: string;
    evidence: EvidenceInfo;
  }>;
  missing_rules: Array<{
    rule: Requirement;
    status: string;
    reason: string;
  }>;
  evidence_map: Record<string, EvidenceInfo>;
  explanation_markdown: string;
  created_at: string;
}

export interface DisclosurePreview {
  opportunity_id: string;
  opportunity_title: string;
  organization: string;
  requested_attributes: Array<{
    attribute: string;
    category: string;
    value_preview: string;
    required_by: string;
    action: string;
  }>;
  redacted_attributes: Array<{
    attribute: string;
    category: string;
    reason: string;
    action: string;
  }>;
  disclosure_reduction_percentage: number;
}

export interface VerifiablePresentationPackage {
  package_id: string;
  opportunity_title: string;
  organization: string;
  generated_at: string;
  verifiable_claims: Array<{
    claim_id: string;
    category: string;
    field_name: string;
    field_value: any;
    confidence: number;
    verification_status: string;
    issuer: string;
  }>;
  redacted_count: number;
  package_hash: string;
  w3c_payload?: Record<string, any>;
}

export interface CareerGaps {
  total_opportunities_analyzed: number;
  user_skill_count: number;
  market_readiness_score: number;
  top_skill_gaps: Array<{
    skill: string;
    missing_in_opportunities: number;
    total_demanding_opportunities: number;
    gap_percentage: number;
    importance: string;
  }>;
}

export interface AuditLogItem {
  id: string;
  event_type: string;
  status: string;
  ip_address?: string;
  metadata_hash: string;
  details: Record<string, any>;
  created_at: string;
}

export interface GraphNode {
  id: string;
  label: string;
  title: string;
  group: string;
  properties: Record<string, string>;
}

export interface GraphEdge {
  from: string;
  to: string;
  label: string;
  relationship: string;
  properties: Record<string, string>;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  node_count: number;
  edge_count: number;
}
