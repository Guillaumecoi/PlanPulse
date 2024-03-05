import React, { useState, useEffect } from 'react';
import { AppBar, Toolbar, Typography, Button } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

const Navbar = ({ isLoggedIn }) => {
    return (
        <AppBar position="static" style={{ height: '60px' }}>
            <Toolbar>
                <Typography variant="h6" style={{ flexGrow: 1 }}>
                    PlanPulse
                </Typography>
                {isLoggedIn ? (
                    <>
                        <Button color="inherit" component={RouterLink} to="/profile">Profile</Button>
                        <Button color="inherit" component={RouterLink} to="/logout">Logout</Button>
                    </>
                ) : (
                    <>
                        <Button color="inherit" component={RouterLink} to="/login">Login</Button>
                        <Button color="inherit" component={RouterLink} to="/register">Register</Button>
                    </>
                )}
            </Toolbar>
        </AppBar>
    );
};

export default Navbar;