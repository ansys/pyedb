import React from 'react';
import {
  Box,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  Typography,
  Toolbar,
} from '@mui/material';
import { Add, Refresh, Delete, Visibility } from '@mui/icons-material';
import { Job } from '../../types/job';
import { jobService } from '../../services/api';

interface JobListProps {
  jobs: Job[];
  onCreateJob: () => void;
  onRefresh: () => void;
}

const JobList: React.FC<JobListProps> = ({ jobs, onCreateJob, onRefresh }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED': return 'success';
      case 'RUNNING': return 'primary';
      case 'PENDING': return 'warning';
      case 'FAILED': return 'error';
      case 'CANCELLED': return 'default';
      default: return 'default';
    }
  };

  const handleDeleteJob = async (jobId: string) => {
    if (window.confirm('Are you sure you want to delete this job?')) {
      try {
        await jobService.deleteJob(jobId);
        onRefresh();
      } catch (error) {
        console.error('Error deleting job:', error);
      }
    }
  };

  return (
    <Box>
      <Toolbar sx={{ pl: { sm: 2 }, pr: { xs: 1, sm: 1 } }}>
        <Typography variant="h6" component="div" sx={{ flex: '1 1 100%' }}>
          Jobs ({jobs.length})
        </Typography>
        <Button
          startIcon={<Refresh />}
          onClick={onRefresh}
          sx={{ mr: 1 }}
        >
          Refresh
        </Button>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={onCreateJob}
        >
          New Job
        </Button>
      </Toolbar>

      <TableContainer component={Paper}>
        <Table sx={{ minWidth: 650 }} aria-label="jobs table">
          <TableHead>
            <TableRow>
              <TableCell>Job ID</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Command</TableCell>
              <TableCell>Resources</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Updated</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {jobs.map((job) => (
              <TableRow key={job.job_id} hover>
                <TableCell component="th" scope="row">
                  <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                    {job.job_id.slice(0, 8)}...
                  </Typography>
                </TableCell>
                <TableCell>{job.name}</TableCell>
                <TableCell>
                  <Chip
                    label={job.status}
                    color={getStatusColor(job.status) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Typography variant="body2" sx={{ fontFamily: 'monospace', maxWidth: 200 }}>
                    {job.command}
                  </Typography>
                </TableCell>
                <TableCell>
                  {job.resource_requirements && (
                    <Box>
                      {job.resource_requirements.num_cpus && `CPU: ${job.resource_requirements.num_cpus}`}
                      {job.resource_requirements.num_gpus && ` GPU: ${job.resource_requirements.num_gpus}`}
                      {job.resource_requirements.memory_mb && ` RAM: ${job.resource_requirements.memory_mb}MB`}
                    </Box>
                  )}
                </TableCell>
                <TableCell>
                  {new Date(job.created_at).toLocaleString()}
                </TableCell>
                <TableCell>
                  {new Date(job.updated_at).toLocaleString()}
                </TableCell>
                <TableCell>
                  <IconButton size="small" onClick={() => {/* TODO: View details */}}>
                    <Visibility />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => handleDeleteJob(job.job_id)}
                    color="error"
                  >
                    <Delete />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        {jobs.length === 0 && (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="body1" color="textSecondary">
              No jobs found. Create your first job to get started.
            </Typography>
          </Box>
        )}
      </TableContainer>
    </Box>
  );
};

export default JobList;