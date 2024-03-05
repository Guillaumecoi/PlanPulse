import React, { useState, useEffect } from 'react';
import { Container, Typography, Box, Card, CardContent, Avatar } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const ProfilePage = () => {
    const [user, setUser] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchProfile = async () => {
            const response = await fetch('/api/user/profile');
            // If the response status is not 200, navigate to the login page
            if (!response.ok) {  
                navigate('/login');
            }
            const data = await response.json();
            setUser(data);
        };

        fetchProfile();
    }, []);

    return (
        <Container component="main" maxWidth="md">
            <Card sx={{ marginTop: 8, display: 'flex', flexDirection: 'row', alignItems: 'center' }}>
                <Avatar sx={{ margin: 1, bgcolor: 'secondary.main', width: 80, height: 80 }}>
                    {user && user.username.charAt(0).toUpperCase()}
                </Avatar>
                <CardContent>
                    <Typography component="h1" variant="h5">
                        Profile Page
                    </Typography>
                    <Box sx={{ mt: 3 }}>
                        <Typography variant="body1">Username: {user && user.username}</Typography>
                        <Typography variant="body1">Email: {user && user.email}</Typography>
                    </Box>
                </CardContent>
            </Card>
        </Container>
    );
};

export default ProfilePage;