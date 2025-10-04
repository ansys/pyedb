import axios from 'axios';
import { Job, CreateJobRequest, Partition, LocalResources, JobPoolStatus } from '../types/job';

// API base URL - relative since we're served from same domain
const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const jobService = {
  async getJobs(): Promise<Job[]> {
    const response = await api.get('/jobs');
    return response.data;
  },

  async getJob(jobId: string): Promise<Job> {
    const response = await api.get(`/jobs/${jobId}`);
    return response.data;
  },

  async createJob(jobData: CreateJobRequest): Promise<Job> {
    const response = await api.post('/jobs', jobData);
    return response.data;
  },

  async updateJob(jobId: string, jobData: Partial<Job>): Promise<Job> {
    const response = await api.put(`/jobs/${jobId}`, jobData);
    return response.data;
  },

  async deleteJob(jobId: string): Promise<void> {
    await api.delete(`/jobs/${jobId}`);
  },

  async getPartitions(): Promise<Partition[]> {
    const response = await api.get('/cluster/partitions');
    return response.data;
  },

  async getLocalResources(): Promise<LocalResources> {
    const response = await api.get('/resources/local');
    return response.data;
  },

  async getJobPoolStatus(): Promise<JobPoolStatus> {
    const response = await api.get('/job-pool/status');
    return response.data;
  },
};