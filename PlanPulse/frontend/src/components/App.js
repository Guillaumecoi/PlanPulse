import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { createRoot } from 'react-dom/client';
import { BrowserRouter as Router, Route, Routes, useLocation } from 'react-router-dom';
import HomePage from './HomePage';
import CreateCoursePage from './course/CreateCoursePage';
import SelectCoursePage from './course/SelectCoursePage';
import Navbar from './core/Navbar';
import LoginPage from './users/LoginPage';
import RegisterPage from './users/RegisterPage';
import ProfilePage from './users/ProfilePage';

const CheckLoginStatus = ({ setIsLoggedIn }) => {
    const location = useLocation();

    useEffect(() => {
        const checkLoginStatus = async () => {
            try {
                const response = await axios.get('/api/user/profile', {
                    withCredentials: true
                });
                if (response.status === 200 && response.data.username) {
                    setIsLoggedIn(true);
                } else {
                    setIsLoggedIn(false);
                }
            } catch (error) {
                console.error('Error checking login status:', error);
                setIsLoggedIn(false);
            }
        };

        checkLoginStatus();
    }, [location, setIsLoggedIn]);

    return null;
};

const App = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    return (
        <div style={{ display: 'flex', flexDirection: 'column', width: '100%' }}>
            <Router>
                <CheckLoginStatus setIsLoggedIn={setIsLoggedIn} />
                <Navbar isLoggedIn={isLoggedIn} />
                <Routes>
                    <Route path="/" element={<HomePage />} />
                    <Route path="/login" element={<LoginPage isLoggedIn={isLoggedIn} />} />
                    <Route path="/register" element={<RegisterPage isLoggedIn={isLoggedIn} />} />
                    <Route path="/profile" element={<ProfilePage />} />
                    <Route path="/course/create" element={<CreateCoursePage isLoggedIn={isLoggedIn} />} />
                    <Route path="/course" element={<SelectCoursePage isLoggedIn={isLoggedIn} />} />
                </Routes>
            </Router>
        </div>
    );
};

const appDiv = document.getElementById("app");
createRoot(appDiv).render(<App />);