import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useEffect } from 'react';
import ThemeProvider from './components/ThemeProvider';
import ProtectedRoute from './components/Auth/ProtectedRoute';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import useAuthStore from './store/authStore';
import { authService } from './services/authService';

function App() {
  const { setAuth, setLoading, isAuthenticated } = useAuthStore();

  useEffect(() => {
    const initAuth = async () => {
      try {
        setLoading(true);
        const response = await authService.refreshToken();
        setAuth({ username: 'User' }, response.access_token);
      } catch (error) {
        console.log('No valid session found');
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, [setAuth, setLoading]);

  return (
    <ThemeProvider>
      <Router>
        <Routes>
          {/* Public routes */}
          <Route path="/" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          
          {/* Protected routes */}
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            } 
          />
          
          {/* Catch all route */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
