import React from 'react';
import {
  Paper,
  Typography,
  Box,
  Grid,
  Chip,
} from '@mui/material';
import { PlayArrow, Schedule, Check, Error } from '@mui/icons-material';
import { JobPoolStatus } from '../../types/job';

interface JobPoolStatusPanelProps {
  status: JobPoolStatus | null;
}

const JobPoolStatusPanel: React.FC<JobPoolStatusPanelProps> = ({ status }) => {
  if (!status) return null;

  const totalJobs = status.active_jobs + status.pending_jobs + status.completed_jobs + status.failed_jobs;

  const statusItems = [
    { label: 'Active', count: status.active_jobs, color: 'primary', icon: <PlayArrow /> },
    { label: 'Pending', count: status.pending_jobs, color: 'warning', icon: <Schedule /> },
    { label: 'Completed', count: status.completed_jobs, color: 'success', icon: <Check /> },
    { label: 'Failed', count: status.failed_jobs, color: 'error', icon: <Error /> },
  ];

  return (
    <Paper sx={{ p: 3, height: '100%' }}>
      <Typography variant="h6" gutterBottom>
        Job Pool Status
      </Typography>
      <Box sx={{ textAlign: 'center', mb: 2 }}>
        <Typography variant="h4" color="primary" fontWeight="bold">
          {totalJobs}
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Total Jobs
        </Typography>
      </Box>
      <Grid container spacing={1}>
        {statusItems.map((item) => (
          <Grid item xs={6} key={item.label}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Chip
                icon={item.icon}
                label={`${item.count} ${item.label}`}
                color={item.color as any}
                variant="outlined"
                size="small"
                sx={{ width: '100%', justifyContent: 'flex-start' }}
              />
            </Box>
          </Grid>
        ))}
      </Grid>
    </Paper>
  );
};

export default JobPoolStatusPanel;