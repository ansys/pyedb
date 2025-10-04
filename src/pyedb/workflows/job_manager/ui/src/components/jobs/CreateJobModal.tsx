import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Grid,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Typography,
} from '@mui/material';
import { LocalResources } from '../../types/job';

interface CreateJobModalProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (jobData: any) => Promise<void>;
  availableResources: LocalResources | null;
}

const CreateJobModal: React.FC<CreateJobModalProps> = ({
  open,
  onClose,
  onSubmit,
  availableResources,
}) => {
  const [formData, setFormData] = useState({
    name: '',
    command: '',
    working_directory: '',
    environment_variables: '',
    num_cpus: 1,
    num_gpus: 0,
    memory_mb: 1024,
  });
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const jobData = {
        name: formData.name,
        command: formData.command,
        working_directory: formData.working_directory || undefined,
        environment_variables: formData.environment_variables
          ? JSON.parse(formData.environment_variables)
          : undefined,
        resource_requirements: {
          num_cpus: formData.num_cpus,
          num_gpus: formData.num_gpus,
          memory_mb: formData.memory_mb,
        },
      };
      await onSubmit(jobData);
      setFormData({
        name: '',
        command: '',
        working_directory: '',
        environment_variables: '',
        num_cpus: 1,
        num_gpus: 0,
        memory_mb: 1024,
      });
    } catch (error) {
      console.error('Error submitting job:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = () => {
    setFormData({
      name: '',
      command: '',
      working_directory: '',
      environment_variables: '',
      num_cpus: 1,
      num_gpus: 0,
      memory_mb: 1024,
    });
    onClose();
  };

  const resourceValidation = {
    cpus: availableResources && formData.num_cpus > availableResources.available_cpus,
    gpus: availableResources && formData.num_gpus > availableResources.available_gpus,
    memory: availableResources && formData.memory_mb > availableResources.available_memory_mb,
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>Create New Job</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Job Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Command"
                value={formData.command}
                onChange={(e) => setFormData({ ...formData, command: e.target.value })}
                placeholder="e.g., python train_model.py --epochs 10"
                required
                multiline
                rows={2}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Working Directory (optional)"
                value={formData.working_directory}
                onChange={(e) => setFormData({ ...formData, working_directory: e.target.value })}
                placeholder="/path/to/working/directory"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Environment Variables (optional)"
                value={formData.environment_variables}
                onChange={(e) => setFormData({ ...formData, environment_variables: e.target.value })}
                placeholder='{"KEY": "value", "ANOTHER_KEY": "another_value"}'
                multiline
                rows={2}
                helperText="Enter as JSON object"
              />
            </Grid>

            {/* Resource Requirements */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Resource Requirements
              </Typography>
            </Grid>

            <Grid item xs={4}>
              <FormControl fullWidth error={resourceValidation.cpus ?? undefined}>
                <InputLabel>CPU Cores</InputLabel>
                <Select
                  value={formData.num_cpus}
                  label="CPU Cores"
                  onChange={(e) => setFormData({ ...formData, num_cpus: Number(e.target.value) })}
                >
                  {[1, 2, 4, 8, 16, 32].map(num => (
                    <MenuItem key={num} value={num}>
                      {num} core{num > 1 ? 's' : ''}
                    </MenuItem>
                  ))}
                </Select>
                {availableResources && (
                  <Typography variant="caption" color="textSecondary">
                    Available: {availableResources.available_cpus}
                  </Typography>
                )}
              </FormControl>
            </Grid>

            <Grid item xs={4}>
              <FormControl fullWidth error={resourceValidation.cpus ?? undefined}>
                <InputLabel>GPU Count</InputLabel>
                <Select
                  value={formData.num_gpus}
                  label="GPU Count"
                  onChange={(e) => setFormData({ ...formData, num_gpus: Number(e.target.value) })}
                >
                  {[0, 1, 2, 4, 8].map(num => (
                    <MenuItem key={num} value={num}>
                      {num} GPU{num !== 1 ? 's' : ''}
                    </MenuItem>
                  ))}
                </Select>
                {availableResources && (
                  <Typography variant="caption" color="textSecondary">
                    Available: {availableResources.available_gpus}
                  </Typography>
                )}
              </FormControl>
            </Grid>

            <Grid item xs={4}>
              <FormControl fullWidth error={resourceValidation.cpus ?? undefined}>
                <InputLabel>Memory (MB)</InputLabel>
                <Select
                  value={formData.memory_mb}
                  label="Memory (MB)"
                  onChange={(e) => setFormData({ ...formData, memory_mb: Number(e.target.value) })}
                >
                  {[1024, 2048, 4096, 8192, 16384, 32768, 65536].map(memory => (
                    <MenuItem key={memory} value={memory}>
                      {memory} MB
                    </MenuItem>
                  ))}
                </Select>
                {availableResources && (
                  <Typography variant="caption" color="textSecondary">
                    Available: {availableResources.available_memory_mb} MB
                  </Typography>
                )}
              </FormControl>
            </Grid>

            {/* Resource Validation Warnings */}
            {Object.values(resourceValidation).some(Boolean) && (
              <Grid item xs={12}>
                <Box sx={{ p: 2, bgcolor: 'warning.light', borderRadius: 1 }}>
                  <Typography variant="body2" color="warning.dark">
                    ⚠️ Resource request exceeds available capacity. Job may be queued.
                  </Typography>
                </Box>
              </Grid>
            )}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button
            type="submit"
            variant="contained"
            disabled={submitting}
          >
            {submitting ? 'Creating...' : 'Create Job'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default CreateJobModal;