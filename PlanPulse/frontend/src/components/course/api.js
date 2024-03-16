import axios from 'axios';

function getCsrfToken() {
    const csrfTokenCookie = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='));
    return csrfTokenCookie ? decodeURIComponent(csrfTokenCookie.split('=')[1]) : null;
}

const csrfToken = getCsrfToken();
axios.defaults.headers.post['X-CSRFToken'] = csrfToken;

axios.defaults.withCredentials = true;
const API_BASE_URL = '/api/course'; 

// Course Management
export const createCourseApi = async (courseData) => {
    return axios.post(`${API_BASE_URL}/create`, courseData, { withCredentials: true });
};

export const listCoursesApi = async () => {
  return axios.get(`${API_BASE_URL}`);
};

export const updateCourseApi = async (id, courseData) => {
  return axios.patch(`${API_BASE_URL}/${id}`, courseData);
};

export const deleteCourseApi = async (id) => {
  return axios.delete(`${API_BASE_URL}/${id}`);
};
