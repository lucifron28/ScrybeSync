import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import Dashboard from './pages/Dashboard.jsx';
import NotesList from './pages/NotesList.jsx';
import NoteDetail from './pages/NoteDetail.jsx';

function App() {

  router = createBrowserRouter(
    [
      {
        path: '/',
        element: <Dashboard />,
      },
      {
        path: '/notes',
        element: <NotesList />,
      },
      {
        path: '/notes/:id',
        element: <NoteDetail />,
      },
    ]
  )

  return (
    <RouterProvider router={router} />
  )
}

export default App
