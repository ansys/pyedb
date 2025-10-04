import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Tabs,
  Tab,
} from '@mui/material';
import { Job, Partition, LocalResources, JobPoolStatus } from '../../types/job';
import { jobService } from '../../services/api';
import JobList from './JobList';
import CreateJobModal from './CreateJobModal';
import PartitionsPanel from '../cluster/PartitionsPanel';
import LocalResourcesPanel from '../resources/LocalResourcesPanel';
import JobPoolStatusPanel from './JobPoolStatusPanel';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`dashboard-tabpanel-${index}`}
      aria-labelledby={`dashboard-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const JobDashboard: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [partitions, setPartitions] = useState<Partition[]>([]);
  const [localResources, setLocalResources] = useState<LocalResources | null>(null);
  const [jobPoolStatus, setJobPoolStatus] = useState<JobPoolStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [createModalOpen, setCreateModalOpen] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [jobsData, partitionsData, resourcesData, poolStatusData] = await Promise.all([
        jobService.getJobs(),
        jobService.getPartitions(),
        jobService.getLocalResources(),
        jobService.getJobPoolStatus(),
      ]);
      setJobs(jobsData);
      setPartitions(partitionsData);
      setLocalResources(resourcesData);
      setJobPoolStatus(poolStatusData);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Set up polling for updates
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleCreateJob = async (jobData: any) => {
    try {
      await jobService.createJob(jobData);
      setCreateModalOpen(false);
      fetchData();
    } catch (error) {
      console.error('Error creating job:', error);
      throw error;
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  if (loading) {
    return <Typography>Loading...</Typography>;
  }

  return (
    <Box>
      {/* Overview Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <JobPoolStatusPanel status={jobPoolStatus} />
        </Grid>
        <Grid item xs={12} md={9}>
          <LocalResourcesPanel resources={localResources} />
        </Grid>
      </Grid>

      {/* Main Content Tabs */}
      <Paper sx={{ width: '100%' }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="dashboard tabs">
          <Tab label="Job Management" />
          <Tab label="Cluster Partitions" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <JobList
            jobs={jobs}
            onCreateJob={() => setCreateModalOpen(true)}
            onRefresh={fetchData}
          />
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <PartitionsPanel partitions={partitions} />
        </TabPanel>
      </Paper>

      <CreateJobModal
        open={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        onSubmit={handleCreateJob}
        availableResources={localResources}
      />
    </Box>
  );
};

export default JobDashboard;