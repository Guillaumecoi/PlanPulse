import React, { Component } from 'react';
import { render } from 'react-dom';
import { BrowserRouter as Router, Route, Link, Routes } from 'react-router-dom';
import HomePage from './HomePage';
import CreateCoursePage from './CreateCoursePage';
import SelectCoursePage from './SelectCoursePage';

export default class App extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <Router>
                <Routes>
                    <Route path="/" element={<HomePage />} />
                    <Route path="/course/create" element={<CreateCoursePage />} />
                    <Route path="/course" element={<SelectCoursePage />} />
                </Routes>
            </Router>
        );
    }
}

const appDiv = document .getElementById("app");
render(<App />, appDiv);