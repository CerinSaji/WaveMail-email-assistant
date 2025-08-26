import { useEffect, useState } from "react";

function App() {
  const [notifications, setNotifications] = useState([]);
  const [todos, setTodos] = useState([]);

  useEffect(() => {
    // Fetch Notifications
    fetch("http://localhost:8000/notifications?n=4")
      .then(res => res.json())
      .then(data => setNotifications(data.notifications || []))
      .catch(err => console.error("Error fetching notifications:", err));

    // Fetch To-Do List
    fetch("http://localhost:8000/todolist?n=2")
      .then(res => res.json())
      .then(data => setTodos(data.todolist || []))
      .catch(err => console.error("Error fetching todos:", err));
  }, []);

  return (
    <div style={{ fontFamily: "Arial, sans-serif", padding: "2rem" }}>
      <h1>🌊 WaveMail</h1>
      <p><i>Surf through the email tides!</i></p>

      {/* Notifications Section */}
      <section style={{ marginBottom: "2rem" }}>
        <h2>📬 Notifications</h2>
        {notifications.length === 0 ? (
          <p>No important emails right now.</p>
        ) : (
          <ul>
            {notifications.map((note, idx) => (
              <li key={idx}>
                <strong>{note.subject}</strong> from {note.from} — {note.date}
                <br />
                {note.summary && <em>{note.summary}</em>}
              </li>
            ))}
          </ul>
        )}
      </section>

      {/* To-Do List Section */}
      <section>
        <h2>📝 To-Do List</h2>
        {todos.length === 0 ? (
          <p>No tasks extracted.</p>
        ) : (
          <ul>
            {todos.map((taskObj, idx) => (
              <li key={idx}>{taskObj.todo}</li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

export default App;
