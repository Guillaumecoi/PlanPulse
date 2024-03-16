import React, { useState } from 'react';
import { Stepper, Step, StepLabel, Button, TextField, Grid, Card, CardHeader, CardContent, CardActions, Divider } from "@mui/material";
import CreateCourseStep from './steps/CreateCourseStep';

const steps = ['Course', 'Metrics'];

const CreateCoursePage = () => {
    const [activeStep, setActiveStep] = useState(0);
  
    const handleNext = () => {
      setActiveStep((prevActiveStep) => prevActiveStep + 1);
    };
  
    const renderStep = () => {
      switch (activeStep) {
        case 0:
          return <CreateCourseStep onNext={handleNext} />;
        // Define and render additional steps similarly
        default:
          return <div>Step not found</div>;
      }
    };

    return (
        <Grid container spacing={3} style={{ marginTop: '40px' }}>
            <Grid item xs></Grid>
            {/* get a wide box in the middel */}
            <Grid item xs={6}>
                <Card style={{ minHeight: '500px' }}>
                    <CardContent style={{ paddingTop: '60px', paddingBottom: '60px'}}>
                        {renderStep()}
                    </CardContent>
                </Card>        
            </Grid>
            <Grid item xs></Grid>
        </Grid>  
    );
};

export default CreateCoursePage;