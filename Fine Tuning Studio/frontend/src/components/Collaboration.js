import React, { useState, useEffect } from 'react';
import apiClient from '../services/api';

export const Collaboration = () => {
  const [teams, setTeams] = useState([]);
  const [teamName, setTeamName] = useState('');
  const [teamDesc, setTeamDesc] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');

  useEffect(() => {
    fetchTeams();
  }, []);

  const fetchTeams = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/collaboration/teams');
      setTeams(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch teams');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTeam = async () => {
    if (!teamName.trim()) {
      setError('Team name is required');
      return;
    }

    try {
      const response = await apiClient.post('/collaboration/teams', {
        name: teamName,
        description: teamDesc
      });

      setTeams([...teams, response.data]);
      setTeamName('');
      setTeamDesc('');
      setError(null);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create team');
    }
  };

  const handleAddComment = async (jobId) => {
    if (!newComment.trim()) {
      setError('Comment cannot be empty');
      return;
    }

    try {
      await apiClient.post(`/collaboration/jobs/${jobId}/comments`, {
        content: newComment
      });

      setNewComment('');
      setError(null);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to add comment');
    }
  };

  const fetchComments = async (jobId) => {
    try {
      const response = await apiClient.get(`/collaboration/jobs/${jobId}/comments`);
      setComments(response.data);
    } catch (err) {
      console.error('Error fetching comments:', err);
    }
  };

  return (
    <div style={{ maxWidth: '1000px', margin: '20px auto' }}>
      <h2>Team Collaboration</h2>

      {error && <div style={{ color: 'red', marginBottom: '10px', padding: '10px', backgroundColor: '#ffe6e6', borderRadius: '4px' }}>{error}</div>}

      <div style={{ marginBottom: '30px', padding: '15px', backgroundColor: '#f9f9f9', borderRadius: '4px' }}>
        <h3>Create Team</h3>
        <input
          type="text"
          placeholder="Team name"
          value={teamName}
          onChange={(e) => setTeamName(e.target.value)}
          style={{ width: '100%', padding: '8px', marginBottom: '10px', boxSizing: 'border-box' }}
        />
        <textarea
          placeholder="Team description (optional)"
          value={teamDesc}
          onChange={(e) => setTeamDesc(e.target.value)}
          style={{ width: '100%', padding: '8px', marginBottom: '10px', boxSizing: 'border-box', minHeight: '80px' }}
        />
        <button
          onClick={handleCreateTeam}
          style={{ padding: '10px 20px', backgroundColor: '#007bff', color: 'white', border: 'none', cursor: 'pointer' }}
        >
          Create Team
        </button>
      </div>

      <div>
        <h3>My Teams</h3>
        {loading ? (
          <p>Loading teams...</p>
        ) : teams.length === 0 ? (
          <p>No teams yet. Create one to get started!</p>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
            {teams.map(team => (
              <div
                key={team.id}
                onClick={() => {
                  setSelectedTeam(team);
                  fetchComments(team.id);
                }}
                style={{
                  padding: '15px',
                  border: selectedTeam?.id === team.id ? '2px solid #007bff' : '1px solid #ddd',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  backgroundColor: selectedTeam?.id === team.id ? '#f0f7ff' : '#fff'
                }}
              >
                <h4>{team.name}</h4>
                <p style={{ fontSize: '12px', color: '#666' }}>{team.description || 'No description'}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {selectedTeam && (
        <div style={{ marginTop: '30px', padding: '15px', backgroundColor: '#f9f9f9', borderRadius: '4px' }}>
          <h3>{selectedTeam.name} - Comments</h3>

          <div style={{ marginBottom: '15px' }}>
            <textarea
              placeholder="Add a comment..."
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              style={{ width: '100%', padding: '8px', marginBottom: '10px', boxSizing: 'border-box', minHeight: '80px' }}
            />
            <button
              onClick={() => handleAddComment(selectedTeam.id)}
              style={{ padding: '8px 16px', backgroundColor: '#28a745', color: 'white', border: 'none', cursor: 'pointer' }}
            >
              Post Comment
            </button>
          </div>

          <div>
            <h4>Comments ({comments.length})</h4>
            {comments.length === 0 ? (
              <p style={{ color: '#666' }}>No comments yet</p>
            ) : (
              <div>
                {comments.map(comment => (
                  <div key={comment.id} style={{ padding: '10px', backgroundColor: '#fff', marginBottom: '10px', borderRadius: '4px', border: '1px solid #eee' }}>
                    <div style={{ fontSize: '12px', color: '#999' }}>
                      <strong>{comment.user_id}</strong> - {new Date(comment.created_at).toLocaleString()}
                    </div>
                    <p style={{ marginTop: '5px' }}>{comment.content}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Collaboration;
