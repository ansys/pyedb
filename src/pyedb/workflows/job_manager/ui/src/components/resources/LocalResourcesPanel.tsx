import React from 'react';
import {
  Paper,
  Typography,
  Box,
  LinearProgress,
  Grid,
  Chip,
} from '@mui/material';
import ComputerIcon from '@mui/icons-material/Computer';   // CPU
import MemoryIcon from '@mui/icons-material/Memory';       // RAM
import DeveloperBoardIcon from '@mui/icons-material/DeveloperBoard'; // GPU-ish
import { LocalResources } from '../../types/job';

interface LocalResourcesPanelProps {
  resources: LocalResources | null;
}

const LocalResourcesPanel: React.FC<LocalResourcesPanelProps> = ({ resources }) => {
  if (!resources) return null;

  const getUtilizationPercentage = (used: number, total: number) => {
    return total > 0 ? (used / total) * 100 : 0;
  };

  const usedCpus = resources.total_cpus - resources.available_cpus;
  const usedGpus = resources.total_gpus - resources.available_gpus;
  const usedMemory = resources.total_memory_mb - resources.available_memory_mb;

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Local Resources (None Scheduler)
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <ComputerIcon sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="body1">CPU Cores</Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={getUtilizationPercentage(usedCpus, resources.total_cpus)}
              sx={{ mb: 1, height: 8, borderRadius: 4 }}
            />
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2" color="textSecondary">
                {usedCpus} / {resources.total_cpus} used
              </Typography>
              <Chip
                label={`${resources.available_cpus} available`}
                size="small"
                color="primary"
                variant="outlined"
              />
            </Box>
          </Box>
        </Grid>

        <Grid item xs={12} md={4}>
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <DeveloperBoardIcon  sx={{ mr: 1, color: 'secondary.main' }} />
              <Typography variant="body1">GPUs</Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={getUtilizationPercentage(usedGpus, resources.total_gpus)}
              sx={{ mb: 1, height: 8, borderRadius: 4 }}
              color="secondary"
            />
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2" color="textSecondary">
                {usedGpus} / {resources.total_gpus} used
              </Typography>
              <Chip
                label={`${resources.available_gpus} available`}
                size="small"
                color="secondary"
                variant="outlined"
              />
            </Box>
          </Box>
        </Grid>

        <Grid item xs={12} md={4}>
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <MemoryIcon  sx={{ mr: 1, color: 'success.main' }} />
              <Typography variant="body1">Memory</Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={getUtilizationPercentage(usedMemory, resources.total_memory_mb)}
              sx={{ mb: 1, height: 8, borderRadius: 4 }}
              color="success"
            />
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2" color="textSecondary">
                {Math.round(usedMemory / 1024)} / {Math.round(resources.total_memory_mb / 1024)} GB used
              </Typography>
              <Chip
                label={`${Math.round(resources.available_memory_mb / 1024)} GB available`}
                size="small"
                color="success"
                variant="outlined"
              />
            </Box>
          </Box>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default LocalResourcesPanel;