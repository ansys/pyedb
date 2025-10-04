import React from 'react';
import {
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Box,
} from '@mui/material';
import { Partition } from '../../types/job';

interface PartitionsPanelProps {
  partitions: Partition[];
}

const PartitionsPanel: React.FC<PartitionsPanelProps> = ({ partitions }) => {
  const getUtilizationColor = (utilization: number) => {
    if (utilization < 60) return 'success';
    if (utilization < 80) return 'warning';
    return 'error';
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Cluster Partitions
      </Typography>
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Partition Name</TableCell>
              <TableCell>Nodes</TableCell>
              <TableCell>CPU Cores</TableCell>
              <TableCell>GPUs</TableCell>
              <TableCell>Memory</TableCell>
              <TableCell>Utilization</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {partitions.map((partition) => {
              const cpuUtilization = ((partition.total_cpus - partition.available_cpus) / partition.total_cpus) * 100;
              const gpuUtilization = ((partition.total_gpus - partition.available_gpus) / partition.total_gpus) * 100;
              const memoryUtilization = ((partition.total_memory_mb - partition.available_memory_mb) / partition.total_memory_mb) * 100;

              return (
                <TableRow key={partition.name} hover>
                  <TableCell>
                    <Typography variant="body1" fontWeight="medium">
                      {partition.name}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box>
                      <Typography variant="body2">
                        {partition.available_nodes} / {partition.total_nodes} available
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box>
                      <Typography variant="body2">
                        {partition.available_cpus} / {partition.total_cpus} available
                      </Typography>
                      <Chip
                        label={`${cpuUtilization.toFixed(1)}%`}
                        color={getUtilizationColor(cpuUtilization)}
                        size="small"
                      />
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box>
                      <Typography variant="body2">
                        {partition.available_gpus} / {partition.total_gpus} available
                      </Typography>
                      <Chip
                        label={`${gpuUtilization.toFixed(1)}%`}
                        color={getUtilizationColor(gpuUtilization)}
                        size="small"
                      />
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box>
                      <Typography variant="body2">
                        {Math.round(partition.available_memory_mb / 1024)} / {Math.round(partition.total_memory_mb / 1024)} GB available
                      </Typography>
                      <Chip
                        label={`${memoryUtilization.toFixed(1)}%`}
                        color={getUtilizationColor(memoryUtilization)}
                        size="small"
                      />
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Chip
                        label={`CPU: ${cpuUtilization.toFixed(1)}%`}
                        variant="outlined"
                        size="small"
                      />
                      <Chip
                        label={`GPU: ${gpuUtilization.toFixed(1)}%`}
                        variant="outlined"
                        size="small"
                      />
                    </Box>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
        {partitions.length === 0 && (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="body1" color="textSecondary">
              No partitions available.
            </Typography>
          </Box>
        )}
      </TableContainer>
    </Paper>
  );
};

export default PartitionsPanel;