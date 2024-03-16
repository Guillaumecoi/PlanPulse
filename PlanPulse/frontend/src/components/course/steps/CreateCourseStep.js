import React, { useState } from 'react';
import { Button, TextField, Divider, Stack, Typography } from "@mui/material";
import { createCourseApi } from '../api'; // Make sure this path is correct

const CreateCourseStep = ({ onNext }) => {
  const [courseName, setCourseName] = useState('');
  const [studyPoints, setStudyPoints] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    try {
      await createCourseApi({ name: courseName, studyPoints });
      console.log('Course created successfully');
      onNext();
    } catch (error) {
      console.error('Failed to create course:', error);
      setError('Failed to create course. Please try again.');
    }
  };

  return (
    <Stack direction="column" justifyContent="center" alignItems="center" spacing={2} >
      <Typography variant="h4" gutterBottom component="div" sx={{ mb: '32px' }}>
        Create New Course
      </Typography>
      < Stack direction="row" spacing={2} >
        <TextField
          fullWidth
          required
          label="Course Name"
          variant="outlined"
          value={courseName}
          onChange={(e) => setCourseName(e.target.value)}
        />
        <TextField
          label="Study Points"
          variant="outlined"
          type="number"
          value={studyPoints}
          onChange={(e) => setStudyPoints(e.target.value)}
        />
      </Stack>
      
      <Divider />
      
      {error && (
        <Typography color="error">{error}</Typography>
      )}
      
      <Button variant="contained" color="primary" onClick={handleSubmit}>
        Create Course
      </Button>
    </Stack>
  );
};

export default CreateCourseStep;
