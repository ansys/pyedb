import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  Chip,
} from '@mui/material';
import { Science, Dashboard } from '@mui/icons-material';

const Header: React.FC = () => {
  return (
    <AppBar position="static" elevation={2}>
      <Toolbar>
        <Science sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          PyEDB Job Manager
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Chip
            icon={<Dashboard />}
            label="Local Scheduler"
            variant="outlined"
            sx={{ color: 'white', borderColor: 'white' }}
          />
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;