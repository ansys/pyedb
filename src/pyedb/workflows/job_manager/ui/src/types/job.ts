export interface Job {
  job_id: string;
  name: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
  created_at: string;
  updated_at: string;
  command: string;
  working_directory?: string;
  environment_variables?: Record<string, string>;
  resource_requirements?: {
    num_cpus?: number;
    num_gpus?: number;
    memory_mb?: number;
  };
  output?: string;
  error?: string;
  exit_code?: number;
}

export interface CreateJobRequest {
  name: string;
  command: string;
  working_directory?: string;
  environment_variables?: Record<string, string>;
  resource_requirements?: {
    num_cpus?: number;
    num_gpus?: number;
    memory_mb?: number;
  };
}

export interface Partition {
  name: string;
  total_nodes: number;
  available_nodes: number;
  total_cpus: number;
  available_cpus: number;
  total_gpus: number;
  available_gpus: number;
  total_memory_mb: number;
  available_memory_mb: number;
}

export interface LocalResources {
  available_cpus: number;
  available_gpus: number;
  available_memory_mb: number;
  total_cpus: number;
  total_gpus: number;
  total_memory_mb: number;
}

export interface JobPoolStatus {
  active_jobs: number;
  pending_jobs: number;
  completed_jobs: number;
  failed_jobs: number;
}