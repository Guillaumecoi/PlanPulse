import React from 'react';
import { AppBar, Toolbar, Typography, Button } from '@mui/material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';

const Navbar = ({ isLoggedIn }) => {
    const navigate = useNavigate();

    const handleLogout = async () => {
        const response = await fetch('/api/user/logout', { method: 'POST' });

        if (response.ok) {
            navigate('/');
        } else {
            console.error('Logout failed');
        }
    };

    return (
        <AppBar position="static" style={{ height: '60px' }}>
            <Toolbar>
                <Typography variant="h6" style={{ flexGrow: 1 }}>
                    PlanPulse
                </Typography>
                {isLoggedIn ? (
                    <>
                        <Button color="inherit" component={RouterLink} to="/profile">Profile</Button>
                        <Button color="inherit" onClick={handleLogout}>Logout</Button>
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